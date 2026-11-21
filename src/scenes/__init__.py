# -*- coding: utf-8 -*-
"""Scene registry: id -> (draw(ctx, S, lt) -> opts, sfx(S) -> [(t, name, gain, pan)])."""
import importlib

from draw.core import text

REGISTRY = {}


def _placeholder(sid):
    def draw(ctx, S, lt):
        ctx.set_source_rgb(0.15, 0.12, 0.1)
        ctx.paint()
        text(ctx, sid, 960, 540, "Cinzel Black", 80, "#f6e3b4")
    return draw, (lambda S: [])


ORDER = ["cold_open", "title", "birth", "agoge", "mess", "persia", "chosen", "march", "pass",
         "scout", "molon", "day1", "immortals", "betrayal", "morning", "final", "survivor",
         "aftermath", "outro"]

for sid in ORDER:
    REGISTRY[sid] = _placeholder(sid)

for mod in ("s_intro", "s_sparta", "s_persia", "s_battle", "s_end"):
    try:
        m = importlib.import_module(f"scenes.{mod}")
    except ModuleNotFoundError as e:
        if e.name != f"scenes.{mod}":
            raise
        continue
    for sid in ORDER:
        if hasattr(m, sid):
            REGISTRY[sid] = (getattr(m, sid), getattr(m, sid + "_sfx", lambda S: []))
