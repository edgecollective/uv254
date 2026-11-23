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
- U2 is an Adafruit Feather (since 2026-11-23). Its pin map, and why each signal
  is where it is, are in [`v0.4-design.md`](v0.4-design.md#feather-pins). Keep to
  that map when re-routing: it is what lets the board take an nRF52840, ESP32-S3 or
  M4 Feather.
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

- [ ] **Bring the PCB up to date with the Feather schematic.** As of 2026-11-23 the schematic has U2 as an Adafruit Feather, the new power switch SW1 and its panel-switch connector J12, and no J9/J11 (battery), but the PCB still has the Pro Micro.
  - In the PCB editor run *Tools > Update PCB from Schematic*, with "Replace footprints with those specified in the schematic" and "Delete footprints with no symbols" ticked. U2 becomes `uv254:Adafruit_Feather_on_socket` at the Pro Micro's old position, SW1 and J12 are added, and J9/J11 are deleted.
  - Delete the old tracks to U2's pads and the BAT tracks (back, x 52.4; front, y 8.1 and y 40.4). They keep their old nets and DRC will flag them.
  - Re-place U2 on the back, on female headers like the Pro Micro.
    - To hold the Feather with standoffs, use the footprint `uv254:Adafruit_Feather_on_socket_WithMountingHoles` instead: it adds the Feather's four mounting holes (2.7 mm, M2.5) with copper keep-outs. The screw heads end up on the front, so keep front parts clear of the holes too.
    - The Feather is 22.9 x 50.8 mm (the Pro Micro was 18 x 33), longer than the board is tall (45.55 mm).
    - Its USB connector is at the RST end of the long header (pad 1). Face that end to a board edge so a cable can reach it.
    - On standard 8.5 mm sockets the Feather's underside is 11.04 mm from the board and its tallest parts about 18 mm. Back-side parts under it must be lower than 11 mm, and the enclosure needs the depth; the 3D view shows it.
  - Place SW1, the power switch, at a board edge with its actuator over the edge (it's a right-angle slide switch). Its pad 2 is the common (PWR_EN), pad 1 goes to GND (off) and pad 3 is open (on). Check which slider position joins pads 1-2 before marking ON/OFF on the silkscreen.
  - Place J12 (2-pin 0.1 in header: 1 PWR_EN, 2 GND) where a cable to a panel-mount switch in the enclosure can reach it.
  - J8 becomes the Adafruit 5644 boost breakout. In the schematic select J8 and use *Change Symbol* with `uv254:adafruit_tps61040_boost`: its pins sit where the 4-pin connector's did, so the wiring is kept. *Update PCB* then gives J8 the footprint `uv254:Adafruit_TPS61040_Boost_5644`, with pads exactly where J8's are now. Leave the breakout's 10.16 x 15.24 mm clear beside them; it lies 2.54 mm above the board on its header.
    - The footprint now has the breakout's mounting hole (2.7 mm, M2.5, with a 6 mm copper keep-out on both sides). On the board, J8 still has the earlier copy without it: select J8 and run *Update Footprints from Library*, then move any tracks out of the keep-out. The screw head is on the other side of the board, so keep parts there clear too.
  - Re-route. The long header carries A0-A5 and SPI; the short header carries I2C and the display and LED control pins (5-13).
  - Coordinates in the items below were taken before this change. Re-check any near U2.
  - Done when `kicad-cli pcb drc --schematic-parity` shows 0 parity issues and 0 unconnected items.
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
  - SW1, the power switch: C&K OS102011MA1QN1 (footprint `Button_Switch_THT:SW_Slide_SPDT_Angled_CK_OS102011MA1Q`)
  - J12, 2-pin 0.1 in header for the panel switch's wires (or a mating socket/housing). The panel switch itself (e.g. a rocker) is the owner's choice; prefer gold-plated contacts, since it only carries the EN pull-up's microamps.
  - J8: the Adafruit 5644 boost breakout (it comes with its header), if it's fitted instead of U6 and its parts, plus an M2.5 screw, nut and 2.5 mm spacer for its mounting hole. Adafruit's breakout uses a 10 µH 1008 inductor (MPL2520S100MWT) with the 400 mA TPS61040, a useful reference when choosing L1.
  - If U2 uses the mounting-hole footprint: 4 M2.5 x 11 mm standoffs (11 mm matches the socket plus header stack) with M2.5 screws, or nuts for male-female standoffs.
  - U2, now an Adafruit Feather (footprint `uv254:Adafruit_Feather_on_socket`; `part_for()` matched the Pro Micro by its `nice_nano` footprint). Also list the female headers it plugs into (16-pin and 12-pin, 0.1 in).

  Add them to `PARTS` and `part_for()`, run `scripts/make-bom.py`, and commit
  `hardware/BOM.md`, `hardware/bom.csv` and `docs/bom/index.html`.
  - **L1** has no part chosen yet. It needs a saturation current of at least about 0.35 A (the TPS61041 switch peak is about 0.3 A). Few 1008-size 15 µH parts reach that, so the footprint may need to grow.
  - **C1:** at 12 V an 0805 10 µF/25 V ceramic keeps only part of its capacitance. Pick one with a usable value at 12 V.
- [ ] **Delete the dangling 3V3 stub** on B.Cu at (60.16, 40.10)-(60.26, 40.20). DRC reports it as `track_dangling`.

## Should do

- [ ] **Separate the emitter's ground return from the ADS filter caps.**
  - A 0.7 mm front trace runs from the GND via by J2 pin 6 at (11.70, 22.80) to the ground pads of C9/C10.
  - Delete the segment (11.70, 22.80)-(17.40, 22.80). The via stays in the fill, and C9/C10 stay grounded through their back traces.
  - Re-run DRC to confirm 0 unconnected.
- [ ] **EN** (J8 pin 4 at 54.92, 42.80 to U6 pin 4 / R3) runs 16 mm up the back at x 54.9, a second cut beside BAT. It's below the display lines, so it's minor. Shorten it or run it right next to BAT so the two cuts merge.

## Owner to decide

- [ ] **J4 (optional SSD1306 OLED header) sits under the display.** Its courtyard overlapping U5 is the remaining DRC error. Move it out, put it on the back, or drop it.
- [ ] **Display support.** A footprint with the holes now exists: `uv254:st7789_200in_240x320_WithMountingHoles` (2.7 mm, M2.5, 6 mm copper keep-outs). With U5 at (118, 36) rotated 180 the holes land at about (118.8, 12.5), (118.8, 41.7), (60.0, 12.5) and (60.0, 41.7), all clear on the board as of 2026-11-23. To use it, set U5's footprint to the variant and update the PCB; it takes 4 M2.5 screws and nuts with 2.5 mm spacers. Measure the module first (below).
  - The 62 mm GMT020 module is held only by its 8-pin header at the button end. Its far end floats 2.5 mm above the board.
  - Its corner holes (on Dwgs.User in the footprint) are at about (54.45, 7.06), (54.45, 36.31), (113.25, 7.06) and (113.25, 36.31). Traces pass through both far-end spots.
  - The footprint and 3D model dimensions are photo estimates (±0.3 mm). Caliper-check a module first, then update `D2` in `lib/uv254.3dshapes/make_models.py` and `lib/uv254.pretty/st7789_200in_240x320.kicad_mod`.
- [ ] **Boost output margin.**
  - R10/R16 set V_LED to 1.233 × (1 + 1.40M/160k) ≈ 12.0 V.
  - With the TPS61041's 250 mA switch limit, a rough estimate is about 30 mA at 12 V from 3.3 V. The emitter v0.5 LED takes about 24-26 mA while on, so there's little margin.
  - The TPS61040 has the same pinout and a 400 mA limit (about 45 mA). Check TI's output-current curves.
- [ ] **3V3 load.**
  - While the LED is on, the boost draws about 120 mA from 3V3, on top of the backlight, microSD and MCU. The Feather's 3.3 V regulator (typically 500-600 mA) supplies all of it; on an ESP32-S3, Wi-Fi transmit peaks share that budget.
  - That load switches at the LED rate on the same 3V3 that feeds the detector (J1 pin 1) and U3. If it shows up in measurements, filter the detector's supply (RC or ferrite plus cap).
- [ ] **Ground fill clearance** is 0.5 mm, which can't fit between 0.1 in header pins, so U2's columns, J1/J2 and the test headers act as walls in both fills. A clearance of 0.25 mm lets thin necks through. Optional.

## Other open items

- [ ] **Firmware:** write the Arduino firmware for the Feather, using the pin map in [`v0.4-design.md`](v0.4-design.md#feather-pins) (re-assigned 2026-11-23 to suit the layout: buttons on 5, 6 and A2; display RST/DC/CS/BL_OFF on 9-12; SD_CS on RX; ADS_ALERT on TX; LED drive on A1 and disable on A0).
  - On the ESP32-S3, drive `PIN_I2C_POWER` high in `setup()`.
  - The CircuitPython `firmware/uv-control/v0.4/code.py` is out of date (first-draft pins, Pro Micro).
- [ ] **Schematic:** ERC has no errors. Remaining warnings:
  - library mismatch for U5 (`st7789`) and U6 (`TPS61041DBV`); fix with *Update Symbols from Library*
  - `EN` is both a local and a global label
- [ ] **Footprints:** R17, R20, R22 and R24 differ from their `Resistor_SMD` library copies (DRC warnings). Update them from the library unless the difference is deliberate.
- [ ] **Two starved thermals** (DRC):
  - J7 pad 1's front-fill connection goes to an isolated island. Harmless, since the pad connects through its back trace.
  - R16 pad 2 has one spoke. It's also tied to U6 pin 2 by a trace.
- [ ] **After any board change:** run `scripts/render-images.sh uv-control` (README images) and `scripts/make-bom.py`, and commit their output with the change.

## Done

2026-11-23:

- [x] Feather pins re-assigned to suit the layout (schematic labels and the board's U2 pad nets; board-schematic parity 0). Spare: A3, A4, 13.

- [x] Schematic: U2 is an Adafruit Feather (`uv254:feather`, pin map in `v0.4-design.md`). J9/J11 (battery) are removed, since the Feather has its own charger and jack, and so is the PWR_FLAG on 3V3 (the Feather's 3V pin drives it). The BAT cut in the back ground goes with them once the PCB is updated.
- [x] Symbol, footprint and 3D model for Adafruit's 5644 boost breakout, for J8 (`uv254:adafruit_tps61040_boost`, `uv254:Adafruit_TPS61040_Boost_5644`).
- [x] Footprint variant with the Feather's mounting holes: `uv254:Adafruit_Feather_on_socket_WithMountingHoles`.
- [x] U2's footprint is `uv254:Adafruit_Feather_on_socket`, with Adafruit's nRF52840 Feather model (MIT) on 8.5 mm sockets.
- [x] Power switch SW1 added: it pulls the Feather's EN pin to GND (net `PWR_EN`) to turn the whole board off. J12, in parallel, takes a panel-mount switch (e.g. a rocker).
- [x] `v0.4-design.md` updated for the boost, the test headers, the Feather and the power switch.

2026-11-21, from the first layout review:

- [x] V_LED no longer crosses the analog corner. It comes from the on-board boost and runs along the bottom and left edges to J2/J5, and J8 sits beside the boost.
- [x] U3's ground pins have vias into the main front ground fill; the front island around U3 is gone.
- [x] DET_1V8's run to U2 pin 19 is on the back, clear of SCK.
- [x] Removed the GND via drilled into J5 pad 5 and the dangling via on A0 under U3.
- [x] U6 pin 2 (GND) connected.
