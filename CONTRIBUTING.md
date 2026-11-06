# Working on uv254

## KiCad version

Everyone uses **KiCad 10.0.x** (any 10.0 point release).

KiCad upgrades files when it saves them, and older versions can't open the
result. If one person saves with a newer major version, nobody else can open
the board. Move to a new major version together, in one commit that does
nothing else. CI uses the same version (the `kicad/kicad:10.0` image in
`.github/workflows/kicad.yml`).

If the 3D viewer shows bare boards with no parts, your KiCad install has no 3D
model library; AppImage builds, for example, don't include one. Install
KiCad's 3D models and point `KICAD10_3DMODEL_DIR` at them in *Preferences >
Configure Paths*. Paths in the boards written as `${KICAD6_3DMODEL_DIR}` or
`${KICAD8_3DMODEL_DIR}` are fine, because KiCad 10 resolves them to the same
place.

## Libraries

- **Standard parts** come from KiCad's built-in libraries (`Device`,
  `Resistor_SMD`, `Package_SO`, ...). Use them whenever they fit.
- **Custom parts** go in the shared project library: `lib/uv254.kicad_sym`
  (symbols) and `lib/uv254.pretty/` (footprints). Every board refers to it by
  the nickname `uv254`, through its own `sym-lib-table` and `fp-lib-table` with
  the path `${KIPRJMOD}/../../lib/...`.
- **Don't add project parts to your global (personal) library tables**, and
  don't point the project at files outside the repository. Anything that isn't
  in the repo won't exist for the next person who clones it.
- **3D models** for custom footprints go in `lib/uv254.3dshapes/` (create it
  when you add the first one). Reference them from the footprint as
  `${KIPRJMOD}/../../lib/uv254.3dshapes/<name>.step`.
- When you add a symbol, set its **Footprint** field to the matching footprint
  (`uv254:<name>` or a standard one) and fill in **Datasheet**.
- After changing a part in `lib/`, update the boards that use it:
  *Tools > Update Symbols from Library* in the schematic editor and
  *Tools > Update Footprints from Library* in the PCB editor. Commit the library
  change and the board updates together.

See [lib/README.md](lib/README.md) for what's in the library.

## Working together on KiCad files

KiCad files are text, but git can't merge two people's edits to the same
schematic or board in any useful way. So:

1. **One person edits a given board at a time.** Say so (in an issue or chat)
   before you start on a board.
2. **Pull before you open KiCad, and close KiCad before you pull, switch
   branches or check out a tag.** KiCad doesn't notice files changing on disk,
   and saving would overwrite what git just brought in.
3. Work on a **branch** and open a **pull request** to `main`. Keep branches
   short-lived.
4. Commit the schematic and the board together after *Update PCB from
   Schematic*, so they never disagree in history.
5. Per-user files are already git-ignored (`*.kicad_prl`, `fp-info-cache`,
   `*-backups/`, lock files). If `git status` shows something like that, don't
   commit it.

## Checks

On every push and pull request, CI runs ERC and DRC (with schematic parity) on
all three boards. The reports are on the run's summary page and attached as
artifacts.

The checks are **report-only** for now, because the current designs still have
known violations. To make them blocking once a board is clean, add
`--severity-error --exit-code-violations` to its `kicad-cli` calls in
`.github/workflows/kicad.yml`.

To run them locally:

```sh
kicad-cli sch erc --severity-all hardware/uv-detector/uv-detector.kicad_sch
kicad-cli pcb drc --severity-all --schematic-parity hardware/uv-detector/uv-detector.kicad_pcb
```

## Releasing a board revision

Versions are per board: `v<major>.<minor>`, with an optional `_A`, `_B` suffix
for variants of a revision (as with `uv-detector/v0.2_A`). Any change that gets
fabricated gets a new version.

1. Update the version wherever it appears on the board: silkscreen text and the
   title block (*File > Page Settings* in both the schematic and PCB editors).
2. Run the checks above and fix what matters.
3. Build the fab package into the board's `fab/` folder:
   ```sh
   scripts/build-fab.sh uv-detector v0.4 hardware/uv-detector/fab/v0.4
   ```
   It builds the gerbers and drill file (from the board's saved *File > Plot*
   settings), a ready-to-upload gerber zip, BOM, pick-and-place file, schematic
   PDF and ERC/DRC reports. It also builds an interactive BOM if
   [InteractiveHtmlBom](https://github.com/openscopeproject/InteractiveHtmlBom)
   is installed.
4. Commit the design and `fab/v0.4/` together, then add an annotated tag. Its
   message becomes the release notes:
   ```sh
   git commit -m "uv-detector v0.4: fab release"
   git tag -a uv-detector/v0.4 -m "uv-detector v0.4" -m "What changed and why."
   git push origin main uv-detector/v0.4
   ```
5. CI rebuilds the package from the tag and publishes a GitHub Release with
   the files. Order from the committed `fab/v0.4/` files. CI is a cross-check,
   since its KiCad point release may differ slightly from yours.

Push tags one or two at a time: GitHub doesn't start workflows when more than
three tags are pushed at once.
