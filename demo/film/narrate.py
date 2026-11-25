#!/usr/bin/env python3
"""Narration for the demo films, spoken by an open-weight text-to-speech model, locally.

    synth LINES.json OUT_DIR              writes OUT_DIR/<id>.wav per line and OUT_DIR/durations.json
    mix CUES.json OUT_DIR SECONDS OUT.wav places each line at its cue time on one track

The film scripts call both steps when FILM_VOICE is set. The model runs on this
machine, so the narration text never leaves it.

Two engines, chosen with FILM_TTS:

  pocket   Kyutai's Pocket TTS (recommended): natural, human-sounding voices on a CPU.
           `pip install pocket-tts soundfile`. FILM_TTS_LANGUAGE picks the model
           (english, or french_24l for French) and FILM_VOICE a voice from its catalog,
           for example alba (English) or estelle (French). The weights and voices
           download from Hugging Face on first use. Voice licenses:
           https://huggingface.co/kyutai/tts-voices
  kokoro   The Kokoro model (the default, for the older films): `pip install kokoro-onnx
           soundfile` and the two model files from
           https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
           (kokoro-v1.0.onnx and voices-v1.0.bin), passed as KOKORO_MODEL and
           KOKORO_VOICES. FILM_VOICE picks the voice (for example af_heart) and
           FILM_VOICE_SPEED the pace.

FILM_TTS_CACHE names a folder that keeps every take, so a re-render only speaks the
lines whose text changed. FILM_TTS_MAX_PAUSE (seconds, for example 0.5) shortens long
silences inside a line, for narrators who pause like an audiobook.
"""
import hashlib
import json
import os
import sys
import zlib

import numpy as np
import soundfile as sf

RATE = 24000  # both engines speak at 24 kHz

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


def cap_pauses(samples, longest, threshold_db=-42.0, win=0.02, fade=0.01):
    """Shortens every pause inside a line to at most `longest` seconds.

    Some narrators leave audiobook-length silences between sentences. Cutting the middle
    out of those silences keeps the voice untouched and the pace brisker.
    """
    n = int(win * RATE)
    frames = len(samples) // n
    if frames == 0:
        return samples
    rms = np.sqrt((samples[: frames * n].reshape(frames, n) ** 2).mean(axis=1))
    silent = 20 * np.log10(rms + 1e-9) < threshold_db
    keep_frames = max(1, int(longest / win))
    pieces, start, i = [], 0, 0
    while i < frames:
        if not silent[i]:
            i += 1
            continue
        j = i
        while j < frames and silent[j]:
            j += 1
        if j - i > keep_frames and i > 0 and j < frames:  # only pauses between words
            half = keep_frames // 2
            cut_from, cut_to = (i + half) * n, (j - (keep_frames - half)) * n
            pieces.append(samples[start:cut_from])
            start = cut_to
        i = j
    pieces.append(samples[start:])
    out = pieces[0]
    f = int(fade * RATE)
    for piece in pieces[1:]:  # a short crossfade at each cut, so no click
        if len(out) > f and len(piece) > f:
            ramp = np.linspace(0, 1, f, dtype=np.float32)
            out = np.concatenate([out[:-f], out[-f:] * (1 - ramp) + piece[:f] * ramp, piece[f:]])
        else:
            out = np.concatenate([out, piece])
    return out


def kokoro_engine():
    from kokoro_onnx import Kokoro

    kokoro = Kokoro(os.environ["KOKORO_MODEL"], os.environ["KOKORO_VOICES"])
    voice = os.environ.get("FILM_VOICE", "af_heart")
    speed = float(os.environ.get("FILM_VOICE_SPEED", "1.0"))
    lang = os.environ.get("FILM_VOICE_LANG") or LANGS.get(voice[:1], "en-us")

    def speak(key, text, attempt):
        samples, rate = kokoro.create(text, voice=voice, speed=speed, lang=lang)
        return np.asarray(samples, dtype=np.float32), rate

    return speak, False


def pocket_engine():
    import torch
    from pocket_tts import TTSModel

    torch.set_num_threads(int(os.environ.get("FILM_TTS_THREADS") or os.cpu_count() or 4))
    model = TTSModel.load_model(language=os.environ.get("FILM_TTS_LANGUAGE", "english"))
    voice = model.get_state_for_audio_prompt(os.environ.get("FILM_VOICE", "alba"))

    def speak(key, text, attempt):
        # The model samples, so each line gets its own fixed seed: the same script
        # gives the same takes, and a retake (attempt 1, 2) gets a fresh one.
        torch.manual_seed(zlib.crc32(f"{key}/{attempt}".encode()))
        audio = model.generate_audio(voice, text, copy_state=True)
        return audio.numpy().reshape(-1).astype(np.float32), model.sample_rate

    return speak, True


def plausible(seconds, text):
    """A take far longer or shorter than the text needs is a bad take (a stall or a cut)."""
    per_char = seconds / max(1, len(text))
    return 0.03 <= per_char <= 0.12


def synth(lines_path, out_dir):
    engine = os.environ.get("FILM_TTS", "kokoro").strip().lower()
    make_engine = {"kokoro": kokoro_engine, "pocket": pocket_engine}[engine]
    loaded = []  # the model loads only if a line is not in the cache
    # FILM_TTS_CACHE keeps each take, keyed by engine, model, voice, line id and text,
    # so a re-render only speaks the lines that changed.
    cache = os.environ.get("FILM_TTS_CACHE")
    setting = "|".join([engine, os.environ.get("FILM_TTS_LANGUAGE", ""), os.environ.get("FILM_VOICE", ""),
                        os.environ.get("FILM_VOICE_SPEED", ""), os.environ.get("FILM_VOICE_LANG", "")])
    if cache:
        os.makedirs(cache, exist_ok=True)
    with open(lines_path) as f:
        lines = json.load(f)
    max_pause = float(os.environ.get("FILM_TTS_MAX_PAUSE") or 0)
    durations = {}
    for key, text in lines.items():
        cached = cache and os.path.join(cache, hashlib.sha1(f"{setting}|{key}|{text}".encode()).hexdigest() + ".wav")
        if cached and os.path.exists(cached):
            samples, _ = sf.read(cached, dtype="float32")
        else:
            if not loaded:
                loaded.append(make_engine())
            speak, retake = loaded[0]
            for attempt in range(3 if retake else 1):
                samples, rate = speak(key, text, attempt)
                if rate != RATE:
                    raise ValueError(f"unexpected sample rate {rate}")
                samples = trim(samples)
                if plausible(len(samples) / RATE, text):
                    break
                print(f"  {key}: implausible take ({len(samples) / RATE:.1f}s), retaking", file=sys.stderr)
            if cached:
                sf.write(cached, samples, RATE)
        if max_pause:
            samples = cap_pauses(samples, max_pause)
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
