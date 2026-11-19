"""Generate simple STEP models for uv254 footprints (CadQuery).

Boxes in the right places, for checking the stack-up and for designing the panel;
not detailed renderings. Every model is built in its footprint's coordinates
(KiCad footprint y points down, model y points up, so y is flipped), with z = 0
on the top of the board the part is mounted on.

  pip install cadquery          (once, ideally in a virtualenv)
  python make_models.py         (writes the .step files next to this script)
  python make_models.py ST7789_2.0in_GMT020_on_header.step
                                (writes just that one)
  python make_models.py --button-top 13
                                (12x12 buttons: cap top 13 mm above the board)
  python make_models.py --above-screen 3
                                (12x12 buttons: cap top 3 mm above the display glass)

All heights are measured from the surface of the board the parts sit on, the same
z = 0 KiCad uses, so the 3D viewer and STL export show them as they'd really be.

Dimensions marked ESTIMATE come from the vendor's drawing or photos, not a
caliper; measure the real parts and adjust.
"""
import argparse
import os
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
BLUE, BLACK, GLASS, GOLD, METAL, ORANGE, CAPCOL = (
    cq.Color(0.08, 0.28, 0.62), cq.Color(0.06, 0.06, 0.06), cq.Color(0.10, 0.12, 0.16),
    cq.Color(0.85, 0.68, 0.25), cq.Color(0.75, 0.75, 0.78), cq.Color(0.90, 0.50, 0.10),
    cq.Color(0.20, 0.20, 0.22))


def box(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box given in footprint coordinates (y down)."""
    return (cq.Workplane('XY').box(abs(x1 - x0), abs(y1 - y0), z1 - z0, centered=False)
            .translate((min(x0, x1), -max(y0, y1), z0)))


def save(assy, name):
    path = os.path.join(HERE, name)
    assy.export(path)
    print('wrote', path)


# ------------------------------------------------------------------ ST7789 display modules
# Both display footprints put the 1x8 header along y: pin 1 (BL) at y = 0 .. pin 8 (GND) at y = 17.78,
# at x = xh. The module lies with its header edge along the left, glass extending to +x, display
# facing up, mounted on the supplied 1x8 header (plastic spacer between the two boards). The
# footprints draw the same outline, holes and active area on Dwgs.User: keep them in step.
#
# 1.54 in, 240 x 240 (MRD module). Footprint uv254:st7789_154in_240x240.
D = dict(
    name='ST7789_1.54in',
    xh=-1.0,           # header pin row x in the footprint
    W=32.0,            # module width, along the header           (vendor drawing)
    L=43.5,            # module length, across the header         (vendor drawing)
    hdr_edge=1.8,      # header pin row to the module's near edge  ESTIMATE
    pcb_t=1.6,         # module PCB thickness                      ESTIMATE
    spacer=2.5,        # header plastic between the boards         (standard header)
    hole_d=2.2,        # corner holes                              ESTIMATE
    hole_inset_l=2.25, # hole centres from the short edges         ESTIMATE
    hole_inset_w=2.25, # hole centres from the long edges          ESTIMATE
    glass_from=4.0,    # module edge (header side) to glass        ESTIMATE
    glass_w=31.5,      # glass, along the header                   ESTIMATE
    glass_l=33.7,      # glass, across the header (without ledge)  ESTIMATE
    ledge_l=1.7,       # FPC bonding ledge after the glass         ESTIMATE
    fpc_w=14.0,        # FPC, along the header                     ESTIMATE
    fpc_l=1.2,         # FPC beyond the ledge                      ESTIMATE
    lcd_t=2.6,         # LCD + backlight + tape above the module PCB  ESTIMATE
    active_w=27.72,    # active area along the header              (240 px at 0.1155 mm)
    active_l=27.72,    # active area across the header             (240 px at 0.1155 mm)
    active_from=1.5,   # glass edge (header side) to active area   ESTIMATE
    board_t=1.6,       # the control board, for the header pins below it
)

# 2.0 in, 240 x 320 (Golden Morning GMT020-02-8P, sold as XIITIA on Amazon). Footprint
# uv254:st7789_200in_240x320. Outline and active area from the vendor's spec table
# (goldenmorninglcd.com, GMT020-02: "37.25 x 62.00 mm", "active area 30.60 x 40.80 mm");
# the rest measured off product photos, scaled by the 2.54 mm header pitch (about +-0.3 mm).
D2 = dict(
    name='ST7789_2.0in_GMT020',
    xh=0.0,
    W=37.25,           # module width, along the header           (vendor)
    L=62.0,            # module length, across the header         (vendor)
    hdr_edge=2.4,      # header pin row to the module's near edge  ESTIMATE (photo); row centred
    pcb_t=1.6,         #                                           ESTIMATE
    spacer=2.5,        #                                           (standard header)
    hole_d=2.5,        #                                           ESTIMATE (photo)
    hole_inset_l=1.6,  # from the short edges                      ESTIMATE (photo)
    hole_inset_w=4.0,  # from the long edges                       ESTIMATE (photo)
    glass_from=4.9,    #                                           ESTIMATE (photo)
    glass_w=35.8,      #                                           ESTIMATE (photo; 2.0 in panels are 35.8)
    glass_l=45.0,      #                                           ESTIMATE (photo)
    ledge_l=3.8,       #                                           ESTIMATE (photo)
    fpc_w=23.0,        #                                           ESTIMATE (photo)
    fpc_l=3.9,         #                                           ESTIMATE (photo)
    lcd_t=2.8,         #                                           ESTIMATE (similar panels: 2.65-3.85)
    active_w=30.6,     # 240 px at 0.1275 mm                       (vendor)
    active_l=40.8,     # 320 px at 0.1275 mm                       (vendor)
    active_from=2.4,   # centred in the black mask                 ESTIMATE (photo)
    board_t=1.6,
)


def screen_top(p=D):
    """Height of the display's glass face above the board."""
    return p['spacer'] + p['pcb_t'] + p['lcd_t']


def outline(p):
    """Module outline, hole centres and active area in footprint coordinates (y down)."""
    xh, ymid = p['xh'], 8.89                    # header pin row, header centre
    x0, x1 = xh - p['hdr_edge'], xh - p['hdr_edge'] + p['L']
    y0, y1 = ymid - p['W'] / 2, ymid + p['W'] / 2
    holes = [(hx, hy) for hx in (x0 + p['hole_inset_l'], x1 - p['hole_inset_l'])
             for hy in (y0 + p['hole_inset_w'], y1 - p['hole_inset_w'])]
    ax0 = x0 + p['glass_from'] + p['active_from']
    active = (ax0, ax0 + p['active_l'], ymid - p['active_w'] / 2, ymid + p['active_w'] / 2)
    return (x0, x1, y0, y1), holes, active


def display(p=D):
    xh, ymid = p['xh'], 8.89
    (x0, x1, y0, y1), holes, (ax0, ax1, ay0, ay1) = outline(p)
    zb = p['spacer']                            # underside of the module PCB
    zt = zb + p['pcb_t']                        # top of the module PCB
    pcb = box(x0, x1, y0, y1, zb, zt)
    for hx, hy in holes:
        pcb = pcb.cut(cq.Workplane('XY').circle(p['hole_d'] / 2).extrude(10).translate((hx, -hy, -1)))
    gx0 = x0 + p['glass_from']
    gx1 = gx0 + p['glass_l']
    gy0, gy1 = ymid - p['glass_w'] / 2, ymid + p['glass_w'] / 2
    glass = box(gx0, gx1, gy0, gy1, zt, zt + p['lcd_t'])
    ledge = box(gx1, gx1 + p['ledge_l'], gy0, gy1, zt, zt + p['lcd_t'] - 0.7)
    fx0 = gx1 + p['ledge_l']
    fpc = box(fx0, fx0 + p['fpc_l'], ymid - p['fpc_w'] / 2, ymid + p['fpc_w'] / 2, zt, zt + 0.3)
    active = box(ax0, ax1, ay0, ay1, zt + p['lcd_t'], zt + p['lcd_t'] + 0.05)
    spacer = box(xh - 1.27, xh + 1.27, -1.27, 17.78 + 1.27, 0, p['spacer'])
    pins = None
    for k in range(8):
        pin = box(xh - 0.32, xh + 0.32, k * 2.54 - 0.32, k * 2.54 + 0.32, -p['board_t'] - 1.5, zt + 1.0)
        pins = pin if pins is None else pins.union(pin)
    a = cq.Assembly(name=p['name'])
    a.add(pcb, name='pcb', color=BLUE)
    a.add(glass, name='glass', color=BLACK)
    a.add(ledge, name='ledge', color=GLASS)
    a.add(fpc, name='fpc', color=ORANGE)
    a.add(active, name='active_area', color=GLASS)
    a.add(spacer, name='header', color=BLACK)
    a.add(pins, name='pins', color=GOLD)
    return a


# ------------------------------------------------------------------ 12 x 12 mm tactile switch and cap
# Footprint uv254:SW_Tactile_12x12_B3F-40xx: pins at (0,0) (12.5,0) (0,5) (12.5,5); body centred
# at (6.25, 2.5).
S = dict(
    body=12.0, body_h=3.5,      # housing                               (12 x 12 x 7.3 class) ESTIMATE
    plate_h=0.3,                # metal cover
    stem=3.6, top=7.3,          # square actuator, top height above the board
    cap=11.6,                   # cap outline (square)                   ESTIMATE until caps are chosen
    button_top=12.0,            # ABSOLUTE height of the cap's top face above the board surface (mm)
    cap_gap=0.7,                # gap between the switch cover and the cap's lower edge
    board_t=1.6,
)


def switch12(p=S):
    cx, cy = 6.25, 2.5
    h = p['body'] / 2
    body = box(cx - h, cx + h, cy - h, cy + h, 0, p['body_h'])
    plate = box(cx - h + 0.2, cx + h - 0.2, cy - h + 0.2, cy + h - 0.2, p['body_h'], p['body_h'] + p['plate_h'])
    s = p['stem'] / 2
    stem = box(cx - s, cx + s, cy - s, cy + s, p['body_h'] + p['plate_h'], p['top'])
    legs = None
    for (x, y) in ((0, 0), (12.5, 0), (0, 5), (12.5, 5)):
        leg = box(x - 0.35, x + 0.35, y - 0.2, y + 0.2, -p['board_t'] - 1.5, 0.5)
        legs = leg if legs is None else legs.union(leg)
    a = cq.Assembly(name='SW_Tactile_12x12')
    a.add(body, name='body', color=BLACK)
    a.add(plate, name='cover', color=METAL)
    a.add(stem, name='actuator', color=BLACK)
    a.add(legs, name='legs', color=METAL)
    return a


def cap12(p=S):
    cx, cy = 6.25, 2.5
    c = p['cap'] / 2
    z0 = p['body_h'] + p['plate_h'] + p['cap_gap']             # cap reaches down over the actuator
    if p['button_top'] < p['top'] + 1.0:
        raise SystemExit(f"button_top {p['button_top']} mm is below the switch actuator ({p['top']} mm) + a cap")
    cap = box(cx - c, cx + c, cy - c, cy + c, z0, p['button_top']).edges('>Z').fillet(0.8)
    a = cq.Assembly(name='Cap_12x12')
    a.add(cap, name='cap', color=CAPCOL)
    return a


# ------------------------------------------------------------------ Pro Micro nRF52840 (SuperMini / nice!nano)
# Footprint uv254:nice_nano_cleanest: pads 1-12 at y = +7.62, 13-24 at y = -7.62 (x -13.97 .. 13.97),
# B+ (25) and B- (26) at x = -16.51; outline x -17.78 .. 15.24, y -8.89 .. 8.89; USB-C at the -x end.
# Modelled components-up on a 2.54 mm pin header. On the back of the control board, KiCad flips it.
P = dict(
    x0=-17.78, x1=15.24, w=17.78,   # module outline                       (footprint outline)
    pcb_t=1.2,                      # module PCB                            ESTIMATE
    spacer=2.5,                     # header plastic; ~11 for a socket strip plus header
    usb_w=8.94, usb_l=7.35, usb_h=3.26, usb_over=0.6,   # USB-C receptacle, overhang past the edge
    chip=7.0, chip_h=0.9,           # nRF52840 QFN73
    board_t=1.6,
)


def promicro(p=P):
    zb, zt = p['spacer'], p['spacer'] + p['pcb_t']
    pcb = box(p['x0'], p['x1'], -p['w'] / 2, p['w'] / 2, zb, zt)
    ux0 = p['x0'] - p['usb_over']
    usb = box(ux0, ux0 + p['usb_l'], -p['usb_w'] / 2, p['usb_w'] / 2, zt, zt + p['usb_h'])
    c = p['chip'] / 2
    chip = box(2.0 - c, 2.0 + c, -c, c, zt, zt + p['chip_h'])
    xs = [-16.51] + [-13.97 + 2.54 * k for k in range(12)]
    pins = strips = None
    for y in (-7.62, 7.62):
        s = box(-16.51 - 1.27, 13.97 + 1.27, y - 1.27, y + 1.27, 0, p['spacer'])
        strips = s if strips is None else strips.union(s)
        for x in xs:
            pin = box(x - 0.32, x + 0.32, y - 0.32, y + 0.32, -p['board_t'] - 1.5, zt + 1.0)
            pins = pin if pins is None else pins.union(pin)
    a = cq.Assembly(name='ProMicro_nRF52840')
    a.add(pcb, name='pcb', color=cq.Color(0.10, 0.10, 0.12))
    a.add(usb, name='usb_c', color=METAL)
    a.add(chip, name='nrf52840', color=BLACK)
    a.add(strips, name='headers', color=BLACK)
    a.add(pins, name='pins', color=GOLD)
    return a


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--button-top', type=float, default=S['button_top'],
                   help='12x12 buttons: height of the cap top above the board, mm (default %(default)s)')
    g.add_argument('--above-screen', type=float,
                   help='12x12 buttons: height of the cap top above the 1.54 in display glass, mm')
    ap.add_argument('files', nargs='*', metavar='FILE.step',
                    help='write only these models (default: all of them)')
    args = ap.parse_args()
    S['button_top'] = screen_top() + args.above_screen if args.above_screen is not None else args.button_top
    models = {
        'ST7789_1.54in_MRD_on_header.step': lambda: display(D),
        'ST7789_2.0in_GMT020_on_header.step': lambda: display(D2),
        'SW_Tactile_12x12.step': switch12,
        'ProMicro_nRF52840_on_header.step': promicro,
        'Cap_12x12_square.step': cap12,
    }
    unknown = [f for f in args.files if f not in models]
    if unknown:
        raise SystemExit('unknown model(s): ' + ', '.join(unknown) + '\nknown: ' + ', '.join(models))
    for name, make in models.items():
        if not args.files or name in args.files:
            save(make(), name)
    bb = cap12().toCompound().BoundingBox()
    for label, p in (('1.54 in', D), ('2.0 in', D2)):
        print(f'{label} display glass top: {screen_top(p):.2f} mm above the board')
    st = screen_top()
    print(f'12x12 button top:  {bb.zmax:.2f} mm above the board ({bb.zmax - st:+.2f} mm relative to the 1.54 in glass)')
