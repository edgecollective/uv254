# uv254

Open hardware for the **uv254** UV water-quality sensor. The device is three
boards, each its own KiCad project:

| Board | Folder | What's on it | Current design |
|---|---|---|---|
| **UV-Control** | [`hardware/uv-control`](hardware/uv-control) | Adafruit ItsyBitsy nRF52840 Express, SSD1306 OLED display, buttons, power circuitry | v0.1_A plus later edits |
| **UV-Emitter** | [`hardware/uv-emitter`](hardware/uv-emitter) | Inolux IN-C35PPCTGU0 UV-C LED and its driver | v0.4 (in progress) |
| **UV-Detector** | [`hardware/uv-detector`](hardware/uv-detector) | SD008-2171-112 photodiode with an op-amp front end | v0.4 (in progress) |

UV-Emitter was called *UV-LED-source* in earlier revisions. Background notes
are at <https://edgecollective.io/notes/uvf/>.

## Repository layout

```
hardware/
  uv-control/                 one KiCad project per board
    uv-control.kicad_pro      open this in KiCad
    uv-control.kicad_sch
    uv-control.kicad_pcb
    sym-lib-table             -> lib/uv254.kicad_sym
    fp-lib-table              -> lib/uv254.pretty
    fab/<version>/            fabrication files that were actually sent out
  uv-emitter/
  uv-detector/
lib/                          shared project library (custom parts only)
  uv254.kicad_sym
  uv254.pretty/
firmware/uv-control/          CircuitPython scripts for the control board
scripts/build-fab.sh          builds gerbers, drill, BOM, PDF, positions
.github/workflows/kicad.yml   ERC/DRC on every push; fab package on release tags
```

## Opening the boards

Use **KiCad 10.0.x**, the version everyone on the project uses (see
[CONTRIBUTING.md](CONTRIBUTING.md)). Clone the repository and open
`hardware/<board>/<board>.kicad_pro`. Custom parts come from `lib/` through the
project's own library tables, so you don't need any global library setup beyond
KiCad's standard libraries.

## Versions and releases

Each board is versioned on its own. A revision is a git tag named
`<board>/<version>`:

```
git tag -l 'uv-detector/*'          # list detector revisions
git checkout uv-detector/v0.3       # the exact design ordered from JLCPCB in Aug 2024
git checkout main                   # back to the current work
```

`hardware/<board>/fab/<version>/` holds the files that were actually sent to
the fab house for that revision. Each board's README has the revision history.
Pushing a new tag makes CI build that board's fab package and attach it to a
GitHub Release (see [CONTRIBUTING.md](CONTRIBUTING.md#releasing-a-board-revision)).

The history before this repository is in
[gitlab.com/edgecollective/uv-water](https://gitlab.com/edgecollective/uv-water).
Every tagged revision here was imported from it. The imported fab files were
checked by regenerating them from the tagged design.

## License

- **Hardware** (everything except `firmware/`): [CERN Open Hardware Licence
  Version 2 – Strongly Reciprocal](LICENSE) (CERN-OHL-S-2.0).
- **Firmware** (`firmware/`): [MIT License](firmware/uv-control/LICENSE). The
  bundled Adafruit libraries are also MIT, under Adafruit's copyright.

Contributors: Don Blair, Craig Versek.
