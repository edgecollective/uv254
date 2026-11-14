# uv254 project library

Custom parts shared by all boards. Each board's `sym-lib-table` and
`fp-lib-table` load this library under the nickname **`uv254`**. Conventions
are in [CONTRIBUTING.md](../CONTRIBUTING.md#libraries).

## Symbols (`uv254.kicad_sym`)

| Symbol | Used on | Default footprint |
|---|---|---|
| `555_nicepins` | uv-control | — |
| `itsybitsy_nrf52840_express` | uv-control (A1) | `uv254:itsybitsy` |
| `ssd1306` | uv-control (A2) | `uv254:ssd1306_b` |
| `SD008-2171-112` | uv-detector (D2) | `Package_TO_SOT_THT:TO-18-3` |
| `nice_nano_clean` | uv-control (U2), from Rook v0.4 | `uv254:nice_nano_cleanest` |
| `st7789` | uv-control (U5), from Rook v0.4 | `uv254:st7789_154in_240x240` |

## Footprints (`uv254.pretty`)

| Footprint | Used on |
|---|---|
| `itsybitsy` | uv-control: socket strips for the ItsyBitsy module |
| `ssd1306_b` | uv-control: 4-pin socket strip for the OLED module |
| `LED_IN-C35PPCTGU0` | uv-emitter: Inolux IN-C35PPCTGU0 UV-C LED |
| `nice_nano_cleanest` | uv-control: Pro Micro nRF52840 (SuperMini / nice!nano), 26 pads incl. B+/B-; from Rook v0.4 |
| `st7789_154in_240x240` | uv-control: 1.54 in ST7789 display header; from Rook v0.4 |
| `st7789_tft_2in_320x240` | 2.0 in ST7789 display header (same pin order); from Rook's library |
| `DM3D-SF_outline` | uv-control: Hirose DM3D-SF microSD socket; from Rook v0.4 |
| `SSW_1825232-1` | uv-control: TE 1825232-1 slide switch (display backlight); from Rook v0.4 |
| `SW_Tactile_12x12_B3F-40xx` | uv-control (B1-B3): 12x12 mm tactile switch, Omron B3F-40xx pattern (fits generic 4-pin 12x12); 3D model includes a cap |

## Where these came from

These are the parts the current boards use, gathered from the old per-project
libraries (`lucc`, `uvcontrol`, `symbols`, `footprints`) in `uv-water`. The
unused parts from those libraries (GPS, LoRa, display variants, S5971,
adafruit_qt_py, SK6812MINI, ...) are still available at the older tags, for
example `git show uv-control/v0.1_A:hardware/uv-control/lucc.kicad_sym`.

## Known issues

- `itsybitsy_nrf52840_express`: the description and datasheet were copied from
  the Feather 32u4 Bluefruit symbol ("ATmega32u4 MCU and bluetooth").
- `ssd1306`: the description and datasheet are the generic Feather ones.
- `555_nicepins`: no description or datasheet.
- `LED_IN-C35PPCTGU0`: the description and 3D model are left over from the
  0805 LED footprint it was made from, so the 3D view shows an 0805 LED. Add
  the real model under `uv254.3dshapes/`.

## 3D models (`uv254.3dshapes`)

Simple box models for checking heights and designing the front panel, generated
by [`uv254.3dshapes/make_models.py`](uv254.3dshapes/make_models.py) (CadQuery:
`pip install cadquery`, then `python make_models.py`). Values marked ESTIMATE in
the script come from vendor drawings; measure the parts and regenerate.

| Model | Used by |
|---|---|
| `ST7789_1.54in_MRD_on_header.step` | `st7789_154in_240x240`: the 32 x 43.5 mm MRD 1.54 in module on its 1x8 header (2.5 mm spacer) |
| `SW_Tactile_12x12.step` | `SW_Tactile_12x12_B3F-40xx`: 12 x 12 x 7.3 mm switch |
| `Cap_12x12_square.step` | `SW_Tactile_12x12_B3F-40xx`: placeholder square cap. Its top is set as an absolute height above the board (`--button-top 13`) or relative to the display glass (`--above-screen 3`); the script prints both heights |
| `ProMicro_nRF52840_on_header.step` | `nice_nano_cleanest`: Pro Micro board, pins, USB-C and nRF52840 on a 2.54 mm header (2.5 mm spacer; set `P['spacer']` for a socket) |
| (KiCad's) `Connector_Card.3dshapes/microSD_HC_Hirose_DM3D-SF.step` | `DM3D-SF_outline`: Rook's footprint is KiCad's DM3D-SF pad pattern shifted by (0.025, -4.475) mm, so the stock model is used with that offset |

The whole board, with these models, exports to STL with
`kicad-cli pcb export stl -o uv-control.stl hardware/uv-control/uv-control.kicad_pcb`
(or File > Export > STL in the PCB editor).

