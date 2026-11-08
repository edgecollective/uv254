# uv-emitter v0.4 — fabrication files

Released 2026-11-08. Built with `scripts/build-fab.sh` and kicad-cli 10.0.8.

The matching design is the git tag **`uv-emitter/v0.4`**: `git checkout uv-emitter/v0.4` and
open `hardware/uv-emitter/uv-emitter.kicad_pro`.

| File | What it is |
|---|---|
| `uv-emitter-v0.4-gerbers.zip` | Gerber layers, Excellon drill file and Gerber job file. Upload this to the fab house. |
| `gerbers/` | The same files, unzipped |
| `uv-emitter-v0.4-bom.csv` | Bill of materials, grouped by value and footprint |
| `uv-emitter-v0.4-pos.csv` | Component positions for assembly (both sides, mm) |
| `uv-emitter-v0.4-schematic.pdf` | Schematic |
| `reports/` | ERC and DRC reports at release |

## Checks at release

- **DRC:** no errors, 0 unconnected pads, and the board matches the schematic. The 12
  warnings are all footprint-library mismatches.
- **ERC:** 2 "Input Power pin not driven" errors, because there are no `PWR_FLAG` symbols and
  power comes in through the connector. 2 warnings: Q1 and D1 differ slightly from the
  current library copies.
