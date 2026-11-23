# uv-detector v0.6 — fabrication files

Released 2026-11-23, together with the other two boards of the set (detector,
emitter and control v0.6). Built with `scripts/build-fab.sh` and kicad-cli 10.0.8.

The matching design is the git tag **`uv-detector/v0.6`**: `git checkout uv-detector/v0.6` and
open `hardware/uv-detector/uv-detector.kicad_pro`.

| File | What it is |
|---|---|
| `uv-detector-v0.6-gerbers.zip` | Gerber layers, Excellon drill file and Gerber job file. Upload this to the fab house. |
| `gerbers/` | The same files, unzipped |
| `uv-detector-v0.6-bom.csv` | Bill of materials, grouped by value and footprint (part numbers: [`hardware/BOM.md`](../../../BOM.md)) |
| `uv-detector-v0.6-pos.csv` | Component positions for assembly (both sides, mm) |
| `uv-detector-v0.6-schematic.pdf` | Schematic |
| `reports/` | ERC and DRC reports at release |

## Board

Two layers, 34 x 34 mm.

## Works with

UV-Control v0.6: its J1 (7-pin JST PH) to this board's J2, on a straight cable (pin 1 to pin 1). Pins: 1 3V3, 2 1V8 (reference out), 3 light-tight, 4 rect, 5 detect, 6 and 7 GND. Not compatible with the v0.4 boards, which used 5 V, a 2.5 V reference and a 6-pin connector.

## Changes

From v0.5: none; renumbered v0.6 with the set (the control board gained pin labels at
its display header).

From v0.4:

- Runs from 3.3 V; MCP1501-18 1.8 V reference (replaces the 2.5 V one).
- 7-pin JST PH connector, with pin 7 as a second GND.

## Checks at release

- **DRC:** no errors, 0 unconnected pads, and the board matches the schematic. The 17 warnings are all footprint-library mismatches.
- **ERC:** no errors or warnings.

## Notes

- The op-amp gains haven't been re-tuned for the 3.3 V supply: the outputs have about 1.5 V of swing above the 1.8 V reference. Check them on the first boards.
