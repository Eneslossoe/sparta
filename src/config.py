"""Global settings for the "300 Spartalıdan Biri Olsaydın?" video build."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")          # intermediate files (gitignored)
OUT = os.path.join(ROOT, "output")           # final deliverables
FONTS = os.path.join(ROOT, "assets", "fonts")
VOICE_DIR = os.environ.get("PIPER_VOICE_DIR", os.path.join(BUILD, "voices"))
VOICE_NAME = "tr_TR-dfki-medium"

W, H = 1920, 1080
FPS = 30
SR = 44100                                   # audio sample rate of the final mix

FONT_TITLE = "Cinzel"          # Roman capitals, like the channel banner
FONT_CARTOON = "Baloo 2"       # labels / name tags
FONT_SUB = "Nunito"            # subtitles

for d in (BUILD, OUT):
    os.makedirs(d, exist_ok=True)
