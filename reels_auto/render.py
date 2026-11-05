"""Render the decay reel from reels_auto/out/data.json -> MP4 with music.

python3 reels_auto/render.py OUT.mp4            full reel
python3 reels_auto/render.py --stills 5 16 20   review frames into reels_auto/out/
"""
import asyncio, json, os, subprocess, sys
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FPS = 30
TOTAL = 28.2
SEGMENTS = [(0, 10), (10, 19), (19, TOTAL)]


async def page_with_data(p):
    b = await p.chromium.launch()
    pg = await b.new_page(viewport={"width": 1080, "height": 1920})
    data = json.load(open(os.path.join(OUT, "data.json")))
    await pg.add_init_script("window.DATA=" + json.dumps(data) + ";")
    await pg.goto("file://" + os.path.join(HERE, "template.html"))
    await pg.evaluate("document.fonts.ready")
    await pg.wait_for_timeout(300)
    return b, pg


async def segment(p, a, z, out):
    b, pg = await page_with_data(p)
    tmp = out[:-4] + ".part.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
                           "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                           "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    for n in range(round(a * FPS), round(z * FPS)):
        await pg.evaluate(f"renderFrame({n / FPS})")
        ff.stdin.write(await pg.screenshot(type="jpeg", quality=92))
    ff.stdin.close()
    if ff.wait() != 0:
        raise RuntimeError("ffmpeg failed on segment " + out)
    os.replace(tmp, out)
    await b.close()


async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        if sys.argv[1] == "--stills":
            b, pg = await page_with_data(p)
            for t in sys.argv[2:]:
                await pg.evaluate(f"renderFrame({float(t)})")
                await pg.screenshot(path=os.path.join(OUT, f"still_{float(t):05.2f}.jpg"), type="jpeg", quality=88)
            await b.close()
            return
        final = sys.argv[1]
        segs = [os.path.join(OUT, f"seg{i}.mp4") for i in range(len(SEGMENTS))]
        await asyncio.gather(*(segment(p, a, z, f) for (a, z), f in zip(SEGMENTS, segs)))
    lst = os.path.join(OUT, "list.txt")
    open(lst, "w").write("".join(f"file '{f}'\n" for f in segs))
    silent = os.path.join(OUT, "video.mp4")
    music = os.path.join(OUT, "music.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)
    subprocess.run([sys.executable, os.path.join(HERE, "music.py"), music], check=True)
    tmp = final[:-4] + ".part.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", music, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, final)
    print("REEL:", final)


asyncio.run(main())
