"""DDS reel v2: colour, kinetic word-by-word text, Indian (Hindi/Hinglish) voices. Usage:
  python3 -I reels_src/reel_v2.py spec.json out.mp4
spec scenes: {"kind":"hook|say|pain|fix|end","speaker":"Papa|Beta|Dada|DDS","text":"on-screen Hinglish; *word* = highlighted","voice":"spoken line, Devanagari for Hindi","label":"small tag"}
Voices (Kokoro, lang hi): Papa/Dada/DDS = hm_omega, Beta = hf_alpha. Needs kokoro-onnx, soundfile, numpy, pillow, ffmpeg, models in $REEL_MODELS."""
import json, os, re, subprocess, sys, tempfile
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont
W, H = 1080, 1920; FPS = 30; M = 80
NAVY, GOLD, CREAM, CORAL, GREEN, INK = (11, 31, 58), (255, 180, 0), (255, 246, 229), (255, 90, 95), (0, 168, 107), (17, 24, 39)
THEME = {"hook": (NAVY, CREAM, GOLD), "say_a": (CREAM, INK, CORAL), "say_b": (GOLD, INK, NAVY), "pain": (CORAL, CREAM, NAVY),
         "fix": (GREEN, CREAM, GOLD), "end": (NAVY, CREAM, GOLD)}
CHIP = {"Papa": NAVY, "Beta": CORAL, "Dada": GREEN, "DDS": NAVY}
VOICE = {"Beta": "hf_alpha"}; DEFAULT_VOICE = "hm_omega"
P = "/usr/share/fonts/truetype/google-fonts/"; PF = lambda s, w="Bold": ImageFont.truetype(f"{P}Poppins-{"Medium" if w=="SemiBold" else w}.ttf", s)
MONO = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/ibm-plex/IBMPlexMono-Regular.ttf", s)
DISC = "AMFI Registered Mutual Fund Distributor (ARN-359084). Mutual fund investments are subject to market risks; read all scheme related documents carefully. Educational content, not advice or a recommendation."
mix_c = lambda a, b, p: tuple(int(a[i] + (b[i] - a[i]) * p) for i in range(3))
ease = lambda p: 1 - (1 - min(max(p, 0), 1)) ** 3


def theme(s, i):
    k = s["kind"]
    return THEME["say_a" if i % 2 else "say_b"] if k == "say" else THEME[k]


def layout(text, font, width, d):
    toks = re.findall(r"\*[^*]+\*\S*|\S+", text); words = [(t.replace("*",""), t.startswith("*")) for t in toks]
    lines, cur = [], []
    for w in words:
        t = " ".join(x[0] for x in cur + [w])
        if d.textlength(t, font=font) <= width or not cur: cur.append(w)
        else: lines.append(cur); cur = [w]
    lines.append(cur); return lines


def draw_scene(img, d, s, i, n, t, dur, vdur, gt, total):
    bg, fg, ac = theme(s, i); p_in = ease(t / 0.28)
    y0 = int(H * (1 - p_in)); d.rectangle([0, y0, W, H], fill=bg)
    if p_in < 1: return
    k = s["kind"]; big = k in ("hook", "pain", "fix", "end"); font = PF(88 if k == "hook" else 74 if big else 64, "Bold" if big else "SemiBold")
    lines = layout(s["text"], font, W - 2 * M, d); lh = int(font.size * 1.28)
    top = 840 - len(lines) * lh // 2 + (60 if k == "say" else 0)
    nwords = sum(len(l) for l in lines); span = s.get("reveal") or min(max(0.6, vdur * 0.8), 4.2); wi = 0
    for ln in lines:
        x = M
        for (w, hl) in ln:
            ts = 0.3 + span * wi / max(1, nwords); p = ease((t - ts) / 0.22); wi += 1
            col = mix_c(bg, ac if hl else fg, p); d.text((x, top + (1 - p) * 36), w, font=font, fill=col)
            x += d.textlength(w + " ", font=font)
        top += lh
    if k == "say":
        sp = s.get("speaker", ""); cc = CHIP.get(sp, NAVY); bob = 6 * abs(np.sin(t * 9)) if 0.3 < t < vdur + 0.3 else 0
        cx, cy = M + 62, 560 - bob; d.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], fill=cc)
        d.text((cx, cy), sp[:1], font=PF(64), fill=CREAM, anchor="mm"); d.text((cx + 90, cy - 24), sp.upper(), font=PF(34), fill=fg)
    if s.get("label"):
        d.text((M, 440), s["label"].upper(), font=PF(30, "SemiBold"), fill=ac)
    if k == "end":
        d.rounded_rectangle([M, top + 40, W - M, top + 150], radius=55, fill=GOLD)
        d.text((W // 2, top + 95), "SAVE  ·  SHARE  ·  COMMENT", font=PF(40), fill=NAVY, anchor="mm")


def render_frame(sc, times, t, total, vd):
    img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
    i = max(j for j, a in enumerate(times) if a <= t or j == 0); s = sc[i]
    if i > 0 and t - times[i] < 0.28:  # previous scene stays underneath during the slide
        pb, pf, pa = theme(sc[i - 1], i - 1); d.rectangle([0, 0, W, H], fill=pb)
    draw_scene(img, d, s, i, len(sc), t - times[i], 0, vd[i], t, total)
    bg, fg, ac = theme(s, i)
    d.text((M, 150), "DDS CAPITAL WEALTH", font=PF(30, "SemiBold"), fill=fg)
    d.rectangle([0, 0, int(W * t / total), 12], fill=GOLD if bg != GOLD else NAVY)
    yy = 1660
    for ln in layout(DISC, MONO(17), W - 2 * M, d) if False else []: pass
    words = DISC.split(); cur = ""; ys = 1700
    for w in words:
        if d.textlength((cur + " " + w).strip(), font=MONO(20)) > W - 2 * M: d.text((M, ys), cur, font=MONO(20), fill=mix_c(bg, fg, .88)); ys += 27; cur = w
        else: cur = (cur + " " + w).strip()
    d.text((M, ys), cur, font=MONO(20), fill=mix_c(bg, fg, .88))
    return img


def main(spec_path, out):
    from kokoro_onnx import Kokoro
    sc = json.load(open(spec_path))["scenes"]; work = tempfile.mkdtemp(prefix="reel2_"); M_DIR = os.environ.get("REEL_MODELS", "/tmp/reel_models")
    k = Kokoro(f"{M_DIR}/kokoro-v1.0.onnx", f"{M_DIR}/voices-v1.0.bin"); aud = []
    for s in sc:
        a, sr = k.create(s.get("voice", s["text"]), voice=VOICE.get(s.get("speaker"), DEFAULT_VOICE), speed=1.0, lang="hi"); aud.append((a, sr))
    vd = [len(a) / sr for a, sr in aud]; gap = 0.45; times = []; t = 0.0
    for j, s in enumerate(sc):
        times.append(t); t += 0.3 + vd[j] + gap + (0.9 if s["kind"] == "end" else 0)
    total = t; SR = 24000; mix = np.zeros(int(total * SR) + SR, np.float32)
    for (a, sr), t0 in zip(aud, times):
        a = np.interp(np.linspace(0, len(a), int(len(a) * SR / sr), endpoint=False), np.arange(len(a)), a).astype(np.float32)
        st = int((t0 + 0.3) * SR); mix[st:st + len(a)] += a
        tt = np.arange(int(0.12 * SR)) / SR; mix[int(t0 * SR):int(t0 * SR) + len(tt)] += (0.18 * np.sin(2 * np.pi * 660 * tt) * np.exp(-tt * 30)).astype(np.float32)
    tt = np.arange(len(mix)) / SR; bed = sum(a * np.sin(2 * np.pi * f * tt) for f, a in ((130.8, .5), (196, .35), (261.6, .3), (329.6, .2)))
    bed = bed * 0.04 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.5 * tt)) * np.minimum(1, np.minimum(tt, total - tt) / 1.0)
    env = np.convolve(np.abs(mix) > 0.03, np.ones(SR // 5) / (SR // 5), "same"); mix = np.clip(mix + bed * (1 - 0.55 * np.clip(env, 0, 1)), -1, 1)
    wav = f"{work}/m.wav"; sf.write(wav, mix, SR)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                           "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for f in range(int(total * FPS)): ff.stdin.write(render_frame(sc, times, f / FPS, total, vd).tobytes())
    ff.stdin.close(); assert ff.wait() == 0
    print("OK", out, f"{total:.1f}s", "scene starts", [round(x, 1) for x in times])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
