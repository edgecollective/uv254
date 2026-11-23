# uv-emitter v0.6 — fabrication files

Released 2026-11-23, together with the other two boards of the set (detector,
emitter and control v0.6). Built with `scripts/build-fab.sh` and kicad-cli 10.0.8.

The matching design is the git tag **`uv-emitter/v0.6`**: `git checkout uv-emitter/v0.6` and
open `hardware/uv-emitter/uv-emitter.kicad_pro`.

| File | What it is |
|---|---|
| `uv-emitter-v0.6-gerbers.zip` | Gerber layers, Excellon drill file and Gerber job file. Upload this to the fab house. |
| `gerbers/` | The same files, unzipped |
| `uv-emitter-v0.6-bom.csv` | Bill of materials, grouped by value and footprint (part numbers: [`hardware/BOM.md`](../../../BOM.md)) |
| `uv-emitter-v0.6-pos.csv` | Component positions for assembly (both sides, mm) |
| `uv-emitter-v0.6-schematic.pdf` | Schematic |
| `reports/` | ERC and DRC reports at release |

## Board

Two layers, 34 x 34 mm.

## Works with

UV-Control v0.6: its J2 (6-pin JST PH) to this board's J2, on a straight cable (pin 1 to pin 1). Pins: 1 LED current (out), 2 LED_DISABLE (high = LED off), 3 LED_DRIVE, 4 12 V (from the control board's boost), 5 3V3, 6 GND. Not compatible with the v0.4 boards (7 V LED supply, 5 V, LED_ENABLE).

## Changes

From v0.5: none; renumbered v0.6 with the set (the control board gained pin labels at
its display header).

From v0.4:

- Op-amp on 3.3 V; the LED runs from its own 12 V supply.
- Q1 is an MMBT3904 (a BSS138 fits the same pads).
- LED_ENABLE became LED_DISABLE (high = off), and Q2's pinout is fixed (v0.4 used a TO-92 2N7000 symbol on a SOT-23 footprint).
- PWR_FLAGs on +3V3 and GND, so ERC has no errors.

## Checks at release

- **DRC:** no errors, 0 unconnected pads, and the board matches the schematic. The 12 warnings are all footprint-library mismatches.
- **ERC:** no errors. 1 warning: D1's LED symbol differs slightly from the current library copy.

## Notes

- LED_DISABLE has no pull resistor on either board, so the LED is enabled until the firmware drives it high. With the 555 drive option selected on the control board (J3/JP1 2-3), the LED pulses from power-up.
- 3.3 V on LED_DRIVE gives about 26 mA in the LED.
