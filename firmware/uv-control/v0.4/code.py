# SPDX-License-Identifier: MIT
"""UV-Control v0.4 bring-up test.

Reads the detector and emitter signals through the ADS1115, switches the UV LED
and shows the readings on the ST7789 TFT and the USB serial console.

Board: SuperMini nRF52840 (CircuitPython's "SuperMini NRF52840" build).
Wiring: hardware/uv-control/v0.4-design.md (pin map).

Buttons:
  A  LED on/off (manual)
  B  measure: dark, LED on, dark again; shows light minus dark per channel
  C  use the last measurement as the blank, so later ones show absorbance
"""
import math
import time

import analogio
import board
import busio
import digitalio
import displayio
import terminalio
from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15
from adafruit_display_text import label
from adafruit_st7789 import ST7789
from fourwire import FourWire

# --- Pins: keep in step with the schematic and v0.4-design.md
TFT_SCK, TFT_MOSI, TFT_CS = board.P1_13, board.P0_10, board.P1_11
TFT_DC, TFT_RST, TFT_BL = board.P0_06, board.P0_08, board.P1_15
I2C_SDA, I2C_SCL = board.P0_17, board.P0_20
LED_ENABLE = board.P0_22   # emitter: HIGH forces the LED off, LOW lets LED_DRIVE set it
LED_DRIVE = board.P0_24    # emitter current setpoint: HIGH (3.3 V) gives about 26 mA
BOOST_EN = board.P1_00     # U1 (LMR62014) enable: HIGH turns the 8 V LED supply on
BUTTONS = (board.P0_11, board.P1_04, board.P1_06)   # A, B, C to GND
V8_SENSE = board.P0_31     # 8 V LED supply through a 20k/10k divider
DET_2V5 = board.P0_02      # the detector's 2.5 V reference

SENSE_OHMS = 24.9          # emitter current-sense resistor (R2 on the emitter)
SETTLE_S = 0.05            # wait after switching the LED before reading
SAMPLES = 8                # readings averaged per channel


def output(pin, value):
    io = digitalio.DigitalInOut(pin)
    io.switch_to_output(value=value)
    return io


# LED off before anything else
led_enable = output(LED_ENABLE, True)
led_drive = output(LED_DRIVE, False)
boost_en = output(BOOST_EN, True)
led_is_on = False


def set_led(on):
    global led_is_on
    led_drive.value = on
    led_enable.value = not on
    led_is_on = on


buttons = []
for pin in BUTTONS:
    b = digitalio.DigitalInOut(pin)
    b.switch_to_input(pull=digitalio.Pull.UP)
    buttons.append(b)
last_state = [True] * len(buttons)


def pressed():
    """Index of a button that was just pressed, or None."""
    for i, b in enumerate(buttons):
        down = not b.value
        if down and last_state[i]:
            last_state[i] = False
            return i
        if not down:
            last_state[i] = True
    return None


# --- ADC
i2c = busio.I2C(I2C_SCL, I2C_SDA)
ads = ADS1115(i2c)          # address 0x48 (ADDR to GND)
ads.gain = 1                # +/-4.096 V full scale
CHANNELS = (
    ("detect", AnalogIn(ads, ads1x15.Pin.A0)),
    ("rect", AnalogIn(ads, ads1x15.Pin.A1)),
    ("light-tight", AnalogIn(ads, ads1x15.Pin.A2)),
    ("LED sense", AnalogIn(ads, ads1x15.Pin.A3)),
)
v8 = analogio.AnalogIn(V8_SENSE)
v2v5 = analogio.AnalogIn(DET_2V5)


def read_all():
    sums = [0.0] * len(CHANNELS)
    for _ in range(SAMPLES):
        for i, (_, ch) in enumerate(CHANNELS):
            sums[i] += ch.voltage
    return [s / SAMPLES for s in sums]


def internal_volts(adc, scale=1.0):
    return adc.value / 65535 * adc.reference_voltage * scale


# --- Display: 2.0" 240x320 ST7789, used in landscape
displayio.release_displays()
spi = busio.SPI(TFT_SCK, MOSI=TFT_MOSI)
bus = FourWire(spi, command=TFT_DC, chip_select=TFT_CS, reset=TFT_RST, baudrate=24_000_000)
display = ST7789(bus, width=320, height=240, rotation=90, backlight_pin=TFT_BL)
screen = displayio.Group()
display.root_group = screen


def text_line(y, color=0xFFFFFF, scale=2):
    t = label.Label(terminalio.FONT, text="", color=color, scale=scale, x=6, y=y)
    screen.append(t)
    return t


title = text_line(12, 0x66CCFF)
title.text = "UV-Control v0.4"
rows = [text_line(44 + 24 * i) for i in range(len(CHANNELS))]
status = text_line(150, 0xFFCC00)
result = text_line(184, 0x99FF99)
hint = text_line(226, 0x888888, scale=1)
hint.text = "A: LED on/off   B: measure   C: set blank"

blank = None
last = None


def measure():
    """Light minus dark for each channel, with the LED off before and after."""
    set_led(False)
    time.sleep(SETTLE_S)
    dark1 = read_all()
    set_led(True)
    time.sleep(SETTLE_S)
    light = read_all()
    set_led(False)
    time.sleep(SETTLE_S)
    dark2 = read_all()
    return [l - (a + b) / 2 for l, a, b in zip(light, dark1, dark2)], light


print("time_s,detect_V,rect_V,light_tight_V,led_sense_V,led_on")
while True:
    button = pressed()
    if button == 0:
        set_led(not led_is_on)
    elif button == 1:
        last, light = measure()
        led_mA = light[3] / SENSE_OHMS * 1000
        line = "signal %.4f V  LED %.1f mA" % (last[0], led_mA)
        if blank and last[0] > 0 and blank[0] > 0:
            line = "A = %.4f  LED %.1f mA" % (-math.log10(last[0] / blank[0]), led_mA)
        result.text = line
        print("measure," + ",".join("%.5f" % v for v in last))
    elif button == 2 and last:
        blank = last
        result.text = "blank set: %.4f V" % blank[0]

    volts = read_all()
    for row, (name, _), v in zip(rows, CHANNELS, volts):
        row.text = "%-11s %7.4f V" % (name, v)
    status.text = "LED %s  8V %.2f V  2V5 %.3f V" % (
        "ON " if led_is_on else "off", internal_volts(v8, 3.0), internal_volts(v2v5))
    print("%.2f,%s,%d" % (time.monotonic(), ",".join("%.5f" % v for v in volts), led_is_on))
    time.sleep(0.2)
