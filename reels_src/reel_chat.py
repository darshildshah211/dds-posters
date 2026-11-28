"""DDS reel v3: 'chat from your future self' format. Lock-screen notification hook -> chat bubbles with typing dots,
one continuous narrator voice (Kokoro, lang hi), optional stat card with count-up, CTA end card. Usage:
  python3 -I reels_src/reel_chat.py spec.json out_prefix [voice1,voice2,...]
Writes out_prefix-<voice>.mp4 for each voice (video is rendered once, audio muxed per voice).
spec: {"hook":{"text":"Roman","voice":"Devanagari"},
       "items":[{"who":"future","text":"..","voice":".."} | {"who":"me","text":".."} (silent reply) |
                {"who":"future","stat":{"a_label","a_value","b_label","b_to":number,"b_prefix":"₹","note":".."},"text":"short caption","voice":".."}],
       "end":{"text":"..","voice":"..","button":"SAVE · SHARE · COMMENT"}}"""
import json, os, subprocess, sys, tempfile
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont
W, H, FPS, M = 1080, 1920, 30, 70
NAVY, GOLD, CREAM, CORAL, GREEN, INK = (11, 31, 58), (255, 180, 0), (255, 246, 229), (255, 90, 95), (0, 168, 107), (17, 24, 39)
P = "/usr/share/fonts/truetype/google-fonts/"
PF = lambda s, w="Bold": ImageFont.truetype(f"{P}Poppins-{'Medium' if w == 'SemiBold' else w}.ttf", s)
MONO = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/ibm-plex/IBMPlexMono-Regular.ttf", s)
DISC = "AMFI Registered Mutual Fund Distributor (ARN-359084). Mutual fund investments are subject to market risks; read all scheme related documents carefully. Educational content, not advice or a recommendation."
ease = lambda p: 1 - (1 - min(max(p, 0), 1)) ** 3
mixc = lambda a, b, p: tuple(int(a[i] + (b[i] - a[i]) * p) for i in range(3))
_d = ImageDraw.Draw(Image.new("RGB", (10, 10)))


def wrap(text, font, width):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if _d.textlength(t, font=font) <= width or not cur: cur = t
        else: out.append(cur); cur = w
    return out + [cur]


def tts(lines, voice, speed=0.92):
    from kokoro_onnx import Kokoro
    M_DIR = os.environ.get("REEL_MODELS", "/tmp/reel_models")
    k = Kokoro(f"{M_DIR}/kokoro-v1.0.onnx", f"{M_DIR}/voices-v1.0.bin"); out = []
    for ln in lines:
        a, sr = k.create(ln, voice=voice, speed=speed, lang="hi"); a = a.astype(np.float32)
        nz = np.where(np.abs(a) > 0.01)[0]; a = a[nz[0]:nz[-1] + 1] if len(nz) else a  # trim silence
        f = int(0.03 * sr); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
        out.append((a, sr))
    return out


def timeline(spec, vd):
    """vd: dict key->voice duration. Returns events with times."""
    ev = []; t = 0.0; TY = spec.get("typing", 0.75); GAP = spec.get("gap", 0.4)
    h = spec["hook"]; ev.append(dict(kind="hook", t=t, voice_at=0.2, vdur=vd["hook"], end=0.3 + vd["hook"] + 0.3)); t = ev[-1]["end"]
    for i, it in enumerate(spec["items"]):
        if it.get("voice"):
            e = dict(kind="msg", who=it["who"], item=it, t=t, appear=t + TY, voice_at=t + TY + 0.05, vdur=vd[i], end=t + TY + 0.05 + vd[i] + GAP)
        else:
            e = dict(kind="msg", who=it["who"], item=it, t=t, appear=t + 0.3, voice_at=None, vdur=0, end=t + 0.85)
        ev.append(e); t = e["end"]
    e = spec["end"]; ev.append(dict(kind="end", t=t, voice_at=t + 0.4, vdur=vd["end"], end=t + 0.4 + vd["end"] + 0.8)); return ev


def bubble_size(it, d):
    if it.get("stat"): return 900, 560 if it["stat"].get("note") else 500, []
    f = PF(44, "SemiBold"); lines = wrap(it["text"], f, 640); w = max(int(_d.textlength(l, font=f)) for l in lines) + 70
    return min(w, 760), len(lines) * 58 + 56, lines


def build_layout(ev):
    y = 0; items = []
    for e in ev:
        if e["kind"] != "msg": continue
        w, h, lines = bubble_size(e["item"], _d); e.update(w=w, h=h, lines=lines, y=y); y += h + 30; items.append(e)
    return items


def draw_chat(img, d, ev, items, t, total):
    d.rectangle([0, 0, W, H], fill=CREAM)
    CH_TOP, CH_BOT = 430, 1560
    vis = [e for e in items if e["appear"] <= t]
    def bottom(tt): 
        v = [e for e in items if e["appear"] <= tt]; return (v[-1]["y"] + v[-1]["h"]) if v else 0
    typing = [e for e in items if e["who"] == "future" and e["t"] <= t < e["appear"]]
    bt = bottom(t) if not typing else bottom(t) + 90
    tgt = lambda tt: max(0, (bottom(tt) + (90 if any(e["who"] == "future" and e["t"] <= tt < e["appear"] for e in items) else 0)) - (CH_BOT - CH_TOP - 30))
    sc = tgt(t - 0.3) + (tgt(t) - tgt(t - 0.3)) * ease(0.5 + 0.5 * 1) if False else tgt(t)
    layer = Image.new("RGB", (W, CH_BOT - CH_TOP), CREAM); ld = ImageDraw.Draw(layer)
    for e in vis:
        p = ease((t - e["appear"]) / 0.25); y = e["y"] - sc + (1 - p) * 40; w, h = e["w"], e["h"]
        fut = e["who"] == "future"; x0 = M if fut else W - M - w
        bg, fg = (NAVY, CREAM) if fut else (GOLD, INK)
        if p < 1: bg, fg = mixc(CREAM, bg, p), mixc(CREAM, fg, p)
        ld.rounded_rectangle([x0, y + 20, x0 + w, y + 20 + h], radius=36, fill=bg)
        it = e["item"]
        if it.get("stat"):
            s = it["stat"]; cx = x0 + 44
            ld.text((cx, y + 52), s["a_label"], font=PF(28, "SemiBold"), fill=mixc(bg, fg, .75))
            ld.text((cx, y + 92), s["a_value"], font=PF(62), fill=fg)
            ld.line([(cx, y + 190), (x0 + w - 44, y + 190)], fill=mixc(bg, fg, .4), width=2)
            ld.text((cx, y + 212), s["b_label"], font=PF(28, "SemiBold"), fill=mixc(bg, fg, .75))
            q = min(1, max(0, (t - e["voice_at"] - 1.0) / 2.5)); val = int(s["b_to"] * ease(q))
            ld.text((cx, y + 252), s["b_prefix"] + f"{val:,}", font=PF(96), fill=GOLD)
            if s.get("note"): 
                for j, ln in enumerate(wrap(s["note"], PF(26, "SemiBold"), w - 88)): ld.text((cx, y + 392 + j * 34), ln, font=PF(26, "SemiBold"), fill=mixc(bg, fg, .8))
        else:
            for j, ln in enumerate(e["lines"]): ld.text((x0 + 35, y + 20 + 28 + j * 58), ln, font=PF(44, "SemiBold"), fill=fg)
    for e in typing:
        ty = bottom(t) - sc + 20; ld.rounded_rectangle([M, ty + 10, M + 170, ty + 90], radius=36, fill=NAVY)
        for k in range(3): ld.ellipse([M + 38 + k * 42 - 10, ty + 50 - 10 - 9 * max(0, np.sin(t * 9 - k * 0.9)), M + 38 + k * 42 + 10, ty + 50 + 10 - 9 * max(0, np.sin(t * 9 - k * 0.9))], fill=CREAM)
    img.paste(layer, (0, CH_TOP))
    d.rectangle([0, 0, W, 410], fill=NAVY)
    d.ellipse([M, 250, M + 110, 360], fill=GOLD); d.text((M + 55, 305), "F", font=PF(58), fill=NAVY, anchor="mm")
    d.text((M + 140, 262), "Future Aap", font=PF(46), fill=CREAM); d.ellipse([M + 140, 335, M + 158, 353], fill=GREEN)
    d.text((M + 172, 326), "60 saal ke aap  ·  online", font=PF(28, "SemiBold"), fill=(190, 200, 215))
    d.text((W - M, 150), "DDS CAPITAL WEALTH", font=PF(26, "SemiBold"), fill=(190, 200, 215), anchor="ra")


def draw_hook(img, d, spec, e, t):
    d.rectangle([0, 0, W, H], fill=NAVY)
    d.text((W // 2, 520), "abhi", font=PF(36, "SemiBold"), fill=(150, 165, 190), anchor="mm")
    p = ease((t - 0.1) / 0.35); sc = 0.92 + 0.08 * p; ww, hh = int(900 * sc), int(300 * sc); x0 = (W - ww) // 2; y0 = 640 + (1 - p) * 60
    pulse = 1 + 0.015 * np.sin(t * 7)
    d.rounded_rectangle([x0, y0, x0 + ww, y0 + hh], radius=44, fill=CREAM)
    d.ellipse([x0 + 40, y0 + 40, x0 + 130, y0 + 130], fill=GOLD); d.text((x0 + 85, y0 + 85), "F", font=PF(50), fill=NAVY, anchor="mm")
    d.text((x0 + 160, y0 + 40), "Future Aap (60 saal)", font=PF(34), fill=INK); d.text((x0 + ww - 40, y0 + 46), "abhi", font=PF(26, "SemiBold"), fill=GREY if False else (110, 110, 110), anchor="ra")
    for j, ln in enumerate(wrap(spec["hook"]["text"], PF(40, "SemiBold"), ww - 200)[:3]): d.text((x0 + 160, y0 + 100 + j * 52), ln, font=PF(40, "SemiBold"), fill=INK)
    d.ellipse([x0 + ww - 60 - 14 * pulse, y0 - 22 - 14 * pulse, x0 + ww - 60 + 14 * pulse, y0 - 22 + 14 * pulse], fill=CORAL)
    d.text((W // 2, 1180), "1 naya message", font=PF(64), fill=GOLD, anchor="mm")
    d.text((W // 2, 1270), "Sunne ke liye rukiye.", font=PF(36, "SemiBold"), fill=CREAM, anchor="mm")


def draw_end(img, d, spec, e, t):
    p = ease((t - e["t"]) / 0.4); y0 = int(H * (1 - p)); d.rounded_rectangle([0, y0, W, H + 80], radius=60, fill=NAVY)
    if p < 1: return
    f = PF(58); y = y0 + 560
    st = e["t"] + 0.6; words = spec["end"]["text"].split(); n = len(words); span = min(4.5, e["vdur"] * 0.8); x = M; lines = []
    cur = []
    for w in words:
        if _d.textlength(" ".join(cur + [w]), font=f) <= W - 2 * M or not cur: cur.append(w)
        else: lines.append(cur); cur = [w]
    lines.append(cur); wi = 0
    for ln in lines:
        x = M
        for w in ln:
            pp = ease((t - st - span * wi / n) / 0.2); wi += 1; d.text((x, y + (1 - pp) * 30), w, font=f, fill=mixc(NAVY, CREAM, pp)); x += _d.textlength(w + " ", font=f)
        y += 78
    d.rounded_rectangle([M, y + 40, W - M, y + 160], radius=60, fill=GOLD); d.text((W // 2, y + 100), spec["end"].get("button", "SAVE · SHARE · COMMENT"), font=PF(42), fill=NAVY, anchor="mm")


def frame(spec, ev, items, t, total):
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
    hook, end = ev[0], ev[-1]
    if t < hook["end"]: draw_hook(img, d, spec, hook, t)
    else:
        draw_chat(img, d, ev, items, t, total)
        if t >= end["t"]: draw_end(img, d, spec, end, t)
        elif t - hook["end"] < 0.3: 
            p = ease((t - hook["end"]) / 0.3); d.rectangle([0, 0, W, int(H * (1 - p))], fill=NAVY)
    d.rectangle([0, 0, int(W * t / total), 12], fill=GOLD)
    cur = ""; ys = 1700; dark = (t < hook["end"]) or (t >= end["t"] + 0.4)
    fg = (190, 200, 215) if dark else (90, 90, 90)
    if not dark: d.rectangle([0, 1650, W, H], fill=CREAM)
    for w in DISC.split():
        if _d.textlength((cur + " " + w).strip(), font=MONO(20)) > W - 2 * M: d.text((M, ys), cur, font=MONO(20), fill=fg); ys += 27; cur = w
        else: cur = (cur + " " + w).strip()
    d.text((M, ys), cur, font=MONO(20), fill=fg)
    return img


def main(spec_path, prefix, voices):
    spec = json.load(open(spec_path)); work = tempfile.mkdtemp(prefix="chat_"); SR = 24000; results = {}
    keys = ["hook"] + [i for i, it in enumerate(spec["items"]) if it.get("voice")] + ["end"]
    texts = {"hook": spec["hook"]["voice"], "end": spec["end"]["voice"], **{i: spec["items"][i]["voice"] for i in keys if isinstance(i, int)}}
    auds = {}
    for v in voices: auds[v] = dict(zip(keys, tts([texts[k] for k in keys], v, spec.get("speed", 0.92))))
    vd = {k: len(a) / sr for k, (a, sr) in auds[voices[0]].items()}   # timeline from first voice
    for v in voices[1:]:
        for k in keys: vd[k] = max(vd[k], len(auds[v][k][0]) / auds[v][k][1])
    ev = timeline(spec, vd); items = build_layout(ev); total = ev[-1]["end"]
    vid = f"{work}/v.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    for f in range(int(total * FPS)): ff.stdin.write(frame(spec, ev, items, f / FPS, total).tobytes())
    ff.stdin.close(); assert ff.wait() == 0
    starts = {"hook": ev[0]["voice_at"], "end": ev[-1]["voice_at"]}
    for e, k in zip([e for e in ev if e["kind"] == "msg"], range(len(spec["items"]))): 
        if e["voice_at"] is not None: starts[k] = e["voice_at"]
    tt = np.arange(int(total * SR) + SR) / SR
    for v in voices:
        mix = np.zeros(len(tt), np.float32)
        for k in keys:
            a, sr = auds[v][k]; a = np.interp(np.linspace(0, len(a), int(len(a) * SR / sr), endpoint=False), np.arange(len(a)), a).astype(np.float32)
            i = int(starts[k] * SR); mix[i:i + len(a)] += a
        for e in ev:
            if e["kind"] == "msg":
                b = np.arange(int(0.09 * SR)) / SR; i = int(e["appear"] * SR); mix[i:i + len(b)] += (0.12 * np.sin(2 * np.pi * (880 if e["who"] == "future" else 660) * b) * np.exp(-b * 38)).astype(np.float32)
        bed = sum(a * np.sin(2 * np.pi * f * tt) for f, a in ((130.8, .5), (196, .35), (261.6, .3), (329.6, .2))) * 0.035 * np.minimum(1, np.minimum(tt, total - tt) / 1.0)
        env = np.convolve(np.abs(mix) > 0.03, np.ones(SR // 5) / (SR // 5), "same"); mix = np.clip(mix + bed * (1 - 0.6 * np.clip(env, 0, 1)), -1, 1)
        wav = f"{work}/{v}.wav"; sf.write(wav, mix, SR); out = f"{prefix}-{v}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
        print("OK", out, f"{total:.1f}s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "hf_alpha").split(","))
