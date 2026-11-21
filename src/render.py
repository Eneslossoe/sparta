# -*- coding: utf-8 -*-
"""Frame renderer: scenes -> transitions -> overlays -> ffmpeg."""
import argparse
import math
import multiprocessing as mp
import os
import subprocess
import sys
import time

import cairo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import BUILD, FPS, H, W
from draw import fx, overlay
from draw.core import clamp, ease, prog
from scenes import REGISTRY
from scenes.common import G
from script import SPEAKERS
from timeline import CHAPTER_CARD, build, speaking

# transition between consecutive scenes (default: crack if the next scene opens a
# chapter, otherwise a short dip to black)
TRANS = {
    ("cold_open", "title"): "cut",
    ("title", "birth"): "whitein",
    ("march", "pass"): "fade",
    ("day1", "immortals"): "cut",
    ("final", "survivor"): "slowfade",
    ("survivor", "aftermath"): "fade",
    ("aftermath", "outro"): "slowfade",
}


def boundaries(scenes):
    out = []
    for i, (a, b) in enumerate(zip(scenes, scenes[1:])):
        kind = TRANS.get((a.id, b.id)) or ("crack" if b.chapter else "fade")
        out.append((a.end, kind, i))
    return out


class Renderer:
    def __init__(self):
        self.scenes, self.cues = build()
        self.bounds = boundaries(self.scenes)
        self.total = self.scenes[-1].end
        self.nframes = int(math.ceil(self.total * FPS))

    def scene_at(self, t):
        for s in self.scenes:
            if s.start <= t < s.end:
                return s
        return self.scenes[-1]

    def draw(self, ctx, f):
        t = f / FPS
        G.t, G.frame = t, f
        G.spk, G.mouth = speaking(self.scenes, t)
        S = self.scene_at(t)
        lt = t - S.start
        src_ = REGISTRY[S.id][0]
        ctx.save()
        ctx.rectangle(0, 0, W, H)
        ctx.set_source_rgb(0, 0, 0)
        ctx.fill()
        opts = src_(ctx, S, lt) or {}
        ctx.restore()

        lb = opts.get("letterbox", 0.0)
        fx.letterbox(ctx, W, H, lb)
        if opts.get("vignette", 0.5):
            fx.vignette(ctx, W, H, opts.get("vignette", 0.5))
        if S.chapter:
            overlay.chapter_card(ctx, W, H, S.chapter, lt - (S.first_beat - CHAPTER_CARD),
                                 CHAPTER_CARD)
        if not opts.get("no_subs"):
            overlay.subtitles(ctx, W, H, self.cues, t, SPEAKERS,
                              bottom=H - 70 - (40 * ease(lb) if lb else 0))
        for B, kind, i in self.bounds:
            d = t - B
            if kind == "fade" and abs(d) < 0.28:
                fx.flash(ctx, W, H, 1 - abs(d) / 0.28, "#000000")
            elif kind == "slowfade" and -1.0 < d < 0.9:
                fx.flash(ctx, W, H, (1 + d / 1.0) if d < 0 else 1 - d / 0.9, "#000000")
            elif kind == "crack" and -0.5 < d < 0.45:
                fx.crack(ctx, W, H, (d + 0.5) / 0.95, seed=7 + i)
            elif kind == "whitein" and 0 <= d < 0.6:
                fx.flash(ctx, W, H, 1 - d / 0.6, "#fff6e0")
        # global fade in / out
        if t < 0.05:
            fx.flash(ctx, W, H, 1, "#000000")
        if t > self.total - 1.2:
            fx.flash(ctx, W, H, (t - (self.total - 1.2)) / 1.2, "#000000")



_R = None


def _init():
    global _R
    _R = Renderer()


def render_range(args):
    f0, f1, path = args
    R = _R or Renderer()
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-g", str(FPS * 2), path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
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


def render_video(out, workers=4, chunk_sec=20, t0=0.0, t1=None):
    R = Renderer()
    f_start = int(t0 * FPS)
    f_end = R.nframes if t1 is None else min(R.nframes, int(t1 * FPS))
    cdir = os.path.join(BUILD, "chunks")
    os.makedirs(cdir, exist_ok=True)
    jobs = []
    step = chunk_sec * FPS
    for i, f in enumerate(range(f_start, f_end, step)):
        jobs.append((f, min(f + step, f_end), os.path.join(cdir, f"c{i:04d}.mp4")))
    print(f"rendering {f_end - f_start} frames in {len(jobs)} chunks on {workers} workers", flush=True)
    t_start = time.time()
    with mp.Pool(workers, initializer=_init) as pool:
        for f0, f1, dt in pool.imap_unordered(render_range, jobs):
            print(f"  frames {f0}-{f1} done in {dt:.0f}s ({(f1 - f0) / dt:.1f} fps)", flush=True)
    lst = os.path.join(cdir, "list.txt")
    with open(lst, "w") as fh:
        for _, _, p in jobs:
            fh.write(f"file '{p}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", out], check=True)
    print(f"video -> {out} ({time.time() - t_start:.0f}s)")
    return R


def stills(times, outdir):
    R = Renderer()
    os.makedirs(outdir, exist_ok=True)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    paths = []
    for tt in times:
        f = int(tt * FPS)
        ctx.save()
        t0 = time.time()
        R.draw(ctx, f)
        ctx.restore()
        p = os.path.join(outdir, f"still_{tt:07.2f}.png")
        surf.write_to_png(p)
        paths.append(p)
        print(p, f"{(time.time() - t0) * 1000:.0f}ms")
    return paths


def contact_sheet(times, out, cols=4, scale=0.25):
    R = Renderer()
    w, h = int(W * scale), int(H * scale)
    rows = (len(times) + cols - 1) // cols
    sheet = cairo.ImageSurface(cairo.FORMAT_ARGB32, w * cols, h * rows)
    sc = cairo.Context(sheet)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    for i, tt in enumerate(times):
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
        sc.select_font_face("DejaVu Sans")
        sc.set_font_size(14)
        sc.move_to((i % cols) * w + 6, (i // cols) * h + 18)
        sc.show_text(f"{tt:.1f}s")
    sheet.write_to_png(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", help="contact sheet of one scene")
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--at", type=float, nargs="*")
    ap.add_argument("--video", help="output mp4 (no audio)")
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--t1", type=float, default=None)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    out = os.path.join(BUILD, "test")
    if a.scene:
        R = Renderer()
        S = [s for s in R.scenes if s.id == a.scene][0]
        ts = [S.start + 0.05 + (S.dur - 0.1) * i / (a.n - 1) for i in range(a.n)]
        print(contact_sheet(ts, os.path.join(out, f"sheet_{a.scene}.png")))
    elif a.at:
        stills(a.at, out)
    elif a.video:
        render_video(a.video, a.workers, t0=a.t0, t1=a.t1)
