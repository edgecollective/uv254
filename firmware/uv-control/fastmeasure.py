# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This test will initialize the display using displayio and draw a solid white
background, a smaller black rectangle, and some white text.
"""

import board
import displayio
import digitalio
import analogio
import time
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.rect import Rect
from adafruit_debouncer import Debouncer
import math

pin = digitalio.DigitalInOut(board.D10)
pin.direction = digitalio.Direction.INPUT
pin.pull = digitalio.Pull.UP
switch = Debouncer(pin)

MODE = 1

adc = analogio.AnalogIn(board.A1)

# Compatibility with both CircuitPython 8.x.x and 9.x.x.
# Remove after 8.x.x is no longer a supported release.
try:
    from i2cdisplaybus import I2CDisplayBus

    # from fourwire import FourWire
except ImportError:
    from displayio import I2CDisplay as I2CDisplayBus

    # from displayio import FourWire

import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306

displayio.release_displays()

oled_reset = board.D9

# Use for I2C
i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
display_bus = I2CDisplayBus(i2c, device_address=0x3C, reset=oled_reset)

# Use for SPI
# spi = board.SPI()
# oled_cs = board.D5
# oled_dc = board.D6
# display_bus = FourWire(spi, command=oled_dc, chip_select=oled_cs,
#                                 reset=oled_reset, baudrate=1000000)

WIDTH = 128
HEIGHT = 64  # Change to 64 if needed
BORDER = 5

display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

# Make the display context
splash = displayio.Group()
display.root_group = splash

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
#splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(WIDTH - BORDER * 2, HEIGHT - BORDER * 2, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Black
inner_sprite = displayio.TileGrid(
    inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER
)
#splash.append(inner_sprite)

# Draw a label
text = "Booting up..."
directions = label.Label(
    terminalio.FONT, text=text, scale=1, color=0xFFFFFF, x=5, y=5
)
#splash.append(directions)


text = "BLANK: "
blank = label.Label(
    #terminalio.FONT, text=text, scale=2, color=0xFFFFFF, x=5, y=HEIGHT // 2
    terminalio.FONT, text=text, scale=2, color=0xFFFFFF, x=10, y=10
)
splash.append(blank)

text = "SUT: "
SUT = label.Label(
    terminalio.FONT, text=text, scale=2, color=0xFFFFFF, x=10, y = 30
)
splash.append(SUT)

text = "ABS: "
ABS = label.Label(
    terminalio.FONT, text=text, scale=2, color=0xFFFFFF, x=10, y = 50
)
splash.append(ABS)

circle = Circle(3, 10, 4, fill=0x00FF00, outline=0xFF00FF)
splash.append(circle)
 
#rect = Rect(0, 1, 3 , 19, outline=0xFFFFFF, fill=0xFFFFFF,stroke=1)
#splash.append(rect)
#adc.reference_voltage=3.3

blank_val=0.
SUT_val=0.
ABS_val=0.
while True:

    switch.update()
    
    print(switch.value)
    
    if switch.fell:
        print("Just pressed")
        MODE=MODE+1
        if (MODE>3):
            MODE=1
        if MODE==1:
            ABS.text="ABS:"
            SUT.text="SUT:"
            circle.y=5
        if MODE==2:
            circle.y=25
        if MODE==3:
            circle.y=45
            ABS_val=math.log(blank_val/SUT_val,10)
            ABS.text="ABS:"+'{:03.2f}'.format(ABS_val)
        
        
    voltage=adc.value / 65535 * adc.reference_voltage
    volts_str='{:03.3f}'.format(voltage)
    
    if MODE==1:
        blank_val=voltage
        blank.text="BLN:"+volts_str    
    if MODE==2:    
        SUT_val=voltage
        SUT.text="SUT:"+volts_str
        
        
