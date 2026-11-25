"""Builds the narrator voice track and subtitles for the agentic assurance film.

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
DUR = 560.0
SPEED = 1.0
SPEED_MAX = 1.12
GAP = 0.25  # minimum silence between cues (s)

# (start in seconds, text). Scene boundaries come from timeline.json.
CUES = [
    # Cold open
    (0.8, "Nine twenty, Monday morning."),
    (3.4, "AI accelerates operations. It also accelerates change."),
    (8.0, "And change now happens at machine speed."),
    # Critical infrastructure
    (13.0, "Banks, telecom operators, railways, energy utilities, governments and AI platforms all run on the network."),
    (20.4, "On premises and in the cloud, across WAN, SD-WAN and data centers."),
    (26.0, "AI agents now help engineers troubleshoot, generate configurations and execute changes across that infrastructure."),
    (33.8, "That creates enormous opportunity, and a new operational risk."),
    # Agentic operations
    (41.0, "Consider a routine optimization."),
    (43.2, "An engineer asks an AI agent to improve connectivity between Montreal and Toronto, without hurting application performance."),
    (51.6, "The agent analyzes telemetry, and proposes a BGP preference change on forty-eight edge routers."),
    (58.4, "Following change policy, the change is approved, and executed through the automation platform."),
    (65.2, "Human and policy, then agent, then approved automation. Exactly as it should be."),
    # The change
    (73.0, "Forty-eight devices are updated."),
    (76.0, "No configuration errors. No devices down. BGP sessions remain established."),
    (82.2, "The automation platform reports success."),
    (95.8, "But did the business outcome succeed?"),
    # Detect
    (101.4, "Independent network telemetry tells a different story."),
    (105.0, "Traffic has shifted onto a more constrained path."),
    (110.6, "WAN utilization climbs from forty-seven to eighty-two percent. Latency, from eighteen to sixty-three milliseconds. Packet loss reaches two percent."),
    (120.6, "Yet BGP is still established, and every device is still up."),
    (125.4, "SevOne compares live behavior with each path's learned baseline, and flags the deviation within minutes."),
    (133.4, "This is the critical distinction. Technical success does not guarantee business success."),
    # Before it becomes an incident
    (146.0, "This is where observability changes the risk equation."),
    (150.0, "Baselines, flow records and streaming telemetry show the degradation while services are still up."),
    (157.6, "SevOne raises the condition at nine twenty-four, before packet loss spreads, and before any customer calls."),
    (165.6, "Don't wait for down. Detect degradation while services are still up."),
    # Six industries
    (176.0, "For a bank, the same deviation becomes transaction latency, and operational-resilience exposure."),
    (185.6, "For a telecom operator, it means SLA penalties, and avoidable NOC escalations."),
    (195.2, "For rail, communications visibility keeps degradation from cascading into operational disruption."),
    (204.8, "For energy, visibility across operational communications stays separate from safety and control systems."),
    (214.4, "For government and critical services, it is evidence for availability and accountability."),
    (224.0, "And for AI platforms, congested data paths leave expensive GPUs waiting. AI infrastructure is network infrastructure."),
    # Root cause
    (236.0, "Next question: what exactly happened, and where?"),
    (239.8, "SevOne moves from the symptom, to the scope, to the path, to the flows, and back to the change that caused it."),
    (247.8, "Latency on the payments path. Three WAN circuits at the Toronto edge. The BGP best path moved to a one-gigabit circuit."),
    (257.0, "Replication and payment flows now share it. The trigger: the nine twenty-one policy change."),
    (264.4, "What changed, where, what is abnormal, what could be affected, and how urgent. Answered with evidence, not opinion."),
    # Respond
    (281.0, "Detection alone doesn't reduce risk. The insight has to enter your existing processes."),
    (287.6, "SevOne raises the event. A ServiceNow incident opens automatically, with the configuration item, the priority and the evidence."),
    (296.4, "NetOps is paged. DevSecOps is informed of the AI-initiated change."),
    (301.8, "Levels one and two are automated: triage, correlation, and a rollback proposal."),
    (307.8, "Level three is human. An engineer approves the rollback."),
    (312.2, "The automation platform executes it. SevOne remains the independent observer."),
    # Verify
    (326.0, "And remediation isn't complete because a job reports success. The network is measured again."),
    (333.4, "Utilization returns to forty-nine percent. Latency to nineteen milliseconds. Packet loss disappears."),
    (340.8, "Only then does the ticket close. Observe, detect, understand, act, and verify."),
    # Risk controls
    (356.0, "This is how network evidence supports enterprise risk controls."),
    (359.8, "Preventive controls govern what can change. Detective controls surface abnormal behavior."),
    (366.0, "Diagnostic evidence explains it. Corrective workflows respond. Verification confirms recovery."),
    (372.6, "And the history becomes evidence for audit, regulators, and due diligence."),
    (378.4, "SevOne is an important source of that evidence, alongside change, ITSM and security records."),
    (385.6, "It doesn't replace those controls. It makes them measurable."),
    # Executive dashboard
    (396.0, "Executives get one view of network operational risk."),
    (399.6, "KPIs are set per service class: availability, performance, capacity, stability, change and coverage."),
    (407.2, "And one new metric for the agentic era: the change outcome assurance rate."),
    (412.6, "The share of changes whose network outcome was actually verified."),
    # TCO / OPEX
    (426.0, "The business case goes beyond avoided outages."),
    (429.6, "Consolidated tools, automated baselines, automatic tickets and CMDB sync reduce the effort behind every incident."),
    (437.8, "But don't estimate savings from marketing assumptions."),
    (441.6, "Baseline today's tooling, administration, incident, reporting and onboarding costs."),
    (448.6, "Run a proof of value, measure the delta, and build the business case from evidence."),
    (455.6, "That is how you prove lower TCO and OPEX."),
    # Three truths
    (471.0, "The AI agent tells you the task was completed."),
    (474.8, "The automation platform tells you the change was applied."),
    (478.8, "SevOne tells you what happened to the network."),
    (482.6, "The business needs all three. Only independent observability verifies the outcome."),
    # The question
    (493.4, "If an AI agent changed five hundred network devices tonight, how quickly could you determine whether every change produced the intended business outcome?"),
    # Assessment
    (513.4, "Start with an Agentic Network Readiness and Observability Assessment."),
    (518.6, "Visibility, AI use cases, critical dependencies, telemetry coverage, and BGP and WAN visibility."),
    (527.4, "Baselines, change-impact validation, incident workflows, observability gaps, and closed-loop assurance."),
    # Closing
    (541.0, "In the age of agentic AI, autonomy without observability is risk."),
    (545.8, "The future isn't just autonomous networking."),
    (548.8, "It's autonomous networking, with continuous assurance."),
    (553.8, "IBM SevOne."),
]

# Words the model tends to mispronounce → spoken form. Subtitles keep the written form.
SPOKEN = {
    "SevOne": "Sev One", "SD-WAN": "S D WAN", "SNMP": "S N M P", "MPLS": "M P L S",
    "BGP": "B G P", "WAF": "waff", "U.S.": "U S", "A.M.": "A M", "AI": "A I", "QoS": "Q o S", "IPv4": "I P v 4", "IPv6": "I P v 6", "BI": "B I", "NOC": "knock", "TCO": "T C O", "OPEX": "op ex", "GPUs": "G P Us", "ITSM": "I T S M", "SLA": "S L A", "ITAM": "eye tam", "CMDB": "C M D B", "NetOps": "net ops", "DevSecOps": "dev sec ops",
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
