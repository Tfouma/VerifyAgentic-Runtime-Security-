"""Builds the narrator voice track and subtitles for the Part 2 incident-to-resolution film.

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
    (0.7, "Ten fourteen, Tuesday morning. Branch services are slowing down."),
    (5.2, "And nobody has opened a ticket yet."),
    # End-to-end flow
    (9.6, "Part two: from the first symptom to a closed ticket, end to end."),
    (14.4, "Detect, enrich, ticket, notify. Levels one and two are automated."),
    (19.4, "Level three keeps a human in the loop."),
    # The question
    (24.6, "So who owns this incident?"),
    (27.6, "Machines handle levels one and two. People decide at level three."),
    # Title
    (33.0, "IBM SevOne. From incident, to resolution."),
    # 01 Detect & enrich
    (41.0, "Step one: detect and enrich."),
    (43.2, "A failing optic triggers twenty-three alerts. SevOne correlates them into one incident."),
    (49.6, "ITAM and the CMDB add the asset, the owner group, and the business service."),
    (55.4, "Card payments. Tier one. Under support contract, with the last change on record."),
    # 02 Ticket
    (65.0, "Step two: the ticket."),
    (67.0, "SevOne opens a ServiceNow incident in six seconds."),
    (71.0, "Configuration item, priority, assignment group, and evidence, filled in automatically."),
    (77.4, "One ticket, not twenty-three, and it stays in sync both ways."),
    # 03 Notify
    (87.0, "Step three: notify and route."),
    (89.0, "NetOps South is paged in Teams. DevSecOps gets the agent change in Slack."),
    (95.4, "The service owner is told what to expect."),
    (98.6, "The policy is clear: levels one and two run automatically."),
    (102.6, "Level three needs a human."),
    # 04 L1 + L2
    (108.8, "Step four: levels one and two."),
    (110.8, "Level one triages, and fails traffic over to the backup path."),
    (115.2, "Service is restored in forty-seven seconds. Nobody was paged to fix it."),
    (120.6, "Level two finds the failing optic, opens the vendor case, and reserves a spare from ITAM."),
    (127.4, "The hardware swap is a risky change. It escalates to level three."),
    # 05 L3
    (135.0, "Step five: the human in the loop."),
    (137.0, "A level three engineer reviews the evidence, and approves the change."),
    (142.0, "After the swap, SevOne verifies zero loss, and the incident closes itself, with ITAM updated."),
    # Close
    (152.5, "Machines handle levels one and two."),
    (155.2, "People decide at level three."),
    (159.4, "IBM SevOne. From incident, to resolution."),
]

# Words the model tends to mispronounce → spoken form. Subtitles keep the written form.
SPOKEN = {
    "SevOne": "Sev One", "SD-WAN": "S D WAN", "SNMP": "S N M P", "MPLS": "M P L S",
    "BGP": "B G P", "WAF": "waff", "U.S.": "U S", "A.M.": "A M", "AI": "A I", "QoS": "Q o S", "IPv4": "I P v 4", "IPv6": "I P v 6", "BI": "B I", "ITAM": "eye tam", "CMDB": "C M D B", "NetOps": "net ops", "DevSecOps": "dev sec ops",
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
