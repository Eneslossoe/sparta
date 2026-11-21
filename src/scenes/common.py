# -*- coding: utf-8 -*-
"""Shared scene helpers: camera, standard sets, phalanx & wave battle system."""
import math
from contextlib import contextmanager
from dataclasses import dataclass, replace

from draw import backgrounds as bg
from draw import fx
from draw.characters import (Look, Pose, draw_char, draw_tag, greek, immortal, leonidas, mede,
                             persian, spartan, xerxes)
from draw.core import (Cam, PI, cam_lerp, clamp, ease, ease_out, hx, lerp, mix, noise1, prog,
                       rng, shade, src)

W, H = 1920, 1080


class G:
    """Per-frame globals filled by the renderer."""
    t = 0.0
    frame = 0
    spk = None
    mouth = 0.0


def talk(spk):
    return G.mouth if G.spk == spk else 0.0


@contextmanager
def world(ctx, cam, shake=0.0, t=0.0):
    ctx.save()
    cam.apply(ctx, W, H, shake, t)
    try:
        yield
    finally:
        ctx.restore()


def shots(lt, end, marks):
    """marks: list of (start_time, name) sorted. Returns (name, local_time, shot_len)."""
    cur = marks[0]
    nxt = end
    for i, m in enumerate(marks):
        if lt >= m[0]:
            cur = m
            nxt = marks[i + 1][0] if i + 1 < len(marks) else end
    return cur[1], lt - cur[0], nxt - cur[0]


def tag_pop(ctx, x, y, label, lt, t0, t1=999.0, s=1.0):
    if lt < t0 or lt > t1:
        return
    k = ease_out(prog(lt, t0, t0 + 0.3))
    a = clamp((t1 - lt) / 0.3)
    draw_tag(ctx, x, y, label, s=s * (0.6 + 0.4 * k), alpha=k * a)


# ====================================================================== sets
def set_thermopylae(ctx, t, tod="day", x0=-1200, x1=3200, gy=880, wall=None, sea=True,
                    far_shift=0.0):
    pal = {
        "day":   ("#7fc4ec", "#f2e3c0", "#9bb2c8", "#a88a62", "#d7b98a"),
        "dawn":  ("#3c4f86", "#f6b48a", "#7c7aa0", "#8a6a5a", "#c9a07a"),
        "dusk":  ("#2b2a5a", "#f08a4a", "#6a5070", "#7a5040", "#b8885a"),
        "dark":  ("#3a3f4a", "#8a8070", "#5a5a64", "#6a5a4a", "#9a8a6a"),
        "night": ("#0b1430", "#2a3a6a", "#1e2a48", "#2a2a38", "#3a3a48"),
    }[tod]
    top, bot, far, cliff, grd = pal
    bg.sky(ctx, x0, -800, x1, gy + 10, top, bot)
    if tod == "day":
        bg.sun(ctx, 1500 + far_shift * 0.1, 160, 50)
    elif tod in ("dawn", "dusk"):
        bg.sun(ctx, 300 + far_shift * 0.1, gy - 330, 70, "#fff0c0", "#ff9a5a", 0.6)
    elif tod == "night":
        bg.stars(ctx, x0, -800, x1, gy - 300, t)
        bg.moon(ctx, 1500, 150, 46)
    if tod in ("day", "dawn", "dusk"):
        bg.clouds(ctx, t, seed=3, n=5, x0=x0, x1=x1, y0=60, y1=300, speed=6,
                  color="#ffffff" if tod == "day" else "#f8c6a8", alpha=0.85)
    ctx.save()
    ctx.translate(far_shift * 0.3, 0)
    bg.mountains(ctx, 11, x0 - 400, x1 + 400, gy - 120, 420, far, rough=0.7, outline=False,
                 shade_k=-0.1)
    if sea:
        bg.sea(ctx, x0 - 400, 700, gy - 130, gy + 10, t,
               color="#4a9ad0" if tod == "day" else mix("#4a9ad0", top, 0.5),
               deep="#2a6a9a" if tod == "day" else mix("#2a6a9a", top, 0.5))
    ctx.restore()
    ctx.save()
    ctx.translate(far_shift * 0.6, 0)
    bg.mountains(ctx, 5, 600, x1 + 600, gy - 40, 520, cliff, rough=1.3, peaks=4,
                 shade_k=-0.22)
    ctx.restore()
    bg.ground(ctx, x0, x1, gy - 20, gy + 900, grd, seed=8,
              grass=None if tod == "night" else shade(grd, -0.3))
    if wall:
        bg.stone_wall(ctx, wall[0], wall[1], gy - 6, wall[2] if len(wall) > 2 else 110,
                      color="#b9ad96" if tod != "night" else "#5a5a68")


def set_sparta(ctx, t, x0=-800, x1=2800, gy=860, houses=True, tod="day"):
    top, bot = ("#86c9ee", "#f6e8c6") if tod == "day" else ("#f08a4a", "#ffd8a0")
    bg.sky(ctx, x0, -900, x1, gy + 10, top, bot)
    bg.sun(ctx, 1550, 170, 48)
    bg.clouds(ctx, t, seed=5, n=5, x0=x0, x1=x1, y0=60, y1=280, speed=8)
    bg.mountains(ctx, 21, x0 - 300, x1 + 300, gy - 150, 470, "#8f8fb0", rough=1.0, snow="#f4f4fa",
                 peaks=3)   # Taygetos
    bg.hills(ctx, 4, x0 - 300, x1 + 300, gy - 60, 120, "#9fbf6a")
    if houses:
        for i, hx_ in enumerate(range(-200, x1, 520)):
            bg.house(ctx, hx_ + 180, gy - 52, 0.55, roof=["#b9572e", "#a84a2a", "#c2643a"][i % 3])
        for hx_ in range(60, x1, 640):
            bg.cypress(ctx, hx_, gy - 50, 0.7)
    bg.ground(ctx, x0, x1, gy - 30, gy + 800, "#cdb27a", seed=2, grass="#8a9a4a")


def set_persian_camp(ctx, t, x0=-800, x1=2800, gy=860, tod="day"):
    if tod == "night":
        bg.sky(ctx, x0, -900, x1, gy, "#0b1430", "#2a2f5a")
        bg.stars(ctx, x0, -900, x1, gy - 300, t)
        bg.moon(ctx, 400, 160, 40)
    else:
        bg.sky(ctx, x0, -900, x1, gy, "#e8a85a", "#f8e2b0")
        bg.sun(ctx, 300, 220, 60, glow="#ffb060")
    bg.mountains(ctx, 31, x0 - 300, x1 + 300, gy - 100, 360,
                 "#b08a6a" if tod != "night" else "#2a2a40", rough=0.8, outline=False)
    r = rng(5)
    for i in range(14):
        tx = x0 + 100 + i * 230 + r.uniform(-40, 40)
        bg.tent(ctx, tx, gy - 90 - r.uniform(0, 40), 0.5,
                c2=["#a8432e", "#2f5f9a", "#c99a2a"][i % 3], flag="#c8202a", t=t)
    bg.ground(ctx, x0, x1, gy - 30, gy + 800, "#d4b07a" if tod != "night" else "#3a3a4a", seed=6)


# ====================================================================== battle
@dataclass
class Foe:
    lane: int
    ts: float
    x0: float
    sp: float
    tc: float = 0.0      # reaches the shield wall
    tf: float = 0.0      # falls
    look: Look = None
    seed: int = 0


LANE_DY = 30          # each depth lane is drawn this much higher
LANE_DS = 0.07        # ... and this much smaller


def wave_schedule(seed, t0, t1, rate, contact_x, kind="mede", lanes=3, x_start=2250,
                  speed=(300, 380), fight=(0.7, 1.8), survive_after=None):
    r = rng(seed)
    foes = []
    t = t0
    last = {l: -99.0 for l in range(lanes)}
    i = 0
    maker = {"mede": mede, "persian": persian, "immortal": immortal}[kind]
    while t < t1:
        lane = r.randrange(lanes)
        sp = r.uniform(*speed)
        x0 = x_start + r.uniform(0, 260)
        ta = t + (x0 - contact_x) / sp
        tc = max(ta, last[lane] + 0.45)
        tf = tc + r.uniform(*fight)
        last[lane] = tf
        foes.append(Foe(lane, t, x0, sp, tc, tf, maker(seed=r.randrange(9)), seed=seed * 100 + i))
        t += r.expovariate(rate)
        i += 1
    return foes


def foe_x(f, foes, t, contact_x):
    if t >= f.tc:
        return contact_x
    ahead = 0.0
    for g in foes:
        if g is f:
            break
        if g.lane == f.lane and g.tf + 0.7 > t:
            ahead += clamp((g.tf + 0.7 - t) / 0.45)
    return max(contact_x + 72 * ahead, f.x0 - f.sp * (t - f.ts))


def draw_wave(ctx, t, foes, contact_x, gy, s=1.0, lane=None, corpse_life=1.6, face=-1,
              weapon="short_spear"):
    for f in foes:
        if lane is not None and f.lane != lane:
            continue
        if t < f.ts or t > f.tf + 0.45 + corpse_life:
            continue
        x = foe_x(f, foes, t, contact_x) if t < f.tf else contact_x + 30
        ls = s * (1 - f.lane * LANE_DS)
        y = gy - f.lane * LANE_DY
        fighting = f.tc <= t < f.tf
        moving = t < f.tc and x > contact_x + 1 and abs(x - (f.x0 - f.sp * (t - f.ts))) < 2
        fall = ease_out(prog(t, f.tf, f.tf + 0.45))
        alpha = 1 - prog(t, f.tf + 0.45 + corpse_life - 0.4, f.tf + 0.45 + corpse_life)
        ps = Pose(face=face, t=t + f.seed, walk=(t * 11 + f.seed) if moving else None, run=moving,
                  weapon=weapon if f.look.kind != "mede" or f.seed % 3 else "short_spear",
                  grip="ready", thrust=max(0, math.sin(t * 7 + f.seed)) ** 2 if fighting else 0,
                  eyes="dead" if fall > 0.3 else ("angry" if fighting or moving else "normal"),
                  mshape="shout" if moving else ("o" if fall > 0 else "line"),
                  fall=fall, alpha=alpha, shield="front" if fall < 0.5 else "none")
        draw_char(ctx, x, y, ls, f.look, ps)


def spartan_thrust(t, foes, lane):
    v = 0.0
    for f in foes:
        if f.lane == lane:
            d = t - (f.tf - 0.22)
            if -0.25 < d < 0.35:
                v = max(v, math.sin(clamp((d + 0.25) / 0.6) * PI))
    return v


def phalanx(ctx, t, x_front, gy, s=1.0, lanes=3, ranks=4, foes=None, face=1, walk=None,
            shield="front", grip="ready", seed=0, you=None, leo=None, looks=None, eyes="angry",
            run=False, extra=None, spacing=74, alpha=1.0, dead=None, only_lane=None):
    """Draw a block of hoplites. `you`=(lane,rank) gets the SEN look, `leo` the king."""
    out = {}
    for lane in reversed(range(lanes)):
        if only_lane is not None and lane != only_lane:
            continue
        ls = s * (1 - lane * LANE_DS)
        y = gy - lane * LANE_DY
        for rk in reversed(range(ranks)):
            x = x_front - face * (rk * spacing * s + lane * 12 * s)
            idx = seed + lane * 10 + rk
            lk = spartan(idx)
            if looks:
                lk = looks(lane, rk, lk)
            if leo == (lane, rk):
                lk = leonidas()
            if you == (lane, rk):
                lk = spartan(1, spk="SEN")
            th = 0.0
            if foes is not None and rk == 0:
                th = spartan_thrust(t, foes, lane)
            elif rk > 0 and grip == "ready" and walk is None:
                th = 0.15 * max(0, math.sin(t * 2 + idx))
            ps = Pose(face=face, t=t + idx * 0.7, walk=(walk + idx * 0.4) if walk is not None else None,
                      run=run, grip=grip, thrust=th, shield=shield, eyes=eyes, alpha=alpha,
                      mshape="line")
            if extra:
                ps = extra(lane, rk, ps) or ps
            if dead and (lane, rk) in dead:
                continue
            draw_char(ctx, x, y, ls, lk, ps)
            out[(lane, rk)] = (x, y, ls)
    return out


def clash_events(foes, t_off, contact_x, pan_center=960, gain=1.0):
    """Sound events (time, name, gain, pan) for a wave."""
    ev = []
    for f in foes:
        pan = clamp((contact_x - pan_center) / 1200, -0.8, 0.8)
        ev.append((t_off + f.tc, "shield_bash", 0.55 * gain * (1 - f.lane * 0.2), pan))
        ev.append((t_off + f.tf - 0.05, "stab", 0.6 * gain * (1 - f.lane * 0.2), pan))
        if f.seed % 3 == 0:
            ev.append((t_off + f.tf, "grunt", 0.35 * gain, pan))
        if f.seed % 2 == 0:
            ev.append((t_off + f.tf - 0.1, "clang", 0.45 * gain, pan))
    return ev


def battle(ctx, t, foes, x_front, gy, s=1.0, lanes=3, ranks=4, contact=None, foe_kw=None,
           **kw):
    """Phalanx vs wave, interleaved lane by lane for correct depth."""
    contact = x_front + 145 * s if contact is None else contact
    for lane in reversed(range(lanes)):
        phalanx(ctx, t, x_front, gy, s=s, lanes=lanes, ranks=ranks, foes=foes, only_lane=lane, **kw)
        draw_wave(ctx, t, foes, contact, gy, s=s, lane=lane, **(foe_kw or {}))


def fight_cloud(ctx, x, y, t, s=1.0, seed=0, alpha=1.0):
    """Cartoon brawl cloud with fists, feet and stars popping out."""
    from draw.core import circle, fill_stroke, rng as _r, src as _src, poly
    from draw.characters import draw_spear
    r = _r(seed)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for k in range(5):
        a = t * 9 + k * 1.3
        L = 120 + 40 * math.sin(t * 13 + k)
        ex, ey = math.cos(a) * L, math.sin(a) * L * 0.6
        if k % 2 == 0:
            draw_spear(ctx, ex * 0.4, ey * 0.4, a, 160, 0.5, broken=True)
        else:
            circle(ctx, ex, ey, 18)
            fill_stroke(ctx, "#f1c29a", 4)
    for i in range(14):
        a = i * 0.45 + noise1(t * 3 + i, seed) * 0.3
        rr = 90 + 25 * noise1(t * 6 + i, seed + 1)
        circle(ctx, math.cos(a) * rr, math.sin(a) * rr * 0.65, 70 + 12 * noise1(t * 5 + i, seed + 2))
        ctx.new_sub_path()
    _src(ctx, (0.1, 0.08, 0.07, alpha))
    ctx.set_line_width(10)
    ctx.stroke_preserve()
    _src(ctx, (0.86, 0.8, 0.68, alpha))
    ctx.fill()
    for i in range(4):
        ph = (t * 2.2 + i * 0.25) % 1.0
        a = i * 1.7 + seed
        px, py = math.cos(a) * (60 + ph * 150), math.sin(a) * (40 + ph * 110) - ph * 40
        pts = []
        for j in range(10):
            aa = j * math.pi / 5
            rr = (26 if j % 2 == 0 else 11) * (1 - ph * 0.5)
            pts.append((px + math.cos(aa) * rr, py + math.sin(aa) * rr))
        poly(ctx, pts)
        fill_stroke(ctx, "#ffe14a", 3, alpha=(1 - ph) * alpha)
    ctx.restore()
