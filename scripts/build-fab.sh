#!/usr/bin/env bash
# Build a fabrication package for one board with kicad-cli.
#
#   scripts/build-fab.sh <board> <version> [outdir]
#
#   <board>    uv-control | uv-detector | uv-emitter
#   <version>  e.g. v0.4 (used in file names)
#   [outdir]   default: build/<board>-<version>
#              to record a release in git: hardware/<board>/fab/<version>
#
# Gerber layers and options come from the settings saved in the board
# (File > Plot in the PCB editor), so what you set up in KiCad is what CI builds.
# CI runs this same script when a <board>/<version> tag is pushed.
set -euo pipefail

usage() { sed -n '2,13p' "$0" | sed -E 's/^# ?//'; exit "${1:-0}"; }
[[ ${1:-} == -h || ${1:-} == --help ]] && usage 0
[[ $# -ge 2 && $# -le 3 ]] || usage 1

board=$1
version=$2
root=$(cd "$(dirname "$0")/.." && pwd)
dir="$root/hardware/$board"
pcb="$dir/$board.kicad_pcb"
sch="$dir/$board.kicad_sch"
[[ -f $pcb && -f $sch ]] || { echo "error: no KiCad project at hardware/$board" >&2; exit 1; }
out=$(mkdir -p "${3:-$root/build/$board-$version}" && cd "${3:-$root/build/$board-$version}" && pwd)
name="$board-$version"

# Unlike the Plot dialog, kicad-cli applies the board's "Drill marks" setting to
# Gerber output. Refuse rather than put drill marks on the copper layers.
if grep -qE '\(drillshape [1-9]' "$pcb"; then
  echo "error: hardware/$board has 'Drill marks' enabled in its plot settings." >&2
  echo "       Set Drill marks to None in File > Plot, then save the board." >&2
  exit 1
fi

rm -rf "$out/gerbers" "$out/reports" "$out/$name"-*
mkdir -p "$out/gerbers" "$out/reports"
echo "kicad-cli $(kicad-cli version): building $name -> ${out#"$root"/}"

run() { "$@" >/dev/null || { echo "error: failed: $*" >&2; exit 1; }; }

# Checks (reports only; violations don't stop the build)
run kicad-cli sch erc --format report --severity-all -o "$out/reports/erc.rpt" "$sch"
run kicad-cli pcb drc --format report --severity-all --schematic-parity -o "$out/reports/drc.rpt" "$pcb"

# Gerbers + drill, plus a zip ready to upload to the fab house
run kicad-cli pcb export gerbers --board-plot-params -o "$out/gerbers/" "$pcb"
run kicad-cli pcb export drill --format excellon --excellon-units mm -o "$out/gerbers/" "$pcb"
(cd "$out/gerbers" && python3 -m zipfile -c "../$name-gerbers.zip" ./*)

# Assembly and documentation
run kicad-cli sch export bom --group-by "Value,Footprint" --ref-range-delimiter "" \
  --fields 'Reference,Value,Footprint,${QUANTITY},${DNP},Description' \
  --labels 'Refs,Value,Footprint,Qty,DNP,Description' \
  -o "$out/$name-bom.csv" "$sch"
run kicad-cli pcb export pos --format csv --units mm --side both -o "$out/$name-pos.csv" "$pcb"
run kicad-cli sch export pdf -o "$out/$name-schematic.pdf" "$sch"

# Interactive HTML BOM, if the InteractiveHtmlBom tool is installed
if command -v generate_interactive_bom >/dev/null 2>&1; then
  INTERACTIVE_HTML_BOM_NO_DISPLAY=1 run generate_interactive_bom --no-browser \
    --dest-dir "$out" --name-format "$name-ibom" "$pcb"
else
  echo "note: InteractiveHtmlBom not installed; skipping the interactive BOM"
fi

grep -hE '^ ?\*\* (ERC messages|Found [0-9]+ (DRC|unconnected|Footprint))' "$out"/reports/*.rpt | sed 's/^/  /' || true
echo "done: $(find "$out" -type f | wc -l) files in ${out#"$root"/}"
