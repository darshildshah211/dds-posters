"""DDS Capital Instagram poster generator.
Feed posts 1080x1350 (4:5) and Stories 1080x1920 (9:16), IBM Plex, monochrome.
Stories keep key content inside y=270..1650 (clear of Instagram's UI overlays).
"""
import json
import sys
from PIL import Image, ImageDraw, ImageFont

BLACK = (17, 17, 17)
WHITE = (255, 255, 255)
GREY = (90, 90, 90)
LIGHT = (200, 200, 200)
M = 80
F = "/usr/share/fonts/truetype/ibm-plex/"
DISCLAIMER = ("Investments in securities are subject to market risk. For informational "
              "and educational purposes only; not investment advice.")


def fnt(name, size):
    return ImageFont.truetype(F + name, size)


SB = lambda s: fnt("IBMPlexSerif-Bold.ttf", s)
SS = lambda s: fnt("IBMPlexSerif-SemiBold.ttf", s)
SI = lambda s: fnt("IBMPlexSerif-Italic.ttf", s)
MR = lambda s: fnt("IBMPlexMono-Regular.ttf", s)
MM = lambda s: fnt("IBMPlexMono-Medium.ttf", s)


def wrap(d, text, font, width):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= width:
            cur = t
        else:
            out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def tracked(d, xy, text, font, fill, tr=3):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + tr


def para(d, x, y, text, font, fill, width, lh):
    for ln in wrap(d, text, font, width):
        d.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def footer(d, W, y, fg=BLACK, sub=GREY, cta="To know more, contact us."):
    d.line([(M, y), (W - M, y)], fill=fg, width=2)
    d.text((M, y + 22), cta, font=SI(24), fill=fg)
    yy = y + 60
    for ln in wrap(d, DISCLAIMER, MR(15), W - 2 * M):
        d.text((M, yy), ln, font=MR(15), fill=sub)
        yy += 20


def feed_canvas():
    img = Image.new("RGB", (1080, 1350), WHITE)
    d = ImageDraw.Draw(img)
    tracked(d, (M, 70), "DDS CAPITAL WEALTH", MM(24), BLACK)
    d.line([(M, 112), (1080 - M, 112)], fill=BLACK, width=2)
    return img, d


def sample_tag(d, W, y):
    d.rectangle([W - M - 230, y, W - M, y + 36], outline=GREY, width=2)
    d.text((W - M - 218, y + 8), "SAMPLE LAYOUT", font=MM(16), fill=GREY)


# ---------------- FEED: hero stat ----------------
def feed_hero(path, eyebrow, hero, suffix, subject, lines, tagline, sample=False):
    img, d = feed_canvas()
    W = 1080
    hero_f = SB(240)
    hh = 250
    sub_lines = wrap(d, subject, SS(40), W - 2 * M)
    body_h = len(lines) * 36
    tag_lines = wrap(d, tagline, SI(34), W - 2 * M)
    total = 34 + 30 + hh + 30 + len(sub_lines) * 52 + 20 + body_h + 50 + 40 + len(tag_lines) * 46
    y = 150 + (1170 - 150 - total) // 2
    tracked(d, (M, y), eyebrow.upper(), MM(22), BLACK)
    y += 64
    d.text((M, y), hero, font=hero_f, fill=BLACK)
    if suffix:
        d.text((M + d.textlength(hero, font=hero_f) + 14, y + 130), suffix, font=SS(52), fill=BLACK)
    y += hh + 30
    y = para(d, M, y, subject, SS(40), BLACK, W - 2 * M, 52) + 20
    for ln in lines:
        d.text((M, y), ln, font=MR(25), fill=(60, 60, 60))
        y += 36
    y += 36
    d.line([(M, y), (M + 90, y)], fill=BLACK, width=4)
    y += 34
    para(d, M, y, tagline, SI(34), BLACK, W - 2 * M, 46)
    if sample:
        sample_tag(d, W, 128)
    footer(d, W, 1200)
    img.save(path)


# ---------------- FEED: numbered checklist ----------------
def feed_checklist(path, eyebrow, title, items, tagline, sample=False):
    img, d = feed_canvas()
    W = 1080
    t_lines = wrap(d, title.upper(), SB(54), W - 2 * M)
    item_h = []
    for _, head, body in items:
        item_h.append(52 + len(wrap(d, body, MR(24), W - 2 * M - 120)) * 34 + 34)
    tag_lines = wrap(d, tagline, SI(32), W - 2 * M)
    total = 34 + 56 + len(t_lines) * 64 + 30 + sum(item_h) + 30 + len(tag_lines) * 44
    y = 150 + (1170 - 150 - total) // 2
    tracked(d, (M, y), eyebrow.upper(), MM(22), BLACK)
    y += 56
    for ln in t_lines:
        d.text((M, y), ln, font=SB(54), fill=BLACK)
        y += 64
    y += 30
    for (num, head, body), h in zip(items, item_h):
        d.line([(M, y), (W - M, y)], fill=LIGHT, width=2)
        d.text((M, y + 16), num, font=MM(44), fill=BLACK)
        d.text((M + 120, y + 14), head, font=SS(34), fill=BLACK)
        para(d, M + 120, y + 62, body, MR(24), (60, 60, 60), W - 2 * M - 120, 34)
        y += h
    y += 30
    para(d, M, y, tagline, SI(32), BLACK, W - 2 * M, 44)
    if sample:
        sample_tag(d, W, 128)
    footer(d, W, 1200)
    img.save(path)


# ---------------- FEED: scoreboard ----------------
def feed_scoreboard(path, headline, boxes, insight, tagline, sample=False):
    img, d = feed_canvas()
    W = 1080
    h_lines = wrap(d, headline.upper(), SB(52), W - 2 * M)
    i_lines = wrap(d, insight, SS(30), W - 2 * M - 56)
    ibox = len(i_lines) * 42 + 56
    t_lines = wrap(d, tagline, SI(30), W - 2 * M)
    total = len(h_lines) * 62 + 34 + 240 + 40 + ibox + 34 + len(t_lines) * 40
    y = 150 + (1170 - 150 - total) // 2
    for ln in h_lines:
        d.text((M, y), ln, font=SB(52), fill=BLACK)
        y += 62
    y += 34
    bw = (W - 2 * M - 48) // 3
    x = M
    for label, val, sub in boxes:
        d.rectangle([x, y, x + bw, y + 240], outline=BLACK, width=2)
        ly = y + 20
        for ln in wrap(d, label.upper(), MR(15), bw - 30):
            d.text((x + 18, ly), ln, font=MR(15), fill=GREY)
            ly += 20
        vf = SB(46) if len(val) <= 7 else SB(34)
        d.text((x + 18, y + 240 - 112), val, font=vf, fill=BLACK)
        d.text((x + 18, y + 240 - 42), sub, font=MR(16), fill=GREY)
        x += bw + 24
    y += 240 + 40
    d.rectangle([M, y, W - M, y + ibox], fill=BLACK)
    para(d, M + 28, y + 28, insight, SS(30), WHITE, W - 2 * M - 56, 42)
    y += ibox + 34
    para(d, M, y, tagline, SI(30), BLACK, W - 2 * M, 40)
    if sample:
        sample_tag(d, W, 128)
    footer(d, W, 1200)
    img.save(path)


# ---------------- STORY canvases ----------------
def story_canvas(bg):
    return Image.new("RGB", (1080, 1920), bg)


# ---------------- STORY: quote (inverted, black) ----------------
def story_quote(path, quote, attribution, sample=False):
    img = story_canvas(BLACK)
    d = ImageDraw.Draw(img)
    W = 1080
    tracked(d, (M, 280), "DDS CAPITAL WEALTH", MM(24), WHITE)
    d.line([(M, 322), (W - M, 322)], fill=WHITE, width=2)
    qf = SI(70)
    lines = wrap(d, quote, qf, W - 2 * M)
    h = len(lines) * 96
    y = 330 + (1560 - 330 - (h + 190 + 90)) // 2
    d.text((M - 6, y - 40), "“", font=SB(240), fill=(70, 70, 70))
    y += 150
    for ln in lines:
        d.text((M, y), ln, font=qf, fill=WHITE)
        y += 96
    y += 40
    d.line([(M, y), (M + 90, y)], fill=WHITE, width=4)
    d.text((M, y + 28), attribution, font=MM(26), fill=LIGHT)
    if sample:
        d.rectangle([W - M - 230, 340, W - M, 376], outline=LIGHT, width=2)
        d.text((W - M - 218, 348), "SAMPLE LAYOUT", font=MM(16), fill=LIGHT)
    footer(d, W, 1600, fg=WHITE, sub=(150, 150, 150))
    img.save(path)


# ---------------- STORY: IPO listing ----------------
def story_ipo(path, company, segment, date, issue, listing, source, sample=False):
    gain = (listing - issue) / issue * 100
    sign = "+" if gain >= 0 else "−"
    img = story_canvas(WHITE)
    d = ImageDraw.Draw(img)
    W = 1080
    tracked(d, (M, 280), "DDS CAPITAL WEALTH", MM(24), BLACK)
    d.line([(M, 322), (W - M, 322)], fill=BLACK, width=2)
    tracked(d, (M, 400), "IPO LISTING · " + date.upper(), MM(22), BLACK)
    y = 460
    for ln in wrap(d, company, SB(72), W - 2 * M):
        d.text((M, y), ln, font=SB(72), fill=BLACK)
        y += 86
    d.text((M, y + 6), segment, font=MR(26), fill=GREY)
    y += 90
    big = f"{sign}{abs(gain):.1f}%"
    d.text((M, y), big, font=SB(250), fill=BLACK)
    y += 290
    d.text((M, y), "LISTING GAIN VS ISSUE PRICE", font=MM(22), fill=GREY)
    y += 70
    bw = (W - 2 * M - 24) // 2
    for i, (lab, val) in enumerate([("ISSUE PRICE", issue), ("LISTING PRICE", listing)]):
        x = M + i * (bw + 24)
        d.rectangle([x, y, x + bw, y + 190], outline=BLACK, width=2)
        d.text((x + 24, y + 24), lab, font=MR(18), fill=GREY)
        d.text((x + 24, y + 80), f"₹{val:,.2f}".replace(".00", ""), font=SB(60), fill=BLACK)
    y += 190 + 50
    para(d, M, y, "Listing gain is the first-trade price versus issue price. It is not a "
         "return you can bank: many IPOs give it back.", SI(30), BLACK, W - 2 * M, 42)
    d.text((M, 1560), "Source: " + source, font=MR(18), fill=GREY)
    if sample:
        d.rectangle([W - M - 230, 340, W - M, 376], outline=GREY, width=2)
        d.text((W - M - 218, 348), "SAMPLE LAYOUT", font=MM(16), fill=GREY)
    footer(d, W, 1600)
    img.save(path)


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    kind = spec.pop("kind")
    out = spec.pop("path")
    {"feed_hero": feed_hero, "feed_checklist": feed_checklist,
     "feed_scoreboard": feed_scoreboard, "story_quote": story_quote,
     "story_ipo": story_ipo}[kind](out, **spec)
