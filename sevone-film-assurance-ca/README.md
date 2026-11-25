# When AI Changes the Network, Who Verifies the Outcome? (Canada–U.S. architecture edition)

This copy extends `../sevone-film-assurance/` with three scenes: the **network architecture** (data centers in Montréal, Toronto and Vancouver; U.S. sites in New York, Chicago, Atlanta and San Francisco), the **BGP and SD-WAN configuration the AI agent builds and applies**, and **what went wrong, explained**. It runs 11:06.

A narrated, end-to-end demo film of about 11 minutes, with a production-ready storyboard. It shows
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
| `sevone-agentic-assurance-ca.mp4` | The film: 11:06, 1920×1080, 30 fps, narration, music and impacts, with an English subtitle track you can switch on |
| `sevone-agentic-assurance-ca-captioned.mp4` | The same film with subtitles burned in |
| `storyboard/storyboard.pdf` | **Production storyboard** for each scene: still frame, visuals, on-screen text, narration and soundtrack cues. Appendices cover industry risk-control matrices, the KPI framework, incident automation, the TCO/OPEX method, the 60-minute run of show and the assessment |
| `storyboard/STORYBOARD.md` | The same storyboard in Markdown |
| `film.html` | The film as a web page, with a CC toggle, chapter buttons and a chapters panel |
| `timeline.json` | **Single source of truth** for scene times, steps, chapters, impacts, background tint and every soundtrack cue |
| `build_film.py` · `narration.py` · `soundtrack.py` · `render.js` · `build_storyboard.py` | Rebuild the film, voice, music, video and storyboard |
| `subtitles.srt`, `subtitles.vtt` | Subtitles for video platforms |

## The story in 20 scenes

| Time | Scene | What it proves |
|------|-------|----------------|
| 0:00 | Cold open | AI accelerates operations, and change |
| 0:12 | Critical infrastructure | Six industries, on-prem and cloud, all depend on the network |
| 0:40 | **Network architecture** | DCs in Montréal, Toronto and Vancouver on an MPLS core (path A 10 Gb/s, path B 1 Gb/s); New York, Chicago, Atlanta and San Francisco over SD-WAN; BGP to ISPs and cloud |
| 1:08 | Agentic operations, with controls | Human and policy → agent → approved automation → network |
| 1:40 | **AI-built BGP and SD-WAN configuration** | The agent writes a route-map (local-pref 200 on path B) and an SD-WAN SLA class; syntax, lint, dry run and approval all pass |
| 2:14 | The change | 48/48 applied, 0 errors, BGP established: technical **success** |
| 2:42 | SevOne sees something different | Baseline deviation while BGP stays up |
| 3:27 | Before it becomes an incident | SevOne detects the problem at 09:24, while services are still up |
| 3:57 | Six industries, six consequences | Same signal, different business risk |
| 4:57 | Root cause and blast radius | Symptom → scope → path → flow → change |
| 5:42 | **What went wrong, explained** | (1) the route-map matches every prefix; (2) the SD-WAN SLA thresholds are far looser than the baseline; (3) success was defined as "config applied", with no outcome check. Each issue shows the evidence SevOne used to reveal it |
| 6:26 | Incident automation | Automatic ServiceNow ticket, routing, L1 and L2 automated, L3 human approval |
| 7:11 | Verify the outcome | Ticket closes only after SevOne re-measures |
| 7:41 | Risk controls | Network evidence for every control layer and for due diligence |
| 8:21 | Executive risk dashboard | KPIs plus the change outcome assurance rate |
| 8:51 | TCO and OPEX | Baseline → proof of value → measured delta → business case |
| 9:36 | Three truths | Agent, automation and SevOne |
| 9:58 | The question | The 500-device question |
| 10:18 | Next step | Agentic Network Readiness & Observability Assessment |
| 10:46 | Closing | Autonomy without observability is risk |

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
python3 build_film.py ../sevone-film-part2/film.html   # shared film engine
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
node render.js 30 4 sevone-agentic-assurance-ca.mp4
```

```bash
CC=1 node render.js 30 4 sevone-agentic-assurance-ca-captioned.mp4
```

To retime a scene, edit `timeline.json` (scene times, impacts and audio cues) and the cue times
in `narration.py`, then rebuild.
