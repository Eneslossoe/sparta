# -*- coding: utf-8 -*-
"""Chapters VII-X: the battles, the betrayal, the last morning, the final stand."""
import math
from dataclasses import replace
from functools import lru_cache

import cairo

from draw import backgrounds as bg
from draw import fx, overlay
from draw.characters import (HY, R, Look, Pose, draw_char, draw_shield, greek, immortal, leonidas,
                             mede, persian, spartan, xerxes)
from draw.core import (OUT, PI, Cam, cam_lerp, circle, clamp, ease, ease_back, ease_out, ellipse,
                       fill_stroke, lerp, limb, noise1, poly, prog, rad_grad, rng, rrect, shade,
                       smooth_poly, src, text)
from .common import (G, H, W, battle, clash_events, draw_wave, fight_cloud, phalanx,
                     set_persian_camp, set_thermopylae, shots, tag_pop, talk, wave_schedule, world)

XER = xerxes()
LEO = leonidas()
YOU = spartan(1, spk="SEN")
EPH = Look(kind="ephialtes", cloth="#7a6040", hair="#3a3a2a", beard="#3a3a2a", helmet=None,
           cloak=None, seed=17, spk="EPH")
GRK_SCOUT = Look(kind="spartan", helmet=None, cloth="#c9b48a", cloak=None, hair="#3a2415",
                 beard="#3a2415", seed=18, spk="GRK", long_hair=False)
SPA = spartan(7, spk="SPA")

GY = 900
FRONT = 760
CONTACT = 145


def desat(ctx, a):
    if a <= 0:
        return
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_HSL_SATURATION)
    src(ctx, (0.5, 0.5, 0.5, a))
    ctx.rectangle(0, 0, W, H)
    ctx.fill()
    ctx.restore()


# ======================================================================= DAY 1
@lru_cache(None)
def _day1_foes(t_charge, t_end):
    return tuple(wave_schedule(101, t_charge + 0.4, t_end - 1.0, 2.2, FRONT + CONTACT, kind="mede",
                               speed=(330, 420), fight=(0.5, 1.6)))


def day1(ctx, S, lt):
    tc, tcl, tph, tlf, tw, tf2 = (S.t("charge"), S.t("clash"), S.t("phalanx"), S.t("left"),
                                  S.t("waves"), S.t("fight2"))
    foes = list(_day1_foes(round(tc, 3), round(S.dur, 3)))
    shot, st, sl = shots(lt, S.dur, [(0, "wide"), (tc + 2.4, "behind"), (tcl, "clash"),
                                     (tph, "diagram"), (tw, "weapons"), (tf2, "wide2")])
    if shot in ("wide", "wide2"):
        cam = cam_lerp(Cam(1100, 600, 0.8), Cam(1000, 620, 0.9), ease(prog(st, 0, sl)))
        with world(ctx, cam):
            set_thermopylae(ctx, lt, "day", wall=(-400, 520, 110))
            if shot == "wide":
                phalanx(ctx, lt, FRONT, GY, s=1.0, lanes=3, ranks=4, grip="ready", eyes="angry",
                        leo=(0, 2), you=(1, 0))
                draw_wave(ctx, lt, foes, FRONT + CONTACT, GY)
            else:
                fx.dust_cloud(ctx, 600, 1400, GY - 20, lt, alpha=0.35)
                battle(ctx, lt, foes, FRONT, GY, s=1.0, ranks=4, leo=(0, 2), you=(1, 0))
        if shot == "wide":
            tag_pop(ctx, 1500, 350, "MED ASKERLERİ", lt, tc + 0.6, tc + 2.3)
        return {"letterbox": 1.0, "vignette": 0.55}

    if shot == "behind":
        cam = cam_lerp(Cam(1250, 640, 1.35), Cam(1150, 660, 1.5), ease(prog(st, 0, sl)))
        with world(ctx, cam):
            set_thermopylae(ctx, lt, "day", wall=(-400, 520, 110))
            phalanx(ctx, lt, FRONT, GY, s=1.0, lanes=3, ranks=4, grip="ready", eyes="angry",
                    leo=(0, 2), you=(1, 0))
            draw_wave(ctx, lt, foes, FRONT + CONTACT, GY)
        return {"letterbox": 1.0, "vignette": 0.6}

    if shot in ("clash", "weapons"):
        z = 1.55 if shot == "clash" else 1.35
        shake = 7 * (1 - prog(st, 0, 1.2)) if shot == "clash" else 0
        cam = Cam(860, 690, z)
        with world(ctx, cam, shake=shake, t=lt):
            set_thermopylae(ctx, lt, "day", wall=(-400, 520, 110))
            battle(ctx, lt, foes, FRONT, GY, s=1.0, ranks=4, leo=(0, 2), you=(1, 0))
            for f in foes:
                if f.lane == 0:
                    fx.sparks(ctx, FRONT + 90, GY - 150, lt - (f.tf - 0.1), seed=f.seed, size=1.2)
                    fx.pow_star(ctx, FRONT + 140, GY - 130, lt - (f.tf - 0.05), 0.9, dur=0.3)
                if abs(lt - f.tc) < 0.6 and f.lane < 2:
                    fx.dust(ctx, FRONT + 160, GY, lt - f.tc, seed=f.seed, size=0.8)
        if shot == "weapons":
            k1 = ease_back(prog(st, 1.0, 1.4))
            k2 = ease_back(prog(st, 2.3, 2.7))
            k3 = ease_back(prog(st, 4.0, 4.4))
            if k1 > 0:
                overlay.banner(ctx, 560, 210, "UZUN MIZRAK", size=46, s=k1, fill="#2a5aa8")
            if k2 > 0:
                overlay.banner(ctx, 1380, 210, "KISA MIZRAK", size=46, s=k2)
            if k3 > 0:
                overlay.banner(ctx, 1380, 300, "HASIR KALKAN", size=46, s=k3, rot=0.03)
        return {"letterbox": 1.0, "vignette": 0.6}

    # diagram: interlocked shields seen from above (enemy = top of screen)
    bg.sky(ctx, 0, 0, W, H, "#e8d6a8", "#d4bc88")
    hl = lt >= tlf
    k_hl = ease(prog(lt, tlf + 0.3, tlf + 0.9))
    for row in range(2):
        for i in range(7):
            cx = 450 + i * 150
            cy = 520 + row * 200
            ki = ease_back(prog(st, 0.12 * i + row * 0.3, 0.12 * i + row * 0.3 + 0.4))
            if ki <= 0:
                continue
            glow = hl and row == 0 and i == 3
            draw_shield(ctx, cx, cy, 95 * ki, "#c99230" if not glow else "#ffd34a", "lambda",
                        sx=1.0, sy=1.0)
    if hl:
        cx, cy = 450 + 3 * 150, 520
        ctx.set_source(rad_grad(cx, cy, 60, 200, [(0, (1, 0.9, 0.3, 0.0)), (0.6, (1, 0.9, 0.3, 0.35 * k_hl)),
                                                (1, (1, 0.9, 0.3, 0))]))
        circle(ctx, cx, cy, 200)
        ctx.fill()
        ax = lerp(cx - 40, cx - 150, k_hl)
        limb(ctx, [(cx - 30, cy + 130), (ax, cy + 130)], "#b81e28", 10, 4)
        poly(ctx, [(ax - 30, cy + 130), (ax, cy + 108), (ax, cy + 152)])
        fill_stroke(ctx, "#b81e28", 4)
        text(ctx, "SOLUNDAKİNİ KORUR", cx - 90, cy + 215, "Baloo 2 ExtraBold", 46, "#b81e28",
             alpha=k_hl, outline="#fff6e0", olw=6)
    text(ctx, "FALANKS", W / 2, 180, "Cinzel Black", 110, "#3a2410", outline="#f6ecd0", olw=8,
         alpha=ease_out(prog(st, 0.2, 0.7)))
    a = prog(st, 1.4, 1.8)
    text(ctx, "DÜŞMAN", 1640, 300, "Baloo 2 ExtraBold", 50, "#b81e28", alpha=a)
    limb(ctx, [(1640, 620), (1640, 360)], "#5a3a1a", 6, 0)
    poly(ctx, [(1622, 365), (1640, 330), (1658, 365)])
    src(ctx, "#5a3a1a", a)
    ctx.fill()
    return {"vignette": 0.35}


def day1_sfx(S):
    t0 = S.start
    foes = list(_day1_foes(round(S.t("charge"), 3), round(S.dur, 3)))
    ev = [(t0 + 0.2, "wind", 0.3, 0.0), (t0 + S.t("charge") + 0.2, "horn", 0.6, 0.6),
          (t0 + S.t("charge") + 0.6, "war_cry", 0.75, 0.5),
          (t0 + S.t("charge") + 0.5, "battle_amb", 0.0, 0.0)]
    ev += clash_events(foes, t0, FRONT + CONTACT)
    ev.append((t0 + S.t("phalanx") + 0.1, "paper", 0.4, 0.0))
    for i in range(6):
        ev.append((t0 + S.t("phalanx") + 0.15 * i + 0.3, "shield_place", 0.35, -0.5 + i * 0.2))
    ev.append((t0 + S.t("left") + 0.4, "ding", 0.5, 0.0))
    return [e for e in ev if not (S.t("phalanx") + t0 - 0.1 < e[0] < S.t("waves") + t0 and e[1] in
                                  ("shield_bash", "stab", "grunt", "clang"))]


# ======================================================================= IMMORTALS
@lru_cache(None)
def _imm_foes(t0, t1):
    return tuple(wave_schedule(202, t0, t1, 2.4, FRONT + CONTACT, kind="immortal",
                               speed=(300, 380), fight=(0.7, 1.9)))


def _chase_people(lt, t_feign, t_turn, t_counter):
    """Positions during the feigned retreat + counter-attack."""
    run = ease_out(prog(lt, t_feign + 0.8, t_turn)) * 700
    turned = lt >= t_turn + 0.3
    charge = ease(prog(lt, t_counter, t_counter + 1.6)) * 260
    return run, turned, charge


def immortals(ctx, S, lt):
    t_s, t_o, t_c, t_f, t_ch, t_t, t_co, t_th, t_x, t_d2 = (
        S.t("send"), S.t("order"), S.t("clash"), S.t("feign"), S.t("chase"), S.t("turn"),
        S.t("counter"), S.t("throne"), S.t("xer"), S.t("day2"))
    foes = list(_imm_foes(round(t_c - 3.0, 3), round(t_f + 0.5, 3)))
    shot, st, sl = shots(lt, S.dur, [(0, "assemble"), (t_o, "order"), (t_c, "clash"),
                                     (t_f, "feign"), (t_t, "turn"), (t_co, "counter"),
                                     (t_th, "throne"), (t_x, "xer"), (t_d2, "day2")])
    if shot == "assemble":
        with world(ctx, Cam(960, 560, 1.0 + 0.04 * st)):
            set_persian_camp(ctx, lt)
            for row in range(3, -1, -1):
                for i in range(10):
                    draw_char(ctx, 250 + i * 120 + (row % 2) * 60, 900 - row * 40, 0.75 - row * 0.05,
                              immortal(i + row), Pose(face=1, t=lt + i, weapon="short_spear",
                                                      grip="rest", shield="front", eyes="angry"))
            bg.throne(ctx, 1640, 760, 0.8)
            draw_char(ctx, 1610, 760 - 96, 0.8, XER,
                      Pose(face=-1, t=lt, sit=True, weapon="none", shield="none",
                           arm=(60, -140), eyes="angry"))
        tag_pop(ctx, 700, 360, "ÖLÜMSÜZLER · 10.000", lt, t_s + 0.8, t_o - 0.1)
        return {"vignette": 0.5, "letterbox": 1.0}

    if shot in ("order", "xer"):
        scared = shot == "xer"
        with world(ctx, Cam(960, 560, 1.0 + 0.04 * st), shake=4 if scared else 0, t=lt):
            set_persian_camp(ctx, lt)
            draw_char(ctx, 920, 1140, 3.2, XER,
                      Pose(face=1, t=lt, weapon="none", shield="none",
                           arm=(95, -130) if not scared else (110, -140),
                           eyes="angry" if not scared else "wide", sweat=scared,
                           mouth=talk("XER"), mshape="line"))
        return {"vignette": 0.6, "letterbox": 1.0}

    if shot == "clash":
        with world(ctx, Cam(900, 680, 1.4), shake=6 * (1 - prog(st, 1.0, 2.0)), t=lt):
            set_thermopylae(ctx, lt, "day", wall=(-400, 520, 110))
            battle(ctx, lt, foes, FRONT, GY, s=1.0, ranks=4, leo=(0, 2), you=(1, 0))
            for f in foes:
                if f.lane == 0:
                    fx.sparks(ctx, FRONT + 90, GY - 150, lt - (f.tf - 0.1), seed=f.seed, size=1.2)
        return {"letterbox": 1.0, "vignette": 0.55}

    if shot in ("feign", "turn", "counter"):
        run, turned, charge = _chase_people(lt, t_f, t_t, t_co)
        camx = lerp(1000, 640, ease(prog(lt, t_f + 0.5, t_t))) + charge * 0.6
        z = 1.0 if shot != "turn" else 1.0 + 0.5 * ease_out(prog(st, 0, 0.4))
        with world(ctx, Cam(camx if shot != "turn" else 520, 600 if shot != "turn" else 640, z)):
            set_thermopylae(ctx, lt, "day", x0=-1800, wall=(-1400, -500, 110))
            r = rng(5)
            # chasing Persians: scattered, running left
            for i in range(14):
                lane = i % 3
                delay = r.uniform(0, 1.2)
                px0 = 1050 + (i // 3) * 140 + r.uniform(-30, 30)
                chase_k = ease(prog(lt, t_f + 1.2 + delay, t_t + 0.6))
                px = px0 - chase_k * 900 + charge * 0.15
                hit_t = t_co + 0.35 + i * 0.08
                fall = ease_out(prog(lt, hit_t, hit_t + 0.4)) if shot == "counter" else 0
                moving = 0.01 < chase_k < 0.99
                draw_char(ctx, px, GY - lane * 30 + r.uniform(-10, 10), 1.0 - lane * 0.07,
                          immortal(i), Pose(face=-1, t=lt + i, walk=lt * 11 + i if moving else None,
                                            run=True, weapon="short_spear", grip="ready",
                                            eyes="happy" if fall == 0 and moving else ("dead" if fall > 0.3 else "wide"),
                                            mshape="shout" if moving else "o", fall=fall,
                                            shield="front" if i % 2 else "none"))
                if shot == "counter":
                    fx.pow_star(ctx, px, GY - 150, lt - hit_t, 1.0)
            # Spartans
            for lane in reversed(range(3)):
                for rk in range(4):
                    x = FRONT - rk * 74 - lane * 12 - run + charge
                    face = 1 if turned else -1
                    moving = (0.8 + t_f < lt < t_t) or (t_co < lt < t_co + 1.6)
                    lk = LEO if (lane, rk) == (0, 2) else (YOU if (lane, rk) == (1, 0) else spartan(lane * 10 + rk))
                    draw_char(ctx, x if turned else x - 30, GY - lane * 30, 1.0 - lane * 0.07, lk,
                              Pose(face=face, t=lt + rk, walk=lt * 11 + rk + lane if moving else None,
                                   run=True, grip="ready" if turned else "march",
                                   thrust=0.8 if shot == "counter" and rk == 0 else 0,
                                   shield="front", eyes="sly" if not turned else "angry",
                                   mshape="grin" if not turned else "shout"))
        if shot == "feign":
            k = ease_back(prog(st, 0.6, 1.0))
            if k > 0:
                overlay.banner(ctx, 960, 200, "SAHTE GERİ ÇEKİLME", size=54, s=k, fill="#2a5aa8")
        return {"letterbox": 1.0, "vignette": 0.5}

    if shot == "throne":
        jumps = [st > 1.0 + j * 1.25 for j in range(3)]
        jt = [(st - (1.0 + j * 1.25)) for j in range(3)]
        jump = 0.0
        for j in range(3):
            if 0 < jt[j] < 0.7:
                jump = math.sin(jt[j] / 0.7 * PI) * 150
        with world(ctx, Cam(1150, 640, 1.55)):
            set_persian_camp(ctx, lt)
            bg.throne(ctx, 1150, 900, 1.0)
            sitting = jump < 30
            draw_char(ctx, 1110, 900 - (120 if sitting else 40) - jump, 1.0, XER,
                      Pose(face=-1, t=lt, sit=sitting, weapon="none", shield="none",
                           arm=(30, -220) if not sitting else (40, -110),
                           eyes="wide" if any(jumps) else "normal", sweat=any(jumps),
                           mshape="o" if not sitting else "frown"))
        for j in range(3):
            k = ease_back(prog(st, 1.05 + j * 1.25, 1.4 + j * 1.25))
            if k > 0:
                ctx.save()
                ctx.translate(560 + j * 180, 300)
                ctx.scale(k, k)
                text(ctx, str(j + 1), 0, 50, "Cinzel Black", 150, "#ffe14a", outline=OUT, olw=10,
                     shadow=(5, 7))
                ctx.restore()
        return {"vignette": 0.55}

    # day 2: exhausted at sunset
    with world(ctx, Cam(900, 680, 1.45)):
        set_thermopylae(ctx, lt, "dusk", wall=(-400, 1100, 110))
        for i, x in enumerate((420, 1260, 1500)):
            draw_char(ctx, x, 930, 1.0, spartan(i + 4),
                      Pose(face=1 if i else -1, t=lt + i, sit=True, grip="rest", weapon="none",
                           shield="ground", eyes="closed" if i == 1 else "sad", blink=False))
        draw_char(ctx, 880, 930, 1.05, YOU,
                  Pose(face=1, t=lt, sit=True, weapon="none", shield="ground", eyes="sad",
                       bandage=True, mshape="frown", sweat=True))
        draw_shield(ctx, 1020, 900, 56, "#c99230", "lambda", sx=0.8)
        tag_pop(ctx, 880, 650, "SEN", lt, t_d2 + 0.5, S.dur - 0.3)
    rrect(ctx, W / 2 - 170, 140, 340, 110, 16)
    src(ctx, (0.05, 0.03, 0.02, 0.75 * prog(st, 0.2, 0.6)))
    ctx.fill()
    text(ctx, "2. GÜN", W / 2, 220, "Cinzel Black", 70, "#f6e3b4", alpha=prog(st, 0.2, 0.6))
    return {"vignette": 0.6, "letterbox": 1.0}


def immortals_sfx(S):
    t0 = S.start
    t_c, t_f, t_t, t_co, t_th = S.t("clash"), S.t("feign"), S.t("turn"), S.t("counter"), S.t("throne")
    foes = list(_imm_foes(round(t_c - 3.0, 3), round(t_f + 0.5, 3)))
    ev = [(t0 + 0.3, "drums_persian", 0.5, 0.4), (t0 + S.t("order") + 0.2, "boom", 0.6, 0.0),
          (t0 + t_c - 0.4, "war_cry", 0.6, 0.5)]
    ev += [e for e in clash_events(foes, t0, FRONT + CONTACT) if t0 + t_c - 0.1 < e[0] < t0 + t_f]
    ev += [(t0 + t_f + 0.6, "whoosh", 0.5, -0.3), (t0 + t_f + 0.9, "run_many", 0.6, -0.2),
           (t0 + t_f + 1.6, "war_cry", 0.4, 0.4), (t0 + t_t, "whoosh_big", 0.7, 0.0),
           (t0 + t_t + 0.35, "shields_up", 0.7, 0.0)]
    for i in range(14):
        hit_t = t0 + t_co + 0.35 + i * 0.08
        ev.append((hit_t, "stab" if i % 2 else "clang", 0.45, 0.2))
        if i % 3 == 0:
            ev.append((hit_t + 0.05, "grunt", 0.3, 0.3))
    for j in range(3):
        ev.append((t0 + t_th + 1.0 + j * 1.25, "boing", 0.55, 0.3))
        ev.append((t0 + t_th + 1.05 + j * 1.25, "pop", 0.5, -0.3 + j * 0.3))
    ev.append((t0 + S.t("day2"), "crickets", 0.35, 0.0))
    return ev


# ======================================================================= BETRAYAL
def betrayal(ctx, S, lt):
    t_e, t_o, t_g, t_c, t_op = S.t("eph"), S.t("offer"), S.t("gold"), S.t("climb"), S.t("open")
    shot, st, sl = shots(lt, S.dur, [(0, "sneak"), (t_o, "tent"), (t_c, "climb"), (t_op, "open")])
    if shot == "sneak":
        k = ease(prog(lt, t_e + 0.3, t_o))
        with world(ctx, Cam(lerp(700, 1100, k), 680, 1.4)):
            set_persian_camp(ctx, lt, tod="night")
            bg.tent(ctx, 1450, 900, 1.0, c1="#c9a46a", c2="#7a2a8a", flag="#f2c23a", t=lt, big=True)
            for tx in (1150, 1750):
                draw_torch_pole(ctx, tx, 900, lt)
            x = lerp(400, 1150, k)
            draw_char(ctx, x, 920, 1.0, EPH,
                      Pose(face=1, t=lt, walk=lt * 5 if 0.01 < k < 0.99 else None, tilt=0.2,
                           weapon="none", shield="none", eyes="sly",
                           look=(math.sin(lt * 2), 0), mshape="grin"))
            tag_pop(ctx, x, 620, "EFİALTES", lt, t_e + 1.5, t_o - 0.2)
        return {"vignette": 0.75}

    if shot == "tent":
        gold = lt >= t_g
        with world(ctx, Cam(960, 640, 1.4)):
            bg.sky(ctx, -400, -400, 2400, 1400, "#3a1a2a", "#7a3a2a")
            for i in range(10):
                poly(ctx, [(-400 + i * 300, -400), (-250 + i * 300, -400), (-100 + i * 300, 900),
                           (-250 + i * 300, 900)])
                src(ctx, (0.6, 0.25, 0.4, 0.25 if i % 2 else 0.1))
                ctx.fill()
            ctx.set_source(rad_grad(700, 500, 20, 800, [(0, (1, 0.7, 0.3, 0.4)), (1, (1, 0.6, 0.2, 0))]))
            ctx.paint()
            draw_torch_pole(ctx, 520, 900, lt)
            bg.ground(ctx, -400, 2400, 880, 1400, "#4a2a1a", pebbles=False)
            bg.throne(ctx, 1250, 900, 1.0)
            draw_char(ctx, 1210, 900 - 120, 1.0, XER,
                      Pose(face=-1, t=lt, sit=True, weapon="none", shield="none",
                           arm=(60, -150) if gold else (40, -110), eyes="sly" if not gold else "angry",
                           mouth=talk("XER"), mshape="smile"))
            bow = 0.35 if not gold else 0.1
            draw_char(ctx, 820, 920, 1.0, EPH,
                      Pose(face=1, t=lt, tilt=bow, weapon="none", shield="none",
                           arm=(50, -80) if not gold else (40, -150), eyes="sly",
                           mouth=talk("EPH"), mshape="grin"))
            if gold:
                k = prog(lt, t_g + 0.6, t_g + 1.3)
                bx = lerp(1150, 860, k)
                by = lerp(720, 760, k) - math.sin(k * PI) * 160
                ctx.save()
                ctx.translate(bx, by)
                ctx.rotate(k * 6)
                ctx.move_to(-30, 20)
                ctx.curve_to(-40, -20, -10, -30, -8, -36)
                ctx.line_to(8, -36)
                ctx.curve_to(10, -30, 40, -20, 30, 20)
                ctx.close_path()
                fill_stroke(ctx, "#a87a3a", 4)
                ctx.restore()
                if k >= 1:
                    for i in range(6):
                        a = lt * 3 + i
                        circle(ctx, 860 + math.cos(a) * 60, 740 + math.sin(a) * 30, 6)
                        src(ctx, (1, 0.9, 0.3, 0.8))
                        ctx.fill()
        return {"vignette": 0.7}

    if shot == "climb":
        with world(ctx, Cam(960, 540, 1.0 + 0.05 * st)):
            bg.sky(ctx, -200, -200, 2200, 1300, "#050a1e", "#1a2448")
            bg.stars(ctx, -200, -200, 2200, 700, lt)
            bg.moon(ctx, 1600, 160, 44)
            pts = bg.mountains(ctx, 71, -300, 2300, 1000, 760, "#141a2e", rough=1.0, outline=False)
            path = [(0, 1000), (300, 900), (200, 780), (560, 700), (450, 580), (820, 520), (760, 420),
                    (1100, 380), (1300, 300)]
            smooth_poly(ctx, path, close=False)
            src(ctx, (0.6, 0.5, 0.3, 0.3))
            ctx.set_line_width(6)
            ctx.set_dash([10, 12])
            ctx.stroke()
            ctx.set_dash([])
            L = len(path) - 1
            for i in range(40):
                u = (st * 0.08 + i * 0.022) % 1.0
                seg = u * L
                j = min(int(seg), L - 1)
                f = seg - j
                x = lerp(path[j][0], path[j + 1][0], f)
                y = lerp(path[j][1], path[j + 1][1], f)
                ctx.set_source(rad_grad(x, y - 10, 0, 30, [(0, (1, 0.8, 0.3, 0.9)), (1, (1, 0.5, 0.1, 0))]))
                circle(ctx, x, y - 10, 30)
                ctx.fill()
                circle(ctx, x, y - 10, 4)
                src(ctx, "#fff3b0")
                ctx.fill()
        overlay.caption(ctx, W, H, "ANOPAIA PATİKASI", st, 0.4, sl - 0.2, y=230)
        return {"vignette": 0.7}

    # Phocians on the hill
    with world(ctx, Cam(960, 600, 1.15)):
        bg.sky(ctx, -200, -200, 2200, 1300, "#0b1430", "#2a3a6a")
        bg.stars(ctx, -200, -200, 2200, 600, lt)
        ctx.move_to(-300, 760)
        ctx.curve_to(100, 500, 600, 480, 900, 760)
        ctx.line_to(900, 1300)
        ctx.line_to(-300, 1300)
        ctx.close_path()
        fill_stroke(ctx, "#2a3448", 4)
        bg.ground(ctx, 800, 2300, 900, 1300, "#2a2a3a", pebbles=False)
        for i in range(5):
            draw_char(ctx, 120 + i * 120, 600 + abs(i - 2) * 30, 0.85,
                      greek(i, cloak="#2f7a4a", emblem="crescent"),
                      Pose(face=1, t=lt + i, grip="rest", shield="front", eyes="scared",
                           look=(1, 0.5), sweat=i % 2 == 0))
        for i in range(8):
            x = 2200 - ((st * 140 + i * 210) % 1500)
            draw_char(ctx, x, 960, 0.9, immortal(i),
                      Pose(face=-1, t=lt + i, walk=lt * 6 + i, weapon="torch", shield="none",
                           arm=(40, -150), eyes="angry"))
        tag_pop(ctx, 360, 380, "FOKİSLİLER", st, 0.3, sl - 0.2)
        k = ease_back(prog(st, 2.0, 2.4))
        if k > 0:
            text(ctx, "?", 300, 300, "Cinzel Black", 140 * k, "#ffffff", outline=OUT, olw=8)
    return {"vignette": 0.7}


def draw_torch_pole(ctx, x, y, t):
    limb(ctx, [(x, y), (x, y - 200)], "#5a3a1a", 10, 3)
    ctx.set_source(rad_grad(x, y - 230, 10, 260, [(0, (1, 0.7, 0.3, 0.5)), (1, (1, 0.5, 0.2, 0))]))
    circle(ctx, x, y - 230, 260)
    ctx.fill()
    bg.fire(ctx, x, y - 200, 0.4, t, seed=int(x))


def betrayal_sfx(S):
    t0 = S.start
    return [(t0 + 0.2, "crickets", 0.45, 0.0), (t0 + S.t("eph") + 0.4, "sneak", 0.5, -0.3),
            (t0 + S.t("offer"), "fire_crackle", 0.4, -0.4), (t0 + S.t("gold") + 0.6, "whoosh", 0.4, 0.0),
            (t0 + S.t("gold") + 1.3, "coins", 0.7, -0.2), (t0 + S.t("climb"), "owl", 0.35, 0.5),
            (t0 + S.t("climb") + 0.5, "march_far", 0.35, 0.0), (t0 + S.t("open") + 2.0, "sting", 0.5, 0.0)]


# ======================================================================= MORNING
def morning(ctx, S, lt):
    t_r, t_n, t_l, t_s, t_y, t_s2, t_b = (S.t("run"), S.t("news"), S.t("leave"), S.t("stay"),
                                          S.t("you"), S.t("stay2"), S.t("breakfast"))
    shot, st, sl = shots(lt, S.dur, [(0, "run"), (t_n, "news"), (t_l, "leave"), (t_s, "stay"),
                                     (t_y, "you"), (t_b, "breakfast")])
    if shot in ("run", "news"):
        k = ease(prog(lt, t_r, t_n))
        with world(ctx, Cam(1000, 640, 1.3)):
            set_thermopylae(ctx, lt, "dawn", wall=(-400, 300, 110))
            sx = lerp(1700, 1000, k)
            draw_char(ctx, 780, 920, 1.05, LEO,
                      Pose(face=1, t=lt, grip="rest", shield="side", eyes="normal" if shot == "run" else "angry"))
            draw_char(ctx, sx, 920, 1.0, GRK_SCOUT,
                      Pose(face=-1, t=lt, walk=lt * 12 if shot == "run" else None, run=True,
                           weapon="none", shield="none", eyes="wide", sweat=True,
                           mouth=talk("GRK"), arm=(50, -170 + 15 * math.sin(lt * 8)) if shot == "news" else None))
        return {"vignette": 0.55}

    if shot == "leave":
        with world(ctx, Cam(960, 620, 1.1)):
            set_thermopylae(ctx, lt, "dawn")
            for j, (cl, sh, em) in enumerate((("#2f7a4a", "#e9e2cf", "crescent"),
                                             ("#8a5a2a", "#f0e0b0", "trident"),
                                             ("#6a3a7a", "#e9e2cf", "bull"))):
                for i in range(4):
                    x = 1300 - st * 160 - i * 110 - j * 470
                    draw_char(ctx, x, 940 - j * 26, 0.85 - j * 0.05, greek(j * 4 + i, cloak=cl, shield=sh, emblem=em),
                              Pose(face=-1, t=lt + i, walk=lt * 7 + i, grip="march", shield="front",
                                   eyes="sad"))
            draw_char(ctx, 1650, 950, 1.1, LEO,
                      Pose(face=-1, t=lt, grip="rest", shield="side", eyes="sad"))
        return {"vignette": 0.6}

    if shot == "stay":
        with world(ctx, Cam(960, 620, 1.05)):
            set_thermopylae(ctx, lt, "dawn", wall=(1400, 2400, 110))
            phalanx(ctx, lt, 1150, 930, s=0.9, lanes=3, ranks=5, grip="rest", eyes="angry",
                    leo=(0, 0), you=(1, 2))
            for i in range(5):
                for lane in range(2):
                    draw_char(ctx, 540 - i * 80 - lane * 12, 930 - lane * 30, 0.85 - lane * 0.06,
                              greek(i + lane * 5), Pose(face=1, t=lt + i, grip="rest", shield="front",
                                                        eyes="angry"))
        tag_pop(ctx, 900, 380, "300 SPARTALI", st, 0.6, sl)
        tag_pop(ctx, 330, 430, "700 THESPİAİLİ", st, 2.4, sl)
        return {"vignette": 0.55}

    if shot == "you":
        decided = lt >= t_s2
        look = (-1, 0) if (not decided and st < 3.2) else (1, 0)
        with world(ctx, Cam(960, 560, 1.0 + 0.03 * st)):
            set_thermopylae(ctx, lt, "dawn")
            draw_char(ctx, 960, 1150, 3.4, YOU,
                      Pose(face=1, t=lt, grip="rest", shield="none",
                           eyes="sad" if not decided else "angry", look=look,
                           mouth=talk("SEN"), mshape="line"))
        if not decided:
            k = ease_back(prog(st, 0.8, 1.3)) * (1 - prog(st, 3.6, 4.0))
            if k > 0.01:
                ctx.save()
                ctx.translate(430, 300)
                ctx.scale(k, k)
                for (cx, cy, r) in ((140, 190, 18), (110, 150, 26)):
                    circle(ctx, cx, cy, r)
                    fill_stroke(ctx, "#ffffff", 4)
                ellipse(ctx, 0, 0, 220, 140)
                fill_stroke(ctx, "#ffffff", 5)
                bg.house(ctx, -40, 70, 0.6)
                draw_char(ctx, 80, 75, 0.45, Look(kind="woman", cloth="#2f6db3", cloth2="#f2d36b",
                                                  hair="#4a2a16", helmet=None, cloak=None),
                          Pose(face=-1, t=lt, weapon="none", shield="none", arm=(40, -150),
                               eyes="happy"))
                ctx.restore()
        tag_pop(ctx, 1300, 280, "SEN", st, 0.3, sl)
        return {"vignette": 0.6, "letterbox": 1.0}

    # breakfast in Hades
    cheer = ease(prog(lt, t_b + 3.6, t_b + 4.2))
    with world(ctx, Cam(960, 600, 1.2)):
        set_thermopylae(ctx, lt, "dawn", wall=(-400, 300, 110))
        for i in range(6):
            x = 420 + i * 220 if i < 3 else 1100 + (i - 3) * 220
            if i in (2, 3):
                continue
            draw_char(ctx, x, 930, 1.0, spartan(i + 2),
                      Pose(face=1 if x < 960 else -1, t=lt + i, grip="rest", shield="front",
                           eyes="happy" if cheer > 0.5 else "angry", jump=cheer * abs(math.sin(lt * 9 + i)) * 30,
                           mouth=cheer * 0.9, mshape="shout" if cheer > 0.5 else "line"))
        draw_char(ctx, 960, 950, 1.15, LEO,
                  Pose(face=1, t=lt, weapon="cup", shield="none", arm=(60, -200 if cheer else -120),
                       eyes="angry", mouth=talk("LEO"), mshape="smile"))
    return {"vignette": 0.55}


def morning_sfx(S):
    t0 = S.start
    ev = [(t0 + 0.3, "rooster_far", 0.0, 0.0), (t0 + S.t("run"), "run_steps", 0.45, 0.5)]
    ev += [(t0 + S.t("leave"), "march_far", 0.45, -0.4), (t0 + S.t("stay") + 0.6, "pop", 0.4, 0.0),
           (t0 + S.t("stay") + 2.4, "pop", 0.4, -0.4), (t0 + S.t("you") + 0.8, "thought", 0.4, -0.4),
           (t0 + S.t("stay2") - 0.2, "heartbeat", 0.5, 0.0),
           (t0 + S.t("breakfast") + 3.6, "crowd_cheer", 0.7, 0.0)]
    return ev


# ======================================================================= FINAL
@lru_cache(None)
def _final_foes(t0, t1):
    return tuple(wave_schedule(303, t0, t1, 3.0, 1180 + CONTACT, kind="persian",
                               speed=(320, 400), fight=(0.4, 1.3)))


def _hill(ctx, cx=960, gy=900, w=700, h=180, color="#a88a62"):
    ctx.move_to(cx - w, gy + 10)
    ctx.curve_to(cx - w * 0.5, gy - h, cx + w * 0.5, gy - h, cx + w, gy + 10)
    ctx.close_path()
    fill_stroke(ctx, color, 4.5)


def final(ctx, S, lt):
    tg = {k: S.t(k) for k in ("advance", "clash", "swords", "leofall", "protect", "body", "hill",
                              "teeth", "rain", "fall", "end")}
    foes = list(_final_foes(round(tg["clash"] - 2.2, 3), round(tg["leofall"] + 0.3, 3)))
    shot, st, sl = shots(lt, S.dur, [(0, "advance"), (tg["clash"], "clash"), (tg["swords"], "swords"),
                                     (tg["leofall"], "leofall"), (tg["protect"], "protect"),
                                     (tg["body"], "body"), (tg["hill"], "hill"), (tg["teeth"], "teeth"),
                                     (tg["rain"], "rain"), (tg["fall"], "fall"), (tg["end"], "end")])
    front = 1180
    if shot == "advance":
        adv = ease(prog(lt, 0.8, tg["clash"] - 0.2)) * 420
        x_front = 760 + adv
        with world(ctx, Cam(lerp(900, 1250, adv / 420), 620, 0.95)):
            set_thermopylae(ctx, lt, "dawn", wall=(-400, 560, 110), x1=3600)
            phalanx(ctx, lt, x_front, GY, s=1.0, lanes=3, ranks=5,
                    walk=lt * 6 if 0.8 < lt < tg["clash"] - 0.2 else None, grip="ready",
                    eyes="angry", leo=(0, 2), you=(1, 0))
            draw_wave(ctx, lt, foes, front + CONTACT, GY)
            r = rng(7)
            for row in range(3, -1, -1):
                for i in range(10):
                    draw_char(ctx, 2000 + i * 70 + row * 30, GY - 120 - row * 22, 0.5, persian(i + row),
                              Pose(face=-1, t=lt + i, weapon="short_spear", grip="ready", shield="front"),
                              lod=True)
        return {"letterbox": 1.0, "vignette": 0.55}

    if shot in ("clash", "swords"):
        swords = shot == "swords"
        with world(ctx, Cam(1060, 690, 1.45), shake=8 * (1 - prog(st, 0, 1.0)) if not swords else 2,
                   t=lt):
            set_thermopylae(ctx, lt, "dawn", wall=(-400, 560, 110), x1=3600)
            def ex(lane, rk, ps):
                if swords and rk == 0:
                    ps.weapon = "sword"
                    ps.thrust = max(0, math.sin(lt * 8 + lane * 1.7)) ** 2
                elif swords and rk == 1:
                    ps.broken = True
                return ps
            battle(ctx, lt, foes, front, GY, s=1.0, ranks=4, leo=(0, 2), you=(1, 0), extra=ex)
            for f in foes:
                if f.lane == 0:
                    fx.sparks(ctx, front + 90, GY - 150, lt - (f.tf - 0.1), seed=f.seed, size=1.3)
                    fx.pow_star(ctx, front + 140, GY - 130, lt - (f.tf - 0.05), 0.9, dur=0.3)
            if swords:
                k = prog(st, 0.2, 0.7)
                for i in range(3):
                    sx_ = front + 40 + i * 30
                    a = -1.0 + i * 0.6 + k * 3
                    draw_spear_piece(ctx, sx_ + k * 80, GY - 200 - math.sin(k * PI) * 120 + k * 150, a, k)
        return {"letterbox": 1.0, "vignette": 0.6}

    if shot == "leofall":
        k = ease_out(prog(st, 0.4, 2.0))
        with world(ctx, Cam(980, 700, 1.9)):
            set_thermopylae(ctx, lt, "dawn", wall=(-400, 560, 110), x1=3600)
            draw_char(ctx, 960, GY, 1.0, LEO,
                      Pose(face=1, t=lt, weapon="sword", shield="front" if k < 0.5 else "none",
                           fall=k, eyes="closed" if k > 0.5 else "wide", blink=False, mshape="o"))
            for i in range(3):
                draw_char(ctx, 1180 + i * 90, GY - (i % 2) * 20, 1.0, persian(i),
                          Pose(face=-1, t=lt * 0.3, weapon="short_spear", grip="ready",
                               thrust=0.6, shield="front", eyes="angry"))
        desat(ctx, 0.85 * prog(st, 0.2, 0.8))
        return {"letterbox": 1.0, "vignette": 0.8}

    if shot in ("protect", "body"):
        pushes = [tg["body"] + 0.5 + j * 1.3 for j in range(4)]
        surge = 0.0
        for p_ in pushes:
            surge += ease_out(prog(lt, p_, p_ + 0.5)) * 55
        with world(ctx, Cam(1100 + surge * 0.5, 680, 1.25), shake=3, t=lt):
            set_thermopylae(ctx, lt, "dawn", wall=(-400, 560, 110), x1=3600)
            fx.dust_cloud(ctx, 700, 1700, GY - 10, lt, alpha=0.3)
            draw_char(ctx, 1000 + surge * 0.6, GY + 40, 1.0, LEO,
                      Pose(face=1, t=0, weapon="none", shield="none", fall=1.0, eyes="closed",
                           blink=False))
            run_in = ease_out(prog(lt, tg["protect"], tg["protect"] + 1.2))
            for lane in reversed(range(3)):
                for rk in range(3):
                    x = 1200 + surge - rk * 80 - lane * 12 - (1 - run_in) * 400
                    draw_char(ctx, x, GY - lane * 30, 1.0 - lane * 0.07,
                              SPA if (lane, rk) == (0, 0) else (YOU if (lane, rk) == (1, 0) else spartan(lane * 10 + rk + 3)),
                              Pose(face=1, t=lt + rk, walk=lt * 10 if run_in < 1 else None, run=True,
                                   weapon="sword", thrust=max(0, math.sin(lt * 7 + lane + rk)) ** 2,
                                   shield="front", eyes="angry", mouth=talk("SPA") if (lane, rk) == (0, 0) else 0,
                                   mshape="shout"))
            for i in range(9):
                lane = i % 3
                base = 1380 + surge + (i // 3) * 110
                rec = sum(ease_out(prog(lt, p_, p_ + 0.5)) for p_ in pushes)
                draw_char(ctx, base + rec * 30, GY - lane * 30, 1.0 - lane * 0.07, persian(i),
                          Pose(face=-1, t=lt + i, weapon="short_spear", grip="ready",
                               thrust=max(0, math.sin(lt * 6 + i)) ** 2, shield="front",
                               eyes="scared" if rec > 0 else "angry", tilt=-0.15 * (rec > 0)))
        if shot == "body":
            n = sum(lt > p_ for p_ in pushes)
            if n:
                k = ease_back(prog(lt, pushes[n - 1], pushes[n - 1] + 0.3))
                ctx.save()
                ctx.translate(W / 2, 250)
                ctx.scale(k, k)
                text(ctx, f"{n}", 0, 60, "Cinzel Black", 170, "#ffe14a", outline=OUT, olw=10, shadow=(5, 7))
                ctx.restore()
        return {"letterbox": 1.0, "vignette": 0.6}

    if shot in ("hill", "teeth", "rain", "fall"):
        rain = shot in ("rain", "fall")
        fall = shot == "fall"
        darken = prog(lt, tg["rain"] + 0.5, tg["rain"] + 2.5)
        cam = Cam(960, 640, 1.0) if shot != "teeth" else Cam(960, 640, 1.5)
        if fall:
            cam = cam_lerp(Cam(960, 640, 1.0), Cam(960, 700, 1.35), ease(prog(st, 0, sl)))
        with world(ctx, cam, shake=2 if shot == "teeth" else 0, t=lt):
            set_thermopylae(ctx, lt, "dusk" if not rain else "dark", x1=3600)
            _hill(ctx)
            retreat = ease(prog(lt, tg["hill"] + 1.5, tg["hill"] + 4.0))
            n_alive = 9 if not fall else int(lerp(9, 0, prog(st, 0.3, sl - 0.6)))
            for i in range(9):
                ang = -0.6 + i * 0.15
                x = lerp(300 + i * 160, 820 + i * 40, retreat)
                y = lerp(GY, GY - 150 + abs(i - 4) * 18, retreat)
                dead = i >= n_alive
                face = 1 if i >= 4 else -1
                lk = YOU if i == 4 else spartan(i + 20)
                if shot == "teeth" and i in (3, 4, 5):
                    continue
                draw_char(ctx, x, y, 0.9, lk,
                          Pose(face=face, t=lt + i, grip="ready" if not rain else "rest",
                               shield="up" if rain and not dead else ("front" if not dead else "none"),
                               eyes="angry" if not dead else "closed", blink=not dead,
                               fall=ease_out(prog(lt, tg["fall"] + 0.3 + (8 - i) * 0.3, tg["fall"] + 0.8 + (8 - i) * 0.3)) if fall else 0,
                               weapon="sword" if shot == "teeth" else "spear", broken=True))
            # Immortals closing in from the left / Persians right
            close = ease(prog(lt, tg["hill"], tg["hill"] + 3.0))
            for i in range(12):
                side = -1 if i % 2 == 0 else 1
                x = 960 + side * lerp(1400, 900 - (i // 2) * 40, close)
                lk = immortal(i) if side < 0 else persian(i)
                draw_char(ctx, x, GY + 30 + (i % 3) * 10, 0.95, lk,
                          Pose(face=-side, t=lt + i, weapon="bow" if rain else "short_spear",
                               grip="ready", shield="none" if rain else "front",
                               thrust=ease(prog(lt, tg["rain"] + 0.4, tg["rain"] + 1.2)) if rain and lt < tg["rain"] + 1.4 else 0,
                               eyes="angry"))
            if shot == "teeth":
                fight_cloud(ctx, 960, 680, lt, 1.4, seed=3)
            if rain:
                fx.volley(ctx, lt, tg["rain"] + 1.3, 31, 70, (0, 700, 300, 800), (700, 620, 1250, 760),
                          dur=1.6, apex=500, size=1.0, spread=1.2)
                fx.volley(ctx, lt, tg["rain"] + 1.4, 32, 70, (1620, 700, 1920, 800), (700, 620, 1250, 760),
                          dur=1.6, apex=500, size=1.0, spread=1.2)
                if lt > tg["fall"]:
                    fx.volley(ctx, lt, tg["fall"], 33, 120, (-200, -400, 2100, -300), (650, 600, 1300, 780),
                              dur=2.2, apex=-50, size=1.0, spread=2.6)
        if rain:
            fx.tint(ctx, W, H, "#1a1a2a", 0.45 * darken)
        if fall:
            desat(ctx, 0.6 * prog(st, 0.5, sl))
            fx.flash(ctx, W, H, ease(prog(st, sl - 1.2, sl)), "#ffffff")
        if shot == "hill":
            k = ease_back(prog(st, 2.2, 2.6))
            if k > 0:
                overlay.banner(ctx, 960, 200, "KOLONOS TEPESİ", size=50, s=k, fill="#5a3a1a")
        return {"letterbox": 1.0, "vignette": 0.65}

    # end: quiet sunset over the hill
    k = prog(st, 0, 1.5)
    with world(ctx, Cam(960, 600, 1.05 - 0.04 * prog(st, 0, sl))):
        bg.sky(ctx, -200, -200, 2200, 1300, "#2a0e10", "#e8703a", "#8a2a1a")
        bg.sun(ctx, 960, 760, 150, "#ffd08a", "#ff6a2a", 0.6)
        bg.mountains(ctx, 5, -300, 2300, 860, 360, "#2a1210", rough=1.0, outline=False)
        _hill(ctx, color="#1a0c0a")
        bg.ground(ctx, -300, 2300, 880, 1300, "#1a0c0a", pebbles=False)
        r = rng(4)
        for i in range(9):
            x = 700 + i * 65
            y = 760 + abs(i - 4) * 14
            a = -PI / 2 + r.uniform(-0.35, 0.35)
            limb(ctx, [(x, y), (x + math.cos(a) * 200, y + math.sin(a) * 200)], "#120806", 6, 0)
        for x in (820, 1010, 1130):
            ctx.save()
            ctx.translate(x, 790)
            ctx.scale(0.5, 0.5)
            circle(ctx, 0, 0, 52)
            src(ctx, "#120806")
            ctx.fill()
            ctx.move_to(-60, -40)
            ctx.curve_to(-40, -110, 50, -110, 70, -40)
            ctx.set_line_width(26)
            ctx.stroke()
            ctx.restore()
        fx.particles(ctx, lt, -200, 0, 2200, 1100, n=40, seed=8, kind="embers", alpha=0.6)
    fx.flash(ctx, W, H, 1 - k, "#ffffff")
    return {"letterbox": 1.0, "vignette": 0.7}


def draw_spear_piece(ctx, x, y, a, alpha):
    ca, sa = math.cos(a), math.sin(a)
    limb(ctx, [(x - ca * 40, y - sa * 40), (x + ca * 40, y + sa * 40)], "#7a4e2a", 7, 3)


def final_sfx(S):
    t0 = S.start
    tg = {k: S.t(k) for k in ("advance", "clash", "swords", "leofall", "protect", "body", "hill",
                              "teeth", "rain", "fall", "end")}
    foes = list(_final_foes(round(tg["clash"] - 2.2, 3), round(tg["leofall"] + 0.3, 3)))
    ev = []
    for i in range(int((tg["clash"] - 1.0) / 0.5)):
        ev.append((t0 + 0.8 + i * 0.5, "march_step", 0.4, 0.0))
    ev.append((t0 + tg["clash"] - 1.2, "war_cry", 0.9, 0.0))
    ev.append((t0 + tg["clash"] - 0.05, "impact_big", 1.0, 0.0))
    ev.append((t0 + tg["clash"], "battle_amb", 0.0, 0.0))
    ev += [e for e in clash_events(foes, t0, 1180 + CONTACT, gain=1.1)
           if t0 + tg["clash"] - 0.2 < e[0] < t0 + tg["leofall"]]
    ev += [(t0 + tg["swords"] + 0.2, "spear_break", 0.8, 0.2), (t0 + tg["swords"] + 0.5, "sword_draw", 0.7, -0.2),
           (t0 + tg["leofall"] + 0.3, "slowmo", 0.8, 0.0), (t0 + tg["leofall"] + 0.6, "heartbeat", 0.8, 0.0),
           (t0 + tg["protect"], "war_cry", 0.7, 0.0)]
    for j in range(4):
        p_ = t0 + tg["body"] + 0.5 + j * 1.3
        ev += [(p_, "shield_bash", 0.8, 0.0), (p_ + 0.05, "drum_hit", 0.7, 0.0), (p_ + 0.1, "clang", 0.5, 0.3)]
    ev += [(t0 + tg["hill"] + 0.3, "horn", 0.6, -0.6), (t0 + tg["hill"] + 1.0, "war_cry", 0.5, -0.5),
           (t0 + tg["teeth"], "brawl", 0.8, 0.0), (t0 + tg["rain"] + 0.5, "bow_creak", 0.6, 0.0),
           (t0 + tg["rain"] + 1.3, "bow_release", 0.9, 0.0), (t0 + tg["rain"] + 1.4, "arrow_swarm", 0.8, 0.0)]
    for tl in fx.volley_land_times(31, 70, 1.6, 1.2)[::3]:
        ev.append((t0 + tg["rain"] + 1.3 + tl, "arrow_thunk", 0.2, -0.3))
    ev += [(t0 + tg["fall"], "arrow_swarm", 0.7, 0.0), (t0 + tg["fall"] + 0.2, "heartbeat", 0.9, 0.0),
           (t0 + tg["fall"] + 1.6, "heartbeat", 0.7, 0.0), (t0 + tg["end"] - 0.5, "whoosh_soft", 0.5, 0.0),
           (t0 + tg["end"] + 0.5, "wind", 0.5, 0.0)]
    return ev
