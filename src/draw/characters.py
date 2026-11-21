# -*- coding: utf-8 -*-
"""Chibi-style 2D characters (big round heads, thick outlines) drawn with cairo.

Every character is drawn facing right in a local coordinate system whose origin
is the point between the feet; `face=-1` mirrors it. Units at scale 1:
head radius 50, total height ~215 px (without crest).
"""
import math
from dataclasses import dataclass, field, replace
from typing import Optional

import cairo

from .core import (OUT, PI, TAU, circle, clamp, ellipse, fill_stroke, hx, limb, mix,
                   noise1, poly, rrect, shade, smooth_poly, src, text, lerp)

R = 50.0
HIP = -50.0
SHO = -116.0
HY = -162.0
SKIN = "#f1c29a"


@dataclass
class Look:
    kind: str = "spartan"     # spartan persian mede immortal xerxes elder woman boy
                              # trainer guest ephialtes demaratus herald scout greek man
    skin: str = SKIN
    cloth: str = "#a8222b"
    cloth2: str = "#e8d7a8"
    hair: str = "#3a2415"
    beard: Optional[str] = None
    helmet: Optional[str] = "#c99230"
    crest: str = "#c4232c"
    shield: str = "#c99230"
    emblem: str = "lambda"
    cloak: Optional[str] = "#9f1d26"
    king: bool = False
    spk: Optional[str] = None
    seed: int = 0
    long_hair: bool = True
    scale: float = 1.0        # body scale multiplier (kids)
    hood: str = "#efe6d2"     # Persian soft cap colour


@dataclass
class Pose:
    face: int = 1
    t: float = 0.0
    walk: Optional[float] = None    # gait phase in radians
    run: bool = False
    weapon: str = "spear"           # spear sword bow stick torch scroll cup comb none
    grip: str = "rest"              # spear: rest ready march thrust
    thrust: float = 0.0
    shield: str = "front"           # front up side none
    arm: Optional[tuple] = None     # free near-arm hand target (local coords)
    arm2: Optional[tuple] = None    # far-arm hand target override
    eyes: str = "normal"
    mouth: float = 0.0
    mshape: str = "line"
    look: tuple = (0.0, 0.0)
    tilt: float = 0.0               # forward lean (rad)
    fall: float = 0.0               # 0..1 fall on the back
    sit: bool = False
    jump: float = 0.0
    sweat: bool = False
    green: float = 0.0              # sick face
    blush: bool = False
    broken: bool = False            # broken spear
    alpha: float = 1.0
    blink: bool = True
    bandage: bool = False
    cloak_wind: float = 0.0


def _ik(S, H, l1, l2, bend=1):
    dx, dy = H[0] - S[0], H[1] - S[1]
    d = math.hypot(dx, dy)
    d = clamp(d, 1e-3, l1 + l2 - 1e-3)
    a = math.atan2(dy, dx)
    c = clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1)
    A = math.acos(c)
    E = (S[0] + l1 * math.cos(a + bend * A), S[1] + l1 * math.sin(a + bend * A))
    Hh = (S[0] + (l1 + l2) * math.cos(a) if math.hypot(dx, dy) > l1 + l2 else H[0],
          S[1] + (l1 + l2) * math.sin(a) if math.hypot(dx, dy) > l1 + l2 else H[1])
    return E, Hh


# ===================================================================== parts
def _eyes(ctx, lk, ps, lod):
    ex = [0.06 * R, 0.58 * R]
    ey = HY - 0.02 * R
    kind = ps.eyes
    if ps.blink and kind in ("normal", "angry", "wide", "sad", "scared"):
        ph = (ps.t + lk.seed * 1.37) % 3.9
        if ph < 0.12:
            kind = "closed"
    lw = 3.2
    for i, x in enumerate(ex):
        rx, ry = 0.215 * R, 0.26 * R
        if kind == "wide":
            rx, ry = 0.25 * R, 0.31 * R
        if kind in ("closed", "happy", "dead"):
            ctx.set_line_width(4.0)
            src(ctx, OUT)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            if kind == "closed":
                ctx.arc(x, ey - 2, 0.15 * R, 0.15 * PI, 0.85 * PI)
            elif kind == "happy":
                ctx.arc_negative(x, ey + 6, 0.15 * R, -0.15 * PI, -0.85 * PI)
            else:
                d = 0.12 * R
                ctx.move_to(x - d, ey - d); ctx.line_to(x + d, ey + d)
                ctx.move_to(x + d, ey - d); ctx.line_to(x - d, ey + d)
            ctx.stroke()
            continue
        ellipse(ctx, x, ey, rx, ry)
        fill_stroke(ctx, "#ffffff", lw)
        if lod:
            continue
        pr = 0.105 * R if kind != "scared" else 0.065 * R
        px = x + 0.05 * R + ps.look[0] * 0.08 * R
        py = ey + 0.03 * R + ps.look[1] * 0.08 * R
        if kind == "sad":
            py += 0.05 * R
        circle(ctx, px, py, pr)
        src(ctx, "#1d1612")
        ctx.fill()
        circle(ctx, px + pr * 0.35, py - pr * 0.4, pr * 0.32)
        src(ctx, "#ffffff")
        ctx.fill()
        if kind == "sly":
            ctx.save()
            ellipse(ctx, x, ey, rx, ry)
            ctx.clip()
            ctx.rectangle(x - rx - 2, ey - ry - 2, rx * 2 + 4, ry * 1.05)
            src(ctx, lk.skin)
            ctx.fill()
            ctx.restore()
            ctx.move_to(x - rx, ey - ry * 0.0)
            ctx.line_to(x + rx, ey - ry * 0.0)
            src(ctx, OUT); ctx.set_line_width(3.5); ctx.stroke()
    if lod:
        return
    # brows
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(5.5)
    src(ctx, OUT)
    by = ey - 0.33 * R
    if kind == "angry":
        ctx.move_to(ex[0] - 0.17 * R, by - 4); ctx.line_to(ex[0] + 0.19 * R, by + 7)
        ctx.move_to(ex[1] - 0.19 * R, by + 7); ctx.line_to(ex[1] + 0.17 * R, by - 4)
    elif kind in ("scared", "sad"):
        ctx.move_to(ex[0] - 0.17 * R, by + 3); ctx.line_to(ex[0] + 0.17 * R, by - 7)
        ctx.move_to(ex[1] - 0.17 * R, by - 7); ctx.line_to(ex[1] + 0.17 * R, by + 3)
    elif kind == "wide":
        ctx.move_to(ex[0] - 0.15 * R, by - 10); ctx.line_to(ex[0] + 0.15 * R, by - 12)
        ctx.move_to(ex[1] - 0.15 * R, by - 12); ctx.line_to(ex[1] + 0.15 * R, by - 10)
    elif kind == "sly":
        ctx.move_to(ex[0] - 0.15 * R, by + 2); ctx.line_to(ex[0] + 0.17 * R, by + 5)
        ctx.move_to(ex[1] - 0.17 * R, by - 4); ctx.line_to(ex[1] + 0.17 * R, by - 9)
    elif kind in ("normal", "closed", "happy"):
        ctx.move_to(ex[0] - 0.14 * R, by); ctx.line_to(ex[0] + 0.14 * R, by - 2)
        ctx.move_to(ex[1] - 0.14 * R, by - 2); ctx.line_to(ex[1] + 0.14 * R, by)
    ctx.stroke()


def _mouth(ctx, lk, ps, lod):
    if lod:
        return
    mx, my = 0.36 * R, HY + 0.47 * R
    m = clamp(ps.mouth, 0, 1.2)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if m > 0.08 or ps.mshape in ("shout", "o"):
        if ps.mshape == "shout":
            m = max(m, 0.9)
        if ps.mshape == "o":
            m = max(m, 0.45)
        w = 0.17 * R if ps.mshape != "o" else 0.1 * R
        h = 0.04 * R + 0.2 * R * m
        ellipse(ctx, mx, my + h * 0.3, w, h)
        fill_stroke(ctx, "#5b1a1c", 3)
        ctx.save()
        ellipse(ctx, mx, my + h * 0.3, w, h)
        ctx.clip()
        ellipse(ctx, mx, my + h * 1.1, w * 0.8, h * 0.6)
        src(ctx, "#e0707a")
        ctx.fill()
        ctx.restore()
        return
    src(ctx, OUT)
    ctx.set_line_width(4.0)
    s = ps.mshape
    if s == "smile":
        ctx.arc(mx, my - 0.12 * R, 0.17 * R, 0.2 * PI, 0.8 * PI)
    elif s == "grin":
        ctx.move_to(mx - 0.2 * R, my - 3)
        ctx.curve_to(mx - 0.1 * R, my + 0.2 * R, mx + 0.15 * R, my + 0.2 * R, mx + 0.24 * R, my - 6)
        ctx.close_path()
        src(ctx, "#ffffff"); ctx.fill_preserve(); src(ctx, OUT); ctx.set_line_width(3.5)
    elif s == "frown":
        ctx.arc_negative(mx, my + 0.16 * R, 0.14 * R, -0.2 * PI, -0.8 * PI)
    elif s == "wavy":
        ctx.move_to(mx - 0.18 * R, my)
        for i in range(4):
            ctx.rel_curve_to(3, -6, 6, -6, 0.09 * R, 0) if i % 2 == 0 else ctx.rel_curve_to(3, 6, 6, 6, 0.09 * R, 0)
    else:
        ctx.move_to(mx - 0.11 * R, my)
        ctx.line_to(mx + 0.11 * R, my)
    ctx.stroke()


def _nose(ctx, lk):
    ctx.move_to(0.8 * R, HY + 0.06 * R)
    ctx.curve_to(0.98 * R, HY + 0.16 * R, 0.96 * R, HY + 0.3 * R, 0.78 * R, HY + 0.28 * R)
    src(ctx, shade(lk.skin, -0.35))
    ctx.set_line_width(3.2)
    ctx.stroke()


def _beard(ctx, lk, style="short"):
    c = lk.beard
    if not c:
        return
    if style == "long":      # Persian square curly beard
        pts = [(-0.35 * R, HY + 0.1 * R), (-0.2 * R, HY + 0.95 * R), (0.1 * R, HY + 1.35 * R),
               (0.6 * R, HY + 1.3 * R), (0.85 * R, HY + 0.85 * R), (0.92 * R, HY + 0.35 * R),
               (0.7 * R, HY + 0.62 * R), (0.0 * R, HY + 0.55 * R)]
    elif style == "elder":
        pts = [(-0.4 * R, HY + 0.05 * R), (-0.25 * R, HY + 1.0 * R), (0.2 * R, HY + 1.55 * R),
               (0.55 * R, HY + 1.25 * R), (0.88 * R, HY + 0.7 * R), (0.92 * R, HY + 0.35 * R),
               (0.6 * R, HY + 0.62 * R), (0.0 * R, HY + 0.5 * R)]
    else:
        pts = [(-0.4 * R, HY + 0.05 * R), (-0.3 * R, HY + 0.75 * R), (0.1 * R, HY + 1.08 * R),
               (0.55 * R, HY + 1.0 * R), (0.88 * R, HY + 0.6 * R), (0.92 * R, HY + 0.32 * R),
               (0.6 * R, HY + 0.6 * R), (0.0 * R, HY + 0.5 * R)]
    smooth_poly(ctx, pts)
    fill_stroke(ctx, c, 4)
    if style == "long":
        src(ctx, shade(c, 0.25))
        ctx.set_line_width(2.5)
        for i in range(5):
            for j in range(2):
                ctx.arc(-0.05 * R + i * 0.17 * R, HY + 0.85 * R + j * 0.22 * R, 4, 0, PI * 1.5)
                ctx.new_sub_path()
        ctx.stroke()


def _head_base(ctx, lk, ps):
    skin = lk.skin if ps.green <= 0 else mix(lk.skin, "#8fbf5a", ps.green)
    circle(ctx, 0, HY, R)
    fill_stroke(ctx, skin, 4.5)
    return skin


def _ear(ctx, lk):
    ellipse(ctx, -0.12 * R, HY + 0.08 * R, 0.14 * R, 0.19 * R)
    fill_stroke(ctx, shade(lk.skin, -0.05), 3.5)


def _spartan_helmet(ctx, lk, ps):
    hc = lk.helmet
    cy = HY - 0.03 * R

    def outer():
        ctx.new_path()
        ctx.arc_negative(0, cy, 1.09 * R, -0.22, -PI * 1.36)
        ctx.line_to(0.15 * R, HY + 1.02 * R)
        ctx.line_to(0.62 * R, HY + 1.0 * R)
        ctx.line_to(0.98 * R, HY + 0.45 * R)
        ctx.close_path()

    def window():
        ctx.new_sub_path()
        poly(ctx, [(-0.27 * R, HY - 0.36 * R), (1.5 * R, HY - 0.36 * R), (1.5 * R, HY + 0.86 * R),
                   (0.16 * R, HY + 0.86 * R), (0.16 * R, HY + 0.27 * R), (-0.27 * R, HY + 0.27 * R)])

    def noseguard():
        ctx.new_sub_path()
        rrect(ctx, 0.27 * R, HY - 0.4 * R, 0.1 * R, 0.55 * R, 0.04 * R)

    # crest (behind the dome)
    _crest(ctx, lk, ps)
    ctx.save()
    ctx.rectangle(-500, -800, 1000, 1200)
    window()
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.clip()
    outer()
    src(ctx, hc)
    ctx.fill_preserve()
    ctx.save()
    ctx.clip()
    # shading crescent on the back + shine
    circle(ctx, 0.35 * R, cy - 0.25 * R, 1.05 * R)
    ctx.rectangle(-300, -600, 600, 900)
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    src(ctx, shade(hc, -0.28))
    ctx.fill()
    ctx.restore()
    outer()
    src(ctx, OUT)
    ctx.set_line_width(4.5)
    ctx.stroke()
    # brow ridge line
    ctx.arc_negative(0, cy, 0.86 * R, -0.35, -PI * 0.92)
    src(ctx, shade(hc, -0.35))
    ctx.set_line_width(3)
    ctx.stroke()
    # shine
    ctx.arc_negative(0, cy, 0.8 * R, -1.1, -1.9)
    src(ctx, (1, 1, 1, 0.55))
    ctx.set_line_width(6)
    ctx.stroke()
    ctx.restore()
    # window outline (only where the helmet is)
    ctx.save()
    outer()
    ctx.clip()
    window()
    src(ctx, OUT)
    ctx.set_line_width(4)
    ctx.stroke()
    noseguard()
    src(ctx, hc)
    ctx.fill_preserve()
    src(ctx, OUT)
    ctx.set_line_width(3)
    ctx.stroke()
    ctx.restore()
    if lk.king:  # golden diadem band
        ctx.arc_negative(0, cy, 1.0 * R, -0.45, -PI * 1.1)
        src(ctx, "#ffe07a")
        ctx.set_line_width(7)
        ctx.stroke()


def _crest(ctx, lk, ps):
    c = lk.crest
    big = 1.25 if lk.king else 1.0
    t = ps.t
    sway = noise1(t * 1.3, lk.seed) * 0.05 + ps.cloak_wind * 0.08
    ctx.save()
    ctx.translate(0, HY - 0.9 * R)
    ctx.rotate(sway)
    # stand
    rrect(ctx, -0.1 * R, -0.25 * R, 0.2 * R, 0.4 * R, 0.05 * R)
    fill_stroke(ctx, lk.helmet, 3.5)
    ctx.new_path()
    ctx.move_to(-1.15 * R * big, 0.55 * R)
    ctx.curve_to(-1.1 * R * big, -0.75 * R * big, 0.5 * R * big, -1.05 * R * big,
                 0.95 * R * big, -0.15 * R)
    ctx.curve_to(0.55 * R * big, -0.62 * R * big, -0.45 * R * big, -0.55 * R * big,
                 -0.75 * R * big, 0.6 * R)
    ctx.close_path()
    fill_stroke(ctx, c, 4)
    src(ctx, shade(c, -0.3))
    ctx.set_line_width(2.5)
    for i in range(5):
        k = i / 5
        ctx.move_to(-0.9 * R * big + k * 1.5 * R * big, 0.0 - math.sin(k * PI) * 0.45 * R * big)
        ctx.rel_line_to(-0.18 * R, -0.12 * R)
    ctx.stroke()
    ctx.restore()


def _long_hair(ctx, lk, ps, back=True):
    c = lk.hair
    if back:
        sway = noise1(ps.t * 1.2, lk.seed + 3) * 4
        pts = [(-0.75 * R, HY - 0.55 * R), (-1.08 * R, HY + 0.1 * R),
               (-0.95 * R + sway, HY + 1.05 * R), (-0.45 * R + sway, HY + 1.12 * R),
               (-0.25 * R, HY + 0.5 * R), (0.1 * R, HY - 0.2 * R)]
        smooth_poly(ctx, pts)
        fill_stroke(ctx, c, 4)
    else:
        ctx.new_path()
        ctx.arc_negative(0, HY, 1.03 * R, -0.25, -PI * 1.12)
        ctx.curve_to(-0.6 * R, HY - 0.35 * R, 0.2 * R, HY - 0.7 * R, 0.98 * R, HY - 0.25 * R)
        ctx.close_path()
        fill_stroke(ctx, c, 4)


def _short_hair(ctx, lk, bald=False):
    c = lk.hair
    if bald:   # elder: ring of hair
        ctx.new_path()
        ctx.arc_negative(0, HY, 1.02 * R, PI * 0.95, PI * 0.55)
        ctx.arc(0, HY, 0.75 * R, PI * 0.6, PI * 0.9)
        ctx.close_path()
        fill_stroke(ctx, c, 3.5)
        return
    ctx.new_path()
    ctx.arc_negative(0, HY, 1.04 * R, -0.15, -PI * 1.15)
    ctx.curve_to(-0.6 * R, HY - 0.3 * R, 0.2 * R, HY - 0.72 * R, 0.95 * R, HY - 0.15 * R)
    ctx.close_path()
    fill_stroke(ctx, c, 4)


def _shaved(ctx, lk):
    ctx.save()
    circle(ctx, 0, HY, R - 2)
    ctx.clip()
    ctx.arc_negative(0, HY, 1.0 * R, -0.3, -PI * 1.05)
    ctx.curve_to(-0.6 * R, HY - 0.25 * R, 0.2 * R, HY - 0.6 * R, 0.95 * R, HY - 0.3 * R)
    ctx.close_path()
    src(ctx, shade(lk.skin, -0.18))
    ctx.fill()
    ctx.restore()


def _persian_hood(ctx, lk, ps, color, tall=False):
    """Soft Persian/Median cap (tiara) wrapped around chin."""
    def outer():
        ctx.new_path()
        if tall:
            ctx.move_to(0.9 * R, HY - 0.4 * R)
            ctx.curve_to(0.8 * R, HY - 1.5 * R, -0.5 * R, HY - 1.6 * R, -0.9 * R, HY - 0.7 * R)
        else:
            ctx.move_to(0.95 * R, HY - 0.35 * R)
            ctx.curve_to(0.85 * R, HY - 1.35 * R, -0.95 * R, HY - 1.4 * R, -1.05 * R, HY - 0.2 * R)
        ctx.curve_to(-1.15 * R, HY + 0.6 * R, -0.6 * R, HY + 1.2 * R, 0.2 * R, HY + 1.15 * R)
        ctx.line_to(0.5 * R, HY + 0.98 * R)
        ctx.curve_to(0.0, HY + 0.85 * R, -0.3 * R, HY + 0.3 * R, -0.2 * R, HY - 0.25 * R)
        ctx.curve_to(0.1 * R, HY - 0.48 * R, 0.6 * R, HY - 0.45 * R, 0.95 * R, HY - 0.35 * R)
        ctx.close_path()
    outer()
    fill_stroke(ctx, color, 4.5)
    ctx.save()
    outer()
    ctx.clip()
    src(ctx, shade(color, -0.2))
    ctx.set_line_width(3)
    for i in range(3):
        ctx.move_to(-0.95 * R + i * 0.25 * R, HY - 0.6 * R)
        ctx.curve_to(-0.8 * R + i * 0.2 * R, HY, -0.6 * R + i * 0.2 * R, HY + 0.6 * R,
                     -0.2 * R + i * 0.2 * R, HY + 1.1 * R)
    ctx.stroke()
    ctx.restore()


def _crown(ctx, lk):
    """Xerxes' crenellated crown."""
    x0, x1 = -0.75 * R, 0.85 * R
    y0, y1 = HY - 0.55 * R, HY - 1.65 * R
    pts = [(x0, y0), (x0 - 0.05 * R, y1 + 0.25 * R)]
    n = 5
    for i in range(n):
        a = x0 - 0.05 * R + (x1 - x0 + 0.1 * R) * i / n
        b = x0 - 0.05 * R + (x1 - x0 + 0.1 * R) * (i + 0.5) / n
        c = x0 - 0.05 * R + (x1 - x0 + 0.1 * R) * (i + 1) / n
        pts += [(a, y1), (b, y1), (b, y1 + 0.22 * R), (c, y1 + 0.22 * R)]
    pts += [(x1 + 0.05 * R, y1 + 0.25 * R), (x1, y0)]
    poly(ctx, pts)
    fill_stroke(ctx, "#f2c23a", 4.5)
    rrect(ctx, x0 - 0.05 * R, HY - 0.95 * R, x1 - x0 + 0.1 * R, 0.25 * R, 3)
    fill_stroke(ctx, "#c7902a", 3)
    for i in range(4):
        circle(ctx, x0 + 0.2 * R + i * 0.38 * R, HY - 0.83 * R, 0.07 * R)
        fill_stroke(ctx, "#d9334a" if i % 2 else "#2e8bd9", 2)


# ===================================================================== equipment
def draw_shield(ctx, cx, cy, r, color, emblem="lambda", sx=0.9, sy=1.0, dent=0.0):
    ellipse(ctx, cx, cy, r * sx, r * sy)
    fill_stroke(ctx, color, 5)
    ellipse(ctx, cx, cy, r * sx * 0.82, r * sy * 0.82)
    src(ctx, shade(color, -0.12))
    ctx.fill()
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(sx, sy)
    if emblem == "lambda":
        poly(ctx, [(-0.42 * r, 0.5 * r), (-0.08 * r, -0.55 * r), (0.08 * r, -0.55 * r),
                   (0.42 * r, 0.5 * r), (0.24 * r, 0.5 * r), (0.0, -0.18 * r),
                   (-0.24 * r, 0.5 * r)])
        fill_stroke(ctx, "#b81e28", 3)
    elif emblem == "club":
        poly(ctx, [(-0.08 * r, 0.55 * r), (0.08 * r, 0.55 * r), (0.2 * r, -0.5 * r),
                   (-0.2 * r, -0.5 * r)])
        fill_stroke(ctx, "#2b2b2b", 3)
        for k in (-0.3, 0.0, 0.3):
            circle(ctx, k * 0.4 * r, -0.12 * r + k * 0.5 * r, 0.06 * r)
            fill_stroke(ctx, "#2b2b2b", 2)
    elif emblem == "star":
        pts = []
        for i in range(10):
            a = -PI / 2 + i * PI / 5
            rr = 0.5 * r if i % 2 == 0 else 0.22 * r
            pts.append((math.cos(a) * rr, math.sin(a) * rr))
        poly(ctx, pts)
        fill_stroke(ctx, "#f4f0e0", 3)
    elif emblem == "crescent":
        ctx.arc(0, 0, 0.45 * r, 0.6, PI * 2 - 0.6)
        ctx.arc_negative(0.18 * r, 0, 0.36 * r, PI * 2 - 0.9, 0.9)
        ctx.close_path()
        fill_stroke(ctx, "#f4f0e0", 3)
    elif emblem == "trident":
        ctx.move_to(0, 0.55 * r); ctx.line_to(0, -0.45 * r)
        ctx.move_to(-0.3 * r, -0.45 * r); ctx.line_to(-0.3 * r, -0.05 * r)
        ctx.line_to(0.3 * r, -0.05 * r); ctx.line_to(0.3 * r, -0.45 * r)
        src(ctx, "#1d1d1d"); ctx.set_line_width(0.1 * r); ctx.stroke()
    elif emblem == "bull":
        circle(ctx, 0, 0.05 * r, 0.25 * r)
        fill_stroke(ctx, "#5a3a1a", 3)
        ctx.move_to(-0.2 * r, -0.1 * r); ctx.curve_to(-0.5 * r, -0.2 * r, -0.5 * r, -0.5 * r, -0.3 * r, -0.55 * r)
        ctx.move_to(0.2 * r, -0.1 * r); ctx.curve_to(0.5 * r, -0.2 * r, 0.5 * r, -0.5 * r, 0.3 * r, -0.55 * r)
        src(ctx, "#f4f0e0"); ctx.set_line_width(0.08 * r); ctx.stroke()
    ctx.restore()
    # shine
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(sx, sy)
    ctx.arc(0, 0, 0.9 * r, PI * 1.1, PI * 1.45)
    src(ctx, (1, 1, 1, 0.5))
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.restore()


def draw_wicker(ctx, cx, cy, w, h, color="#c9a46a"):
    rrect(ctx, cx - w / 2, cy - h / 2, w, h, 10)
    fill_stroke(ctx, color, 4.5)
    ctx.save()
    rrect(ctx, cx - w / 2, cy - h / 2, w, h, 10)
    ctx.clip()
    src(ctx, shade(color, -0.25))
    ctx.set_line_width(2)
    for i in range(-8, 9):
        ctx.move_to(cx - w / 2 + i * 9, cy - h / 2)
        ctx.line_to(cx - w / 2 + i * 9 + h * 0.6, cy + h / 2)
        ctx.move_to(cx + w / 2 - i * 9, cy - h / 2)
        ctx.line_to(cx + w / 2 - i * 9 - h * 0.6, cy + h / 2)
    ctx.stroke()
    ctx.restore()
    rrect(ctx, cx - w / 2 + 6, cy - h / 2 + 6, w - 12, h - 12, 7)
    src(ctx, shade(color, -0.35))
    ctx.set_line_width(2.5)
    ctx.stroke()


def draw_spear(ctx, hx_, hy_, ang, length=300, back=0.33, color="#7a4e2a", tip="#d8a640",
               broken=False, butt=True, short=False):
    ca, sa = math.cos(ang), math.sin(ang)
    b = (hx_ - ca * length * back, hy_ - sa * length * back)
    f_len = length * (1 - back) * (0.35 if broken else 1.0)
    f = (hx_ + ca * f_len, hy_ + sa * f_len)
    limb(ctx, [b, f], color, 7, 3, cap=cairo.LINE_CAP_BUTT)
    if broken:
        # splinters
        poly(ctx, [f, (f[0] + ca * 10 - sa * 6, f[1] + sa * 10 + ca * 6),
                   (f[0] + ca * 4, f[1] + sa * 4), (f[0] + ca * 12 + sa * 5, f[1] + sa * 12 - ca * 5)])
        fill_stroke(ctx, color, 2.5)
    else:
        L = 34 if not short else 26
        Wd = 9
        p0 = f
        p1 = (f[0] + ca * L * 0.45 - sa * Wd, f[1] + sa * L * 0.45 + ca * Wd)
        p2 = (f[0] + ca * L, f[1] + sa * L)
        p3 = (f[0] + ca * L * 0.45 + sa * Wd, f[1] + sa * L * 0.45 - ca * Wd)
        poly(ctx, [p0, p1, p2, p3])
        fill_stroke(ctx, tip, 3.5)
    if butt:
        e = (b[0] - ca * 18, b[1] - sa * 18)
        limb(ctx, [b, e], shade(tip, -0.2), 6, 3)


def draw_sword(ctx, hx_, hy_, ang, length=70):
    ca, sa = math.cos(ang), math.sin(ang)
    tip = (hx_ + ca * length, hy_ + sa * length)
    poly(ctx, [(hx_ - sa * 6, hy_ + ca * 6), (hx_ + ca * length * 0.6 - sa * 9, hy_ + sa * length * 0.6 + ca * 9),
               tip, (hx_ + ca * length * 0.6 + sa * 9, hy_ + sa * length * 0.6 - ca * 9),
               (hx_ + sa * 6, hy_ - ca * 6)])
    fill_stroke(ctx, "#d9dde2", 3.5)
    limb(ctx, [(hx_ - sa * 13, hy_ + ca * 13), (hx_ + sa * 13, hy_ - ca * 13)], "#8a5a2b", 6, 3)


def draw_bow(ctx, hx_, hy_, draw=0.0):
    ctx.new_path()
    ctx.arc(hx_ - 30, hy_, 62, -1.05, 1.05)
    src(ctx, OUT); ctx.set_line_width(11); ctx.stroke_preserve()
    src(ctx, "#8a5a2b"); ctx.set_line_width(6); ctx.stroke()
    top = (hx_ - 30 + 62 * math.cos(-1.05), hy_ + 62 * math.sin(-1.05))
    bot = (hx_ - 30 + 62 * math.cos(1.05), hy_ + 62 * math.sin(1.05))
    mid = (hx_ - 12 - draw * 45, hy_)
    poly(ctx, [top, mid, bot], close=False)
    src(ctx, "#eeeeee"); ctx.set_line_width(2); ctx.stroke()
    if draw > 0.05:
        limb(ctx, [mid, (mid[0] + 75, mid[1])], "#8a5a2b", 3, 1.5)
        poly(ctx, [(mid[0] + 75, mid[1] - 5), (mid[0] + 86, mid[1]), (mid[0] + 75, mid[1] + 5)])
        fill_stroke(ctx, "#bbbbbb", 2)
    return mid


def draw_torch(ctx, x, y, t, s=1.0):
    limb(ctx, [(x, y), (x + 4 * s, y + 55 * s)], "#6b4423", 8 * s, 3)
    for i, (c, r) in enumerate((("#ff7a1a", 22), ("#ffb52e", 15), ("#fff2a0", 8))):
        fl = noise1(t * 9 + i, 5) * 4
        ctx.move_to(x - r * s, y)
        ctx.curve_to(x - r * s, y - r * 1.2 * s, x + fl * s, y - r * 2.6 * s + fl, x + fl * s, y - r * 3.0 * s)
        ctx.curve_to(x + fl * s, y - r * 2.4 * s, x + r * s, y - r * 1.2 * s, x + r * s, y)
        ctx.close_path()
        src(ctx, c)
        ctx.fill()


# ===================================================================== body
def _legs(ctx, lk, ps, robe=False):
    if ps.sit:
        for i, dx in enumerate((-4, 8)):
            col = shade(lk.skin, -0.12) if i == 0 else lk.skin
            limb(ctx, [(dx - 6, HIP + 10), (dx + 38, HIP + 12), (dx + 40, -2)], col, 15, 4)
            ellipse(ctx, dx + 48, -2, 14, 7)
            fill_stroke(ctx, "#6b3f1f", 3.5)
        return
    amp = 0.0
    if ps.walk is not None:
        amp = 0.75 if ps.run else 0.45
    for i, side in enumerate((-1, 1)):
        a = math.sin((ps.walk or 0) + (PI if side < 0 else 0)) * amp
        hipx = side * 9
        knee = (hipx + math.sin(a) * 26, HIP + math.cos(a) * 26)
        lift = max(0, math.sin((ps.walk or 0) + (PI if side < 0 else 0) + PI / 2)) * (10 if ps.walk is not None else 0)
        foot = (hipx + math.sin(a) * 50, HIP + math.cos(a) * 50 - lift)
        col = lk.skin if i == 1 else shade(lk.skin, -0.12)
        if robe:
            col = shade(lk.cloth2 if lk.kind in ("mede", "scout") else lk.cloth, -0.1 if i == 0 else 0)
        limb(ctx, [(hipx, HIP + 4), knee, foot], col, 16, 4)
        if lk.kind in ("spartan", "greek") and lk.helmet:
            # bronze greave
            g0 = (knee[0] + (foot[0] - knee[0]) * 0.1, knee[1] + (foot[1] - knee[1]) * 0.1)
            limb(ctx, [g0, (foot[0], foot[1] - 7)], shade(lk.helmet, -0.08 if i == 0 else 0.05), 15, 3,
                 cap=cairo.LINE_CAP_BUTT)
        sandal = "#6b3f1f" if lk.kind not in ("boy",) else shade(lk.skin, -0.2)
        ellipse(ctx, foot[0] + 7, foot[1] + 1, 14, 7)
        fill_stroke(ctx, sandal, 3.5)


def _cloak(ctx, lk, ps):
    if not lk.cloak:
        return
    t = ps.t
    w = noise1(t * 1.6, lk.seed + 7) * 6 + (math.sin((ps.walk or 0) * 1.0) * 8 if ps.walk is not None else 0)
    wind = ps.cloak_wind * 30 + (16 if ps.run else 0)
    pts = [(-16, SHO - 2), (-34 - wind * 0.4, SHO + 30), (-48 - wind + w, -40),
           (-52 - wind * 1.3 + w * 1.4, -10), (-30 - wind * 0.6 + w, -4), (-8, -22), (10, SHO + 10)]
    smooth_poly(ctx, pts, k=0.8)
    fill_stroke(ctx, lk.cloak, 4.5)
    smooth_poly(ctx, [(-22, SHO + 8), (-40 - wind * 0.6 + w * 0.5, -40), (-36 - wind + w, -12)],
                close=False)
    src(ctx, shade(lk.cloak, -0.25))
    ctx.set_line_width(3)
    ctx.stroke()


def _torso(ctx, lk, ps):
    k = lk.kind
    if k in ("spartan", "greek") and lk.helmet:
        # chiton skirt
        poly(ctx, [(-27, -72), (27, -72), (31, HIP + 8), (-31, HIP + 8)])
        fill_stroke(ctx, lk.cloth, 4)
        # pteruges
        ctx.save()
        poly(ctx, [(-29, -68), (29, -68), (30, HIP + 2), (-30, HIP + 2)])
        src(ctx, "#d8c08a"); ctx.fill_preserve(); src(ctx, OUT); ctx.set_line_width(3.5); ctx.stroke()
        for i in range(1, 6):
            x = -29 + i * 58 / 6
            ctx.move_to(x, -68); ctx.line_to(x, HIP + 2)
        ctx.set_line_width(2.5); ctx.stroke()
        ctx.restore()
        # bronze cuirass
        pts = [(-24, SHO), (24, SHO), (30, SHO + 20), (27, -66), (-27, -66), (-30, SHO + 20)]
        smooth_poly(ctx, pts, k=0.3)
        fill_stroke(ctx, lk.helmet, 4.5)
        src(ctx, shade(lk.helmet, -0.3))
        ctx.set_line_width(3)
        ctx.arc(-6, SHO + 22, 11, 0.1, PI - 0.1)
        ctx.new_sub_path()
        ctx.arc(14, SHO + 22, 11, 0.1, PI - 0.1)
        ctx.move_to(4, SHO + 34); ctx.line_to(4, -72)
        ctx.stroke()
        ctx.move_to(-18, SHO + 6); ctx.line_to(-12, -74)
        src(ctx, (1, 1, 1, 0.35)); ctx.set_line_width(5); ctx.stroke()
        return
    if k in ("spartan", "greek", "boy", "trainer", "man", "ephialtes"):
        # simple tunic (chiton/exomis)
        bot = HIP + 14
        pts = [(-24, SHO), (24, SHO), (32, bot), (-32, bot)]
        poly(ctx, pts)
        fill_stroke(ctx, lk.cloth, 4.5)
        ctx.move_to(-30, -70); ctx.line_to(30, -70)
        src(ctx, shade(lk.cloth, -0.3)); ctx.set_line_width(5); ctx.stroke()
        if k == "ephialtes":
            for (px, py) in ((-12, -95), (12, -58)):
                rrect(ctx, px - 8, py - 7, 16, 14, 3)
                fill_stroke(ctx, "#8a7a52", 2.5)
        return
    if k in ("elder", "woman", "guest", "demaratus"):
        bot = -6 if k != "elder" else -14
        belly = 18 if k == "guest" else 0
        pts = [(-24, SHO), (24, SHO), (34 + belly, -80), (36 + belly * 0.6, bot), (-36, bot), (-32, -80)]
        smooth_poly(ctx, pts, k=0.25)
        fill_stroke(ctx, lk.cloth, 4.5)
        # drape
        src(ctx, shade(lk.cloth, -0.22)); ctx.set_line_width(3)
        ctx.move_to(-20, SHO + 4); ctx.curve_to(0, -80, 16, -60, 28 + belly * 0.5, -30)
        ctx.move_to(-10, -40); ctx.line_to(-14, bot + 2)
        ctx.move_to(10, -40); ctx.line_to(12, bot + 2)
        ctx.stroke()
        if k in ("woman", "guest", "demaratus"):
            ctx.move_to(-28, -60); ctx.curve_to(0, -56, 20, -56, 33 + belly, -62)
            src(ctx, lk.cloth2); ctx.set_line_width(7); ctx.stroke()
        if k == "guest":
            ctx.arc(8, SHO + 4, 16, 0.2, PI - 0.2)
            src(ctx, "#ffd34a"); ctx.set_line_width(5); ctx.stroke()
        return
    if k in ("persian", "immortal", "xerxes", "herald"):
        bot = -6
        pts = [(-24, SHO), (24, SHO), (30, -80), (40, bot), (-40, bot), (-30, -80)]
        smooth_poly(ctx, pts, k=0.2)
        fill_stroke(ctx, lk.cloth, 4.5)
        ctx.save()
        smooth_poly(ctx, pts, k=0.2)
        ctx.clip()
        # rosette pattern
        src(ctx, lk.cloth2)
        for j in range(4):
            for i in range(5):
                circle(ctx, -32 + i * 16 + (j % 2) * 8, -100 + j * 24, 3.2)
                ctx.fill()
        # hem band + belt
        ctx.rectangle(-60, bot - 12, 120, 12)
        src(ctx, lk.cloth2); ctx.fill()
        ctx.rectangle(-40, -76, 80, 9)
        src(ctx, "#f2c23a" if k in ("xerxes", "immortal") else shade(lk.cloth, -0.35)); ctx.fill()
        # vertical pleats
        src(ctx, shade(lk.cloth, -0.25)); ctx.set_line_width(3)
        for x in (-14, 6, 24):
            ctx.move_to(x, -66); ctx.line_to(x * 1.2, bot - 12)
        ctx.stroke()
        ctx.restore()
        smooth_poly(ctx, pts, k=0.2)
        src(ctx, OUT); ctx.set_line_width(4.5); ctx.stroke()
        if k == "xerxes":
            ctx.move_to(0, SHO + 4); ctx.line_to(0, bot)
            src(ctx, "#f2c23a"); ctx.set_line_width(9); ctx.stroke()
        return
    if k in ("mede", "scout"):
        # tunic to knees + trousers (legs drawn with cloth2)
        pts = [(-24, SHO), (24, SHO), (32, -40), (-32, -40)]
        poly(ctx, pts)
        fill_stroke(ctx, lk.cloth, 4.5)
        ctx.rectangle(-30, -76, 61, 8)
        src(ctx, shade(lk.cloth, -0.35)); ctx.fill()
        ctx.move_to(-31, -46); ctx.line_to(31, -46)
        src(ctx, lk.cloth2); ctx.set_line_width(6); ctx.stroke()
        return


def _arm(ctx, S, H, color, sleeve=None, w=14, bend=1, hand=True, skin=SKIN):
    E, Hh = _ik(S, H, 30, 30, bend)
    if sleeve:
        limb(ctx, [S, E, Hh], sleeve, w + 8, 4)
    else:
        limb(ctx, [S, E, Hh], color, w, 4)
    if hand:
        circle(ctx, Hh[0], Hh[1], 9)
        fill_stroke(ctx, skin, 3.5)
    return Hh


# ===================================================================== main
def draw_char(ctx, x, y, s, lk: Look, ps: Pose, lod=None):
    if ps.alpha <= 0.01:
        return
    if lod is None:
        lod = s * lk.scale < 0.3
    ctx.save()
    ctx.translate(x, y)
    if ps.alpha < 0.999:
        ctx.push_group()
    ctx.scale(s * lk.scale * ps.face, s * lk.scale)
    if ps.fall:
        f = ps.fall
        ctx.translate(-20 * f, 0)
        ctx.rotate(-f * PI / 2 * 0.95)
    if ps.tilt:
        ctx.rotate(ps.tilt)
    bob = 0.0
    if ps.walk is not None:
        bob = -abs(math.sin(ps.walk)) * (7 if ps.run else 4)
    elif not ps.sit and not ps.fall:
        bob = math.sin(ps.t * 2.2 + lk.seed) * 1.4
    ctx.translate(0, bob - ps.jump)
    if ps.sit:
        ctx.translate(0, 34)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    k = lk.kind
    robe = k in ("persian", "immortal", "xerxes", "herald", "woman", "elder", "guest", "demaratus")
    armored = k in ("spartan", "greek") and lk.helmet is not None
    sleeve = lk.cloth if k in ("persian", "immortal", "xerxes", "herald", "mede", "scout",
                               "demaratus", "guest") else None
    arm_col = lk.skin

    # ---- far arm & weapon (behind body)
    far_sh = (-4, SHO + 8)
    weapon_hand = None
    spear_ang = 0.0
    if ps.weapon in ("spear", "sword", "stick", "torch", "comb", "short_spear") and ps.arm2 is None:
        if ps.weapon in ("spear", "short_spear"):
            if ps.grip == "rest":
                weapon_hand = (24, -104)
                spear_ang = -PI / 2
            elif ps.grip == "march":
                weapon_hand = (16, -104)
                spear_ang = -PI / 2 - 0.55
            elif ps.grip == "low":
                weapon_hand = (10 + 46 * ps.thrust, -86)
                spear_ang = -0.05
            else:  # ready / thrust (overhand)
                weapon_hand = (-6 + 52 * ps.thrust, -150 + 8 * ps.thrust)
                spear_ang = 0.13
        elif ps.weapon == "sword":
            sw = ps.thrust
            weapon_hand = (8 + 44 * sw, -150 + 60 * sw)
            spear_ang = -1.2 + 1.5 * sw
        elif ps.weapon == "stick":
            weapon_hand = (26 + 20 * ps.thrust, -110 - 30 * ps.thrust)
            spear_ang = -1.2 + 1.6 * ps.thrust
        elif ps.weapon == "torch":
            weapon_hand = (26, -128)
        elif ps.weapon == "comb":
            weapon_hand = (-20 + 10 * math.sin(ps.t * 6), -175 + 25 * math.sin(ps.t * 6))
    elif ps.arm2 is not None:
        weapon_hand = ps.arm2

    if lk.kind in ("persian", "immortal", "mede") and ps.weapon != "bow":
        # quiver on the back
        ctx.save()
        ctx.translate(-26, -100)
        ctx.rotate(-0.4)
        rrect(ctx, -9, -40, 18, 70, 5)
        fill_stroke(ctx, "#7a4a24", 3.5)
        for i in range(3):
            limb(ctx, [(-5 + i * 5, -40), (-6 + i * 5, -56)], "#e8e0d0", 2, 1.5)
        ctx.restore()

    _cloak(ctx, lk, ps)
    if k == "spartan" and lk.long_hair and lk.helmet:
        # long hair peeking under the helmet
        _long_hair(ctx, replace(lk), ps, back=True)

    if weapon_hand is not None:
        Hh = _arm(ctx, far_sh, weapon_hand, shade(arm_col, -0.12), sleeve=shade(sleeve, -0.15) if sleeve else None,
                  bend=-1, skin=shade(lk.skin, -0.1))
        if ps.weapon == "spear":
            draw_spear(ctx, Hh[0], Hh[1], spear_ang, 300, 0.33 if ps.grip not in ("rest", "march") else 0.34,
                       broken=ps.broken, tip="#d8a640")
        elif ps.weapon == "short_spear":
            draw_spear(ctx, Hh[0], Hh[1], spear_ang, 200, 0.45 if ps.grip != "rest" else 0.5,
                       broken=ps.broken, tip="#c8c8c8", short=True)
        elif ps.weapon == "sword":
            draw_sword(ctx, Hh[0], Hh[1], spear_ang)
        elif ps.weapon == "stick":
            draw_spear(ctx, Hh[0], Hh[1], spear_ang, 120, 0.2, color="#8a6a3a", tip=None, butt=False,
                       broken=True) if False else limb(
                ctx, [(Hh[0] - math.cos(spear_ang) * 20, Hh[1] - math.sin(spear_ang) * 20),
                      (Hh[0] + math.cos(spear_ang) * 95, Hh[1] + math.sin(spear_ang) * 95)],
                "#8a6a3a", 7, 3)
        elif ps.weapon == "torch":
            pass
        elif ps.weapon == "comb":
            rrect(ctx, Hh[0] - 4, Hh[1] - 18, 9, 24, 2)
            fill_stroke(ctx, "#e8d8b0", 2.5)
    else:
        _arm(ctx, far_sh, (-14, -66), shade(arm_col, -0.12), sleeve=shade(sleeve, -0.15) if sleeve else None,
             bend=-1, skin=shade(lk.skin, -0.1))

    # ---- legs & torso
    _legs(ctx, lk, ps, robe=k in ("mede", "scout"))
    _torso(ctx, lk, ps)

    # raised shield: the arm goes behind the head so the face stays visible
    if ps.shield == "up" and k in ("spartan", "greek", "persian", "immortal", "mede"):
        _arm(ctx, (8, SHO + 10), (18, -220), arm_col, sleeve=sleeve, skin=lk.skin)

    # ---- head
    if lk.long_hair and not lk.helmet and k in ("spartan", "greek", "woman", "trainer", "man",
                                                  "demaratus", "ephialtes"):
        _long_hair(ctx, lk, ps, back=True)
    if k == "woman":
        circle(ctx, -0.85 * R, HY - 0.35 * R, 0.33 * R)   # hair bun
        fill_stroke(ctx, lk.hair, 4)
    skin = _head_base(ctx, lk, ps)
    if not armored and k not in ("persian", "immortal", "herald", "mede", "scout"):
        _ear(ctx, lk)
    if k == "boy":
        _shaved(ctx, lk)
    if ps.blush or k in ("woman",):
        for bx in (0.0, 0.62):
            ellipse(ctx, bx * R, HY + 0.3 * R, 0.13 * R, 0.08 * R)
            src(ctx, (0.95, 0.45, 0.45, 0.45))
            ctx.fill()
    # beard below eyes
    bstyle = {"persian": "long", "immortal": "long", "xerxes": "long", "herald": "long",
              "mede": "long", "scout": "short", "elder": "elder"}.get(k, "short")
    if lk.beard:
        _beard(ctx, lk, bstyle)
    if armored:
        pass
    _nose(ctx, lk)
    _eyes(ctx, lk, ps, lod)
    _mouth(ctx, lk, ps, lod)
    if ps.green > 0.3 and not lod:
        for i in range(3):
            ctx.move_to(-0.3 * R + i * 0.3 * R, HY - 0.75 * R)
            ctx.rel_line_to(0, 10)
        src(ctx, (0.3, 0.55, 0.2, ps.green)); ctx.set_line_width(4); ctx.stroke()

    # headgear
    if armored:
        _spartan_helmet(ctx, lk, ps)
    elif k in ("persian", "herald", "scout"):
        _persian_hood(ctx, lk, ps, lk.hood, tall=k == "herald")
    elif k == "immortal":
        _persian_hood(ctx, lk, ps, lk.hood)
        ctx.arc_negative(0, HY, 0.99 * R, -0.35, -PI * 0.9)
        src(ctx, "#f2c23a"); ctx.set_line_width(7); ctx.stroke()
    elif k == "mede":
        _persian_hood(ctx, lk, ps, "#8a5a32", tall=True)
    elif k == "xerxes":
        _crown(ctx, lk)
    elif k == "elder":
        _short_hair(ctx, lk, bald=True)
    elif k in ("woman",):
        _long_hair(ctx, lk, ps, back=False)
        ctx.arc_negative(0, HY, 0.98 * R, -0.5, -PI * 0.95)
        src(ctx, lk.cloth2); ctx.set_line_width(6); ctx.stroke()
    elif k in ("spartan", "greek", "demaratus", "trainer", "man", "guest", "ephialtes"):
        if lk.long_hair:
            _long_hair(ctx, lk, ps, back=False)
        else:
            _short_hair(ctx, lk)
        if k == "demaratus":
            ctx.arc_negative(0, HY, 0.98 * R, -0.4, -PI * 0.95)
            src(ctx, "#f2f2f2"); ctx.set_line_width(6); ctx.stroke()
    if ps.bandage:
        ctx.arc_negative(0, HY, 1.0 * R if not armored else 1.1 * R, -0.3, -PI * 1.0)
        src(ctx, OUT); ctx.set_line_width(14); ctx.stroke_preserve()
        src(ctx, "#f4f1ea"); ctx.set_line_width(9); ctx.stroke()

    if ps.sweat and not lod:
        ctx.move_to(-0.55 * R, HY - 0.45 * R)
        ctx.curve_to(-0.75 * R, HY - 0.15 * R, -0.35 * R, HY - 0.15 * R, -0.55 * R, HY - 0.45 * R)
        fill_stroke(ctx, "#9fd8ff", 2.5)

    # ---- near arm & shield (in front)
    near_sh = (8, SHO + 10)
    if ps.shield != "none" and k in ("spartan", "greek", "persian", "immortal", "mede"):
        wick = k in ("persian", "immortal", "mede")
        if ps.shield == "front":
            hand = (34, -86)
            _arm(ctx, near_sh, hand, arm_col, sleeve=sleeve, skin=lk.skin)
            if wick:
                draw_wicker(ctx, 40, -96, 58, 104, "#c9a46a" if k != "immortal" else "#d9b46a")
            else:
                draw_shield(ctx, 38, -94, 62, lk.shield, lk.emblem, sx=0.82)
        elif ps.shield == "up":
            if wick:
                draw_wicker(ctx, 18, -236, 104, 34)
            else:
                draw_shield(ctx, 16, -238, 66, lk.shield, lk.emblem, sx=1.0, sy=0.33)
        elif ps.shield == "side":
            hand = (30, -72)
            _arm(ctx, near_sh, hand, arm_col, sleeve=sleeve, skin=lk.skin)
            if wick:
                draw_wicker(ctx, 38, -58, 50, 92)
            else:
                draw_shield(ctx, 40, -60, 54, lk.shield, lk.emblem, sx=0.45)
        elif ps.shield == "ground":
            _arm(ctx, near_sh, ps.arm or (24, -70), arm_col, sleeve=sleeve, skin=lk.skin)
    else:
        if ps.weapon == "bow":
            hand = (52, -132)
            _arm(ctx, near_sh, hand, arm_col, sleeve=sleeve, skin=lk.skin)
            mid = draw_bow(ctx, hand[0] + 30, hand[1], ps.thrust)
            _arm(ctx, near_sh, (mid[0] + 2, mid[1]), shade(arm_col, -0.05), sleeve=sleeve, skin=lk.skin)
        elif ps.arm is not None:
            hand = _arm(ctx, near_sh, ps.arm, arm_col, sleeve=sleeve, skin=lk.skin)
            if ps.weapon == "torch":
                draw_torch(ctx, hand[0], hand[1] - 10, ps.t, 0.9)
            elif ps.weapon == "scroll":
                rrect(ctx, hand[0] - 6, hand[1] - 34, 18, 64, 6)
                fill_stroke(ctx, "#f1e2b8", 3)
            elif ps.weapon == "cup":
                poly(ctx, [(hand[0] - 14, hand[1] - 24), (hand[0] + 14, hand[1] - 24),
                           (hand[0] + 8, hand[1] + 2), (hand[0] - 8, hand[1] + 2)])
                fill_stroke(ctx, "#b8742e", 3)
        else:
            hand = (22, -68) if not ps.sit else (30, -74)
            _arm(ctx, near_sh, hand, arm_col, sleeve=sleeve, skin=lk.skin)
            if ps.weapon == "torch":
                pass

    if ps.alpha < 0.999:
        ctx.pop_group_to_source()
        ctx.restore()
        ctx.save()
        ctx.paint_with_alpha(ps.alpha)
    ctx.restore()


# ===================================================================== extras
def draw_baby(ctx, x, y, s=1.0, t=0.0, cry=False, eyes="happy"):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ellipse(ctx, 0, 0, 46, 26)
    fill_stroke(ctx, "#f3ead6", 4)
    ctx.move_to(-30, -18); ctx.line_to(-8, 22)
    ctx.move_to(-10, -24); ctx.line_to(14, 22)
    src(ctx, "#d8cbb0"); ctx.set_line_width(3); ctx.stroke()
    circle(ctx, 32, -10, 22)
    fill_stroke(ctx, SKIN, 4)
    ellipse(ctx, 30, 2, 5, 3); src(ctx, (0.95, 0.45, 0.45, 0.5)); ctx.fill()
    if eyes == "happy" and not cry:
        for ex in (26, 40):
            ctx.arc_negative(ex, -10, 4, -0.2 * PI, -0.8 * PI)
            src(ctx, OUT); ctx.set_line_width(2.5); ctx.stroke()
        ctx.arc(34, -3, 5, 0.2 * PI, 0.8 * PI); ctx.stroke()
    else:
        for ex in (26, 40):
            circle(ctx, ex, -12, 2.8); src(ctx, OUT); ctx.fill()
        ellipse(ctx, 34, 0, 4 + (3 if cry else 0), 3 + (3 if cry else 0))
        src(ctx, "#5b1a1c"); ctx.fill()
    ctx.restore()


def draw_tag(ctx, x, y, label, s=1.0, rot=-0.04, color="#ffffff", fg="#1a1410", alpha=1.0):
    """White name label like the channel thumbnails (e.g. 'BALIKÇI')."""
    from .core import font, text_w
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    font(ctx, "Baloo 2 ExtraBold", 34)
    w = text_w(ctx, label) + 34
    rrect(ctx, -w / 2 + 4, -26 + 5, w, 50, 12)
    src(ctx, (0, 0, 0, 0.35 * alpha)); ctx.fill()
    rrect(ctx, -w / 2, -26, w, 50, 12)
    fill_stroke(ctx, color, 4, alpha=alpha)
    text(ctx, label, 0, 12, "Baloo 2 ExtraBold", 34, fg, alpha=alpha)
    ctx.restore()


# ---------------------------------------------------------------- presets
def spartan(seed=0, **kw):
    hair = ["#3a2415", "#5a3518", "#2a1a10", "#6b4423"][seed % 4]
    base = dict(kind="spartan", beard=hair, hair=hair, seed=seed)
    base.update(kw)
    return Look(**base)


def leonidas(**kw):
    base = dict(kind="spartan", beard="#3b2a1e", hair="#3b2a1e", king=True,
                helmet="#e0ac3c", crest="#d4202a", cloak="#b5121d", seed=11, spk="LEO")
    base.update(kw)
    return Look(**base)


def greek(seed=0, cloak="#2f5f9a", shield="#e9e2cf", emblem="star", **kw):
    hair = ["#3a2415", "#5a3518", "#2a1a10"][seed % 3]
    base = dict(kind="spartan", beard=hair, hair=hair, seed=seed, cloak=cloak, cloth="#2f5f9a",
                crest="#2a2a2a", shield=shield, emblem=emblem)
    base.update(kw)
    return Look(**base)


def persian(seed=0, **kw):
    cols = [("#2f6db3", "#f2d36b"), ("#c8862a", "#f6edd8"), ("#7a3f8f", "#f2d36b"),
            ("#3f8a5a", "#f6edd8"), ("#b33a3a", "#f2d36b")]
    c1, c2 = cols[seed % len(cols)]
    hood = ["#efe6d2", "#e3d3b0", "#f4efe4", "#d8c49a"][seed % 4]
    base = dict(kind="persian", cloth=c1, cloth2=c2, beard="#221510", hair="#221510",
                helmet=None, cloak=None, seed=seed, skin="#d9a77a", hood=hood)
    base.update(kw)
    return Look(**base)


def immortal(seed=0, **kw):
    cols = [("#e0b13a", "#f6edd8"), ("#6b3f8f", "#f2d36b"), ("#e0b13a", "#2f6db3")]
    c1, c2 = cols[seed % len(cols)]
    base = dict(kind="immortal", cloth=c1, cloth2=c2, beard="#1a100c", hair="#1a100c",
                helmet=None, cloak=None, seed=seed, skin="#d39f72", hood="#f6f1e6")
    base.update(kw)
    return Look(**base)


def mede(seed=0, **kw):
    cols = [("#b5562a", "#5a4632"), ("#4f7f3a", "#6b4a2a"), ("#8a6a2a", "#3f3f5a")]
    c1, c2 = cols[seed % len(cols)]
    base = dict(kind="mede", cloth=c1, cloth2=c2, beard="#221510", hair="#221510",
                helmet=None, cloak=None, seed=seed, skin="#d9a77a")
    base.update(kw)
    return Look(**base)


def xerxes(**kw):
    base = dict(kind="xerxes", cloth="#5b2a86", cloth2="#f2c23a", beard="#120c0a",
                hair="#120c0a", helmet=None, cloak=None, seed=21, skin="#d6a072", spk="XER")
    base.update(kw)
    return Look(**base)
