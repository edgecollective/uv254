# UV-Control v0.4 bring-up firmware

`code.py` is a first test for the v0.4 control board, or its breadboard
prototype. It reads the four signals through the ADS1115, switches the UV LED,
and shows the values on the TFT. It also prints them over USB serial as CSV.

It hasn't been run on hardware yet.

## Setup

1. **CircuitPython.** Install the *SuperMini NRF52840* build (CircuitPython 9
   or 10) from circuitpython.org. Double-press reset; the board should appear
   as a USB drive. Copy the `.uf2` onto it.
2. **Libraries.** Install them with
   [circup](https://github.com/adafruit/circup):
   ```sh
   circup install adafruit_ads1x15 adafruit_st7789 adafruit_display_text
   ```
   This needs the current `adafruit_ads1x15`, which uses `ads1x15.Pin.A0`
   (older versions used `ADS.P0`).
3. Copy `code.py` to the `CIRCUITPY` drive.

## Use

| Button | Action |
|---|---|
| A | LED on/off |
| B | measure: dark, LED on, dark again. Shows light minus dark, and the LED current |
| C | use the last measurement as the blank. Later measurements show absorbance, −log10(signal/blank) on the detect channel |

The pins are set at the top of `code.py` and follow the pin map in
[`hardware/uv-control/v0.4-design.md`](../../../hardware/uv-control/v0.4-design.md).
