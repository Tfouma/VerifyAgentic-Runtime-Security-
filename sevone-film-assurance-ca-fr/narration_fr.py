"""French narration with a choice of voice engine.

    python3 narration_fr.py --engine kokoro --voice ff_siwis --model <kokoro dir> --tag femme
    python3 narration_fr.py --engine piper --voice <dir>/fr_FR-upmc-medium.onnx --speaker 1 --tag homme
    cbenv/bin/python narration_fr.py --engine chatterbox --ref <reference.wav> --tag homme   # Chatterbox Multilingual

Writes narration_<tag>.wav (44.1 kHz mono), narration_<tag>.json, subtitles_<tag>.srt/.vtt.
With --inject, also writes the cues into film.html (used for burned-in captions and the web page).

Each line is synthesized at its natural pace. If it runs into the next line, it is time-compressed
with ffmpeg's pitch-preserving atempo filter, up to MAX_TEMPO; beyond that the build fails, so the
timing never drifts silently.
"""
import argparse, json, re, subprocess, tempfile, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
from cues_fr import CUES, SPOKEN, EN_TERMS, EN_SAY  # noqa: E402
EN_RE = re.compile(r'(?<![\w-])(' + '|'.join(re.escape(t) for t in sorted(EN_TERMS, key=len, reverse=True)) + r')(?![\w-])')


def segments(text):
    """Split a French line into (segment, lang) parts; technical terms in EN_TERMS are English."""
    out, pos = [], 0
    for m in EN_RE.finditer(text):
        if m.start() > pos: out.append((text[pos:m.start()], 'fr'))
        out.append((EN_SAY.get(m.group(0), m.group(0)), 'en'))
        pos = m.end()
    if pos < len(text): out.append((text[pos:], 'fr'))
    return [(t, l) for t, l in out if t.strip()]

SR = 44100
DUR = float(json.loads((HERE / 'timeline.json').read_text())['duration'])
GAP = 0.25
MAX_TEMPO = 1.22


def spoken(text):
    for k, v in sorted(SPOKEN.items(), key=lambda kv: -len(kv[0])):
        text = re.sub(r"(?<![\w-])" + re.escape(k) + r"(?![\w-])", v, text)
    return text


def resample(x, sr_in):
    if sr_in == SR: return x
    n = int(len(x) * SR / sr_in)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)


def trim(x, thr=0.004):
    idx = np.where(np.abs(x) > thr)[0]
    return x[max(0, idx[0] - 200): idx[-1] + 2000] if len(idx) else x


def atempo(x, factor):
    with tempfile.TemporaryDirectory() as d:
        a, b = Path(d) / 'a.wav', Path(d) / 'b.wav'
        with wave.open(str(a), 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(a), '-filter:a', f'atempo={factor:.4f}', str(b)], check=True)
        with wave.open(str(b), 'rb') as w:
            return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16) / 32767.0


def ts(t, sep):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d}{sep}{int(round((s % 1) * 1000)):03d}"


def make_engine(a):
    if a.engine == 'kokoro':
        from kokoro_onnx import Kokoro
        k = Kokoro(str(Path(a.model) / 'model.onnx'), str(Path(a.model) / 'voices.npz'))
        def synth(t):
            ph = ' '.join(k.tokenizer.phonemize(seg.strip(), 'en-us' if l == 'en' else 'fr-fr') for seg, l in segments(t))
            audio, sr = k.create(ph, voice=a.voice, speed=a.speed, lang='fr-fr', is_phonemes=True)
            return np.asarray(audio, dtype=np.float64), sr
        return synth
    if a.engine == 'piper':
        from piper import PiperVoice
        from piper.config import SynthesisConfig
        v = PiperVoice.load(a.voice)
        cfg = SynthesisConfig(speaker_id=a.speaker, length_scale=1.0 / a.speed, noise_scale=0.6, noise_w_scale=0.75)
        from piper.phonemize_espeak import EspeakPhonemizer
        esp = EspeakPhonemizer()
        def synth(t):
            ph = []
            for seg, l in segments(t):
                for sent in esp.phonemize('en-us' if l == 'en' else 'fr', seg.strip()):
                    ph += sent + [' ']
            x = v.phoneme_ids_to_audio(v.phonemes_to_ids(ph[:-1]), cfg)
            return np.asarray(x, dtype=np.float64), v.config.sample_rate
        return synth
    if a.engine == 'chatterbox':
        import torch
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        torch.manual_seed(7)
        m = ChatterboxMultilingualTTS.from_pretrained(device='cpu')
        def synth(t):
            wav = m.generate(t, language_id='fr', audio_prompt_path=a.ref, exaggeration=a.exaggeration, cfg_weight=a.cfg)
            return wav.squeeze().cpu().numpy().astype(np.float64), m.sr
        return synth
    raise SystemExit('unknown engine')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--engine', required=True, choices=['kokoro', 'piper', 'chatterbox'])
    ap.add_argument('--voice'); ap.add_argument('--model'); ap.add_argument('--speaker', type=int)
    ap.add_argument('--ref'); ap.add_argument('--exaggeration', type=float, default=0.5); ap.add_argument('--cfg', type=float, default=0.5)
    ap.add_argument('--speed', type=float, default=1.0)
    ap.add_argument('--tag', required=True); ap.add_argument('--inject', action='store_true')
    ap.add_argument('--only', type=int, default=0, help='synthesize only the first N cues (for samples)')
    a = ap.parse_args()
    synth = make_engine(a)
    cues = sorted(CUES, key=lambda c: c[0])
    if a.only: cues = cues[:a.only]
    track = np.zeros(int(DUR * SR)); out, problems = [], []
    for i, (start, text) in enumerate(cues):
        limit = (cues[i + 1][0] - GAP) if i + 1 < len(cues) else DUR - 1.5
        x, sr = synth(spoken(text) if a.engine == 'chatterbox' else text)
        x = trim(resample(x, sr))
        x = x / (np.abs(x).max() + 1e-9) * 0.9
        room = limit - start; length = len(x) / SR; tempo = 1.0
        if length > room:
            tempo = length / room
            if tempo > MAX_TEMPO:
                problems.append(f'cue {i} at {start}s needs tempo {tempo:.2f}: {text!r}')
            x = atempo(x, min(tempo, 2.0))
        end = start + len(x) / SR
        a0 = int(start * SR); track[a0:a0 + len(x)] += x[: len(track) - a0]
        out.append({'start': round(start, 2), 'end': round(end, 2), 'text': text})
        print(f'{start:6.1f}–{end:6.1f}  x{tempo:.2f}  {text}', flush=True)
    if problems:
        raise SystemExit('\n'.join(problems))
    track = track / (np.abs(track).max() + 1e-9) * 0.89
    with wave.open(str(HERE / f'narration_{a.tag}.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((track * 32767).astype(np.int16).tobytes())
    (HERE / f'narration_{a.tag}.json').write_text(json.dumps(out, indent=1, ensure_ascii=False))
    (HERE / f'subtitles_{a.tag}.srt').write_text('\n'.join(f"{i + 1}\n{ts(c['start'], ',')} --> {ts(c['end'] + .3, ',')}\n{c['text']}\n" for i, c in enumerate(out)))
    (HERE / f'subtitles_{a.tag}.vtt').write_text('WEBVTT\n\n' + '\n'.join(f"{ts(c['start'], '.')} --> {ts(c['end'] + .3, '.')}\n{c['text']}\n" for c in out))
    if a.inject:
        html = (HERE / 'film.html').read_text()
        js = '/*NARRATION*/' + json.dumps([[c['start'], c['end'], c['text']] for c in out], ensure_ascii=False) + '/*END_NARRATION*/'
        html, n = re.subn(r'/\*NARRATION\*/.*?/\*END_NARRATION\*/', lambda m: js, html, flags=re.S)
        assert n == 1
        (HERE / 'film.html').write_text(html)
    print(f'wrote narration_{a.tag}.wav ({len(out)} cues, {a.engine})')


if __name__ == '__main__':
    main()
