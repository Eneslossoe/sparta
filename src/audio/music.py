# -*- coding: utf-8 -*-
"""Procedural score: one cue per scene mood, rendered to the scene's real length."""
import numpy as np

from .synth import (SR, bass_note, bell, brass, choir, cymbal, frame_drum, midi, ney, pad, place,
                    pluck, reverb, snare, strings, taiko)

# chords as MIDI note lists (D minor world)
Dm = [50, 57, 62, 65]
Bb = [46, 53, 58, 62]
C = [48, 55, 60, 64]
A = [45, 52, 57, 61]
Gm = [43, 50, 55, 58]
F = [41, 48, 53, 57]
Dmaj = [50, 57, 62, 66]

THEME = [(69, 1), (74, 1), (72, .5), (70, .5), (69, 1), (70, 1), (69, .5), (67, .5), (65, 2),
         (67, 1), (69, 1), (70, 1), (72, 1), (69, 4)]
HIJAZ = [(62, .5), (63, .5), (66, .5), (67, .5), (69, 1), (67, .5), (66, .5), (63, 1), (62, 1),
         (66, .5), (63, .5), (62, 1)]
LAMENT = [(74, 2), (72, 1), (70, 1), (69, 3), (65, 1), (67, 2), (69, 1), (70, 1), (69, 4)]
COMIC = [(65, .5), (69, .5), (72, .5), (69, .5), (70, .5), (67, .5), (64, .5), (60, .5),
         (65, .5), (67, .5), (69, .5), (70, .5), (72, 1), (0, 1)]
MARCH = [(62, 1.5), (62, .5), (65, 1), (67, 1), (69, 2), (67, 1), (65, 1), (64, 1.5), (65, .5),
         (62, 2), (0, 2)]


def _buf(dur):
    return np.zeros((2, int(dur * SR) + 1))


def melody(buf, notes, t0, t1, bpm, inst, gain=1.0, pan=0.0, octave=0, loop=True, gap=0.0):
    b = 60.0 / bpm
    t = t0
    while t < t1:
        for n, beats in notes:
            if t >= t1:
                break
            d = beats * b
            if n:
                x = inst(midi(n + 12 * octave), d * 1.05 + 0.1)
                place(buf, x, t * SR, gain, pan)
            t += d
        t += gap * b
        if not loop:
            break


def chords_pad(buf, prog, t0, t1, bar, gain=0.3, cutoff=1400, inst="pad", vowel="a"):
    t = t0
    i = 0
    while t < t1:
        ch = prog[i % len(prog)]
        d = min(bar, t1 - t) + 0.6
        if inst == "pad":
            x = pad([midi(n) for n in ch], d, cutoff=cutoff, attack=min(0.5, bar * 0.3), release=0.6)
            place(buf, x, t * SR, gain, -0.3)
            place(buf, x[::-1][::-1], t * SR + 300, gain * 0.8, 0.3)
        elif inst == "choir":
            for k, n in enumerate(ch[1:]):
                x = choir(midi(n), d, vowel)
                place(buf, x, t * SR, gain, -0.5 + k * 0.5)
        elif inst == "strings":
            for k, n in enumerate(ch):
                x = strings(midi(n), d, attack=0.3, release=0.5, cutoff=1600)
                place(buf, x, t * SR, gain, -0.4 + k * 0.25)
        t += bar
        i += 1


def drum_pattern(buf, pattern, t0, t1, bpm, gain=1.0, sub=4):
    """pattern: list of strings per step ('T' taiko, 't' small taiko, 'D' doum, 'k' tek, 'S' snare, '.' rest)."""
    st = 60.0 / bpm / sub
    t = t0
    i = 0
    seed = 0
    while t < t1:
        c = pattern[i % len(pattern)]
        seed += 1
        if c == "T":
            place(buf, taiko(52, 1.2, seed=seed), t * SR, gain, -0.1)
        elif c == "t":
            place(buf, taiko(85, 0.6, 0.6, seed=seed), t * SR, gain * 0.7, 0.2)
        elif c == "D":
            place(buf, frame_drum("doum", seed=seed), t * SR, gain, -0.2)
        elif c == "k":
            place(buf, frame_drum("tek", seed=seed), t * SR, gain * 0.7, 0.3)
        elif c == "S":
            place(buf, snare(seed=seed), t * SR, gain * 0.6, 0.15)
        elif c == "s":
            place(buf, snare(0.15, seed=seed), t * SR, gain * 0.3, 0.15)
        t += st
        i += 1


def arpeggio(buf, prog, t0, t1, bpm, gain=0.35, octave=12, inst=None, pat=(0, 1, 2, 3, 2, 1, 2, 3),
             bar_beats=4, step=0.5, pan=0.2, bright=0.4):
    b = 60.0 / bpm
    inst = inst or (lambda f, d: pluck(f, d, bright))
    t = t0
    i = 0
    while t < t1:
        ch = prog[(i // int(bar_beats / step)) % len(prog)]
        n = ch[pat[i % len(pat)] % len(ch)] + octave
        place(buf, inst(midi(n), b * step * 2.5), t * SR, gain, pan)
        t += b * step
        i += 1


# =================================================================== cues
def cue_tension(dur, **k):
    buf = _buf(dur + 2)
    n = buf.shape[1]
    x = pad([midi(38), midi(45), midi(50)], dur + 1.5, cutoff=500, attack=2.0, release=1.5)
    place(buf, x, 0, 0.55)
    tt = np.arange(int((dur + 1.5) * SR)) / SR
    trem = strings(midi(81), dur + 1.5, attack=dur * 0.6, release=1.0, cutoff=5000) * \
        (0.6 + 0.4 * np.sin(2 * np.pi * 11 * tt))
    place(buf, trem, 0, 0.18, 0.4)
    t = 0.6
    i = 0
    while t < dur:
        g = 0.45 + 0.5 * min(1, t / max(dur, 1))
        place(buf, taiko(48, 1.0, seed=i), t * SR, g)
        place(buf, taiko(48, 1.0, 0.7, seed=i + 50), (t + 0.28) * SR, g * 0.7)
        t += 1.6
        i += 1
    return buf


def cue_title(dur, **k):
    buf = _buf(dur + 2)
    place(buf, taiko(42, 2.5, 1.4, seed=1), 0, 1.0)
    place(buf, cymbal(4.0, seed=2), 0, 0.5)
    for t_, n_, d_ in ((1.0, 50, 0.6), (1.5, 57, 0.6), (2.2, 62, 2.4)):
        for o in (0, 12):
            place(buf, brass(midi(n_ + o), d_ + 0.4), t_ * SR, 0.32, -0.2 if o else 0.2)
        place(buf, taiko(55, 1.0, seed=int(t_ * 10)), t_ * SR, 0.8)
    chords_pad(buf, [Dm, Bb, Gm, A], 2.2, dur, 2.6, gain=0.22, inst="choir")
    chords_pad(buf, [Dm, Bb, Gm, A], 2.2, dur, 2.6, gain=0.18, cutoff=1200)
    drum_pattern(buf, "T...t...T.t.t...", 4.4, dur - 1.0, 92, 0.55)
    return buf


def cue_sparta(dur, **k):
    buf = _buf(dur + 2)
    bpm = 84
    arpeggio(buf, [Dm, C, Bb, C], 0, dur, bpm, gain=0.32, octave=12)
    chords_pad(buf, [Dm, C, Bb, C], 0, dur, 4 * 60 / bpm, gain=0.16, cutoff=1100)
    melody(buf, THEME, 4 * 4 * 60 / bpm, dur, bpm, lambda f, d: ney(f, d), gain=0.32, pan=-0.1,
           gap=8)
    return buf


def cue_training(dur, **k):
    buf = _buf(dur + 2)
    bpm = 116
    drum_pattern(buf, "D.k.D.kkD.k.Dkk.", 0, dur, bpm, 0.7)
    arpeggio(buf, [Dm, Dm, C, Bb], 0, dur, bpm, gain=0.28, octave=0, pat=(0, 2, 1, 3), step=0.5,
             bright=0.7)
    b = 60 / bpm
    t = 0
    i = 0
    prog = [50, 50, 48, 46]
    while t < dur:
        place(buf, bass_note(midi(prog[(i // 8) % 4] - 12), b * 0.45), t * SR, 0.5)
        t += b * 0.5
        i += 1
    melody(buf, THEME, 8 * b, dur, bpm, lambda f, d: brass(f, d, bright=0.6), gain=0.22, gap=16)
    return buf


def cue_comic(dur, **k):
    buf = _buf(dur + 2)
    bpm = 112
    b = 60 / bpm
    t = 0
    i = 0
    bass = [41, 48, 41, 48, 46, 53, 48, 43]
    while t < dur:
        place(buf, bass_note(midi(bass[i % 8]), b * 0.3, cutoff=700), t * SR, 0.55)
        t += b
        i += 1
    melody(buf, COMIC, 0, dur, bpm, lambda f, d: pluck(f, min(d, 0.25), 0.9), gain=0.35, pan=0.2)
    drum_pattern(buf, "k...k.k.", 0, dur, bpm, 0.4, sub=2)
    return buf


def cue_persian(dur, **k):
    buf = _buf(dur + 2)
    bpm = 96
    drum_pattern(buf, "D..k..k.D.k.k...", 0, dur, bpm, 0.65)
    place(buf, pad([midi(38), midi(45)], dur + 1, cutoff=600, attack=1.5), 0, 0.3)
    melody(buf, HIJAZ, 0, dur, bpm, lambda f, d: pluck(f, d + 0.3, 0.75), gain=0.33, pan=0.25)
    melody(buf, HIJAZ, 8 * 60 / bpm, dur, bpm, lambda f, d: ney(f, d), gain=0.28, pan=-0.25,
           octave=1, gap=8)
    return buf


def cue_solemn(dur, **k):
    buf = _buf(dur + 2)
    bpm = 66
    bar = 4 * 60 / bpm
    chords_pad(buf, [Dm, Bb, F, A], 0, dur, bar, gain=0.26, inst="choir", vowel="a")
    chords_pad(buf, [Dm, Bb, F, A], 0, dur, bar, gain=0.2, inst="strings")
    t = 0
    i = 0
    while t < dur:
        place(buf, taiko(46, 1.6, 0.6, seed=i), t * SR, 0.45)
        t += bar
        i += 1
    melody(buf, THEME, bar * 2, dur, bpm, lambda f, d: ney(f, d), gain=0.22, gap=8)
    return buf


def cue_march(dur, **k):
    buf = _buf(dur + 2)
    bpm = 100
    drum_pattern(buf, "T.s.S.s.t.s.S.ss", 0, dur, bpm, 0.6)
    chords_pad(buf, [Dm, Dm, Bb, C], 0, dur, 4 * 60 / bpm, gain=0.18, inst="strings")
    melody(buf, MARCH, 0, dur, bpm, lambda f, d: brass(f, d, bright=0.7), gain=0.26, octave=-1)
    return buf


def cue_battle(dur, intensity=1.0, choir_on=True, **k):
    buf = _buf(dur + 2)
    bpm = 138
    b = 60 / bpm
    drum_pattern(buf, "T.tTt.T.T.tTt.tt", 0, dur, bpm, 0.75 * intensity)
    prog = [50, 50, 46, 48]
    t = 0
    i = 0
    while t < dur:
        root = prog[(i // 16) % 4]
        for o in (0, 12):
            place(buf, strings(midi(root - 12 + o), b * 0.22, attack=0.005, release=0.05, cutoff=2600),
                  t * SR, 0.3 * intensity, -0.3 if o else 0.3)
        t += b * 0.25 * 1
        i += 1
    bar = 4 * b
    chords_pad(buf, [Dm, Bb, C, A], 0, dur, bar, gain=0.2 * intensity, inst="choir" if choir_on else "pad")
    melody(buf, [(62, 4), (65, 2), (64, 2), (62, 4), (57, 4)], bar * 2, dur, bpm,
           lambda f, d: brass(f, d, bright=1.0), gain=0.3 * intensity, gap=0)
    t = 0
    while t < dur:
        place(buf, cymbal(3.0, seed=int(t)), t * SR, 0.35 * intensity)
        t += bar * 4
    return buf


def cue_night(dur, **k):
    buf = _buf(dur + 2)
    bpm = 76
    b = 60 / bpm
    walk = [50, 51, 50, 49, 48, 49, 46, 45]
    t = 0
    i = 0
    while t < dur:
        place(buf, pluck(midi(walk[i % 8]), 0.6, 0.15), t * SR, 0.5, -0.2)
        t += b
        i += 1
    drum_pattern(buf, "D.......k.......", 0, dur, bpm, 0.4)
    place(buf, pad([midi(38), midi(44)], dur + 1, cutoff=450, attack=2.0), 0, 0.35)
    melody(buf, [(74, 4), (75, 4), (73, 6), (0, 2)], 4 * b, dur, bpm, lambda f, d: ney(f, d, breath=0.4),
           gain=0.18, pan=0.3)
    return buf


def cue_lament(dur, **k):
    buf = _buf(dur + 2)
    bpm = 60
    chords_pad(buf, [Dm, Bb, Gm, A], 0, dur, 4.0, gain=0.18, cutoff=900)
    chords_pad(buf, [Dm, Bb, Gm, A], 0, dur, 4.0, gain=0.12, inst="choir", vowel="u")
    melody(buf, LAMENT, 1.0, dur, bpm, lambda f, d: ney(f, d), gain=0.33, gap=4)
    return buf


def cue_epic_end(dur, **k):
    buf = _buf(dur + 2)
    bpm = 72
    bar = 4 * 60 / bpm
    prog = [Dm, Bb, F, C, Dm, Bb, C, Dmaj]
    chords_pad(buf, prog, 0, dur, bar * 0.9, gain=0.26, inst="choir")
    chords_pad(buf, prog, 0, dur, bar * 0.9, gain=0.18, inst="strings")
    melody(buf, THEME, bar, dur, bpm, lambda f, d: brass(f, d, bright=0.6), gain=0.22, octave=-1, gap=4)
    t = 0
    i = 0
    while t < dur:
        place(buf, taiko(44, 2.0, 0.8, seed=i), t * SR, 0.5)
        t += bar * 0.9
        i += 1
    return buf


def cue_outro(dur, **k):
    buf = _buf(dur + 3)
    bpm = 84
    arpeggio(buf, [Dm, Bb, C, Dm], 0, dur - 2.5, bpm, gain=0.3)
    chords_pad(buf, [Dm, Bb, C, Dm], 0, dur - 2.5, 4 * 60 / bpm, gain=0.18, cutoff=1300)
    melody(buf, THEME, 0, dur - 2.5, bpm, lambda f, d: ney(f, d), gain=0.25, loop=False)
    end = max(0.5, dur - 2.6)
    place(buf, taiko(42, 2.5, 1.2, seed=9), end * SR, 0.8)
    for k_, n in enumerate(Dm):
        place(buf, choir(midi(n + 12), 3.5), end * SR, 0.22, -0.4 + k_ * 0.3)
    place(buf, bell(midi(74), 3.0), end * SR, 0.4)
    return buf


def cue_silence(dur, **k):
    return _buf(dur + 1)


CUES = {"tension": cue_tension, "title": cue_title, "sparta": cue_sparta, "training": cue_training,
        "comic": cue_comic, "persian": cue_persian, "solemn": cue_solemn, "march": cue_march,
        "battle": cue_battle, "night": cue_night, "lament": cue_lament, "epic_end": cue_epic_end,
        "outro": cue_outro, "silence": cue_silence}


def plan(scenes):
    """Music segments (t0, t1, cue, kwargs). Merges consecutive scenes with the same cue."""
    segs = []
    for S in scenes:
        if S.music == "final":
            t = S.start
            tg = {k: S.start + S.t(k) for k in ("leofall", "protect", "rain", "fall", "end")}
            segs += [(t, tg["leofall"], "battle", {"intensity": 1.15}),
                     (tg["leofall"], tg["protect"], "lament", {}),
                     (tg["protect"], tg["rain"], "battle", {"intensity": 1.0}),
                     (tg["rain"], tg["fall"], "tension", {}),
                     (tg["fall"], tg["end"], "silence", {}),
                     (tg["end"], S.end, "lament", {})]
            continue
        if segs and segs[-1][2] == S.music and not segs[-1][3]:
            segs[-1] = (segs[-1][0], S.end, S.music, {})
        else:
            segs.append((S.start, S.end, S.music, {}))
    return segs


def build_music(scenes, total):
    out = np.zeros((2, int((total + 3) * SR)))
    segs = plan(scenes)
    for i, (t0, t1, cue, kw) in enumerate(segs):
        dur = t1 - t0
        x = CUES[cue](dur + 0.8, **kw)
        n = int((dur + 0.8) * SR)
        x = x[:, :n]
        fi = int(0.12 * SR)
        fo = int(1.0 * SR)
        x[:, :fi] *= np.linspace(0, 1, fi)
        x[:, -fo:] *= np.linspace(1, 0, fo)
        s = int(t0 * SR)
        e = min(out.shape[1], s + x.shape[1])
        out[:, s:e] += x[:, :e - s]
        print(f"  music {cue:9s} {t0:6.1f}-{t1:6.1f}s", flush=True)
    for ch in range(2):
        out[ch] = reverb(out[ch], wet=0.22, dur=2.4, decay=2.2, seed=11 + ch)
    return out
