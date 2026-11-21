# -*- coding: utf-8 -*-
"""YouTube thumbnail in the channel's style (split background, big number, red banner, tags)."""
import os
import sys

import cairo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import OUT
from draw import backgrounds as bg
from draw import fx, overlay
from draw.characters import Pose, draw_char, draw_tag, leonidas, spartan, xerxes, immortal
from draw.core import OUT as INK, poly, src, text

W, H = 1920, 1080


def make(path_png, path_jpg):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    # left: stormy arrow sky over the pass
    ctx.save()
    poly(ctx, [(0, 0), (1060, 0), (880, H), (0, H)])
    ctx.clip()
    bg.sky(ctx, 0, 0, W, H, "#2a3448", "#8a7a6a")
    bg.mountains(ctx, 5, -200, 1200, 900, 420, "#5a4a3a", rough=1.2)
    bg.ground(ctx, 0, W, 880, H, "#8a7050", pebbles=False)
    fx.volley(ctx, 1.0, 0.0, 9, 80, (1200, -300, 1400, -200), (-100, 100, 1000, 700), dur=1.6,
              apex=-100, size=1.4, stuck=False, spread=0.6)
    ctx.restore()
    # right: golden Persian camp
    ctx.save()
    poly(ctx, [(1060, 0), (W, 0), (W, H), (880, H)])
    ctx.clip()
    bg.sky(ctx, 0, 0, W, H, "#f0a040", "#ffe6a0")
    bg.sun(ctx, 1600, 260, 90, glow="#ff9a3a")
    bg.mountains(ctx, 31, 800, 2200, 900, 300, "#c08a5a", outline=False)
    bg.ground(ctx, 0, W, 880, H, "#d8b07a", pebbles=False)
    for i, x in enumerate((1150, 1400, 1700)):
        bg.tent(ctx, x, 880, 0.7, c2=["#a8432e", "#2f5f9a", "#c99a2a"][i], flag="#c8202a")
    ctx.restore()
    ctx.move_to(1060, 0)
    ctx.line_to(880, H)
    src(ctx, "#ffffff")
    ctx.set_line_width(16)
    ctx.stroke()

    # characters (big, expressive)
    draw_char(ctx, 470, 1260, 3.3, spartan(1),
              Pose(face=1, t=0.4, grip="ready", shield="front", eyes="angry", mshape="shout",
                   blink=False))
    draw_char(ctx, 1480, 1240, 3.0, xerxes(),
              Pose(face=-1, t=0.4, weapon="none", shield="none", arm=(100, -150), eyes="wide",
                   sweat=True, mshape="o", blink=False))
    # titles
    text(ctx, "300", W / 2 - 30, 300, "Cinzel Black", 300, "#ffd34a", outline="#1a0c06", olw=22,
         shadow=(10, 14))
    overlay.banner(ctx, W / 2 - 20, 420, "SPARTALI OLSAYDIN?", size=92, rot=-0.04)
    draw_tag(ctx, 330, 560, "SPARTALI", s=1.8, rot=-0.08)
    draw_tag(ctx, 1600, 520, "KSERKSES", s=1.8, rot=0.06)
    surf.write_to_png(path_png)
    # 1280x720 jpg for YouTube
    small = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1280, 720)
    c2 = cairo.Context(small)
    c2.scale(1280 / W, 720 / H)
    c2.set_source_surface(surf, 0, 0)
    c2.paint()
    tmp = path_jpg + ".png"
    small.write_to_png(tmp)
    os.system(f"ffmpeg -v error -y -i {tmp} -q:v 2 {path_jpg} && rm {tmp}")
    return path_png


if __name__ == "__main__":
    print(make(os.path.join(OUT, "thumbnail.png"), os.path.join(OUT, "thumbnail.jpg")))
