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

## Footprints (`uv254.pretty`)

| Footprint | Used on |
|---|---|
| `itsybitsy` | uv-control: socket strips for the ItsyBitsy module |
| `ssd1306_b` | uv-control: 4-pin socket strip for the OLED module |
| `LED_IN-C35PPCTGU0` | uv-emitter: Inolux IN-C35PPCTGU0 UV-C LED |

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
- `ssd1306_b` uses the KiCad 6 file format; it will be upgraded along with the
  rest of the library when moving to KiCad 10.
