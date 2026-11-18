# SevOne: Observability in the Age of Agentic AI (Canada-first edition, narrated)

This edition puts **Canadian sovereignty first**. Montréal, Toronto and Vancouver are the data
centers where SevOne runs and where telemetry and agent audit data are stored. New York,
Chicago, Atlanta and San Francisco are U.S. branches, visible in the same view, with the
Canada–U.S. border drawn on the map. It runs 2 min 46 s with a narrator, subtitles and an
on-screen use case for each chapter.

**Everything in the film is a simulated scenario.** Devices, agents, events and figures are
made up for illustration. The narrator is a synthetic voice (Kokoro-82M, Apache-2.0), and the
closing screen says so.

| File | What it is |
|------|------------|
| `sevone-agentic-observability-ca.mp4` | The film: 1920×1080, 30 fps, narration and music, with an English subtitle track you can switch on |
| `sevone-agentic-observability-ca-captioned.mp4` | The same film with subtitles burned in |
| `film.html` | The film as a web page: **CC** toggle, chapter buttons and a **Use cases** panel that jumps to each chapter |
| `soundtrack.mp3` | Music, impacts and narration, mixed (the web page uses it) |
| `narration.py` | Narration script (`CUES`). It builds the voice track, `narration.json`, `subtitles.srt` / `.vtt`, and the cues in `film.html` |
| `soundtrack.py` | Music and impacts, with the narration mixed on top (the music ducks under the voice) |
| `render.js` | Renders `film.html` frame by frame into MP4 |
| `subtitles.srt`, `subtitles.vtt` | Subtitles for YouTube, LinkedIn or a video platform |

## How sovereignty shows up in the film

| Where | What the audience sees |
|---|---|
| Throughout | A **DATA RESIDENCY · CANADA** badge in the top-left corner of every scene |
| Question (0:24) | "Who is watching the agents? **And is your data still in Canada?**" |
| Title (0:32) | "Canada first · Sovereign observability for the age of agentic AI" |
| 01 Observe | Topology led by **DC Montréal, DC Toronto and DC Vancouver**, plus AWS ca-central-1 and Azure Canada Central. A dashed **Canada / United States** border separates the U.S. branches. A KPI shows **100% of data stored in Canada**, and a source chip reads "Collectors on-prem in Canada" |
| 02 Anticipate | The core link is **MPLS Toronto ↔ Montréal**. The breach is forecast before the **TSX** opens |
| 03 Prevent | The pre-flight check fails on **"Sovereignty breach on failover: Canadian traffic would transit Chicago (U.S.)"**. The HOLD comes from a **data-sovereignty policy**, and the agent re-plans so failover stays in Canada via Montréal |
| 04 React | The incident is in **AWS ca-central-1**. The audit trail stays in Canada |
| 05 Control | 100% of telemetry and audit data in Canada · 37 risky changes held, **6 for sovereignty** · MTTR 47 s · **$4.2M CAD** avoided (illustrative) |
| Close | "SevOne observes at machine speed. In Canada. IBM SevOne. Sovereign by design." |

## Comparison with the other editions

| | Original (`sevone-film/`) | North America (`sevone-film-na/`) | Canada first (this folder) |
|---|---|---|---|
| Data centers | Paris, Frankfurt | Dallas, Ashburn | **Montréal, Toronto, Vancouver** |
| Branches | European cities | U.S. and Canadian cities | New York, Chicago, Atlanta, San Francisco |
| Cloud | AWS eu-west-1, Azure West EU | AWS us-east-1, Azure Canada Central | **AWS ca-central-1, Azure Canada Central** |
| Currency and market | €, market open 09:00 | USD, NYSE and TSX | **CAD, TSX** |
| Theme | Agentic observability | Agentic observability, narrated | **Sovereign** agentic observability, narrated |

## The five use cases

| # | Chapter | Use case | Situation | How SevOne helps | Outcome |
|---|---|---|---|---|---|
| 1 | Observe (0:40) | Sovereign observability · Canadian DCs first | 14 agents change routers, firewalls, load balancers and cloud routes overnight, across Canadian DCs and U.S. branches. | Runs on-prem in Montréal, Toronto and Vancouver. Collects SNMP, flow, streaming telemetry, logs and Canadian cloud-region metrics, and ties each agent change to its identity, device and effect. | Telemetry and audit data stay in Canada, and the U.S. branches are still in the same view. |
| 2 | Anticipate (1:04) | SD-WAN policy drift → MPLS capacity forecast | A Devin agent changes an SD-WAN policy at 01:12 ET. | Baselines show the Toronto ↔ Montréal MPLS link drifting above normal. The forecast predicts a 95% breach at 08:40 ET. | About 6 hours of warning, before the TSX opens, with the users at risk and a fix. |
| 3 | Prevent (1:26) | Sovereignty-aware pre-flight for a core upgrade | A Claude Code agent plans to upgrade both Toronto core routers at once. | The agent's tool calls SevOne APIs: device health, backup-path loss, **the failover route** and the business calendar. The failover would cross into the U.S. A policy decides. | The change is held (CHG-20931). The agent re-plans a rolling upgrade with failover kept in Canada. |
| 4 | React (1:48) | WAF misconfiguration → correlation and rollback | A Cursor agent's WAF rule makes checkout latency 11 times worse in ca-central-1. | Detects it in 8 s, links the change and the agent, and a webhook triggers watsonx Orchestrate to roll back. | Resolved in 47 s. The audit trail stays in Canada. |
| 5 | Control (2:14) | Sovereign agent governance | Leaders and regulators ask which agents touch Canadian systems and where the data lives. | A safe-change score for each agent. Data residency is measured, not assumed. | 100% of data in Canada · 37 changes held (6 for sovereignty) · $4.2M CAD avoided (illustrative). |

## Narration script

The script lives in `CUES` in `narration.py`. Each line is timed to its scene. If a line runs
long, the build speeds it up, up to 1.12×, and fails rather than letting the timing drift.

| Time | Line |
|------|------|
| 0:00 | Two forty-seven A.M., Eastern. No engineer is awake. But fourteen AI agents are changing your network. |
| 0:09 | From Vancouver to Toronto to Montreal, your teams have handed the network to AI agents. BGP, SD-WAN, firewalls, patching, even incident response. Twelve hundred changes in one hour. Forty-one reviewed by a human. |
| 0:24 | So who is watching the agents? And is your data still in Canada? |
| 0:33 | IBM SevOne. Sovereign observability, for the age of agentic AI. |
| 0:41 | Use case one: observe, with Canada first. SevOne runs in your Montreal, Toronto and Vancouver data centers. Telemetry and agent audit data stay in Canada. It still sees your U.S. branches, and ties every agent change to its identity, its device, and its effect. |
| 1:05 | Use case two: anticipate. At one-twelve, a Devin agent changed an SD-WAN policy. Nothing broke. But SevOne sees the Toronto to Montreal MPLS link drifting above baseline, and forecasts a breach at eight-forty, before the TSX opens. With the cause, the users at risk, and the fix. |
| 1:27 | Use case three: prevent. A Claude Code agent plans to upgrade both Toronto core routers. SevOne's pre-flight finds the failover would carry Canadian traffic through Chicago. That breaks sovereignty. The change is held. The agent re-plans, and stays in Canada. Sovereignty becomes a guardrail. |
| 1:48 | Use case four: react. A Cursor agent pushes a new WAF rule. Checkout latency jumps eleven times. SevOne flags it in eight seconds. It links the anomaly to the change, and the change to the agent, then triggers a rollback through watsonx Orchestrate. Resolved in forty-seven seconds. The audit trail never leaves Canada. |
| 2:15 | Use case five: control. All telemetry, kept in Canada. Every agent change, attributed. And a safe-change score for every agent, based on what it actually did. Sovereign control. In real time. |
| 2:32 | Your AI agents act at machine speed. SevOne observes at machine speed. In Canada. IBM SevOne. Sovereign by design. |

## Play it

- **Video:** open either MP4. In the clean version, turn on the English subtitle track in your
  player if you want captions.
- **Browser:** open `film.html`, which needs `soundtrack.mp3` in the same folder. Use **CC** to
  turn subtitles on or off, **Use cases** to open the explainer, **Space** to play or pause and
  **← / →** to move 5 s. Add `?cc=0` to the URL to start with subtitles off.

## Rebuild it

Requires Python 3 with numpy, `kokoro-onnx` and `soundfile`, Node 18+ with Playwright, and ffmpeg.

1. Get the voice model once from Hugging Face (`onnx-community/Kokoro-82M-v1.0-ONNX`): `onnx/model.onnx`, plus
   the `voices/<name>.bin` files you want. Pack the voices with:

   ```bash
   python3 -c "import numpy as np,sys; np.savez('voices.npz', **{n: np.fromfile(n+'.bin', dtype=np.float32).reshape(-1,1,256) for n in sys.argv[1:]})" af_heart am_michael
   ```

2. Build the narration, then the soundtrack, then the video:

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
   node render.js 30 3 sevone-agentic-observability-ca.mp4
   ```

   ```bash
   CC=1 node render.js 30 3 sevone-agentic-observability-ca-captioned.mp4
   ```

**Changing the voice:** the film uses `af_heart`, a warm female U.S. voice and the
highest-rated Kokoro voice. For a deeper trailer-style read, try `am_michael` or `am_fenrir`.
To use your own recorded voiceover instead, replace `narration.wav` (44.1 kHz mono, lines at
the times above) and run `soundtrack.py` again.

## Presenter notes: what is product and what is pattern

Confirm current capabilities and packaging with your IBM SevOne product team before you
present to a client.

- **Product capabilities:** multi-source collection (SNMP, NetFlow/IPFIX/sFlow, streaming
  telemetry, syslog/traps, APIs, cloud metrics), topology, baselining and anomaly detection,
  capacity forecasting, dashboards, alerting, webhooks and REST APIs.
- **Integration patterns** (built with SevOne APIs plus an orchestrator or agent platform):
  - **Agent attribution.** You join change and audit logs (AAA/TACACS, Git commits, agent
    session IDs) to SevOne events.
  - **Pre-flight HOLD.** The agent's tool calls SevOne APIs, and a policy decides whether the
    change goes ahead. Enforcement lives in the agent or orchestration layer.
  - **Auto-rollback.** A SevOne alert webhook triggers a workflow in watsonx Orchestrate or
    another runbook tool.
- **Sovereignty claims.** Data residency depends on the deployment: SevOne installed in
  Canadian data centers, collectors and storage in Canada, and Canadian cloud regions. Confirm
  the deployment architecture and any requirements (for example OSFI, PIPEDA, Quebec Law 25,
  or Protected B) with the client and the IBM team. The "sovereignty breach on failover" check
  is an integration pattern: a policy evaluates the route that SevOne reports.
- **Illustrative numbers:** the Control-scene KPIs, the safe-change scores and the CAD figure.

Agent and product names describe the kinds of tools clients use. They do not mean that
those vendors endorse this demo.
