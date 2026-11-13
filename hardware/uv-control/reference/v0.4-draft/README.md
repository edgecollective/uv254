# UV-Control v0.4: first draft (reference only)

The first v0.4 control-board draft, kept for reference when the board was
restarted from Rook v0.4 on 2026-11-13. It is the state of `main` at commit
`87ac380` plus the edits made on 2026-11-13 before the restart (schematic tidy-up
and a start on the PCB).

- `uv-control.kicad_sch`, `.kicad_pcb`, `.kicad_pro`: the KiCad project. Opens
  on its own; library tables point at the shared `lib/`. Its Pro Micro symbol
  (`ProMicro_nRF52840`) is embedded in the schematic; the matching footprint is
  only in the PCB and in git history.
- `uv-control-v0.4-draft-schematic.pdf`: the schematic.
- `v0.4-design.md`: the design notes for this draft (pin map, LMR62014 8 V boost,
  checks before building).

The ADS1115 block, the detector/emitter JST connectors and the LED_DRIVE parts
were carried over into the restarted board. The LMR62014 boost was not.
