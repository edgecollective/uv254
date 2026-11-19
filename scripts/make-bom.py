#!/usr/bin/env python3
"""Build the bill of materials for one set of uv254 boards from the schematics.

  scripts/make-bom.py

Writes:
  hardware/BOM.md         per-board tables, cables, open items
  hardware/bom.csv        order list for one set, by manufacturer part number
  docs/bom/index.html     the same as a web page (GitHub Pages), with a
                          sets multiplier and a CSV download

The schematics don't carry part numbers, so PARTS below holds them. A part the
script doesn't recognise stops it with a message: add it to PARTS and to
part_for(). Files are only rewritten when their content changes (the date line
aside), so re-running on unchanged schematics leaves git clean.

Needs kicad-cli (KiCad 10) on your PATH. Run from anywhere in the repository.
"""
import csv, datetime, html, io, json, os, re, shutil, subprocess, sys, tempfile, urllib.parse
from collections import OrderedDict, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOARDS = [('uv-detector', 'UV-Detector'), ('uv-emitter', 'UV-Emitter'), ('uv-control', 'UV-Control')]
SHORT = {'uv-detector': 'detector', 'uv-emitter': 'emitter', 'uv-control': 'control'}
REPO_URL = 'https://github.com/edgecollective/uv254'
PAGE_URL = 'https://edgecollective.io/uv254/bom/'

# id: (description, manufacturer, MPN, where to buy if not Digi-Key, note)
PARTS = OrderedDict([
    # resistors: 1 %, 0805
    ('R_10k',  ('10 kΩ 1% 0805', 'Yageo', 'RC0805FR-0710KL', '', '')),
    ('R_4k7',  ('4.7 kΩ 1% 0805', 'Yageo', 'RC0805FR-074K7L', '', '')),
    ('R_4k99', ('4.99 kΩ 1% 0805', 'Yageo', 'RC0805FR-074K99L', '', '')),
    ('R_5k49', ('5.49 kΩ 1% 0805', 'Yageo', 'RC0805FR-075K49L', '', '')),
    ('R_1k',   ('1 kΩ 1% 0805', 'Yageo', 'RC0805FR-071KL', '', '')),
    ('R_24k9', ('24.9 kΩ 1% 0805', 'Yageo', 'RC0805FR-0724K9L', '', '')),
    ('R_24r9', ('24.9 Ω 1% 0805', 'Yageo', 'RC0805FR-0724R9L', '', 'LED current sense')),
    ('R_43k2', ('43.2 kΩ 1% 0805', 'Yageo', 'RC0805FR-0743K2L', '', '')),
    ('R_100k', ('100 kΩ 1% 0805', 'Yageo', 'RC0805FR-07100KL', '', '')),
    ('R_1M',   ('1 MΩ 1% 0805', 'Yageo', 'RC0805FR-071ML', '', '')),
    # capacitors: 0805
    ('C_10p',  ('10 pF 50 V C0G 0805', 'Samsung', 'CL21C100JBANNNC', '', '')),
    ('C_100p', ('100 pF 50 V C0G 0805', 'Samsung', 'CL21C101JBANNNC', '', '')),
    ('C_100n', ('100 nF 50 V X7R 0805', 'Samsung', 'CL21B104KBCNNNC', '', '')),
    ('C_330n', ('330 nF 50 V X7R 0805', 'Samsung', 'CL21B334KBFNNNE', '',
                'long factory lead time; Murata GRM219R71H334KA88D is an alternate')),
    ('C_1u',   ('1 µF 25 V X7R 0805', 'Samsung', 'CL21B105KAFNNNE', '',
                'CX2 is on +12V: keep it 25 V or more')),
    ('C_2u2',  ('2.2 µF 25 V X7R 0805', 'Samsung', 'CL21B225KAFNFNE', '', '')),
    ('C_10u',  ('10 µF 16 V X5R 0805', 'Samsung', 'CL21A106KOQNNNE', '', '')),
    # semiconductors
    ('PD',     ('UV-C photodiode, 220-280 nm, TO-46 can (datasheet name SD008-2171-112)',
                'Advanced Photonix', '008-2171-112', '',
                'about $45; TO-46 has the same pin circle as the TO-18 footprint')),
    ('LED',    ('UV-C LED, 255 nm, 3535', 'Inolux', 'IN-C35PPCTGU0', '', 'about $20')),
    ('OPA',    ('Quad rail-to-rail op-amp, SOIC-14', 'Texas Instruments', 'OPA4340UA', '', '')),
    ('VREF',   ('1.8 V 0.1% voltage reference, SOT-23-6', 'Microchip', 'MCP1501T-18E/CHY', '', '')),
    ('BAT54S', ('Dual Schottky diode, series, SOT-23', 'Diodes Inc', 'BAT54S-7-F', '', '')),
    ('3904',   ('NPN transistor, SOT-23', 'onsemi', 'MMBT3904LT1G', '', '')),
    ('7002',   ('N-channel MOSFET 60 V, SOT-23', 'onsemi', '2N7002LT1G', '', '')),
    ('4148',   ('Switching diode, SOD-123', 'Diodes Inc', '1N4148W-7-F', '', '')),
    ('ADS',    ('16-bit 4-channel I2C ADC, VSSOP-10', 'Texas Instruments', 'ADS1115IDGSR', '', '')),
    ('555',    ('CMOS 555 timer, SOIC-8', 'Texas Instruments', 'TLC555IDR', '', '')),
    # connectors, switches, modules
    ('PH7',    ('JST PH 7-pin header, vertical', 'JST', 'B7B-PH-K-S(LF)(SN)', '', '')),
    ('PH6',    ('JST PH 6-pin header, vertical', 'JST', 'B6B-PH-K-S(LF)(SN)', '', '')),
    ('HDR',    ('0.1 in male header, 1x40, break to length', 'Sullins', 'PRPC040SAAN-RC', '',
                'one strip covers every 0.1 in header in a set')),
    ('SOCK6',  ('0.1 in female socket, 1x6', 'Sullins', 'PPTC061LFBN-RC', '', '')),
    ('SW12',   ('Tactile switch 12x12 mm, 7.3 mm, projected plunger', 'Omron', 'B3F-4055', '',
                'takes Omron B32 key caps')),
    ('SW6',    ('Tactile switch 6x6 mm, 5 mm', 'Omron', 'B3F-1020', '', '')),
    ('USD',    ('microSD socket', 'Hirose', 'DM3D-SF', '', '')),
    ('MCU',    ('Pro Micro nRF52840 module (nice!nano v2, or a SuperMini clone)', '', '',
                'nice!nano: Nice Keyboards; clones: AliExpress',
                'same module as Rook v0.4; usually ships with headers')),
    ('TFT',    ('1.54 in 240x240 ST7789 IPS SPI module, 8 pins in the order GND VCC SCL SDA RES DC CS BLK',
                '', '', 'AliExpress and similar', 'check the pin order before buying')),
    ('TFT2',   ('2.0 in 240x320 ST7789 IPS SPI module (GMT020-02-8P), 8 pins in the order GND VCC SCL SDA RST DC CS BL',
                '', '', 'Amazon (XIITIA, 2 per pack)', 'a 1.54 in 240x240 module with the same pin order fits the same holes')),
    ('OLED',   ('SSD1306 I2C OLED module, 4-pin (VCC GND SCL SDA)', '', '', 'AliExpress and similar', '')),
    # cables and loose parts (not in any schematic)
    ('PHR7',   ('JST PH 7-pin cable housing', 'JST', 'PHR-7', '', '')),
    ('PHR6',   ('JST PH 6-pin cable housing', 'JST', 'PHR-6', '', '')),
    ('LEAD',   ('JST PH pre-crimped lead, 6 in, 24 AWG, socket both ends', 'JST', 'ASPHSPH24K152', '',
                'or crimp SPH-002T-P0.5S terminals onto your own wire')),
    ('SHUNT',  ('0.1 in shunt (jumper)', 'Sullins', 'SPC02SYAN', '', '')),
])

# Buy links for parts that aren't on Digi-Key (the rest link to a Digi-Key search for the MPN)
BUY = {
    'TFT2': ('Amazon', 'https://www.amazon.com/XIITIA-Display-240x320-Interface-Arduino/dp/B0DFWLD38D'),
}

# Per set, not in any schematic: (part, qty, what it's for)
EXTRAS = [
    ('PHR7', 2, 'cables: control J1 to detector J2'),
    ('PHR6', 2, 'cables: control J2 to emitter J2'),
    ('LEAD', 13, 'cables: 7 + 6 wires'),
    ('SHUNT', 1, 'control: on J3'),
]

# Notes on particular references; OPTIONAL ones are left out of the order list
REFNOTE = {
    ('uv-detector', 'J1'): '0.1 in header in parallel with J2: optional',
    ('uv-emitter', 'J1'): '0.1 in socket in parallel with J2: optional',
    ('uv-control', 'J3'): 'LED drive select, with a shunt',
    ('uv-control', 'J4'): 'optional OLED header: not fitted',
    ('uv-control', 'R11'): 'ALERT pull-up: not fitted',
    ('uv-control', 'R13'): 'backlight pull-up: not fitted',
}
OPTIONAL = {('uv-detector', 'J1'), ('uv-emitter', 'J1')}

BOARD_NOTE = {
    'uv-detector': 'H1-H4 are M3 mounting holes (no part).',
    'uv-emitter': 'H1-H4 are M3 mounting holes (no part). The LED runs from +12V on J2 pin 4.',
    'uv-control': 'JP1 (solder jumper) and H1-H4 (mounting holes) have no part. J3 takes one '
                  'shunt (Sullins SPC02SYAN); use J3 or JP1, never both. The display and the Pro '
                  'Micro can be soldered straight to the board or plugged into 0.1 in sockets.',
}


def dk_url(mpn):
    """Digi-Key search for an exact MPN (it opens the product page when there's one match)."""
    return 'https://www.digikey.com/en/products/result?keywords=' + urllib.parse.quote(mpn, safe='')


def buy_link(part, mpn):
    """(label, url) for the Buy column, or None."""
    if part in BUY:
        return BUY[part]
    return ('Digi-Key', dk_url(mpn)) if mpn else None


def part_for(ref, value, fp):
    """Map one schematic part to a PARTS id (None: no part to buy)."""
    v = value.replace(' ', '').lower()
    pfx = re.match(r'[A-Z]+', ref).group(0)
    if pfx in ('R', 'RX'):
        return {'10k': 'R_10k', '4.7k': 'R_4k7', '4.99k': 'R_4k99', '5.49k': 'R_5k49', '1k': 'R_1k',
                '24.9k': 'R_24k9', '24.9': 'R_24r9', '43.2k': 'R_43k2', '100k': 'R_100k',
                '1meg': 'R_1M'}.get(v)
    if pfx in ('C', 'CX'):
        return {'10pf': 'C_10p', '100pf': 'C_100p', '0.1uf': 'C_100n', '0.1u': 'C_100n',
                '100n': 'C_100n', '100nf': 'C_100n', '330n': 'C_330n', '1uf': 'C_1u', '1u': 'C_1u',
                '2.2uf': 'C_2u2', '10u': 'C_10u', '10uf': 'C_10u'}.get(v)
    for key, part in [('JST_PH_B7B', 'PH7'), ('JST_PH_B6B', 'PH6'), ('PinHeader', 'HDR'),
                      ('PinSocket_1x06', 'SOCK6'), ('Tactile_12x12', 'SW12'), ('SW_PUSH_6mm', 'SW6'),
                      ('DM3D', 'USD'), ('ssd1306', 'OLED'), ('nice_nano', 'MCU'), ('st7789_200in', 'TFT2'),
                      ('st7789', 'TFT')]:
        if key in fp:
            return part
    return {'sd008-2171-112': 'PD', 'uvled': 'LED', 'opa4340ua': 'OPA', 'mcp1501-18xch': 'VREF',
            'bat54s': 'BAT54S', 'mmbt3904': '3904', '2n7002': '7002', '1n4148w': '4148',
            'ads1115idgs': 'ADS', 'tlc555': '555', 'mountinghole': None}.get(v, '?')


def natkey(ref):
    m = re.match(r'([A-Za-z]+)(\d+)', ref)
    return (m.group(1), int(m.group(2))) if m else (ref, 0)


def read_boards():
    kicad = shutil.which('kicad-cli')
    if not kicad:
        sys.exit('error: kicad-cli not found on PATH (KiCad 10)')
    boards, problems = [], []
    with tempfile.TemporaryDirectory() as tmp:
        for b, name in BOARDS:
            out = os.path.join(tmp, b + '.csv')
            subprocess.run([kicad, 'sch', 'export', 'bom', '--group-by', 'Value,Footprint',
                            '--ref-range-delimiter', '',
                            '--fields', 'Reference,Value,Footprint,${QUANTITY},${DNP}',
                            '--labels', 'Refs,Value,Footprint,Qty,DNP',
                            '-o', out, os.path.join(ROOT, 'hardware', b, b + '.kicad_sch')],
                           check=True, stdout=subprocess.DEVNULL)
            with open(os.path.join(ROOT, 'hardware', b, b + '.kicad_pro')) as f:
                version = json.load(f).get('text_variables', {}).get('VERSION', '')
            rows, pins = [], {}
            for r in csv.DictReader(open(out, encoding='utf-8')):
                for ref in r['Refs'].split(','):
                    part = part_for(ref, r['Value'], r['Footprint'])
                    if part == '?' or (part is None and 'MountingHole' not in r['Footprint']):
                        problems.append(f"{b} {ref}: value '{r['Value']}', footprint '{r['Footprint']}'")
                        continue
                    if part is None:
                        continue
                    if part == 'HDR':
                        pins[ref] = int(re.search(r'1x(\d+)', r['Footprint']).group(1))
                    fitted = r['DNP'].strip() != 'DNP' and (b, ref) not in OPTIONAL
                    rows.append((ref, part, fitted))
            rows.sort(key=lambda x: (list(PARTS).index(x[1]), natkey(x[0])))
            boards.append({'id': b, 'title': f'{name} {version}'.strip(), 'rows': rows, 'pins': pins})
    if problems:
        sys.exit('error: parts not in scripts/make-bom.py (add them to PARTS and part_for()):\n  '
                 + '\n  '.join(problems))
    return boards


def order_list(boards):
    """[(part, qty per set, used-on text)] in PARTS order."""
    qty, used = defaultdict(int), defaultdict(list)
    for bd in boards:
        refs = defaultdict(list)
        for ref, part, fitted in bd['rows']:
            if fitted:
                refs[part].append(ref)
        for part, rs in refs.items():
            qty[part] += 0 if part == 'HDR' else len(rs)
            used[part].append(f"{SHORT[bd['id']]} {' '.join(rs)}")
    if 'HDR' in used:
        qty['HDR'] = 1
    for part, n, what in EXTRAS:
        qty[part] += n
        used[part].append(what)
    return [(p, qty[p], '; '.join(used[p])) for p in PARTS if p in qty]


def board_groups(bd):
    """Rows of a board's table: (refs, qty, part, description, mfr/mpn text, notes)."""
    groups = OrderedDict()
    for ref, part, fitted in bd['rows']:
        note = REFNOTE.get((bd['id'], ref))
        groups.setdefault((part, fitted, note), []).append(ref)
    out = []
    for (part, fitted, note), refs in groups.items():
        desc, mfr, mpn, where, pnote = PARTS[part]
        if part == 'HDR':
            desc = '0.1 in male header, ' + ', '.join(f"{r} 1x{bd['pins'][r]}" for r in refs)
            mfr, mpn, pnote = 'Sullins', 'PRPC040SAAN-RC', 'cut from the 1x40 strip'
        if part == 'C_1u' and bd['id'] != 'uv-emitter':
            pnote = ''
        notes = '; '.join(x for x in (note, pnote) if x)
        out.append((refs, len(refs) if fitted else 0, part, desc, mfr, mpn, where, notes))
    return out


def csv_text(order):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['Qty per set', 'Manufacturer', 'MPN', 'Description', 'Used on', 'Source', 'Notes'])
    for part, q, used in order:
        desc, mfr, mpn, where, note = PARTS[part]
        w.writerow([q, mfr, mpn, desc, used, BUY[part][1] if part in BUY else where or 'Digi-Key', note])
    return buf.getvalue()


INTRO = '''Parts for one set: a detector, an emitter and a control board, plus the two
cables between them. Taken from the schematics on {date}:
{versions}, all still in progress, so re-check it against the schematics before
ordering.

The part numbers are suggestions; the schematics don't carry them yet. Any
equivalent passive works (same value and package, same or higher voltage and the
same dielectric, C0G where given). The Pro Micro module and the display aren't
sold by Digi-Key or Mouser.

Quantity 0 means the part has a footprint but isn't fitted, or is optional.
All resistors and capacitors are 0805. Order a few spares of the small parts:
cut-tape prices usually drop at 10 pieces.'''

CABLES = f'''Two cables, wired **pin 1 to pin 1** (ready-made JST PH cables are often
reversed, pin 1 to pin 6, and those don't work here):

| Cable | Ends | Parts |
|---|---|---|
| Control J1 to detector J2 | 7-pin JST PH | 2 JST [PHR-7]({dk_url('PHR-7')}) housings, 7 leads |
| Control J2 to emitter J2 | 6-pin JST PH | 2 JST [PHR-6]({dk_url('PHR-6')}) housings, 6 leads |

The leads are JST [ASPHSPH24K152]({dk_url('ASPHSPH24K152')}) (6 in, crimped at both
ends, pushed into the housings), 13 in all. Or crimp JST
[SPH-002T-P0.5S]({dk_url('SPH-002T-P0.5S')}) terminals onto 24-28 AWG wire.
All four links go to Digi-Key.'''

TODO = '''The control board has no source for **V_LED** (the emitter's +12V, J2 pin 4)
until the boost for the UV LED is added, so its parts aren't listed. Until then,
feed V_LED from a bench supply on J5 pin 4. (J5 pin 3, 5V, isn't connected to
anything else.)'''


def md_inline(s):
    """The little markdown used in the prose blocks, as HTML."""
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', s)
    return re.sub(r'`(.+?)`', r'<code>\1</code>', s)


def md_block_html(text):
    """Paragraphs and pipe tables from a prose block, as HTML."""
    out = []
    for block in text.split('\n\n'):
        lines = block.strip().split('\n')
        if lines[0].startswith('|'):
            cells = [[c.strip() for c in l.strip('|').split('|')] for l in lines if not l.startswith('|---')]
            head = ''.join(f'<th>{md_inline(c)}</th>' for c in cells[0])
            body = ''.join('<tr>' + ''.join(f'<td>{md_inline(c)}</td>' for c in row) + '</tr>' for row in cells[1:])
            out.append(f'<div class="scroll"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
        else:
            out.append(f'<p>{md_inline(" ".join(lines))}</p>')
    return '\n'.join(out)


def make_md(boards, order, date, versions):
    out = ['<!-- Generated by scripts/make-bom.py from the schematics. Edit the script, not this file. -->',
           '# Bill of materials', '', INTRO.format(date=date, versions=versions), '',
           'The order list for one set is [`bom.csv`](bom.csv), by manufacturer part number, ready',
           "for Digi-Key's or Mouser's BOM upload. The [web page](" + PAGE_URL + ') has the same',
           'lists, scales the order to several sets and downloads it as CSV. The Buy links',
           'search Digi-Key for each part number.', '']
    for bd in boards:
        out += [f"## {bd['title']}", '', '| Refs | Qty | Part | Manufacturer, MPN | Buy | Notes |',
                '|---|---|---|---|---|---|']
        for refs, q, part, desc, mfr, mpn, where, notes in board_groups(bd):
            mm = f'{mfr} {mpn}'.strip() or where
            link = buy_link(part, mpn)
            buy = f'[{link[0]}]({link[1]})' if link else ''
            out.append(f"| {', '.join(refs)} | {q} | {desc} | {mm} | {buy} | {notes} |")
        out += ['', BOARD_NOTE[bd['id']], '']
    out += ['## Cables', '', CABLES, '', '## Not in the design yet', '', TODO, '']
    return '\n'.join(out)


HTML = '''<!doctype html>
<!-- Generated by scripts/make-bom.py from the schematics. Edit the script, not this file. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>uv254 bill of materials</title>
<meta name="description" content="Parts for one set of uv254 boards (detector, emitter, control) and the cables between them, with manufacturer part numbers.">
<style>
:root {
  --bg: #ffffff; --fg: #1c1d21; --muted: #5d6169; --faint: #8b9098; --line: #dfe1e6;
  --head: #f5f6f8; --chip: #eef0f4; --accent: #5a3ec8; --accent-fg: #ffffff; --accent-soft: #efeafe;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #131417; --fg: #e7e8eb; --muted: #a3a7af; --faint: #767b84; --line: #2c2f35;
    --head: #1b1d21; --chip: #22252a; --accent: #a993ff; --accent-fg: #131417; --accent-soft: #241f3a;
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #131417; --fg: #e7e8eb; --muted: #a3a7af; --faint: #767b84; --line: #2c2f35;
  --head: #1b1d21; --chip: #22252a; --accent: #a993ff; --accent-fg: #131417; --accent-soft: #241f3a;
  color-scheme: dark;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--fg);
  font: 15px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
main { max-width: 1140px; margin: 0 auto; padding: 28px 16px 72px; }
a { color: var(--accent); }
.crumb { font-size: 14px; color: var(--muted); margin: 0 0 6px; }
.crumb a { color: inherit; }
h1 { font-size: 30px; line-height: 1.2; margin: 0 0 10px; letter-spacing: -0.01em; }
h2 { font-size: 20px; margin: 44px 0 10px; scroll-margin-top: 72px; }
p { max-width: 75ch; margin: 0 0 12px; }
.lede { color: var(--muted); }
code, .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 13px; }
span.mono, td.buy { white-space: nowrap; }
.bar { position: sticky; top: 0; z-index: 2; background: var(--bg); border-bottom: 1px solid var(--line);
  display: flex; flex-wrap: wrap; gap: 10px 18px; align-items: center; padding: 10px 0; margin: 18px 0 8px; }
.bar label { display: flex; align-items: center; gap: 8px; font-weight: 600; }
.bar input { width: 72px; font: inherit; padding: 5px 8px; border: 1px solid var(--line); border-radius: 6px;
  background: var(--bg); color: var(--fg); }
button { font: inherit; font-weight: 600; padding: 6px 14px; border: 0; border-radius: 6px;
  background: var(--accent); color: var(--accent-fg); cursor: pointer; }
button:focus-visible, input:focus-visible, a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
nav { display: flex; flex-wrap: wrap; gap: 6px; }
nav a { text-decoration: none; color: var(--fg); background: var(--chip); padding: 3px 10px; border-radius: 999px; font-size: 14px; }
nav a:hover { background: var(--accent-soft); }
.scroll { overflow-x: auto; border: 1px solid var(--line); border-radius: 8px; margin: 12px 0; }
table { border-collapse: collapse; width: 100%; min-width: 1000px; font-size: 14px; }
th, td { text-align: left; vertical-align: top; padding: 7px 10px; border-bottom: 1px solid var(--line); }
th { background: var(--head); font-weight: 600; white-space: nowrap; }
tbody tr:last-child td { border-bottom: 0; }
td.q { text-align: right; font-variant-numeric: tabular-nums; font-weight: 600; white-space: nowrap; }
td.refs { min-width: 10ch; }
td.desc, td.used { min-width: 22ch; }
td.notes { color: var(--muted); min-width: 22ch; }
tr.off td { color: var(--faint); }
tr.off td.q { font-weight: 400; }
.sum { color: var(--muted); font-size: 14px; }
@media (max-width: 640px) { .bar { position: static; } }
footer { margin-top: 56px; padding-top: 16px; border-top: 1px solid var(--line); color: var(--muted); font-size: 14px; }
</style>
</head>
<body>
<main>
<p class="crumb"><a href="../">uv254</a> / bill of materials</p>
<h1>Bill of materials</h1>
<p class="lede">Parts for one set of uv254 boards (@@versions@@) and the two cables between them.
From the KiCad schematics on @@date@@. The boards are still in progress, so check against the schematics before ordering.</p>

<div class="bar">
  <label for="sets">Sets <input id="sets" type="number" min="1" max="999" value="1" inputmode="numeric"></label>
  <button id="dl" type="button">Download CSV</button>
  <nav aria-label="Sections">
    <a href="#order">Order list</a>@@nav@@
    <a href="#cables">Cables</a>
    <a href="#todo">Not in the design yet</a>
  </nav>
</div>

<section id="order">
<h2>Order list</h2>
<p>Everything for <strong id="setsLabel">one set</strong>, by manufacturer part number: @@nlines@@ lines.
The Buy links search Digi-Key for each part number; the CSV loads into Digi-Key's or Mouser's BOM upload.
The part numbers are suggestions: any equivalent passive works (same value and package, same or higher voltage, same dielectric).
The Pro Micro module and the display aren't sold by Digi-Key or Mouser.</p>
<div class="scroll"><table>
<thead><tr><th>Qty</th><th>Manufacturer</th><th>MPN</th><th>Buy</th><th>Description</th><th>Used on</th><th>Notes</th></tr></thead>
<tbody>
@@order_rows@@
</tbody></table></div>
</section>
@@board_sections@@
<section id="cables">
<h2>Cables</h2>
@@cables@@
</section>

<section id="todo">
<h2>Not in the design yet</h2>
@@todo@@
</section>

<footer>
<p>Made by <code>scripts/make-bom.py</code> from the schematics in the
<a href="@@repo@@">uv254 repository</a>; also as <a href="@@repo@@/blob/main/hardware/BOM.md">BOM.md</a>
and <a href="@@repo@@/blob/main/hardware/bom.csv">bom.csv</a>.
Hardware CERN-OHL-S-2.0.</p>
</footer>
</main>
<script>
const CSV_HEADER = @@csv_header@@;
const ORDER = @@order_json@@;
const setsEl = document.getElementById('sets');
function sets() {
  const n = parseInt(setsEl.value, 10);
  return Number.isFinite(n) && n > 0 ? Math.min(n, 999) : 1;
}
function render() {
  const n = sets();
  document.querySelectorAll('td[data-q]').forEach(td => { td.textContent = Number(td.dataset.q) * n; });
  document.getElementById('setsLabel').textContent = n === 1 ? 'one set' : n + ' sets';
}
function cell(v) {
  const s = String(v);
  return /[",\\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
}
document.getElementById('dl').addEventListener('click', () => {
  const n = sets();
  const head = CSV_HEADER.slice();
  head[0] = n === 1 ? 'Qty per set' : 'Qty for ' + n + ' sets';
  const lines = [head].concat(ORDER.map(r => [r[0] * n].concat(r.slice(1))));
  const text = lines.map(r => r.map(cell).join(',')).join('\\n') + '\\n';
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type: 'text/csv' }));
  a.download = n === 1 ? 'uv254-bom.csv' : 'uv254-bom-' + n + '-sets.csv';
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
});
const fromUrl = new URLSearchParams(location.search).get('sets');
if (fromUrl) setsEl.value = fromUrl;
setsEl.addEventListener('input', () => {
  const url = new URL(location.href);
  if (sets() === 1) url.searchParams.delete('sets'); else url.searchParams.set('sets', sets());
  history.replaceState(null, '', url);
  render();
});
render();
</script>
</body>
</html>
'''


def e(s):
    return html.escape(s, quote=True)


def mpn_html(mpn):
    return f'<span class="mono">{e(mpn)}</span>' if mpn else ''


def buy_html(part, mpn):
    link = buy_link(part, mpn)
    return f'<a href="{e(link[1])}">{e(link[0])}</a>' if link else ''


def make_html(boards, order, date, versions):
    order_rows, order_data = [], []
    rows = list(csv.reader(io.StringIO(csv_text(order))))
    header, data = rows[0], rows[1:]
    for (part, q, used), r in zip(order, data):
        desc, mfr, mpn, where, note = PARTS[part]
        order_rows.append(f'<tr><td class="q" data-q="{q}">{q}</td><td>{e(mfr or where)}</td>'
                          f'<td>{mpn_html(mpn)}</td><td class="buy">{buy_html(part, mpn)}</td>'
                          f'<td class="desc">{e(desc)}</td><td class="used">{e(used)}</td>'
                          f'<td class="notes">{e(note)}</td></tr>')
        order_data.append([int(r[0])] + r[1:])
    nav, sections = [], []
    for bd in boards:
        nav.append(f'\n    <a href="#{bd["id"]}">{e(bd["title"])}</a>')
        trs = []
        for refs, q, part, desc, mfr, mpn, where, notes in board_groups(bd):
            mm = (f'{e(mfr)} {mpn_html(mpn)}' if mpn else e(where)).strip()
            cls = ' class="off"' if q == 0 else ''
            trs.append(f'<tr{cls}><td class="refs mono">{e(", ".join(refs))}</td><td class="q">{q}</td>'
                       f'<td class="desc">{e(desc)}</td><td>{mm}</td><td class="buy">{buy_html(part, mpn)}</td>'
                       f'<td class="notes">{e(notes)}</td></tr>')
        sections.append(f'''
<section id="{bd["id"]}">
<h2>{e(bd["title"])}</h2>
<div class="scroll"><table>
<thead><tr><th>Refs</th><th>Qty</th><th>Part</th><th>Manufacturer, MPN</th><th>Buy</th><th>Notes</th></tr></thead>
<tbody>
{chr(10).join(trs)}
</tbody></table></div>
<p class="sum">{md_inline(BOARD_NOTE[bd["id"]])}</p>
</section>''')
    fill = {'versions': e(versions), 'date': e(date), 'nav': ''.join(nav), 'nlines': str(len(order)),
            'order_rows': '\n'.join(order_rows), 'board_sections': ''.join(sections),
            'cables': md_block_html(CABLES), 'todo': md_block_html(TODO), 'repo': REPO_URL,
            'csv_header': json.dumps(header, ensure_ascii=False),
            'order_json': json.dumps(order_data, ensure_ascii=False)}
    return re.sub(r'@@(\w+)@@', lambda m: fill[m.group(1)], HTML)


DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')


def write(rel, text):
    """Write a file only if it changed (ignoring dates)."""
    path = os.path.join(ROOT, rel)
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            if DATE_RE.sub('', f.read()) == DATE_RE.sub('', text):
                print(f'  unchanged  {rel}')
                return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    print(f'  wrote      {rel}')


def main():
    if len(sys.argv) > 1:
        print(__doc__.strip())
        sys.exit(0 if sys.argv[1] in ('-h', '--help') else 1)
    boards = read_boards()
    order = order_list(boards)
    date = datetime.date.today().isoformat()
    versions = ', '.join(bd['title'] for bd in boards)
    write('hardware/bom.csv', csv_text(order))
    write('hardware/BOM.md', make_md(boards, order, date, versions))
    write('docs/bom/index.html', make_html(boards, order, date, versions))
    fitted = sum(1 for bd in boards for r in bd['rows'] if r[2])
    print(f'{fitted} fitted parts on {len(boards)} boards; {len(order)} lines in the order list')


if __name__ == '__main__':
    main()
