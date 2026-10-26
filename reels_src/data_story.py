import sys, math, subprocess
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cairo
from PIL import Image, ImageDraw
import engine as R
from engine import *

DUR2 = 38
SP = R.SP

# ---- data: year-end closes (NSE Nifty 50 price index) ----
NSE = {2007: 6138.60, 2008: 2959.15, 2009: 5201.05, 2010: 6134.50, 2011: 4624.30, 2012: 5905.10, 2013: 6304.00,
       2014: 8282.70, 2015: 7946.35, 2016: 8185.80, 2017: 10530.70, 2018: 10862.55, 2019: 12168.45, 2020: 13981.75,
       2021: 17354.05, 2022: 18105.30, 2023: 21731.40, 2024: 23644.80, 2025: 26129.60}
YF = {2007: 6139, 2008: 2959, 2009: 5201, 2010: 6135, 2011: 4624, 2012: 5905, 2013: 6304, 2014: 8283, 2015: 7946,
      2016: 8186, 2017: 10531, 2018: 10863, 2019: 12168, 2020: 13982, 2021: 17354, 2022: 18105, 2023: 21731,
      2024: 23645, 2025: 26130}
YEARS = sorted(NSE)
assert all(abs(NSE[y] - YF[y]) <= 0.6 for y in YEARS), "sources disagree"
RET = {y: (NSE[y] / NSE[y - 1] - 1) * 100 for y in YEARS[1:]}
FALLS = [y for y in YEARS[1:] if RET[y] < 0]
assert FALLS == [2008, 2011, 2015], FALLS
NEXT = {y: RET[y + 1] for y in FALLS}
assert all(v > 0 for v in NEXT.values())

def f1(x): return f"{x:+.1f}%".replace("-", "−")

# chart geometry
PX0, PX1, PY0, PY1 = 160, 960, 540, 1110   # plot area (y top .. bottom)
YMAX = 28000.0
def cx(i): return PX0 + (PX1 - PX0) * i / (len(YEARS) - 1)
def cy(v): return PY1 - (PY1 - PY0) * v / YMAX

def sceneA(c, t):
    # big phone with falling line, worried papa
    a = win(t, 0.3, 1.0)
    c.save(); c.translate(540, 770)
    c.translate(0, 8 * math.sin(t * 1.5))
    rr(c, -230, -330, 460, 660, 54); C(c, NAVY); c.fill()
    rr(c, -204, -296, 408, 592, 30); C(c, (236, 238, 244)); c.fill()
    pts = [(-170, -150), (-120, -110), (-80, -150), (-30, -40), (10, -80), (60, 60), (100, 20), (160, 170)]
    q = win(t, 0.8, 4.2) * len(pts)
    c.move_to(*pts[0])
    for i in range(1, len(pts)):
        if q >= i: c.line_to(*pts[i])
        elif q > i - 1:
            f = q - (i - 1); c.line_to(lerp(pts[i - 1][0], pts[i][0], f), lerp(pts[i - 1][1], pts[i][1], f))
    stroke_(c, RED, 12)
    # red tag
    if q > 5:
        rr(c, 40, 195, 160, 58, 14); C(c, RED); c.fill()
        c.move_to(70, 214); c.line_to(86, 236); c.line_to(102, 214); stroke_(c, PAPER, 6)
        c.move_to(122, 225); c.line_to(178, 225); stroke_(c, PAPER, 6)
    c.restore()
    # papa (watching), question marks
    person(c, 540, 1470, 0.74, SK1, "short", NAVY, NAVY, (60, 70, 96), "worry", 2.7 + 0.1 * math.sin(t * 3), 0.2, 3 * math.sin(t * 2.2), look=0)
    for k, dx in enumerate((-320, 320)):
        c.save(); c.translate(540 + dx, 1000 + 12 * math.sin(t * 3 + k)); C(c, GOLDD, win(t, 2.0 + k * 0.4, 2.8 + k * 0.4))
        c.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(90)
        c.move_to(0, 0); c.show_text("?"); c.restore()

def sceneB(c, t):
    t0 = 7.4
    ap = ease((t - t0) / 0.8)
    c.save(); c.translate(0, 40 * (1 - ap))
    rr(c, 70, 410, 940, 790, 32); C(c, NAVY, 0.10); c.translate(8, 12); c.fill(); c.translate(-8, -12)
    rr(c, 70, 410, 940, 790, 32); C(c, PAPER); c.fill_preserve(); stroke_(c, NAVY, 5)
    say(540, 470, "NIFTY 50  ·  YEAR-END LEVEL", FONTS["lab"], NAVY, ap, "m", 4)
    for v in (0, 10000, 20000):
        y = cy(v); c.move_to(PX0, y); c.line_to(PX1, y); stroke_(c, GREY, 2, 0.35)
        say(PX0 - 14, y, f"{v:,}", FONTS["labs"], GREY, ap, "r")
    for i, y_ in enumerate(YEARS):
        if (y_ - 2007) % 3 == 0: say(cx(i), PY1 + 32, str(y_), FONTS["labs"], GREY, ap, "m")
    prog = max(0.0, (t - 8.3) / 6.4) * (len(YEARS) - 1)
    # area + line
    pts = []
    for i, y_ in enumerate(YEARS):
        if i <= prog: pts.append((cx(i), cy(NSE[y_])))
        elif i - 1 < prog:
            f = prog - (i - 1); x0, y0 = cx(i - 1), cy(NSE[YEARS[i - 1]]); pts.append((lerp(x0, cx(i), f), lerp(y0, cy(NSE[y_]), f)))
    if len(pts) > 1:
        c.move_to(pts[0][0], PY1)
        for p in pts: c.line_to(*p)
        c.line_to(pts[-1][0], PY1); c.close_path(); C(c, GOLD, 0.22); c.fill()
        c.move_to(*pts[0])
        for p in pts[1:]: c.line_to(*p)
        stroke_(c, NAVY, 7)
        circ(c, pts[-1][0], pts[-1][1], 9, GOLDD)
    # fall markers
    for y_ in FALLS:
        i = YEARS.index(y_)
        q = back((prog - i) / 0.6) if prog >= i else 0
        if q > 0:
            x, yy = cx(i), cy(NSE[y_])
            circ(c, x, yy, 17 * q, RED); circ(c, x, yy, 7 * q, PAPER)
            lab = f"{y_}  {f1(RET[y_])}"
            ly = {2008: 600, 2011: 665, 2015: 600}[y_]
            bx = max(x, PX0 + 95)
            c.move_to(x, yy - 20); c.line_to(x, ly + 22); stroke_(c, RED, 3, min(1, q))
            rr(c, bx - 82, ly - 20, 164, 42, 12); C(c, RED, min(1, q)); c.fill()
            say(bx, ly + 1, lab, FONTS["labs"], PAPER, min(1, q), "m")
    c.restore()
    say(540, 1262, "Year-end closing values, price index (excludes dividends)", FONTS["labs"], GREY, ap, "m")

def sceneC(c, t):
    t0 = 19.4
    for k, y_ in enumerate(FALLS):
        ts = t0 + 0.5 + k * 2.8
        a_ = ease((t - ts) / 0.5)
        if a_ <= 0.01: continue
        off = 40 * (1 - a_)
        top = 400 + k * 270
        def card(top=top, y_=y_, off=off):
            c.save(); c.translate(0, off)
            rr(c, 88, top + 10, 920, 210, 28); C(c, NAVY, 0.10); c.fill()
            rr(c, 80, top, 920, 210, 28); C(c, PAPER); c.fill_preserve(); stroke_(c, NAVY, 5)
            c.move_to(450, top + 105); c.line_to(630, top + 105); stroke_(c, GOLDD, 8)
            c.move_to(605, top + 78); c.line_to(634, top + 105); c.line_to(605, top + 132); stroke_(c, GOLDD, 8)
            c.restore()
            say(280, top + 60 + off, str(y_), FONTS["lab"], GREY, 1, "m", 3)
            say(280, top + 135 + off, f1(RET[y_]), FONTS["big"], RED, 1, "m")
            say(540, top + 60 + off, "next year", FONTS["labs"], GREY, 1, "m")
            say(800, top + 60 + off, str(y_ + 1), FONTS["lab"], GREY, 1, "m", 3)
            say(800, top + 135 + off, f1(NEXT[y_]), FONTS["big"], GREEN, 1, "m")
        grp(c, a_, card)
        if ts + 0.9 <= t < ts + 1.6:
            qq = (t - ts - 0.9) / 0.7; sparkle(c, 800, top + 105, 60 + 60 * qq, 1 - qq, GOLD)
    fa = win(t, t0 + 8.2, t0 + 9.0)
    say(540, 1240, "3 instances. Past data — not a forecast.", FONTS["hand"], NAVY, fa, "m")

def sceneD(c, t):
    t0 = 29.6
    c.save(); c.translate(540, 1640); c.scale(1, 0.30); circ(c, 0, 0, 1000, (232, 222, 198)); c.restore()
    b = 3 * math.sin(t * 2)
    # little scene: family planning at a table w/ book
    a = win(t, t0, t0 + 0.8)
    # open book / plan card
    c.save(); c.translate(540, 760 + 6 * math.sin(t * 1.5))
    rr(c, -290, -190, 580, 380, 34); C(c, PAPER); c.fill_preserve(); stroke_(c, NAVY, 5)
    c.move_to(0, -190); c.line_to(0, 190); stroke_(c, NAVY, 3, 0.5)
    for i in range(4):
        w = [200, 160, 210, 120][i]
        c.move_to(-250, -120 + i * 60); c.line_to(-250 + w, -120 + i * 60); stroke_(c, GREY, 6, 0.45)
    # ticks on right page
    for i in range(3):
        q = back((t - (t0 + 0.8 + i * 0.7)) / 0.5)
        if q > 0:
            y = -110 + i * 90
            circ(c, 60, y, 28 * q, GOLD)
            c.move_to(48, y); c.line_to(58, y + 11); c.line_to(76, y - 11); stroke_(c, NAVY, 6 * q)
            c.move_to(110, y); c.line_to(240 * (0.5 + 0.5 * (i % 2)), y); stroke_(c, GREY, 6, 0.45)
    c.restore()
    person(c, 360, 1490, 0.8, SK1, "short", NAVY, NAVY, (60, 70, 96), "smile", 0.12, 1.1, b)
    person(c, 560, 1490, 0.8, SK3, "long", (40, 30, 40), TERRA, (80, 60, 90), "smile", 1.0, 0.12, -b, bindi=True, stripe=GOLD)
    person(c, 760, 1490, 0.58, SK3, "ponytail", (40, 30, 40), MUST, (80, 100, 130), "open", 1.0, 0.12, 0, headr=1.18, look=-0.6)

FAM2 = R.FAM
def sceneE(c, t):
    t0 = 35.0
    a = win(t, t0, t0 + 0.8)
    c.save(); c.translate(0, 30 * (1 - a))
    circ(c, 540, 330, 78, GOLD); circ(c, 540, 330, 66, NAVY)
    say(540, 330, "D", FONTS["logo"], GOLD, a, "m")
    c.restore()
    say(540, 470, "DDS CAPITAL WEALTH", FONTS["brand"], NAVY, win(t, t0 + 0.3, t0 + 1.0), "m", 8)
    say(540, 600, "Wealth, organised", FONTS["big"], NAVY, win(t, t0 + 0.4, t0 + 1.2), "m")
    say(540, 700, "for families.", FONTS["bigi"], GOLDD, win(t, t0 + 0.6, t0 + 1.4), "m")
    q = win(t, t0 + 1.0, t0 + 1.8)
    c.move_to(540 - 90 * q, 775); c.line_to(540 + 90 * q, 775); stroke_(c, GOLD, 4)
    say(540, 825, "Follow  @dds_capital", FONTS["hand"], NAVY, win(t, t0 + 1.2, t0 + 1.9), "m", 2)
    for i, (x, sk, hr, hc, sh, pn, k) in enumerate(FAM2):
        aa = win(t, t0 + 0.2 + i * 0.1, t0 + 0.9 + i * 0.1)
        sc = 0.52 if k == 3 else 0.62
        wv = (2.7 + 0.25 * math.sin(t * 7 + k)) if k == 2 else 0.12
        grp(c, aa, lambda x=x, sk=sk, hr=hr, hc=hc, sh=sh, pn=pn, k=k, sc=sc, wv=wv:
            person(c, x, 1330, sc, sk, hr, hc, sh, pn, "smile", 0.12, wv, 3 * math.sin(t * 2 + k),
                   headr=1.18 if k == 3 else 1.0, glasses=(k == 0), bindi=(k == 2), stripe=GOLD if k == 2 else None))
    da = win(t, t0 + 1.4, t0 + 2.2); y = 1470
    for ln in ["Source: NSE Nifty 50 year-end closing values (price index), cross-checked",
               "with a second public data source. Past performance is not indicative of",
               "future returns. AMFI-registered Mutual Fund Distributor, ARN-359084. Mutual",
               "fund investments are subject to market risks; read all scheme related",
               "documents carefully. Educational content; not investment advice."]:
        say(540, y, ln, FONTS["disc"], GREY, da, "m"); y += 32

CAPS2 = [(0.0, 7.2, "MARKET FALLS", "Markets fall. And every time it feels like this time is different."),
         (7.6, 19.2, "THE DATA", "In the 18 calendar years from 2008 to 2025, only 3 ended lower."),
         (19.6, 29.2, "WHAT CAME NEXT", "In each case, the following year ended higher."),
         (29.8, 34.8, "THE TAKEAWAY", "Falls are normal. A written plan helps families stay steady.")]

def render(t):
    R.TXT.clear()
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    c.set_antialias(cairo.ANTIALIAS_BEST)
    draw_bg(c); doodles(c, t)
    R.CUR_A[0] = 1.0
    if t < 7.9: grp(c, 1 - win(t, 7.0, 7.7), lambda: sceneA(c, t))
    if 7.3 < t < 19.9: grp(c, win(t, 7.4, 8.0) * (1 - win(t, 19.0, 19.6)), lambda: sceneB(c, t))
    if 19.3 < t < 30.0: grp(c, win(t, 19.4, 20.0) * (1 - win(t, 29.2, 29.8)), lambda: sceneC(c, t))
    if 29.4 < t < 35.4: grp(c, win(t, 29.6, 30.2) * (1 - win(t, 34.6, 35.2)), lambda: sceneD(c, t))
    if t > 34.8: grp(c, win(t, 35.0, 35.7), lambda: sceneE(c, t))
    ba = win(t, 0.3, 1.0) * (1 - win(t, 34.6, 35.2))
    say(540, 120, "DDS CAPITAL WEALTH", FONTS["brand"], GOLDD, ba, "m", 7)
    for (a, b, kick, cap) in CAPS2:
        al = win(t, a + 0.2, a + 0.9) * (1 - win(t, b - 0.5, b))
        if al > 0.01:
            say(540, 1565, kick, FONTS["kick"], GOLDD, al, "m", 6)
            lines = wrap_t(ImageDraw.Draw(Image.new("RGB", (4, 4))), cap, FONTS["cap"], 880)
            for i, ln in enumerate(lines): say(540, 1640 + i * 70, ln, FONTS["cap"], NAVY, al, "m")
    buf = np.frombuffer(s.get_data(), np.uint8).reshape(H, W, 4)
    img = Image.fromarray(buf[:, :, [2, 1, 0]].copy())
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for (x, y, tx, font, fill, al, anchor, tr) in R.TXT:
        if al <= 0.01: continue
        f = fill + (int(255 * min(1, al)),)
        if tr:
            tw = sum(d.textlength(ch, font=font) + tr for ch in tx) - tr; xx = x - tw / 2
            for ch in tx:
                d.text((xx, y), ch, font=font, fill=f, anchor="lm"); xx += d.textlength(ch, font=font) + tr
        else:
            d.text((x, y), tx, font=font, fill=f, anchor={"m": "mm", "r": "rm"}.get(anchor, "lm"))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    g = min(1.0, t / 0.5) * min(1.0, (DUR2 - t) / 0.6)
    if g < 1.0: img = Image.blend(Image.new("RGB", (W, H), CREAM), img, g)
    return img

def music():
    import wave
    R.DUR = DUR2
    # reuse reel2 audio generator with longer duration
    R.make_audio(SP + "a3.wav")

if __name__ == "__main__":
    print("falls", FALLS, {y: round(RET[y], 2) for y in FALLS}, {y + 1: round(NEXT[y], 2) for y in FALLS})
    if sys.argv[1] == "prev":
        for sec in [float(x) for x in sys.argv[2:]]: render(sec).save(SP + f"p3_{sec}.png")
    elif sys.argv[1] == "audio":
        music()
    else:
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                              "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "medium", "-an", sys.argv[2]], stdin=subprocess.PIPE)
        for i in range(FPS * DUR2): p.stdin.write(render(i / FPS).tobytes())
        p.stdin.close(); p.wait()
