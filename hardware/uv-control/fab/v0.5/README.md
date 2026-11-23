# uv-control v0.5 — fabrication files

Released 2026-11-23, together with the other two boards of the set (detector,
emitter and control v0.5). Built with `scripts/build-fab.sh` and kicad-cli 10.0.8.

The matching design is the git tag **`uv-control/v0.5`**: `git checkout uv-control/v0.5` and
open `hardware/uv-control/uv-control.kicad_pro`.

| File | What it is |
|---|---|
| `uv-control-v0.5-gerbers.zip` | Gerber layers, Excellon drill file and Gerber job file. Upload this to the fab house. |
| `gerbers/` | The same files, unzipped |
| `uv-control-v0.5-bom.csv` | Bill of materials, grouped by value and footprint (part numbers: [`hardware/BOM.md`](../../../BOM.md)) |
| `uv-control-v0.5-pos.csv` | Component positions for assembly (both sides, mm) |
| `uv-control-v0.5-schematic.pdf` | Schematic |
| `reports/` | ERC and DRC reports at release |

## Board

Two layers, 147 x 54 mm. Most parts are on the back; the display (U5), buttons (B1-B3), RESET1, SW1, J12, JP1 and the optional J4 are on the front.

## Works with

UV-Detector v0.5 on J1 (7-pin JST PH) and UV-Emitter v0.5 on J2 (6-pin JST PH), each on a straight cable (pin 1 to pin 1). Not compatible with the v0.4 detector and emitter.

## Changes from v0.4

None in the design: v0.4 (tagged earlier the same day, never fabricated) was renumbered v0.5 so the three boards of the set share a version. The silkscreen reads `UV-Control-v0.5`.

## Checks at release

- **DRC:** 0 unconnected pads, and the board matches the schematic. 20 entries:
  - J4 (optional OLED header) and U5 (display) courtyards overlap. J4 isn't fitted.
  - 3 one-spoke thermal reliefs (U5 pin 8, SW1 pin 1, J9 pin 2), each also connected on the other layer.
  - 4 footprint-library-mismatch warnings (R17, R20, R22, R24).
  - 12 silkscreen-clipped-by-mask warnings, all on the microSD socket (J10).
- **ERC:** 0 errors. 3 warnings: two symbol-library mismatches (U5, U6) and `EN` used as both a local and a global label.

## Notes

- The drill file holds both plated and non-plated holes (15 non-plated); some fab houses plate every hole in a single drill file, which is harmless here.
- U2 is an Adafruit Feather (nRF52840 Express; an ESP32-S3 or M4 Express also fits the pin map) on two 8.5 mm female sockets, 1x16 and 1x12.
- Fit either the on-board boost (U6 with L1, D3, C1-C3, R3, R10, R16) or Adafruit's 5644 boost breakout at J8, not both. Don't fit J4. The display has no mounting holes on this revision.
- Open items: [`hardware/uv-control/TODO.md`](../../TODO.md).
