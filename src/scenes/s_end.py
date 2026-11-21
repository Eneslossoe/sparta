# -*- coding: utf-8 -*-
"""Chapter XI + aftermath + outro."""
import math

import cairo

from draw import backgrounds as bg
from draw import fx, overlay
from draw.characters import HY, R, Look, Pose, draw_char, persian, spartan, greek
from draw.core import (OUT, PI, Cam, cam_lerp, circle, clamp, ease, ease_back, ease_out, ellipse,
                       fill_stroke, font, lerp, limb, poly, prog, rad_grad, rng, rrect, shade,
                       smooth_poly, src, text, text_w)
from .common import (G, H, W, phalanx, set_sparta, set_thermopylae, shots, tag_pop, talk, world)

ARIS = Look(kind="spartan", helmet=None, cloth="#a8222b", cloak="#8a1a20", hair="#4a3020",
            beard="#4a3020", seed=40)


def blindfold(ctx, x, y, s, face=1):
    ey = y + (HY - 0.02 * R) * s
    ctx.save()
    ctx.translate(x, ey)
    ctx.scale(face * s, s)
    rrect(ctx, -0.55 * R, -0.2 * R, 1.55 * R, 0.4 * R, 8)
    fill_stroke(ctx, "#f4f1ea", 4)
    limb(ctx, [(-0.55 * R, 0), (-0.95 * R, 0.5 * R)], "#f4f1ea", 9, 3)
    ctx.restore()


def survivor(ctx, S, lt):
    t_a, t_s, t_p = S.t("aris"), S.t("shame"), S.t("plataea")
    t_l = S.beats[-1].start - S.start
    shot, st, sl = shots(lt, S.dur, [(0, "road"), (t_a, "aris"), (t_s, "shame"), (t_p, "plataea"),
                                     (t_l, "helmet")])
    if shot in ("road", "aris"):
        k = ease(prog(lt, 0.3, S.dur))
        with world(ctx, Cam(960, 640, 1.25)):
            set_thermopylae(ctx, lt, "dusk")
            x = lerp(1250, 700, ease(prog(lt, t_a, t_s)))
            walking = shot == "aris" and lt < t_s - 0.2
            draw_char(ctx, x, 920, 1.1, ARIS,
                      Pose(face=-1, t=lt, walk=lt * 4 if walking else None, weapon="none",
                           shield="none", eyes="closed", blink=False, mshape="frown"))
            blindfold(ctx, x, 920, 1.1, face=-1)
            if shot == "road":
                q = ease_back(prog(lt, 2.9, 3.4))
                if q > 0:
                    text(ctx, "?", x - 40, 600, "Cinzel Black", 180 * q, "#ffffff", outline=OUT, olw=10)
        if shot == "aris":
            tag_pop(ctx, 960 + (x - 960) * 1.25, 330, "ARİSTODEMOS", st, 0.3, sl - 0.2)
        return {"vignette": 0.6}

    if shot == "shame":
        with world(ctx, Cam(960, 640, 1.2)):
            set_sparta(ctx, lt, tod="dusk")
            for i, x in enumerate((360, 560, 1360, 1560)):
                draw_char(ctx, x, 920, 1.0, spartan(i + 30, helmet=None, cloak="#7a1a20"),
                          Pose(face=1 if x < 960 else -1, t=lt, weapon="none", shield="none",
                               eyes="angry", arm=(50, -120) if i % 2 else None, mshape="frown"))
            draw_char(ctx, 960, 930, 1.05, ARIS,
                      Pose(face=1, t=lt, weapon="none", shield="none", eyes="sad", look=(0, 1),
                           mshape="frown", tilt=0.12))
        for i, (x, y, lbl) in enumerate(((480, 330, "TİTREK!"), (1460, 300, "KORKAK!"), (760, 220, "TİTREK!"))):
            k = ease_back(prog(st, 1.2 + i * 0.6, 1.6 + i * 0.6))
            if k > 0:
                overlay.bubble(ctx, x, y, lbl, size=44, s=k, tail=(-30 if x < 960 else 30, 60))
        return {"vignette": 0.6}

    if shot == "plataea":
        run = ease(prog(st, 0.2, 2.6))
        x = lerp(500, 1250, run)
        fallen = ease_out(prog(st, 2.6, 3.2))
        with world(ctx, Cam(lerp(800, 1150, run), 640, 1.2), shake=2, t=lt):
            bg.sky(ctx, -200, -300, 2400, 1000, "#3a0e0a", "#d8602a")
            bg.sun(ctx, 1500, 500, 90, "#ffd08a", "#ff6a2a", 0.5)
            bg.mountains(ctx, 81, -300, 2500, 820, 300, "#4a2a2a", outline=False)
            bg.ground(ctx, -300, 2500, 880, 1300, "#6a4a32", pebbles=False)
            fx.dust_cloud(ctx, 800, 2000, 870, lt, alpha=0.35)
            phalanx(ctx, lt, 520 + run * 300, 930, s=0.9, lanes=2, ranks=4, walk=lt * 6, grip="ready")
            for i in range(6):
                draw_char(ctx, 1400 + i * 100, 930 - (i % 2) * 25, 0.9, persian(i),
                          Pose(face=-1, t=lt + i, weapon="short_spear", grip="ready", shield="front",
                               eyes="scared"))
            draw_char(ctx, x, 950, 1.05, spartan(40, helmet="#b08a3a"),
                      Pose(face=1, t=lt, walk=lt * 12 if run < 1 else None, run=True, weapon="sword",
                           thrust=abs(math.sin(lt * 6)), shield="front", eyes="angry", mshape="shout",
                           fall=fallen))
        overlay.caption(ctx, W, H, "PLATAİA · M.Ö. 479", st, 0.2, sl - 0.2, y=230)
        return {"vignette": 0.6, "letterbox": 1.0}

    # helmet on the ground
    with world(ctx, Cam(960, 600, 1.0 + 0.03 * st)):
        bg.sky(ctx, -200, -300, 2400, 1300, "#2a1a2a", "#e8905a")
        bg.sun(ctx, 960, 700, 110, "#ffe0a0", "#ff8a4a", 0.5)
        bg.ground(ctx, -300, 2500, 820, 1300, "#5a4032", pebbles=False)
        ctx.save()
        ctx.translate(960, 820)
        ctx.scale(3.0, 3.0)
        ctx.rotate(0.25)
        ctx.translate(0, 112)
        from draw.characters import _spartan_helmet
        lk = spartan(40)
        _spartan_helmet(ctx, lk, Pose(t=lt))
        ctx.restore()
    return {"vignette": 0.6}


def survivor_sfx(S):
    t0 = S.start
    return [(t0 + 0.4, "wind", 0.4, 0.0), (t0 + S.t("aris") + 0.3, "footsteps", 0.3, -0.3),
            (t0 + S.t("shame") + 1.2, "pop", 0.4, -0.5), (t0 + S.t("shame") + 1.8, "pop", 0.4, 0.5),
            (t0 + S.t("shame") + 2.4, "pop", 0.4, 0.0), (t0 + S.t("shame") + 1.3, "crowd_boo", 0.45, 0.0),
            (t0 + S.t("plataea"), "war_cry", 0.6, 0.0), (t0 + S.t("plataea") + 0.3, "battle_amb_short", 0.6, 0.0),
            (t0 + S.t("plataea") + 2.6, "stab", 0.6, 0.2), (S.beats[-1].start + 0.2, "wind", 0.4, 0.0)]


# ======================================================================= AFTERMATH
def lion(ctx, x, y, s=1.0, color="#b8b0a0"):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ellipse(ctx, 0, -60, 120, 55)
    fill_stroke(ctx, color, 5)
    for lx in (-80, -40, 50, 90):
        rrect(ctx, lx - 14, -40, 28, 50, 8)
        fill_stroke(ctx, shade(color, -0.05), 4)
    ctx.move_to(-115, -80)
    ctx.curve_to(-190, -110, -190, -30, -150, -20)
    src(ctx, OUT)
    ctx.set_line_width(14)
    ctx.stroke_preserve()
    src(ctx, color)
    ctx.set_line_width(8)
    ctx.stroke()
    for i in range(12):
        a = i * PI / 6
        circle(ctx, 110 + math.cos(a) * 52, -120 + math.sin(a) * 52, 26)
        ctx.new_sub_path()
    fill_stroke(ctx, shade(color, -0.12), 5)
    circle(ctx, 115, -120, 44)
    fill_stroke(ctx, color, 5)
    ellipse(ctx, 150, -108, 22, 16)
    fill_stroke(ctx, shade(color, 0.05), 4)
    circle(ctx, 128, -132, 5)
    src(ctx, OUT)
    ctx.fill()
    ctx.restore()


def aftermath(ctx, S, lt):
    t_s, t_p, t_st, t_e = S.t("salamis"), S.t("plataea"), S.t("stone"), S.t("epitaph")
    shot, st, sl = shots(lt, S.dur, [(0, "athens"), (t_s, "salamis"), (t_p, "plataea"),
                                     (t_st, "stone")])
    if shot == "athens":
        with world(ctx, Cam(960, 560, 1.0 + 0.04 * st)):
            bg.sky(ctx, -200, -300, 2200, 1300, "#2a0a0a", "#c8501a")
            bg.smoke(ctx, 900, 560, lt, 2.4, seed=1, n=10)
            bg.smoke(ctx, 1150, 560, lt + 1.3, 2.0, seed=2, n=10)
            bg.hills(ctx, 3, -300, 2300, 760, 230, "#3a1a12")
            bg.temple(ctx, 1000, 600, 0.9, color="#8a6a5a")
            for i, fxp in enumerate((760, 900, 1050, 1220)):
                bg.fire(ctx, fxp, 600, 1.0 + 0.3 * (i % 2), lt, seed=i)
            fx.particles(ctx, lt, -200, 0, 2200, 1100, n=80, seed=3, kind="embers")
            bg.ground(ctx, -300, 2300, 900, 1300, "#2a120a", pebbles=False)
            for i in range(5):
                draw_char(ctx, 280 + i * 330, 980, 0.9, persian(i),
                          Pose(face=1 if i % 2 else -1, t=lt + i, weapon="torch", shield="none",
                               arm=(40, -160), eyes="angry"))
        overlay.caption(ctx, W, H, "ATİNA · M.Ö. 480", st, 0.3, sl - 0.2, y=230)
        return {"vignette": 0.7, "letterbox": 1.0}

    if shot == "salamis":
        with world(ctx, Cam(960, 560, 1.0)):
            bg.sky(ctx, -200, -300, 2200, 700, "#7fb4dc", "#f2e3c0")
            bg.hills(ctx, 9, -300, 2300, 600, 120, "#8a9a6a")
            bg.sea(ctx, -200, 2200, 600, 1300, lt)
            ram = ease_out(prog(st, 0.6, 2.0))
            bg.trireme(ctx, lerp(200, 640, ram), 860, 1.0, t=lt, emblem="#2a5aa8")
            k = prog(st, 2.0, 3.6)
            ctx.save()
            ctx.translate(1180, 860)
            ctx.rotate(k * 0.35)
            bg.trireme(ctx, 0, 0, 1.0, color="#4a2a3a", sail="#d9c08a", emblem="#7a2a8a", t=lt, face=-1)
            ctx.restore()
            fx.sparks(ctx, 900, 840, st - 2.0, seed=4, size=2.5)
            fx.dust(ctx, 900, 880, st - 2.0, seed=5, n=10, size=2.0, color=(0.9, 0.95, 1.0))
            bg.trireme(ctx, 1700, 760, 0.6, color="#4a2a3a", sail="#d9c08a", emblem="#7a2a8a", t=lt, face=-1)
            bg.trireme(ctx, 260, 740, 0.55, t=lt, emblem="#2a5aa8")
        overlay.caption(ctx, W, H, "SALAMİS · M.Ö. 480", st, 0.3, sl - 0.2, y=230)
        return {"vignette": 0.5, "letterbox": 1.0}

    if shot == "plataea":
        with world(ctx, Cam(960, 600, 1.0)):
            bg.sky(ctx, -200, -300, 2200, 1000, "#8ac8ea", "#f2e3c0")
            bg.sun(ctx, 1500, 200, 50)
            bg.hills(ctx, 14, -300, 2300, 820, 140, "#9fb06a")
            bg.ground(ctx, -300, 2300, 880, 1300, "#c9b07a", seed=2)
            phalanx(ctx, lt, 700 + st * 120, 940, s=0.85, lanes=3, ranks=5, walk=lt * 6, grip="ready",
                    eyes="happy")
            for i in range(12):
                x = 1150 + (i // 3) * 130 + st * 260
                draw_char(ctx, x, 940 - (i % 3) * 25, 0.85, persian(i),
                          Pose(face=1, t=lt + i, walk=lt * 11 + i, run=True, weapon="none",
                               shield="none", eyes="scared", mshape="o", sweat=True))
        overlay.caption(ctx, W, H, "PLATAİA · M.Ö. 479", st, 0.3, sl - 0.2, y=230)
        return {"vignette": 0.45, "letterbox": 1.0}

    # the monument + epitaph
    z = 1.0 + 0.08 * prog(st, 0, sl)
    with world(ctx, Cam(960, 560, z)):
        bg.sky(ctx, -200, -300, 2200, 1300, "#2a1a3a", "#f0904a", "#a84a4a")
        bg.sun(ctx, 1600, 640, 90, "#ffe0a0", "#ff8a4a", 0.5)
        bg.mountains(ctx, 5, -300, 2300, 860, 420, "#4a2a3a", rough=1.2, outline=False)
        bg.ground(ctx, -300, 2300, 860, 1300, "#5a3a2a", pebbles=False)
        rrect(ctx, 420, 400, 1080, 520, 14)
        fill_stroke(ctx, "#b8b0a0", 6)
        rrect(ctx, 380, 880, 1160, 60, 8)
        fill_stroke(ctx, "#a8a090", 5)
        lion(ctx, 960, 400, 1.1)
        lines = ["EY YOLCU, GİT SPARTALILARA SÖYLE:", "ONLARIN YASALARINA BAĞLI KALARAK,",
                 "BURADA YATIYORUZ."]
        e_line = S.tag("epitaph")
        dur = e_line.speech_end - e_line.start
        for i, ln in enumerate(lines):
            t_i = t_e - t_st + dur * (0.0, 0.42, 0.78)[i]
            a = ease_out(prog(st, t_i, t_i + 0.8))
            text(ctx, ln, 960, 560 + i * 90, "Cinzel Black", 40, "#3a3028", alpha=a, outline="#d8d0c0",
                 olw=2)
        a = ease_out(prog(st, t_e - t_st + dur + 0.2, t_e - t_st + dur + 1.0))
        text(ctx, "— SİMONİDES", 1300, 860, "Cinzel", 36, "#4a3a30", alpha=a, align="right")
    return {"vignette": 0.65, "no_subs": lt > t_e}


def aftermath_sfx(S):
    t0 = S.start
    return [(t0 + 0.2, "fire_big", 0.6, 0.0), (t0 + S.t("salamis") + 0.2, "waves", 0.6, 0.0),
            (t0 + S.t("salamis") + 2.0, "ship_crash", 0.9, 0.0), (t0 + S.t("plataea"), "crowd_cheer", 0.5, -0.3),
            (t0 + S.t("plataea") + 0.2, "run_many", 0.4, 0.4), (t0 + S.t("stone"), "wind", 0.4, 0.0),
            (t0 + S.t("epitaph"), "stone_carve", 0.35, 0.0)]


# ======================================================================= OUTRO
def outro(ctx, S, lt):
    t_q, t_s, t_b, t_l = S.t("q"), S.t("sub"), S.t("bye"), S.t("logo")
    bg.sky(ctx, 0, 0, W, H, "#1a0e0a", "#8a3a1a", "#4a1a0e")
    bg.sun(ctx, W / 2, 900, 220, "#ffcf7a", "#ff6a2a", 0.4)
    fx.particles(ctx, lt, 0, 0, W, H, n=50, seed=4, kind="embers", alpha=0.6)
    if lt < t_b:
        # helmet + spear in the ground
        limb(ctx, [(1500, 1000), (1560, 380)], "#5a3a1a", 12, 4)
        poly(ctx, [(1556, 380), (1580, 320), (1570, 384)])
        fill_stroke(ctx, "#d8a640", 4)
        ctx.save()
        ctx.translate(1420, 1000)
        ctx.scale(2.0, 2.0)
        ctx.rotate(-0.15)
        ctx.translate(0, 112)
        from draw.characters import _spartan_helmet
        _spartan_helmet(ctx, spartan(1), Pose(t=lt))
        ctx.restore()
        a = ease_out(prog(lt, t_q, t_q + 0.6))
        text(ctx, "SEN OLSAYDIN", 680, 260, "Cinzel Black", 90, "#f6e3b4", outline="#2a0c06", olw=8,
             alpha=a, shadow=(4, 6))
        text(ctx, "NE YAPARDIN?", 680, 370, "Cinzel Black", 90, "#e8b04a", outline="#2a0c06", olw=8,
             alpha=a, shadow=(4, 6))
        for i, (lbl, col) in enumerate((("KALIRDIM", "#2a8a4a"), ("DÖNERDİM", "#b81e28"))):
            k = ease_back(prog(lt, t_q + 1.6 + i * 0.5, t_q + 2.0 + i * 0.5))
            if k > 0:
                ctx.save()
                ctx.translate(480 + i * 400, 520)
                ctx.scale(k, k)
                rrect(ctx, -170, -50, 340, 100, 50)
                fill_stroke(ctx, col, 6)
                text(ctx, lbl, 0, 18, "Baloo 2 ExtraBold", 50, "#ffffff")
                ctx.restore()
        # subscribe button
        if lt > t_s:
            k = ease_back(prog(lt, t_s, t_s + 0.4))
            clicked = lt > t_s + 1.8
            ctx.save()
            ctx.translate(680, 760)
            ctx.scale(k * (0.92 if t_s + 1.7 < lt < t_s + 1.9 else 1.0), k)
            rrect(ctx, -240, -60, 480, 120, 60)
            fill_stroke(ctx, "#cc1f1f" if not clicked else "#5a5a5a", 6)
            text(ctx, "ABONE OL" if not clicked else "ABONE OLUNDU", 0, 20, "Baloo 2 ExtraBold",
                 54 if not clicked else 46, "#ffffff")
            ctx.restore()
            if clicked:
                ring = math.sin((lt - t_s - 1.9) * 25) * 0.4 * max(0, 1 - (lt - t_s - 1.9) / 1.2)
                ctx.save()
                ctx.translate(1000, 760)
                ctx.rotate(ring)
                ctx.move_to(-40, 30)
                ctx.curve_to(-40, -60, 40, -60, 40, 30)
                ctx.line_to(52, 42)
                ctx.line_to(-52, 42)
                ctx.close_path()
                fill_stroke(ctx, "#ffd34a", 5)
                circle(ctx, 0, 52, 12)
                fill_stroke(ctx, "#ffd34a", 4)
                ctx.restore()
            # cursor
            cx = lerp(1100, 700, ease(prog(lt, t_s + 0.6, t_s + 1.6)))
            cy = lerp(950, 780, ease(prog(lt, t_s + 0.6, t_s + 1.6)))
            if lt < t_s + 3.0:
                poly(ctx, [(cx, cy), (cx, cy + 60), (cx + 16, cy + 46), (cx + 28, cy + 72),
                           (cx + 38, cy + 66), (cx + 26, cy + 42), (cx + 46, cy + 42)])
                fill_stroke(ctx, "#ffffff", 4)
    else:
        k = ease_back(prog(lt, t_b, t_b + 0.8))
        overlay.hourglass(ctx, W / 2, 400, 0.95 * k, lt, alpha=clamp(k))
        a = ease_out(prog(lt, t_b + 0.6, t_b + 1.4))
        overlay.logo_text(ctx, W / 2, 790, 1.0, alpha=a)
    return {"vignette": 0.6}


def outro_sfx(S):
    t0 = S.start
    t_q, t_s, t_b = S.t("q"), S.t("sub"), S.t("bye")
    return [(t0 + t_q + 1.6, "pop", 0.5, -0.3), (t0 + t_q + 2.1, "pop", 0.5, 0.3),
            (t0 + t_s, "pop", 0.6, 0.0), (t0 + t_s + 1.8, "click", 0.8, 0.0),
            (t0 + t_s + 1.9, "bell", 0.7, 0.2), (t0 + t_b, "whoosh", 0.5, 0.0),
            (t0 + t_b + 0.1, "boom", 0.6, 0.0)]
