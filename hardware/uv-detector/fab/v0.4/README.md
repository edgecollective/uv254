# uv-detector v0.4 — fabrication files

Released 2026-11-08. Built with `scripts/build-fab.sh` and kicad-cli 10.0.8.

The matching design is the git tag **`uv-detector/v0.4`**: `git checkout uv-detector/v0.4` and
open `hardware/uv-detector/uv-detector.kicad_pro`.

| File | What it is |
|---|---|
| `uv-detector-v0.4-gerbers.zip` | Gerber layers, Excellon drill file and Gerber job file. Upload this to the fab house. |
| `gerbers/` | The same files, unzipped |
| `uv-detector-v0.4-bom.csv` | Bill of materials, grouped by value and footprint |
| `uv-detector-v0.4-pos.csv` | Component positions for assembly (both sides, mm) |
| `uv-detector-v0.4-schematic.pdf` | Schematic |
| `reports/` | ERC and DRC reports at release |

## Checks at release

- **DRC:** 0 unconnected pads, and the board matches the schematic. One error is excluded:
  J2 pad 6 (GND) has room for only one thermal-relief spoke on F.Cu, but it also has a GND
  track on B.Cu. The other 28 entries are footprint-library-mismatch warnings.
- **ERC:** 3 "Input Power pin not driven" errors, because there are no `PWR_FLAG` symbols and
  power comes in through the connector. Also 56 symbol-library warnings.
