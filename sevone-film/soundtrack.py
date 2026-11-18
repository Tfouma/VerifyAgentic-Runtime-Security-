"""Generates the film soundtrack: dark pad, pulsing bass, risers and cinematic impacts.

Every sound is synthesized, so there are no licensing questions.
Impact times must match IMPACTS in film.html.

    python3 soundtrack.py            # writes soundtrack.wav
"""
import wave
import numpy as np

SR = 44100
DUR = 166.0
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(7)
L = np.zeros(N)
R = np.zeros(N)

IMPACTS = [(0.5, 1), (9, .45), (24, 1), (32, 1.2), (40, .45), (64, .45), (86, .45), (97, 1),
           (108, .45), (113, 1), (134, .5), (152, .8), (158.5, 1.2)]


def env_ar(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def add(sig, start, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * gain * (1 - max(0, pan))
    R[i:i + len(sig)] += sig * gain * (1 + min(0, pan))


def lowpass_fft(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def bandpass_fft(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= ((f > lo) & (f < hi))
    return np.fft.irfft(X, len(x))


def note(m):
    return 440 * 2 ** ((m - 69) / 12)


# ---------- Pad: D minor progression, slow and wide ----------
# Each chord: MIDI notes. Dm, Bb, F, C, repeating; brightens in CONTROL/close.
prog = [[50, 57, 62, 65], [46, 53, 58, 62], [41, 53, 57, 60], [48, 55, 60, 64]]
seg = 8.0
pad = np.zeros(N)
pos = 0.0
k = 0
while pos < DUR:
    chord = prog[k % 4]
    n = int(min(seg + 2, DUR - pos) * SR)
    tt = np.arange(n) / SR
    s = np.zeros(n)
    for m in chord:
        for det in (-0.12, 0.0, 0.11):
            f = note(m + det)
            # few harmonics → soft saw-like tone without filtering cost
            s += np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(4 * np.pi * f * tt) + 0.12 * np.sin(6 * np.pi * f * tt)
    s *= env_ar(n, 2.0, 2.0)
    i = int(pos * SR)
    pad[i:i + n] += s[: N - i]
    pos += seg
    k += 1
pad /= np.abs(pad).max()
# Pad level automation
pad_lvl = np.interp(t, [0, 9, 24, 24.3, 27, 32, 40, 108, 134, 152, 160, 166],
                       [.25, .35, .35, .05, .22, .4, .32, .32, .38, .45, .4, 0])
pad_s = pad * pad_lvl * 0.3
# Slow stereo movement
L += pad_s * (0.85 + 0.15 * np.sin(2 * np.pi * 0.05 * t))
R += pad_s * (0.85 + 0.15 * np.cos(2 * np.pi * 0.05 * t))

# ---------- Sub drone ----------
drone = np.sin(2 * np.pi * note(38) * t) * 0.13 * np.interp(t, [0, 3, 24, 24.3, 30, 160, 166], [0, 1, 1, .3, 1, 1, 0])
L += drone
R += drone

# ---------- Pulse bass: 8th notes at 96 bpm ----------
BPM = 96
step = 60 / BPM / 2
bass_lvl = lambda x: np.interp(x, [9, 23.8, 24, 32, 40, 64, 86, 108, 113, 134, 150, 152, 166],
                                  [.35, .45, 0, 0, .5, .55, .6, .55, .75, .6, .6, 0, 0])
roots = [38, 34, 29, 36]
pt = 9.0
pluck_n = int(step * SR)
tt = np.arange(pluck_n) / SR
while pt < 152:
    lvl = float(bass_lvl(pt))
    if lvl > 0.01:
        root = roots[int((pt) // seg) % 4]
        f = note(root)
        s = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(4 * np.pi * f * tt) + 0.2 * np.sin(6 * np.pi * f * tt))
        s *= np.exp(-tt * 9) * (1 - np.exp(-tt * 400))
        add(s, pt, 0.32 * lvl)
    pt += step

# ---------- Kick on beats during scenes 4–8 ----------
kick_n = int(0.4 * SR)
kt = np.arange(kick_n) / SR
kick = np.sin(2 * np.pi * (45 + 90 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 8)
bt = 40.0
while bt < 152:
    if not (96.6 < bt < 98) and not (112.6 < bt < 114):
        add(kick, bt, 0.34 * (1.25 if 108 <= bt < 125 else 1))
    bt += step * 2

# ---------- Hi-hat ticks (data feel) ----------
hat_n = int(0.05 * SR)
hat = bandpass_fft(rng.standard_normal(hat_n), 6000, 16000) * np.exp(-np.arange(hat_n) / SR * 90)
ht = 40.0 + step
i = 0
while ht < 152:
    if not (96.6 < ht < 98):
        add(hat, ht, 0.10 * (1.2 if i % 2 else .7), pan=(0.4 if i % 2 else -0.4))
    ht += step / 2
    i += 1

# ---------- Data blips in S0/S1 and on feed rows ----------
def blip(f, d=0.08):
    n = int(d * SR)
    x = np.arange(n) / SR
    return np.sin(2 * np.pi * f * x) * np.exp(-x * 40)

for j, tm in enumerate(np.arange(1.8, 3.1, 1.3 / 21)):          # typewriter
    add(blip(1800 + (j % 3) * 200, 0.03), tm, 0.06)
for j in range(8):                                               # agent change feed rows
    add(blip(1320, 0.12), 40 + 3.2 + j * 1.9, 0.16, pan=0.5)
    add(blip(1760, 0.1), 40 + 3.2 + j * 1.9 + 0.06, 0.12, pan=0.5)
for j in range(5):                                               # pre-flight checks
    add(blip(990 if j in (0, 4) else 520, 0.18), 86 + 4.4 + j * 1.2, 0.22)

# ---------- Alarm in REACT ----------
an = int(4.2 * SR)
at = np.arange(an) / SR
alarm = np.sin(2 * np.pi * np.where((at * 2.5) % 1 < .5, 880, 660) * at) * 0.5 * np.exp(-at * 0.5)
add(alarm * env_ar(an, 0.02, 0.8), 113.1, 0.11)
# Resolution chime at rollback (chart s=80 → local 1.6+80*0.0995 ≈ 9.56 → 117.6)
for m, d in ((74, 0), (78, .12), (81, .24)):
    n = int(1.5 * SR)
    x = np.arange(n) / SR
    add(np.sin(2 * np.pi * note(m) * x) * np.exp(-x * 3), 117.6 + d, 0.16)

# ---------- Risers ----------
def riser(d, f0=200, f1=6000):
    n = int(d * SR)
    x = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    # crude rising band via sliding FFT bands in chunks
    out = np.zeros(n)
    chunks = 24
    cs = n // chunks
    for c in range(chunks):
        lo = f0 * (f1 / f0) ** (c / chunks)
        seg_ = noise[c * cs:(c + 1) * cs + 2048]
        out[c * cs:c * cs + len(seg_)] += bandpass_fft(seg_, lo, lo * 2.5) * np.hanning(len(seg_))
    tone = np.sin(2 * np.pi * np.cumsum(np.interp(x, [0, 1], [110, 880])) / SR)
    return (out / (np.abs(out).max() + 1e-9) * 0.8 + 0.25 * tone) * x ** 2.2

add(riser(3.0), 29.0, 0.32)
add(riser(2.0), 111.0, 0.26)
add(riser(3.0), 149.0, 0.30)
add(riser(2.5), 156.0, 0.3)
add(riser(1.6), 95.4, 0.22)

# ---------- Impacts ----------
def impact(w):
    d = 3.5
    n = int(d * SR)
    x = np.arange(n) / SR
    sub = np.sin(2 * np.pi * np.cumsum(30 + 110 * np.exp(-x * 12)) / SR) * np.exp(-x * 1.4)
    body = lowpass_fft(rng.standard_normal(n), 900) * np.exp(-x * 6)
    crack = bandpass_fft(rng.standard_normal(n), 1500, 9000) * np.exp(-x * 30)
    s = 1.0 * sub + 0.9 * body / (np.abs(body).max() + 1e-9) + 0.5 * crack / (np.abs(crack).max() + 1e-9)
    return s * w

for tm, w in IMPACTS:
    add(impact(w), tm, 1.0)

# ---------- Reverb (FFT convolution with decaying noise IR) ----------
def reverb(x, secs=2.6, mix=0.22, seed=1):
    r = np.random.default_rng(seed)
    n = int(secs * SR)
    ir = r.standard_normal(n) * np.exp(-np.arange(n) / SR * 3.2)
    ir = lowpass_fft(ir, 5000)
    ir /= np.sqrt((ir ** 2).sum())
    m = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[: len(x)]
    return x + mix * y

L = reverb(L, seed=1)
R = reverb(R, seed=2)

# ---------- Sidechain-style duck after impacts ----------
duck = np.ones(N)
for tm, w in IMPACTS:
    i = int(tm * SR)
    n = int(1.2 * SR)
    x = np.arange(min(n, N - i)) / SR
    duck[i:i + len(x)] = np.minimum(duck[i:i + len(x)], 1 - 0.25 * w * np.exp(-x * 3))
L *= duck
R *= duck

# Final fade, master, soft clip
fade = np.interp(t, [0, 0.05, 163.5, 166], [0, 1, 1, 0])
L *= fade
R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
L = np.tanh(L / peak * 1.6) / np.tanh(1.6) * 0.95
R = np.tanh(R / peak * 1.6) / np.tanh(1.6) * 0.95

out = (np.stack([L, R], axis=1) * 32767).astype(np.int16)
with wave.open("soundtrack.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(out.tobytes())
print("wrote soundtrack.wav", out.shape[0] / SR, "s")
