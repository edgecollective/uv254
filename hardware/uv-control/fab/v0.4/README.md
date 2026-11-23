# uv-control v0.4 — fabrication files

Released 2026-11-23. Built with `scripts/build-fab.sh` and kicad-cli 10.0.8.

The matching design is the git tag **`uv-control/v0.4`**: `git checkout uv-control/v0.4` and
open `hardware/uv-control/uv-control.kicad_pro`.

| File | What it is |
|---|---|
| `uv-control-v0.4-gerbers.zip` | Gerber layers, Excellon drill file and Gerber job file. Upload this to the fab house. |
| `gerbers/` | The same files, unzipped |
| `uv-control-v0.4-bom.csv` | Bill of materials, grouped by value and footprint (no part numbers: see [`hardware/BOM.md`](../../../BOM.md)) |
| `uv-control-v0.4-pos.csv` | Component positions for assembly (both sides, mm) |
| `uv-control-v0.4-schematic.pdf` | Schematic |
| `reports/` | ERC and DRC reports at release |

## Board

Two layers, 147 x 54 mm. Most parts are on the back; the display (U5), buttons
(B1-B3), RESET1, SW1, J12, JP1 and the optional J4 are on the front.

## Checks at release

- **DRC:** 0 unconnected pads, and the board matches the schematic. 20 entries:
  - J4 (optional OLED header) and U5 (display) courtyards overlap. J4 isn't fitted on v0.4.
  - 3 one-spoke thermal reliefs (U5 pin 8, SW1 pin 1, J9 pin 2). Each pad is also
    connected to ground on the other layer.
  - 4 footprint-library-mismatch warnings (R17, R20, R22, R24: hand-solder pads from Rook).
  - 12 silkscreen-clipped-by-mask warnings, all on the microSD socket (J10).
- **ERC:** 0 errors. 3 warnings: two symbol-library mismatches (U5, U6) and `EN` used as
  both a local and a global label.

## Ordering and assembly notes

- The drill file holds both plated and non-plated holes (15 non-plated: the corner M3
  holes, the Feather's standoff holes, J8's mounting hole and the microSD pegs). Some fab
  houses plate every hole in a single drill file, which is harmless for these.
- U2 is an Adafruit Feather (nRF52840 Express; an ESP32-S3 or M4 Express also fits the
  pin map) on two 8.5 mm female sockets, 1x16 and 1x12.
- Fit either the on-board boost (U6 with L1, D3, C1-C3, R3, R10, R16) or Adafruit's 5644
  boost breakout at J8, not both.
- Don't fit J4. The display has no mounting holes on this revision.
- Parts with manufacturer part numbers: [`hardware/BOM.md`](../../../BOM.md). Open items:
  [`hardware/uv-control/TODO.md`](../../TODO.md).
