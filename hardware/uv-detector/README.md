# UV-Detector

Photodiode board: an SD008-2171-112 photodiode with an op-amp front end and a
voltage reference.

Open `uv-detector.kicad_pro` in KiCad 10. Custom parts come from
[`lib/`](../../lib).

## Revisions

| Version | Date | Status | Design | Fab files |
|---|---|---|---|---|
| v0.1 | 2024-03-12 | gerbers released | tag `uv-detector/v0.1` | [`fab/v0.1`](fab/v0.1) |
| v0.2 | 2024-04-06 | gerbers released | tag `uv-detector/v0.2` | [`fab/v0.2`](fab/v0.2) |
| v0.3 | 2024-08-19 | ordered from JLCPCB with emitter v0.3 and control v0.1 | tag `uv-detector/v0.3` | [`fab/v0.3`](fab/v0.3) |
| v0.2_A | 2026-06-26 | branched from v0.2; sent to Josh | tag `uv-detector/v0.2_A` | — |
| v0.2_B | 2026-10 | follows v0.2_A | tag `uv-detector/v0.2_B` | — |
| **v0.4** | 2026-11 | **in progress on `main`**, derived from v0.2_B | `main` | — |

Notes:

- **v0.2**: the fabricated gerbers also include the copper text
  `uva-detect-v0.2` on F.Cu. It was deleted from the board before the design
  was committed. See [`fab/v0.2/README.md`](fab/v0.2/README.md).
- **v0.3** has no `.kicad_pro`, because it was never committed upstream. Open
  `uv-detector.kicad_pcb` or `.kicad_sch` directly at that tag.
- **v0.4** was called "v0.3" in `uv-water`. It was renumbered because v0.3 was
  already used by the 2024 JLCPCB order. Its silkscreen still reads
  `uva-detect-v0.3` and `Detect_0.3`, so update it before fabrication.
