# -*- coding: utf-8 -*-
"""Instrument synthesis with numpy/scipy (mono float32 arrays at SR)."""
import numpy as np
from scipy import signal

SR = 44100
_rng = np.random.default_rng(7)


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def env_adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    s_n = max(0, n - a_n - d_n - r_n)
    e = np.concatenate([np.linspace(0, 1, max(a_n, 1)), np.linspace(1, s, max(d_n, 1)),
                        np.full(s_n, s), np.linspace(s, 0, max(r_n, 1))])
    if len(e) < n:
        e = np.pad(e, (0, n - len(e)))
    return e[:n]


def env_exp(n, decay):
    return np.exp(-np.arange(n) / (decay * SR))


def noise(n, seed=None):
    r = np.random.default_rng(seed) if seed is not None else _rng
    return r.standard_normal(n)


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo / (SR / 2), min(hi / (SR / 2), 0.99)], "band", output="sos")
    return signal.sosfilt(sos, x)


def lp(x, f, order=2):
    sos = signal.butter(order, min(f / (SR / 2), 0.99), "low", output="sos")
    return signal.sosfilt(sos, x)


def hp(x, f, order=2):
    sos = signal.butter(order, f / (SR / 2), "high", output="sos")
    return signal.sosfilt(sos, x)


def saw(f, t, phase=0.0):
    return 2 * ((f * t + phase) % 1.0) - 1


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


# ------------------------------------------------------------------ percussion
def taiko(f=55, dur=1.2, hit=1.0, seed=None):
    n = int(dur * SR)
    t = np.arange(n) / SR
    fr = f * (1 + 1.2 * np.exp(-t * 30))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    body = np.sin(ph) * np.exp(-t * 4.0)
    skin = bp(noise(n, seed), 80, 900) * np.exp(-t * 25) * 0.6
    x = (body + skin) * hit
    return np.tanh(x * 1.6) * 0.8


def frame_drum(kind="doum", dur=0.5, seed=None):
    n = int(dur * SR)
    t = np.arange(n) / SR
    if kind == "doum":
        fr = 95 * (1 + 0.6 * np.exp(-t * 40))
        x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 9)
        x += bp(noise(n, seed), 100, 600) * np.exp(-t * 30) * 0.3
    else:  # tek / ka
        x = bp(noise(n, seed), 1800, 6000) * np.exp(-t * 60) * 0.9
        x += np.sin(2 * np.pi * 420 * t) * np.exp(-t * 50) * 0.4
    return x * 0.8


def snare(dur=0.35, seed=None):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bp(noise(n, seed), 1200, 7000) * np.exp(-t * 22)
    x += np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.5
    return x * 0.6


def cymbal(dur=2.5, seed=None):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return hp(noise(n, seed), 5000) * np.exp(-t * 1.6) * 0.4


# ------------------------------------------------------------------ tonal
def pluck(f, dur=1.2, bright=0.5, decay=0.996, seed=None):
    """Karplus-Strong string (lyre / oud)."""
    n = int(dur * SR)
    N = max(2, int(SR / f))
    exc = noise(N, seed)
    exc = lp(exc, 1500 + 6000 * bright) if bright < 0.95 else exc
    x = np.zeros(n)
    x[:N] = exc
    a = np.zeros(N + 2)
    a[0] = 1.0
    a[N] = -0.5 * decay
    a[N + 1] = -0.5 * decay
    y = signal.lfilter([1.0], a, x)
    y *= env_adsr(n, 0.002, 0.05, 1.0, min(0.15, dur * 0.3))
    return y / (np.max(np.abs(y)) + 1e-9) * 0.7


def pad(freqs, dur, cutoff=1800, detune=0.006, attack=0.8, release=1.2, voices=3):
    t = t_axis(dur)
    x = np.zeros(len(t))
    for f in freqs:
        for v in range(voices):
            d = 1 + detune * (v - (voices - 1) / 2)
            x += saw(f * d, t, phase=_rng.random())
    x = lp(x, cutoff, 2)
    x *= env_adsr(len(t), attack, 0.3, 0.85, release)
    return x / (len(freqs) * voices) * 0.9


def brass(f, dur, vib=5.0, bright=1.0):
    t = t_axis(dur)
    fm = f * (1 + 0.004 * np.sin(2 * np.pi * vib * t) * np.clip(t * 2, 0, 1))
    ph = np.cumsum(fm) / SR
    x = 2 * (ph % 1.0) - 1
    x += 0.6 * (2 * ((ph * 1.003) % 1.0) - 1)
    env = env_adsr(len(t), 0.06, 0.15, 0.8, min(0.25, dur * 0.3))
    # filter opens with envelope (blocks)
    out = np.zeros_like(x)
    blk = 1024
    zi = None
    for i in range(0, len(x), blk):
        c = 400 + 3500 * bright * env[i]
        b, a = signal.butter(2, min(c / (SR / 2), 0.99))
        if zi is None:
            zi = signal.lfilter_zi(b, a) * 0
        out[i:i + blk], zi = signal.lfilter(b, a, x[i:i + blk], zi=zi)
    return out * env * 0.5


def choir(f, dur, vowel="a", voices=4, vib=5.2):
    formants = {"a": [(800, 80), (1150, 90), (2900, 120)], "o": [(450, 70), (800, 80), (2830, 100)],
                "u": [(325, 50), (700, 60), (2530, 100)], "e": [(400, 60), (1600, 80), (2700, 120)]}[vowel]
    t = t_axis(dur)
    src = np.zeros(len(t))
    for v in range(voices):
        d = 1 + 0.008 * (v - voices / 2)
        fm = f * d * (1 + 0.006 * np.sin(2 * np.pi * (vib + v * 0.3) * t + v))
        ph = np.cumsum(fm) / SR
        src += 2 * (ph % 1.0) - 1
    out = np.zeros(len(t))
    for fc, bw in formants:
        out += bp(src, fc - bw, fc + bw, 2) * (1.0 if fc < 1000 else 0.6)
    out += 0.03 * bp(noise(len(t)), 1000, 4000)
    out *= env_adsr(len(t), min(0.4, dur * 0.3), 0.2, 0.9, min(0.6, dur * 0.4))
    return out / voices * 2.2


def ney(f, dur, vib=5.5, breath=0.25):
    t = t_axis(dur)
    fm = f * (1 + 0.007 * np.sin(2 * np.pi * vib * t) * np.clip(t * 1.5, 0, 1))
    ph = 2 * np.pi * np.cumsum(fm) / SR
    x = np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph)
    x += breath * bp(noise(len(t)), f * 0.8, f * 3.5)
    x *= env_adsr(len(t), 0.08, 0.1, 0.85, min(0.25, dur * 0.3))
    return x * 0.45


def strings(f, dur, attack=0.02, release=0.08, cutoff=2400):
    t = t_axis(dur)
    x = saw(f, t) + saw(f * 1.004, t, 0.3) + 0.5 * saw(f * 0.5, t)
    x = lp(x, cutoff)
    return x * env_adsr(len(t), attack, 0.05, 0.8, release) * 0.3


def bass_note(f, dur, cutoff=500):
    t = t_axis(dur)
    x = saw(f, t) + np.sin(2 * np.pi * f * t)
    x = lp(x, cutoff)
    return x * env_adsr(len(t), 0.005, 0.1, 0.6, 0.06) * 0.6


def bell(f, dur=2.0):
    t = t_axis(dur)
    x = np.zeros(len(t))
    for k, a, d in ((1, 1, 1.5), (2.76, 0.5, 0.8), (5.4, 0.25, 0.4), (8.9, 0.12, 0.2)):
        x += a * np.sin(2 * np.pi * f * k * t) * np.exp(-t / d)
    return x * 0.3


# ------------------------------------------------------------------ fx helpers
def reverb_ir(dur=2.2, decay=2.5, seed=3, damp=6000):
    n = int(dur * SR)
    t = np.arange(n) / SR
    ir = noise(n, seed) * np.exp(-t * decay)
    ir = lp(ir, damp)
    ir[0] = 1.0
    return ir / np.sqrt(np.sum(ir ** 2))


def reverb(x, wet=0.25, dur=2.2, decay=2.5, seed=3):
    ir = reverb_ir(dur, decay, seed)
    y = signal.fftconvolve(x, ir)[:len(x)]
    return x * (1 - wet) + y * wet


def place(buf, x, start, gain=1.0, pan=0.0):
    """Add mono x into stereo buf (2, N) at sample `start` with equal-power pan."""
    s = int(start)
    if s >= buf.shape[1] or len(x) == 0:
        return
    if s < 0:
        x = x[-s:]
        s = 0
    e = min(buf.shape[1], s + len(x))
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    buf[0, s:e] += x[:e - s] * gain * l
    buf[1, s:e] += x[:e - s] * gain * r
