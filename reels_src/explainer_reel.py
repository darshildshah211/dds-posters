"""Spec-driven voiceover reel (1080x1920): family dialogue / explainer. Usage:
  python3 -I reels_src/explainer_reel.py spec.json out.mp4
spec = {"title":..., "scenes":[{"kind":"hook|say|point|end","speaker":"Papa|Beta|Dada|DDS","text":"on-screen text","voice":"spoken line (optional, defaults to text)","label":"small tag"}]}
Voices: Papa/Dada/DDS = bm_george, Beta = af_heart (Kokoro). Needs kokoro-onnx, soundfile, numpy, pillow, ffmpeg, models in $REEL_MODELS.
Every scene: still card + slow zoom + fade; music bed is a soft synthesised pad; voice ducks it. Disclaimer sits on every frame."""
import json, os, subprocess, sys, tempfile
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ig_gen as g

M_DIR = os.environ.get("REEL_MODELS", "/tmp/reel_models")
VOICES = {"Beta": "af_heart"}; DEFAULT_VOICE = "bm_george"
W, H = 1080, 1920


def card(scene, idx, n, path):
    kind = scene["kind"]; dark = kind in ("hook", "end") or (kind == "say" and idx % 2 == 0)
    bg, fg = (g.BLACK, g.WHITE) if dark else (g.WHITE, g.BLACK)
    sub = (170, 170, 170) if dark else g.GREY
    img = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(img)
    g.tracked(d, (g.M, 280), "DDS CAPITAL WEALTH", g.MM(24), fg)
    g.tracked(d, (W - g.M - 120, 282), f"{idx + 1:02d}/{n:02d}", g.MM(22), sub)
    d.line([(g.M, 322), (W - g.M, 322)], fill=fg, width=2)
    text = scene["text"]
    if kind == "hook":
        f = g.SB(84); lines = g.wrap(d, text, f, W - 2 * g.M); y = 760 - len(lines) * 55
        for ln in lines: d.text((g.M, y), ln, font=f, fill=fg); y += 110
    elif kind == "say":
        sp = scene.get("speaker", "")
        g.tracked(d, (g.M, 640), sp.upper(), g.MM(34), sub, tr=6)
        d.text((g.M - 6, 640), "", font=g.SB(10), fill=fg)
        f = g.SI(68); lines = g.wrap(d, text, f, W - 2 * g.M); y = 720
        for ln in lines: d.text((g.M, y), ln, font=f, fill=fg); y += 94
    elif kind == "point":
        g.tracked(d, (g.M, 560), scene.get("label", "REMEMBER").upper(), g.MM(30), sub, tr=6)
        f = g.SB(64); lines = g.wrap(d, text, f, W - 2 * g.M); y = 640
        for ln in lines: d.text((g.M, y), ln, font=f, fill=fg); y += 88
        d.line([(g.M, y + 20), (g.M + 110, y + 20)], fill=fg, width=6)
    else:  # end
        f = g.SI(64); lines = g.wrap(d, text, f, W - 2 * g.M); y = 700
        for ln in lines: d.text((g.M, y), ln, font=f, fill=fg); y += 90
        d.text((g.M, y + 50), "To know more, contact us.", font=g.SS(40), fill=fg)
    g.footer(d, W, 1600, fg=fg, sub=sub)
    img.save(path)


def voice(spec, work):
    from kokoro_onnx import Kokoro
    k = Kokoro(f"{M_DIR}/kokoro-v1.0.onnx", f"{M_DIR}/voices-v1.0.bin"); out = []
    for i, s in enumerate(spec["scenes"]):
        v = VOICES.get(s.get("speaker"), DEFAULT_VOICE)
        a, sr = k.create(s.get("voice", s["text"]), voice=v, speed=0.95, lang="en-gb")
        p = f"{work}/v{i}.wav"; sf.write(p, a, sr); out.append((p, len(a) / sr))
    return out


def pad(dur, sr=44100):
    t = np.arange(int(dur * sr)) / sr; x = 0
    for f, a in ((110, .5), (165, .3), (220.5, .25), (277, .15)):
        x = x + a * np.sin(2 * np.pi * f * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t + f))
    x *= 0.05 * np.minimum(1, np.minimum(t, dur - t) / 1.5)
    return np.stack([x, x], 1).astype(np.float32), sr


def main(spec_path, out):
    spec = json.load(open(spec_path)); sc = spec["scenes"]; n = len(sc)
    work = tempfile.mkdtemp(prefix="reel_"); vs = voice(spec, work); clips = []; durs = []
    for i, s in enumerate(sc):
        dur = vs[i][1] + 0.9 + (0.8 if s["kind"] == "end" else 0); durs.append(dur)
        png = f"{work}/c{i}.png"; card(s, i, n, png); mp = f"{work}/c{i}.mp4"; fr = int(dur * 30)
        vf = (f"scale=2160:-1,zoompan=z='1+0.0006*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={fr}:s={W}x{H}:fps=30,"
              f"fade=t=in:st=0:d=0.25,fade=t=out:st={dur - 0.25:.2f}:d=0.25,format=yuv420p")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", png, "-vf", vf, "-t", f"{dur:.2f}",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", mp], check=True); clips.append(mp)
    total = sum(durs); sr = 24000
    vox = np.zeros(int(total * sr) + sr, dtype=np.float32); t0 = 0.3
    for (p, _), dur in zip(vs, durs):
        a, r = sf.read(p, dtype="float32")
        if r != sr:
            a = np.interp(np.linspace(0, len(a), int(len(a) * sr / r), endpoint=False), np.arange(len(a)), a).astype(np.float32)
        vox[int(t0 * sr):int(t0 * sr) + len(a)] += a; t0 += dur
    bed, _ = pad(total, sr); bed = bed[:, 0]; env = np.convolve(np.abs(vox[:len(bed)]) > 0.02, np.ones(sr // 4) / (sr // 4), "same")
    mix = vox[:len(bed)] * 0.95 + bed * (1 - 0.6 * np.clip(env, 0, 1)) * 3
    wav = f"{work}/mix.wav"; sf.write(wav, np.clip(mix, -1, 1), sr)
    lst = f"{work}/l.txt"; open(lst, "w").write("".join(f"file '{c}'\n" for c in clips))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    print("OK", out, f"{total:.1f}s", "cards in", work)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
