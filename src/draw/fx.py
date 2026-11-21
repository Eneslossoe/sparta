# -*- coding: utf-8 -*-
"""Particles & camera effects: arrows, sparks, dust, crack transition, grain..."""
import math

import cairo
import numpy as np

from .core import (OUT, PI, TAU, circle, clamp, ease, ease_out, ellipse, fill_stroke, hx,
                   lerp, limb, noise1, poly, rad_grad, rng, src, prog)


# ---------------------------------------------------------------- arrows
def draw_arrow(ctx, x, y, ang, size=1.0, color="#6b4a2a", alpha=1.0, length=52):
    ca, sa = math.cos(ang), math.sin(ang)
    L = length * size
    tail = (x - ca * L, y - sa * L)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(*tail)
    ctx.line_to(x, y)
    src(ctx, OUT, alpha)
    ctx.set_line_width(4.5 * size)
    ctx.stroke()
    ctx.move_to(*tail)
    ctx.line_to(x, y)
    src(ctx, color, alpha)
    ctx.set_line_width(2.2 * size)
    ctx.stroke()
    h = 9 * size
    poly(ctx, [(x + ca * h, y + sa * h), (x - ca * 3 * size - sa * 5 * size, y - sa * 3 * size + ca * 5 * size),
               (x - ca * 3 * size + sa * 5 * size, y - sa * 3 * size - ca * 5 * size)])
    src(ctx, "#3a3a3a", alpha)
    ctx.fill()
    f = 10 * size
    for k in (-1, 1):
        ctx.move_to(tail[0] + ca * f, tail[1] + sa * f)
        ctx.line_to(tail[0] - sa * 6 * size * k, tail[1] + ca * 6 * size * k)
    src(ctx, "#e8e0d0", alpha)
    ctx.set_line_width(2.5 * size)
    ctx.stroke()


def volley(ctx, t, t0, seed, n, src_box, dst_box, dur=1.7, apex=700, size=1.0, stuck=True,
           spread=0.7, stuck_len=0.55, max_stuck_time=99.0):
    """Arrows on parabolas from src_box to dst_box. Returns number of arrows that just landed."""
    r = rng(seed)
    landed = []
    for i in range(n):
        delay = r.random() * spread
        sx = r.uniform(src_box[0], src_box[2]); sy = r.uniform(src_box[1], src_box[3])
        dx = r.uniform(dst_box[0], dst_box[2]); dy = r.uniform(dst_box[1], dst_box[3])
        d = dur * (0.85 + 0.3 * r.random())
        ap = apex * (0.8 + 0.4 * r.random())
        T = t - t0 - delay
        if T < 0:
            continue
        if T < d:
            u = T / d
            x = sx + (dx - sx) * u
            y = sy + (dy - sy) * u - ap * 4 * u * (1 - u)
            vx = (dx - sx) / d
            vy = (dy - sy) / d - ap * 4 * (1 - 2 * u) / d
            draw_arrow(ctx, x, y, math.atan2(vy, vx), size)
        elif stuck and T - d < max_stuck_time:
            vx = (dx - sx) / d
            vy = (dy - sy) / d + ap * 4 / d
            a = math.atan2(vy, vx)
            draw_arrow(ctx, dx + math.cos(a) * 14 * size, dy + math.sin(a) * 14 * size, a, size,
                       length=52 * stuck_len)
            landed.append((dx, dy))
    return landed


def arrow_cloud(ctx, t, x0, x1, y0, y1, density=1.0, seed=3, alpha=1.0, ang=0.35, speed=900,
                size=0.7):
    """Dense band of arrows streaking across the sky (the 'darkened sun' shot)."""
    r = rng(seed)
    n = int(160 * density)
    ca, sa = math.cos(ang), math.sin(ang)
    w = x1 - x0
    for i in range(n):
        ox = r.uniform(0, w)
        oy = r.uniform(y0, y1)
        sp = speed * (0.8 + 0.4 * r.random())
        x = x0 + (ox + t * sp * ca) % w
        y = oy + ((ox + t * sp * ca) // w) * 0 + (t * sp * sa) % (y1 - y0 + 1) * 0
        draw_arrow(ctx, x, y, ang, size * (0.7 + 0.5 * r.random()), alpha=alpha)


# ---------------------------------------------------------------- impacts
def sparks(ctx, x, y, age, seed=0, n=10, size=1.0, color="#fff3a0"):
    if age < 0 or age > 0.4:
        return
    r = rng(seed)
    k = age / 0.4
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(n):
        a = r.uniform(0, TAU)
        sp = r.uniform(60, 160) * size
        d0 = sp * k
        d1 = sp * k + 18 * size * (1 - k)
        ctx.move_to(x + math.cos(a) * d0, y + math.sin(a) * d0)
        ctx.line_to(x + math.cos(a) * d1, y + math.sin(a) * d1)
    src(ctx, color, 1 - k)
    ctx.set_line_width(4 * size)
    ctx.stroke()
    if k < 0.35:
        circle(ctx, x, y, 22 * size * (1 - k))
        src(ctx, (1, 1, 0.85, 0.8 * (1 - k / 0.35)))
        ctx.fill()


def pow_star(ctx, x, y, age, size=1.0, color="#ffe14a", dur=0.45):
    if age < 0 or age > dur:
        return
    k = age / dur
    s = ease_out(min(1, k * 3)) * size * (1 - 0.3 * k)
    pts = []
    for i in range(16):
        a = i * TAU / 16
        rr = (46 if i % 2 == 0 else 22) * s
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    poly(ctx, pts)
    fill_stroke(ctx, color, 4 * s, alpha=1 - k)


def dust(ctx, x, y, age, seed=0, n=6, size=1.0, color=(0.85, 0.78, 0.62), life=1.2):
    if age < 0 or age > life:
        return
    r = rng(seed)
    k = age / life
    for i in range(n):
        a = r.uniform(PI * 1.05, PI * 1.95)
        sp = r.uniform(40, 110) * size
        px = x + math.cos(a) * sp * ease_out(k)
        py = y + math.sin(a) * sp * 0.5 * ease_out(k)
        circle(ctx, px, py, (14 + 30 * k) * size * r.uniform(0.7, 1.2))
        src(ctx, (*color, 0.55 * (1 - k)))
        ctx.fill()


def dust_cloud(ctx, x0, x1, y, t, seed=0, alpha=0.5, h=80, color=(0.82, 0.74, 0.58)):
    r = rng(seed)
    for i in range(int((x1 - x0) / 40)):
        px = r.uniform(x0, x1) + noise1(t * 0.5 + i, seed) * 30
        py = y - r.uniform(0, h)
        rr = r.uniform(30, 70)
        circle(ctx, px, py, rr)
        src(ctx, (*color, alpha * r.uniform(0.3, 0.8)))
        ctx.fill()


def speed_lines(ctx, cx, cy, t, alpha=0.5, n=60, r0=380, r1=1400, seed=2, color=(1, 1, 1)):
    r = rng(seed)
    for i in range(n):
        a = r.uniform(0, TAU) + t * 0.05
        w = r.uniform(0.004, 0.012)
        rr0 = r0 * r.uniform(0.9, 1.3) + noise1(t * 6 + i, seed) * 40
        poly(ctx, [(cx + math.cos(a - w) * r1, cy + math.sin(a - w) * r1),
                   (cx + math.cos(a) * rr0, cy + math.sin(a) * rr0),
                   (cx + math.cos(a + w) * r1, cy + math.sin(a + w) * r1)])
        src(ctx, (*color, alpha))
        ctx.fill()


def particles(ctx, t, x0, y0, x1, y1, n=80, seed=5, kind="snow", alpha=1.0):
    r = rng(seed)
    w, h = x1 - x0, y1 - y0
    for i in range(n):
        ox, oy = r.uniform(0, w), r.uniform(0, h)
        sp = r.uniform(0.6, 1.4)
        if kind == "snow":
            x = x0 + (ox + noise1(t * 0.6 + i, seed) * 40) % w
            y = y0 + (oy + t * 70 * sp) % h
            circle(ctx, x, y, 3 + 3 * sp)
            src(ctx, (1, 1, 1, 0.85 * alpha))
            ctx.fill()
        elif kind == "embers":
            x = x0 + (ox + t * 20 * sp + noise1(t + i, seed) * 30) % w
            y = y1 - (oy + t * 90 * sp) % h
            circle(ctx, x, y, 2 + 2 * sp)
            src(ctx, (1, 0.6 + 0.3 * r.random(), 0.2, alpha * (0.5 + 0.5 * math.sin(t * 5 + i))))
            ctx.fill()
        elif kind == "sand":
            x = x0 + (ox + t * 40 * sp) % w
            y = y0 + (oy + noise1(t * 0.5 + i, seed) * 30) % h
            circle(ctx, x, y, 1.5 + 1.5 * sp)
            src(ctx, (1, 0.85, 0.55, 0.5 * alpha))
            ctx.fill()
        elif kind == "petals":
            x = x0 + (ox + t * 30 * sp) % w
            y = y0 + (oy + t * 40 * sp) % h
            ellipse(ctx, x, y, 6, 3)
            src(ctx, (1, 1, 0.95, 0.6 * alpha))
            ctx.fill()


# ---------------------------------------------------------------- screen effects
_VIG = {}
_GRAIN = []


def vignette(ctx, W, H, strength=0.55):
    key = (W, H)
    if key not in _VIG:
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        c = cairo.Context(s)
        c.set_source(rad_grad(W / 2, H / 2, H * 0.35, W * 0.75,
                              [(0, (0, 0, 0, 0)), (0.7, (0, 0, 0, 0.45)), (1, (0, 0, 0, 0.9))]))
        c.paint()
        _VIG[key] = s
    ctx.set_source_surface(_VIG[key], 0, 0)
    ctx.paint_with_alpha(strength)


def grain(ctx, W, H, frame, strength=0.06):
    if not _GRAIN:
        r = np.random.default_rng(1)
        for i in range(6):
            w2, h2 = W // 2, H // 2
            v = r.integers(0, 255, (h2, w2), dtype=np.uint8)
            arr = np.zeros((h2, w2, 4), np.uint8)
            arr[..., 0] = v; arr[..., 1] = v; arr[..., 2] = v; arr[..., 3] = 255
            s = cairo.ImageSurface.create_for_data(memoryview(arr), cairo.FORMAT_ARGB32, w2, h2)
            _GRAIN.append((s, arr))
    s, _ = _GRAIN[frame % len(_GRAIN)]
    ctx.save()
    ctx.scale(2, 2)
    ctx.set_source_surface(s, 0, 0)
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.paint_with_alpha(strength)
    ctx.restore()


def letterbox(ctx, W, H, amount, size=110):
    if amount <= 0:
        return
    h = size * ease(amount)
    src(ctx, "#000000")
    ctx.rectangle(0, 0, W, h)
    ctx.rectangle(0, H - h, W, h)
    ctx.fill()


def flash(ctx, W, H, a, color="#ffffff"):
    if a <= 0:
        return
    src(ctx, color, clamp(a))
    ctx.rectangle(0, 0, W, H)
    ctx.fill()


def tint(ctx, W, H, color, a, op=cairo.OPERATOR_MULTIPLY):
    if a <= 0:
        return
    ctx.save()
    ctx.set_operator(op)
    src(ctx, color, a)
    ctx.rectangle(0, 0, W, H)
    ctx.fill()
    ctx.restore()


_CRACKS = {}


def _crack_net(seed, cx, cy):
    r = rng(seed)
    segs = []
    def walk(x, y, a, length, depth, d0):
        pts = [(x, y, d0)]
        d = d0
        while length > 0:
            st = r.uniform(30, 70)
            a += r.uniform(-0.35, 0.35)
            x += math.cos(a) * st
            y += math.sin(a) * st
            d += st
            length -= st
            pts.append((x, y, d))
            if depth < 2 and r.random() < 0.18:
                walk(x, y, a + r.choice((-1, 1)) * r.uniform(0.5, 1.1), length * 0.6, depth + 1, d)
        segs.append(pts)
    for i in range(14):
        walk(cx, cy, i * TAU / 14 + r.uniform(-0.2, 0.2), r.uniform(900, 1500), 0, 0)
    # concentric rings
    rings = []
    for rr in (90, 200, 340):
        pts = []
        for i in range(15):
            a = i * TAU / 14
            q = rr * r.uniform(0.85, 1.15)
            pts.append((cx + math.cos(a) * q, cy + math.sin(a) * q, rr))
        rings.append(pts)
    return segs, rings


def crack(ctx, W, H, p, seed=7, cx=None, cy=None):
    """'Zaman Kırığı' glass-crack transition. p: 0..1."""
    if p <= 0 or p >= 1:
        return
    cx = W / 2 if cx is None else cx
    cy = H / 2 if cy is None else cy
    key = (seed, cx, cy)
    if key not in _CRACKS:
        _CRACKS[key] = _crack_net(seed, cx, cy)
    segs, rings = _CRACKS[key]
    grow = ease_out(prog(p, 0.0, 0.45)) * 1600
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for lw, col in ((7, (0, 0, 0, 0.55)), (2.5, (1, 1, 1, 0.95))):
        for pts in segs:
            ctx.move_to(pts[0][0], pts[0][1])
            for (x, y, d) in pts[1:]:
                if d > grow:
                    break
                ctx.line_to(x, y)
            ctx.new_sub_path()
        for ring in rings:
            if ring[0][2] * 3 < grow:
                poly(ctx, [(x, y) for x, y, _ in ring])
        src(ctx, col)
        ctx.set_line_width(lw)
        ctx.stroke()
    fl = prog(p, 0.42, 0.55) * (1 - prog(p, 0.6, 1.0))
    if fl > 0:
        flash(ctx, W, H, fl, "#fff6e0")
    glow = prog(p, 0.1, 0.45) * (1 - prog(p, 0.5, 0.6))
    if glow > 0:
        ctx.set_source(rad_grad(cx, cy, 0, 300, [(0, (1, 0.95, 0.8, 0.7 * glow)), (1, (1, 0.9, 0.7, 0))]))
        circle(ctx, cx, cy, 300)
        ctx.fill()


def volley_land_times(seed, n, dur=1.7, spread=0.7):
    """Landing times (relative to volley start) matching volley()'s random sequence."""
    r = rng(seed)
    out = []
    for i in range(n):
        delay = r.random() * spread
        r.uniform(0, 1); r.uniform(0, 1); r.uniform(0, 1); r.uniform(0, 1)
        d = dur * (0.85 + 0.3 * r.random())
        r.random()
        out.append(delay + d)
    return out
