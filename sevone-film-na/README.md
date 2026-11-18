# SevOne: Observability in the Age of Agentic AI (North America edition, narrated)

The North America version of the demo film: U.S. and Canada sites, Eastern time and USD,
plus a **narrator voice**, **subtitles** and an **on-screen use case for each chapter**.
It runs 2 min 46 s.

**Everything in the film is a simulated scenario.** Devices, agents, events and figures are
made up for illustration. The narrator is a synthetic voice (Kokoro-82M, a neural
text-to-speech model, Apache-2.0 licence), and the closing screen says so.

| File | What it is |
|------|------------|
| `sevone-agentic-observability-na.mp4` | The film: 1920×1080, 30 fps, narration and music. Includes an English subtitle track you can switch on in the player |
| `sevone-agentic-observability-na-captioned.mp4` | The same film with the subtitles burned in, for rooms with the sound off and for social posts |
| `film.html` | The film as a web page you can play. Includes a **CC** subtitle toggle, chapter buttons and a **Use cases** panel that explains each chapter and jumps to it |
| `soundtrack.mp3` | Music, impacts and narration, mixed (the web page uses it) |
| `narration.py` | Builds the narrator voice track, `narration.json`, `subtitles.srt` / `.vtt`, and writes the cues into `film.html` |
| `soundtrack.py` | Builds the music and impacts and mixes the narration on top. The music ducks about 13 dB under each spoken line |
| `render.js` | Renders `film.html` frame by frame into MP4 |
| `subtitles.srt`, `subtitles.vtt` | Subtitle files you can upload to YouTube, LinkedIn or a video platform |

## What changed from the original edition

| | Original (`sevone-film/`) | North America (this folder) |
|---|---|---|
| Sites | Paris, Frankfurt, Lyon, Milan, Madrid, London, Brussels, Zurich | DC Dallas, DC Ashburn, New York, Chicago, Atlanta, San Francisco, Vancouver, Toronto, Montreal |
| Cloud | AWS eu-west-1, Azure West Europe | AWS us-east-1, Azure Canada Central |
| Time and money | CET, € | Eastern Time (ET), USD |
| Core link | MPLS Paris ↔ Frankfurt | MPLS Ashburn ↔ Dallas |
| Business window | Market open 09:00 | NYSE and TSX open 09:30 ET |
| Audio | Music and impacts | Music, impacts and a **narrator** |
| Explanation | On-screen captions | A **use-case tag** on each chapter, **subtitles**, and a **Use cases** panel in the web page |

## The five use cases

| # | Chapter (time) | Use case | Situation | How SevOne helps | Outcome |
|---|---|---|---|---|---|
| 1 | Observe (0:40) | Agent change attribution across the U.S. and Canada | 14 agents change routers, firewalls, load balancers and cloud routes overnight. Nobody can say who changed what. | Collects SNMP, flow, streaming telemetry, logs and cloud metrics into one live topology. Each change is tied to the agent identity, the device and the measured effect. | One source of truth from Vancouver to Montreal and from AWS us-east-1 to Azure Canada Central. |
| 2 | Anticipate (1:04) | SD-WAN policy drift → MPLS capacity forecast | A Devin agent changes an SD-WAN policy at 01:12 ET. Nothing breaks yet. | Baselines show the Ashburn ↔ Dallas MPLS link drifting above normal. Forecasting predicts a 95% breach at 08:40 ET and names the likely cause. | About 6 hours of warning, 50 min before the NYSE and TSX open, with the users at risk and a recommended fix. |
| 3 | Prevent (1:26) | Pre-flight blast-radius check for a core upgrade | A Claude Code agent plans to upgrade both core routers at the same time. | The agent's tool calls SevOne APIs first: device health, loss on the redundant path, blast radius and the business calendar. A policy decides. | The change is held for a human (CHG-20931) and the agent re-plans a rolling upgrade. No outage at market open. |
| 4 | React (1:48) | WAF misconfiguration → correlation and rollback | A WAF rule pushed by a Cursor agent makes checkout latency 11 times worse in us-east-1. | Detects the anomaly in 8 s, links it to the change made 8 s earlier and to the agent session, and a webhook triggers watsonx Orchestrate to roll back. | Resolved in 47 s with a full audit trail. Nobody paged at 3 AM. |
| 5 | Control (2:14) | Agent governance scorecard | Leaders must decide which agents to trust with production. | Every agent gets a safe-change score based on what it actually did: changes, incidents caused, rollbacks. | 100% attribution, risky changes held, MTTR in seconds, $3.1M downtime avoided (illustrative). |

## Narration script

The script lives in `CUES` in `narration.py`. Change a line there and rebuild. Each line has a
target start time. If a line runs into the next one, the script speeds it up, up to 1.12×,
and stops with an error if it still doesn't fit, so the timing never drifts silently.

| Time | Line |
|------|------|
| 0:00 | Two forty-seven A.M., Eastern. No engineer is awake. But fourteen AI agents are changing your network. |
| 0:09 | From New York to Vancouver, your teams have handed the network to AI agents. BGP, SD-WAN, firewalls, patching, even incident response. Twelve hundred changes in one hour. Forty-one reviewed by a human. |
| 0:24 | So who is watching the agents? Machine-speed change needs machine-speed observability. |
| 0:33 | IBM SevOne. Observability, for the age of agentic AI. |
| 0:41 | Use case one: observe. SevOne collects SNMP, flow, telemetry, logs and cloud metrics, across the U.S. and Canada, into one real-time view. And every change an agent makes is tied to its identity, the device it touched, and the effect it had. |
| 1:05 | Use case two: anticipate. At one-twelve, a Devin agent changed an SD-WAN policy. Nothing broke. But SevOne sees the Ashburn to Dallas MPLS link drifting above baseline, and forecasts a breach at eight-forty, before the opening bell. With the cause, the users at risk, and the fix. |
| 1:27 | Use case three: prevent. A Claude Code agent plans to upgrade both core routers at once. SevOne's pre-flight finds a degraded backup path, and fourteen sites at risk. The change is held for a human. The agent re-plans a safe, rolling upgrade. SevOne's live data becomes the guardrail. |
| 1:48 | Use case four: react. A Cursor agent pushes a new WAF rule. Checkout latency jumps eleven times. SevOne flags it in eight seconds. It links the anomaly to the change, and the change to the agent, then triggers a rollback through watsonx Orchestrate. Resolved in forty-seven seconds. Nobody paged at three A.M. |
| 2:15 | Use case five: control. Every agent change, attributed. Thirty-seven risky changes, held. And a safe-change score for every agent, based on what it actually did to your network. That's real control. In real time. |
| 2:32 | Your AI agents act at machine speed. SevOne observes at machine speed. IBM SevOne. See everything. Control everything. |

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
   node render.js 30 3 sevone-agentic-observability-na.mp4
   ```

   ```bash
   CC=1 node render.js 30 3 sevone-agentic-observability-na-captioned.mp4
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
- **Illustrative numbers:** the Control-scene KPIs, the safe-change scores and the USD figure.

Agent and product names describe the kinds of tools clients use. They do not mean that
those vendors endorse this demo.
