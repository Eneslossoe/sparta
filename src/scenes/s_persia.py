# -*- coding: utf-8 -*-
"""Chapters IV-VI: Persian threat, the chosen 300, march, the pass, scout, Molon labe."""
import math
from dataclasses import replace

import cairo

from draw import backgrounds as bg
from draw import fx, overlay
from draw.characters import (HY, R, SKIN, Look, Pose, draw_char, draw_shield, greek, immortal,
                             leonidas, mede, persian, spartan, xerxes)
from draw.core import (OUT, PI, Cam, cam_lerp, circle, clamp, ease, ease_back, ease_out, ellipse,
                       fill_stroke, font, hx, lerp, limb, mix, noise1, poly, prog, rad_grad, rng,
                       rrect, shade, smooth_poly, src, text, text_w)
from .common import (G, H, W, phalanx, set_persian_camp, set_sparta, set_thermopylae, shots,
                     tag_pop, talk, world)

XER = xerxes()
LEO = leonidas()
YOU = spartan(1, spk="SEN")
MOTHER_OLD = Look(kind="woman", cloth="#5a3a6a", cloth2="#d9c08a", hair="#9a9090", helmet=None,
                  cloak=None, seed=4, spk="MOM")
DEMARATUS = Look(kind="demaratus", cloth="#2f5f9a", cloth2="#f2d36b", hair="#b0a89a",
                 beard="#b0a89a", helmet=None, cloak=None, seed=14, spk="DEM", long_hair=False)
SCOUT = Look(kind="scout", cloth="#7a5a3a", cloth2="#4a3a2a", beard="#221510", hair="#221510",
             helmet=None, cloak=None, seed=15, skin="#d9a77a", spk="SCT", hood="#d9c08a")
HERALD = Look(kind="herald", cloth="#c8862a", cloth2="#f6edd8", beard="#221510", hair="#221510",
              helmet=None, cloak=None, seed=16, skin="#d9a77a", spk="HER", hood="#f2d36b")


def palace(ctx, t, x0=-400, x1=2400, gy=880):
    bg.sky(ctx, x0, -600, x1, gy, "#5a2a3a", "#c87a4a")
    for i in range(9):
        rrect(ctx, x0 + i * 330, -300, 330, gy + 300, 0)
        src(ctx, shade("#a8643a", (i % 2) * 0.06 - 0.03))
        ctx.fill()
    for x in (150, 520, 1400, 1770):
        bg.column(ctx, x, gy, 560, 1.0)
    for x in (330, 1590):
        poly(ctx, [(x - 70, 130), (x + 70, 130), (x + 70, 600), (x, 650), (x - 70, 600)])
        fill_stroke(ctx, "#6b2a7a", 4)
        circle(ctx, x, 330, 34)
        fill_stroke(ctx, "#f2c23a", 4)
    bg.ground(ctx, x0, x1, gy - 10, gy + 600, "#8a5a3a", pebbles=False)
    for i in range(8):
        rrect(ctx, x0 + i * 340, gy + 30, 300, 60, 6)
        src(ctx, (0, 0, 0, 0.12))
        ctx.fill()


def pontoon(ctx, t, x0, x1, y, march_t=None):
    for i, x in enumerate(range(int(x0), int(x1), 130)):
        bob = math.sin(t * 1.6 + i) * 3
        ctx.move_to(x - 60, y + bob)
        ctx.curve_to(x - 50, y + 40 + bob, x + 50, y + 40 + bob, x + 60, y + bob)
        ctx.close_path()
        fill_stroke(ctx, "#7a4a2a", 4)
    rrect(ctx, x0 - 70, y - 14, x1 - x0 + 140, 16, 4)
    fill_stroke(ctx, "#b08a5a", 4)
    for x in range(int(x0) - 60, int(x1) + 70, 60):
        ctx.move_to(x, y - 14)
        ctx.line_to(x, y + 2)
    src(ctx, (0.3, 0.2, 0.1, 0.6))
    ctx.set_line_width(2)
    ctx.stroke()


# ======================================================================= PERSIA
def persia(ctx, S, lt):
    t_x, t_b, t_c = S.t("xer"), S.t("bridge"), S.t("count")
    t_l = S.beats[-1].start - S.start
    shot, st, sl = shots(lt, S.dur, [(0, "palace"), (t_x, "close"), (t_b, "bridge"), (t_c, "count"),
                              (t_l, "army")])
    if shot == "palace":
        cam = cam_lerp(Cam(960, 600, 1.15), Cam(980, 680, 1.6), ease(prog(lt, 0, sl)))
        with world(ctx, cam):
            palace(ctx, lt)
            bg.throne(ctx, 1000, 900, 1.0)
            draw_char(ctx, 960, 900 - 120, 1.0, XER,
                      Pose(face=1, t=lt, sit=True, weapon="none", shield="none", arm=(40, -120),
                           eyes="normal", mshape="smile"))
            for i, x in enumerate((360, 560, 1400, 1600)):
                draw_char(ctx, x, 920, 1.0, immortal(i),
                          Pose(face=1 if x < 960 else -1, t=lt + i, weapon="short_spear", grip="rest",
                               shield="front", eyes="normal"))
        tag_pop(ctx, 960, 200, "KRAL KSERKSES", lt, 4.5, sl - 0.2)
        return {"vignette": 0.55}

    if shot == "close":
        with world(ctx, Cam(960, 560, 1.0 + 0.04 * st), shake=3 if st > 3.4 else 0, t=lt):
            palace(ctx, lt)
            draw_char(ctx, 900, 1140, 3.2, XER,
                      Pose(face=1, t=lt, weapon="none", shield="none",
                           arm=(95, -125) if st > 0.6 else None, eyes="angry",
                           mouth=talk("XER"), mshape="line"))
        return {"vignette": 0.6, "letterbox": 1.0}

    if shot == "bridge":
        with world(ctx, Cam(960, 560, 1.0)):
            bg.sky(ctx, -200, -400, 2200, 700, "#7fc4ec", "#f2e3c0")
            bg.clouds(ctx, lt, seed=7, n=4, y0=60, y1=260)
            bg.hills(ctx, 3, -300, 600, 640, 140, "#a8b86a")
            bg.hills(ctx, 8, 1400, 2300, 640, 160, "#b8a86a")
            bg.sea(ctx, -200, 2200, 640, 1300, lt)
            pontoon(ctx, lt, 380, 1540, 760)
            for i in range(26):
                x = (200 + i * 60 + st * 90) % 1500 + 250
                if 360 < x < 1560:
                    lk = persian(i) if i % 3 else mede(i)
                    draw_char(ctx, x, 746, 0.42, lk,
                              Pose(face=1, t=lt + i, walk=lt * 7 + i, weapon="short_spear",
                                   grip="march", shield="front"), lod=True)
        overlay.caption(ctx, W, H, "ÇANAKKALE BOĞAZI (HELLESPONTOS)", st, 0.3, sl - 0.2, y=230)
        return {"vignette": 0.45}

    if shot == "count":
        line = S.tag("count")
        mid = (line.speech_end - line.start) * 0.5
        bg.sky(ctx, 0, 0, W, H, "#e8d6a8", "#d4bc88")
        r = rng(3)
        for i in range(50):
            ellipse(ctx, r.uniform(0, W), r.uniform(0, H), r.uniform(20, 90), r.uniform(10, 40))
            src(ctx, (0.6, 0.45, 0.25, 0.08))
            ctx.fill()
        ctx.move_to(W / 2, 120)
        ctx.line_to(W / 2, H - 160)
        src(ctx, (0.35, 0.25, 0.15, 0.6))
        ctx.set_line_width(4)
        ctx.stroke()
        # left: Herodotus
        k1 = ease_out(prog(st, 0.2, 2.0))
        text(ctx, "HERODOT'A GÖRE", W / 4, 200, "Cinzel Black", 54, "#5a3a1a")
        n1 = int(2_640_000 * k1)
        text(ctx, f"{n1:,}".replace(",", ".") + "+", W / 4, 330, "Cinzel Black", 96, "#b81e28",
             outline="#2a0c06", olw=5)
        rows = int(1 + 9 * k1)
        for j in range(rows):
            for i in range(14):
                draw_char(ctx, 120 + i * 52 + (j % 2) * 26, 520 + j * 42, 0.22,
                          persian(i + j) if (i + j) % 3 else mede(i), Pose(face=1, t=lt + i,
                          weapon="short_spear", grip="rest", shield="none"), lod=True)
        # right: modern estimate
        k2 = ease_out(prog(st, mid, mid + 1.6))
        if k2 > 0.005:
            text(ctx, "MODERN TAHMİN", 3 * W / 4, 200, "Cinzel Black", 54, "#5a3a1a")
            a, b = int(100_000 * k2), int(300_000 * k2)
            text(ctx, f"{a:,}–{b:,}".replace(",", "."), 3 * W / 4, 330, "Cinzel Black", 82,
                 "#2a5a8a", outline="#0a1a2a", olw=4)
            for j in range(int(1 + 2 * k2)):
                for i in range(14):
                    draw_char(ctx, 1080 + i * 52 + (j % 2) * 26, 520 + j * 42, 0.22,
                              persian(i + j), Pose(face=-1, t=lt + i, weapon="short_spear",
                                                   grip="rest", shield="none"), lod=True)
        return {"vignette": 0.35}

    # army: huge host marching across a plain
    with world(ctx, Cam(960, 540, 1.0 + 0.04 * st)):
        bg.sky(ctx, -200, -200, 2200, 800, "#e8a85a", "#f8e2b0")
        bg.sun(ctx, 1500, 300, 70, glow="#ffb060")
        bg.mountains(ctx, 51, -400, 2400, 640, 260, "#b08a6a", outline=False)
        bg.ground(ctx, -400, 2400, 620, 1300, "#d4b07a", pebbles=False)
        fx.dust_cloud(ctx, -200, 2200, 650, lt, seed=4, alpha=0.4, h=60)
        for row in range(12, -1, -1):
            for i in range(30):
                x = -200 + i * 85 + (row % 2) * 40 + (lt * 40) % 85
                y = 660 + row * 34
                draw_char(ctx, x, y, 0.22 + row * 0.022, persian(i + row) if (i + row) % 3 else mede(i),
                          Pose(face=1, t=lt + i, walk=lt * 7 + i + row, weapon="short_spear",
                               grip="march", shield="front"), lod=True)
    return {"vignette": 0.6, "letterbox": 1.0}


def persia_sfx(S):
    t0 = S.start
    ev = [(t0 + 0.4, "fanfare_persian", 0.55, 0.0), (t0 + S.t("xer") + 0.6, "boom", 0.5, 0.0),
          (t0 + S.t("bridge"), "waves", 0.5, 0.0), (t0 + S.t("bridge") + 0.2, "march_far", 0.5, 0.0),
          (t0 + S.t("count") + 0.2, "counter", 0.5, -0.4)]
    line = S.tag("count")
    ev.append((line.start + (line.speech_end - line.start) * 0.5, "counter", 0.5, 0.4))
    ev.append((S.beats[-1].start, "march_big", 0.7, 0.0))
    return ev


# ======================================================================= CHOSEN
def chosen(ctx, S, lt):
    t_leo, t_sons, t_you, t_ready, t_mom, t_sh = (S.t("leo"), S.t("sons"), S.t("you"), S.t("ready"),
                                                  S.t("mom"), S.t("shield"))
    shot, st, sl = shots(lt, S.dur, [(0, "festival"), (t_leo, "choose"), (t_sons, "sons"), (t_you, "you"),
                              (t_ready, "leo"), (t_mom, "mom"), (t_sh, "mom_close")])
    if shot == "festival":
        with world(ctx, Cam(960, 600, 1.15 + 0.03 * st)):
            set_sparta(ctx, lt, houses=False)
            bg.temple(ctx, 1300, 860, 1.0)
            rrect(ctx, 800, 780, 120, 80, 6)
            fill_stroke(ctx, "#d8d0c0", 4)
            bg.fire(ctx, 860, 785, 0.6, lt)
            bg.smoke(ctx, 860, 700, lt, 0.8)
            draw_char(ctx, 1000, 880, 1.0, Look(kind="elder", cloth="#f4f0e4", hair="#f2f2f2",
                                                beard="#f2f2f2", helmet=None, cloak=None),
                      Pose(face=-1, t=lt, weapon="none", shield="none",
                           arm=(30, -170 - 20 * math.sin(lt * 3)), eyes="closed", blink=False))
            for i in range(6):
                x = 200 + i * 105
                jump = abs(math.sin(lt * 5 + i)) * 26
                draw_char(ctx, x, 920 + (i % 2) * 20, 0.95, spartan(i, helmet=None, cloak="#8a1a20"),
                          Pose(face=1, t=lt + i, weapon="none", shield="none", jump=jump,
                               arm=(64, -118 + 8 * math.sin(lt * 12 + i)), eyes="happy",
                               mshape="smile"))
        overlay.caption(ctx, W, H, "KARNEİA BAYRAMI", st, 0.4, sl - 0.3, y=230)
        return {"vignette": 0.45}

    if shot in ("choose", "sons", "you"):
        sons = lt >= t_sons
        k = ease(prog(lt, t_leo, t_sons))
        if shot == "you":
            cam = cam_lerp(Cam(960, 600, 1.0), Cam(1145, 640, 1.9), ease_out(prog(st, 0, 0.8)))
        else:
            cam = Cam(960, 600, 1.0)
        with world(ctx, cam):
            set_sparta(ctx, lt, houses=True)
            for i in range(7):
                x = 330 + i * 210
                lk = YOU if i == 4 else spartan(i + 3)
                draw_char(ctx, x, 930, 1.0, lk,
                          Pose(face=-1 if i > 3 else 1, t=lt + i, grip="rest", shield="front",
                               eyes="normal"))
                if sons:
                    kk = ease_back(prog(lt, t_sons + i * 0.12, t_sons + i * 0.12 + 0.4))
                    if kk > 0:
                        draw_char(ctx, x + 70, 935, 0.8 * kk,
                                  Look(kind="boy", cloth="#8a3a2a", helmet=None, cloak=None,
                                       scale=0.8, seed=30 + i),
                                  Pose(face=1, t=lt + i, weapon="none", shield="none",
                                       eyes="happy", mshape="smile"))
            lx = lerp(150, 1700, k) if shot == "choose" else 1750
            walking = shot == "choose" and 0.02 < k < 0.98
            draw_char(ctx, lx, 970, 1.1, LEO,
                      Pose(face=1, t=lt, walk=lt * 6 if walking else None, grip="rest",
                           shield="side", eyes="angry", mshape="line",
                           arm=(60, -110) if not walking else None))
            if shot == "choose":
                tag_pop(ctx, lx, 600, "KRAL LEONİDAS", lt, t_leo + 0.4, t_sons - 0.2, s=0.9)
        if sons:
            a = ease_back(prog(lt, t_sons + 1.0, t_sons + 1.4))
            if shot == "sons" and a > 0:
                ctx.save()
                ctx.translate(960, 220)
                ctx.scale(a, a)
                text(ctx, "300", 0, 60, "Cinzel Black", 170, "#e8b04a", outline="#2a0c06", olw=10,
                     shadow=(5, 7))
                ctx.restore()
        if shot == "you":
            tag_pop(ctx, 1170, 330, "SEN", st, 0.6, sl, s=1.4)
            if st > 0.6:
                yy = 420 + math.sin(lt * 8) * 10
                poly(ctx, [(1150, yy), (1190, yy), (1170, yy + 40)])
                fill_stroke(ctx, "#ffffff", 4)
        return {"vignette": 0.45}

    if shot == "leo":
        with world(ctx, Cam(960, 560, 1.0 + 0.03 * st)):
            set_sparta(ctx, lt, houses=False, tod="day")
            draw_char(ctx, 900, 1140, 3.3, LEO,
                      Pose(face=1, t=lt, grip="rest", shield="none", eyes="angry",
                           mouth=talk("LEO"), mshape="line"))
        return {"vignette": 0.55, "letterbox": 1.0}

    # mother hands over the shield
    close = shot == "mom_close"
    handed = ease(prog(lt, t_mom + 2.5, t_mom + 4.0))
    cam = Cam(960, 600, 1.35) if not close else Cam(1180, 640, 2.0)
    with world(ctx, cam):
        set_sparta(ctx, lt, houses=True)
        bg.house(ctx, 1500, 880, 1.2)
        draw_char(ctx, 1240, 900, 1.05, MOTHER_OLD,
                  Pose(face=-1, t=lt, weapon="none", shield="none", arm=(46, -96),
                       eyes="angry" if close else "sad", mouth=talk("MOM"), mshape="line"))
        sx = lerp(1180, 860, handed)
        draw_char(ctx, 760, 900, 1.05, replace(YOU, cloak="#9f1d26"),
                  Pose(face=1, t=lt, grip="rest", shield="none", eyes="normal",
                       arm=(70, -96) if handed > 0.6 else None))
        draw_shield(ctx, sx, 795, 64, "#c99230", "lambda", sx=0.9)
    return {"vignette": 0.55, "letterbox": 1.0 if close else 0.0}


def chosen_sfx(S):
    t0 = S.start
    return [(t0 + 0.4, "crowd_cheer", 0.35, 0.0), (t0 + S.t("leo") + 0.3, "footsteps_armor", 0.4, -0.3),
            (t0 + S.t("sons") + 1.0, "drum_hit", 0.8, 0.0), (t0 + S.t("you") + 0.5, "whoosh", 0.5, 0.0),
            (t0 + S.t("you") + 0.7, "pop", 0.5, 0.0), (t0 + S.t("ready"), "boom", 0.5, 0.0),
            (t0 + S.t("mom") + 3.5, "shield_hand", 0.6, 0.0)]


# ======================================================================= MARCH
ALLIES = [("THESPİAİ · 700", "#2f5f9a", "#e9e2cf", "star"),
          ("THEBAİ · 400", "#3a3a3a", "#d8c8a0", "club"),
          ("FOKİS · 1000", "#2f7a4a", "#e9e2cf", "crescent"),
          ("KORİNTHOS · 400", "#8a5a2a", "#f0e0b0", "trident"),
          ("ARKADİA · 2000+", "#6a3a7a", "#e9e2cf", "bull")]


def march(ctx, S, lt):
    t7 = S.t("7000")
    scroll = lt * 160
    with world(ctx, Cam(960, 560, 1.0)):
        bg.sky(ctx, -200, -200, 2200, 900, "#7fc4ec", "#f2e3c0")
        bg.clouds(ctx, lt, seed=2, n=5, y0=60, y1=260)
        ctx.save()
        ctx.translate(-scroll * 0.1, 0)
        bg.mountains(ctx, 61, -400, 2800, 700, 360, "#9bb2c8", outline=False)
        ctx.restore()
        ctx.save()
        ctx.translate(-scroll * 0.4, 0)
        bg.hills(ctx, 12, -300, 3600, 800, 110, "#a8b86a")
        for x in range(0, 3600, 420):
            bg.olive(ctx, x, 800, 0.6, lt)
        ctx.restore()
        bg.ground(ctx, -200, 2200, 860, 1300, "#cdb27a", seed=5)
        # Spartan column
        for i in range(9):
            x = 1500 - i * 120
            draw_char(ctx, x, 950, 0.75, YOU if i == 2 else (LEO if i == 0 else spartan(i)),
                      Pose(face=1, t=lt + i, walk=lt * 7 + i * 0.5, grip="march", shield="front",
                           eyes="normal"))
        # allies join from the left in turn
        for j, (label, cloak, shield, em) in enumerate(ALLIES):
            tj = 1.0 + j * 1.8
            if lt < tj:
                continue
            k = ease_out(prog(lt, tj, tj + 2.2))
            base = lerp(-500, 300 - j * 40, k) - (lt - tj) * 25
            for i in range(3):
                draw_char(ctx, base - i * 95, 1000 + (j % 2) * 30, 0.7,
                          greek(j * 3 + i, cloak=cloak, shield=shield, emblem=em),
                          Pose(face=1, t=lt + i, walk=lt * 7 + i, grip="march", shield="front"))
            if lt < tj + 3.0:
                tag_pop(ctx, base - 95, 790 + (j % 2) * 30, label, lt, tj + 0.3, tj + 3.0, s=0.8)
    # counter
    k = ease(prog(lt, t7 + 0.8, t7 + 3.2))
    n = int(300 + (7000 - 300) * k)
    rrect(ctx, W - 470, 60, 400, 150, 18)
    src(ctx, (0.05, 0.03, 0.02, 0.75))
    ctx.fill()
    text(ctx, "YUNAN ASKERİ", W - 270, 112, "Baloo 2 ExtraBold", 36, "#e9c27a")
    text(ctx, ("~" if k > 0.5 else "") + f"{n:,}".replace(",", "."), W - 270, 190, "Cinzel Black",
         72, "#ffffff")
    return {"vignette": 0.45}


def march_sfx(S):
    t0 = S.start
    ev = []
    for i in range(int(S.dur / 0.43)):
        ev.append((t0 + i * 0.43, "march_step", 0.32, 0.0))
    for j in range(len(ALLIES)):
        ev.append((t0 + 1.3 + j * 1.8, "pop", 0.35, -0.5))
    ev.append((t0 + S.t("7000") + 0.8, "counter", 0.5, 0.6))
    return ev


# ======================================================================= PASS (map)
def tmap(ctx, t, focus=0.0):
    # parchment base
    bg.sky(ctx, -600, -600, 2600, 1700, "#ead8aa", "#d8c08a")
    # sea (north, top)
    pts = [(2600, 300), (2000, 360), (1500, 420), (1200, 470), (960, 500), (700, 470),
           (400, 400), (0, 330), (-600, 300)]
    smooth_poly(ctx, pts, close=False)
    ctx.line_to(-600, -900)
    ctx.line_to(2600, -900)
    ctx.close_path()
    fill_stroke(ctx, "#6aaad4", 5)
    src(ctx, (1, 1, 1, 0.5))
    ctx.set_line_width(3)
    for i in range(12):
        x = -300 + i * 240 + (t * 15) % 60
        ctx.move_to(x, 150 + (i % 3) * 50)
        ctx.rel_curve_to(15, -8, 30, -8, 45, 0)
    ctx.stroke()
    # mountains (south, bottom)
    mpts = [(-600, 600), (0, 640), (400, 600), (700, 560), (960, 548), (1200, 565), (1500, 610),
            (2000, 650), (2600, 620)]
    smooth_poly(ctx, mpts, close=False)
    ctx.line_to(2600, 1700)
    ctx.line_to(-600, 1700)
    ctx.close_path()
    fill_stroke(ctx, "#a8845a", 5)
    for i in range(30):
        x = -500 + i * 105
        y = 760 + (i % 3) * 120
        poly(ctx, [(x - 46, y + 40), (x, y - 40), (x + 46, y + 40)])
        fill_stroke(ctx, "#8a6a42", 4)
        poly(ctx, [(x - 12, y - 18), (x, y - 40), (x + 12, y - 18)])
        src(ctx, "#f0e6d0")
        ctx.fill()
    # road
    rp = [(-600, 450), (0, 480), (400, 500), (700, 515), (960, 524), (1200, 520), (1500, 515),
          (2000, 505), (2600, 470)]
    smooth_poly(ctx, rp, close=False)
    src(ctx, "#7a5a3a")
    ctx.set_line_width(10)
    ctx.set_dash([24, 14])
    ctx.stroke()
    ctx.set_dash([])


def pass_(ctx, S, lt):
    t_n, t_num, t_w = S.t("narrow"), S.t("numbers"), S.t("wall")
    shot, st, sl = shots(lt, S.dur, [(0, "map"), (t_n, "zoom"), (t_num, "numbers"), (t_w, "wall")])
    if shot in ("map", "zoom", "numbers"):
        if shot == "map":
            cam = Cam(960, 520, 0.75 + 0.05 * st / max(sl, 1))
        elif shot == "zoom":
            cam = cam_lerp(Cam(960, 520, 0.8), Cam(960, 530, 2.2), ease(prog(st, 0, 1.4)))
        else:
            cam = cam_lerp(Cam(960, 530, 2.2), Cam(960, 520, 1.1), ease(prog(st, 0, 1.0)))
        with world(ctx, cam):
            tmap(ctx, lt)
            if shot == "map":
                for lbl, x, y, a in (("DENİZ", 600, 200, prog(st, 0.5, 1.0)),
                                     ("DAĞLAR", 1300, 900, prog(st, 2.2, 2.7)),
                                     ("TERMOPİL", 960, 440, prog(st, 3.2, 3.7))):
                    text(ctx, lbl, x, y, "Cinzel Black", 70, "#3a2410", alpha=a,
                         outline="#f6ecd0", olw=6)
            if shot == "zoom":
                a = prog(st, 1.4, 1.8)
                for yy, d in ((498, -1), (552, 1)):
                    poly(ctx, [(960, yy), (952, yy - d * 14), (968, yy - d * 14)])
                    src(ctx, "#b81e28", a)
                    ctx.fill()
                ctx.move_to(960, 500)
                ctx.line_to(960, 550)
                src(ctx, "#b81e28", a)
                ctx.set_line_width(3)
                ctx.stroke()
                text(ctx, "TEK ARABA GENİŞLİĞİ", 1080, 535, "Baloo 2 ExtraBold", 18, "#b81e28",
                     alpha=a, align="left", outline="#f6ecd0", olw=4)
            if shot == "numbers":
                r = rng(9)
                for i in range(260):
                    ox = r.uniform(-500, 450)
                    oy = r.uniform(380, 640)
                    pr = ease(prog(st, 0.6 + r.random() * 0.8, 4.0 + r.random()))
                    x = lerp(ox, 900 - r.random() * 60, pr * 0.85)
                    y = lerp(oy, 524 + r.uniform(-14, 14), pr)
                    circle(ctx, x, y, 7)
                    fill_stroke(ctx, "#c8202a", 2)
                for i in range(12):
                    circle(ctx, 960 + (i % 4) * 16, 512 + (i // 4) * 12, 7)
                    fill_stroke(ctx, "#2a5aa8", 2)
                text(ctx, "PERSLER", 300, 360, "Cinzel Black", 60, "#b81e28", outline="#f6ecd0",
                     olw=6, alpha=prog(st, 0.5, 1.0))
                text(ctx, "YUNANLAR", 1150, 470, "Cinzel Black", 46, "#2a5aa8", outline="#f6ecd0",
                     olw=6, alpha=prog(st, 1.0, 1.5), align="left")
        return {"vignette": 0.5}

    # wall rebuilding
    with world(ctx, Cam(960, 600, 1.15)):
        set_thermopylae(ctx, lt, "day")
        n = 24
        r = rng(4)
        for i in range(n):
            ti = 0.3 + i * (sl - 1.0) / n
            k = prog(st, ti, ti + 0.45)
            if k <= 0:
                continue
            col, row = i % 8, i // 8
            x = 520 + col * 110 + (row % 2) * 40
            y = 860 - row * 64
            yy = lerp(y - 500, y, ease_out(k)) - math.sin(prog(st, ti + 0.45, ti + 0.7) * PI) * 14
            rrect(ctx, x - 52, yy - 60, 104, 60, 10)
            fill_stroke(ctx, shade("#b9ad96", r.uniform(-0.12, 0.08)), 4)
        for i, x in enumerate((360, 1520)):
            carry = abs(math.sin(lt * 3 + i))
            draw_char(ctx, x, 900, 1.0, spartan(i + 2, helmet=None),
                      Pose(face=1 if i == 0 else -1, t=lt, walk=lt * 6 + i, weapon="none",
                           shield="none", arm=(30, -170), eyes="normal", sweat=True))
            rrect(ctx, x - 40 + (10 if i == 0 else -10), 900 - 230, 80, 50, 10)
            fill_stroke(ctx, "#b9ad96", 4)
    overlay.caption(ctx, W, H, "FOKİS DUVARI", st, 0.3, sl - 0.2, y=230)
    return {"vignette": 0.45}


def pass__sfx(S):
    t0 = S.start
    ev = [(t0 + 0.2, "paper", 0.5, 0.0), (t0 + S.t("narrow") + 0.1, "whoosh", 0.5, 0.0),
          (t0 + S.t("numbers") + 0.6, "crowd_murmur", 0.4, -0.4)]
    sl = S.dur - S.t("wall")
    n = 24
    for i in range(n):
        ti = 0.3 + i * (sl - 1.0) / n
        ev.append((t0 + S.t("wall") + ti + 0.45, "stone", 0.4, -0.4 + (i % 8) * 0.1))
    return ev


# ======================================================================= SCOUT
def scout(ctx, S, lt):
    t_s, t_l, t_d, t_w = S.t("scout"), S.t("laugh"), S.t("dem"), S.t("warn")
    shot, st, sl = shots(lt, S.dur, [(0, "spy"), (t_s, "report"), (t_l, "laugh"), (t_d, "dem")])
    if shot == "spy":
        with world(ctx, Cam(900, 700, 1.45)):
            set_thermopylae(ctx, lt, "day", wall=(-100, 600, 100))
            for i in range(4):
                x = 260 + i * 200
                ph = lt * 5 + i
                if i % 2 == 0:
                    jj = abs(math.sin(ph)) * 40
                    up = math.sin(ph) > 0
                    draw_char(ctx, x, 860, 0.9, spartan(i, helmet=None, cloak=None),
                              Pose(face=1, t=lt, weapon="none", shield="none", jump=jj,
                                   arm=(20, -200) if up else (40, -60), eyes="happy",
                                   mshape="smile"))
                else:
                    draw_char(ctx, x, 860, 0.9, spartan(i + 4, helmet=None, cloak="#8a1a20"),
                              Pose(face=1, t=lt + i, weapon="comb", shield="none", eyes="closed",
                                   blink=False, mshape="smile"))
            bg.rock(ctx, 1500, 1000, 3.0, seed=2)
            peek = ease_out(prog(st, 0.6, 1.2))
            draw_char(ctx, 1500, 1000 + 160 * (1 - peek), 1.6, SCOUT,
                      Pose(face=-1, t=lt, weapon="none", shield="none", eyes="wide",
                           look=(1, 0), mshape="o"))
            bg.rock(ctx, 1560, 1060, 2.4, seed=5)
        return {"vignette": 0.45}

    with world(ctx, Cam(960 if shot != "laugh" else 1100, 690 if shot != "laugh" else 640,
                        1.55 if shot != "laugh" else 2.1)):
        set_persian_camp(ctx, lt, tod="day")
        bg.throne(ctx, 1150, 900, 1.0)
        laugh = shot == "laugh"
        worried = shot == "dem" and lt > t_w + 1.0
        draw_char(ctx, 1110, 900 - 120, 1.0, XER,
                  Pose(face=-1, t=lt, sit=True, weapon="none", shield="none",
                       eyes="happy" if laugh else ("sad" if worried else "normal"),
                       mouth=talk("XER") if not laugh else 0.6 + 0.4 * abs(math.sin(lt * 14)),
                       mshape="smile" if not worried else "frown",
                       jump=abs(math.sin(lt * 12)) * 8 if laugh else 0, tilt=-0.12 if laugh else 0))
        if shot == "report":
            draw_char(ctx, 700, 900, 1.0, SCOUT,
                      Pose(face=1, t=lt, weapon="none", shield="none", eyes="wide",
                           mouth=talk("SCT"), arm=(40, -170 + 20 * math.sin(lt * 7)), sweat=True))
        if shot == "dem":
            k = ease_out(prog(st, 0.0, 1.0))
            draw_char(ctx, lerp(300, 720, k), 900, 1.05, DEMARATUS,
                      Pose(face=1, t=lt, walk=lt * 6 if k < 1 else None, weapon="none",
                           shield="none", eyes="sad" if lt > t_w else "normal",
                           mouth=talk("DEM"), mshape="line"))
        if shot == "dem":
            pass
    if shot == "dem":
        tag_pop(ctx, 620, 280, "DEMARATOS · SÜRGÜN SPARTA KRALI", lt, t_d + 0.6, t_w + 3.0, s=0.9)
    return {"vignette": 0.5}


def scout_sfx(S):
    t0 = S.start
    ev = [(t0 + 0.5, "grunt_exercise", 0.25, -0.4), (t0 + 1.3, "peek", 0.4, 0.5)]
    for i in range(10):
        ev.append((t0 + 0.4 + i * 0.63, "jump_land", 0.15, -0.5))
    ev += [(t0 + S.t("laugh"), "laugh_king", 0.0, 0.0), (t0 + S.t("dem"), "footsteps", 0.3, -0.3),
           (t0 + S.t("warn") + 1.0, "sting_low", 0.5, 0.0)]
    return ev


# ======================================================================= MOLON LABE
def molon(ctx, S, lt):
    t_h, t_m = S.t("herald"), S.t("molon")
    t_p = t_h + (S.tag("herald").end - S.tag("herald").start)
    t_l = S.beats[-1].start - S.start
    shot, st, sl = shots(lt, S.dur, [(0, "days"), (t_h, "herald"), (t_p, "stare"), (t_m, "molon"),
                              (t_l, "text")])
    if shot == "days":
        day = clamp(st / max(sl, 0.1)) * 4
        ph = day % 1.0
        ang = PI + ph * PI
        with world(ctx, Cam(960, 560, 1.0)):
            set_thermopylae(ctx, lt, "day", wall=(600, 1300, 100))
            sx, sy = 960 + math.cos(ang) * 800, 860 + math.sin(ang) * 640
            bg.sun(ctx, sx, sy, 50)
            night = clamp(1 - math.sin(ph * PI) * 1.6)
            fx.tint(ctx, W * 2, H * 2, "#1a2448", 0.7 * night)
            phalanx(ctx, lt, 1400, 880, s=0.7, lanes=2, ranks=4, grip="rest", eyes="normal")
        n = min(4, int(day) + 1)
        rrect(ctx, W / 2 - 170, 60, 340, 110, 16)
        src(ctx, (0.05, 0.03, 0.02, 0.75))
        ctx.fill()
        text(ctx, f"{n}. GÜN", W / 2, 140, "Cinzel Black", 70, "#f6e3b4")
        return {"vignette": 0.5}

    if shot == "herald":
        with world(ctx, Cam(960, 600, 1.2)):
            set_thermopylae(ctx, lt, "day", wall=(-200, 700, 110))
            phalanx(ctx, lt, 600, 900, s=1.0, lanes=2, ranks=4, grip="rest", eyes="angry",
                    leo=(0, 0))
            draw_char(ctx, 1300, 920, 1.05, HERALD,
                      Pose(face=-1, t=lt, weapon="scroll", shield="none", arm=(50, -140),
                           eyes="angry", mouth=talk("HER")))
            draw_char(ctx, 1460, 920, 1.0, immortal(1),
                      Pose(face=-1, t=lt, weapon="short_spear", grip="rest", shield="front"))
        tag_pop(ctx, 1300 * 1.2 - 960 * 0.2, 330, "PERS HABERCİSİ", st, 0.3, sl - 0.2, s=0.9)
        return {"vignette": 0.5}

    if shot in ("stare", "molon"):
        z = 1.0 if shot == "stare" else 1.0 + 0.3 * ease_out(prog(st, 0, 0.3))
        with world(ctx, Cam(960, 560, z), shake=8 * (1 - prog(st, 0.1, 0.8)) if shot == "molon" else 0,
                   t=lt):
            bg.sky(ctx, -300, -300, 2300, 1400, "#3a2a20", "#a86a3a")
            if shot == "molon":
                fx.speed_lines(ctx, 960, 500, lt, alpha=0.35, color=(1, 0.9, 0.7))
            draw_char(ctx, 960, 1150, 3.5, LEO,
                      Pose(face=1, t=lt, grip="rest", shield="none", eyes="angry",
                           mouth=talk("LEO"), mshape="line" if shot == "stare" else "shout",
                           blink=shot != "stare"))
        return {"vignette": 0.75, "letterbox": 1.0}

    # MOLON LABE text on stone
    bg.sky(ctx, 0, 0, W, H, "#1a120c", "#3a2618")
    rrect(ctx, 260, 240, 1400, 560, 20)
    fill_stroke(ctx, "#8a8478", 6)
    r = rng(2)
    for i in range(60):
        circle(ctx, r.uniform(280, 1640), r.uniform(260, 780), r.uniform(2, 8))
        src(ctx, (0.3, 0.3, 0.3, 0.3))
        ctx.fill()
    a = ease_out(prog(st, 0.2, 1.2))
    text(ctx, "ΜΟΛΩΝ ΛΑΒΕ", W / 2, 530, "DejaVu Serif", 150, "#2a2420", alpha=a, spacing=12,
         outline="#b0a898", olw=3)
    a2 = ease_out(prog(st, 1.0, 1.8))
    text(ctx, "“GEL DE AL”", W / 2, 690, "Cinzel Black", 80, "#e9c27a", alpha=a2,
         outline="#2a1a0c", olw=6)
    return {"vignette": 0.7}


def molon_sfx(S):
    t0 = S.start
    ev = []
    t_h = S.t("herald")
    for d in range(4):
        ev.append((t0 + 0.5 + d * (t_h - 0.5) / 4, "tick", 0.4, 0.0))
    ev += [(t0 + t_h, "horn", 0.4, 0.4), (t0 + S.t("molon") - 0.05, "boom", 0.9, 0.0),
           (t0 + S.t("molon"), "whoosh_big", 0.6, 0.0),
           (S.beats[-1].start + 0.2, "stone_carve", 0.6, 0.0)]
    return ev


# registry names
globals()["pass"] = pass_
globals()["pass_sfx"] = pass__sfx
