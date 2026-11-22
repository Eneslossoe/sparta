# -*- coding: utf-8 -*-
"""Renderer for the vertical Reels cut (1080x1920, 30 fps)."""
import math
import multiprocessing as mp
import os
import subprocess
import sys
import time

import cairo

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BUILD, FPS
from draw import fx, overlay
from draw.core import clamp, ease, ease_back, font, prog, text, text_w
import scenes.common as C
from script import SPEAKERS
from timeline import build, speaking
from reels.script_reels import REEL_SCENES
from reels.scenes_reels import REGISTRY, RW, RH


def reel_chunks(t):
    """Short 1-3 word subtitle chunks (reels style)."""
    words = t.split()
    out, cur = [], []
    for w in words:
        cand = " ".join(cur + [w])
        if cur and (len(cand) > 19 or len(cur) >= 3):
            out.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
        if w[-1] in ".!?," and len(" ".join(cur)) > 6:
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def bounds(scenes):
    return [(a.end, "cut", i) for i, a in enumerate(scenes[:-1])]


class ReelRenderer:
    def __init__(self):
        self.scenes, self.cues = build(REEL_SCENES, chunker=reel_chunks)
        self.total = self.scenes[-1].end
        self.nframes = int(math.ceil(self.total * FPS))
        self.bounds = bounds(self.scenes)

    def scene_at(self, t):
        for s in self.scenes:
            if s.start <= t < s.end:
                return s
        return self.scenes[-1]

    def subtitles(self, ctx, t, y):
        act = [c for c in self.cues if c.start <= t < c.end + 0.05]
        if not act:
            return
        c = act[-1]
        s = c.text.replace("i", "İ").upper()   # Turkish dotted capital İ
        col = "#ffd34a" if c.spk != "NR" else "#ffffff"
        size = 84
        font(ctx, "Nunito Black", size)
        w = text_w(ctx, s)
        if w > 940:
            size = size * 940 / w
        k = max(0.0, ease_back(prog(t, c.start, c.start + 0.12), 2.0))
        ctx.save()
        ctx.translate(RW / 2, y)
        ctx.scale(0.75 + 0.25 * k, 0.75 + 0.25 * k)
        text(ctx, s, 0, size * 0.35, "Nunito Black", size, col, outline="#0d0a08", olw=size * 0.2,
             shadow=(4, 6))
        ctx.restore()

    def draw(self, ctx, f):
        t = f / FPS
        C.G.t, C.G.frame = t, f
        C.G.spk, C.G.mouth = speaking(self.scenes, t)
        S = self.scene_at(t)
        lt = t - S.start
        ctx.save()
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()
        opts = REGISTRY[S.id][0](ctx, S, lt) or {}
        ctx.restore()
        fx.vignette(ctx, RW, RH, 0.45)
        if opts.get("banner", True):
            overlay.banner(ctx, RW / 2, 255, "300 SPARTALIDAN BİRİ OLSAYDIN?", size=40, rot=-0.02)
        self.subtitles(ctx, t, opts.get("sub_y", 1400))
        for B, kind, i in self.bounds:
            d = t - B
            if 0 <= d < 0.14:
                fx.flash(ctx, RW, RH, 0.55 * (1 - d / 0.14), "#ffffff")
        if t > self.total - 0.4:
            fx.flash(ctx, RW, RH, (t - (self.total - 0.4)) / 0.4, "#000000")


_R = None


def _init():
    global _R
    _R = ReelRenderer()


def _render_range(args):
    f0, f1, path = args
    R = _R or ReelRenderer()
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, RW, RH)
    ctx = cairo.Context(surf)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{RW}x{RH}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                          "-pix_fmt", "yuv420p", "-g", str(FPS * 2), path], stdin=subprocess.PIPE)
    t0 = time.time()
    for f in range(f0, f1):
        ctx.save()
        R.draw(ctx, f)
        ctx.restore()
        surf.flush()
        p.stdin.write(surf.get_data())
    p.stdin.close()
    p.wait()
    return f0, f1, time.time() - t0


def render_video(out, workers=4, chunk_sec=6):
    R = ReelRenderer()
    cdir = os.path.join(BUILD, "reel_chunks")
    os.makedirs(cdir, exist_ok=True)
    step = chunk_sec * FPS
    jobs = [(f, min(f + step, R.nframes), os.path.join(cdir, f"r{i:03d}.mp4"))
            for i, f in enumerate(range(0, R.nframes, step))]
    with mp.Pool(workers, initializer=_init) as pool:
        for f0, f1, dt in pool.imap_unordered(_render_range, jobs):
            print(f"  frames {f0}-{f1} in {dt:.0f}s", flush=True)
    lst = os.path.join(cdir, "list.txt")
    with open(lst, "w") as fh:
        for _, _, p in jobs:
            fh.write(f"file '{p}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out],
                   check=True)
    return R


def contact_sheet(out, n=24, cols=6, scale=0.2):
    R = ReelRenderer()
    w, h = int(RW * scale), int(RH * scale)
    rows = (n + cols - 1) // cols
    sheet = cairo.ImageSurface(cairo.FORMAT_ARGB32, w * cols, h * rows)
    sc = cairo.Context(sheet)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, RW, RH)
    ctx = cairo.Context(surf)
    for i in range(n):
        tt = 0.3 + (R.total - 0.6) * i / (n - 1)
        ctx.save()
        R.draw(ctx, int(tt * FPS))
        ctx.restore()
        sc.save()
        sc.translate((i % cols) * w, (i // cols) * h)
        sc.scale(scale, scale)
        sc.set_source_surface(surf, 0, 0)
        sc.paint()
        sc.restore()
        sc.set_source_rgb(1, 1, 0)
        sc.set_font_size(14)
        sc.move_to((i % cols) * w + 4, (i // cols) * h + 16)
        sc.show_text(f"{tt:.1f}s")
    sheet.write_to_png(out)
    return out


if __name__ == "__main__":
    print(contact_sheet(os.path.join(BUILD, "test", "reel_sheet.png")))
