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
| `feather` | uv-control (U2): Adafruit Feather, KiCad's `Adafruit_Feather_Generic` with the pins named by their silkscreen labels (D5-D13, not D0-D6) and 3V3 as a power output | `uv254:Adafruit_Feather_on_socket` |
| `nice_nano_clean` | uv-control U2 until 2026-11-23, from Rook v0.4 | `uv254:nice_nano_cleanest` |
| `adafruit_tps61040_boost` | uv-control (J8): Adafruit's 12 V boost breakout (product 5644), pins G, 12V, In, En as on its header. Pin positions match `Connector_Generic:Conn_01x04`, so *Change Symbol* from a 4-pin connector keeps the wiring | `uv254:Adafruit_TPS61040_Boost_5644` |
| `st7789` | uv-control (U5), from Rook v0.4 | `uv254:st7789_154in_240x240` (U5 uses `st7789_200in_240x320`) |

## Footprints (`uv254.pretty`)

| Footprint | Used on |
|---|---|
| `itsybitsy` | uv-control: socket strips for the ItsyBitsy module |
| `ssd1306_b` | uv-control: 4-pin socket strip for the OLED module |
| `LED_IN-C35PPCTGU0` | uv-emitter: Inolux IN-C35PPCTGU0 UV-C LED |
| `nice_nano_cleanest` | Pro Micro nRF52840 (SuperMini / nice!nano), 26 pads incl. B+/B-; from Rook v0.4 (uv-control U2 until 2026-11-23) |
| `st7789_154in_240x240` | 1.54 in ST7789 display header; from Rook v0.4 (uv-control used it until U5 became the 2.0 in) |
| `st7789_200in_240x320` | uv-control (U5): 2.0 in 240x320 ST7789 module, Golden Morning GMT020-02-8P (37.25 x 62 mm, sold as XIITIA), on a 1x8 header in the same pin order as the 1.54 in one. Module outline, corner holes and active area on Dwgs.User; the courtyard is the whole module |
| `st7789_200in_240x320_WithMountingHoles` | The same, with the module's four corner holes drilled 2.7 mm (M2.5) for 2.5 mm spacers, each with a 6 mm copper keep-out on both sides. The hole positions are photo estimates (+/-0.3 mm): measure a module before ordering |
| `st7789_tft_2in_320x240` | 2.0 in ST7789 display header (same pin order), outline 38 x 64 mm; from Rook's library, not the GMT020 module |
| `ssd1306_a` | 0.96 in SSD1306 I2C OLED: 1x04 socket, pins 1 3V3, 2 GND, 3 SCL, 4 SDA (the square pad is pin 4), module outline on Dwgs.User; from Rook v0.4 |
| `DM3D-SF_outline` | uv-control: Hirose DM3D-SF microSD socket; from Rook v0.4 |
| `SSW_1825232-1` | uv-control: TE 1825232-1 slide switch (display backlight); from Rook v0.4 |
| `SW_Tactile_12x12_B3F-40xx` | uv-control (B1-B3): 12x12 mm tactile switch, Omron B3F-40xx pattern (fits generic 4-pin 12x12); 3D model includes a cap |
| `Adafruit_TPS61040_Boost_5644` | uv-control (J8): the Adafruit 5644 breakout (10.16 x 15.24 mm) on a 1x04 header, lying over the board (2.54 mm spacer) with its body to the +x side. Pads in the same places as `PinHeader_1x04_P2.54mm_Vertical` (pin 1 G at the origin, along +y). Dimensions from Adafruit's Eagle file ([Adafruit-TPS61040-PCB](https://github.com/adafruit/Adafruit-TPS61040-PCB)). The breakout's mounting hole is drilled 2.7 mm (M2.5) with a 6 mm copper keep-out on both sides, for a screw and a 2.5 mm spacer |
| `Adafruit_Feather_on_socket` | uv-control (U2): KiCad's `Module:Adafruit_Feather` pads and outline, with a 3D model of the Feather plugged into 8.5 mm female sockets (its underside 11.04 mm from the board) |
| `Adafruit_Feather_on_socket_WithMountingHoles` | The same, plus the Feather's four mounting holes (positions as in KiCad's `Module:Adafruit_Feather_WithMountingHoles`), drilled 2.7 mm for M2.5 standoffs, each with a 6 mm copper keep-out (tracks, vias, fill) on both sides for the standoff and the screw head. M2.5 x 11 mm standoffs match the 8.5 mm socket plus the 2.5 mm header spacer |

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
`pip install cadquery`, then `python make_models.py`, or name one model to write just that). Values marked ESTIMATE in
the script come from vendor drawings; measure the parts and regenerate.

| Model | Used by |
|---|---|
| `ST7789_1.54in_MRD_on_header.step` | `st7789_154in_240x240`: the 32 x 43.5 mm MRD 1.54 in module on its 1x8 header (2.5 mm spacer) |
| `ST7789_2.0in_GMT020_on_header.step` | `st7789_200in_240x320`: the 37.25 x 62 mm GMT020-02-8P module on its 1x8 header (2.5 mm spacer). Outline and active area from the vendor; header offset, holes and glass measured off photos |
| `SW_Tactile_12x12.step` | `SW_Tactile_12x12_B3F-40xx`: 12 x 12 x 7.3 mm switch |
| `Cap_12x12_square.step` | `SW_Tactile_12x12_B3F-40xx`: placeholder square cap. Its top is set as an absolute height above the board (`--button-top 13`) or relative to the display glass (`--above-screen 3`); the script prints both heights |
| `ProMicro_nRF52840_on_header.step` | `nice_nano_cleanest`: Pro Micro board, pins, USB-C and nRF52840 on a 2.54 mm header (2.5 mm spacer; set `P['spacer']` for a socket) |
| `Adafruit_Feather_nRF52840_4062.step` | `Adafruit_Feather_on_socket`: Adafruit's own model of the Feather nRF52840 Express (product 4062), unchanged, from [Adafruit_CAD_Parts](https://github.com/adafruit/Adafruit_CAD_Parts). **MIT License**, Copyright (c) 2016 Adafruit Industries: see [`Adafruit_CAD_Parts-LICENSE.txt`](uv254.3dshapes/Adafruit_CAD_Parts-LICENSE.txt). The footprint stacks it with KiCad's `PinSocket_1x16`/`1x12` (8.5 mm) and `PinHeader_1x16`/`1x12` models. Adafruit's model has the USB end at x = 0 and pin 1 at (6.35, 1.27), so it is placed with rotation (0, 0, 90) and offset (-1.27, 6.35, 11.04). Adafruit's models of the other Feathers (5323 ESP32-S3, 3857 M4 Express) line up the same way |
| `Adafruit_TPS61040_Boost_5644.step` | `Adafruit_TPS61040_Boost_5644`: Adafruit's model of the 5644 breakout, unchanged, from Adafruit_CAD_Parts (**MIT**, same notice as above), placed with rotation (0, 0, 90) and offset (-2.54, 1.27, 2.54) on KiCad's `PinHeader_1x04` model |
| (KiCad's) `Connector_Card.3dshapes/microSD_HC_Hirose_DM3D-SF.step` | `DM3D-SF_outline`: Rook's footprint is KiCad's DM3D-SF pad pattern shifted by (0.025, -4.475) mm, so the stock model is used with that offset |

The whole board, with these models, exports to STL with
`kicad-cli pcb export stl -o uv-control.stl hardware/uv-control/uv-control.kicad_pcb`
(or File > Export > STL in the PCB editor).

