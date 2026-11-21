# -*- coding: utf-8 -*-
"""Scenery: skies, mountains, sea, buildings, props."""
import math

import cairo

from .core import (OUT, PI, TAU, circle, clamp, ellipse, fill_stroke, hx, lin_grad, limb,
                   mix, noise1, poly, rad_grad, rng, rrect, shade, smooth_poly, src)


def sky(ctx, x0, y0, x1, y1, top, bottom, mid=None):
    stops = [(0, top), (1, bottom)] if mid is None else [(0, top), (0.6, mid), (1, bottom)]
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.set_source(lin_grad(0, y0, 0, y1, stops))
    ctx.fill()


def sun(ctx, x, y, r, color="#fff3c4", glow="#ffd27a", ga=0.55):
    ctx.set_source(rad_grad(x, y, r * 0.5, r * 5, [(0, (*hx(glow)[:3], ga)), (1, (*hx(glow)[:3], 0))]))
    circle(ctx, x, y, r * 5)
    ctx.fill()
    circle(ctx, x, y, r)
    src(ctx, color)
    ctx.fill()


def cloud(ctx, x, y, s=1.0, color="#ffffff", alpha=0.95, outline=True):
    puffs = [(-60, 8, 36), (-25, -14, 46), (22, -22, 50), (62, -2, 38), (0, 14, 40), (-90, 18, 24),
             (94, 16, 26)]
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    if outline:
        for px, py, r in puffs:
            circle(ctx, px, py, r + 4)
            ctx.new_sub_path()
        src(ctx, OUT, 0.25 * alpha)
        ctx.fill()
    for px, py, r in puffs:
        circle(ctx, px, py, r)
        ctx.new_sub_path()
    src(ctx, color, alpha)
    ctx.fill()
    for px, py, r in puffs[:4]:
        circle(ctx, px + 6, py + 10, r * 0.75)
        ctx.new_sub_path()
    src(ctx, shade(color, -0.08), alpha * 0.5)
    ctx.fill()
    ctx.restore()


def clouds(ctx, t, seed=1, n=6, x0=-400, x1=2400, y0=80, y1=380, speed=8, color="#ffffff",
           alpha=0.9, s0=0.6, s1=1.3):
    r = rng(seed)
    span = x1 - x0
    for i in range(n):
        x = x0 + (r.random() * span + t * speed * (0.6 + r.random())) % span
        y = r.uniform(y0, y1)
        cloud(ctx, x, y, r.uniform(s0, s1), color, alpha)


def ridge(seed, x0, x1, base, height, rough=1.0, step=40, peaks=3):
    pts = []
    n = int((x1 - x0) / step) + 2
    for i in range(n):
        x = x0 + i * step
        u = x / 900.0
        h = 0.55 + 0.45 * noise1(u * peaks * 0.5, seed) + 0.18 * rough * noise1(u * 6, seed + 9) \
            + 0.06 * rough * noise1(u * 20, seed + 17)
        pts.append((x, base - height * clamp(h, 0.05, 1.3)))
    return pts


def mountains(ctx, seed, x0, x1, base, height, color, rough=1.0, snow=None, outline=True,
              shade_k=-0.15, peaks=3, bottom=2000):
    pts = ridge(seed, x0, x1, base, height, rough, peaks=peaks)
    poly(ctx, pts + [(x1 + 40, bottom), (x0, bottom)])
    if outline:
        fill_stroke(ctx, color, 4)
    else:
        src(ctx, color)
        ctx.fill()
    # shading strokes
    ctx.save()
    poly(ctx, pts + [(x1 + 40, bottom), (x0, bottom)])
    ctx.clip()
    r = rng(seed + 5)
    src(ctx, shade(color, shade_k))
    for i in range(1, len(pts) - 1):
        if pts[i][1] < pts[i - 1][1] and pts[i][1] < pts[i + 1][1]:
            x, y = pts[i]
            poly(ctx, [(x, y), (x + 120 + r.random() * 80, base + 60), (x + 30, base + 60)])
            ctx.fill()
    if snow:
        for i in range(1, len(pts) - 1):
            x, y = pts[i]
            if y < base - height * 0.82 and pts[i][1] <= pts[i - 1][1] and pts[i][1] <= pts[i + 1][1]:
                poly(ctx, [(x - 70, y + 60), (x - 30, y + 30), (x, y - 2), (x + 34, y + 34),
                           (x + 75, y + 62), (x + 40, y + 50), (x + 10, y + 64), (x - 25, y + 48)])
                src(ctx, snow)
                ctx.fill()
    ctx.restore()
    return pts


def hills(ctx, seed, x0, x1, base, height, color, outline=True, bottom=2000):
    pts = ridge(seed, x0, x1, base, height, 0.3, step=60, peaks=2)
    ctx.move_to(x0, bottom)
    smooth_poly(ctx, pts, close=False)
    ctx.line_to(x1 + 60, bottom)
    ctx.line_to(x0, bottom)
    ctx.close_path()
    if outline:
        fill_stroke(ctx, color, 4)
    else:
        src(ctx, color)
        ctx.fill()
    return pts


def sea(ctx, x0, x1, y, y1, t, color="#3d8fc4", deep="#24628f", lines=True):
    ctx.rectangle(x0, y, x1 - x0, y1 - y)
    ctx.set_source(lin_grad(0, y, 0, y1, [(0, color), (1, deep)]))
    ctx.fill()
    if lines:
        r = rng(77)
        src(ctx, (1, 1, 1, 0.45))
        ctx.set_line_width(3)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for i in range(28):
            yy = y + 10 + r.random() * (y1 - y - 20)
            xx = x0 + (r.random() * (x1 - x0) + t * 12 * (1 + yy / 1000)) % (x1 - x0)
            w = 20 + r.random() * 40
            ctx.move_to(xx, yy)
            ctx.curve_to(xx + w * 0.3, yy - 5, xx + w * 0.7, yy - 5, xx + w, yy)
            ctx.stroke()


def ground(ctx, x0, x1, y, y1, color, pebbles=True, seed=3, grass=None):
    ctx.rectangle(x0, y, x1 - x0, y1 - y)
    ctx.set_source(lin_grad(0, y, 0, y1, [(0, color), (1, shade(color, -0.18))]))
    ctx.fill()
    ctx.move_to(x0, y)
    ctx.line_to(x1, y)
    src(ctx, OUT)
    ctx.set_line_width(4)
    ctx.stroke()
    r = rng(seed)
    if pebbles:
        for i in range(int((x1 - x0) / 25)):
            px = r.uniform(x0, x1)
            py = r.uniform(y + 10, y1)
            ellipse(ctx, px, py, 3 + r.random() * 6, 2 + r.random() * 3)
            src(ctx, shade(color, -0.25 + r.random() * 0.15))
            ctx.fill()
    if grass:
        src(ctx, grass)
        ctx.set_line_width(3)
        for i in range(int((x1 - x0) / 60)):
            gx = r.uniform(x0, x1)
            gy = y + r.uniform(4, 40)
            for k in (-1, 0, 1):
                ctx.move_to(gx, gy)
                ctx.line_to(gx + k * 7, gy - 12 - abs(k) * -3)
            ctx.stroke()


def olive(ctx, x, y, s=1.0, t=0.0, leaf="#6f8f3a"):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    poly(ctx, [(-10, 0), (-6, -60), (-26, -100), (-14, -104), (0, -76), (12, -110), (24, -104),
               (8, -60), (12, 0)])
    fill_stroke(ctx, "#7a5a3a", 4)
    sw = math.sin(t * 1.2 + x) * 2
    for (px, py, r) in ((-40, -120, 40), (0, -150, 48), (42, -122, 40), (-10, -110, 38), (24, -96, 30),
                        (-46, -96, 28)):
        circle(ctx, px + sw, py, r)
        ctx.new_sub_path()
    src(ctx, OUT)
    ctx.set_line_width(8)
    ctx.stroke_preserve()
    src(ctx, leaf)
    ctx.fill()
    for (px, py, r) in ((-30, -130, 18), (10, -158, 20), (40, -128, 16)):
        circle(ctx, px + sw, py, r)
        src(ctx, shade(leaf, 0.15))
        ctx.fill()
    ctx.restore()


def cypress(ctx, x, y, s=1.0, color="#3f6b3a"):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, -230)
    ctx.curve_to(40, -150, 36, -40, 8, 0)
    ctx.line_to(-8, 0)
    ctx.curve_to(-36, -40, -40, -150, 0, -230)
    fill_stroke(ctx, color, 4)
    ctx.restore()


def house(ctx, x, y, s=1.0, wall="#efe3c8", roof="#b9572e", door=True, w=170, h=110):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -w / 2, -h, w, h, 4)
    fill_stroke(ctx, wall, 4.5)
    poly(ctx, [(-w / 2 - 18, -h + 4), (0, -h - 62), (w / 2 + 18, -h + 4)])
    fill_stroke(ctx, roof, 4.5)
    src(ctx, shade(roof, -0.25))
    ctx.set_line_width(2.5)
    for i in range(1, 6):
        ctx.move_to(-w / 2 - 18 + i * (w + 36) / 6, -h + 4)
        ctx.line_to(0 + (i - 3) * 6, -h - 58)
    ctx.stroke()
    if door:
        rrect(ctx, -18, -64, 36, 64, 16)
        fill_stroke(ctx, "#6b4423", 4)
    rrect(ctx, -w / 2 + 20, -h + 26, 26, 24, 3)
    fill_stroke(ctx, "#3a2a1a", 3.5)
    ctx.restore()


def temple(ctx, x, y, s=1.0, color="#efe8d8", ncol=6, w=420, h=200):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -w / 2 - 20, -24, w + 40, 24, 3)
    fill_stroke(ctx, shade(color, -0.08), 4)
    rrect(ctx, -w / 2 - 10, -40, w + 20, 18, 3)
    fill_stroke(ctx, color, 4)
    cw = 22
    for i in range(ncol):
        cx = -w / 2 + 20 + i * (w - 40) / (ncol - 1)
        rrect(ctx, cx - cw / 2, -40 - h, cw, h, 2)
        fill_stroke(ctx, color, 4)
        src(ctx, shade(color, -0.15))
        ctx.set_line_width(2)
        ctx.move_to(cx - 4, -36 - h); ctx.line_to(cx - 4, -44)
        ctx.move_to(cx + 4, -36 - h); ctx.line_to(cx + 4, -44)
        ctx.stroke()
    rrect(ctx, -w / 2 - 14, -64 - h, w + 28, 26, 3)
    fill_stroke(ctx, color, 4)
    poly(ctx, [(-w / 2 - 24, -62 - h), (0, -150 - h), (w / 2 + 24, -62 - h)])
    fill_stroke(ctx, color, 4)
    ctx.restore()


def tent(ctx, x, y, s=1.0, c1="#d9c39a", c2="#a8432e", flag=None, t=0.0, big=False):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * (1.5 if big else 1), s * (1.5 if big else 1))
    pts = [(-110, 0), (-90, -90), (0, -150), (90, -90), (110, 0)]
    poly(ctx, pts)
    fill_stroke(ctx, c1, 4.5)
    ctx.save()
    poly(ctx, pts)
    ctx.clip()
    src(ctx, c2)
    for i in range(-3, 4):
        poly(ctx, [(i * 34 - 8, 0), (i * 8 - 3, -150), (i * 8 + 3, -150), (i * 34 + 8, 0)])
        ctx.fill()
    ctx.restore()
    poly(ctx, pts)
    src(ctx, OUT); ctx.set_line_width(4.5); ctx.stroke()
    poly(ctx, [(-22, 0), (0, -70), (22, 0)])
    fill_stroke(ctx, "#3a2416", 4)
    limb(ctx, [(0, -150), (0, -200)], "#6b4423", 5, 2.5)
    if flag:
        wv = math.sin(t * 4) * 6
        poly(ctx, [(2, -200), (50, -192 + wv), (2, -178)])
        fill_stroke(ctx, flag, 3)
    ctx.restore()


def stone_wall(ctx, x0, x1, y, h, color="#b9ad96", seed=4, broken=0.0):
    r = rng(seed)
    bh = 34
    rows = int(h / bh)
    for j in range(rows):
        xx = x0 - (j % 2) * 30
        while xx < x1:
            bw = r.uniform(50, 90)
            top = y - (j + 1) * bh
            if broken and j >= rows - 2 and r.random() < broken:
                xx += bw
                continue
            rrect(ctx, max(xx, x0), top, min(bw, x1 - max(xx, x0)) - 3, bh - 3, 6)
            fill_stroke(ctx, shade(color, r.uniform(-0.12, 0.08)), 3.5)
            xx += bw


def rock(ctx, x, y, s=1.0, color="#9a8f7c", seed=0):
    r = rng(seed)
    pts = []
    for i in range(8):
        a = PI + i * PI / 7
        rr = 40 * s * (0.7 + 0.4 * r.random())
        pts.append((x + math.cos(a) * rr * 1.4, y + math.sin(a) * rr))
    smooth_poly(ctx, pts + [(x + 56 * s, y), (x - 56 * s, y)], k=0.6)
    fill_stroke(ctx, color, 4)


def stars(ctx, x0, y0, x1, y1, t, seed=9, n=140):
    r = rng(seed)
    for i in range(n):
        x = r.uniform(x0, x1)
        y = r.uniform(y0, y1)
        tw = 0.5 + 0.5 * math.sin(t * (1 + r.random() * 3) + i)
        circle(ctx, x, y, 1 + r.random() * 2)
        src(ctx, (1, 1, 0.9, 0.3 + 0.7 * tw))
        ctx.fill()


def moon(ctx, x, y, r):
    ctx.set_source(rad_grad(x, y, r, r * 4, [(0, (0.8, 0.85, 1, 0.35)), (1, (0.8, 0.85, 1, 0))]))
    circle(ctx, x, y, r * 4)
    ctx.fill()
    circle(ctx, x, y, r)
    src(ctx, "#f4f1dc")
    ctx.fill()
    for (dx, dy, rr) in ((-0.3, -0.2, 0.2), (0.25, 0.3, 0.15), (0.2, -0.35, 0.1)):
        circle(ctx, x + dx * r, y + dy * r, rr * r)
        src(ctx, "#dcd8bf")
        ctx.fill()


def column(ctx, x, y, h, s=1.0, color="#d8c9a8"):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -22, -h, 44, h, 3)
    fill_stroke(ctx, color, 4)
    src(ctx, shade(color, -0.15))
    ctx.set_line_width(2.5)
    for dx in (-10, 0, 10):
        ctx.move_to(dx, -h + 40)
        ctx.line_to(dx, -10)
    ctx.stroke()
    rrect(ctx, -34, -14, 68, 14, 3)
    fill_stroke(ctx, shade(color, -0.05), 4)
    # bull capital (Persepolis style, simplified)
    rrect(ctx, -60, -h - 40, 120, 40, 12)
    fill_stroke(ctx, shade(color, -0.05), 4)
    for side in (-1, 1):
        circle(ctx, side * 44, -h - 26, 16)
        fill_stroke(ctx, shade(color, -0.12), 3.5)
        poly(ctx, [(side * 54, -h - 40), (side * 70, -h - 58), (side * 60, -h - 36)])
        fill_stroke(ctx, "#f2c23a", 3)
    ctx.restore()


def throne(ctx, x, y, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    # parasol
    limb(ctx, [(-70, -40), (-70, -330)], "#8a5a2b", 7, 3)
    ctx.move_to(-190, -300)
    ctx.curve_to(-160, -380, 20, -380, 50, -300)
    ctx.close_path()
    fill_stroke(ctx, "#7a2a8a", 4.5)
    src(ctx, "#f2c23a")
    for i in range(6):
        circle(ctx, -185 + i * 46, -300, 7)
        ctx.fill()
    # steps
    rrect(ctx, -170, -30, 260, 30, 4)
    fill_stroke(ctx, "#c99a4a", 4)
    rrect(ctx, -140, -55, 200, 28, 4)
    fill_stroke(ctx, "#d9aa5a", 4)
    # seat
    rrect(ctx, -110, -230, 30, 180, 6)       # back
    fill_stroke(ctx, "#f2c23a", 4.5)
    rrect(ctx, -110, -120, 150, 26, 6)
    fill_stroke(ctx, "#f2c23a", 4.5)
    for lx in (-100, 22):
        rrect(ctx, lx, -96, 16, 42, 4)
        fill_stroke(ctx, "#d9a52a", 4)
        circle(ctx, lx + 8, -54, 10)
        fill_stroke(ctx, "#d9a52a", 3.5)
    circle(ctx, -95, -238, 16)
    fill_stroke(ctx, "#f2c23a", 4)
    ctx.restore()


def trireme(ctx, x, y, s=1.0, color="#7a4a2a", sail="#efe3c8", emblem="#b81e28", t=0.0, face=1):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * face, s)
    rock_ = math.sin(t * 1.5 + x * 0.01) * 0.02
    ctx.rotate(rock_)
    # oars
    for i in range(9):
        ox = -150 + i * 34
        a = math.sin(t * 3 + i * 0.3) * 0.3
        limb(ctx, [(ox, -10), (ox - 30 + math.sin(a) * 20, 50)], "#8a5a2b", 4, 2)
    poly(ctx, [(-220, -40), (200, -40), (260, -10), (230, 10), (-190, 20), (-240, -70)])
    fill_stroke(ctx, color, 4.5)
    ctx.move_to(-200, -18); ctx.line_to(210, -18)
    src(ctx, shade(color, 0.25)); ctx.set_line_width(5); ctx.stroke()
    circle(ctx, 210, -24, 8)
    fill_stroke(ctx, "#ffffff", 3)
    limb(ctx, [(0, -40), (0, -230)], "#6b4423", 6, 2.5)
    poly(ctx, [(-90, -220), (90, -220), (100, -80), (-100, -80)])
    fill_stroke(ctx, sail, 4)
    circle(ctx, 0, -150, 28)
    fill_stroke(ctx, emblem, 3)
    ctx.restore()


def fire(ctx, x, y, s, t, seed=0):
    r = rng(seed)
    for i, (c, k) in enumerate((("#ff5a1a", 1.0), ("#ffa82e", 0.7), ("#fff0a0", 0.4))):
        for j in range(3):
            fx = x + (j - 1) * 30 * s * k
            fl = noise1(t * 5 + j * 3 + i, seed) * 10 * s
            h = (90 + r.random() * 40) * s * k
            ctx.move_to(fx - 30 * s * k, y)
            ctx.curve_to(fx - 30 * s * k, y - h * 0.5, fx + fl, y - h * 0.8, fx + fl, y - h)
            ctx.curve_to(fx + fl, y - h * 0.7, fx + 30 * s * k, y - h * 0.5, fx + 30 * s * k, y)
            ctx.close_path()
            src(ctx, c, 0.9)
            ctx.fill()


def smoke(ctx, x, y, t, s=1.0, seed=0, color=(0.25, 0.22, 0.2), n=8):
    r = rng(seed)
    for i in range(n):
        ph = (t * 0.25 + i / n) % 1.0
        px = x + noise1(ph * 3 + i, seed) * 40 * s + ph * 60 * s
        py = y - ph * 420 * s
        rr = (30 + ph * 90) * s
        circle(ctx, px, py, rr)
        src(ctx, (*color, 0.45 * (1 - ph)))
        ctx.fill()
