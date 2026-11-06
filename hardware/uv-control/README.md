# UV-Control

Controller board: an Adafruit ItsyBitsy nRF52840 Express, an SSD1306 OLED
display, push buttons and power circuitry. Firmware is in
[`firmware/uv-control`](../../firmware/uv-control).

Open `uv-control.kicad_pro` in KiCad 10. Custom parts come from
[`lib/`](../../lib).

## Revisions

| Version | Date | Status | Design | Fab files |
|---|---|---|---|---|
| v0.1 | 2024-07-29 | gerbers released; ordered from JLCPCB on 2024-08-19 | tag `uv-control/v0.1` | [`fab/v0.1`](fab/v0.1) |
| v0.1_A | 2026-06-26 | branched from v0.1; sent to Josh | tag `uv-control/v0.1_A` | — |
| **next** | 2026-10 | **on `main`**: board edits made after v0.1_A was sent, untagged | `main` | — |

Notes:

- The silkscreen still points to `gitlab.com/edgecollective/uv-water/` and
  reads `UV-Control v0.1 / July 2024`. Update both before the next fabrication.
