# -*- coding: utf-8 -*-
"""Low-level cairo helpers: colours, shapes, easing, text, camera."""
import math
import random

import cairo

OUT = (0.10, 0.08, 0.07)     # ink colour used for all outlines
PI = math.pi
TAU = 2 * math.pi


# ----------------------------------------------------------------- colour
def hx(h, a=1.0):
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


def mix(c1, c2, t):
    c1 = hx(c1) if isinstance(c1, str) else c1
    c2 = hx(c2) if isinstance(c2, str) else c2
    if len(c1) == 3:
        c1 = (*c1, 1.0)
    if len(c2) == 3:
        c2 = (*c2, 1.0)
    return tuple(a + (b - a) * t for a, b in zip(c1, c2))


def shade(c, k):
    """k<0 darker, k>0 lighter."""
    c = hx(c) if isinstance(c, str) else c
    if k < 0:
        return mix(c, (0, 0, 0, c[3] if len(c) > 3 else 1), -k)
    return mix(c, (1, 1, 1, c[3] if len(c) > 3 else 1), k)


def src(ctx, c, a=None):
    c = hx(c) if isinstance(c, str) else c
    if len(c) == 3:
        c = (*c, 1.0)
    if a is not None:
        c = (c[0], c[1], c[2], c[3] * a)
    ctx.set_source_rgba(*c)


# ----------------------------------------------------------------- math / easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def prog(t, t0, t1):
    """0..1 progress of t inside [t0, t1]."""
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0))


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t ** 3


def ease_back(t, s=1.7):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def bounce(t):
    t = clamp(t)
    return abs(math.sin(t * PI * 2.5)) * (1 - t)


def pulse(t, freq=1.0):
    return 0.5 + 0.5 * math.sin(t * TAU * freq)


def rng(seed):
    return random.Random(seed)


def noise1(x, seed=0):
    """Cheap smooth 1D value noise in [-1, 1]."""
    i = math.floor(x)
    f = x - i
    def h(n):
        n = (n * 374761393 + seed * 668265263) & 0xFFFFFFFF
        n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
        return ((n ^ (n >> 16)) & 0xFFFF) / 32767.5 - 1
    u = f * f * (3 - 2 * f)
    return h(i) * (1 - u) + h(i + 1) * u


# ----------------------------------------------------------------- shapes
def fill_stroke(ctx, fill, lw=4.0, stroke=OUT, alpha=None):
    if fill is not None:
        src(ctx, fill, alpha)
        if lw and stroke is not None:
            ctx.fill_preserve()
        else:
            ctx.fill()
    if lw and stroke is not None:
        src(ctx, stroke, alpha)
        ctx.set_line_width(lw)
        ctx.stroke()
    else:
        ctx.new_path()


def ellipse(ctx, x, y, rx, ry):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(max(rx, 1e-3), max(ry, 1e-3))
    ctx.arc(0, 0, 1, 0, TAU)
    ctx.restore()


def circle(ctx, x, y, r):
    ctx.arc(x, y, r, 0, TAU)


def rrect(ctx, x, y, w, h, r):
    r = min(r, abs(w) / 2, abs(h) / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -PI / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, PI / 2)
    ctx.arc(x + r, y + h - r, r, PI / 2, PI)
    ctx.arc(x + r, y + r, r, PI, 3 * PI / 2)
    ctx.close_path()


def poly(ctx, pts, close=True):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if close:
        ctx.close_path()


def smooth_poly(ctx, pts, close=True, k=0.5):
    """Catmull-Rom style smooth path through points."""
    n = len(pts)
    if n < 3:
        poly(ctx, pts, close)
        return
    P = pts + pts[:2] if close else [pts[0]] + pts + [pts[-1]]
    ctx.move_to(*P[1] if close else pts[0])
    rng_ = range(1, n + 1) if close else range(1, n)
    for i in rng_:
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[(i + 2) % len(P)] if close else P[min(i + 2, len(P) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 3, p1[1] + (p2[1] - p0[1]) * k / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 3, p2[1] - (p3[1] - p1[1]) * k / 3)
        ctx.curve_to(*c1, *c2, *p2)
    if close:
        ctx.close_path()


def limb(ctx, pts, color, w, lw=4.0, cap=cairo.LINE_CAP_ROUND):
    """Thick outlined stroke (arms, legs, spear shafts)."""
    ctx.set_line_cap(cap)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    poly(ctx, pts, close=False)
    if lw:
        src(ctx, OUT)
        ctx.set_line_width(w + lw * 2)
        ctx.stroke_preserve()
    src(ctx, color)
    ctx.set_line_width(w)
    ctx.stroke()


def lin_grad(x0, y0, x1, y1, stops):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for off, c in stops:
        c = hx(c) if isinstance(c, str) else c
        if len(c) == 3:
            c = (*c, 1.0)
        g.add_color_stop_rgba(off, *c)
    return g


def rad_grad(x, y, r0, r1, stops, x1=None, y1=None):
    g = cairo.RadialGradient(x, y, r0, x if x1 is None else x1, y if y1 is None else y1, r1)
    for off, c in stops:
        c = hx(c) if isinstance(c, str) else c
        if len(c) == 3:
            c = (*c, 1.0)
        g.add_color_stop_rgba(off, *c)
    return g


# ----------------------------------------------------------------- text
_FACE_CACHE = {}


def font(ctx, family, size, bold=False):
    ctx.select_font_face(family, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)


def text_w(ctx, s):
    return ctx.text_extents(s).x_advance


def text(ctx, s, x, y, family, size, color="#ffffff", align="center", outline=None,
         olw=0, alpha=1.0, shadow=None, spacing=0.0):
    """Draw text with optional outline + drop shadow. y = baseline."""
    font(ctx, family, size)
    if spacing:
        widths = [ctx.text_extents(ch).x_advance + spacing for ch in s]
        w = sum(widths) - spacing
    else:
        w = ctx.text_extents(s).x_advance
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)

    def path():
        ctx.new_path()
        if spacing:
            cx = x0
            for ch, cw in zip(s, widths):
                ctx.move_to(cx, y)
                ctx.text_path(ch)
                cx += cw
        else:
            ctx.move_to(x0, y)
            ctx.text_path(s)

    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    if shadow:
        ctx.save()
        ctx.translate(*shadow[:2])
        path()
        if outline:
            ctx.set_line_width(olw)
            src(ctx, (0, 0, 0, 0.45 * alpha))
            ctx.stroke_preserve()
        src(ctx, (0, 0, 0, 0.45 * alpha))
        ctx.fill()
        ctx.restore()
    path()
    if outline:
        ctx.set_line_width(olw)
        src(ctx, outline, alpha)
        ctx.stroke_preserve()
    src(ctx, color, alpha)
    ctx.fill()
    return w


# ----------------------------------------------------------------- camera
class Cam:
    """World->screen transform: centre (x, y) and zoom, plus shake."""

    def __init__(self, x=960, y=540, zoom=1.0, rot=0.0):
        self.x, self.y, self.zoom, self.rot = x, y, zoom, rot

    def apply(self, ctx, W=1920, H=1080, shake=0.0, t=0.0):
        sx = sy = 0.0
        if shake:
            sx = noise1(t * 31, 1) * shake
            sy = noise1(t * 29, 2) * shake
        ctx.translate(W / 2 + sx, H / 2 + sy)
        if self.rot:
            ctx.rotate(self.rot)
        ctx.scale(self.zoom, self.zoom)
        ctx.translate(-self.x, -self.y)


def cam_lerp(a, b, t):
    return Cam(lerp(a.x, b.x, t), lerp(a.y, b.y, t), a.zoom * (b.zoom / a.zoom) ** t,
               lerp(a.rot, b.rot, t))
