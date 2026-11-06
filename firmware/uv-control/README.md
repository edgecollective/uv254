# UV-Control firmware

CircuitPython scripts for the UV-Control board (Adafruit ItsyBitsy nRF52840
Express with an SSD1306 OLED). These are experiments from 2024, imported as-is
from `uv-water`.

## Running a script

1. Install CircuitPython 8.x or 9.x on the ItsyBitsy. The bundled libraries
   are `.mpy` format 6, which those versions use.
2. Copy `lib/` to `CIRCUITPY/lib/`.
3. Copy the script you want to `CIRCUITPY/code.py`, e.g. `measure.py`.

## Contents

| Path | What it is |
|---|---|
| `*.py` | board scripts: display tests (`simpledisplay.py`, `border.py`, ...) and measurement variants (`measure.py`, `fastmeasure.py`, `kbmeas.py`, `moving_measure.py`, ...) |
| `serialreader.py` | runs on a computer, not the board: reads the board's serial output (needs `pyserial`) |
| `font5x8.bin` | font file loaded by `adafruit_framebuf`, used through `adafruit_ssd1306` (e.g. `simpledisplay.py`). Copy it to the board as well. |
| `lib/` | Adafruit CircuitPython libraries, compiled `.mpy` |
| `data.txt`, `*_noise*.txt`, `exp_aug_17/` | measurement logs |

## Libraries

`lib/` holds compiled libraries from the
[Adafruit CircuitPython Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle),
which are MIT-licensed by Adafruit Industries. Several scripts started from
Adafruit examples and keep their `SPDX-License-Identifier: MIT` headers. To
refresh the libraries instead of using these copies, use
[circup](https://github.com/adafruit/circup).
