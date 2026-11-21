# -*- coding: utf-8 -*-
"""Procedural sound effects. sfx(name, variant) -> mono float array."""
import numpy as np

from .synth import (SR, bell, bp, brass, choir, env_adsr, frame_drum, hp, lp, midi, noise, pad,
                    pluck, reverb, saw, snare, taiko)


def add(*xs):
    n = max(len(x) for x in xs)
    out = np.zeros(n)
    for x in xs:
        out[:len(x)] += x
    return out


def T(d):
    return np.arange(int(d * SR)) / SR


def ex(n, d):
    return np.exp(-np.arange(n) / (d * SR))


def cat(*parts, gap=0.0):
    g = np.zeros(int(gap * SR))
    out = []
    for p in parts:
        out += [p, g]
    return np.concatenate(out)


def mixat(length, items):
    out = np.zeros(int(length * SR))
    for t0, x, g in items:
        s = int(t0 * SR)
        e = min(len(out), s + len(x))
        if s < len(out):
            out[s:e] += x[:e - s] * g
    return out


def vox(f0, dur, vowel="a", rough=0.0, seed=0):
    """Formant voice. f0: float or (start, end)."""
    t = T(dur)
    if isinstance(f0, tuple):
        f = np.linspace(f0[0], f0[1], len(t))
    else:
        f = np.full(len(t), f0)
    f = f * (1 + 0.01 * np.sin(2 * np.pi * 5 * t))
    ph = np.cumsum(f) / SR
    src = 2 * (ph % 1.0) - 1
    if rough:
        src *= 1 + rough * noise(len(t), seed) * 0.5
    form = {"a": [(800, 1.0), (1200, 0.6), (2700, 0.3)], "o": [(500, 1.0), (850, 0.6), (2700, 0.2)],
            "u": [(330, 1.0), (700, 0.4), (2500, 0.15)], "e": [(450, 1.0), (1900, 0.6), (2600, 0.3)],
            "i": [(300, 1.0), (2300, 0.6), (3000, 0.3)]}[vowel]
    y = sum(bp(src, fc * 0.88, fc * 1.12) * a for fc, a in form)
    return y * env_adsr(len(t), 0.03, 0.05, 0.9, min(0.12, dur * 0.4))


def crowd(dur, n=14, vowel="a", f_lo=110, f_hi=220, rise=0.2, seed=0, noise_amt=0.3):
    r = np.random.default_rng(seed)
    out = np.zeros(int(dur * SR))
    for i in range(n):
        f = r.uniform(f_lo, f_hi)
        d0 = r.uniform(0, 0.3)
        d = dur - d0
        y = vox((f, f * (1 + rise * r.uniform(0.5, 1.5))), d, vowel, rough=0.6, seed=i + seed)
        s = int(d0 * SR)
        out[s:s + len(y)] += y[:len(out) - s] * r.uniform(0.5, 1.0)
    out += noise_amt * bp(noise(len(out), seed), 300, 3000) * env_adsr(len(out), 0.2, 0.2, 0.8, 0.5)
    return out / n * 3


def metal(dur=0.7, base=520, seed=0, decay=0.35):
    r = np.random.default_rng(seed)
    t = T(dur)
    x = np.zeros(len(t))
    for k in (1.0, 2.52, 4.03, 6.6, 8.9):
        f = base * k * r.uniform(0.97, 1.03)
        x += np.sin(2 * np.pi * f * t + r.random() * 6) * np.exp(-t / (decay / k ** 0.4)) / k ** 0.6
    x += hp(noise(len(t), seed), 2500) * np.exp(-t * 60) * 0.8
    return x * 0.5


def thud(dur=0.3, f=90, seed=0, bright=600):
    t = T(dur)
    x = np.sin(2 * np.pi * f * (1 + np.exp(-t * 40)) * t) * np.exp(-t * 14)
    x += lp(noise(len(t), seed), bright) * np.exp(-t * 30) * 0.7
    return x


def whoosh(dur=0.8, lo=300, hi=3000, up=True, seed=0):
    n = int(dur * SR)
    x = noise(n, seed)
    out = np.zeros(n)
    blocks = 24
    for b in range(blocks):
        s, e = b * n // blocks, (b + 1) * n // blocks
        k = b / (blocks - 1)
        k = k if up else 1 - k
        fc = lo + (hi - lo) * k
        out[s:e] = bp(x[max(0, s - 2000):e], fc * 0.7, fc * 1.4)[-(e - s):]
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    return out * env * 1.2


def steps(dur, rate, seed=0, gain=1.0, metal_amt=0.0):
    r = np.random.default_rng(seed)
    items = []
    t = 0.0
    i = 0
    while t < dur - 0.2:
        items.append((t, thud(0.2, 70 + r.uniform(-10, 10), seed + i, 400), 0.6 * gain))
        if metal_amt:
            items.append((t + 0.01, metal(0.25, 900 + r.uniform(-80, 80), seed + i, 0.12), metal_amt))
        t += rate * r.uniform(0.9, 1.1)
        i += 1
    return mixat(dur, items)


def chirps(dur, seed=0, f=(2500, 5200), n=10):
    r = np.random.default_rng(seed)
    items = []
    for i in range(n):
        d = r.uniform(0.05, 0.15)
        t = T(d)
        f0, f1 = r.uniform(*f), r.uniform(*f)
        y = np.sin(2 * np.pi * np.cumsum(np.linspace(f0, f1, len(t))) / SR) * np.sin(np.linspace(0, np.pi, len(t)))
        items.append((r.uniform(0, dur - 0.2), y, 0.3))
    return mixat(dur, items)


# ---------------------------------------------------------------- registry
def make(name, v=0):
    r = np.random.default_rng(v + 100)
    if name in ("wind", "wind_cold"):
        d = 7.0
        x = lp(noise(int(d * SR), v), 900 if name == "wind" else 2400)
        tt = T(d)
        x *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.15 * tt + 1) * np.sin(2 * np.pi * 0.07 * tt)
        if name == "wind_cold":
            x += 0.15 * bp(noise(len(x), v + 1), 1800, 2600)
        return x * env_adsr(len(x), 1.0, 0.1, 1.0, 2.0) * 0.6
    if name == "horn":
        x = brass(midi(50), 3.0, vib=4.0, bright=0.5) + 0.6 * brass(midi(57), 3.0, vib=4.3, bright=0.4)
        return reverb(x * env_adsr(len(x), 0.6, 0.2, 0.9, 0.8), 0.4)
    if name == "fanfare_persian":
        x = mixat(4.0, [(0, make("horn"), 0.8)] + [(i * 0.125, frame_drum("tek", seed=i), 0.4) for i in range(16)])
        return x
    if name == "bow_creak":
        n = int(1.0 * SR)
        pulses = np.zeros(n)
        for i in range(60):
            pulses[int(r.uniform(0, n - 10))] = r.uniform(0.5, 1)
        x = bp(np.convolve(pulses, np.hanning(60), "same"), 300, 1800) * np.linspace(0.3, 1, n)
        return x * 2
    if name == "bow_release":
        items = [(r.uniform(0, 0.15), pluck(r.uniform(90, 140), 0.4, 0.3, seed=i), 0.3) for i in range(14)]
        items.append((0.05, whoosh(0.9, 400, 2500, True, v), 0.8))
        return mixat(1.2, items)
    if name == "arrow_swarm":
        d = 3.2
        x = whoosh(d, 600, 4000, True, v) * 1.2
        tt = T(d)
        for i in range(10):
            f0 = r.uniform(1500, 3000)
            s = r.uniform(0, 1.5)
            m = (tt > s) & (tt < s + 1.2)
            g = np.zeros(len(tt))
            g[m] = np.sin(np.linspace(0, np.pi, m.sum()))
            x += 0.05 * np.sin(2 * np.pi * np.cumsum(f0 * (1 - 0.3 * (tt - s).clip(0, 1.2))) / SR) * g
        return x
    if name == "shields_up":
        items = [(r.uniform(0, 0.25), metal(0.4, r.uniform(380, 650), i, 0.2), 0.35) for i in range(8)]
        items.append((0, bp(noise(int(0.4 * SR), v), 200, 2000) * ex(int(0.4 * SR), 0.1), 0.6))
        return mixat(0.9, items)
    if name == "arrow_thunk":
        return add(thud(0.12, 180 + r.uniform(-30, 30), v, 2500) * 0.8, bp(noise(int(0.12 * SR), v), 1000, 3500) * ex(int(0.12 * SR), 0.015))
    if name == "arrow_ground":
        return thud(0.1, 120, v, 900) * 0.5
    if name in ("whoosh", "whoosh_big", "whoosh_soft"):
        d = {"whoosh": 0.7, "whoosh_big": 1.3, "whoosh_soft": 1.6}[name]
        x = whoosh(d, 200, 2500 if name != "whoosh_soft" else 1200, True, v)
        if name == "whoosh_big":
            x += 0.5 * whoosh(d, 80, 600, False, v + 1)
        return x
    if name == "boom":
        t = T(3.0)
        x = np.sin(2 * np.pi * 38 * (1 + 0.8 * np.exp(-t * 6)) * t) * np.exp(-t * 1.6)
        x += lp(noise(len(t), v), 200) * np.exp(-t * 2.5) * 0.6
        return np.tanh(x * 1.5) * 0.9
    if name == "impact_big":
        items = [(0, make("boom"), 0.9)] + [(r.uniform(0, 0.15), metal(0.9, r.uniform(300, 700), i), 0.4) for i in range(8)]
        items += [(r.uniform(0, 0.1), thud(0.4, 80, i), 0.6) for i in range(6)]
        return mixat(3.0, items)
    if name == "drum_hit":
        return taiko(50, 1.6, 1.2, seed=v)
    if name == "tick":
        return hp(noise(int(0.03 * SR), v), 2500) * ex(int(0.03 * SR), 0.005)
    if name == "glass_crack":
        items = [(r.uniform(0, 0.5) ** 2, hp(noise(int(0.01 * SR), i), 3000) * ex(int(0.01 * SR), 0.002), r.uniform(0.3, 1)) for i in range(50)]
        t = T(1.5)
        ring = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 3) for f in (2900, 4170, 5630)) * 0.08
        items.append((0.0, ring, 1.0))
        return mixat(1.6, items)
    if name == "glass_shatter":
        n = int(1.8 * SR)
        x = hp(noise(n, v), 2500) * ex(n, 0.25) * 0.7
        t = T(1.8)
        for i in range(30):
            s = r.uniform(0, 0.6)
            f = r.uniform(2000, 7000)
            g = (t > s) * np.exp(-(t - s).clip(0) * r.uniform(6, 14))
            x += np.sin(2 * np.pi * f * t) * g * 0.08
        return x
    if name == "birds":
        return chirps(4.0, v, n=14)
    if name == "baby":
        a = vox((420, 520), 0.6, "a", seed=v)
        b = vox((520, 380), 0.7, "e", seed=v + 1)
        return cat(a, b, gap=0.15) * 0.5
    if name == "sparkle":
        return mixat(1.6, [(i * 0.07, bell(midi(86 + k), 1.0), 0.5) for i, k in enumerate((0, 4, 7, 12, 16))])
    if name == "crow":
        c = vox((620, 560), 0.3, "a", rough=1.5, seed=v)
        return cat(c, c * 0.8, gap=0.2) * 0.7
    if name == "pop":
        t = T(0.1)
        return np.sin(2 * np.pi * np.cumsum(np.linspace(900, 300, len(t))) / SR) * ex(len(t), 0.03)
    if name == "boing":
        t = T(0.6)
        f = 180 * (1 + 0.3 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 4)) * (1 + t)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * ex(len(t), 0.25) * 0.8
    if name in ("footsteps", "run_steps"):
        return steps(3.0, 0.5 if name == "footsteps" else 0.22, v, 0.6)
    if name == "footsteps_armor":
        return steps(4.0, 0.55, v, 0.6, metal_amt=0.15)
    if name == "run_many":
        return sum(steps(3.0, 0.19 + i * 0.013, v + i * 10, 0.4) for i in range(5))
    if name == "march_step":
        return add(thud(0.3, 65, v, 500) * 0.8, metal(0.3, 800 + r.uniform(-50, 50), v, 0.1) * 0.15)
    if name in ("march_far", "march_big"):
        d = 5.0
        x = sum(steps(d, 0.5 + i * 0.01, v + i * 7, 0.5, metal_amt=0.1) for i in range(4))
        x = add(x, crowd(d, 6, "o", 90, 140, 0.0, v, noise_amt=0.2) * 0.3)
        return lp(x, 900 if name == "march_far" else 3000) * (0.7 if name == "march_far" else 1.0)
    if name in ("stamp", "jump_land", "step", "stone", "shield_place"):
        if name == "stamp":
            return reverb(thud(0.5, 60, v, 800) * 1.2, 0.4)
        if name == "stone":
            return thud(0.3, 110, v, 700) * 0.9
        if name == "shield_place":
            return thud(0.15, 220, v, 2000) * 0.6
        return thud(0.18, 90, v, 500) * 0.5
    if name == "snap":
        return bp(noise(int(0.06 * SR), v), 1500, 6000) * ex(int(0.06 * SR), 0.01) * 1.2
    if name in ("sting", "sting_low"):
        low = name == "sting_low"
        x = sum(brass(midi(n - (12 if low else 0)), 1.6, bright=1.0) for n in (50, 56, 62))
        return mixat(2.0, [(0, x, 0.6), (0, taiko(48, 1.6, 1.0, seed=v), 0.8)])
    if name == "bonk":
        t = T(0.35)
        x = np.sin(2 * np.pi * np.cumsum(np.linspace(420, 180, len(t))) / SR) * ex(len(t), 0.08)
        return add(x, bp(noise(len(t), v), 800, 3000) * ex(len(t), 0.01))
    if name == "birdies":
        return chirps(1.8, v, (3000, 4800), n=16) * 0.8
    if name == "fanfare_small":
        return mixat(1.4, [(i * 0.15, brass(midi(n), 0.5 if i < 2 else 0.9, bright=0.8), 0.4)
                           for i, n in enumerate((62, 66, 69))])
    if name == "snore":
        a = vox((90, 80), 1.0, "o", rough=2.0, seed=v) * 0.6
        b = lp(noise(int(0.9 * SR), v), 1200) * env_adsr(int(0.9 * SR), 0.3, 0.1, 0.8, 0.4) * 0.2
        return cat(a, b, gap=0.1)
    if name == "bubbles":
        items = []
        for i in range(18):
            t = T(0.06)
            f0 = r.uniform(300, 700)
            items.append((r.uniform(0, 2.2), np.sin(2 * np.pi * np.cumsum(np.linspace(f0, f0 * 2.2, len(t))) / SR) * np.hanning(len(t)), 0.35))
        return mixat(2.5, items)
    if name == "slurp":
        return whoosh(0.6, 400, 1800, True, v) * 0.8
    if name == "gag":
        return cat(vox((160, 110), 0.35, "u", rough=2.5, seed=v), vox((140, 90), 0.4, "o", rough=2.5, seed=v + 1), gap=0.08)
    if name == "laugh":
        items = []
        for p in range(5):
            f = r.uniform(110, 190)
            for k in range(8):
                items.append((p * 0.07 + k * 0.2 + r.uniform(0, 0.03), vox(f * (1 - k * 0.02), 0.11, "a", seed=p * 10 + k), 0.4))
        return mixat(2.6, items)
    if name == "waves":
        d = 7.0
        x = lp(noise(int(d * SR), v), 700)
        tt = T(d)
        x *= 0.4 + 0.6 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.25 * tt)) ** 2
        return x * env_adsr(len(x), 0.8, 0.1, 1, 1.5) * 0.7
    if name == "counter":
        items = []
        t = 0.0
        k = 0
        while t < 1.8:
            items.append((t, make("tick", k) * 0.8, 1.0))
            t += 0.12 * (1 - t / 2.4)
            k += 1
        items.append((1.9, bell(midi(84), 1.0), 0.6))
        return mixat(2.8, items)
    if name in ("crowd_cheer", "war_cry", "crowd_boo", "crowd_murmur", "grunt_exercise"):
        if name == "crowd_cheer":
            return crowd(3.0, 16, "e", 130, 260, 0.35, v) * env_adsr(int(3 * SR), 0.2, 0.3, 0.8, 1.0)
        if name == "war_cry":
            return crowd(2.4, 18, "a", 100, 200, 0.45, v, noise_amt=0.4)
        if name == "crowd_boo":
            return crowd(2.6, 12, "u", 90, 150, -0.15, v, noise_amt=0.15) * 0.8
        if name == "grunt_exercise":
            return mixat(3.0, [(i * 0.63, vox((150, 120), 0.18, "u", rough=1.0, seed=i), 0.5) for i in range(5)])
        return crowd(3.5, 10, "o", 100, 160, 0.0, v, noise_amt=0.2) * 0.5
    if name == "paper":
        n = int(0.7 * SR)
        x = bp(noise(n, v), 2000, 8000)
        am = np.repeat(r.uniform(0.1, 1, n // 400 + 1), 400)[:n]
        return x * lp(am, 40) * 0.7
    if name == "peek":
        return whoosh(0.35, 800, 2500, True, v) * 0.6
    if name == "laugh_king" or name == "rooster_far":
        return np.zeros(10)
    if name == "stone_carve":
        return mixat(2.0, [(i * 0.22 + r.uniform(0, 0.03), metal(0.2, 1800 + r.uniform(-200, 200), i, 0.06), 0.4) for i in range(8)])
    if name == "shield_bash":
        return add(thud(0.35, 85, v, 1200) * 0.9, metal(0.3, 300 + r.uniform(-40, 40), v, 0.12) * 0.4)
    if name == "stab":
        n = int(0.14 * SR)
        return add(bp(noise(n, v), 1500, 6000) * ex(n, 0.03) * 0.8, thud(0.14, 100, v, 800) * 0.6)
    if name == "grunt":
        return vox((r.uniform(110, 150), r.uniform(80, 100)), 0.28, r.choice(["u", "o", "a"]), rough=1.5, seed=v)
    if name == "clang":
        return metal(0.8, r.uniform(450, 700), v, 0.4)
    if name in ("battle_amb", "battle_amb_short"):
        d = 20.0 if name == "battle_amb" else 4.5
        x = crowd(d, 16, "a", 90, 190, 0.05, v, noise_amt=0.6) * 0.6
        items = []
        t = 0.0
        k = 0
        while t < d - 1:
            items.append((t, make(r.choice(["clang", "shield_bash", "stab", "grunt"]), v + k), r.uniform(0.15, 0.35)))
            t += r.uniform(0.12, 0.4)
            k += 1
        x = add(x, mixat(d, items))
        return x * env_adsr(len(x), 0.8, 0.1, 1.0, 2.0)
    if name == "ding":
        return bell(midi(88), 1.2)
    if name == "drums_persian":
        pat = "D.kkD.k.D.kkDkk."
        items = [(i * 0.13, frame_drum("doum" if c == "D" else "tek", seed=i), 0.7)
                 for i, c in enumerate(pat * 2) if c != "."]
        return mixat(4.5, items)
    if name == "crickets":
        d = 6.0
        tt = T(d)
        g = ((np.sin(2 * np.pi * 28 * tt) > 0.3) * (np.sin(2 * np.pi * 0.9 * tt) > 0)).astype(float)
        x = np.sin(2 * np.pi * 4600 * tt) * lp(g, 200) * 0.12
        x += np.sin(2 * np.pi * 5100 * tt) * lp(((np.sin(2 * np.pi * 31 * tt + 1) > 0.3) * (np.sin(2 * np.pi * 0.7 * tt + 2) > 0)).astype(float), 200) * 0.08
        return x * env_adsr(len(x), 0.5, 0.1, 1, 1.5)
    if name == "sneak":
        notes = [50, 0, 53, 0, 50, 0, 49, 0, 50, 0, 53, 55, 57, 0, 0, 0]
        return mixat(4.0, [(i * 0.22, pluck(midi(n), 0.25, 0.4, seed=i), 0.6) for i, n in enumerate(notes) if n])
    if name in ("fire_crackle", "fire_big"):
        d = 6.0
        x = lp(noise(int(d * SR), v), 300 if name == "fire_crackle" else 600) * (0.3 if name == "fire_crackle" else 0.8)
        items = [(r.uniform(0, d - 0.1), hp(noise(int(0.008 * SR), i), 2000) * ex(int(0.008 * SR), 0.002), r.uniform(0.2, 0.8)) for i in range(160)]
        x = add(x, mixat(d, items))
        return x * env_adsr(len(x), 0.5, 0.1, 1, 1.5)
    if name == "coins":
        return mixat(1.4, [(r.uniform(0, 0.6), metal(0.5, r.uniform(2500, 4200), i, 0.15), 0.25) for i in range(16)])
    if name == "owl":
        h = vox((420, 380), 0.35, "u", seed=v)
        return cat(h, h * 0.8, gap=0.25) * 0.6
    if name == "thought":
        return mixat(1.6, [(i * 0.06, pluck(midi(n), 0.9, 0.6, seed=i), 0.35) for i, n in enumerate((62, 65, 69, 72, 74, 77, 81))])
    if name == "heartbeat":
        return mixat(1.1, [(0, thud(0.25, 50, v, 150) * 1.4, 1.0), (0.28, thud(0.25, 46, v + 1, 150) * 1.1, 0.8)])
    if name == "spear_break":
        n = int(0.5 * SR)
        x = bp(noise(n, v), 800, 5000) * ex(n, 0.04) * 1.2
        return add(x, mixat(0.5, [(r.uniform(0.02, 0.2), make("snap", i), 0.4) for i in range(5)]))
    if name == "sword_draw":
        x = whoosh(0.7, 2000, 7000, True, v) * 0.5
        return add(x, metal(0.9, 1300, v, 0.5) * 0.3)
    if name == "slowmo":
        t = T(2.0)
        x = np.sin(2 * np.pi * np.cumsum(np.linspace(120, 35, len(t))) / SR) * np.sin(np.linspace(0, np.pi, len(t)))
        return add(x * 0.8, whoosh(2.0, 100, 600, False, v) * 0.6)
    if name == "brawl":
        items = []
        t = 0.0
        k = 0
        while t < 4.0:
            kind = r.choice(["bonk", "shield_bash", "boing", "clang", "pop", "grunt"])
            items.append((t, make(kind, v + k), 0.4))
            t += r.uniform(0.1, 0.3)
            k += 1
        return add(mixat(4.6, items), crowd(4.6, 6, "a", 120, 180, 0.0, v) * 0.3)
    if name == "ship_crash":
        items = [(r.uniform(0, 0.25), make("snap", i), 0.6) for i in range(14)]
        items += [(0, thud(0.6, 60, v, 500), 1.0), (0.1, whoosh(1.5, 300, 1500, False, v) * 0.6, 1.0)]
        return mixat(2.2, items)
    if name == "click":
        return hp(noise(int(0.02 * SR), v), 1500) * ex(int(0.02 * SR), 0.004) * 1.2
    if name == "bell":
        return mixat(1.6, [(0, bell(midi(84), 1.2), 0.6), (0.18, bell(midi(88), 1.2), 0.6)])
    if name == "shield_hand":
        return add(metal(0.6, 420, v, 0.3) * 0.6, thud(0.2, 120, v, 800) * 0.5)
    raise KeyError(name)


_CACHE = {}


def sfx(name, variant=0):
    key = (name, variant % 4)
    if key not in _CACHE:
        x = make(name, variant % 4)
        m = np.max(np.abs(x)) + 1e-9
        _CACHE[key] = (x / m * 0.9).astype(np.float32)
    return _CACHE[key]
