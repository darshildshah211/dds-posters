# DDS Capital reel engine (illustrated explainer films, 1080x1920, music + British male voiceover)

Setup (cloud): `pip install pycairo pillow numpy soundfile kokoro-onnx --break-system-packages`; download from
github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/ the files kokoro-v1.0.onnx and voices-v1.0.bin into /tmp/reel_models.
Fonts: /usr/share/fonts/truetype/google-fonts (Lora, Poppins). Set REEL_WORK=/tmp/reel_work for scratch output.

- engine.py     : drawing kit (cairo): person() characters, item icons, backgrounds, scene functions of reel #1 (family story), music generator make_audio().
                  Reel #1 render: `python3 -I engine.py render out.mp4` (video+music); audio mixing with voice via mix.py.
- data_story.py : reel #2 template "Nifty falls and what came next": data check (two sources), hook / line chart / cards / family takeaway / end card.
                  Copy it and change DATA, CAPS2, scene timings for a new data story. `python3 -I data_story.py prev t1 t2 ...` writes preview PNGs;
                  `python3 -I data_story.py audio` writes the music bed; `python3 -I data_story.py render video.mp4` renders silent video.
- voice.py      : make_voice(lines, outdir) -> list for mix.py
- mix.py        : mix(music_wav, [(voice_wav, start_s)], out_wav, dur) ducks the music under the voice.
Final: ffmpeg -i video.mp4 -i mixed.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest out.mp4
Always view preview frames (PNG) for clipped or overlapping text before rendering the full video.
Logo: the end-card "D" circle is a placeholder; replace with the owner's logo when provided.
