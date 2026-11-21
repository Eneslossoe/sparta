# -*- coding: utf-8 -*-
"""Final soundtrack: voice + music (ducked) + SFX, mastered to -14 LUFS."""
import json
import os
import subprocess
import wave

import numpy as np
from scipy import signal

from .music import build_music
from .sfx import sfx
from .synth import SR, lp, place, reverb

DEFAULT_GAIN = {"battle_amb": 0.4, "battle_amb_short": 0.4}
REVERB_SFX = {"war_cry", "horn", "crowd_cheer", "boom", "impact_big", "drum_hit", "stamp", "sting",
              "sting_low", "glass_shatter", "heartbeat"}


def ducking_curve(voice, depth=0.62):
    hop = 441
    n = len(voice) // hop + 1
    rms = np.array([np.sqrt(np.mean(voice[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)])
    pres = (rms > 0.02).astype(float)
    # attack fast, release slow
    out = np.zeros(n)
    v = 0.0
    for i in range(n):
        target = pres[i]
        k = 0.35 if target > v else 0.025
        v += (target - v) * k
        out[i] = v
    curve = 1 - depth * out
    return np.repeat(curve, hop)[:len(voice)]


def build_audio(scenes, registry, bounds, chapter_card, out_wav):
    total = scenes[-1].end
    N = int((total + 1.5) * SR)
    voice = np.zeros(N)
    for S in scenes:
        for b in S.beats:
            if b.kind == "line":
                x = np.load(b.npy)
                s = int(b.start * SR)
                voice[s:s + len(x)] += x[:N - s]
    print("voice placed", flush=True)

    music = build_music(scenes, total)[:, :N]
    if music.shape[1] < N:
        music = np.pad(music, ((0, 0), (0, N - music.shape[1])))
    duck = ducking_curve(voice)

    fx = np.zeros((2, N))
    fx_wet = np.zeros((2, N))
    count = 0
    events = []
    for S in scenes:
        events += registry[S.id][1](S)
        if S.chapter:
            t_card = S.start + S.first_beat - chapter_card
            events += [(t_card, "drum_hit", 0.55, 0.0), (t_card, "whoosh", 0.35, 0.0)]
    for B, kind, i in bounds:
        if kind == "crack":
            events += [(B - 0.5, "glass_crack", 0.55, 0.0), (B - 0.05, "glass_shatter", 0.6, 0.0),
                       (B - 0.1, "whoosh_big", 0.45, 0.0)]
        elif kind == "fade":
            events += [(B - 0.3, "whoosh_soft", 0.18, 0.0)]
    for k, (t, name, gain, pan) in enumerate(sorted(events, key=lambda e: e[0])):
        if gain == 0.0:
            gain = DEFAULT_GAIN.get(name, 0.0)
            if gain == 0.0:
                continue
        x = sfx(name, k)
        target = fx_wet if name in REVERB_SFX else fx
        place(target, x, t * SR, gain, pan)
        count += 1
    for ch in range(2):
        fx_wet[ch] = reverb(fx_wet[ch], wet=0.35, dur=2.0, decay=2.6, seed=21 + ch)
    fx += fx_wet
    print(f"sfx placed: {count}", flush=True)

    mix = np.zeros((2, N))
    mix += voice[None, :] * 1.0
    mix += music * 0.55 * duck[None, :]
    mix += fx * 0.62
    # gentle bus compression + soft clip
    peak = np.max(np.abs(mix))
    mix = mix / max(peak, 1e-9) * 0.98
    mix = np.tanh(mix * 1.4) / np.tanh(1.4)
    raw = out_wav.replace(".wav", "_raw.wav")
    _write_wav(raw, mix)
    _loudnorm(raw, out_wav)
    os.remove(raw)
    return out_wav


def _write_wav(path, x):
    x = np.clip(x, -1, 1)
    data = (x.T * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def _loudnorm(src, dst, I=-14.0, TP=-1.5, LRA=11.0):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af",
                        f"loudnorm=I={I}:TP={TP}:LRA={LRA}:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    txt = r.stderr
    js = json.loads(txt[txt.rindex("{"):txt.rindex("}") + 1])
    af = (f"loudnorm=I={I}:TP={TP}:LRA={LRA}:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:"
          f"linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", af, "-ar", str(SR), dst], check=True)
    print(f"loudness: input {js['input_i']} LUFS -> {I} LUFS", flush=True)
