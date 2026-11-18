"""Builds the narrator voice track and subtitles for the Canada-first film.

Uses Kokoro-82M (Apache-2.0), a neural text-to-speech model that runs locally on CPU.

    python3 narration.py --model <dir with model.onnx and voices.npz> [--voice af_heart]

Writes:
  narration.wav   voice track at 44.1 kHz, placed on the film timeline
  narration.json  [{start, end, text}] cues (soundtrack.py uses these to duck the music)
  subtitles.srt / subtitles.vtt
and injects the cues into film.html between /*NARRATION*/ and /*END_NARRATION*/.

Each cue has a target start time. If a line runs into the next cue, it is re-spoken a
little faster, up to SPEED_MAX. If it still does not fit, the script fails, so the timing
is never silently wrong.
"""
import argparse
import json
import re
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SR = 44100
DUR = 166.0
SPEED = 1.0
SPEED_MAX = 1.12
GAP = 0.25  # minimum silence between cues (s)

# (start in seconds, text). Scene boundaries: 0 · 9 · 24 · 32 · 40 · 64 · 86 · 108 · 134 · 152 · 166
CUES = [
    (0.7, "Two forty-seven A.M., Eastern. No engineer is awake."),
    (4.9, "But fourteen AI agents are changing your network."),
    # The new operating model
    (9.6, "From Vancouver to Toronto to Montreal, your teams have handed the network to AI agents."),
    (15.0, "BGP, SD-WAN, firewalls, patching, even incident response."),
    (19.8, "Twelve hundred changes in one hour. Forty-one reviewed by a human."),
    # The question
    (24.6, "So who is watching the agents?"),
    (27.6, "And is your data still in Canada?"),
    # Title
    (33.0, "IBM SevOne. Sovereign observability, for the age of agentic AI."),
    # 01 Observe
    (41.0, "Use case one: observe, with Canada first."),
    (43.8, "SevOne runs in your Montreal, Toronto and Vancouver data centers. Telemetry and agent audit data stay in Canada."),
    (51.6, "It still sees your U.S. branches, and ties every agent change to its identity, its device, and its effect."),
    # 02 Anticipate
    (65.0, "Use case two: anticipate."),
    (67.0, "At one-twelve, a Devin agent changed an SD-WAN policy. Nothing broke."),
    (72.2, "But SevOne sees the Toronto to Montreal MPLS link drifting above baseline, and "
           "forecasts a breach at eight-forty, before the TSX opens."),
    (81.8, "With the cause, the users at risk, and the fix."),
    # 03 Prevent
    (87.0, "Use case three: prevent."),
    (88.8, "A Claude Code agent plans to upgrade both Toronto core routers."),
    (93.2, "SevOne's pre-flight finds the failover would carry Canadian traffic through Chicago."),
    (98.6, "That breaks sovereignty. The change is held."),
    (101.6, "The agent re-plans, and stays in Canada."),
    (104.6, "Sovereignty becomes a guardrail."),
    # 04 React
    (108.8, "Use case four: react."),
    (110.6, "A Cursor agent pushes a new WAF rule."),
    (114.0, "Checkout latency jumps eleven times. SevOne flags it in eight seconds."),
    (119.0, "It links the anomaly to the change, and the change to the agent, then triggers a "
            "rollback through watsonx Orchestrate."),
    (127.0, "Resolved in forty-seven seconds. The audit trail never leaves Canada."),
    # 05 Control
    (135.0, "Use case five: control."),
    (137.0, "All telemetry, kept in Canada. Every agent change, attributed. And a safe-change "
            "score for every agent, based on what it actually did."),
    (147.0, "Sovereign control. In real time."),
    # Close
    (152.5, "Your AI agents act at machine speed."),
    (155.2, "SevOne observes at machine speed. In Canada."),
    (159.4, "IBM SevOne. Sovereign by design."),
]

# Words the model tends to mispronounce → spoken form. Subtitles keep the written form.
SPOKEN = {
    "SevOne": "Sev One", "SD-WAN": "S D WAN", "SNMP": "S N M P", "MPLS": "M P L S",
    "BGP": "B G P", "WAF": "waff", "U.S.": "U S", "A.M.": "A M", "AI": "A I",
}


def spoken(text):
    for k, v in SPOKEN.items():
        text = re.sub(r"(?<![\w-])" + re.escape(k) + r"(?![\w-])", v, text)
    return text


def resample(x, sr_in):
    n = int(len(x) * SR / sr_in)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)


def trim(x, thr=0.004):
    idx = np.where(np.abs(x) > thr)[0]
    return x[max(0, idx[0] - 200): idx[-1] + 2000] if len(idx) else x


def ts(t, sep):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d}{sep}{int(round((s % 1) * 1000)):03d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--voice", default="af_heart")
    args = ap.parse_args()
    from kokoro_onnx import Kokoro
    k = Kokoro(str(Path(args.model) / "model.onnx"), str(Path(args.model) / "voices.npz"))

    track = np.zeros(int(DUR * SR))
    out, problems = [], []
    for i, (start, text) in enumerate(CUES):
        limit = (CUES[i + 1][0] - GAP) if i + 1 < len(CUES) else DUR - 1.5
        speed = SPEED
        while True:
            audio, sr = k.create(spoken(text), voice=args.voice, speed=speed, lang="en-us")
            audio = trim(resample(np.asarray(audio, dtype=np.float64), sr))
            end = start + len(audio) / SR
            if end <= limit or speed >= SPEED_MAX:
                break
            speed = round(min(SPEED_MAX, speed + 0.04), 2)
        if end > limit + 0.05:
            problems.append(f"cue {i} at {start}s runs {end - limit:.2f}s too long even at speed {speed}: {text!r}")
        a = int(start * SR)
        track[a:a + len(audio)] += audio
        out.append({"start": round(start, 2), "end": round(end, 2), "text": text})
        print(f"{start:6.1f}–{end:6.1f}  x{speed:.2f}  {text}")

    if problems:
        raise SystemExit("\n".join(problems))
    peak = np.abs(track).max()
    track = track / peak * 0.89
    with wave.open(str(HERE / "narration.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((track * 32767).astype(np.int16).tobytes())

    (HERE / "narration.json").write_text(json.dumps(out, indent=1))
    srt = "\n".join(f"{i + 1}\n{ts(c['start'], ',')} --> {ts(c['end'] + .3, ',')}\n{c['text']}\n" for i, c in enumerate(out))
    (HERE / "subtitles.srt").write_text(srt)
    vtt = "WEBVTT\n\n" + "\n".join(f"{ts(c['start'], '.')} --> {ts(c['end'] + .3, '.')}\n{c['text']}\n" for c in out)
    (HERE / "subtitles.vtt").write_text(vtt)

    html = (HERE / "film.html").read_text()
    js = "/*NARRATION*/" + json.dumps([[c["start"], c["end"], c["text"]] for c in out]) + "/*END_NARRATION*/"
    html, n = re.subn(r"/\*NARRATION\*/.*?/\*END_NARRATION\*/", lambda m: js, html, flags=re.S)
    assert n == 1, "narration marker not found in film.html"
    (HERE / "film.html").write_text(html)
    print(f"wrote narration.wav, narration.json, subtitles.srt/.vtt and updated film.html ({len(out)} cues, voice {args.voice})")


if __name__ == "__main__":
    main()
