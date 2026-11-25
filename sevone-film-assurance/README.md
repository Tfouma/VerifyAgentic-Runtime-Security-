# When AI Changes the Network, Who Verifies the Outcome?

A narrated, end-to-end demo film of about 9 minutes, with a production-ready storyboard. It shows
how IBM SevOne provides **continuous, independent network assurance** when AI agents and
automation change enterprise networks. The film covers banking, telecom, rail, energy, government
and critical services, and AI and data infrastructure, both on-prem and in the cloud.

**Single message:** AI agents accelerate change. SevOne provides the independent network
observability needed to understand the impact, detect unintended consequences and verify
operational outcomes.

**Everything in the film is a simulated scenario.** All devices, agents, tickets, KPIs and figures
are demo values, not customer results. The narrator is a synthetic voice (Kokoro-82M, Apache-2.0).

| File | What it is |
|------|------------|
| `sevone-agentic-assurance.mp4` | The film: 9:20, 1920×1080, 30 fps, narration, music and impacts, with an English subtitle track you can switch on |
| `sevone-agentic-assurance-captioned.mp4` | The same film with subtitles burned in |
| `storyboard/storyboard.pdf` | **Production storyboard** for each scene: still frame, visuals, on-screen text, narration and soundtrack cues. Appendices cover industry risk-control matrices, the KPI framework, incident automation, the TCO/OPEX method, the 60-minute run of show and the assessment |
| `storyboard/STORYBOARD.md` | The same storyboard in Markdown |
| `film.html` | The film as a web page, with a CC toggle, chapter buttons and a chapters panel |
| `timeline.json` | **Single source of truth** for scene times, steps, chapters, impacts, background tint and every soundtrack cue |
| `build_film.py` · `narration.py` · `soundtrack.py` · `render.js` · `build_storyboard.py` | Rebuild the film, voice, music, video and storyboard |
| `subtitles.srt`, `subtitles.vtt` | Subtitles for video platforms |

## The story in 17 scenes

| Time | Scene | What it proves |
|------|-------|----------------|
| 0:00 | Cold open | AI accelerates operations, and change |
| 0:12 | Critical infrastructure | Six industries, on-prem and cloud, all depend on the network |
| 0:40 | Agentic operations, with controls | Human and policy → agent → approved automation → network (48 edge routers) |
| 1:12 | The change | 48/48 applied, 0 errors, BGP established: technical **success** |
| 1:40 | SevOne sees something different | Against its baseline, utilization goes from 47 to 82%, latency from 18 to 63 ms and loss from 0.1 to 2.1%, while BGP stays up |
| 2:25 | Before it becomes an incident | SevOne detects the problem at 09:24, before packet loss spreads |
| 2:55 | Six industries, six consequences | The same signal means different business risk in each sector |
| 3:55 | Root cause and blast radius | Symptom → scope → path → flow → change |
| 4:40 | Incident automation | SevOne event → automatic ServiceNow ticket → routing → **L1 and L2 automated, L3 human approval** |
| 5:25 | Verify the outcome | Re-measure against the baseline; the ticket closes only after recovery is confirmed |
| 5:55 | Risk controls | Network evidence for preventive, detective, diagnostic, corrective, verification and evidence controls, plus due diligence |
| 6:35 | Executive risk dashboard | KPIs set per service class, plus the **change outcome assurance rate** |
| 7:05 | TCO and OPEX | Before and after, six cost pools, then baseline → proof of value → measured delta → business case |
| 7:50 | Three truths | The agent, the automation platform and SevOne each report a different truth |
| 8:12 | The question | *If an AI agent changed 500 network devices tonight, how quickly could you determine whether every change produced the intended business outcome?* |
| 8:32 | Next step | Agentic Network Readiness & Observability Assessment (10 areas) |
| 9:00 | Closing | *In the age of Agentic AI, autonomy without observability is risk…* |

The narration for each scene, and its timing, is in the storyboard.

## Accuracy guardrails built into the film

- **SevOne observes and provides evidence.** The automation platform executes the remediation, and
  the L3 approval is made by a human. SevOne doesn't fix the network on its own, and it doesn't
  govern the AI agent. AI-agent and LLM observability is a separate product, IBM Instana.
- **gNMI / OpenConfig streaming telemetry** is labelled *Public Preview*.
- **Rail and energy:** network and communications assurance only. It is not a train-safety system,
  and it does not replace SCADA or OT protection.
- **Risk and compliance:** SevOne is "an important source of evidence", not a compliance guarantee.
- **TCO and OPEX:** no invented percentages. The film shows the measurement method; the numbers come
  from the customer's own proof of value.
- **The ServiceNow ticket, CMDB sync, routing and runbooks** are integrations built with SevOne
  events, webhooks and APIs. Confirm the exact options with the IBM SevOne team for the client's
  version.

## Rebuild it

Requires Python 3 with numpy, `kokoro-onnx` and `soundfile`, Node 18+ with Playwright, and ffmpeg.
The voice model setup is described in `../sevone-film-na/README.md`.

```bash
python3 build_film.py ../sevone-film-part2/film.html
```

```bash
python3 narration.py --model /path/to/kokoro --voice af_heart
```

```bash
python3 soundtrack.py
```

```bash
ffmpeg -y -i soundtrack.wav -af loudnorm=I=-16:TP=-1.0 -c:a libmp3lame -b:a 192k soundtrack.mp3
```

```bash
python3 build_storyboard.py
```

```bash
node render.js 30 4 sevone-agentic-assurance.mp4
```

```bash
CC=1 node render.js 30 4 sevone-agentic-assurance-captioned.mp4
```

To retime a scene, edit `timeline.json` (scene times, impacts and audio cues) and the cue times
in `narration.py`, then rebuild.
