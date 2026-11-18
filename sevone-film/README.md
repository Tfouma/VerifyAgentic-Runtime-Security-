# SevOne: Observability in the Age of Agentic AI (demo film)

A 2 min 46 s cinematic demo film for a client audience. It shows how IBM SevOne helps an
organization **observe, anticipate, prevent, react to and control** what AI agents do to
the network and infrastructure.

**Everything in the film is a simulated scenario.** Devices, agents, events and figures are
made up for illustration. Nothing connects to a real system.

| File | What it is |
|------|------------|
| `sevone-agentic-observability.mp4` | The rendered film: 1920×1080, 30 fps, H.264 + AAC, with the soundtrack |
| `film.html` | The same film as a web page you can play, pause and jump through by chapter. It needs `soundtrack.mp3` in the same folder |
| `soundtrack.py` | Builds the soundtrack (pad, pulse bass, risers, impacts). Every sound is synthesized, so there is no licensing issue |
| `render.js` | Renders `film.html` frame by frame into the MP4 |
| `shots.js` | Saves still frames for review: `node shots.js <dir> 12 60 97` |

## Play it

- **Video:** open `sevone-agentic-observability.mp4` in any player.
- **Live in a browser:** open `film.html`. Press **Space** to play or pause and **← / →** to
  move 5 s. The chapter buttons jump to Observe, Anticipate, Prevent, React and Control.

## Rebuild it

Requires Python 3 with numpy, Node 18+ with Playwright, and ffmpeg.

```bash
python3 soundtrack.py
```

```bash
ffmpeg -y -i soundtrack.wav -af loudnorm=I=-16:TP=-1.0 -c:a libmp3lame -b:a 192k soundtrack.mp3
```

```bash
node render.js 30 3 sevone-agentic-observability.mp4
```

Impact times appear in two places: `IMPACTS` in `film.html` and `IMPACTS` in `soundtrack.py`.
Keep them in sync when you retime a scene.

## Storyboard and voiceover

The film has no spoken voice, so you can narrate it live. Or record this script over it.
Each line fits its scene at a calm pace.

| Time | Scene | On screen | Voiceover |
|------|-------|-----------|-----------|
| 0:00 | Cold open | "Sunday · 02:47 AM. No engineer is awake. But 14 AI agents are changing your network." | *"It's 2:47 on a Sunday morning. Nobody on your team is awake. But your network is changing."* |
| 0:09 | The new operating model | watsonx Orchestrate, IBM Bob, Devin, Windsurf, Codex, Claude Code, Cursor, Grok, Amazon Bedrock Agents and more connect to the network. Tasks: BGP, SD-WAN, firewall, WAF, load balancing, MPLS, cloud, patching, upgrades, root cause, ITDR. 1,284 changes, 41 reviewed by a human. | *"Your teams have handed routine work to AI agents: router configs, BGP, SD-WAN, firewalls, patching, upgrades, even incident handling. In one hour, more than a thousand changes. A human reviewed forty-one."* |
| 0:24 | The question | "Who is watching the agents?" | *"So who is watching the agents?"* |
| 0:32 | Title | IBM SevOne: Observe · Anticipate · Prevent · React · Control | *"IBM SevOne. Observability for the age of agentic AI."* |
| 0:40 | **01 Observe** | Live hybrid-WAN topology, telemetry counters, and an agent change stream with each change tied to its agent, device and effect. | *"SevOne collects SNMP, flow and streaming telemetry, logs and cloud metrics into one real-time view. Every change an agent makes is tied to its identity, the device it touched and the effect it had."* |
| 1:04 | **02 Anticipate** | MPLS Paris–Frankfurt utilization against its learned baseline. After Devin's SD-WAN policy change, the forecast crosses 95% at 08:40. | *"Baselines and forecasting catch the side effects. A policy change at 1:12 AM is quietly pushing the core link toward saturation. SevOne predicts the breach six hours ahead and names the likely cause."* |
| 1:26 | **03 Prevent** | A Claude Code agent plans a parallel IOS-XE upgrade of both core routers. A SevOne pre-flight finds a degraded redundant path, a large blast radius and the market-open window. **HOLD.** The agent re-plans a rolling upgrade. | *"Before it acts, the agent checks with SevOne. The redundant path is already degraded and both routers serve fourteen sites. The change is held for a human. The agent re-plans a safe rolling upgrade."* |
| 1:48 | **04 React** | A WAF rule pushed by a Cursor agent spikes checkout latency ×11. SevOne detects it in 8 s, correlates the change and the agent, and a webhook triggers rollback through watsonx Orchestrate. Resolved in 47 s. | *"When something still breaks, speed matters. SevOne flags the anomaly in eight seconds, links it to the change made eight seconds earlier and the agent behind it, and triggers an automated rollback. Resolved in under a minute."* |
| 2:14 | **05 Control** | 100% of agent changes attributed · 37 risky changes held · MTTR 47 s · €2.4M downtime avoided. A safe-change score for each agent. | *"That's real control: every agent change attributed, risky changes held, and a safe-change score for each agent, based on what it actually did to your network."* |
| 2:32 | Close | "Your AI agents act at machine speed. SevOne observes at machine speed." | *"Your agents act at machine speed. SevOne observes at machine speed."* |

## Presenter notes: what is product and what is pattern

Confirm current capabilities and packaging with your IBM SevOne product team before you
present to a client. In the film:

- **Product capabilities:** multi-source collection (SNMP, NetFlow/IPFIX/sFlow, streaming
  telemetry, syslog/traps, APIs, cloud metrics), topology, baselining and anomaly detection,
  capacity forecasting, dashboards, alerting and webhooks, and REST APIs.
- **Integration patterns** (built with SevOne APIs plus an orchestrator or agent platform,
  not a single checkbox):
  - **Agent attribution.** You join change and audit logs (AAA/TACACS, Git commits, agent
    session IDs) to SevOne events.
  - **Pre-flight "HOLD".** The agent's tool calls SevOne APIs, and a policy decides whether
    the change goes ahead. SevOne supplies the live data. The enforcement lives in the agent
    or orchestration layer.
  - **Auto-rollback.** A SevOne alert webhook triggers a workflow in watsonx Orchestrate or
    another runbook tool.
- **Illustrative numbers:** the KPIs in the Control scene, the safe-change scores and the
  euro figure.

Agent and product names describe the kinds of tools clients use. They do not mean that
those vendors endorse this demo.
