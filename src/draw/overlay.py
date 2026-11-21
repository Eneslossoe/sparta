# -*- coding: utf-8 -*-
"""Screen-space overlays: subtitles, chapter cards, captions, channel logo."""
import math

import cairo

from .core import (OUT, PI, TAU, circle, clamp, ease, ease_back, ease_out, ellipse, fill_stroke,
                   font, hx, lin_grad, poly, prog, rad_grad, rrect, shade, src, text, text_w)

SUB_FONT = "Nunito Black"
TITLE_FONT = "Cinzel Black"
TITLE_FONT2 = "Cinzel"
TAG_FONT = "Baloo 2 ExtraBold"


def subtitles(ctx, W, H, cues, t, speakers, bottom=None, scale=1.0):
    active = [c for c in cues if c.start <= t < c.end + 0.08]
    if not active:
        return
    c = active[-1]
    col = speakers.get(c.spk, (None, None))[1] or "#ffffff"
    lines = c.text.split("\n")
    size = 50 * scale
    lh = size * 1.18
    base = (bottom if bottom is not None else H - 70) - (len(lines) - 1) * lh
    # fade in/out a touch
    a = clamp(min((t - c.start) / 0.08, (c.end + 0.08 - t) / 0.08, 1.0))
    for i, ln in enumerate(lines):
        text(ctx, ln, W / 2, base + i * lh, SUB_FONT, size, col, outline="#0d0a08",
             olw=10 * scale, alpha=a, shadow=(3, 4))


def chapter_card(ctx, W, H, title, lt, dur=2.3):
    if lt < 0 or lt > dur:
        return
    a_in = ease_out(prog(lt, 0.0, 0.45))
    a_out = 1 - ease(prog(lt, dur - 0.45, dur))
    a = a_in * a_out
    if a <= 0:
        return
    # dim scene
    src(ctx, (0, 0, 0, 0.45 * a))
    ctx.rectangle(0, 0, W, H)
    ctx.fill()
    if ". " in title:
        num, name = title.split(". ", 1)
    else:
        num, name = "", title
    cy = H / 2
    bw = 1500 * a_in
    ctx.set_source(lin_grad(W / 2 - bw / 2, 0, W / 2 + bw / 2, 0,
                            [(0, (0.05, 0.03, 0.02, 0)), (0.2, (0.08, 0.05, 0.03, 0.85 * a)),
                             (0.8, (0.08, 0.05, 0.03, 0.85 * a)), (1, (0.05, 0.03, 0.02, 0))]))
    ctx.rectangle(W / 2 - bw / 2, cy - 120, bw, 240)
    ctx.fill()
    for yy in (cy - 120, cy + 120):
        ctx.set_source(lin_grad(W / 2 - bw / 2, 0, W / 2 + bw / 2, 0,
                                [(0, (0.85, 0.65, 0.3, 0)), (0.5, (0.95, 0.75, 0.35, a)),
                                 (1, (0.85, 0.65, 0.3, 0))]))
        ctx.rectangle(W / 2 - bw / 2, yy - 2, bw, 4)
        ctx.fill()
    dy = (1 - a_in) * 30
    if num:
        text(ctx, "BÖLÜM " + num, W / 2, cy - 42 + dy, TITLE_FONT2, 38, "#e9c27a", alpha=a,
             spacing=6)
    size = 92 if len(name) < 16 else 72
    text(ctx, name, W / 2, cy + 58 + dy, TITLE_FONT, size, "#f6e3b4", outline="#2a1a0c", olw=6,
         alpha=a, shadow=(4, 5), spacing=3)


def caption(ctx, W, H, s, lt, t0=0.0, t1=99.0, x=80, y=None):
    """Typewriter caption box, lower-left."""
    if lt < t0 or lt > t1:
        return
    y = H - 210 if y is None else y
    n = int(clamp((lt - t0) / 1.2) * len(s) + 0.999)
    a = clamp((t1 - lt) / 0.4) * clamp((lt - t0) / 0.2)
    shown = s[:n]
    font(ctx, TITLE_FONT, 44)
    w = text_w(ctx, s) + 60
    rrect(ctx, x, y - 54, w, 76, 6)
    src(ctx, (0.05, 0.03, 0.02, 0.75 * a))
    ctx.fill()
    ctx.rectangle(x, y - 54, 8, 76)
    src(ctx, (0.85, 0.2, 0.15, a))
    ctx.fill()
    text(ctx, shown, x + 34, y, TITLE_FONT, 44, "#f6e3b4", align="left", alpha=a)


def hourglass(ctx, x, y, s, t, crack_p=0.0, alpha=1.0, flow=True):
    """Channel-style logo: hourglass in a dark medallion."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.push_group()
    ctx.set_source(rad_grad(0, 0, 0, 230, [(0, "#3a2a1c"), (0.8, "#1c130d"), (1, "#0e0a07")]))
    circle(ctx, 0, 0, 220)
    ctx.fill()
    circle(ctx, 0, 0, 220)
    src(ctx, "#b8873e")
    ctx.set_line_width(8)
    ctx.stroke()
    circle(ctx, 0, 0, 200)
    src(ctx, "#6b4a22")
    ctx.set_line_width(3)
    ctx.stroke()
    # glass
    glass = [(-70, -120), (70, -120), (62, -80), (14, -12), (14, 12), (62, 80), (70, 120),
             (-70, 120), (-62, 80), (-14, 12), (-14, -12), (-62, -80)]
    poly(ctx, glass)
    src(ctx, (0.85, 0.9, 1.0, 0.18))
    ctx.fill_preserve()
    src(ctx, "#e8d8b0")
    ctx.set_line_width(4)
    ctx.stroke()
    # sand
    level = (t * 0.05) % 1.0 if flow else 0.35
    top_h = 70 * (1 - level)
    poly(ctx, [(-58 * (top_h / 70) - 8, -12 - top_h), (58 * (top_h / 70) + 8, -12 - top_h), (10, -14),
               (-10, -14)])
    src(ctx, "#e7b55a")
    ctx.fill()
    bh = 20 + 60 * level
    poly(ctx, [(-66, 118), (66, 118), (10, 118 - bh), (-10, 118 - bh)])
    src(ctx, "#e7b55a")
    ctx.fill()
    if flow:
        ctx.rectangle(-2, -14, 4, 132 - bh)
        src(ctx, "#f0c46a")
        ctx.fill()
    # Spartan helmet silhouette in the upper bulb
    ctx.save()
    ctx.translate(0, -62)
    ctx.scale(0.42, 0.42)
    ctx.move_to(-60, 40); ctx.curve_to(-70, -60, 60, -70, 62, 0); ctx.line_to(62, 50)
    ctx.line_to(20, 50); ctx.line_to(20, 0); ctx.line_to(-4, 0); ctx.line_to(-4, 50)
    ctx.close_path()
    src(ctx, "#2a1a0c", 0.75)
    ctx.fill()
    ctx.move_to(-70, -40); ctx.curve_to(-50, -110, 40, -110, 70, -50)
    ctx.set_line_width(22)
    src(ctx, "#a8222b", 0.85)
    ctx.stroke()
    ctx.restore()
    # frame
    for yy in (-128, 128):
        rrect(ctx, -95, yy - 12, 190, 24, 6)
        fill_stroke(ctx, "#b8873e", 4, "#3a2410")
    for xx in (-86, 86):
        rrect(ctx, xx - 7, -118, 14, 236, 5)
        fill_stroke(ctx, "#a07030", 3.5, "#3a2410")
    # the crack
    if crack_p > 0:
        L = crack_p
        pts = [(-60, -100), (-20, -60), (-36, -30), (10, 10), (-6, 40), (40, 90), (58, 110)]
        ctx.move_to(*pts[0])
        n = max(1, int(L * (len(pts) - 1)))
        for p in pts[1:n + 1]:
            ctx.line_to(*p)
        src(ctx, "#ffffff")
        ctx.set_line_width(3)
        ctx.stroke()
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(alpha)
    ctx.restore()


def logo_text(ctx, x, y, s=1.0, alpha=1.0):
    text(ctx, "ZAMAN", x, y, TITLE_FONT, 90 * s, "#e9d3a0", outline="#2a1a0c", olw=6 * s,
         alpha=alpha, spacing=8 * s, shadow=(3, 4))
    text(ctx, "KIRIĞI", x, y + 70 * s, TITLE_FONT, 56 * s, "#d9a347", outline="#2a1a0c", olw=5 * s,
         alpha=alpha, spacing=14 * s)


def banner(ctx, x, y, label, size=46, rot=-0.03, fill="#c8202a", fg="#ffffff", alpha=1.0, s=1.0):
    """Red banner like the thumbnail ('İSTANBUL HALKI OLSAYDIN?')."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    font(ctx, TAG_FONT, size)
    w = text_w(ctx, label) + 50
    h = size * 1.35
    poly(ctx, [(-w / 2 - 18, -h / 2), (w / 2 + 18, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)])
    fill_stroke(ctx, fill, 5, alpha=alpha)
    text(ctx, label, 0, size * 0.36, TAG_FONT, size, fg, alpha=alpha)
    ctx.restore()


def bubble(ctx, x, y, label, size=40, alpha=1.0, tail=(-40, 50), s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    font(ctx, TAG_FONT, size)
    w = text_w(ctx, label) + 50
    h = size * 1.5
    rrect(ctx, -w / 2, -h / 2, w, h, h / 2)
    ctx.move_to(-12, h / 2 - 2)
    ctx.line_to(tail[0], tail[1])
    ctx.line_to(14, h / 2 - 2)
    fill_stroke(ctx, "#ffffff", 4, alpha=alpha)
    text(ctx, label, 0, size * 0.35, TAG_FONT, size, "#1a1410", alpha=alpha)
    ctx.restore()
