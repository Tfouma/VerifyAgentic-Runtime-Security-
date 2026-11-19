# SevOne Part 2: Incident to Resolution, With a Human in the Loop

The second demo film follows on from the bank network edition (`sevone-film-bank/`). One incident
goes end to end:

1. SevOne detects and correlates the problem.
2. ITAM and the CMDB enrich it.
3. A ServiceNow incident is opened automatically.
4. NetOps and DevSecOps are notified.
5. **Levels 1 and 2 run automatically, and Level 3 keeps a human in the loop.**

The film runs 2 min 46 s, with narration, subtitles and an on-screen use case for each chapter.

**Everything in the film is a simulated scenario**, including the ServiceNow, Teams and Slack
screens. The narrator is a synthetic voice (Kokoro-82M, Apache-2.0).

| File | What it is |
|------|------------|
| `sevone-incident-to-resolution-part2.mp4` | The film: 1920×1080, 30 fps, narration and music, with an English subtitle track you can switch on |
| `sevone-incident-to-resolution-part2-captioned.mp4` | The same film with subtitles burned in |
| `film.html` | The film as a web page, with a CC toggle, chapter buttons and a **Use cases** panel |
| `narration.py`, `soundtrack.py`, `render.js` | Rebuild the voice, the soundtrack and the video. The *Rebuild it* steps below apply, using this edition's file names |
| `subtitles.srt`, `subtitles.vtt` | Subtitles for video platforms |

## The incident, step by step

| Chapter | What happens | Who acts |
|---|---|---|
| 01 Detect & enrich (0:40) | A failing optic on `core-rtr-hubS-02` raises 23 alerts across 37 branches. SevOne correlates them into **one incident**, suppressing duplicates and damping flaps. ITAM and the CMDB add the asset and serial, location, owner group (NetOps-South), business service (card payments, Tier 1), support contract, lifecycle and the last change (an IBM Bob agent). | Automatic |
| 02 Ticket (1:04) | A ServiceNow incident `INC0048213` opens **in 6 s**. Configuration item, impact and urgency (giving priority P2), assignment group, caller and SevOne evidence (trend, topology, config diff) are filled in. The alert and the incident stay in sync both ways, so it is 1 ticket, not 23. | Automatic |
| 03 Notify & route (1:26) | Routing rules page **NetOps-South** on-call in Teams, tell **DevSecOps** in Slack about the agent change on the CI, and email the service owner. The escalation policy is shown: L1 and L2 automated, L3 human. | Automatic |
| 04 L1 + L2 (1:48) | **L1:** triage (ping, trace, counters, optics), then a pre-approved runbook fails traffic over to the backup path. Service is restored in 47 s. **L2:** diagnoses the failing SFP from the optics trend, opens a vendor TAC case and reserves a spare from ITAM. | Automatic |
| 05 L3 (2:14) | Replacing hardware is a risky change, so it **escalates**. Change `CHG0031877` goes to an L3 NetOps engineer in ServiceNow and Teams with the evidence attached. **The engineer approves.** After the swap, SevOne verifies 0% loss, traffic returns to the primary path, the incident resolves and the ITAM serial is updated. | **Human approves**, then automatic verification |

## L1 / L2 / L3 policy shown in the film

| Level | Allowed without a human | Examples in the film | Guardrails |
|---|---|---|---|
| L1 | Read-only diagnostics, and pre-approved reversible actions | Ping, traceroute, interface and optic counters; fail over to a healthy backup path | Runbook allow-list; only when the backup is healthy; logged to the incident |
| L2 | Diagnosis and logistics, with no production change outside policy | Root cause from the optics trend; vendor TAC case; spare reserved in ITAM | Every step written to ServiceNow work notes |
| L3 | **Nothing that changes production without approval** | Hardware replacement, config change, firmware | A named approver, evidence attached, a change window and a rollback plan; SevOne verifies the result |

## Narration script

| Time | Line |
|------|------|
| 0:00 | Ten fourteen, Tuesday morning. Branch services are slowing down. And nobody has opened a ticket yet. |
| 0:09 | Part two: from the first symptom to a closed ticket, end to end. Detect, enrich, ticket, notify. Levels one and two are automated. Level three keeps a human in the loop. |
| 0:24 | So who owns this incident? Machines handle levels one and two. People decide at level three. |
| 0:33 | IBM SevOne. From incident, to resolution. |
| 0:41 | Step one: detect and enrich. A failing optic triggers twenty-three alerts. SevOne correlates them into one incident. ITAM and the CMDB add the asset, the owner group, and the business service. Card payments. Tier one. Under support contract, with the last change on record. |
| 1:05 | Step two: the ticket. SevOne opens a ServiceNow incident in six seconds. Configuration item, priority, assignment group, and evidence, filled in automatically. One ticket, not twenty-three, and it stays in sync both ways. |
| 1:27 | Step three: notify and route. NetOps South is paged in Teams. DevSecOps gets the agent change in Slack. The service owner is told what to expect. The policy is clear: levels one and two run automatically. Level three needs a human. |
| 1:48 | Step four: levels one and two. Level one triages, and fails traffic over to the backup path. Service is restored in forty-seven seconds. Nobody was paged to fix it. Level two finds the failing optic, opens the vendor case, and reserves a spare from ITAM. The hardware swap is a risky change. It escalates to level three. |
| 2:15 | Step five: the human in the loop. A level three engineer reviews the evidence, and approves the change. After the swap, SevOne verifies zero loss, and the incident closes itself, with ITAM updated. |
| 2:32 | Machines handle levels one and two. People decide at level three. IBM SevOne. From incident, to resolution. |

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
   node render.js 30 3 sevone-incident-to-resolution-part2.mp4
   ```

   ```bash
   CC=1 node render.js 30 3 sevone-incident-to-resolution-part2-captioned.mp4
   ```

**Changing the voice:** the film uses `af_heart`, a warm female U.S. voice and the
highest-rated Kokoro voice. For a deeper trailer-style read, try `am_michael` or `am_fenrir`.
To use your own recorded voiceover instead, replace `narration.wav` (44.1 kHz mono, lines at
the times above) and run `soundtrack.py` again.

## Presenter notes: product, integration and confirmation

Confirm current capabilities and packaging with the IBM SevOne team before you present this to a client.

- **SevOne:** alerting, correlation, deduplication and flap handling; topology and baselines;
  webhooks and REST APIs for the evidence and state that flow into the ticket.
- **Integration patterns**, built with SevOne APIs and webhooks:
  - The ServiceNow incident and change records and the bidirectional sync. Check the available
    ServiceNow integration for the client's SevOne version.
  - ITAM and CMDB enrichment, for example through the ServiceNow CMDB or an ITAM tool.
  - Teams, Slack and email routing, for example through ServiceNow notifications or the
    orchestrator.
  - L1 and L2 runbooks and the L3 approval, run through an orchestrator such as watsonx
    Orchestrate or another automation platform, with approvals in ServiceNow.
- **Illustrative numbers:** all figures, IDs and timings in the film.
