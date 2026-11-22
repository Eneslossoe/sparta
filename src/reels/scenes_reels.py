# -*- coding: utf-8 -*-
"""Vertical (1080x1920) scenes for the Reels cut. Reuses the long video's characters & sets."""
import math
from contextlib import contextmanager

from draw import backgrounds as bg
from draw import fx, overlay
from draw.characters import Look, Pose, draw_baby, draw_char, draw_tag, greek, immortal, mede, persian, spartan
from draw.core import (OUT, PI, Cam, cam_lerp, circle, clamp, ease, ease_back, ease_out, ellipse,
                       fill_stroke, lerp, limb, poly, prog, rad_grad, rng, rrect, smooth_poly, src, text)
from scenes.common import (battle, phalanx, set_persian_camp, set_sparta, set_thermopylae, talk,
                           wave_schedule, clash_events)
from scenes.s_battle import EPH, LEO, XER, _hill, draw_torch_pole
from scenes.s_persia import HERALD, palace
from scenes.s_sparta import BOY, ELDERS, MOTHER, TRAINER

RW, RH = 1080, 1920
YOU = spartan(1, spk="SEN")


@contextmanager
def rworld(ctx, cam, shake=0.0, t=0.0):
    ctx.save()
    cam.apply(ctx, RW, RH, shake, t)
    try:
        yield
    finally:
        ctx.restore()


def tag(ctx, x, y, label, lt, t0, t1=99, s=1.3):
    if lt < t0 or lt > t1:
        return
    k = ease_out(prog(lt, t0, t0 + 0.25))
    draw_tag(ctx, x, y, label, s=s * (0.6 + 0.4 * k), alpha=k * clamp((t1 - lt) / 0.25))


def big_word(ctx, s, y, lt, t0, size=150, color="#ffd34a", rot=-0.04):
    if lt < t0:
        return
    k = max(0.01, ease_back(prog(lt, t0, t0 + 0.3), 2.2))
    ctx.save()
    ctx.translate(RW / 2, y)
    ctx.rotate(rot)
    ctx.scale(k, k)
    text(ctx, s, 0, size * 0.35, "Cinzel Black", size, color, outline="#1a0c06", olw=size * 0.08,
         shadow=(6, 8))
    ctx.restore()


def whoosh_in(S):
    return [(S.start + 0.0, "whoosh", 0.35, 0.0)]


# ===================================================================== hook
def r_hook(ctx, S, lt):
    z = 1.0 + 0.05 * lt
    bg.sky(ctx, 0, 0, RW, RH, "#141c30", "#a8603a", "#4a2a2a")
    bg.sun(ctx, 760, 1180, 90, "#ffd08a", "#ff7a3a", 0.4)
    fx.arrow_cloud(ctx, lt, -200, RW + 200, 60, 900, density=1.0, seed=5, ang=0.3, speed=650, size=1.0)
    ctx.save()
    ctx.translate(RW / 2, RH)
    ctx.scale(z, z)
    ctx.translate(-RW / 2, -RH)
    draw_char(ctx, 560, 2120, 3.9, YOU,
              Pose(face=1, t=lt, grip="rest", shield="none", eyes="angry", mshape="line"))
    ctx.restore()
    tag(ctx, 830, 1270, "SEN", lt, 0.9, 99, s=1.6)
    k = max(0.01, ease_back(prog(lt, 0.05, 0.4), 2.0))
    ctx.save()
    ctx.translate(RW / 2, 470)
    ctx.scale(k, k)
    text(ctx, "300", 0, 90, "Cinzel Black", 290, "#ffd34a", outline="#1a0c06", olw=20, shadow=(8, 12))
    ctx.restore()
    k2 = ease_back(prog(lt, 0.35, 0.7))
    if k2 > 0:
        overlay.banner(ctx, RW / 2, 680, "SPARTALI OLSAYDIN?", size=70, s=k2, rot=-0.04)
    return {"sub_y": 930, "banner": False}


def r_hook_sfx(S):
    return [(S.start + 0.02, "boom", 0.9, 0.0), (S.start + 0.05, "arrow_swarm", 0.5, 0.0),
            (S.start + 0.4, "drum_hit", 0.8, 0.0), (S.start + 0.9, "pop", 0.5, 0.3)]


# ===================================================================== birth
def r_birth(ctx, S, lt):
    with rworld(ctx, Cam(1450, 690, 1.75 + 0.04 * lt)):
        set_sparta(ctx, lt, houses=False)
        bg.olive(ctx, 1480, 860, 1.3, lt)
        rrect(ctx, 1280, 790, 380, 26, 6)
        fill_stroke(ctx, "#8a6a3a", 4)
        doubt = lt > S.dur * 0.55
        for i, lk in enumerate(ELDERS):
            draw_char(ctx, 1340 + i * 120, 860, 0.9, lk,
                      Pose(face=-1, t=lt + i, sit=True, weapon="none", shield="none",
                           arm=(34, -120) if i == 1 else None,
                           eyes="sly" if doubt else "normal", look=(-0.5, -0.3),
                           mshape="frown" if doubt else "line"))
        ctx.save()
        ctx.translate(1460 - 32 * 0.9, 860 - 120 * 0.9 + 30)
        ctx.rotate(math.sin(lt * 3.2) * 0.4)
        draw_baby(ctx, 0, 0, 0.62, lt, eyes="open", cry=doubt)
        ctx.restore()
    tag(ctx, 470, 760, "SEN", lt, 0.4, 99)
    tag(ctx, 640, 360, "SPARTA", lt, 0.2, 99, s=1.1)
    return {}


def r_birth_sfx(S):
    return whoosh_in(S) + [(S.start + 0.3, "baby", 0.45, 0.0), (S.start + S.dur * 0.55, "sting_low", 0.35, 0.0)]


# ===================================================================== agoge
def r_agoge(ctx, S, lt):
    cut = 1.9
    if lt < cut:
        k = ease(prog(lt, 0.3, cut))
        with rworld(ctx, Cam(930 + 120 * k, 730, 1.9)):
            set_sparta(ctx, lt)
            bg.house(ctx, 640, 870, 1.2)
            draw_char(ctx, 720, 880, 1.0, MOTHER,
                      Pose(face=1, t=lt, weapon="none", shield="none", arm=(40, -150 + 20 * math.sin(lt * 7)),
                           eyes="sad", mshape="frown"))
            bx, tx = 860 + 260 * k, 1000 + 260 * k
            draw_char(ctx, tx, 885, 1.05, TRAINER,
                      Pose(face=1, t=lt, walk=lt * 7, weapon="none", shield="none", arm=(-40, -60),
                           eyes="angry"))
            draw_char(ctx, bx, 885, 1.0, BOY,
                      Pose(face=-1, t=lt, walk=lt * 9, weapon="none", shield="none", eyes="sad",
                           mshape="frown", arm=(30, -80)))
        tag(ctx, 560, 640, "7 YAŞ", lt, 0.3, cut)
        return {}
    st = lt - cut
    scroll = st * 480
    with rworld(ctx, Cam(900, 820, 1.25)):
        bg.sky(ctx, -200, -400, 2200, 1200, "#8ac8ea", "#f2e2c0")
        ctx.save()
        ctx.translate(-scroll * 0.15, 0)
        bg.mountains(ctx, 21, -400, 3000, 700, 400, "#8f8fb0", snow="#f4f4fa")
        ctx.restore()
        bg.ground(ctx, -200, 2200, 860, 1700, "#c4a87a", pebbles=False)
        for i in range(40):
            x = (i * 137 - scroll) % 2300 - 200
            bg.rock(ctx, x, 940 + (i % 3) * 50, 0.3 + (i % 4) * 0.08, seed=i)
        for i in range(3):
            draw_char(ctx, 720 + i * 230 + math.sin(lt * 1.3 + i) * 20, 1010 + (i % 2) * 40, 1.6, BOY,
                      Pose(face=1, t=lt + i, walk=lt * 13 + i, run=True, weapon="none", shield="none",
                           eyes="angry", sweat=True))
        draw_char(ctx, 470, 1060, 1.35, TRAINER,
                  Pose(face=1, t=lt, walk=lt * 12, run=True, weapon="stick",
                       thrust=max(0, math.sin(lt * 5)) ** 2, shield="none", eyes="angry", mshape="shout"))
    big_word(ctx, "YALINAYAK!", 470, lt, cut + 0.5, size=110, color="#ffffff")
    return {}


def r_agoge_sfx(S):
    ev = whoosh_in(S) + [(S.start + 0.4, "footsteps", 0.3, 0.0)]
    for i in range(14):
        ev.append((S.start + 1.9 + i * 0.18, "step", 0.22, 0.0))
    ev.append((S.start + 2.4, "stamp", 0.5, 0.0))
    return ev


# ===================================================================== steal
def r_steal(ctx, S, lt):
    line = S.beats[0]
    ln = line.speech_end - line.start
    t_grab = ln * 0.38
    t_caught = ln * 0.62
    t_bonk = S.t("bonk") + 0.05
    caught = lt > t_caught
    whack = lt > t_bonk
    sneak = ease(prog(lt, 0.0, t_grab))
    bx = lerp(700, 900, sneak)
    with rworld(ctx, Cam(860, 760, 2.0)):
        bg.sky(ctx, -300, -300, 2300, 1300, "#0b1430", "#2a3a6a")
        bg.stars(ctx, -300, -300, 2300, 600, lt)
        bg.moon(ctx, 1080, 420, 30)
        bg.ground(ctx, -300, 2300, 880, 1400, "#3a3a4a", pebbles=False)
        rrect(ctx, 960, 790, 300, 22, 5)
        fill_stroke(ctx, "#6b4a2a", 4)
        for lx in (980, 1220):
            rrect(ctx, lx, 810, 18, 70, 3)
            fill_stroke(ctx, "#6b4a2a", 3.5)
        grabbed = lt > t_grab
        if not grabbed:
            ellipse(ctx, 1040, 778, 50, 22)
            fill_stroke(ctx, "#d9a05a", 4)
        circle(ctx, 1150, 774, 16)
        fill_stroke(ctx, "#c83a3a", 3.5)
        jump = math.sin(clamp((lt - t_bonk) / 0.4) * PI) * 50 if whack else 0
        draw_char(ctx, bx, 900, 1.0, BOY,
                  Pose(face=1, t=lt, walk=lt * 6 if sneak < 1 else None, tilt=0.18 if not caught else 0,
                       weapon="none", shield="none", arm=(40, -100) if grabbed else (50, -60),
                       eyes="sly" if not caught else ("dead" if whack else "scared"), sweat=caught,
                       mshape="grin" if grabbed and not caught else ("o" if caught else "line"),
                       jump=jump, look=(1, 0) if not caught else (-1, 0)))
        if grabbed:
            ellipse(ctx, bx + 45, 900 - 108, 40, 18)
            fill_stroke(ctx, "#d9a05a", 4)
        if caught:
            k = ease_back(prog(lt, t_caught, t_caught + 0.3))
            hit = prog(lt, t_bonk - 0.1, t_bonk + 0.2)
            draw_char(ctx, bx - 190, 900, 1.15 * k, TRAINER,
                      Pose(face=1, t=lt, weapon="stick", shield="none", thrust=math.sin(hit * PI),
                           eyes="angry", mshape="shout"))
            if whack:
                fx.pow_star(ctx, bx + 10, 900 - 200, lt - t_bonk, 2.0)
    if whack:
        big_word(ctx, "DAYAK!", 470, lt, t_bonk, size=150, color="#ff5a3a", rot=0.05)
    return {}


def r_steal_sfx(S):
    line = S.beats[0]
    ln = line.speech_end - line.start
    return whoosh_in(S) + [(S.start + 0.1, "sneak", 0.45, -0.2), (S.start + ln * 0.38, "pop", 0.4, 0.0),
                           (S.start + ln * 0.62, "sting", 0.5, 0.0), (S.start + S.t("bonk") + 0.05, "bonk", 0.9, 0.0),
                           (S.start + S.t("bonk") + 0.2, "birdies", 0.5, 0.0)]


# ===================================================================== xerxes
def r_xerxes(ctx, S, lt):
    cut = 2.5
    if lt < cut:
        with rworld(ctx, Cam(960, 800, 1.0 + 0.03 * lt), shake=3 if lt > 1.2 else 0, t=lt):
            palace(ctx, lt)
            ctx.rectangle(-400, 1470, 2800, 1200)
            src(ctx, "#7a4e32")
            ctx.fill()
            draw_char(ctx, 900, 1170, 3.3, XER,
                      Pose(face=1, t=lt, weapon="none", shield="none", arm=(95, -125) if lt > 0.5 else None,
                           eyes="angry", mshape="shout" if lt > 1.0 else "line"))
        tag(ctx, 540, 360, "KRAL KSERKSES", lt, 0.3, cut, s=1.2)
        return {}
    st = lt - cut
    with rworld(ctx, Cam(960, 700, 1.05 + 0.03 * st)):
        bg.sky(ctx, -300, -400, 2300, 800, "#e8a85a", "#f8e2b0")
        bg.sun(ctx, 1200, 360, 60, glow="#ffb060")
        bg.mountains(ctx, 51, -400, 2400, 640, 260, "#b08a6a", outline=False)
        bg.ground(ctx, -400, 2400, 620, 1700, "#d4b07a", pebbles=False)
        fx.dust_cloud(ctx, -200, 2200, 650, lt, seed=4, alpha=0.4, h=60)
        for row in range(16, -1, -1):
            for i in range(16):
                x = 420 + i * 72 + (row % 2) * 36 + (lt * 40) % 72
                draw_char(ctx, x, 660 + row * 40, 0.24 + row * 0.03,
                          persian(i + row) if (i + row) % 3 else mede(i),
                          Pose(face=1, t=lt + i, walk=lt * 7 + i + row, weapon="short_spear",
                               grip="march", shield="front"), lod=True)
    big_word(ctx, "DEV ORDU", 470, lt, cut + 0.3, size=130, color="#ffffff")
    return {}


def r_xerxes_sfx(S):
    return whoosh_in(S) + [(S.start + 0.1, "fanfare_persian", 0.45, 0.0), (S.start + 1.2, "boom", 0.4, 0.0),
                           (S.start + 2.5, "march_big", 0.6, 0.0), (S.start + 2.8, "drum_hit", 0.6, 0.0)]


# ===================================================================== pass
def r_pass(ctx, S, lt):
    t7 = S.t("7000")
    allies = ease_out(prog(lt, t7, t7 + 1.0))
    with rworld(ctx, Cam(760, 760, 1.3 + 0.03 * lt)):
        set_thermopylae(ctx, lt, "day", wall=(250, 640, 110))
        if allies > 0:
            for lane in range(2):
                for i in range(5):
                    x = lerp(-400, 160 + i * 70, allies) - lane * 15
                    draw_char(ctx, x, 880 - lane * 28, 0.8 - lane * 0.05,
                              greek(i + lane * 5, cloak=["#2f5f9a", "#2f7a4a", "#6a3a7a"][i % 3],
                                    emblem=["star", "crescent", "bull"][i % 3]),
                              Pose(face=1, t=lt + i, grip="rest", shield="front"))
        phalanx(ctx, lt, 1000, 920, s=1.0, lanes=3, ranks=4, grip="rest", eyes="angry", leo=(0, 1))
    tag(ctx, 640, 640, "LEONİDAS", lt, 0.5, t7)
    n = int(lerp(300, 7000, ease(prog(lt, t7 + 0.2, t7 + 1.4))))
    big_word(ctx, ("~" if lt > t7 + 0.8 else "") + f"{n:,}".replace(",", "."), 450, lt, 0.4, size=140)
    return {}


def r_pass_sfx(S):
    return whoosh_in(S) + [(S.start + 0.4, "drum_hit", 0.7, 0.0), (S.start + S.t("7000") + 0.2, "counter", 0.5, 0.0),
                           (S.start + S.t("7000"), "march_far", 0.4, -0.4)]


# ===================================================================== molon labe
def r_molon(ctx, S, lt):
    tm = S.t("molon")
    if lt < tm:
        with rworld(ctx, Cam(1000, 760, 1.6)):
            set_thermopylae(ctx, lt, "day", wall=(-200, 700, 110))
            phalanx(ctx, lt, 760, 900, s=1.0, lanes=2, ranks=3, grip="rest", eyes="angry")
            draw_char(ctx, 1180, 920, 1.05, HERALD,
                      Pose(face=-1, t=lt, weapon="scroll", shield="none", arm=(50, -140),
                           eyes="angry", mshape="shout" if lt < tm * 0.5 else "line"))
        tag(ctx, 760, 500, "PERS HABERCİSİ", lt, 0.2, tm, s=1.0)
        return {}
    st = lt - tm
    with rworld(ctx, Cam(540, 960, 1.0 + 0.25 * ease_out(prog(st, 0, 0.25))),
                shake=10 * (1 - prog(st, 0.05, 0.7)), t=lt):
        bg.sky(ctx, -400, -400, 1500, 2400, "#3a2a20", "#a86a3a")
        fx.speed_lines(ctx, 540, 1000, lt, alpha=0.35, color=(1, 0.9, 0.7), r1=1700)
        draw_char(ctx, 560, 1640, 3.7, LEO,
                  Pose(face=1, t=lt, grip="rest", shield="none", eyes="angry", mouth=talk("LEO"),
                       mshape="shout"))
    big_word(ctx, "MOLON LABE", 430, lt, tm + 0.35, size=120, color="#ffd34a")
    return {"sub_y": 1500}


def r_molon_sfx(S):
    tm = S.start + S.t("molon")
    return whoosh_in(S) + [(S.start + 0.1, "horn", 0.35, 0.4), (tm - 0.05, "boom", 0.9, 0.0),
                           (tm, "whoosh_big", 0.6, 0.0), (tm + 0.35, "drum_hit", 0.8, 0.0)]


# ===================================================================== battle
_FOES = {}


def _foes(S):
    if S.id not in _FOES:
        _FOES[S.id] = wave_schedule(77, -1.6, S.dur, 2.8, 760 + 145, kind="immortal", speed=(340, 420),
                                    fight=(0.5, 1.3))
    return _FOES[S.id]


def r_battle(ctx, S, lt):
    foes = _foes(S)
    with rworld(ctx, Cam(890, 780, 1.55), shake=4, t=lt):
        set_thermopylae(ctx, lt, "day", wall=(-400, 520, 110))
        fx.dust_cloud(ctx, 600, 1300, 890, lt, alpha=0.3)
        battle(ctx, lt, foes, 760, 900, s=1.0, ranks=4, you=(1, 0))
        for f in foes:
            if f.lane == 0:
                fx.sparks(ctx, 850, 750, lt - (f.tf - 0.1), seed=f.seed, size=1.2)
                fx.pow_star(ctx, 900, 770, lt - (f.tf - 0.05), 0.9, dur=0.3)
    big_word(ctx, "2 GÜN!", 450, lt, 0.3, size=140, color="#ffffff")
    return {}


def r_battle_sfx(S):
    ev = whoosh_in(S) + [(S.start + 0.0, "war_cry", 0.6, 0.3), (S.start + 0.0, "battle_amb_short", 0.5, 0.0)]
    ev += [e for e in clash_events(_foes(S), S.start, 760 + 145) if S.start <= e[0] < S.end]
    return ev


# ===================================================================== betrayal
def r_betray(ctx, S, lt):
    bg.sky(ctx, 0, 0, RW, RH, "#050a1e", "#1a2448")
    bg.stars(ctx, 0, 0, RW, 900, lt)
    bg.moon(ctx, 860, 300, 50)
    bg.mountains(ctx, 71, -200, RW + 200, 1500, 1050, "#141a2e", rough=1.0, outline=False)
    path = [(80, 1350), (300, 1220), (180, 1060), (520, 960), (400, 820), (760, 740), (700, 600), (1000, 520)]
    smooth_poly(ctx, path, close=False)
    src(ctx, (0.6, 0.5, 0.3, 0.3))
    ctx.set_line_width(6)
    ctx.set_dash([10, 12])
    ctx.stroke()
    ctx.set_dash([])
    L = len(path) - 1
    for i in range(30):
        u = (lt * 0.1 + i * 0.03) % 1.0
        seg = u * L
        j = min(int(seg), L - 1)
        f = seg - j
        x = lerp(path[j][0], path[j + 1][0], f)
        y = lerp(path[j][1], path[j + 1][1], f)
        ctx.set_source(rad_grad(x, y - 10, 0, 34, [(0, (1, 0.8, 0.3, 0.9)), (1, (1, 0.5, 0.1, 0))]))
        circle(ctx, x, y - 10, 34)
        ctx.fill()
    ctx.set_source(rad_grad(380, 1400, 20, 500, [(0, (1, 0.6, 0.25, 0.35)), (1, (1, 0.5, 0.2, 0))]))
    circle(ctx, 380, 1400, 500)
    ctx.fill()
    draw_char(ctx, 470, 1900, 3.0, EPH,
              Pose(face=1, t=lt, weapon="torch", shield="none", arm=(55, -150), eyes="sly",
                   look=(1, -0.3), mshape="grin", tilt=0.08))
    tag(ctx, 470, 1060, "HAİN EFİALTES", lt, 0.3, 99, s=1.3)
    return {}


def r_betray_sfx(S):
    return whoosh_in(S) + [(S.start + 0.1, "crickets", 0.4, 0.0), (S.start + 0.3, "sneak", 0.45, 0.0),
                           (S.start + 1.5, "owl", 0.3, 0.5), (S.start + 2.2, "sting_low", 0.45, 0.0)]


# ===================================================================== last stand
def r_last(ctx, S, lt):
    tf = S.t("fall")
    darken = prog(lt, 0.8, 2.5)
    falling = lt > tf - 0.3
    with rworld(ctx, Cam(960, 700, 1.3 + 0.05 * prog(lt, 0, S.dur))):
        set_thermopylae(ctx, lt, "dark", x1=3600)
        _hill(ctx)
        for i in range(7):
            x = 840 + i * 40
            y = 750 + abs(i - 3) * 18
            fall = ease_out(prog(lt, tf - 0.3 + (6 - i) * 0.18, tf + 0.1 + (6 - i) * 0.18))
            draw_char(ctx, x, y, 0.95, YOU if i == 3 else spartan(i + 20),
                      Pose(face=1 if i >= 3 else -1, t=lt + i, grip="rest", shield="up" if fall < 0.3 else "none",
                           eyes="angry" if fall < 0.3 else "closed", blink=fall < 0.3, fall=fall))
        for i in range(6):
            side = -1 if i % 2 == 0 else 1
            x = 960 + side * (400 + (i // 2) * 60)
            draw_char(ctx, x, 950 + (i % 3) * 10, 0.95, immortal(i) if side < 0 else persian(i),
                      Pose(face=-side, t=lt + i, weapon="bow", shield="none",
                           thrust=ease(prog(lt, 0.2, 0.9)) if lt < 1.0 else 0, eyes="angry"))
        fx.volley(ctx, lt, 1.0, 41, 60, (500, 760, 600, 840), (820, 640, 1100, 780), dur=1.4, apex=380, spread=1.4)
        fx.volley(ctx, lt, 1.1, 42, 60, (1320, 760, 1420, 840), (820, 640, 1100, 780), dur=1.4, apex=380, spread=1.4)
        if falling:
            fx.volley(ctx, lt, tf - 0.6, 43, 90, (400, -300, 1500, -200), (800, 600, 1120, 780), dur=1.8,
                      apex=-40, spread=1.6)
    fx.tint(ctx, RW, RH, "#1a1a2a", 0.4 * darken)
    tag(ctx, 540, 560, "SON SAVAŞ", lt, 0.2, tf - 0.5, s=1.2)
    fx.flash(ctx, RW, RH, ease(prog(lt, S.dur - 0.9, S.dur)), "#ffffff")
    return {}


def r_last_sfx(S):
    tf = S.start + S.t("fall")
    ev = whoosh_in(S) + [(S.start + 0.2, "bow_creak", 0.5, 0.0), (S.start + 1.0, "bow_release", 0.8, 0.0),
                         (S.start + 1.1, "arrow_swarm", 0.7, 0.0)]
    for tl in fx.volley_land_times(41, 60, 1.4, 1.4)[::3]:
        ev.append((S.start + 1.0 + tl, "arrow_thunk", 0.2, -0.2))
    ev += [(tf - 0.6, "arrow_swarm", 0.6, 0.0), (tf - 0.2, "heartbeat", 0.9, 0.0), (tf + 0.9, "whoosh_soft", 0.5, 0.0)]
    return ev


# ===================================================================== CTA
def r_cta(ctx, S, lt):
    tq, tfw = S.t("q"), S.t("follow")
    bg.sky(ctx, 0, 0, RW, RH, "#1a0e0a", "#8a3a1a", "#4a1a0e")
    bg.sun(ctx, RW / 2, 1560, 240, "#ffcf7a", "#ff6a2a", 0.4)
    fx.particles(ctx, lt, 0, 0, RW, RH, n=50, seed=4, kind="embers", alpha=0.6)
    limb(ctx, [(700, 1700), (760, 1080)], "#5a3a1a", 12, 4)
    poly(ctx, [(756, 1080), (780, 1020), (770, 1084)])
    fill_stroke(ctx, "#d8a640", 4)
    ctx.save()
    ctx.translate(560, 1700)
    ctx.scale(2.2, 2.2)
    ctx.rotate(-0.15)
    ctx.translate(0, 112)
    from draw.characters import _spartan_helmet
    _spartan_helmet(ctx, spartan(1), Pose(t=lt))
    ctx.restore()
    fx.flash(ctx, RW, RH, 1 - prog(lt, 0, 0.5), "#ffffff")
    a = ease_out(prog(lt, tq, tq + 0.4))
    text(ctx, "SEN OLSAYDIN", RW / 2, 400, "Cinzel Black", 96, "#f6e3b4", outline="#2a0c06", olw=8, alpha=a, shadow=(4, 6))
    text(ctx, "KALIR MIYDIN?", RW / 2, 520, "Cinzel Black", 96, "#e8b04a", outline="#2a0c06", olw=8, alpha=a, shadow=(4, 6))
    for i, (lbl, col) in enumerate((("KALIRDIM", "#2a8a4a"), ("DÖNERDİM", "#b81e28"))):
        k = ease_back(prog(lt, tq + 0.8 + i * 0.3, tq + 1.1 + i * 0.3))
        if k > 0:
            ctx.save()
            ctx.translate(310 + i * 460, 680)
            ctx.scale(k, k)
            rrect(ctx, -200, -60, 400, 120, 60)
            fill_stroke(ctx, col, 6)
            text(ctx, lbl, 0, 22, "Baloo 2 ExtraBold", 58, "#ffffff")
            ctx.restore()
    if lt > tfw:
        k = max(0.01, ease_back(prog(lt, tfw, tfw + 0.35)))
        clicked = lt > tfw + 1.2
        ctx.save()
        ctx.translate(RW / 2, 880)
        ctx.scale(k * (0.92 if tfw + 1.1 < lt < tfw + 1.3 else 1.0), k)
        rrect(ctx, -260, -66, 520, 132, 66)
        fill_stroke(ctx, "#cc1f1f" if not clicked else "#5a5a5a", 6)
        text(ctx, "TAKİP ET" if not clicked else "TAKİP EDİLDİ", 0, 22, "Baloo 2 ExtraBold", 60, "#ffffff")
        ctx.restore()
        cx = lerp(900, 600, ease(prog(lt, tfw + 0.4, tfw + 1.1)))
        cy = lerp(1150, 900, ease(prog(lt, tfw + 0.4, tfw + 1.1)))
        poly(ctx, [(cx, cy), (cx, cy + 70), (cx + 19, cy + 54), (cx + 33, cy + 84),
                   (cx + 45, cy + 77), (cx + 31, cy + 49), (cx + 54, cy + 49)])
        fill_stroke(ctx, "#ffffff", 4)
    overlay.hourglass(ctx, RW / 2, 1150, 0.42, lt)
    text(ctx, "ZAMAN KIRIĞI", RW / 2, 1300, "Cinzel Black", 56, "#e9d3a0", outline="#2a1a0c", olw=5)
    return {"sub_y": 1430, "banner": False}


def r_cta_sfx(S):
    tq, tfw = S.start + S.t("q"), S.start + S.t("follow")
    return [(S.start, "whoosh_soft", 0.4, 0.0), (tq + 0.8, "pop", 0.5, -0.3), (tq + 1.1, "pop", 0.5, 0.3),
            (tfw, "pop", 0.6, 0.0), (tfw + 1.2, "click", 0.8, 0.0), (tfw + 1.3, "bell", 0.6, 0.0)]


REGISTRY = {name: (globals()[name], globals()[name + "_sfx"])
            for name in ("r_hook", "r_birth", "r_agoge", "r_steal", "r_xerxes", "r_pass", "r_molon",
                         "r_battle", "r_betray", "r_last", "r_cta")}
