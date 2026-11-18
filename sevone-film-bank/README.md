# SevOne: Observability in the Age of Agentic AI (bank network edition, narrated)

This edition has no sovereignty theme. The demo is built around use cases from a public-sector
bank's enterprise NMS RFP: about 6,000 devices and 6,000 links, with fault, performance and
configuration in one operating view. It runs 2 min 46 s, with a narrator, subtitles and an
on-screen use case for each chapter.

**Everything in the film is a simulated scenario.** Devices, agents, events and figures are made
up for illustration. The narrator is a synthetic voice (Kokoro-82M, Apache-2.0).

| File | What it is |
|------|------------|
| `sevone-agentic-observability-bank.mp4` | The film: 1920×1080, 30 fps, narration and music, with an English subtitle track you can switch on |
| `sevone-agentic-observability-bank-captioned.mp4` | The same film with subtitles burned in |
| `film.html` | The film as a web page, with a CC toggle, chapter buttons and a **Use cases** panel |
| `narration.py`, `soundtrack.py`, `render.js` | Rebuild the voice, the soundtrack and the video (see *Rebuild it*) |
| `subtitles.srt`, `subtitles.vtt` | Subtitles for video platforms |

## RFI use cases in the film

| Chapter | RFP requirement (paraphrased) | What the audience sees |
|---|---|---|
| 01 Observe (0:40) | L2/L3 topology to port level with distinct icons · primary vs backup links · IPv4, IPv6 and dual stack · real-time config change detection · data lake for your own BI | Topology of DC Primary, DR Site, four hubs and branches. Routers, firewalls, switches and branches have their own icons, primary links are solid, backup links are dashed, and each node shows its address family. A change stream detects config changes, such as running ≠ startup config, and attributes each one to an agent |
| 02 Anticipate (1:04) | Capacity planning · unused and dormant switch ports with last activity | A primary-link forecast breaches 95% at 08:40, before branches open. A port report lists 1,240 dormant switch ports with last-active dates |
| 03 Prevent (1:26) | Config backup · compliance validation · bulk config and firmware · EOL/EOS · vulnerability mapping · **approval gating and dry run** | A Claude Code agent plans an ACL and firmware push to 312 routers. The pre-flight shows the backup taken, a dry run where 3 devices fail, 2 drifting from the golden config, 41 reaching end of support, and the vulnerability fix. Approval by a nominated bank official leads to a phased rollout |
| 04 React (1:48) | **Flap detection and damping** · degraded redundant path vs loss of location · internal URL monitoring · one-click rollback | A QoS change makes the primary link flap. 14 transitions become one condition, the backup link is up (degraded, not down), the config diff points to the agent, and a one-click rollback follows. A synthetic URL test of the core banking portal shows the impact |
| 05 Control (2:14) | Inventory, compliance and policy reporting | 100% of changes attributed · 98.6% golden-config compliance · 41 end-of-support devices tracked · 37 changes held at the approval gate · a safe-change score per agent |

## Narration script

| Time | Line |
|------|------|
| 0:00 | Two forty-seven A.M. No engineer is awake. But fourteen AI agents are changing your bank's network. |
| 0:09 | Your teams have handed six thousand devices and six thousand links to AI agents. Config backups, bulk changes, firmware, firewalls, even incident response. Twelve hundred changes in one hour. Forty-one reviewed by a human. |
| 0:24 | So who is watching the agents? Machine-speed change needs machine-speed observability. |
| 0:33 | IBM SevOne. Observability, for the age of agentic AI. |
| 0:41 | Use case one: observe. SevOne maps layer two and layer three topology down to the port, with primary and backup links shown apart, across IPv4, IPv6 and dual stack. Every configuration change is detected in real time, and tied to the agent that made it. And the data flows to your own BI tools. |
| 1:05 | Use case two: anticipate. At one-twelve, a Devin agent changed an SD-WAN policy. Nothing broke. But SevOne sees the Hub North link drifting above baseline, and forecasts a breach at eight-forty, before branches open. And it finds twelve hundred dormant switch ports to reclaim. |
| 1:27 | Use case three: prevent. A Claude Code agent plans a bulk push to 312 routers. The pre-flight runs a dry run, and checks compliance, firmware lifecycle and vulnerabilities. Bulk changes need approval from a nominated bank official. Approved after the dry run, as a safe, phased rollout. Automation, with a gate. |
| 1:48 | Use case four: react. A Cursor agent changes QoS on a branch router. The primary link starts flapping. SevOne reports one condition, not fourteen alerts. The backup link is up, so the branch is degraded, not down. The config diff points to the agent. One click rolls back to the known-good config. Resolved in forty-seven seconds. |
| 2:15 | Use case five: control. Every agent change, attributed. Golden-config compliance, end-of-support milestones, and the approval log, in one place. Real control. In real time. |
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
   node render.js 30 3 sevone-agentic-observability-bank.mp4
   ```

   ```bash
   CC=1 node render.js 30 3 sevone-agentic-observability-bank-captioned.mp4
   ```

**Changing the voice:** the film uses `af_heart`, a warm female U.S. voice and the
highest-rated Kokoro voice. For a deeper trailer-style read, try `am_michael` or `am_fenrir`.
To use your own recorded voiceover instead, replace `narration.wav` (44.1 kHz mono, lines at
the times above) and run `soundtrack.py` again.

## Presenter notes: product, integration and confirmation

The film is a discussion aid, not a compliance statement. Before you answer an RFP, validate each
item with the IBM SevOne product team.

- **SevOne observability (confirm version and packaging):** topology, discovery including IPv6 and
  dual stack, alerting including flap handling, flow, capacity and reporting (dormant ports), data
  export and APIs, synthetic URL tests.
- **Integration patterns (confirm the IBM ecosystem or partner offering):** configuration backup
  and restore, compliance validation, bulk config and firmware deployment, one-click rollback,
  vulnerability-platform integration, and approval gating with dry run. These run through an
  automation or NCCM tool, an orchestrator (for example watsonx Orchestrate) and ITSM, with SevOne
  providing the live data and the events.
- **Illustrative numbers:** all figures in the film.
