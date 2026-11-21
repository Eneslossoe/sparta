# -*- coding: utf-8 -*-
"""Build the whole video: voice -> timeline -> audio -> frames -> mp4 (+ srt, thumbnail).

    python3 build.py              # full build
    python3 build.py --audio      # soundtrack only
    python3 build.py --video      # frames only (reuses soundtrack)
"""
import argparse
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))

from config import BUILD, OUT  # noqa: E402
from tts import ensure_voice_model  # noqa: E402

NAME = "300_Spartalidan_Biri_Olsaydin"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", action="store_true")
    ap.add_argument("--video", action="store_true")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    a = ap.parse_args()
    do_audio = a.audio or not a.video
    do_video = a.video or not a.audio
    t0 = time.time()
    ensure_voice_model()

    from render import Renderer, boundaries, render_video
    from scenes import REGISTRY
    from timeline import CHAPTER_CARD, srt
    R = Renderer()
    print(f"timeline: {len(R.scenes)} scenes, {R.total:.1f}s, {len(R.cues)} subtitle cues")
    wav = os.path.join(BUILD, "soundtrack.wav")
    srt(R.cues, os.path.join(OUT, NAME + ".srt"))
    if do_audio:
        from audio.mix import build_audio
        build_audio(R.scenes, REGISTRY, R.bounds, CHAPTER_CARD, wav)
    if do_video:
        silent = os.path.join(BUILD, "video_silent.mp4")
        render_video(silent, a.workers)
        out = os.path.join(OUT, NAME + ".mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                        "-shortest", out], check=True)
        print("final ->", out)
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
