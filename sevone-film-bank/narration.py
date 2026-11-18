"""Builds the narrator voice track and subtitles for the bank-network film.

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
    (0.7, "Two forty-seven A.M. No engineer is awake."),
    (4.9, "But fourteen AI agents are changing your bank's network."),
    # The new operating model
    (9.6, "Your teams have handed six thousand devices and six thousand links to AI agents."),
    (14.8, "Config backups, bulk changes, firmware, firewalls, even incident response."),
    (19.8, "Twelve hundred changes in one hour. Forty-one reviewed by a human."),
    # The question
    (24.6, "So who is watching the agents?"),
    (28.0, "Machine-speed change needs machine-speed observability."),
    # Title
    (33.0, "IBM SevOne. Observability, for the age of agentic AI."),
    # 01 Observe
    (41.0, "Use case one: observe."),
    (43.0, "SevOne maps layer two and layer three topology down to the port, with primary and backup links shown apart, across IPv4, IPv6 and dual stack."),
    (53.4, "Every configuration change is detected in real time, and tied to the agent that made it."),
    (59.4, "And the data flows to your own BI tools."),
    # 02 Anticipate
    (65.0, "Use case two: anticipate."),
    (67.0, "At one-twelve, a Devin agent changed an SD-WAN policy. Nothing broke."),
    (72.2, "But SevOne sees the Hub North link drifting above baseline, and forecasts a breach at eight-forty, before branches open."),
    (81.6, "And it finds twelve hundred dormant switch ports to reclaim."),
    # 03 Prevent
    (87.0, "Use case three: prevent."),
    (88.8, "A Claude Code agent plans a bulk push to 312 routers."),
    (92.9, "The pre-flight runs a dry run, and checks compliance, firmware lifecycle and vulnerabilities."),
    (98.4, "Bulk changes need approval from a nominated bank official."),
    (102.2, "Approved after the dry run, as a safe, phased rollout."),
    (105.6, "Automation, with a gate."),
    # 04 React
    (108.8, "Use case four: react."),
    (110.6, "A Cursor agent changes QoS on a branch router."),
    (114.0, "The primary link starts flapping. SevOne reports one condition, not fourteen alerts."),
    (119.6, "The backup link is up, so the branch is degraded, not down. The config diff points to the agent."),
    (126.6, "One click rolls back to the known-good config. Resolved in forty-seven seconds."),
    # 05 Control
    (135.0, "Use case five: control."),
    (137.0, "Every agent change, attributed. Golden-config compliance, end-of-support milestones, and the approval log, in one place."),
    (147.0, "Real control. In real time."),
    # Close
    (152.5, "Your AI agents act at machine speed."),
    (155.2, "SevOne observes at machine speed."),
    (159.4, "IBM SevOne. See everything. Control everything."),
]

# Words the model tends to mispronounce → spoken form. Subtitles keep the written form.
SPOKEN = {
    "SevOne": "Sev One", "SD-WAN": "S D WAN", "SNMP": "S N M P", "MPLS": "M P L S",
    "BGP": "B G P", "WAF": "waff", "U.S.": "U S", "A.M.": "A M", "AI": "A I", "QoS": "Q o S", "IPv4": "I P v 4", "IPv6": "I P v 6", "BI": "B I",
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
