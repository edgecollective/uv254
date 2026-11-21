# UV-Control v0.4: to do

Open work on the control board, for whoever picks it up next (person or agent).
Written 2026-11-21 from a review of the layout as saved that day. Design
background, the pin map and the reasons for the floorplan are in
[`v0.4-design.md`](v0.4-design.md).

Coordinates are in mm in KiCad's board coordinates (origin at the board's
top-left corner, y down), as seen from the front. Parts can move, so check a
position in KiCad before acting on it. Tick items off here (`- [x]`) in the
same commit that does the work.

## Before you start

- Read [CONTRIBUTING.md](../../CONTRIBUTING.md): KiCad 10.0.x only, one person
  per board at a time, and close KiCad before pulling.
- If `~uv-control.kicad_*.lck` files exist in this folder, someone has the
  project open in KiCad. Don't edit the files underneath them; KiCad would
  overwrite your changes when it next saves.
- Check the board before and after changes:
  ```sh
  kicad-cli pcb drc --schematic-parity --severity-all -o /tmp/drc.txt hardware/uv-control/uv-control.kicad_pcb
  kicad-cli sch erc --severity-all -o /tmp/erc.txt hardware/uv-control/uv-control.kicad_sch
  ```
  As of this writing: 0 unconnected items, 0 schematic parity issues.
- U2's footprint (`uv254:nice_nano_cleanest`, on the back) has no courtyard,
  so DRC won't notice a part placed under the Pro Micro. Check its silkscreen
  outline by eye.
- Don't tag a release. The owner decides when.

## Layout goals

These are what most items below protect.

- Two layers, **one GND**, ground fill on both layers, stitched with vias.
- **Analog corner, top left:** J1 (detector) feeds the RC filters (R5-R8, C7-C10), which feed U3 (ADS1115).
  - Keep the LED drive, V_LED, SPI and the boost's switching away from it.
  - Keep the LED's and the boost's return currents out of the ADS ground. The
    LED pulses at the same rate the detector measures, so any pick-up reads as
    light and can't be averaged out.
- **Emitter corner, bottom left:** J2, J5 and the 555 (U4) with its timing parts.
- **MCU (U2)** in the middle. The display (U5), microSD (J10) and buttons (B1-B3) are on the right.
- **SPI (24 MHz) runs on the front, under the display.** The back fill there
  is its ground return, so avoid long cuts in the back fill under those lines.
- **Boost (U6 and its parts, back, around x 56-64, y 23-37):** keep the switching loop small and the GND solid.

## Must do before ordering

- [ ] **Boost: move the FB trace off the switching side.**
  - Now: the trace from C3 pad 2 (60.30, 34.05) to U6 pin 3 (58.40, 29.05) runs between D3's pads (SW at 61.85, 31.55; V_LED at 58.55, 31.55) and under U6 pin 2.
  - FB is the converter's most sensitive node (R10 1.40M / R16 160k).
  - Fix: C3 is in parallel with R10 (both V_LED to FB), so move C3 beside R10 (56.30, 31.35-33.35) and delete the diagonal.
  - Done when no FB copper lies right of x ≈ 58.5.
- [ ] **Boost: tighten the switching loop.** The loop runs U6 SW, D3, C1, GND, U6 pin 2.
  - C1 (output, 57.55, 36.45) is about 5 mm of 0.2 mm trace from D3 pad 1. Put it right against D3 pad 1, with its GND pad close to U6 pin 2.
  - C2 (input, 56.30, 24.30) reaches L1 pad 1 (63.90, 26.85) only through about 8 mm of 0.2 mm trace on the front (y 22.5). Move it beside L1 pad 1, with its GND toward U6 pin 2.
  - Widen SW (U6 pin 1 to L1 pad 2 and D3 pad 2) and the 3V3 into L1 from 0.2 mm to about 0.5 mm.
  - U6 pin 2 now reaches ground through a trace and vias under the chip (fixed 2026-11-21). Keep it at least that well connected.
- [ ] **BOM: add the new parts.** `scripts/make-bom.py` stops on parts it doesn't know:
  - boost: U6 TPS61041QDBVRQ1, D3 MBR0530, L1 15 µH 1008, C1 10 µF/25 V, C2 22 µF/10 V, C3 4.7 pF, R10 1.40M, R16 160k
  - J9 (2-pin JST PH, battery)

  Add them to `PARTS` and `part_for()`, run `scripts/make-bom.py`, and commit
  `hardware/BOM.md`, `hardware/bom.csv` and `docs/bom/index.html`.
  - **L1** has no part chosen yet. It needs a saturation current of at least about 0.35 A (the TPS61041 switch peak is about 0.3 A). Few 1008-size 15 µH parts reach that, so the footprint may need to grow.
  - **C1:** at 12 V an 0805 10 µF/25 V ceramic keeps only part of its capacitance. Pick one with a usable value at 12 V.
- [ ] **Delete the dangling 3V3 stub** on B.Cu at (60.16, 40.10)-(60.26, 40.20). DRC reports it as `track_dangling`.

## Should do

- [ ] **BAT cuts the back fill under the display lines.**
  - BAT runs from J9/J11 (top, about x 38-47) to U2 pins 24/25 (49.44, 40.40 / 42.94).
  - Its 0.7 mm back trace at x 52.4, y 8-40, splits the back ground under every display and button line.
  - Fix: if the battery cable can enter at the bottom edge, move J9/J11 next to U2 pins 24/25, so BAT is a few mm long.
- [ ] **Separate the emitter's ground return from the ADS filter caps.**
  - A 0.7 mm front trace runs from the GND via by J2 pin 6 at (11.70, 22.80) to the ground pads of C9/C10.
  - Delete the segment (11.70, 22.80)-(17.40, 22.80). The via stays in the fill, and C9/C10 stay grounded through their back traces.
  - Re-run DRC to confirm 0 unconnected.
- [ ] **EN** (J8 pin 4 at 54.92, 42.80 to U6 pin 4 / R3) runs 16 mm up the back at x 54.9, a second cut beside BAT. It's below the display lines, so it's minor. Shorten it or run it right next to BAT so the two cuts merge.

## Owner to decide

- [ ] **J4 (optional SSD1306 OLED header) sits under the display.** Its courtyard overlapping U5 is the remaining DRC error. Move it out, put it on the back, or drop it.
- [ ] **Display support.**
  - The 62 mm GMT020 module is held only by its 8-pin header at the button end. Its far end floats 2.5 mm above the board.
  - Its corner holes (on Dwgs.User in the footprint) are at about (54.45, 7.06), (54.45, 36.31), (113.25, 7.06) and (113.25, 36.31). Traces pass through both far-end spots.
  - The footprint and 3D model dimensions are photo estimates (±0.3 mm). Caliper-check a module first, then update `D2` in `lib/uv254.3dshapes/make_models.py` and `lib/uv254.pretty/st7789_200in_240x320.kicad_mod`.
- [ ] **Boost output margin.**
  - R10/R16 set V_LED to 1.233 × (1 + 1.40M/160k) ≈ 12.0 V.
  - With the TPS61041's 250 mA switch limit, a rough estimate is about 30 mA at 12 V from 3.3 V. The emitter v0.5 LED takes about 24-26 mA while on, so there's little margin.
  - The TPS61040 has the same pinout and a 400 mA limit (about 45 mA). Check TI's output-current curves.
- [ ] **3V3 load.**
  - While the LED is on, the boost draws about 120 mA from 3V3, on top of the backlight, microSD and MCU. Check that the Pro Micro's regulator can supply it.
  - That load switches at the LED rate on the same 3V3 that feeds the detector (J1 pin 1) and U3. If it shows up in measurements, filter the detector's supply (RC or ferrite plus cap).
- [ ] **Ground fill clearance** is 0.5 mm, which can't fit between 0.1 in header pins, so U2's columns, J1/J2 and the test headers act as walls in both fills. A clearance of 0.25 mm lets thin necks through. Optional.

## Other open items

- [ ] **Firmware pin map:** `firmware/uv-control/v0.4/code.py` still uses the first draft's pins. The current map is in `v0.4-design.md` (the Pro Micro pin table and the "Firmware" bullet under "To do in KiCad"). The owner deferred this.
- [ ] **Design notes:** `v0.4-design.md` predates the boost and the header changes. Update it:
  - J5 is the emitter test header (CUR, DIS, DRV, V_LED, GND).
  - J8 is the power test header (GND, V_LED, 3V3, EN).
  - J7 is a 2-pin GND/3V3 header.
  - J9/J11 are the battery connectors (BAT to U2 pins 24/25).
  - The boost (U6 and its parts) makes V_LED = 12 V on the board.
- [ ] **Schematic:**
  - ERC has 5 "pin not driven" errors from the Pro Micro symbol typing its GPIOs as inputs (as on Rook) and 2 library-mismatch warnings (*Update Symbols from Library*).
  - It also warns that `EN` is both a local and a global label.
- [ ] **Footprints:** R17, R20, R22 and R24 differ from their `Resistor_SMD` library copies (DRC warnings). Update them from the library unless the difference is deliberate.
- [ ] **Two starved thermals** (DRC):
  - J7 pad 1's front-fill connection goes to an isolated island. Harmless, since the pad connects through its back trace.
  - R16 pad 2 has one spoke. It's also tied to U6 pin 2 by a trace.
- [ ] **After any board change:** run `scripts/render-images.sh uv-control` (README images) and `scripts/make-bom.py`, and commit their output with the change.

## Done

2026-11-21, from the first layout review:

- [x] V_LED no longer crosses the analog corner. It comes from the on-board boost and runs along the bottom and left edges to J2/J5, and J8 sits beside the boost.
- [x] U3's ground pins have vias into the main front ground fill; the front island around U3 is gone.
- [x] DET_1V8's run to U2 pin 19 is on the back, clear of SCK.
- [x] Removed the GND via drilled into J5 pad 5 and the dangling via on A0 under U3.
- [x] U6 pin 2 (GND) connected.
