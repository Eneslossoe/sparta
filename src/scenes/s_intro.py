# -*- coding: utf-8 -*-
"""Cold open (arrows darken the sun) + title card."""
import math

import cairo

from draw import backgrounds as bg
from draw import fx, overlay
from draw.characters import Look, Pose, draw_char, mede, persian, spartan
from draw.core import (Cam, cam_lerp, clamp, ease, ease_back, ease_out, lerp, prog, rng, src,
                       text)
from .common import (G, H, W, phalanx, set_thermopylae, shots, tag_pop, talk, world)

DIENEKES = dict(seed=5, beard="#8a7a6a", hair="#8a7a6a", spk="DIE")
SOLDIER = dict(seed=2, spk="SOL")


def _darkness(lt, S):
    return 0.55 * ease(prog(lt, S.t("dark"), S.t("arrows") + 1.0))


def cold_open(ctx, S, lt):
    shot, st, sl = shots(lt, S.dur, [(0, "wide"), (S.t("dark"), "archers"), (S.t("sol"), "sol"),
                              (S.t("die"), "die"), (S.t("impact"), "impact")])
    dark = _darkness(lt, S)
    if shot == "wide":
        cam = cam_lerp(Cam(960, 560, 1.0), Cam(900, 600, 1.12), ease(prog(lt, 0, sl)))
        with world(ctx, cam):
            set_thermopylae(ctx, lt, "dawn", wall=(380, 760, 70))
            # Persian host on the right, far away
            r = rng(4)
            for row in range(6, -1, -1):
                for i in range(22):
                    x = 1250 + i * 52 + (row % 2) * 26 + r.uniform(-8, 8)
                    y = 860 - row * 14
                    lk = persian(seed=(i + row) % 5) if (i + row) % 3 else mede(seed=i % 3)
                    draw_char(ctx, x, y, 0.3 - row * 0.015, lk,
                              Pose(face=-1, t=lt + i, weapon="short_spear", grip="rest",
                                   shield="front"), lod=True)
            phalanx(ctx, lt, 720, 868, s=0.42, lanes=3, ranks=5, grip="rest", eyes="normal")
        overlay.caption(ctx, W, H, "TERMOPİL GEÇİDİ · YUNANİSTAN", lt, S.t("fadein"),
                        S.t("dark") - 0.1)
        return {"letterbox": 1.0, "vignette": 0.7}

    if shot == "archers":
        cam = cam_lerp(Cam(1100, 640, 1.15), Cam(1000, 560, 1.05), ease(prog(st, 0, sl)))
        rel = S.t("arrows") + 0.3 - S.t("dark")
        with world(ctx, cam):
            set_thermopylae(ctx, lt, "dawn")
            for row in range(2, -1, -1):
                for i in range(9):
                    x = 700 + i * 150 + row * 60
                    draw_char(ctx, x, 900 - row * 34, 0.95 - row * 0.08, mede(seed=(i + row) % 3),
                              Pose(face=-1, t=lt + i * 0.3, weapon="bow", shield="none",
                                   thrust=ease(prog(st, 0.2, rel - 0.1)) if st < rel else 0.0,
                                   eyes="angry"))
            if st > rel:
                fx.volley(ctx, st, rel, 11, 60, (650, 650, 2000, 760), (-900, -300, 200, 200),
                          dur=1.6, apex=500, size=1.2, stuck=False)
        fx.tint(ctx, W, H, "#202838", dark * 0.8)
        return {"letterbox": 1.0, "vignette": 0.7}

    if shot in ("sol", "die"):
        spk = "SOL" if shot == "sol" else "DIE"
        cam = cam_lerp(Cam(960, 560, 1.0), Cam(960, 540, 1.06), ease(prog(st, 0, sl)))
        with world(ctx, cam):
            bg.sky(ctx, -200, -200, 2200, 1300, "#2a3448", "#c8906a")
            bg.sun(ctx, 1500, 260, 60, "#fff2c0", "#ffb070", 0.3)
            fx.tint(ctx, W, H, "#101828", dark * 0.7)
            fx.arrow_cloud(ctx, lt, -300, 2300, 60, 520, density=1.6, seed=5, ang=-0.25 + 0.5,
                           speed=700, size=0.9)
            if shot == "sol":
                lk = spartan(**SOLDIER)
                ps = Pose(face=1, t=lt, shield="side", grip="rest", eyes="scared", sweat=True,
                          look=(0.6, -1.2), mouth=talk("SOL"))
                draw_char(ctx, 800, 1150, 3.4, lk, ps)
            else:
                lk = spartan(**DIENEKES)
                ps = Pose(face=-1, t=lt, shield="side", grip="rest",
                          eyes="sly",
                          mshape="smile" if talk("DIE") < 0.1 else "line", mouth=talk("DIE"))
                draw_char(ctx, 1120, 1150, 3.4, lk, ps)
        if shot == "die":
            tag_pop(ctx, 1300, 260, "DİENEKES", st, 0.2, sl - 0.3)
        return {"letterbox": 1.0, "vignette": 0.8}

    # impact: shields up, arrows rain
    cam = Cam(960, 600, 1.0)
    land0 = 0.15
    shake = 9 * prog(st, land0 + 1.0, land0 + 1.3) * (1 - prog(st, 2.4, 3.2))
    with world(ctx, cam, shake=shake, t=lt):
        set_thermopylae(ctx, lt, "dawn", wall=(-200, 260, 90))
        phalanx(ctx, lt, 1500, 900, s=1.05, lanes=3, ranks=6, shield="up", grip="rest",
                eyes="angry", spacing=96)
        fx.volley(ctx, st, land0 - 0.9, 21, 90, (2100, -500, 2600, -300), (300, 560, 1650, 720),
                  dur=1.9, apex=-80, size=1.1, spread=1.0, stuck_len=0.6)
        fx.volley(ctx, st, land0 - 0.6, 22, 40, (2100, -500, 2600, -300), (0, 880, 1900, 1000),
                  dur=2.0, apex=-60, size=1.1, spread=1.4, stuck_len=0.5)
    fx.tint(ctx, W, H, "#202838", dark * 0.6)
    fl = prog(st, sl - 0.35, sl)
    fx.flash(ctx, W, H, fl, "#fff6e0")
    return {"letterbox": 1.0, "vignette": 0.7}


def cold_open_sfx(S):
    t0 = S.start
    ev = [(t0 + 0.0, "wind", 0.5, 0.0), (t0 + 2.0, "horn", 0.35, 0.5)]
    dark = S.t("dark")
    rel = S.t("arrows") + 0.3
    ev.append((t0 + dark + 0.3, "bow_creak", 0.45, 0.4))
    ev.append((t0 + rel, "bow_release", 0.8, 0.3))
    ev.append((t0 + rel + 0.1, "arrow_swarm", 0.75, -0.2))
    imp = S.t("impact")
    ev.append((t0 + imp - 0.1, "shields_up", 0.7, 0.0))
    for tl in fx.volley_land_times(21, 90, 1.9, 1.0):
        ev.append((t0 + imp + 0.15 - 0.9 + tl, "arrow_thunk", 0.22, 0.0))
    for tl in fx.volley_land_times(22, 40, 2.0, 1.4)[::2]:
        ev.append((t0 + imp + 0.15 - 0.6 + tl, "arrow_ground", 0.18, 0.0))
    ev.append((t0 + S.dur - 0.35, "whoosh_big", 0.6, 0.0))
    return ev


# ---------------------------------------------------------------- title
def title(ctx, S, lt):
    br = S.t("break")
    bg.sky(ctx, 0, 0, W, H, "#1a0a06", "#8a2a12", "#4a160c")
    bg.sun(ctx, W / 2, 760, 160, "#ffcf7a", "#ff6a2a", 0.5)
    fx.particles(ctx, lt, 0, 0, W, H, n=70, seed=3, kind="embers")
    # silhouette phalanx on the horizon
    ctx.push_group()
    r = rng(2)
    for i in range(18):
        x = 60 + i * 108
        draw_char(ctx, x, 1010 + (i % 2) * 14, 0.95, spartan(i),
                  Pose(face=1 if i < 9 else -1, t=lt + i, grip="rest", shield="front"))
    pat = ctx.pop_group()
    src(ctx, "#0c0604")
    ctx.mask(pat)
    ctx.rectangle(0, 990, W, 200)
    src(ctx, "#0c0604")
    ctx.fill()

    k = ease_back(prog(lt, 0.0, 0.9))
    crack_p = prog(lt, br, br + 0.8)
    overlay.hourglass(ctx, W / 2, 330, 0.95 * k, lt, crack_p=crack_p, alpha=clamp(lt / 0.4))
    # title text
    from draw.core import font, text_w
    font(ctx, "Cinzel Black", 230)
    w1 = text_w(ctx, "300")
    font(ctx, "Cinzel Black", 92)
    w2 = text_w(ctx, "SPARTALIDAN BİRİ")
    x0 = W / 2 - (w1 + 40 + w2) / 2
    a1 = ease_out(prog(lt, 1.0, 1.6))
    text(ctx, "300", x0 + w1 / 2, 670, "Cinzel Black", 230 * (0.8 + 0.2 * a1), "#e8b04a",
         outline="#2a0c06", olw=12, alpha=a1, shadow=(6, 8))
    a2 = ease_out(prog(lt, 1.5, 2.1))
    cx2 = x0 + w1 + 40 + w2 / 2
    text(ctx, "SPARTALIDAN BİRİ", cx2, 600, "Cinzel Black", 92, "#f6e3b4",
         outline="#2a0c06", olw=8, alpha=a2, shadow=(5, 6))
    a3 = ease_back(prog(lt, 2.2, 2.7))
    if a3 > 0:
        overlay.banner(ctx, cx2, 680, "OLSAYDIN?", size=64, s=a3, alpha=clamp(a3))
    if lt > br + 0.3:
        fx.crack(ctx, W, H, prog(lt, br + 0.3, S.dur + 0.25), seed=3)
    return {"vignette": 0.6, "letterbox": 0.0}


def title_sfx(S):
    t0 = S.start
    br = S.t("break")
    return [(t0 + 0.05, "boom", 0.9, 0.0), (t0 + 1.0, "drum_hit", 0.8, -0.3),
            (t0 + 1.5, "drum_hit", 0.8, 0.3), (t0 + 2.2, "whoosh", 0.6, 0.0),
            (t0 + 2.35, "drum_hit", 1.0, 0.0), (t0 + br, "tick", 0.5, 0.0),
            (t0 + br + 0.35, "glass_crack", 0.8, 0.0), (t0 + S.dur - 0.25, "glass_shatter", 0.9, 0.0)]
