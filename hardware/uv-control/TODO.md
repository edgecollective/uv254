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
- Releases are tagged by the owner (latest: `uv-control/v0.5`). Follow CONTRIBUTING.md's release steps.

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

## Status

**v0.5 released 2026-11-23**: tag `uv-control/v0.5`, fab files in
[`fab/v0.5`](fab/v0.5), with detector and emitter v0.5. (v0.4, tagged the same day, is the
same design.) The items below are for bring-up and the next revision.

## Bring-up checks on the v0.5 boards

- [ ] **Boost output margin.**
  - R10/R16 set V_LED to 1.233 × (1 + 1.40M/160k) ≈ 12.0 V.
  - With the TPS61041's 250 mA switch limit, a rough estimate is about 30 mA at 12 V from 3.3 V. The emitter v0.5 LED takes about 24-26 mA while on, so there's little margin.
  - The TPS61040 has the same pinout and a 400 mA limit (about 45 mA); Adafruit's 5644 breakout (J8) uses it.
- [ ] **3V3 load.** While the LED is on, the boost draws about 120 mA from 3V3, on top of the backlight, microSD and MCU; the Feather's regulator (typically 500-600 mA) supplies all of it. That load switches at the LED rate on the same 3V3 that feeds the detector (J1 pin 1) and U3; if it shows up in measurements, filter the detector's supply.
- [ ] **SW1 positions.** Check which slider position joins pads 1 and 2 (off) before marking ON/OFF on the case.
- [ ] **L1.** Confirm the Murata LQH32PN150MN0L's saturation current (distributors list about 0.6 A) in Murata's datasheet.

## For the next revision

- [ ] **Boost input cap.** C2 (65.5, 19-21) is 8 mm from L1's input (72.9, 22). Move it beside L1 pad 1, with its GND toward U6 pin 2.
- [ ] **Long runs on the front copper** cut the front ground under the back-side buses (y 33-38): EN at x 70.5 (29 mm), 3V3 at x 61.3 (24 mm) and x 93.7 (16 mm), V_LED at x 69.6 (17 mm). Keep them on the back with short front hops, or move the boost cluster down next to J8.
- [ ] **J4 (optional OLED header) sits under the display**; their courtyards overlap (DRC error). Don't fit J4 on v0.5; move it out from under U5 or drop it.
- [ ] **Display support.** `uv254:st7789_200in_240x320_WithMountingHoles` adds the module's four corner holes (2.7 mm, M2.5, 6 mm copper keep-outs); with U5 at (118, 36) rotated 180 they land at about (118.8, 12.5), (118.8, 41.7), (60.0, 12.5) and (60.0, 41.7). The positions are photo estimates (±0.3 mm): caliper-check a module, update `D2` in `lib/uv254.3dshapes/make_models.py` and the footprints, then switch U5 to the variant.
- [ ] **One-spoke ground connections** (DRC starved thermals): U5 pin 8 (back island), SW1 pin 1, J9 pin 2. Each also connects through the other layer.
- [ ] **Ground fill clearance** is 0.5 mm, too much to pass between 0.1 in header pins. 0.25 mm lets thin necks through. Optional.
- [ ] **AIN3 and AIN0** run a few mm beside SDA/SCL and ADS_ALERT right at U3's pins. Low impact (330 nF / 100 nF on the inputs).

## Other open items

- [ ] **Firmware:** write the Arduino firmware for the Feather, using the pin map in [`v0.4-design.md`](v0.4-design.md#feather-pins) (buttons on 5, 6 and A2; display RST/DC/CS/BL_OFF on 9-12; SD_CS on RX; ADS_ALERT on TX; LED drive on A1 and disable on A0).
  - On the ESP32-S3, drive `PIN_I2C_POWER` high in `setup()`.
  - The CircuitPython `firmware/uv-control/v0.4/code.py` is out of date (first-draft pins, Pro Micro).
- [ ] **Schematic:** ERC has no errors. Remaining warnings: library mismatch for U5 (`st7789`) and U6 (`TPS61041DBV`), and `EN` is both a local and a global label.
- [ ] **Footprints:** R17, R20, R22 and R24 differ from their `Resistor_SMD` library copies (DRC warnings). Update them from the library unless the difference is deliberate.
- [ ] **After any board change:** run `scripts/render-images.sh uv-control` (README images) and `scripts/make-bom.py`, and commit their output with the change.

## Done

2026-11-23, v0.4 release (renumbered v0.5 the same day, with the detector and emitter v0.5):

- [x] PCB updated to the Feather schematic, placed and routed: DRC 0 unconnected, 0 schematic parity; ERC 0 errors.
- [x] Review fixes: V_LED reconnected; the microSD shield fill joined to GND; stray SD_CS and 3V3 copper removed; the Feather's GND pin stitched with five vias; R8 moved next to C10, so the long run to the emitter corner carries the low-impedance EMIT_LED_CURRENT along the left edge; the emitter's ground no longer tied to the ADS filter caps; C1 next to D3; FB moved off the switch side; SW 0.3 mm.
- [x] BOM: every fitted part has a part number (`scripts/make-bom.py`), including L1 (Murata LQH32PN150MN0L, 15 µH 1210) and the Feather's 8.5 mm sockets (Sullins PPTC161LFBN-RC, PPTC121LFBN-RC).
- [x] `UV-Control-${VERSION}` on the front silkscreen; PWR_FLAG on BAT.

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
