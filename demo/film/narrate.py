#!/usr/bin/env python3
"""Narration for the demo film, spoken by the open-weight Kokoro text-to-speech model.

    synth LINES.json OUT_DIR              writes OUT_DIR/<id>.wav per line and OUT_DIR/durations.json
    mix CUES.json OUT_DIR SECONDS OUT.wav places each line at its cue time on one track

record_film.js calls both steps when FILM_VOICE is set. Kokoro runs locally, so the
narration text never leaves the machine.

Needs `pip install kokoro-onnx soundfile` and the two model files from
https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
(kokoro-v1.0.onnx and voices-v1.0.bin), passed as KOKORO_MODEL and KOKORO_VOICES.
FILM_VOICE picks the voice (for example af_heart); FILM_VOICE_SPEED sets the pace.
"""
import json
import os
import sys

import numpy as np
import soundfile as sf

RATE = 24000  # Kokoro's output sample rate

# Kokoro voice names start with a language letter: a = American English, b = British
# English, f = French, and so on. FILM_VOICE_LANG overrides the guess.
LANGS = {"a": "en-us", "b": "en-gb", "f": "fr-fr", "e": "es", "i": "it", "p": "pt-br", "h": "hi", "j": "ja", "z": "cmn"}


def trim(samples, threshold=0.004, keep=0.04):
    """Cut leading and trailing silence so each line's length is its spoken length."""
    loud = np.flatnonzero(np.abs(samples) > threshold)
    if loud.size == 0:
        return samples
    pad = int(keep * RATE)
    return samples[max(0, loud[0] - pad): loud[-1] + pad]


def synth(lines_path, out_dir):
    from kokoro_onnx import Kokoro

    kokoro = Kokoro(os.environ["KOKORO_MODEL"], os.environ["KOKORO_VOICES"])
    voice = os.environ.get("FILM_VOICE", "af_heart")
    speed = float(os.environ.get("FILM_VOICE_SPEED", "1.0"))
    lang = os.environ.get("FILM_VOICE_LANG") or LANGS.get(voice[:1], "en-us")
    with open(lines_path) as f:
        lines = json.load(f)
    durations = {}
    for key, text in lines.items():
        samples, rate = kokoro.create(text, voice=voice, speed=speed, lang=lang)
        if rate != RATE:
            raise ValueError(f"unexpected sample rate {rate}")
        samples = trim(np.asarray(samples, dtype=np.float32))
        sf.write(os.path.join(out_dir, f"{key}.wav"), samples, RATE)
        durations[key] = round(len(samples) / RATE, 3)
        print(f"  {key:6} {durations[key]:5.2f}s  {text}", file=sys.stderr)
    with open(os.path.join(out_dir, "durations.json"), "w") as f:
        json.dump(durations, f, indent=1)


def mix(cues_path, out_dir, seconds, out_path):
    track = np.zeros(int(float(seconds) * RATE) + RATE, dtype=np.float32)
    with open(cues_path) as f:
        cues = json.load(f)
    for cue in cues:
        samples, _ = sf.read(os.path.join(out_dir, f"{cue['id']}.wav"), dtype="float32")
        start = int(cue["t"] * RATE)
        end = min(len(track), start + len(samples))
        track[start:end] += samples[: end - start]
    peak = float(np.max(np.abs(track))) or 1.0
    if peak > 0.98:
        track *= 0.98 / peak
    sf.write(out_path, track, RATE)


if __name__ == "__main__":
    command, *args = sys.argv[1:]
    {"synth": synth, "mix": mix}[command](*args)
