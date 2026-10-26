"""Kokoro neural TTS helper. Needs kokoro-onnx + soundfile and the model files in $REEL_MODELS (default /tmp/reel_models):
 kokoro-v1.0.onnx, voices-v1.0.bin  (from github.com/thewh1teagle/kokoro-onnx releases, tag model-files-v1.0)
Usage: items = make_voice([("a","text",start_s,end_s), ...], outdir)  -> [(wav_path, start_s), ...]
Each line is sped up (max 1.25x) until it ends before end_s and before the next line starts; raises if it cannot fit."""
import os, soundfile as sf
from kokoro_onnx import Kokoro
M = os.environ.get("REEL_MODELS", "/tmp/reel_models")
VOICE = "bm_george"

def make_voice(lines, outdir):
    k = Kokoro(f"{M}/kokoro-v1.0.onnx", f"{M}/voices-v1.0.bin")
    os.makedirs(outdir, exist_ok=True); items = []; prev_end = 0.0
    for name, text, t0, t1 in lines:
        t0 = max(t0, prev_end + 0.1)
        sp = 1.0
        while True:
            s, sr = k.create(text, voice=VOICE, speed=sp, lang="en-gb")
            end = t0 + len(s) / sr
            if end <= t1 or sp >= 1.25: break
            sp = round(sp + 0.05, 2)
        if end > t1 + 0.05: raise RuntimeError(f"voice line {name} ends {end:.1f}s, window ends {t1}s: shorten the text")
        p = f"{outdir}/{name}.wav"; sf.write(p, s, sr); items.append((p, t0)); prev_end = end
        print(f"{name}: {t0:.1f}-{end:.1f}s speed {sp}")
    return items
