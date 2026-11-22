# -*- coding: utf-8 -*-
"""Turns the screenplay into absolute times (scenes, beats, subtitles)."""
import re
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from script import SCENES, SPEAKERS, Line, Pause
from tts import synth_line

CHAPTER_CARD = 2.3   # seconds a chapter card is held before narration starts


@dataclass
class BeatT:
    kind: str
    start: float
    end: float
    spk: Optional[str] = None
    text: Optional[str] = None
    tag: Optional[str] = None
    npy: Optional[str] = None
    env: Optional[np.ndarray] = None
    speech_end: float = 0.0


@dataclass
class SceneT:
    id: str
    music: str
    start: float
    end: float
    chapter: Optional[str]
    beats: list = field(default_factory=list)
    first_beat: float = 0.0

    @property
    def dur(self):
        return self.end - self.start

    def tag(self, name):
        """Beat with this tag (times relative to scene start)."""
        for b in self.beats:
            if b.tag == name:
                return b
        raise KeyError(f"{self.id}: no beat tagged {name}")

    def t(self, name, which="start"):
        b = self.tag(name)
        return (b.start if which == "start" else b.end) - self.start


@dataclass
class Cue:
    start: float
    end: float
    text: str
    spk: str


def _chunks(text, maxlen=44):
    """Split a sentence into subtitle cues of max two lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > maxlen and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
        if re.search(r"[.!?:]$", w) and len(cur) > maxlen * 0.55:
            lines.append(cur)
            cur = ""
    if cur:
        lines.append(cur)
    cues = []
    i = 0
    while i < len(lines):
        if i + 1 < len(lines) and len(lines[i]) + len(lines[i + 1]) < maxlen * 2 \
                and not re.search(r"[.!?]$", lines[i]):
            cues.append(lines[i] + "\n" + lines[i + 1])
            i += 2
        else:
            cues.append(lines[i])
            i += 1
    return cues


def build(scene_defs=None, chunker=None):
    t = 0.0
    scenes, cues = [], []
    chunker = chunker or _chunks
    for sc in (scene_defs or SCENES):
        st = SceneT(sc.id, sc.music, t, t, sc.chapter)
        cur = t + sc.lead + (CHAPTER_CARD if sc.chapter else 0.0)
        st.first_beat = cur - t
        for b in sc.beats:
            if isinstance(b, Pause):
                st.beats.append(BeatT("pause", cur, cur + b.dur, tag=b.tag))
                cur += b.dur
            else:
                npy, dur, env = synth_line(b.spk, b.say or b.text)
                bt = BeatT("line", cur, cur + dur + b.gap, spk=b.spk, text=b.text,
                           tag=b.tag, npy=npy, env=env, speech_end=cur + dur)
                st.beats.append(bt)
                parts = chunker(b.text)
                total = sum(len(p) for p in parts)
                c0 = cur
                for p in parts:
                    d = dur * len(p) / total
                    cues.append(Cue(c0, c0 + d, p, b.spk))
                    c0 += d
                cur += dur + b.gap
        st.end = cur + sc.tail
        t = st.end
        scenes.append(st)
    return scenes, cues


def speaking(scenes, time):
    """(speaker, mouth_open 0..1) for the voice line active at `time`."""
    for sc in scenes:
        if sc.start <= time < sc.end:
            for b in sc.beats:
                if b.kind == "line" and b.start <= time < b.speech_end:
                    i = int((time - b.start) * 30)
                    v = float(b.env[min(i, len(b.env) - 1)]) if len(b.env) else 0
                    return b.spk, v
    return None, 0.0


def srt(cues, path):
    def ts(x):
        h, r = divmod(x, 3600)
        m, s = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
    with open(path, "w", encoding="utf-8") as f:
        for i, c in enumerate(cues, 1):
            name = SPEAKERS[c.spk][0]
            txt = c.text if c.spk == "N" else f"{c.text}"
            f.write(f"{i}\n{ts(c.start)} --> {ts(c.end)}\n{txt}\n\n")


if __name__ == "__main__":
    import sys
    scenes, cues = build()
    for s in scenes:
        print(f"{s.id:12s} {s.start:7.2f} -> {s.end:7.2f}  ({s.dur:5.1f}s) music={s.music}")
    print("TOTAL", scenes[-1].end, "s", len(cues), "cues")
