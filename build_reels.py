# -*- coding: utf-8 -*-
"""Build the vertical Reels cut (<= 60 s): python3 build_reels.py"""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))

from config import BUILD, OUT  # noqa: E402
from tts import ensure_voice_model  # noqa: E402


def main():
    t0 = time.time()
    ensure_voice_model()
    from audio.mix import build_audio
    from reels.render_reels import ReelRenderer, render_video
    from reels.scenes_reels import REGISTRY
    from timeline import srt
    R = ReelRenderer()
    print(f"reels timeline: {R.total:.1f}s")
    assert R.total <= 60.0, "reels must be max 60 s"
    srt(R.cues, os.path.join(OUT, "Reels_300_Spartali.srt"))
    wav = os.path.join(BUILD, "reels_soundtrack.wav")
    build_audio(R.scenes, REGISTRY, R.bounds, 0.0, wav)
    silent = os.path.join(BUILD, "reels_silent.mp4")
    render_video(silent, os.cpu_count() or 4)
    out = os.path.join(OUT, "Reels_300_Spartali.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out],
                   check=True)
    print("reels ->", out, f"({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
