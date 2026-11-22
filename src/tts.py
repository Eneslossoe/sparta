# -*- coding: utf-8 -*-
"""Turkish voice-over with Piper TTS (tr_TR-dfki-medium) + per-character voice FX.

Every character uses the same neural voice but is pushed into its own register
with ffmpeg's rubberband (pitch / formant), tempo and room effects, so Leonidas,
Xerxes, the mother, the narrator... all sound different.
"""
import hashlib
import json
import os
import subprocess
import wave

import numpy as np

from config import BUILD, FPS, SR, VOICE_DIR, VOICE_NAME

CACHE = os.path.join(BUILD, "tts")
os.makedirs(CACHE, exist_ok=True)

# pitch in semitones, length = Piper length_scale (>1 slower), formant: keep vocal
# tract (preserved) or move it with pitch (shifted), fx = extra ffmpeg filters
VOICES = {
    "N":   dict(pitch=0.0,  length=1.04, formant="preserved", fx="", gain=1.0),
    "NR":  dict(pitch=0.0,  length=0.93, formant="preserved", fx="", gain=1.0),   # reels narrator
    "LEO": dict(pitch=-3.0, length=1.06, formant="preserved",
                fx="aecho=0.8:0.6:45:0.18,bass=g=3", gain=1.05),
    "XER": dict(pitch=-5.0, length=1.10, formant="preserved",
                fx="aecho=0.8:0.75:70|140:0.28|0.16,bass=g=4", gain=1.05),
    "DIE": dict(pitch=-2.0, length=1.02, formant="preserved", fx="bass=g=2", gain=1.0),
    "SOL": dict(pitch=1.5,  length=0.93, formant="preserved", fx="", gain=1.0),
    "ELD": dict(pitch=-1.5, length=1.12, formant="preserved",
                fx="tremolo=f=6:d=0.12", gain=0.95),
    "TRN": dict(pitch=-2.5, length=0.95, formant="preserved", fx="bass=g=2", gain=1.05),
    "GST": dict(pitch=3.0,  length=0.95, formant="shifted", fx="", gain=1.0),
    "MOM": dict(pitch=4.0,  length=1.10, formant="shifted",
                fx="aecho=0.8:0.5:40:0.12", gain=0.95),
    "SCT": dict(pitch=2.0,  length=0.90, formant="preserved", fx="", gain=1.0),
    "DEM": dict(pitch=-1.0, length=1.03, formant="preserved", fx="", gain=1.0),
    "HER": dict(pitch=1.0,  length=1.00, formant="preserved",
                fx="aecho=0.8:0.6:55:0.2", gain=1.0),
    "EPH": dict(pitch=2.5,  length=1.12, formant="preserved", fx="treble=g=-3", gain=0.9),
    "GRK": dict(pitch=1.0,  length=0.97, formant="preserved", fx="", gain=1.05),
    "SPA": dict(pitch=-0.5, length=1.0, formant="preserved", fx="", gain=1.05),
    "SEN": dict(pitch=-1.5, length=1.05, formant="preserved", fx="", gain=1.0),
}

_voice = None


def _piper():
    global _voice
    if _voice is None:
        from piper import PiperVoice
        _voice = PiperVoice.load(os.path.join(VOICE_DIR, VOICE_NAME + ".onnx"))
    return _voice


def ensure_voice_model():
    path = os.path.join(VOICE_DIR, VOICE_NAME + ".onnx")
    if not os.path.exists(path):
        os.makedirs(VOICE_DIR, exist_ok=True)
        subprocess.run(["python3", "-m", "piper.download_voices", VOICE_NAME,
                        "--download-dir", VOICE_DIR], check=True)
    return path


def _key(spk, say):
    v = VOICES[spk]
    h = hashlib.sha1(json.dumps([spk, say, v], sort_keys=True).encode()).hexdigest()[:16]
    return f"{spk}_{h}"


def _read_f32(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def _trim(x, thr=0.012, pad=0.04):
    a = np.abs(x)
    idx = np.where(a > thr)[0]
    if len(idx) == 0:
        return x
    p = int(pad * SR)
    return x[max(0, idx[0] - p): min(len(x), idx[-1] + p)]


def synth_line(spk, say):
    """Returns (path_to_f32_npy, duration_seconds, envelope_per_frame)."""
    from piper import SynthesisConfig
    key = _key(spk, say)
    npy = os.path.join(CACHE, key + ".npy")
    envp = os.path.join(CACHE, key + ".env.npy")
    if os.path.exists(npy) and os.path.exists(envp):
        x = np.load(npy, mmap_mode="r")
        return npy, len(x) / SR, np.load(envp)

    v = VOICES[spk]
    raw_wav = os.path.join(CACHE, key + ".raw.wav")
    with wave.open(raw_wav, "wb") as wf:
        _piper().synthesize_wav(say, wf, syn_config=SynthesisConfig(
            length_scale=v["length"], noise_scale=0.6, noise_w_scale=0.75))

    filt = [f"rubberband=pitch={2 ** (v['pitch'] / 12):.5f}:formant={v['formant']}"]
    if v["fx"]:
        filt.append(v["fx"])
    filt.append("highpass=f=70")
    fx_wav = os.path.join(CACHE, key + ".fx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw_wav, "-af", ",".join(filt),
                    "-ar", str(SR), "-ac", "1", fx_wav], check=True)
    x = _trim(_read_f32(fx_wav))
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.9 * v["gain"]
    np.save(npy, x.astype(np.float32))
    os.remove(raw_wav)
    os.remove(fx_wav)

    # loudness envelope per video frame -> mouth opening for lip sync
    hop = SR // FPS
    n = int(np.ceil(len(x) / hop))
    env = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)])
    env = np.clip(env / (np.percentile(env, 95) + 1e-9), 0, 1.2)
    np.save(envp, env.astype(np.float32))
    return npy, len(x) / SR, env
