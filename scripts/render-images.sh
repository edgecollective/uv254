#!/usr/bin/env bash
# Render a board's schematic, PCB layout and 3D views, and show them in its README.
#
#   scripts/render-images.sh [--fast] <board>...
#
#   <board>   uv-control | uv-detector | uv-emitter (one or more)
#   --fast    flat-shaded 3D renders: seconds instead of about a minute per
#             view. Good for a quick look; commit the full renders.
#
# Writes to hardware/<board>/docs/:
#   <board>-schematic.pdf, .png   schematic (one PNG per sheet if there are several)
#   <board>-pcb-front.png, -back  copper and silkscreen; the back is mirrored
#   <board>-3d-front.png, -back   3D renders; the back is seen from below
# and rewrites the section between the render-images markers in
# hardware/<board>/README.md (added above "## Revisions" the first time).
#
# Files are only replaced when the picture changes, so re-running on an
# unchanged board leaves git clean (and skips the slow 3D renders).
#
# Needs kicad-cli (KiCad 10), inkscape, ImageMagick and poppler-utils.
set -euo pipefail

usage() { sed -n '2,20p' "$0" | sed -E 's/^# ?//'; exit "${1:-0}"; }
fast=0
boards=()
for arg; do
  case $arg in
    -h|--help) usage 0 ;;
    --fast) fast=1 ;;
    -*) usage 1 ;;
    *) boards+=("$arg") ;;
  esac
done
[[ ${#boards[@]} -gt 0 ]] || usage 1

for tool in kicad-cli inkscape convert compare identify pdftoppm pdfinfo python3; do
  command -v "$tool" >/dev/null || { echo "error: $tool not found (see the header of $0)" >&2; exit 1; }
done

root=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

# Pin the colour theme so the images don't depend on anyone's KiCad preferences.
theme=_builtin_default
pcb_bg='#001023'   # the PCB editor background in that theme
# ImageMagick stamps PNGs with the time; leave that out so unchanged images stay byte-identical.
png_out=(-define png:exclude-chunks=date,time)

# Run a command quietly, showing its output only if it fails.
quiet() {
  "$@" >"$tmp/log" 2>&1 || { cat "$tmp/log" >&2; echo "error: $1 failed" >&2; exit 1; }
}

# True if two images have the same pixels.
same_image() {
  local diff
  diff=$(compare -metric AE -fuzz 1% "$1" "$2" null: 2>&1) || true
  [[ $diff == 0 ]]
}

# Copy a new image into place unless the existing one has the same pixels.
# Sets changed=1 when it copies.
install_image() { # <new> <dest>
  if [[ -f $2 ]] && same_image "$1" "$2"; then
    return 0
  fi
  cp "$1" "$2"
  echo "  updated ${2#"$root"/}"
  changed=1
}

render_layout() { # <pcb> <front|back> <out.png>
  local pcb=$1 side=$2 out=$3 opts=()
  if [[ $side == front ]]; then
    opts=(-l Edge.Cuts,F.Cu,F.Silkscreen)
  else
    opts=(-l Edge.Cuts,B.Cu,B.Silkscreen --mirror)
  fi
  quiet kicad-cli pcb export svg --mode-single --page-size-mode 2 --exclude-drawing-sheet \
    --theme "$theme" "${opts[@]}" -o "$tmp/pcb-$side.svg" "$pcb"
  quiet inkscape --export-type=png --export-filename="$tmp/pcb-$side.png" --export-width=1600 \
    --export-background="$pcb_bg" --export-background-opacity=1 "$tmp/pcb-$side.svg"
  convert "$tmp/pcb-$side.png" -bordercolor "$pcb_bg" -border 40 "${png_out[@]}" "$out"
}

# 3D view of one side, written straight to <dest>.
#
# The high-quality renderer samples randomly, so two renders of the same board
# differ slightly and can't be compared. The basic render is repeatable, so its
# pixel signature goes into the PNG's comment as a fingerprint of how the board
# looks. While that hasn't changed, the existing image is kept and the slow
# render is skipped.
render_3d() { # <pcb> <front|back> <dest>
  local pcb=$1 side=$2 dest=$3 base="$tmp/3d-$2" kside=top mode=high key old=""
  [[ $side == back ]] && kside=bottom
  [[ $fast == 1 ]] && mode=basic
  quiet kicad-cli pcb render --side "$kside" --quality basic --background transparent \
    -w 1600 -h 1200 -o "$base-basic.png" "$pcb"
  key=$(identify -format '%#' "$base-basic.png")
  [[ -f $dest ]] && old=$(identify -format '%c' "$dest" 2>/dev/null || true)
  # A --fast run also keeps a high-quality image of the same board.
  if [[ $old == "high:$key" || $old == "$mode:$key" ]]; then
    return 0
  fi
  if [[ $mode == basic ]]; then
    cp "$base-basic.png" "$base.png"
  else
    echo "  rendering 3D $side view (about a minute)"
    quiet kicad-cli pcb render --side "$kside" --quality high --background transparent \
      -w 1600 -h 1200 -o "$base-high.png" "$pcb"
    # Post-processing leaves a faint haze in the transparent background. Cut it
    # away with the basic render's alpha, which has the same outline.
    convert "$base-high.png" -alpha extract "$base-a1.png"
    convert "$base-basic.png" -alpha extract "$base-a2.png"
    convert "$base-a1.png" "$base-a2.png" -compose darken -composite "$base-alpha.png"
    convert "$base-high.png" -alpha off "$base-alpha.png" -compose copy_opacity -composite "$base.png"
  fi
  convert "$base.png" -trim +repage -bordercolor none -border 24 -set comment "$mode:$key" \
    "${png_out[@]}" "$dest"
  echo "  updated ${dest#"$root"/}"
}

for board in "${boards[@]}"; do
  dir="$root/hardware/$board"
  pcb="$dir/$board.kicad_pcb"
  sch="$dir/$board.kicad_sch"
  [[ -f $pcb && -f $sch && -f $dir/README.md ]] ||
    { echo "error: no KiCad project and README at hardware/$board" >&2; exit 1; }
  docs="$dir/docs"
  new="$tmp/$board"
  mkdir -p "$docs" "$new"
  rm -f "$new"/*
  echo "$board:"

  # 1. Schematic: PDF, and a PNG of each sheet. The PDF embeds its creation
  # time, so it's only replaced when a sheet image changed.
  quiet kicad-cli sch export pdf --theme "$theme" -o "$new/$board-schematic.pdf" "$sch"
  pages=$(pdfinfo "$new/$board-schematic.pdf" | awk '/^Pages:/ {print $2}')
  sheets=()
  changed=0
  for ((p = 1; p <= pages; p++)); do
    name="$board-schematic.png"
    [[ $pages == 1 ]] || name="$board-schematic-$p.png"
    pdftoppm -png -r 200 -f "$p" -l "$p" -singlefile "$new/$board-schematic.pdf" "$new/${name%.png}"
    install_image "$new/$name" "$docs/$name"
    sheets+=("$name")
  done
  if [[ $changed == 1 || ! -f $docs/$board-schematic.pdf ]]; then
    cp "$new/$board-schematic.pdf" "$docs/"
    echo "  updated ${docs#"$root"/}/$board-schematic.pdf"
  fi
  # Sheet images left over from when the schematic had more sheets.
  for f in "$docs/$board"-schematic*.png; do
    [[ -f $new/${f##*/} ]] || { rm "$f"; echo "  removed ${f#"$root"/}"; }
  done

  # 2. PCB layout, front and back.
  for side in front back; do
    render_layout "$pcb" "$side" "$new/$board-pcb-$side.png"
    install_image "$new/$board-pcb-$side.png" "$docs/$board-pcb-$side.png"
  done

  # 3. 3D views, front and back.
  for side in front back; do
    render_3d "$pcb" "$side" "$docs/$board-3d-$side.png"
  done

  # 4. README section.
  python3 - "$dir/README.md" "$board" "${sheets[@]}" <<'EOF'
import re
import sys

readme, board, sheets = sys.argv[1], sys.argv[2], sys.argv[3:]
text = open(readme).read()
m = re.match(r'# (.+)', text)
title = m.group(1).strip() if m else board
start = '<!-- render-images:start -->'
end = '<!-- render-images:end -->'

pdf = f'docs/{board}-schematic.pdf'
lines = [
    start,
    f'<!-- Generated by scripts/render-images.sh. Edits between these markers are overwritten. -->',
    '',
    '## Schematic',
    '',
]
for k, png in enumerate(sheets, 1):
    alt = f'{title} schematic' + (f', sheet {k}' if len(sheets) > 1 else '')
    lines += [f'[![{alt}](docs/{png})]({pdf})', '']
lines += [
    f'Click the image for the [PDF]({pdf}).',
    '',
    '## Board layout',
    '',
    'Copper and silkscreen. The back is mirrored, as seen from below.',
    '',
    '| Front | Back |',
    '|:---:|:---:|',
    f'| ![{title} PCB, front](docs/{board}-pcb-front.png) '
    f'| ![{title} PCB, back](docs/{board}-pcb-back.png) |',
    '',
    '## 3D view',
    '',
    '| Front | Back |',
    '|:---:|:---:|',
    f'| ![{title} 3D render, front](docs/{board}-3d-front.png) '
    f'| ![{title} 3D render, back](docs/{board}-3d-back.png) |',
    '',
    f'Images of the current design, made with `scripts/render-images.sh {board}`.',
    'Re-run it after changing the board.',
    end,
]
section = '\n'.join(lines)

if start in text and end in text:
    new = re.sub(re.escape(start) + r'.*?' + re.escape(end), lambda _: section, text, flags=re.S)
elif '\n## Revisions' in text:
    new = text.replace('\n## Revisions', '\n' + section + '\n\n## Revisions', 1)
else:
    new = text.rstrip('\n') + '\n\n' + section + '\n'
if new != text:
    open(readme, 'w').write(new)
    print(f'  updated hardware/{board}/README.md')
EOF
done
