import math, sys, wave, subprocess
import numpy as np
import cairo
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, DUR = 1080, 1920, 24, 32
import os
SP = os.environ.get("REEL_WORK", "/tmp/reel_work") .rstrip("/") + "/"
os.makedirs(SP, exist_ok=True)
G = "/usr/share/fonts/truetype/google-fonts/"

CREAM = (247, 241, 229); PAPER = (255, 252, 245); NAVY = (14, 28, 54); GOLD = (201, 158, 80)
GOLDD = (170, 125, 45); TERRA = (196, 98, 72); TEAL = (46, 120, 126); TEAL2 = (96, 163, 152)
MUST = (232, 180, 70); GREY = (120, 128, 142); SK1 = (226, 176, 140); SK2 = (205, 150, 115); SK3 = (240, 196, 160)
RED = (200, 70, 62); GREEN = (60, 150, 100)

def lora(size, w="Regular"):
    f = ImageFont.truetype(G + "Lora-Variable.ttf", size)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
def lorai(size): return ImageFont.truetype(G + "Lora-Italic-Variable.ttf", size)
def pop_(size, w="Medium"): return ImageFont.truetype(G + f"Poppins-{w}.ttf", size)
FONTS = {"cap": lora(54, "Medium"), "kick": pop_(26, "Medium"), "brand": pop_(28, "Medium"),
         "lab": pop_(30, "Medium"), "labs": pop_(24, "Regular"), "big": lora(88, "SemiBold"),
         "bigi": lorai(88), "hand": pop_(32, "Light"), "disc": pop_(22, "Regular"), "logo": lora(70, "Bold"),
         "cal": pop_(30, "Medium")}

def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def eio(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def win(t, a, b): return ease((t - a) / (b - a))
def back(x):  # overshoot pop
    x = max(0.0, min(1.0, x)); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def lerp(a, b, p): return a + (b - a) * p

TXT = []; CUR_A = [1.0]
def say(x, y, s, font, fill, alpha=1.0, anchor="m", track=0):
    TXT.append((x, y, s, font, fill, alpha * CUR_A[0], anchor, track))

def C(c, col, a=1.0): c.set_source_rgba(col[0] / 255, col[1] / 255, col[2] / 255, a)
def rr(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path(); c.arc(x + w - r, y + r, r, -math.pi / 2, 0); c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi); c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); c.close_path()
def circ(c, x, y, r, col, a=1.0):
    C(c, col, a); c.arc(x, y, r, 0, 2 * math.pi); c.fill()
def stroke_(c, col, w, a=1.0):
    C(c, col, a); c.set_line_width(w); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()
def grp(c, a, fn):
    if a <= 0.005: return
    CUR_A[0] *= a
    c.push_group(); fn(); c.pop_group_to_source(); c.paint_with_alpha(a)
    CUR_A[0] /= a

# ---------------- items (drawn centred at origin, ~100px) ----------------
def doc_base(c, fold=True):
    rr(c, -42, -56, 84, 112, 8); C(c, PAPER); c.fill_preserve(); stroke_(c, NAVY, 4)
def it_sticky(c):
    c.save(); rr(c, -44, -44, 88, 88, 6); C(c, MUST); c.fill(); c.restore()
    C(c, NAVY); c.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(64)
    ext = c.text_extents("?"); c.move_to(-ext.width / 2 - ext.x_bearing, 22); c.show_text("?")
def it_key(c):
    c.arc(-22, 0, 20, 0, 2 * math.pi); stroke_(c, GOLDD, 9)
    c.move_to(-2, 0); c.line_to(48, 0); stroke_(c, GOLDD, 9)
    c.move_to(34, 0); c.line_to(34, 16); stroke_(c, GOLDD, 8); c.move_to(48, 0); c.line_to(48, 14); stroke_(c, GOLDD, 8)
def it_pass(c):
    rr(c, -40, -52, 80, 104, 8); C(c, NAVY); c.fill()
    rr(c, -40, -20, 80, 16, 0); C(c, GOLD); c.fill(); circ(c, 0, 24, 14, GOLD)
def it_stmt(c):
    doc_base(c)
    for i, h in enumerate([22, 38, 30, 50]):
        rr(c, -30 + i * 16, 40 - h, 11, h, 2); C(c, TEAL); c.fill()
    c.move_to(-30, -36); c.line_to(24, -36); stroke_(c, GREY, 4)
def it_env(c):
    rr(c, -56, -38, 112, 76, 8); C(c, PAPER); c.fill_preserve(); stroke_(c, NAVY, 4)
    c.move_to(-54, -34); c.line_to(0, 6); c.line_to(54, -34); stroke_(c, NAVY, 4); circ(c, 0, 8, 9, TERRA)
def it_shield(c):
    doc_base(c)
    c.move_to(0, -34); c.curve_to(18, -28, 26, -26, 26, -26); c.curve_to(26, 8, 14, 24, 0, 32)
    c.curve_to(-14, 24, -26, 8, -26, -26); c.curve_to(-26, -26, -18, -28, 0, -34); C(c, GOLD); c.fill()
def it_deed(c):
    doc_base(c)
    for y in (-34, -18, -2): c.move_to(-28, y); c.line_to(28, y); stroke_(c, GREY, 4)
    circ(c, 14, 30, 13, TERRA)
def it_id(c):
    rr(c, -58, -38, 116, 76, 10); C(c, TEAL); c.fill()
    circ(c, -30, -4, 15, PAPER); c.move_to(-4, -14); c.line_to(40, -14); stroke_(c, PAPER, 6); c.move_to(-4, 6); c.line_to(30, 6); stroke_(c, PAPER, 6)
ITEMS = [(it_sticky, 0), (it_key, 0), (it_pass, 1), (it_stmt, 1), (it_env, 2), (it_shield, 2), (it_deed, 3), (it_id, 3)]
CATS = ["Goals", "Investments", "Insurance", "Documents"]

def item(c, fn, x, y, rot=0, s=1.0, a=1.0):
    if s <= 0.01 or a <= 0.01: return
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    # soft shadow
    c.save(); c.translate(6, 8); C(c, NAVY, 0.10 * a); fn_shadow(c, fn); c.restore()
    c.push_group(); fn(c); c.pop_group_to_source(); c.paint_with_alpha(a)
    c.restore()
def fn_shadow(c, fn):
    rr(c, -44, -52, 88, 104, 10); c.fill()

# ---------------- people ----------------
def person(c, x, y, s=1.0, skin=SK1, hair="short", hc=NAVY, shirt=NAVY, pants=(60, 70, 96), mood="smile",
           la=0.12, ra=0.12, bob=0.0, headr=1.0, glasses=False, bindi=False, stripe=None, look=0.0, cane=False):
    """feet at (x,y). la/ra: arm angle outward from hanging (0) to straight up (pi). Returns hand positions."""
    c.save(); c.translate(x, y + bob); c.scale(s, s)
    # shadow
    c.save(); c.scale(1, 0.18); circ(c, 0, 0, 92, NAVY, 0.13); c.restore()
    hr = 52 * headr; hy = -300 - 46 * headr
    # legs
    for dx in (-24, 24):
        rr(c, dx - 17, -132, 34, 132, 12); C(c, pants); c.fill()
        c.save(); c.translate(dx + 4, -2); c.scale(1.5, 0.7); circ(c, 0, 0, 17, NAVY); c.restore()
    # long hair behind
    if hair == "long":
        rr(c, -hr - 6, hy - 6, 2 * hr + 12, 190, 40); C(c, hc); c.fill()
    # torso
    rr(c, -62, -302, 124, 176, 46); C(c, shirt); c.fill()
    if stripe:
        c.move_to(-26, -300); c.line_to(0, -250); c.line_to(26, -300); stroke_(c, stripe, 8)
    # arms
    hands = []
    for side, ang in ((-1, la), (1, ra)):
        sx, sy = side * 56, -280
        ex = sx + side * math.sin(ang) * 118; ey = sy + math.cos(ang) * 118
        c.move_to(sx, sy); c.line_to(ex, ey); stroke_(c, shirt, 32)
        circ(c, ex, ey, 17, skin)
        hands.append((x + ex * s, y + bob + ey * s))
    # neck + head
    rr(c, -16, hy + hr - 6, 32, 40, 8); C(c, skin); c.fill()
    circ(c, 0, hy, hr, skin)
    # hair
    if hair in ("short", "long", "white", "ponytail", "bun"):
        c.new_path(); c.arc(0, hy, hr + 2, math.pi * 1.02, math.pi * 1.98); c.close_path(); C(c, hc); c.fill()
        c.arc(0, hy - 6, hr + 2, math.pi * 1.0, math.pi * 2.0); c.close_path(); C(c, hc); c.fill()
        if hair == "white":
            circ(c, -hr + 2, hy + 6, 14, hc); circ(c, hr - 2, hy + 6, 14, hc)
        if hair == "ponytail":
            c.move_to(hr - 4, hy - 20); c.curve_to(hr + 50, hy - 10, hr + 40, hy + 60, hr + 6, hy + 70); stroke_(c, hc, 22)
        if hair == "bun":
            circ(c, 0, hy - hr - 10, 24, hc)
    # face
    ex = look * 5
    for dx in (-20, 20):
        circ(c, dx + ex, hy + 4, 5.5, NAVY)
    for dx in (-30, 30): circ(c, dx, hy + 22 * headr, 9, TERRA, 0.22)
    my = hy + 30 * headr
    if mood == "smile":
        c.arc(ex, my - 8, 17, 0.15 * math.pi, 0.85 * math.pi); stroke_(c, NAVY, 5)
    elif mood == "calm":
        c.arc(ex, my - 4, 12, 0.2 * math.pi, 0.8 * math.pi); stroke_(c, NAVY, 5)
    elif mood == "open":
        c.new_path(); c.arc(ex, my - 10, 18, 0, math.pi); c.close_path(); C(c, NAVY); c.fill()
    elif mood == "worry":
        c.arc(ex, my + 14, 15, 1.15 * math.pi, 1.85 * math.pi); stroke_(c, NAVY, 5)
        for sgn in (-1, 1):
            c.move_to(sgn * 32 + ex, hy - 16); c.line_to(sgn * 10 + ex, hy - 26); stroke_(c, NAVY, 4)
    if glasses:
        for dx in (-20, 20):
            c.arc(dx + ex, hy + 4, 15, 0, 2 * math.pi); stroke_(c, NAVY, 3.5)
        c.move_to(-5 + ex, hy + 4); c.line_to(5 + ex, hy + 4); stroke_(c, NAVY, 3.5)
    if bindi: circ(c, ex, hy - 20, 4.5, RED)
    if cane:
        hxx = hands[1][0]
    c.restore()
    return hands

def sparkle(c, x, y, r, a, col=GOLD):
    if a <= 0.01: return
    for k in range(6):
        ang = k * math.pi / 3 + 0.3
        c.move_to(x + math.cos(ang) * r * 0.5, y + math.sin(ang) * r * 0.5)
        c.line_to(x + math.cos(ang) * r, y + math.sin(ang) * r); stroke_(c, col, 5, a)
def star4(c, x, y, r, col=GOLD, a=1.0):
    c.move_to(x, y - r); c.curve_to(x, y, x, y, x + r, y); c.curve_to(x, y, x, y, x, y + r)
    c.curve_to(x, y, x, y, x - r, y); c.curve_to(x, y, x, y, x, y - r); C(c, col, a); c.fill()

# ---------------- background ----------------
BGS = None
def make_bg():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    C(c, CREAM); c.paint()
    g = cairo.RadialGradient(540, 700, 80, 540, 760, 1100)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.65); g.add_color_stop_rgba(1, 0.9, 0.84, 0.7, 0.35)
    c.set_source(g); c.paint()
    rng = np.random.RandomState(3)
    for _ in range(40):  # tiny paper dots
        circ(c, rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1.5, 3), GOLD, 0.25)
    return s
def draw_bg(c):
    global BGS
    if BGS is None: BGS = make_bg()
    c.set_source_surface(BGS, 0, 0); c.paint()

def doodles(c, t):
    for k, (x, y, r) in enumerate([(120, 330, 14), (960, 420, 10), (90, 1250, 11), (985, 1180, 15), (900, 270, 9)]):
        star4(c, x, y + 8 * math.sin(t * 1.2 + k), r * (0.8 + 0.2 * math.sin(t * 2 + k)), GOLD, 0.55)

# ---------------- scenes ----------------
def orbit(k, t):
    a = k * 2 * math.pi / 8 + 0.25 * math.sin(t * 0.8 + k)
    x = 540 + 400 * math.cos(a); y = 640 + 230 * math.sin(a) + 26 * math.sin(t * 1.3 + k * 1.7)
    return x, y, 0.45 * math.sin(t * 0.9 + k)

COMP = []  # compartment rects
for i in range(4):
    COMP.append((150 + (i % 2) * 400, 420 + (i // 2) * 330, 380, 310))
LAND0, STEP, FLY = 7.4, 0.5, 0.95

def scene12(c, t):
    # board
    ba = win(t, 6.4, 7.4)
    def board():
        c.save(); c.translate(0, 60 * (1 - ba))
        rr(c, 130, 400, 820, 690, 26); C(c, NAVY); c.fill()
        for i, (x, y, w, h) in enumerate(COMP):
            rr(c, x + 10, y + 20 - 0, w - 20, h - 20, 18); C(c, PAPER); c.fill()
            fl = 0.0
            for k in range(8):
                if ITEMS[k][1] == i:
                    ts = LAND0 + k * STEP + FLY
                    fl = max(fl, max(0.0, 1 - (t - ts) / 0.7) if t >= ts else 0.0)
            if fl > 0:
                rr(c, x + 10, y + 20, w - 20, h - 20, 18); stroke_(c, GOLD, 8 * fl, fl)
            rr(c, x + 40, y + 34, w - 80, 56, 14); C(c, GOLD); c.fill()
            say(x + w / 2, y + 62, CATS[i].upper(), FONTS["lab"], NAVY, ba, "m", 4)
        c.restore()
    if ba > 0.01: grp(c, ba, board)
    # items
    for k, (fn, cat) in enumerate(ITEMS):
        ts = LAND0 + k * STEP
        appear = back((t - (0.3 + k * 0.25)) / 0.7)
        ox, oy, orot = orbit(k, min(t, ts))
        if t < 6.5 or t < ts:
            ox, oy, orot = orbit(k, t)
        cx, cy, cw, ch = COMP[cat]
        j = k % 2
        tx, ty = cx + cw / 2 + (-82 if j == 0 else 82), cy + 205
        p = eio((t - ts) / FLY)
        if t < ts:
            x, y, rot, sc = ox, oy, orot, 1.0
        else:
            sx, sy, sr = orbit(k, ts)
            x = lerp(sx, tx, p); y = lerp(sy, ty, p) - 110 * math.sin(math.pi * p); rot = lerp(sr, 0, p); sc = lerp(1.0, 0.62, p)
        item(c, fn, x, y, rot, sc * max(0.0, appear))
        if ts + FLY <= t < ts + FLY + 0.7:
            q = (t - ts - FLY) / 0.7; sparkle(c, tx, ty, 40 + 50 * q, 1 - q)
    # papa
    mv = eio((t - 6.5) / 1.8)
    px = lerp(540, 250, mv); py = lerp(1420, 1470, mv); ps = lerp(1.0, 0.62, mv)
    happy = t > LAND0 + 7 * STEP + FLY
    if t < 6.5:
        mood, la, ra = "worry", 2.7 + 0.12 * math.sin(t * 3), 0.2
    elif not happy:
        mood, la, ra = "calm", 0.15, 1.35
    else:
        mood, la, ra = "smile", 2.6 + 0.2 * math.sin(t * 6), 2.6 + 0.2 * math.sin(t * 6 + 1)
    bob = 4 * math.sin(t * 2.2)
    person(c, px, py, ps, SK1, "short", NAVY, NAVY, (60, 70, 96), mood, la, ra, bob)
    # worry doodles
    if t < 7.4:
        da = 1 - win(t, 6.5, 7.4)
        for r_, w_ in ((60, 5), (42, 4), (24, 3)):
            c.save(); c.translate(540, 905); c.rotate(t * 2 + r_)
            c.arc(0, 0, r_, 0, 4.4); stroke_(c, NAVY, w_, 0.45 * da * win(t, 0.4, 1.0)); c.restore()
        for k, dx in enumerate((-190, 190)):
            c.save(); c.translate(540 + dx, 940 + 10 * math.sin(t * 3 + k)); C(c, GOLDD, da * win(t, 0.8, 1.4))
            c.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(70)
            c.move_to(0, 0); c.show_text("?"); c.restore()
        dy = (t * 80) % 60
        c.save(); c.translate(610, 1010 + dy); c.move_to(0, -18); c.curve_to(14, 0, 14, 14, 0, 14); c.curve_to(-14, 14, -14, 0, 0, -18)
        C(c, TEAL2, da * 0.9); c.fill(); c.restore()
    # mama walks in
    if t > 7.6:
        mw = eio((t - 7.6) / 1.6)
        mx = lerp(1300, 830, mw); mh = (t > LAND0 + 7 * STEP + FLY)
        wob = 6 * abs(math.sin(t * 7)) * (1 - mw)
        mm = "smile" if mw > 0.9 else "calm"
        person(c, mx, 1470, 0.62, SK3, "long", (40, 30, 40), TERRA, (80, 60, 90), mm,
               0.15, (2.6 + 0.25 * math.sin(t * 6)) if mh else 0.15, bob=-wob, bindi=True, stripe=GOLD, look=-0.6)
    # confetti when finished
    tf = LAND0 + 7 * STEP + FLY
    if t > tf:
        for k in range(14):
            q = (t - tf - k * 0.04) / 1.6
            if 0 < q < 1:
                ang = k * 0.9; r = 60 + 330 * ease(q)
                star4(c, 540 + r * math.cos(ang) * 1.2, 1250 - 200 * ease(q) + r * math.sin(ang) * 0.3, 11, [GOLD, TEAL, TERRA, MUST][k % 4], 1 - q)

def scene3(c, t):
    t0 = 14.0
    # calendar card
    cx, cy, cw, ch = 230, 330, 620, 580
    p = back((t - t0 - 0.3) / 0.8)
    c.save(); c.translate(0, 40 * (1 - ease((t - t0) / 0.8)))
    rr(c, cx + 10, cy + 14, cw, ch, 28); C(c, NAVY, 0.10); c.fill()
    rr(c, cx, cy, cw, ch, 28); C(c, PAPER); c.fill_preserve(); stroke_(c, NAVY, 5)
    c.save(); rr(c, cx, cy, cw, 96, 28); c.clip(); C(c, NAVY); c.paint(); c.restore()
    c.rectangle(cx, cy + 60, cw, 36); C(c, NAVY); c.fill()
    for rx in (cx + 150, cx + cw - 150):
        rr(c, rx - 9, cy - 22, 18, 56, 9); C(c, GOLD); c.fill()
    say(cx + cw / 2, cy + 48, "SCHEDULED REVIEWS", FONTS["lab"], (240, 220, 170), 1.0, "m", 5)
    sel = [(0, 2), (1, 4), (3, 1), (4, 5)]
    cell_w, cell_h = 76, 84
    gx, gy = cx + 52, cy + 140
    for r_ in range(5):
        for k_ in range(7):
            x = gx + k_ * cell_w + cell_w / 2; y = gy + r_ * cell_h + cell_h / 2
            circ(c, x, y, 6, GREY, 0.35)
    for n, (r_, k_) in enumerate(sel):
        ts = t0 + 1.2 + n * 1.5
        q = back((t - ts) / 0.55)
        if q > 0:
            x = gx + k_ * cell_w + cell_w / 2; y = gy + r_ * cell_h + cell_h / 2
            circ(c, x, y, 30 * q, GOLD)
            c.move_to(x - 13 * q, y); c.line_to(x - 3 * q, y + 11 * q); c.line_to(x + 15 * q, y - 11 * q); stroke_(c, NAVY, 6 * q)
    c.restore()
    # phone with market noise
    sh = 5 * math.sin(t * 17)
    c.save(); c.translate(150, 1060 + sh); c.rotate(-0.12 + 0.02 * math.sin(t * 20))
    rr(c, -62, -115, 124, 230, 20); C(c, NAVY); c.fill(); rr(c, -52, -97, 104, 190, 10); C(c, (230, 232, 238)); c.fill()
    pts = [(-40, 30), (-24, -30), (-8, 20), (8, -50), (24, 10), (40, -20)]
    c.move_to(*pts[0])
    for (px_, py_) in pts[1:]: c.line_to(px_, py_ + 6 * math.sin(t * 6 + px_))
    stroke_(c, RED if int(t * 3) % 2 else GREEN, 6)
    c.restore()
    say(150, 1215, "market noise", FONTS["labs"], GREY, 1.0, "m", 1)
    # characters
    wob = 3 * math.sin(t * 2)
    h1 = person(c, 500, 1480, 0.9, SK1, "short", NAVY, NAVY, (60, 70, 96), "calm", 0.12, 1.0, wob, look=0.5)
    h2 = person(c, 790, 1480, 0.9, SK3, "long", (40, 30, 40), TERRA, (80, 60, 90), "smile", 1.7 + 0.1 * math.sin(t * 2), 0.12, -wob, bindi=True, stripe=GOLD, look=-0.5)
    # tea cup in papa's right hand
    hx, hy = h1[1]
    rr(c, hx - 4, hy - 26, 44, 34, 8); C(c, PAPER); c.fill_preserve(); stroke_(c, NAVY, 3.5)
    for k in range(2):
        c.move_to(hx + 8 + k * 16, hy - 32); c.curve_to(hx + 2 + k * 16, hy - 50, hx + 18 + k * 16, hy - 62, hx + 10 + k * 16, hy - 82 + 5 * math.sin(t * 3 + k))
        stroke_(c, GREY, 3, 0.5)

def scene4(c, t):
    t0 = 21.5
    # hill
    c.save(); c.translate(540, 1640); c.scale(1, 0.30); circ(c, 0, 0, 1000, (232, 222, 198)); c.restore()
    # tree
    gr = ease((t - t0) / 1.2)
    c.save(); c.translate(540, 1420)
    c.move_to(-34, 0); c.curve_to(-26, -200, -40, -300, -56, -430); c.line_to(56, -430); c.curve_to(40, -300, 26, -200, 34, 0)
    c.close_path(); C(c, (96, 70, 56)); c.fill()
    c.move_to(0, -250); c.line_to(-100, -380); stroke_(c, (96, 70, 56), 20); c.move_to(0, -280); c.line_to(100, -400); stroke_(c, (96, 70, 56), 20)
    c.restore()
    for k, (dx, dy, r, colr) in enumerate([(0, -640, 190, TEAL), (-180, -540, 150, TEAL2), (190, -550, 155, TEAL2), (-110, -720, 130, TEAL2),
                                          (120, -730, 135, TEAL), (0, -520, 150, TEAL)]):
        circ(c, 540 + dx, 1420 + dy, r * lerp(0.3, 1.0, gr) * (1 + 0.012 * math.sin(t * 1.5 + k)), colr, 0.96)
    coins = [(-150, -680), (60, -760), (170, -620), (-60, -590), (230, -510), (-230, -510), (0, -830), (-120, -800), (130, -820), (-10, -440), (-200, -610), (120, -540)]
    for k, (dx, dy) in enumerate(coins):
        q = back((t - (t0 + 1.0 + k * 0.28)) / 0.6)
        if q > 0:
            x, y = 540 + dx, 1420 + dy + 4 * math.sin(t * 2 + k)
            circ(c, x, y, 24 * q, GOLD); circ(c, x, y, 15 * q, GOLDD, 0.0)
            c.arc(x, y, 15 * q, 0, 2 * math.pi); stroke_(c, GOLDD, 3, 0.9)
    # people
    b = 3 * math.sin(t * 2)
    give = win(t, 24.2, 24.8)
    catch = win(t, 26.0, 26.5)
    gp = person(c, 330, 1490, 0.8, SK2, "white", (235, 235, 235), (112, 120, 134), (70, 76, 92), "smile", 0.12, 0.35, b, glasses=True)
    # cane
    c.move_to(gp[1][0], gp[1][1]); c.line_to(gp[1][0] + 10, 1490); stroke_(c, (96, 70, 56), 9)
    pa = person(c, 560, 1490, 0.8, SK1, "short", NAVY, NAVY, (60, 70, 96), "smile", 0.12, 1.2 * give + 0.12 * (1 - give), -b)
    kid_j = 0 if t < 26.2 else -22 * abs(math.sin((t - 26.2) * 7)) * max(0, 1 - (t - 26.2) / 2.2)
    kd = person(c, 790, 1490, 0.58, SK3, "ponytail", (40, 30, 40), MUST, (80, 100, 130), "open" if t > 26.0 else "smile",
                1.0 * (1 - catch) + 2.5 * catch, 0.12, kid_j, headr=1.18, look=-0.6)
    # book travels from papa hand to kid
    if t < 24.3:
        bx, by = pa[1][0] + 30, pa[1][1] - 10
    else:
        q = eio((t - 24.3) / 1.9)
        sx, sy = pa[1][0] + 30, pa[1][1] - 10
        ex, ey = kd[0][0] - 20, kd[0][1] - 40
        bx = lerp(sx, ex, q); by = lerp(sy, ey, q) - 180 * math.sin(math.pi * q)
    c.save(); c.translate(bx, by); c.rotate(0.35 * math.sin(t * 3))
    rr(c, -34, -44, 68, 88, 6); C(c, GOLD); c.fill_preserve(); stroke_(c, NAVY, 4)
    rr(c, -34, -44, 14, 88, 0); C(c, NAVY); c.fill()
    c.move_to(-4, -14); c.line_to(22, -14); stroke_(c, NAVY, 4); c.move_to(-4, 2); c.line_to(16, 2); stroke_(c, NAVY, 4)
    c.restore()
    if 26.0 < t < 27.4:
        q = (t - 26.0) / 1.4; sparkle(c, bx, by, 40 + 70 * q, 1 - q)
    if t > 26.2:
        for k in range(8):
            q = (t - 26.2 - k * 0.12) / 1.6
            if 0 < q < 1:
                x = 790 + 120 * math.sin(k * 1.7); y = 1180 - 260 * ease(q)
                c.save(); c.translate(x, y); c.scale(1 - 0.3 * q, 1 - 0.3 * q)
                c.move_to(0, 12); c.curve_to(-22, -8, -10, -24, 0, -10); c.curve_to(10, -24, 22, -8, 0, 12); C(c, TERRA, 1 - q); c.fill(); c.restore()

FAM = [(240, SK2, "white", (235, 235, 235), (112, 120, 134), (70, 76, 92), 0), (440, SK1, "short", NAVY, NAVY, (60, 70, 96), 1),
       (640, SK3, "long", (40, 30, 40), TERRA, (80, 60, 90), 2), (830, SK3, "ponytail", (40, 30, 40), MUST, (80, 100, 130), 3)]
def scene5(c, t):
    t0 = 28.4
    a = win(t, t0, t0 + 0.9)
    c.save(); c.translate(0, 30 * (1 - a))
    circ(c, 540, 400, 78, GOLD); circ(c, 540, 400, 66, NAVY)
    say(540, 400, "D", FONTS["logo"], GOLD, a, "m")
    c.restore()
    say(540, 540, "DDS CAPITAL WEALTH", FONTS["brand"], NAVY, win(t, t0 + 0.3, t0 + 1.2), "m", 8)
    say(540, 690, "Wealth, organised", FONTS["big"], NAVY, win(t, t0 + 0.5, t0 + 1.4), "m")
    say(540, 790, "for families.", FONTS["bigi"], GOLDD, win(t, t0 + 0.8, t0 + 1.7), "m")
    q = win(t, t0 + 1.2, t0 + 2.0)
    c.move_to(540 - 90 * q, 870); c.line_to(540 + 90 * q, 870); stroke_(c, GOLD, 4)
    say(540, 925, "Follow  @dds_capital", FONTS["hand"], NAVY, win(t, t0 + 1.4, t0 + 2.2), "m", 2)
    for i, (x, sk, hr, hc, sh, pn, k) in enumerate(FAM):
        aa = win(t, t0 + 0.2 + i * 0.15, t0 + 1.0 + i * 0.15)
        sc = 0.58 if k == 3 else 0.7 if k < 3 else 0.7
        sc = 0.52 if k == 3 else 0.68
        wave_ = (2.7 + 0.25 * math.sin(t * 7 + k)) if k == 2 else 0.12
        grp(c, aa, lambda x=x, sk=sk, hr=hr, hc=hc, sh=sh, pn=pn, k=k, sc=sc, wave_=wave_:
            person(c, x, 1450, sc, sk, hr, hc, sh, pn, "smile", 0.12, wave_, 3 * math.sin(t * 2 + k),
                   headr=1.18 if k == 3 else 1.0, glasses=(k == 0), bindi=(k == 2), stripe=GOLD if k == 2 else None))
    y = 1600
    da = win(t, t0 + 1.8, t0 + 2.6)
    for ln in ["AMFI-registered Mutual Fund Distributor, ARN-359084.",
               "Mutual fund investments are subject to market risks; read all scheme",
               "related documents carefully. Educational content; not investment advice."]:
        say(540, y, ln, FONTS["disc"], GREY, da, "m"); y += 32

CAPS = [(0.0, 6.6, "THE PROBLEM", "Money, papers and decisions — scattered in many places."),
        (7.0, 13.8, "ONE CLEAR PICTURE", "A family wealth office brings it all together in one place."),
        (14.2, 21.2, "STEADY REVIEWS", "Reviews happen on a calendar — not on market-day panic."),
        (21.9, 28.2, "NEXT GENERATION", "So the next generation can pick up where you left off.")]

def wrap_t(d, s, font, width):
    out, cur = [], ""
    for w_ in s.split():
        tt = (cur + " " + w_).strip()
        if d.textlength(tt, font=font) <= width: cur = tt
        else: out.append(cur); cur = w_
    if cur: out.append(cur)
    return out

def render(t):
    TXT.clear()
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    c.set_antialias(cairo.ANTIALIAS_BEST)
    draw_bg(c); doodles(c, t)
    CUR_A[0] = 1.0
    a12 = 1 - win(t, 13.6, 14.3)
    if t < 14.4: grp(c, a12, lambda: scene12(c, t))
    a3 = win(t, 13.9, 14.6) * (1 - win(t, 21.3, 22.0))
    if 13.8 < t < 22.1: grp(c, a3, lambda: scene3(c, t))
    a4 = win(t, 21.6, 22.3) * (1 - win(t, 28.0, 28.7))
    if 21.5 < t < 28.8: grp(c, a4, lambda: scene4(c, t))
    a5 = win(t, 28.3, 29.0)
    if t > 28.2: grp(c, a5, lambda: scene5(c, t))
    # brand strip (hidden on end card)
    ba = win(t, 0.3, 1.0) * (1 - win(t, 28.2, 28.8))
    say(540, 120, "DDS CAPITAL WEALTH", FONTS["brand"], GOLDD, ba, "m", 7)
    # captions
    for (a, b, kick, cap) in CAPS:
        al = win(t, a + 0.2, a + 0.9) * (1 - win(t, b - 0.5, b))
        if al > 0.01:
            say(540, 1565, kick, FONTS["kick"], GOLDD, al, "m", 6)
            tmp = ImageDraw.Draw(Image.new("RGB", (4, 4)))
            lines = wrap_t(tmp, cap, FONTS["cap"], 880)
            for i, ln in enumerate(lines):
                say(540, 1640 + i * 70 - (len(lines) - 1) * 0, ln, FONTS["cap"], NAVY, al, "m")
    # to PIL
    buf = np.frombuffer(s.get_data(), np.uint8).reshape(H, W, 4)
    img = Image.fromarray(buf[:, :, [2, 1, 0]].copy())
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for (x, y, tx, font, fill, al, anchor, tr) in TXT:
        if al <= 0.01: continue
        f = fill + (int(255 * min(1, al)),)
        if tr:
            tw = sum(d.textlength(ch, font=font) + tr for ch in tx) - tr; xx = x - tw / 2
            for ch in tx:
                d.text((xx, y), ch, font=font, fill=f, anchor="lm"); xx += d.textlength(ch, font=font) + tr
        else:
            d.text((x, y), tx, font=font, fill=f, anchor="mm" if anchor == "m" else "lm")
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    g = min(1.0, t / 0.5) * min(1.0, (DUR - t) / 0.6)
    if g < 1.0: img = Image.blend(Image.new("RGB", (W, H), CREAM), img, g)
    return img

# ---------------- audio ----------------
def make_audio(path):
    SR = 44100; n = int(SR * DUR); aud = np.zeros(n)
    def note(f, t0, dur, vol=1.0, bright=1.0):
        i0 = int(t0 * SR); m = int(dur * SR)
        if i0 >= n: return
        m = min(m, n - i0); tt = np.arange(m) / SR
        w = (np.sin(2 * np.pi * f * tt) + 0.35 * bright * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-6 * tt) + 0.12 * np.sin(2 * np.pi * 3.01 * f * tt) * np.exp(-9 * tt))
        aud[i0:i0 + m] += vol * w * np.exp(-3.2 * tt) * np.minimum(1, tt / 0.004)
    prog = [(261.63, [0, 4, 7]), (220.0, [0, 3, 7]), (174.61, [0, 4, 7]), (196.0, [0, 4, 7])]
    beat = 60 / 100.0; ci = 0; t0 = 0.0
    while t0 < DUR - 1.5:
        root, iv = prog[int(t0 / (beat * 4)) % 4]
        k = int(t0 / beat) % 8
        semis = [0, 4, 7, 12, 7, 4, 12, 16][k] if iv[1] == 4 else [0, 3, 7, 12, 7, 3, 12, 15][k]
        note(root * 2 ** (semis / 12), t0, 0.9, 0.5)
        if k % 4 == 0: note(root / 2, t0, 1.6, 0.5, 0.2)
        t0 += beat / 1.0 * 0.5 * 2
    for k in range(8): note(660 * 2 ** (k / 12), LAND0 + k * STEP + FLY, 0.5, 0.35)
    for n_, tt in enumerate([15.2, 16.7, 18.2, 19.7]): note(988, tt, 0.5, 0.3)
    for tt in (24.9, 26.0): note(1318, tt, 0.8, 0.3)
    aud /= np.abs(aud).max()
    aud *= 0.5 * np.minimum(1, np.arange(n) / SR / 1.0) * np.minimum(1, (DUR - np.arange(n) / SR) / 1.5)
    pcm = (aud * 32767).astype("<i2")
    with wave.open(path, "wb") as w_:
        w_.setnchannels(1); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes(pcm.tobytes())

if __name__ == "__main__":
    if sys.argv[1] == "prev":
        for sec in [float(x) for x in sys.argv[2:]]:
            render(sec).save(SP + f"p2_{sec}.png")
    else:
        make_audio(SP + "a2.wav")
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                              "-r", str(FPS), "-i", "-", "-i", SP + "a2.wav", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17",
                              "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", sys.argv[2]],
                             stdin=subprocess.PIPE)
        for i in range(FPS * DUR):
            p.stdin.write(render(i / FPS).tobytes())
        p.stdin.close(); p.wait()
