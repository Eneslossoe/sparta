# -*- coding: utf-8 -*-
"""Chapters I-III: birth, agoge, Spartan life (common mess)."""
import math

import cairo

from draw import backgrounds as bg
from draw import fx, overlay
from draw.characters import (HY, R, SKIN, Look, Pose, draw_baby, draw_char, draw_shield, spartan)
from draw.core import (OUT, PI, Cam, cam_lerp, circle, clamp, ease, ease_back, ease_out, ellipse,
                       fill_stroke, lerp, limb, noise1, poly, prog, rad_grad, rng, rrect, shade,
                       src, text)
from .common import G, H, W, set_sparta, shots, tag_pop, talk, world

FATHER = Look(kind="spartan", helmet=None, cloth="#a8222b", cloak="#8a1a20", beard="#4a2a16",
              hair="#4a2a16", seed=3)
ELDERS = [Look(kind="elder", cloth=c, hair="#f2f2f2", beard="#f2f2f2", helmet=None, cloak=None,
               seed=i, spk="ELD" if i == 1 else None)
          for i, c in enumerate(("#e8dcc0", "#d9c9a0", "#efe6d2"))]
MOTHER = Look(kind="woman", cloth="#2f6db3", cloth2="#f2d36b", hair="#4a2a16", helmet=None,
              cloak=None, seed=4, spk="MOM")
BOY = Look(kind="boy", cloth="#8a3a2a", helmet=None, cloak=None, scale=0.72, seed=6, skin=SKIN)
TRAINER = Look(kind="trainer", cloth="#6b2a1a", hair="#2a1a10", beard="#2a1a10", helmet=None,
               cloak="#5a1a12", long_hair=False, seed=8, spk="TRN")
GUEST = Look(kind="guest", cloth="#2aa39a", cloth2="#f2c23a", hair="#3a2415", helmet=None,
             cloak=None, long_hair=False, seed=9, spk="GST")
RESEARCHER = Look(kind="man", cloth="#5a7a9a", hair="#6b4423", beard=None, helmet=None, cloak=None,
                  long_hair=False, seed=12)


def head_pos(x, y, s, face=1, lk=None):
    sc = s * (lk.scale if lk else 1.0)
    return x + face * 0.32 * R * sc, y + HY * sc


def glasses(ctx, x, y, s, face=1):
    ey = y + (HY - 0.02 * R) * s
    for ex in (0.06, 0.58):
        circle(ctx, x + face * ex * R * s, ey, 0.25 * R * s)
        src(ctx, OUT)
        ctx.set_line_width(4 * s)
        ctx.stroke()
    ctx.move_to(x + face * 0.31 * R * s, ey - 2 * s)
    ctx.line_to(x + face * 0.33 * R * s, ey - 2 * s)
    ctx.stroke()


def hat(ctx, x, y, s, face=1):
    hx_, hy_ = x + face * 0.0, y + (HY - 0.75 * R) * s
    ellipse(ctx, hx_, hy_ + 10 * s, 75 * s, 16 * s)
    fill_stroke(ctx, "#c9a46a", 4 * s)
    ctx.move_to(hx_ - 45 * s, hy_ + 8 * s)
    ctx.curve_to(hx_ - 45 * s, hy_ - 55 * s, hx_ + 45 * s, hy_ - 55 * s, hx_ + 45 * s, hy_ + 8 * s)
    ctx.close_path()
    fill_stroke(ctx, "#c9a46a", 4 * s)
    ctx.rectangle(hx_ - 45 * s, hy_ - 6 * s, 90 * s, 12 * s)
    src(ctx, "#6b4423")
    ctx.fill()


# ======================================================================= BIRTH
def birth(ctx, S, lt):
    ins, ver, cl = S.t("inspect"), S.t("verdict"), S.t("cliff")
    last = [b for b in S.beats][-1].start - S.start
    shot, st, sl = shots(lt, S.dur, [(0, "walk"), (ins, "inspect"), (ver, "verdict"), (cl, "cliff"),
                              (last, "research")])
    if shot == "walk":
        k = ease(prog(lt, 0.5, ins))
        fx_ = lerp(250, 1050, k)
        cam = cam_lerp(Cam(800, 560, 1.0), Cam(1150, 600, 1.12), k)
        with world(ctx, cam):
            set_sparta(ctx, lt)
            bg.olive(ctx, 1480, 860, 1.3, lt)
            rrect(ctx, 1280, 790, 380, 26, 6)
            fill_stroke(ctx, "#8a6a3a", 4)
            for i, lk in enumerate(ELDERS):
                draw_char(ctx, 1340 + i * 120, 860, 0.9, lk, Pose(face=-1, t=lt + i, sit=True,
                                                                  weapon="none", shield="none"))
            walking = 0.5 < lt < ins - 0.2
            draw_char(ctx, fx_, 880, 1.0, FATHER,
                      Pose(face=1, t=lt, walk=lt * 8 if walking else None, weapon="none",
                           shield="none", arm=(38, -104), eyes="normal"))
            draw_baby(ctx, fx_ + 46, 880 - 108, 0.75, lt, eyes="happy")
            tag_pop(ctx, fx_ + 70, 880 - 175, "SEN", lt, 1.2, ins - 0.3, s=0.9)
        return {"vignette": 0.45}

    if shot in ("inspect", "verdict"):
        verdict = shot == "verdict"
        cam = cam_lerp(Cam(1270, 700, 1.5), Cam(1320, 690, 1.6 if not verdict else 1.75),
                       ease(prog(lt, ins, ver + 3)))
        with world(ctx, cam):
            set_sparta(ctx, lt, houses=False)
            bg.olive(ctx, 1480, 860, 1.3, lt)
            rrect(ctx, 1280, 790, 380, 26, 6)
            fill_stroke(ctx, "#8a6a3a", 4)
            for i, lk in enumerate(ELDERS):
                ex = 1340 + i * 120
                lift = 0
                arm = None
                eyes = "normal"
                if i == 1:
                    lift = ease_back(prog(lt, ver - 0.3, ver + 0.4)) if verdict else 0
                    arm = (34, -120 - 70 * lift)
                    eyes = "happy" if verdict else "normal"
                else:
                    eyes = "normal"
                ps = Pose(face=-1, t=lt + i, sit=True, weapon="none", shield="none", arm=arm,
                          eyes=eyes, look=(-0.5, -0.3) if i != 1 else (0, -0.6),
                          mouth=talk("ELD") if i == 1 else 0,
                          mshape="smile" if verdict else "line")
                draw_char(ctx, ex, 860, 0.9, lk, ps)
            # baby in the middle elder's hands
            rot = math.sin(lt * 3.0) * 0.35 if not verdict else 0
            lift = ease_back(prog(lt, ver - 0.3, ver + 0.4)) if verdict else 0
            ctx.save()
            ctx.translate(1460 - 32 * 0.9, 860 - 120 * 0.9 + 30 - 70 * 0.9 * lift)
            ctx.rotate(rot)
            draw_baby(ctx, 0, 0, 0.62, lt, eyes="happy" if verdict else "open")
            ctx.restore()
            if verdict and lift > 0.6:
                for i in range(6):
                    a = i * PI / 3 + lt
                    circle(ctx, 1432 + math.cos(a) * 70, 690 - 63 * lift + math.sin(a) * 50, 5)
                    src(ctx, (1, 0.95, 0.6, 0.8))
                    ctx.fill()
            # father watching, nervous
            draw_char(ctx, 1150, 900, 1.0, FATHER,
                      Pose(face=1, t=lt, weapon="none", shield="none",
                           eyes="scared" if not verdict else "happy", sweat=not verdict,
                           mshape="smile" if verdict else "wavy"))
        return {"vignette": 0.5}

    if shot == "cliff":
        cam = cam_lerp(Cam(960, 540, 1.0), Cam(960, 600, 1.15), ease(prog(st, 0, sl)))
        with world(ctx, cam):
            bg.sky(ctx, -300, -300, 2300, 1300, "#2a3448", "#7a8aa0")
            bg.mountains(ctx, 41, -400, 2400, 700, 520, "#4a5068", rough=1.2, outline=False,
                         snow="#c8d0e0")
            # ravine
            poly(ctx, [(-300, 760), (700, 740), (820, 1300), (-300, 1300)])
            fill_stroke(ctx, "#5a5a68", 4)
            poly(ctx, [(1250, 720), (2300, 700), (2300, 1300), (1120, 1300)])
            fill_stroke(ctx, "#545466", 4)
            ctx.set_source(rad_grad(960, 1100, 50, 500, [(0, (0, 0, 0, 0.95)), (1, (0.1, 0.1, 0.15, 0.6))]))
            poly(ctx, [(700, 740), (1250, 720), (1120, 1300), (820, 1300)])
            ctx.fill()
            for i in range(5):
                y = 820 + i * 50
                ctx.set_source(rad_grad(960 + noise1(lt * 0.3 + i, 3) * 200, y, 0, 500,
                                        [(0, (0.85, 0.88, 0.95, 0.35)), (1, (0.85, 0.88, 0.95, 0))]))
                ellipse(ctx, 960 + noise1(lt * 0.3 + i, 3) * 200, y, 700, 70)
                ctx.fill()
            overlay.caption(ctx, 1920, 1080, "TAYGETOS DAĞI", st, 0.4, sl - 0.2, x=500, y=300)
        return {"vignette": 0.8}

    # research: modern archaeologist with a question mark
    cam = Cam(960, 560, 1.0)
    with world(ctx, cam):
        bg.sky(ctx, -300, -300, 2300, 1300, "#9fc8e0", "#e8e0d0")
        bg.mountains(ctx, 41, -400, 2400, 760, 420, "#8a8aa8", rough=1.2, outline=False,
                     snow="#f0f0f8")
        bg.ground(ctx, -300, 2300, 860, 1300, "#c9b08a", seed=4)
        # scroll
        k = ease_back(prog(st, 0.3, 0.9))
        ctx.save()
        ctx.translate(1300, 520)
        ctx.scale(k, k)
        ctx.rotate(-0.06)
        rrect(ctx, -230, -150, 460, 300, 20)
        fill_stroke(ctx, "#f1e2b8", 5)
        for yy in (-150, 150):
            rrect(ctx, -250, yy - 18, 500, 36, 18)
            fill_stroke(ctx, "#c9a46a", 5)
        text(ctx, "PLUTARKHOS", 0, -40, "Cinzel Black", 54, "#5a3a1a")
        for i in range(4):
            ctx.move_to(-170, 10 + i * 30)
            ctx.line_to(170 - (i % 2) * 60, 10 + i * 30)
        src(ctx, (0.35, 0.25, 0.15, 0.6))
        ctx.set_line_width(5)
        ctx.stroke()
        ctx.restore()
        q = ease_back(prog(st, 1.6, 2.1))
        if q > 0:
            text(ctx, "?", 1560, 400, "Cinzel Black", 260 * q, "#e8402a", outline=OUT, olw=10,
                 shadow=(6, 8))
        x = 650
        draw_char(ctx, x, 900, 1.5, RESEARCHER,
                  Pose(face=1, t=lt, weapon="none", shield="none", arm=(40, -150),
                       eyes="normal", look=(1, -0.3), mshape="frown"))
        glasses(ctx, x, 900, 1.5)
        hat(ctx, x, 900, 1.5)
        tag_pop(ctx, x, 470, "MODERN ARAŞTIRMACI", st, 0.4, sl - 0.2, s=0.9)
    return {"vignette": 0.4}


def birth_sfx(S):
    t0 = S.start
    return [(t0 + 0.6, "birds", 0.35, 0.0), (t0 + 1.4, "baby", 0.4, -0.2),
            (t0 + S.t("inspect") + 0.5, "baby", 0.35, 0.3), (t0 + S.t("verdict") + 0.2, "sparkle", 0.5, 0.0),
            (t0 + S.t("cliff"), "wind", 0.45, 0.0), (t0 + S.t("cliff") + 1.5, "crow", 0.3, 0.6),
            ([b for b in S.beats][-1].start + 0.4, "pop", 0.5, 0.2),
            ([b for b in S.beats][-1].start + 1.7, "boing", 0.45, 0.4)]


# ======================================================================= AGOGE
def reeds(ctx, x0, x1, y, t, seed=1, pulled=None):
    r = rng(seed)
    for i in range(int((x1 - x0) / 22)):
        x = x0 + i * 22 + r.uniform(-6, 6)
        h = r.uniform(120, 200)
        sw = math.sin(t * 1.4 + i * 0.7) * 8
        if pulled and pulled[0] < x < pulled[1]:
            continue
        ctx.move_to(x, y)
        ctx.curve_to(x, y - h * 0.5, x + sw * 0.5, y - h * 0.8, x + sw, y - h)
        src(ctx, OUT)
        ctx.set_line_width(7)
        ctx.stroke_preserve()
        src(ctx, "#8aa04a" if i % 3 else "#a8b85a")
        ctx.set_line_width(4)
        ctx.stroke()
        ellipse(ctx, x + sw, y - h, 5, 16)
        fill_stroke(ctx, "#8a5a2b", 2.5)


def agoge(ctx, S, lt):
    tk = S.t("taken")
    b = S.beats
    t_name = b[1].start - S.start
    t_run = S.t("run")
    t_cloak = b[3].start - S.start
    t_reed, t_steal, t_caught = S.t("reeds"), S.t("steal"), S.t("caught")
    t_whack = b[7].start - S.start
    shot, st, sl = shots(lt, S.dur, [(0, "home"), (t_name, "name"), (t_run, "run"), (t_cloak, "cloak"),
                              (t_reed, "reed"), (t_steal, "steal"), (t_whack, "whack")])
    if shot == "home":
        k = ease(prog(lt, tk + 1.2, tk + 5.5))
        cam = cam_lerp(Cam(860, 720, 1.8), Cam(1330, 720, 1.8), k)
        with world(ctx, cam):
            set_sparta(ctx, lt)
            bg.house(ctx, 640, 870, 1.2)
            leaving = lt > tk + 1.2
            bx = 820 + 600 * k
            tx = 960 + 600 * k
            draw_char(ctx, 700, 880, 1.0, MOTHER,
                      Pose(face=1, t=lt, weapon="none", shield="none",
                           arm=(40, -150 + 20 * math.sin(lt * 6)) if leaving else (60, -90),
                           eyes="sad", mshape="frown"))
            draw_char(ctx, tx, 885, 1.05, TRAINER,
                      Pose(face=1 if leaving else -1, t=lt, walk=lt * 7 if leaving and k < 1 else None,
                           weapon="stick" if not leaving else "none", shield="none",
                           arm=(-40, -60) if leaving else None, eyes="angry", mshape="line"))
            draw_char(ctx, bx, 885, 1.0, BOY,
                      Pose(face=-1 if leaving else -1, t=lt, walk=lt * 9 if leaving and k < 1 else None,
                           weapon="none", shield="none", eyes="sad", mshape="frown",
                           arm=(30, -80)))
            tag_pop(ctx, bx, 680, "SEN · 7 YAŞ", lt, tk + 0.3, t_name - 0.3, s=0.9)
        return {"vignette": 0.45}

    if shot == "name":
        with world(ctx, Cam(960, 540, 1.0 + 0.03 * st)):
            bg.sky(ctx, -100, -100, 2100, 1200, "#e8b070", "#f6e3b4")
            bg.ground(ctx, -100, 2100, 820, 1200, "#c9a46a", seed=9)
            for i in range(8):
                draw_char(ctx, 280 + i * 200, 900, 0.95, BOY,
                          Pose(face=1, t=lt + i, weapon="none", shield="none", eyes="normal"))
            draw_char(ctx, 1780, 900, 1.05, TRAINER,
                      Pose(face=-1, t=lt, weapon="stick", shield="none", eyes="angry"))
        k = ease_back(prog(st, 0.15, 0.45), 2.5)
        sc = 2.4 - 1.4 * k
        if st > 0.15:
            ctx.save()
            ctx.translate(960, 400)
            ctx.scale(sc, sc)
            ctx.rotate(-0.05)
            text(ctx, "AGOGE", 0, 60, "Cinzel Black", 190, "#c8202a", outline="#2a0c06", olw=12,
                 shadow=(8, 10), alpha=clamp(k * 1.5))
            ctx.restore()
            fx.dust(ctx, 960, 470, st - 0.45, seed=3, n=10, size=3)
        return {"vignette": 0.5}

    if shot == "run":
        scroll = st * 420
        with world(ctx, Cam(960, 560, 1.0)):
            bg.sky(ctx, -100, -100, 2100, 1200, "#8ac8ea", "#f2e2c0")
            ctx.save()
            ctx.translate(-scroll * 0.15, 0)
            bg.mountains(ctx, 21, -400, 3000, 700, 400, "#8f8fb0", snow="#f4f4fa")
            ctx.restore()
            ctx.save()
            ctx.translate(-scroll * 0.5, 0)
            bg.hills(ctx, 7, -200, 4400, 820, 90, "#a8b86a")
            ctx.restore()
            bg.ground(ctx, -100, 2100, 860, 1200, "#c4a87a", pebbles=False)
            r = rng(4)
            for i in range(40):
                x = (i * 137 - scroll) % 2300 - 200
                bg.rock(ctx, x, 920 + (i % 3) * 40, 0.25 + (i % 4) * 0.08, seed=i)
            for i in range(4):
                x = 640 + i * 330 + math.sin(lt * 1.3 + i) * 30
                draw_char(ctx, x, 990 + (i % 2) * 30, 1.75, BOY,
                          Pose(face=1, t=lt + i, walk=lt * 13 + i, run=True, weapon="none",
                               shield="none", eyes="angry" if i % 2 else "normal",
                               sweat=True, mshape="line"))
            draw_char(ctx, 250 + math.sin(lt * 1.1) * 20, 1030, 1.5, TRAINER,
                      Pose(face=1, t=lt, walk=lt * 12, run=True, weapon="stick",
                           thrust=pulse_(lt), shield="none", eyes="angry", mshape="shout"))
        # crossed-out sandal icon
        k = ease_back(prog(st, 1.6, 2.0))
        if k > 0:
            ctx.save()
            ctx.translate(1620, 230)
            ctx.scale(k, k)
            circle(ctx, 0, 0, 95)
            fill_stroke(ctx, "#ffffff", 7)
            ellipse(ctx, 0, 10, 55, 26)
            fill_stroke(ctx, "#8a5a2b", 5)
            for dx in (-25, 0, 25):
                ctx.move_to(dx, -15); ctx.line_to(dx * 0.6, 30)
            src(ctx, "#5a3a1a"); ctx.set_line_width(5); ctx.stroke()
            ctx.move_to(-62, -62); ctx.line_to(62, 62)
            src(ctx, "#d4202a"); ctx.set_line_width(16); ctx.stroke()
            circle(ctx, 0, 0, 95)
            ctx.set_line_width(12); ctx.stroke()
            ctx.restore()
        return {"vignette": 0.45}

    if shot == "cloak":
        # split screen: summer / winter
        for side in (0, 1):
            ctx.save()
            if side == 0:
                poly(ctx, [(0, 0), (1060, 0), (860, H), (0, H)])
            else:
                poly(ctx, [(1060, 0), (W, 0), (W, H), (860, H)])
            ctx.clip()
            if side == 0:
                bg.sky(ctx, 0, 0, W, H, "#ffb050", "#ffe8a0")
                bg.sun(ctx, 300, 200, 80, glow="#ff8a2a")
                bg.ground(ctx, 0, W, 820, H, "#e0b070", pebbles=False)
                draw_char(ctx, 480, 1000, 2.5, BOY, Pose(face=1, t=lt, weapon="none", shield="none",
                                                        eyes="sad", sweat=True, mshape="wavy"))
                text(ctx, "YAZ", 330, 170 + 200, "Cinzel Black", 90, "#ffffff", outline=OUT, olw=8)
            else:
                bg.sky(ctx, 0, 0, W, H, "#5a7aa8", "#c8d8ec")
                bg.ground(ctx, 0, W, 820, H, "#eef4fa", pebbles=False)
                fx.particles(ctx, lt, 860, 0, W, H, n=90, seed=2, kind="snow")
                shiver = math.sin(lt * 40) * 4
                draw_char(ctx, 1440 + shiver, 1000, 2.5, replace_(BOY, skin="#e8c8b8"),
                          Pose(face=-1, t=lt, weapon="none", shield="none", eyes="scared",
                               mshape="wavy", arm=(20, -90)))
                text(ctx, "KIŞ", 1640, 370, "Cinzel Black", 90, "#ffffff", outline=OUT, olw=8)
            ctx.restore()
        ctx.move_to(1060, 0); ctx.line_to(860, H)
        src(ctx, "#ffffff"); ctx.set_line_width(14); ctx.stroke()
        overlay.banner(ctx, 960, 140, "YILDA TEK PELERİN", size=50)
        return {"vignette": 0.35}

    if shot == "reed":
        pull_x = 1000
        with world(ctx, Cam(860, 730, 1.75)):
            bg.sky(ctx, -200, -200, 2200, 1300, "#8ac8ea", "#f2e8c8")
            bg.hills(ctx, 9, -300, 2300, 700, 120, "#9fbf6a")
            bg.sea(ctx, -300, 2300, 700, 820, lt, color="#5aa0c8", deep="#3a7aa8")
            bg.ground(ctx, -300, 2300, 820, 1300, "#9a9a5a", pebbles=False)
            reeds(ctx, 100, 1900, 840, lt, pulled=(pull_x - 140, pull_x + 40))
            n_pile = int(clamp(st / sl) * 9)
            for i in range(n_pile):
                limb(ctx, [(560 + i * 6, 900 - i * 7), (760 + i * 4, 892 - i * 7)], "#a8b85a", 6, 2.5)
            yank = abs(math.sin(st * 3.2))
            draw_char(ctx, pull_x - 60, 900, 1.2, BOY,
                      Pose(face=1, t=lt, weapon="none", shield="none", tilt=-0.2 * yank,
                           arm=(60 - 30 * yank, -110 - 20 * yank), eyes="angry", sweat=True,
                           mshape="line"))
            # reed in hand
            hx_, hy_ = pull_x - 60 + (60 - 30 * yank) * 1.2 * 0.72 + 20, 900 - (110 + 20 * yank) * 1.2 * 0.72
            limb(ctx, [(hx_, hy_ + 60), (hx_ + 10, hy_ - 120)], "#a8b85a", 5, 2.5)
        overlay.caption(ctx, 1920, 1080, "EUROTAS NEHRİ", st, 0.3, sl - 0.2, x=80, y=200)
        return {"vignette": 0.45}

    if shot in ("steal", "whack"):
        caught = lt >= t_caught
        whack = shot == "whack"
        sneak = ease(prog(lt, t_steal + 0.3, t_steal + 3.6))
        bx = lerp(250, 900, sneak)
        grabbed = lt > t_steal + 3.8
        with world(ctx, Cam(lerp(560, 940, sneak) if not caught else 840, 740, 1.7 if not caught else 2.0)):
            bg.sky(ctx, -300, -300, 2300, 1300, "#0b1430", "#2a3a6a")
            bg.stars(ctx, -300, -300, 2300, 600, lt)
            bg.moon(ctx, 1600, 160, 40)
            bg.ground(ctx, -300, 2300, 880, 1300, "#3a3a4a", pebbles=False)
            bg.house(ctx, 1500, 880, 1.2, wall="#8a8aa0", roof="#5a3a4a")
            rrect(ctx, 960, 790, 300, 22, 5)
            fill_stroke(ctx, "#6b4a2a", 4)
            for lx in (980, 1220):
                rrect(ctx, lx, 810, 18, 70, 3)
                fill_stroke(ctx, "#6b4a2a", 3.5)
            if not grabbed:
                ellipse(ctx, 1040, 778, 50, 22)
                fill_stroke(ctx, "#d9a05a", 4)
            ellipse(ctx, 1150, 782, 36, 18)
            fill_stroke(ctx, "#f2e6b0", 4)
            circle(ctx, 1200, 774, 16)
            fill_stroke(ctx, "#c83a3a", 3.5)
            jump = ease_out(prog(lt, t_whack + 0.35, t_whack + 0.6)) * (1 - ease(prog(lt, t_whack + 0.6, t_whack + 1.1))) * 60
            draw_char(ctx, bx, 900, 1.0, BOY,
                      Pose(face=1, t=lt, walk=lt * 5 if 0 < sneak < 1 else None, tilt=0.18 if not caught else 0,
                           weapon="none", shield="none",
                           arm=(40, -100) if grabbed else (50, -60),
                           eyes="sly" if not caught else ("scared" if not whack or lt < t_whack + 0.35 else "dead"),
                           sweat=caught, mshape="grin" if grabbed and not caught else ("o" if caught else "line"),
                           jump=jump, look=(1, 0) if not caught else (-1, 0)))
            if grabbed:
                ellipse(ctx, bx + 45, 900 - 108, 40, 18)
                fill_stroke(ctx, "#d9a05a", 4)
            if caught:
                k = ease_back(prog(lt, t_caught, t_caught + 0.35))
                hit = prog(lt, t_whack + 0.1, t_whack + 0.4)
                draw_char(ctx, bx - 190, 900, 1.15 * k, TRAINER,
                          Pose(face=1, t=lt, weapon="stick", shield="none",
                               thrust=1.0 * math.sin(hit * PI) if whack else 0.0,
                               eyes="angry", mouth=talk("TRN"), mshape="line"))
                if whack:
                    fx.pow_star(ctx, bx + 10, 900 - 200, lt - (t_whack + 0.35), 2.0)
                    for i in range(3):
                        a = lt * 4 + i * 2.1
                        if lt > t_whack + 0.5:
                            fx_s = bx + 30 + math.cos(a) * 60
                            text(ctx, "★", fx_s, 900 - 230 + math.sin(a) * 20, "DejaVu Sans", 40,
                                 "#ffe14a", outline=OUT, olw=4)
        return {"vignette": 0.6}
    return {}


def pulse_(t):
    return max(0.0, math.sin(t * 5)) ** 2


def replace_(lk, **kw):
    from dataclasses import replace
    return replace(lk, **kw)


def agoge_sfx(S):
    t0 = S.start
    b = S.beats
    ev = [(t0 + S.t("taken") + 1.0, "footsteps", 0.35, 0.3),
          (b[1].start + 0.15, "stamp", 0.9, 0.0)]
    tr = S.t("run")
    for i in range(int((b[3].start - S.start - tr) / 0.18)):
        ev.append((t0 + tr + i * 0.18, "step", 0.22, (i % 2) * 0.4 - 0.2))
    ev.append((t0 + tr + 1.6, "pop", 0.5, 0.5))
    ev.append((b[3].start, "whoosh", 0.5, 0.0))
    ev.append((b[3].start + 0.3, "wind_cold", 0.4, 0.6))
    tr2 = S.t("reeds")
    for i in range(5):
        ev.append((t0 + tr2 + 0.5 + i * 0.98, "snap", 0.4, 0.0))
    ev.append((t0 + S.t("steal") + 3.8, "pop", 0.35, 0.0))
    ev.append((t0 + S.t("caught"), "sting", 0.7, 0.0))
    ev.append((b[7].start + 0.35, "bonk", 0.9, 0.0))
    ev.append((b[7].start + 0.5, "birdies", 0.5, 0.0))
    return ev


# ======================================================================= MESS
def table_scene(ctx, lt, seed=0, laugh=0.0, guest=None, cam=None, stand=0.0):
    bg.sky(ctx, -400, -400, 2400, 1400, "#4a2a1a", "#7a4a2a")
    # wall stones + torches
    r = rng(3)
    for j in range(12):
        for i in range(16):
            rrect(ctx, -400 + i * 180 + (j % 2) * 90, -300 + j * 90, 176, 86, 8)
            src(ctx, shade("#6b4a32", r.uniform(-0.1, 0.06)))
            ctx.fill()
    for tx in (300, 960, 1620):
        ctx.set_source(rad_grad(tx, 380, 10, 420, [(0, (1, 0.7, 0.3, 0.45)), (1, (1, 0.6, 0.2, 0))]))
        circle(ctx, tx, 380, 420)
        ctx.fill()
        bg.fire(ctx, tx, 400, 0.45, lt, seed=tx)
        limb(ctx, [(tx, 400), (tx, 470)], "#3a2a1a", 12, 3)
    bg.ground(ctx, -400, 2400, 880, 1400, "#5a3a24", pebbles=False)
    # Spartans behind the table
    for i in range(6):
        x = 260 + i * 260
        lk = spartan(i, helmet=None, cloak="#8a1a20")
        hap = laugh > 0 and i != 3
        ps = Pose(face=1 if i < 3 else -1, t=lt + i, sit=stand <= 0, weapon="none", shield="none",
                  arm=(46, -96 - 10 * math.sin(lt * 3 + i)) if not hap else (40, -140),
                  eyes="happy" if hap else "normal",
                  mouth=(0.6 + 0.4 * abs(math.sin(lt * 12 + i))) * laugh if hap else 0,
                  mshape="smile", jump=abs(math.sin(lt * 10 + i)) * 6 * laugh)
        if i == 2 and guest is not None:
            continue
        draw_char(ctx, x, 812 - 40 * stand, 1.0, lk, ps)
    if guest is not None:
        guest(ctx)
    rrect(ctx, 80, 800, 1760, 40, 8)
    fill_stroke(ctx, "#8a5a32", 5)
    rrect(ctx, 100, 840, 1720, 80, 4)
    src(ctx, "#5a3a20")
    ctx.fill()
    for i in range(6):
        bowl(ctx, 300 + i * 260, 798, 1.0, lt + i)


def bowl(ctx, x, y, s=1.0, t=0.0, big=False):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-46, -24)
    ctx.curve_to(-40, 20, 40, 20, 46, -24)
    ctx.close_path()
    fill_stroke(ctx, "#b8742e", 4)
    ellipse(ctx, 0, -24, 46, 10)
    fill_stroke(ctx, "#1a1210", 3.5)
    for i in range(3):
        ph = (t * 0.8 + i * 0.33) % 1.0
        circle(ctx, -20 + i * 18, -26 - ph * 8, 3 + ph * 4)
        src(ctx, (0.25, 0.18, 0.15, 1 - ph))
        ctx.fill()
    ctx.restore()


def ingredient(ctx, kind, x, y, k):
    if k <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(k, k)
    circle(ctx, 0, 0, 90)
    fill_stroke(ctx, "#fff6e0", 6)
    if kind == "pig":
        circle(ctx, 0, 0, 50)
        fill_stroke(ctx, "#f4a0b0", 5)
        ellipse(ctx, 0, 14, 22, 15)
        fill_stroke(ctx, "#e88098", 4)
        for dx in (-8, 8):
            circle(ctx, dx, 14, 4); src(ctx, OUT); ctx.fill()
        for dx in (-18, 18):
            circle(ctx, dx, -14, 5); src(ctx, OUT); ctx.fill()
        poly(ctx, [(-44, -24), (-34, -56), (-16, -40)]); fill_stroke(ctx, "#f4a0b0", 4)
        poly(ctx, [(44, -24), (34, -56), (16, -40)]); fill_stroke(ctx, "#f4a0b0", 4)
        label = "DOMUZ ETİ"
    elif kind == "blood":
        ctx.move_to(0, -56)
        ctx.curve_to(40, -6, 40, 44, 0, 46)
        ctx.curve_to(-40, 44, -40, -6, 0, -56)
        fill_stroke(ctx, "#b8121a", 5)
        label = "KAN"
    elif kind == "vinegar":
        rrect(ctx, -24, -20, 48, 70, 10)
        fill_stroke(ctx, "#6a8a3a", 5)
        rrect(ctx, -10, -50, 20, 34, 4)
        fill_stroke(ctx, "#6a8a3a", 4)
        rrect(ctx, -12, -62, 24, 14, 3)
        fill_stroke(ctx, "#8a5a2b", 3.5)
        label = "SİRKE"
    else:
        poly(ctx, [(-50, 40), (0, -40), (50, 40)])
        fill_stroke(ctx, "#f8f8f8", 5)
        label = "TUZ"
    ctx.restore()
    text(ctx, label, x, y + 140 * k, "Baloo 2 ExtraBold", 44 * k, "#ffffff", outline=OUT, olw=7 * k)


def mess(ctx, S, lt):
    t_soup, t_taste, t_gag, t_joke, t_war = (S.t("soup"), S.t("taste"), S.t("gag"), S.t("joke"),
                                            S.t("war"))
    l1 = S.beats[0]
    t_bar = l1.start - S.start + (l1.speech_end - l1.start) * 0.42
    shot, st, sl = shots(lt, S.dur, [(0, "soldier"), (t_bar, "barracks"), (t_soup, "soup"),
                              (t_taste, "table"), (t_war, "war")])
    if shot == "soldier":
        with world(ctx, Cam(960, 560, 1.0 + 0.04 * st)):
            set_sparta(ctx, lt, houses=True)
            draw_char(ctx, 960, 960, 1.9, spartan(1, spk="SEN"),
                      Pose(face=1, t=lt, grip="rest", shield="side", eyes="normal", mshape="smile"))
            tag_pop(ctx, 960, 300, "SEN · 20 YAŞ", lt, 0.6, t_bar - 0.2)
        return {"vignette": 0.45}

    if shot == "barracks":
        with world(ctx, Cam(960, 560, 1.05)):
            bg.sky(ctx, -200, -200, 2200, 1300, "#1a1a30", "#2a2a48")
            for i in range(10):
                rrect(ctx, -200 + i * 240, -100, 236, 1100, 4)
                src(ctx, shade("#3a3048", (i % 2) * 0.05))
                ctx.fill()
            bg.ground(ctx, -200, 2200, 880, 1300, "#3a2a2a", pebbles=False)
            for i in range(4):
                x = 280 + i * 420
                rrect(ctx, x - 150, 860, 300, 30, 8)
                fill_stroke(ctx, "#8a7a52", 4)
                draw_char(ctx, x + 90, 862, 0.9, spartan(i, helmet=None, cloak="#6a1a20"),
                          Pose(face=1, t=lt, fall=1.0, weapon="none", shield="none", eyes="closed",
                               blink=False, mshape="line"))
                ph = (lt * 0.6 + i * 0.3) % 1.0
                text(ctx, "Z", x - 50 + ph * 40, 760 - ph * 120, "Baloo 2 ExtraBold", 40 + 30 * ph,
                     "#ffffff", outline=OUT, olw=5, alpha=1 - ph)
            tag_pop(ctx, 280 + 90, 620, "SEN", lt, t_bar + 0.3)
        return {"vignette": 0.6}

    if shot == "soup":
        with world(ctx, Cam(960, 600, 1.0)):
            bg.sky(ctx, -200, -200, 2200, 1300, "#3a2014", "#6a3a22")
            rrect(ctx, -100, 760, 2200, 600, 10)
            fill_stroke(ctx, "#8a5a32", 5)
            bowl(ctx, 960, 760, 4.2, lt)
            for i in range(5):
                ph = (lt * 0.4 + i * 0.2) % 1.0
                ctx.set_source(rad_grad(900 + i * 30, 560 - ph * 300, 0, 80,
                                        [(0, (0.9, 0.9, 0.9, 0.3 * (1 - ph))), (1, (1, 1, 1, 0))]))
                circle(ctx, 900 + i * 30, 560 - ph * 300, 80)
                ctx.fill()
        text(ctx, "KARA ÇORBA", 960, 170, "Cinzel Black", 90, "#f6e3b4", outline="#2a0c06", olw=8,
             alpha=ease_out(prog(st, 0.1, 0.5)), shadow=(4, 6))
        cs = [("pig", 300, 470), ("blood", 650, 330), ("vinegar", 1270, 330), ("salt", 1620, 470)]
        line = S.tag("soup")
        dur = line.speech_end - line.start
        for i, (kind, x, y) in enumerate(cs):
            t_i = dur * (0.52 + i * 0.11)
            ingredient(ctx, kind, x, y, ease_back(prog(st, t_i, t_i + 0.35)) * 1.25)
        return {"vignette": 0.6}

    if shot == "table":
        gag = clamp(prog(lt, t_gag, t_gag + 0.4))
        joking = lt >= t_joke
        laugh = ease(prog(lt, t_joke + 1.2, t_joke + 1.6))
        spoon = ease(prog(lt, t_taste + 1.2, t_taste + 2.4))
        z = 1.0 + 0.35 * ease(prog(lt, t_gag - 0.2, t_gag + 0.3)) * (1 - ease(prog(lt, t_joke + 1.0, t_joke + 1.6)))

        def guest(ctx_):
            x = 780
            draw_char(ctx_, x, 812, 1.0, GUEST,
                      Pose(face=1, t=lt, sit=True, weapon="none", shield="none",
                           arm=(46, -96 - 70 * spoon) if gag <= 0 else (30, -70),
                           green=gag * 0.9 if not joking else 0.7, eyes="wide" if gag > 0 else "normal",
                           mouth=talk("GST"), mshape="wavy" if gag > 0 else "line",
                           sweat=gag > 0))
            if gag <= 0:
                hx_ = x + 46 * 1.0
                limb(ctx_, [(hx_ + 5, 812 - 96 + 30 - 70 * spoon), (hx_ + 22, 812 - 150 - 70 * spoon + 50)],
                     "#c9a46a", 4, 2)
        shake = 6 if t_gag < lt < t_gag + 0.6 else 0
        with world(ctx, Cam(780 if z > 1.05 else 960, 640 - 40 * (z - 1), 1.3 * z), shake=shake, t=lt):
            table_scene(ctx, lt, laugh=laugh, guest=guest)
        tag_pop(ctx, 780 if z < 1.05 else 960, 420 if z < 1.05 else 260, "MİSAFİR", lt, t_taste + 0.3,
                t_taste + 3.0)
        return {"vignette": 0.55}

    # war: Spartans rise, red sky
    k = ease(prog(st, 0, 1.6))
    with world(ctx, Cam(960, 560, 1.0 + 0.05 * st)):
        bg.sky(ctx, -200, -200, 2200, 1300, "#3a0a06", "#d8502a")
        bg.sun(ctx, 960, 760, 170, "#ffcf7a", "#ff6a2a", 0.6)
        bg.ground(ctx, -200, 2200, 900, 1300, "#2a120a", pebbles=False)
        for i in range(7):
            x = 240 + i * 240
            draw_char(ctx, x, 980, 1.25, spartan(i),
                      Pose(face=1, t=lt + i, grip="rest", shield="front",
                           eyes="angry", jump=-40 * (1 - k)))
    a = ease_back(prog(st, 1.0, 1.5))
    if a > 0:
        ctx.save()
        ctx.translate(960, 300)
        ctx.scale(a, a)
        text(ctx, "SAVAŞ", 0, 50, "Cinzel Black", 170, "#f6e3b4", outline="#2a0c06", olw=12,
             shadow=(6, 8))
        ctx.restore()
    return {"vignette": 0.7, "letterbox": 1.0}


def mess_sfx(S):
    t0 = S.start
    l1 = S.beats[0]
    t_bar = l1.start + (l1.speech_end - l1.start) * 0.42
    ev = [(t0 + 0.3, "fanfare_small", 0.4, 0.0), (t_bar, "snore", 0.45, -0.3),
          (t_bar + 1.4, "snore", 0.35, 0.3), (t0 + S.t("soup"), "bubbles", 0.5, 0.0)]
    line = S.tag("soup")
    dur = line.speech_end - line.start
    for i in range(4):
        ev.append((line.start + dur * (0.52 + i * 0.11), "pop", 0.55, -0.5 + i * 0.33))
    ev += [(t0 + S.t("taste") + 2.3, "slurp", 0.6, -0.1), (t0 + S.t("gag"), "gag", 0.8, -0.1),
           (t0 + S.t("joke") + 1.2, "laugh", 0.7, 0.0), (t0 + S.t("war"), "drum_hit", 0.9, 0.0),
           (t0 + S.t("war") + 1.0, "boom", 0.8, 0.0)]
    return ev
