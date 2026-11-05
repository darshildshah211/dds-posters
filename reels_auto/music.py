"""Original, royalty-free music bed for the reel (synthesised, no samples)."""
import numpy as np, wave

SR = 44100
DUR = 28.2
BPM = 128
B = 60 / BPM
N = int(SR * DUR)
L = np.zeros(N); Rr = np.zeros(N)
rng = np.random.default_rng(3)

def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N: return
    s = sig[: j - i] * gain
    L[i:j] += s * (1 - pan) ** 0.5 if pan > 0 else s
    Rr[i:j] += s * (1 + pan) ** 0.5 if pan < 0 else s

def env(n, a=0.005, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)

from scipy.signal import lfilter
def lp(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR); return lfilter([1 - a], [1, -a], x)
def _lp_old(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR); y = np.zeros_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a) * x[i] + a * s; y[i] = s
    return y

def hp(x): return np.diff(np.concatenate([[0], x]))

def kick(big=False):
    n = int(SR * (0.6 if big else 0.35)); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.35 if big else 0.16) * 1.1

def hat(open_=False):
    n = int(SR * (0.18 if open_ else 0.05))
    return hp(hp(rng.standard_normal(n))) * env(n, 0.001, 0.06 if open_ else 0.015) * 0.18

def clap():
    n = int(SR * 0.25); x = hp(rng.standard_normal(n)) * 0.5
    e = env(n, 0.001, 0.08)
    for k in (0.0, 0.011, 0.022): e[int(k*SR):int(k*SR)+60] += 0.6
    return lp(x * e, 3500) * 1.4

def tick():
    n = int(SR * 0.03); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 3200 * t) * env(n, 0.0005, 0.006) * 0.35

def saw(freq, dur, cutoff=1800, det=0.006):
    n = int(SR * dur); t = np.arange(n) / SR; s = 0
    for d in (-det, 0, det): s = s + 2 * ((t * freq * (1 + d)) % 1) - 1
    return lp(s / 3, cutoff)

def sub(freq, dur):
    n = int(SR * dur); t = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * t) * env(n, 0.005, dur * 0.8)

def note(m): return 440 * 2 ** ((m - 69) / 12)

def boom():
    n = int(SR * 2.2); t = np.arange(n) / SR
    f = 30 + 80 * np.exp(-t * 6)
    low = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.9)
    noise = lp(rng.standard_normal(n), 900) * env(n, 0.001, 0.5) * 0.6
    return (low + noise) * 0.9

def riser(dur):
    n = int(SR * dur); t = np.arange(n) / SR
    x = hp(rng.standard_normal(n)) * (t / dur) ** 2
    sweep = np.sin(2 * np.pi * np.cumsum(200 + 1800 * (t / dur) ** 2) / SR) * (t / dur) ** 2 * 0.15
    return x * 0.25 + sweep

def pad(midis, t0, dur, cutoff=1200, g=0.12):
    n = int(SR * dur); e = np.minimum(1, np.arange(n) / (SR * 0.8)) * np.minimum(1, (n - np.arange(n)) / (SR * 0.8))
    for m in midis: add(saw(note(m), dur, cutoff, 0.01) * e, t0, g, pan=0.0)

# ---------- arrangement ----------
# Intro 0-3: dark pad + clock ticks
pad([45, 52, 57, 60], 0.0, 3.4, 900, 0.10)
for k in range(int(3.0 / (B / 2))): add(tick(), k * B / 2, 1.0 if k % 2 == 0 else 0.5)

# Decay section 3.0-14.4: driving minor groove (A minor, descending bass)
bass_line = [45, 45, 43, 43, 41, 41, 40, 40]
t = 3.0; bar = 0
while t < 14.4 - 1e-6:
    for beat in range(4):
        tb = t + beat * B
        if tb >= 14.4: break
        add(kick(), tb, 0.95)
        add(hat(), tb + B / 2, 1.0); add(hat(), tb + B / 4, 0.4); add(hat(), tb + 3 * B / 4, 0.4)
        if beat in (1, 3): add(clap(), tb, 0.8)
        add(tick(), tb, 0.5)
        m = bass_line[(bar * 2 + beat // 2) % len(bass_line)]
        add(sub(note(m), B * 0.9), tb, 0.55)
        add(saw(note(m + 12), B * 0.45, 700), tb + B / 2, 0.09)
    # stab chords on bar start
    for m in (57, 60, 64): add(saw(note(m), B * 0.3, 2400) * env(int(SR * B * 0.3), 0.003, 0.12), t, 0.08)
    t += 4 * B; bar += 1
add(riser(2.0), 12.4, 0.9)

# DROP 14.4: bulls - bright major (C major / G), double-time energy
add(boom(), 14.4, 1.0)
t = 14.4
maj = [[60, 64, 67, 72], [55, 59, 62, 67], [57, 60, 64, 69], [53, 57, 60, 65]]
bass_maj = [36, 43, 45, 41]
i = 0
while t < 17.6 - 1e-6:
    for beat in range(4):
        tb = t + beat * B
        if tb >= 17.6: break
        add(kick(), tb, 1.0); add(hat(True), tb + B / 2, 1.0); add(hat(), tb + B / 4, 0.5); add(hat(), tb + 3 * B / 4, 0.5)
        if beat in (1, 3): add(clap(), tb, 0.9)
        add(sub(note(bass_maj[i % 4]), B * 0.9), tb, 0.6)
        for m in maj[i % 4]: add(saw(note(m), B * 0.35, 3200) * env(int(SR * B * 0.35), 0.002, 0.1), tb + B / 2, 0.06)
    # bright arpeggio
    for k in range(8):
        add(saw(note(maj[i % 4][k % 4] + 12), B / 2 * 0.8, 4000) * env(int(SR * B / 2 * 0.8), 0.001, 0.08), t + k * B / 2, 0.05, pan=0.3 if k % 2 else -0.3)
    t += 4 * B; i += 1

# Reveal 17.6: impact + sustained
add(boom(), 17.65, 0.9)
pad([57, 60, 64, 69], 17.6, 4.0, 1600, 0.09)
t = 17.6
while t < 21.4:
    add(kick(), t, 0.7); add(hat(), t + B / 2, 0.8)
    if int(round((t - 17.6) / B)) % 2 == 1: add(clap(), t, 0.6)
    t += B

# Lines 21.4-24.6: half-time, clock ticks return
pad([53, 57, 60, 64], 21.4, 3.4, 1000, 0.10)
t = 21.4; k = 0
while t < 24.6:
    if k % 4 == 0: add(kick(), t, 0.8)
    if k % 4 == 2: add(clap(), t, 0.6)
    add(tick(), t, 0.7); t += B / 2; k += 1

# End 24.8: resolve
add(boom(), 24.8, 0.7)
pad([48, 55, 60, 64, 67], 24.8, 3.4, 1400, 0.10)

# ---------- master ----------
def reverb(x):
    y = x.copy()
    for d, g in ((0.031, .35), (0.047, .3), (0.071, .25), (0.113, .2), (0.163, .15)):
        k = int(d * SR); y[k:] += x[:-k] * g
    return y
L2, R2 = reverb(L), reverb(Rr)
fade = np.ones(N); fn = int(SR * 1.2); fade[-fn:] = np.linspace(1, 0, fn)
fi = int(SR * 0.3); fade[:fi] = np.linspace(0, 1, fi)
st = np.stack([L2, R2], 1) * fade[:, None]
st = np.tanh(st / np.max(np.abs(st)) * 1.6) * 0.89
import sys
with wave.open(sys.argv[1] if len(sys.argv) > 1 else "music.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print("ok")
