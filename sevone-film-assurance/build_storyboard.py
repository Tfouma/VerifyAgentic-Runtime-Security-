"""Builds the production storyboard (Markdown + PDF) from timeline.json, narration.json and scene stills.

    python3 build_storyboard.py         # after narration.py; needs Playwright for stills and the PDF

Writes storyboard/STORYBOARD.md, storyboard/storyboard.html, storyboard/storyboard.pdf and
storyboard/stills/*.jpg. Because the narration, timings and sound cues are read from the same
files the film is rendered from, the storyboard always matches the film.
"""
import html, json, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'storyboard'
(OUT / 'stills').mkdir(parents=True, exist_ok=True)
TL = json.loads((HERE / 'timeline.json').read_text())
NAR = json.loads((HERE / 'narration.json').read_text())
AU = TL['audio']


def mmss(t):
    return f'{int(t) // 60}:{int(t) % 60:02d}'


# Hand-written production detail per scene: visuals, on-screen text, music mood, hero frame (local s).
SCENE = {
 's0': ('Black open. Faint scrolling agent and automation logs behind a centred clock “MONDAY · 09:20”. Typewriter line, then a punch line in red.',
        ['MONDAY · 09:20', 'AI accelerates operations.', 'It also accelerates change.'], 'Sub drone and single bass impact; typewriter ticks; tension pad enters.', 7),
 's1': ('Six industry tiles fill in (banking, telecom, rail, energy, government, AI & data), then a row of environment chips: on-prem DCs, private cloud, AWS · Azure, WAN · MPLS, SD-WAN, BGP edge, DC fabrics, Wi-Fi, OT boundary.',
        ['Every critical service depends on the network, and on the agents that now change it.'], 'Pulse bass starts (96 BPM); pad opens up.', 18),
 's2': ('Engineer prompt card; the agent’s proposal types in. A five-step control chain lights up in sequence: Human & policy → AI agent → Change approval → Automation platform → Network (48 edge routers).',
        ['A routine optimization, done the right way.', '“Optimize connectivity between Montréal and Toronto while maintaining application performance.”', 'No magic. Approved, governed change, executed through automation.'], 'Kick drum enters; light hi-hats for a “systems” feel.', 26),
 's3': ('Automation console prints the playbook run line by line: 48 targeted, 48 applied, 0 errors, BGP 96/96 established. A green “CHANGE SUCCESSFUL” card pops. Hold, then the question lands in red.',
        ['STATUS: SUCCESS', '✓ CHANGE SUCCESSFUL', 'But did the business outcome succeed?'], 'Console blips per line; riser into a hard stop; big impact on the question with music drop-out (0:96).', 25),
 's4': ('Switch to SevOne. Utilization chart draws against the learned baseline band; a red “DEVIATION FROM BASELINE · 09:23” tag pops. KPI tiles count up: 47→82 %, 18→63 ms, 0.1→2.1 %; BGP still ESTABLISHED. Split table: Automation says ✓ vs Network assurance says ⚠.',
        ['The change succeeded. The outcome didn’t.', 'DEVIATION FROM BASELINE · 09:23', 'Demo scenario values · gNMI in Public Preview'], 'Alarm tone and impact at the deviation; red tint; heavier kick.', 22),
 's5': ('Horizontal timeline 09:21 → 09:26. The yellow progress bar stops at 09:24 where a green “SEVONE DETECTS · 09:24” badge appears; 09:25 and 09:26 grey out and are struck through. Four evidence tiles: baselines, flow, telemetry, synthetics.',
        ['Don’t wait for DOWN. Detect while services are still UP.', 'SEVONE DETECTS · 09:24'], 'Amber tint; music steadies; riser into the industries section.', 16),
 's6': ('Six industry cards (3 × 2). Each card in turn brightens with a cyan border while the narrator covers it: architecture path, risk, KPI chips, and a guardrail note for rail, energy and AI.',
        ['One deviation. Six business consequences.', 'Rail: communications assurance, not a train-safety system', 'Energy: monitoring stays separate from safety and OT control', 'AI infrastructure is also network infrastructure'], 'Full arrangement; soft blip as each card activates.', 51),
 's7': ('Five RCA rows slide in (symptom → scope → path → flow → change). On the right, the blast-radius stack turns red from the BGP path down to the critical banking service; five question chips turn green.',
        ['From symptom to cause, with evidence.', 'What changed? Where? What is abnormal? What could be affected? How urgent?'], 'Steady pulse; no impacts, to keep focus on the narration.', 36),
 's8': ('Seven-stage pipeline with a travelling pulse: SevOne → Event → Ticket → Route → L1 (auto) → L2 (auto) → L3 (human). A ServiceNow incident card fills in (CI from CMDB, P2, related change, evidence). L1/L2/L3 cards stack on the right, ending with the engineer’s approval.',
        ['From evidence to action, inside your processes.', 'INC0051207 · AUTO-CREATED · 7 s', 'L3 · human in the loop · automation executes · SevOne observes'], 'Soft chime when the ticket is created.', 30),
 's9': ('Tiles count back down (82→49 %, 63→19 ms, 2.1→0.1 %), service NORMAL. Chart redraws with the 09:31 rollback back inside the baseline band. The assurance loop lights OBSERVE → DETECT → UNDERSTAND → ACT → VERIFY.',
        ['A job says “done”. The network proves it.', '✓ INC0051207 closed only after SevOne confirms the baseline'], 'Resolution chime; green tint.', 18),
 's10': ('Six-row control table builds row by row: preventive, detective, diagnostic, corrective, verification, evidence; columns for business question, SevOne contribution and adjacent enterprise controls. Due-diligence note at the bottom.',
        ['Network evidence across every control layer.', 'SevOne is an important source of evidence, not a compliance guarantee.'], 'Row blips; even, confident pulse.', 30),
 's11': ('Ten executive KPI tiles (demo values) and the change outcome assurance rate formula counting to 98.4 %. Chips show KPI families set per service class.',
        ['Network operational risk, on one page.', 'CHANGE OUTCOME ASSURANCE RATE = validated post-change states ÷ changes requiring validation', 'Illustrative demo values'], 'Pulse continues; slight lift.', 20),
 's12': ('Before vs After columns, six cost-pool tiles, then a flow: TCO baseline → Proof of value → Measured delta → Business case (green).',
        ['Prove the savings. Don’t assume them.', 'TCO baseline → Proof of value → Measured delta → Business case'], 'Green tint; music begins to resolve.', 30),
 's13': ('Three statements appear one by one, attributed to the AI agent, the automation platform and IBM SevOne, then the conclusion.',
        ['“I completed the task.”', '“The configuration was deployed.”', '“Here is what happened to the network.”', 'The business needs all three. Only independent observability verifies the outcome.'], 'Music thins out; riser into the question.', 16),
 's14': ('Full-screen question on a red-tinted background, held for the whole scene.',
        ['If an AI agent changed 500 network devices tonight, how quickly could you determine whether every change produced the intended business outcome?'], 'Biggest impact of the film, then near silence: drone only.', 12),
 's15': ('Title, then ten numbered assessment items appear two by two; outcome line at the bottom.',
        ['Agentic Network Readiness & Observability Assessment', '1–10 assessment areas', 'Outcome: a gap map, prioritized use cases, and a proof-of-value plan with measured KPIs.'], 'Pulse returns softly; blip per item.', 22),
 's16': ('Closing lines build one per beat, then clear to the IBM SevOne brand reveal and tagline; disclaimer at the bottom; fade to black.',
        ['In the age of Agentic AI, autonomy without observability is risk.', 'The future isn’t just autonomous networking.', 'It’s autonomous networking with continuous assurance.', 'IBM SevOne · Observe · Baseline · Detect · Diagnose · Respond · Verify'], 'Riser, brand-reveal impact, sustained final chord, fade out.', 13),
}


def sound_cues(sc):
    a, b = sc['start'], sc['end']
    cues = []
    for t, w in TL['impacts']:
        if a <= t < b: cues.append((t, f'impact ({w})'))
    for t, d in AU['risers']:
        if a <= t + d <= b + .1: cues.append((t, f'riser {d:g} s'))
    for t in AU['alarms']:
        if a <= t < b: cues.append((t, 'alarm tone'))
    for t, g in AU['chimes']:
        if a <= t < b: cues.append((t, 'chime'))
    return [f'{mmss(t)} {c}' for t, c in sorted(cues)]


# Stills
SHOTS = HERE / 'storyboard' / 'stills'
times = [str(sc['start'] + SCENE[sc['id']][3]) for sc in TL['scenes']]
subprocess.run(['node', str(HERE / 'shots.js'), str(SHOTS)] + times, cwd=HERE, check=True)
for sc in TL['scenes']:
    t = sc['start'] + SCENE[sc['id']][3]
    png = SHOTS / f't{str(t).zfill(6)}.png'
    jpg = SHOTS / f'{sc["id"]}.jpg'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(png), '-vf', 'scale=960:-1', '-q:v', '4', str(jpg)], check=True)
    png.unlink()

INDUSTRY = [
 ('Banking', 'Branch · mobile · ATM → SD-WAN / MPLS / internet → firewalls, load balancers → core DC, mainframe → hybrid cloud, payments',
  'A routing, capacity or connectivity change degrades payments or digital banking while the network is technically “up”.',
  ['Change policy plus capacity and SLA assessment', 'Behavioural baselines: latency, loss, jitter, utilization', 'ITSM incident → approved network workflow (reroute, rollback)', 'Post-change KPIs compared with baseline', 'Performance, change and incident records for operational-risk review'],
  'Availability, transaction-path latency, site-to-DC latency, loss, jitter, BGP peers, interface errors, SD-WAN tunnels, QoS, circuit capacity',
  '% of critical paths outside approved baseline; % of high-risk changes followed by abnormal behaviour within 30 min'),
 ('Telecommunications', 'Access / 5G / broadband → aggregation → IP/MPLS → backbone → peering and transit → service platforms',
  'Customer-service degradation, oversubscribed links, peering instability, SLA breach, capacity exhaustion.',
  ['Capacity forecasts, SLA engineering, path validation', 'BGP, loss, latency, jitter, utilization, flows', 'NOC incident and controlled traffic engineering', 'Utilization, loss and latency verified after remediation', 'SLA and historical performance evidence'],
  'Availability, BGP stability, latency, loss, jitter, utilization, errors, traffic volume, QoS, capacity headroom, SLA compliance',
  'Capacity-at-risk: critical links forecast to exceed the engineering threshold in the planning horizon'),
 ('Rail and transportation', 'Stations → IP/MPLS / WAN → communications network → operational applications → DC / cloud',
  'Communications degradation compounding an operational disruption. (SevOne is network assurance, not signalling or train-control safety.)',
  ['Capacity and change assessment for operational communications', 'WAN loss, latency, jitter, interface degradation', 'NOC incident → approved network remediation', 'Communications-path recovery validated', 'Network availability and performance history'],
  'Station connectivity, WAN availability, MPLS path health, latency, loss, interface errors, circuit utilization, redundant-path health',
  'Critical communications paths outside baseline'),
 ('Energy and utilities', 'Enterprise IT → network boundary → OT communications → sites, substations, plants',
  'Loss of visibility across operational communications. (Not a replacement for protection relays, SCADA safety controls or OT-security platforms.)',
  ['Approved network changes, capacity and path planning', 'Availability, latency, loss, interface anomalies', 'Controlled NOC / operations escalation', 'Network recovery confirmed after remediation', 'Network service and SLA history'],
  'Control-site connectivity, communications-path availability, redundant-path status, WAN/MPLS latency, loss, capacity, route stability',
  'Critical communications links outside normal baseline'),
 ('Government and critical services', 'Citizen services → agencies, campuses, remote offices → DC → hybrid cloud',
  'Critical-service availability, digital-service disruption, remote-site failure, cloud connectivity, accountability.',
  ['Change windows, architecture standards, capacity assessment', 'Network, SLA and baseline monitoring', 'Automated incident routing and controlled response', 'Service and network recovery confirmation', 'Historical SLA and performance evidence'],
  'Latency, loss, availability, capacity, interface health, routing; MTTD, MTTA, MTTR; recurring incidents',
  'Network observability coverage = critical assets monitored ÷ critical assets in scope'),
 ('AI and data infrastructure', 'Data sources → network fabric → storage + GPUs → AI platform → model and inference services',
  'Congestion starving GPU and data workloads; expensive compute waiting on data; change-induced degradation.',
  ['Capacity and network architecture planning', 'Fabric utilization, loss, latency, flow anomalies', 'Incident and automation workflow', 'Traffic and performance normalization confirmed', 'Historical network-performance correlation'],
  'Fabric utilization, loss, latency, saturation, throughput, east-west traffic, storage-network throughput, cloud connectivity, headroom',
  'Idle compute attributable to network constraints'),
]
CTRL = ['Preventive', 'Detective', 'Corrective', 'Verification', 'Evidence']

RUN = [('0–5', 'The Network Is Becoming Agentic', 'Establish urgency'), ('5–12', 'When AI Operates at Machine Speed', 'Introduce business risk'),
       ('12–19', 'Why Traditional Monitoring Isn’t Enough', 'Establish need for assurance'), ('19–27', 'SevOne 9.0 Observability Foundation', 'Introduce technology'),
       ('27–35', 'Agentic Network Assurance', 'Observe, baseline, detect, anticipate'), ('35–47', 'Live BGP Agentic AI Scenario', 'Prove value (play this film, then go live)'),
       ('47–52', 'Three Control Planes', 'Establish architecture and boundaries'), ('52–55', 'Closed-Loop Network Assurance', 'Show future operating model'),
       ('55–58', 'Business Value', 'Translate technical capabilities into outcomes'), ('58–60', 'Call to Action', 'Drive assessment / PoV')]
ASSESS = ['Current network visibility', 'AI/automation use cases', 'Critical network dependencies', 'Existing telemetry coverage', 'BGP/WAN/SD-WAN visibility',
          'Baseline and anomaly-detection maturity', 'Change-impact validation', 'Incident and remediation workflows', 'Observability gaps', 'Opportunities for closed-loop assurance']

# ---------------- Markdown
md = [f'# Production storyboard: {TL["title"]}', '',
      f'IBM SevOne · Continuous network assurance in the age of agentic AI · **{mmss(TL["duration"])}** · 1920×1080, 30 fps · narrated, subtitled', '',
      '**Single message:** AI agents accelerate change. SevOne provides the independent network observability needed to understand the impact, detect unintended consequences and verify operational outcomes.', '',
      '**Anchor line:** “The AI agent tells you the task was completed. The automation platform tells you the change was applied. SevOne tells you what happened to the network. The business needs all three.”', '',
      '**Audience:** CIO, CISO, VP Infrastructure, network operations, SRE, risk and audit leaders in banking, telecom, rail, energy, government and AI/data infrastructure.', '',
      '## Production notes', '',
      '- **Style:** dark enterprise-cinematic UI, IBM Plex type, one continuous BGP incident (Montréal ↔ Toronto) carried across six industries.',
      '- **Voice:** synthetic narrator (Kokoro-82M `af_heart`, Apache-2.0). Swap in a recorded voice by replacing `narration.wav` with lines at the times below.',
      '- **Music:** fully synthesized (D-minor pad, 96 BPM pulse bass, kick and hats, risers, impacts). Music ducks about 13 dB under each line.',
      '- **Guardrails on screen and in narration:** all values are demo values; gNMI is Public Preview; SevOne observes and provides evidence, it does not execute remediation, govern AI agents, or act as a rail-safety or OT-safety system; no invented ROI.', '',
      '## Scene by scene', '']
for sc in TL['scenes']:
    vis, ost, mood, _ = SCENE[sc['id']]
    lines = [c['text'] for c in NAR if sc['start'] <= c['start'] < sc['end']]
    md += [f'### {mmss(sc["start"])}–{mmss(sc["end"])} · {sc["name"]}', '', f'![{sc["name"]}](stills/{sc["id"]}.jpg)', '',
           f'**Purpose:** {sc["purpose"]}', '', f'**Visuals:** {vis}', '', '**On-screen text:**', ''] + [f'- {o}' for o in ost] + ['',
           '**Narration:**', ''] + [f'> {l}' for l in lines] + ['', f'**Soundtrack:** {mood}' + (f' Cues: {"; ".join(sound_cues(sc))}.' if sound_cues(sc) else ''), '']
md += ['## Appendix A · Industry risk-control matrices', '']
for name, arch, risk, ctrls, kpis, kri in INDUSTRY:
    md += [f'### {name}', '', f'**Architecture:** {arch}', '', f'**Principal risk:** {risk}', '', '| Control | Network assurance example |', '|---|---|'] + \
          [f'| {c} | {x} |' for c, x in zip(CTRL, ctrls)] + ['', f'**KPIs:** {kpis}', '', f'**Executive KRI:** {kri}', '']
md += ['## Appendix B · Universal NPM KPI framework', '',
       '| Family | Example KPIs |', '|---|---|',
       '| Availability | device, interface, path, site, tunnel availability; BGP neighbour state |',
       '| Performance | latency, loss, jitter, throughput, utilization, errors, discards, QoS |',
       '| Traffic | NetFlow/IPFIX volumes, top applications and conversations, traffic shifts, unexpected flows |',
       '| Capacity | peak and 95th-percentile utilization, headroom, growth, saturation risk |',
       '| Service quality | SLA compliance, critical-path health, site and service availability |',
       '| Change and coverage | change outcome assurance rate, observability coverage |', '',
       '**Change outcome assurance rate** = changes with a validated post-change network state ÷ changes requiring network validation × 100.', '',
       '**Network observability coverage** = critical network assets monitored ÷ critical network assets in scope × 100.', '',
       '## Appendix C · Incident automation (L1 / L2 / L3)', '',
       '| Stage | What happens | Who acts |', '|---|---|---|',
       '| Detect | SevOne raises a condition from baseline deviation, thresholds or flow anomalies | Automatic |',
       '| Ticket | ServiceNow incident created with CI (CMDB-synced), priority, related change and evidence | Automatic (integration) |',
       '| Route | NetOps paged, DevSecOps informed of AI-initiated change, service owner notified | Automatic (integration) |',
       '| L1 | Triage and evidence pack | Automated |', '| L2 | Diagnosis and rollback proposal | Automated |',
       '| L3 | Rollback or risky change approved by a named engineer; executed by the automation platform | **Human** |',
       '| Verify | SevOne re-measures against baseline; ticket closes only after recovery is confirmed | Automatic |', '',
       '## Appendix D · Measuring TCO and OPEX', '',
       'Do not show invented percentages. Baseline six cost pools, run a proof of value, measure the delta:', '',
       '1. **Tooling:** NPM licences + infrastructure + maintenance + support', '2. **Monitoring administration:** engineer hours × loaded labour cost',
       '3. **Incident investigation:** incidents × engineers × hours × labour cost', '4. **Reporting and SLA effort:** manual reporting hours × labour cost',
       '5. **CMDB and device onboarding:** device changes × manual effort', '6. **Avoidable outage and degradation cost:** only where customer data supports it', '',
       '**Annual addressable OPEX** = tooling + administration + incident effort + reporting + onboarding. Compare the current-state baseline with the measured PoV state.', '',
       '## Appendix E · 60-minute webinar run of show', '', '| Time (min) | Topic | Purpose |', '|---|---|---|'] + [f'| {a} | {b} | {c} |' for a, b, c in RUN] + ['',
       'Play this film at the start of the 35–47 minute block (Live BGP Agentic AI Scenario), then switch to the live SevOne demonstration.', '',
       '## Appendix F · Call to action: Agentic Network Readiness & Observability Assessment', ''] + [f'{i + 1}. {a}' for i, a in enumerate(ASSESS)] + ['',
       '**Closing line:** “In the age of Agentic AI, autonomy without observability is risk. The future isn’t just autonomous networking. It’s autonomous networking with continuous assurance.”', '']
(OUT / 'STORYBOARD.md').write_text('\n'.join(md))

# ---------------- HTML → PDF
e = html.escape
rows = ''
for sc in TL['scenes']:
    vis, ost, mood, _ = SCENE[sc['id']]
    lines = [c['text'] for c in NAR if sc['start'] <= c['start'] < sc['end']]
    cues = sound_cues(sc)
    rows += f'''<section class="scene"><div class="hd"><span class="tm">{mmss(sc['start'])}–{mmss(sc['end'])}</span><h3>{e(sc['name'])}</h3><span class="pp">{e(sc['purpose'])}</span></div>
<div class="grid"><img src="stills/{sc['id']}.jpg" alt="{e(sc['name'])}"><div>
<h4>Visuals</h4><p>{e(vis)}</p><h4>On-screen text</h4><ul>{''.join(f'<li>{e(o)}</li>' for o in ost)}</ul></div></div>
<div class="grid2"><div><h4>Narration</h4>{''.join(f'<p class="vo">{e(l)}</p>' for l in lines)}</div><div><h4>Soundtrack</h4><p>{e(mood)}</p>{('<p class="cues">' + '<br>'.join(e(c) for c in cues) + '</p>') if cues else ''}</div></div></section>'''
ind = ''.join(f'''<section class="ind"><h3>{e(n)}</h3><p><b>Architecture:</b> {e(a)}</p><p><b>Principal risk:</b> {e(r)}</p>
<table>{''.join(f'<tr><th>{c}</th><td>{e(x)}</td></tr>' for c, x in zip(CTRL, ctrls))}</table><p><b>KPIs:</b> {e(k)}</p><p><b>Executive KRI:</b> {e(kr)}</p></section>''' for n, a, r, ctrls, k, kr in INDUSTRY)
run = ''.join(f'<tr><td>{a}</td><td>{e(b)}</td><td>{e(c)}</td></tr>' for a, b, c in RUN)
doc = f'''<!doctype html><html><head><meta charset="utf-8"><title>SevOne Assurance Storyboard</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono&display=swap" rel="stylesheet">
<style>
@page {{ size: A4 landscape; margin: 12mm; }}
body {{ font-family: 'IBM Plex Sans', Arial, sans-serif; color: #161616; font-size: 10.5px; line-height: 1.4; margin: 0; }}
h1 {{ font-size: 28px; margin: 0 0 6px; color: #0f62fe; }} h2 {{ font-size: 20px; color: #0f62fe; margin: 18px 0 8px; break-before: page; }}
h3 {{ font-size: 15px; margin: 0; }} h4 {{ font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: .14em; text-transform: uppercase; color: #0f62fe; margin: 8px 0 3px; }}
.cover p {{ font-size: 13px; max-width: 980px; }} .tag {{ color: #6f6f6f; }}
.scene {{ break-inside: avoid; border: 1px solid #e0e0e0; border-radius: 8px; padding: 8px 12px; margin: 0 0 8px; }}
.hd {{ display: flex; gap: 12px; align-items: baseline; }} .tm {{ font-family: 'IBM Plex Mono', monospace; color: #0f62fe; font-weight: 600; }} .pp {{ color: #6f6f6f; margin-left: auto; }}
.grid {{ display: grid; grid-template-columns: 330px 1fr; gap: 14px; margin-top: 6px; }} .grid img {{ width: 330px; border-radius: 6px; }}
.grid2 {{ display: grid; grid-template-columns: 1.4fr 1fr; gap: 14px; }} .vo {{ margin: 2px 0; font-style: italic; }} .cues {{ font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: #525252; }}
ul {{ margin: 0; padding-left: 16px; }} table {{ border-collapse: collapse; width: 100%; margin: 6px 0; }} th, td {{ border: 1px solid #e0e0e0; padding: 4px 8px; text-align: left; vertical-align: top; }}
th {{ background: #edf5ff; width: 120px; }} .ind {{ break-inside: avoid; margin-bottom: 12px; }}
</style></head><body>
<div class="cover"><h1>{e(TL['title'])}</h1><p class="tag">Production storyboard · IBM SevOne · Continuous network assurance in the age of agentic AI · {mmss(TL['duration'])} · 1920×1080 · narrated and subtitled</p>
<p><b>Single message:</b> AI agents accelerate change. SevOne provides the independent network observability needed to understand the impact, detect unintended consequences and verify operational outcomes.</p>
<p><b>Anchor line:</b> “The AI agent tells you the task was completed. The automation platform tells you the change was applied. SevOne tells you what happened to the network. The business needs all three.”</p>
<p><b>Guardrails:</b> all values are demo values; gNMI is Public Preview; SevOne observes and provides evidence — it does not execute remediation, govern AI agents, or act as a rail-safety or OT-safety system; no invented ROI.</p></div>
<h2>Scene by scene</h2>{rows}
<h2>Appendix A · Industry risk-control matrices</h2>{ind}
<h2>Appendix B–F · KPIs, incident automation, TCO, run of show, assessment</h2>
<h4>Universal NPM KPI families</h4><p>Availability · Performance · Traffic · Capacity · Service quality · Change and coverage. <b>Change outcome assurance rate</b> = validated post-change states ÷ changes requiring validation × 100. <b>Network observability coverage</b> = critical assets monitored ÷ critical assets in scope × 100.</p>
<h4>Incident automation</h4><p>Detect (SevOne) → ServiceNow incident with CMDB CI and evidence → route to NetOps / DevSecOps → L1 triage (automated) → L2 diagnosis and rollback proposal (automated) → L3 approval by a named engineer (human) → automation executes → SevOne verifies against baseline → ticket closes.</p>
<h4>TCO and OPEX method</h4><p>Baseline six cost pools — tooling, administration, incident investigation, reporting/SLA, CMDB onboarding, avoidable outage cost (only with customer data) — run a proof of value, measure the delta, build the business case. No unvalidated percentages.</p>
<h4>60-minute run of show</h4><table><tr><th>Time (min)</th><th style="width:auto">Topic</th><th style="width:auto">Purpose</th></tr>{run}</table>
<h4>Agentic Network Readiness &amp; Observability Assessment</h4><ol>{''.join(f'<li>{e(a)}</li>' for a in ASSESS)}</ol>
<p><b>Closing line:</b> “In the age of Agentic AI, autonomy without observability is risk. The future isn’t just autonomous networking. It’s autonomous networking with continuous assurance.”</p>
</body></html>'''
(OUT / 'storyboard.html').write_text(doc)
subprocess.run(['node', '-e', f'''const {{ chromium }} = require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage();await p.goto('file://{OUT / "storyboard.html"}',{{waitUntil:'networkidle'}});await p.evaluate(()=>document.fonts.ready);await p.pdf({{path:'{OUT / "storyboard.pdf"}',format:'A4',landscape:true,printBackground:true,margin:{{top:'12mm',bottom:'12mm',left:'12mm',right:'12mm'}}}});await b.close();}})();'''], check=True)
print('wrote storyboard/STORYBOARD.md, storyboard.html, storyboard.pdf and', len(TL['scenes']), 'stills')
