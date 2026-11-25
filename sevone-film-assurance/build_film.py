"""Builds film.html for the assurance film from the shared film engine and timeline.json.

    python3 build_film.py ../sevone-film-part2/film.html

The engine (canvas background, animation primitives, player, subtitles, render mode) is
reused from the earlier editions; the scenes, data and scene animations are defined here.
After building, run narration.py to inject the narration cues.
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TL = json.loads((HERE / 'timeline.json').read_text())
src = Path(sys.argv[1]).read_text()


def cut(a, b):
    i = src.index(a); return src[i:src.index(b, i)]


head = src[:src.index('  <!-- S0 · Cold open -->')]
tail_markup = src[src.index('  </div>\n  <div id="hud">'):src.index('<script>')]
script_head = src[src.index('<script>'):src.index('/* ---------- Build dynamic content ---------- */')]
engine = cut('/* ---------- Animation engine ---------- */', 'const custom = {')
s2s3 = cut('  s2(lt) {', '  s4(lt) {')
rest = src[src.index('/* Background canvas'):]
SC = {s['id']: s for s in TL['scenes']}


def sec(i):
    s = SC[f's{i}']; return f'<section class="scene" id="s{i}" data-start="{s["start"]}" data-end="{s["end"]}">'


CSS = r"""
/* ---------- Assurance film ---------- */
.ind-grid { position: absolute; left: 96px; right: 96px; top: 270px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 22px; }
.ind { padding: 22px 24px; height: 250px; box-sizing: border-box; transition: none; }
.ind .k { font-family: var(--mono); font-size: 15px; letter-spacing: .22em; color: var(--cyan); }
.ind .v { font-size: 26px; font-weight: 600; margin-top: 10px; line-height: 1.2; }
.ind .s { font-size: 17px; color: var(--dim); margin-top: 10px; line-height: 1.4; }
.ind.dim { opacity: .38; }
.ind.act { border-color: var(--cyan); box-shadow: 0 0 40px rgba(51,177,255,.25); background: rgba(20,36,66,.92); }
.ind .path { font-family: var(--mono); font-size: 14px; color: #9fb4da; margin-top: 10px; line-height: 1.45; }
.ind .kpis { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.ind .kpis span { font-family: var(--mono); font-size: 13px; padding: 3px 8px; border-radius: 6px; border: 1px solid var(--line-2); color: #cfe0ff; }
.ind .note { font-family: var(--mono); font-size: 13px; color: var(--yellow); margin-top: 8px; }
.ind-full { position: absolute; left: 96px; right: 96px; top: 270px; height: 600px; display: grid; grid-template-columns: 1.15fr 1fr; gap: 26px; }
.ind-full .panel { padding: 28px 32px; }
.ind-full .big { font-size: 56px; }
.envchips { position: absolute; left: 96px; right: 96px; bottom: 150px; display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; }
.envchips .chip { font-family: var(--mono); font-size: 16px; padding: 7px 14px; }

.chain { position: absolute; left: 96px; right: 96px; display: flex; align-items: stretch; gap: 0; }
.chain .node { flex: 1; padding: 20px 20px; box-sizing: border-box; }
.chain .node .k { font-family: var(--mono); font-size: 13px; letter-spacing: .2em; color: var(--dim); }
.chain .node .v { font-size: 24px; font-weight: 600; margin-top: 8px; line-height: 1.2; }
.chain .node .s { font-size: 16px; color: var(--dim); margin-top: 6px; line-height: 1.35; }
.chain .arr { width: 44px; display: grid; place-items: center; color: var(--blue); font-size: 30px; }
.chain .node.hot { border-color: var(--cyan); box-shadow: 0 0 34px rgba(51,177,255,.3); }
.prompt { position: absolute; left: 96px; top: 250px; width: 1728px; padding: 26px 30px; box-sizing: border-box; }
.prompt .k { font-family: var(--mono); font-size: 14px; letter-spacing: .2em; color: var(--dim); }
.prompt .pq { font-size: 30px; margin-top: 10px; line-height: 1.35; }
.prompt .a { font-family: var(--mono); font-size: 19px; color: #cfe0ff; margin-top: 16px; line-height: 1.55; }

.console { position: absolute; left: 96px; top: 250px; width: 1080px; height: 560px; padding: 26px 32px; box-sizing: border-box; background: rgba(6,10,20,.92); font-family: var(--mono); font-size: 22px; line-height: 1.7; color: #cfe0ff; }
.console .ok { color: var(--green); } .console .dimc { color: var(--faint); }
#succ3 { position: absolute; left: 1210px; top: 250px; width: 614px; height: 560px; box-sizing: border-box; padding: 40px 36px; border-color: rgba(66,190,101,.7); background: rgba(8,40,22,.82); display: flex; flex-direction: column; justify-content: center; }
#succ3 .v { font-size: 52px; font-weight: 700; color: var(--green); line-height: 1.1; }
#succ3 .s { font-family: var(--mono); font-size: 19px; color: #b9f0c9; margin-top: 22px; line-height: 1.7; }
#q3 { position: absolute; left: 0; right: 0; bottom: 120px; text-align: center; font-size: 60px; font-weight: 600; letter-spacing: -0.02em; }

.mtiles { position: absolute; left: 96px; right: 96px; top: 250px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.mt { padding: 18px 24px; }
.mt .k { font-family: var(--mono); font-size: 13px; letter-spacing: .2em; color: var(--dim); text-transform: uppercase; }
.mt .row { display: flex; align-items: baseline; gap: 14px; margin-top: 6px; font-family: var(--mono); }
.mt .mb { font-size: 24px; color: var(--dim); white-space: nowrap; } .mt .ar { font-size: 22px; color: var(--faint); }
.mt .ma { font-size: 40px; font-weight: 500; white-space: nowrap; }
#chart4, #chart9 { position: absolute; left: 96px; top: 430px; width: 1060px; height: 450px; padding: 18px 22px; box-sizing: border-box; }
#split4 { position: absolute; left: 1186px; top: 430px; width: 638px; height: 450px; padding: 18px 24px; box-sizing: border-box; }
.sp { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; padding: 13px 0; border-bottom: 1px solid var(--line); font-size: 19px; }
.sp .l { color: #b9f0c9; } .sp .r { color: #ffb3b8; }
.sp.h { font-family: var(--mono); font-size: 13px; letter-spacing: .18em; color: var(--dim); text-transform: uppercase; }
#dev4 { position: absolute; left: 600px; top: 70px; padding: 10px 16px; border-radius: 10px; font-family: var(--mono); font-size: 16px; color: #fff; background: rgba(218,30,40,.85); box-shadow: 0 0 30px rgba(250,77,86,.5); }

#tl5 { position: absolute; left: 96px; right: 96px; top: 300px; height: 330px; }
.tnode { position: absolute; top: 120px; width: 250px; margin-left: -125px; text-align: center; }
.tnode .dot { width: 26px; height: 26px; border-radius: 50%; margin: 0 auto; background: var(--line-2); border: 3px solid #04060d; }
.tnode .tm { font-family: var(--mono); font-size: 20px; margin-top: 16px; color: #eef2fa; }
.tnode .tx { font-size: 19px; color: var(--dim); margin-top: 6px; line-height: 1.3; }
.tnode.on .dot { background: var(--yellow); } .tnode.hit .dot { background: var(--red); box-shadow: 0 0 0 10px rgba(250,77,86,.2); }
.tnode.gone { opacity: .35; } .tnode.gone .tx { text-decoration: line-through; }
#det5 { position: absolute; top: 20px; padding: 10px 18px; border-radius: 10px; font-family: var(--mono); font-size: 18px; color: #06210f; background: var(--green); transform: translateX(-50%); white-space: nowrap; }
.evid { position: absolute; left: 96px; right: 96px; top: 690px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
.evid .panel { padding: 16px 20px; } .evid .k { font-family: var(--mono); font-size: 13px; letter-spacing: .18em; color: var(--cyan); }
.evid .v { font-size: 19px; margin-top: 6px; line-height: 1.35; }

#rca7 { position: absolute; left: 96px; top: 250px; width: 980px; }
.rca { display: grid; grid-template-columns: 150px 1fr; gap: 18px; padding: 15px 22px; margin-bottom: 12px; align-items: center; }
.rca .k { font-family: var(--mono); font-size: 15px; letter-spacing: .2em; color: var(--cyan); }
.rca .v { font-size: 21px; line-height: 1.35; }
#br7 { position: absolute; left: 1120px; top: 250px; width: 704px; padding: 18px 24px; box-sizing: border-box; }
.brn { padding: 12px 18px; border-radius: 12px; border: 1px solid var(--line-2); font-size: 20px; margin-top: 10px; display: flex; justify-content: space-between; }
.brn .m { font-family: var(--mono); font-size: 14px; color: var(--dim); }
.brn.hot { border-color: rgba(250,77,86,.8); background: rgba(70,12,20,.7); } .brn.hot .m { color: #ffb3b8; }
.brd { text-align: center; color: var(--faint); font-size: 18px; line-height: 1; margin-top: 8px; }
#qs7 { position: absolute; left: 1120px; top: 760px; width: 704px; display: flex; flex-wrap: wrap; gap: 10px; }
#qs7 .chip { font-size: 16px; padding: 6px 12px; } #qs7 .chip.done { border-color: var(--green); color: #b9f0c9; }

#tick8 { position: absolute; left: 96px; top: 520px; width: 860px; padding: 0 0 16px; overflow: hidden; box-sizing: border-box; }
#tick8 .tbar { padding: 12px 22px; background: rgba(41,61,101,.85); display: flex; gap: 14px; font-size: 18px; font-weight: 600; }
#tick8 .tbar .n { font-family: var(--mono); color: var(--cyan); font-weight: 400; }
#tick8 .tbar .st { margin-left: auto; font-family: var(--mono); font-size: 13px; letter-spacing: .12em; color: #b9f0c9; background: rgba(66,190,101,.16); padding: 3px 10px; border-radius: 6px; font-weight: 400; }
#tick8 .f { display: grid; grid-template-columns: 210px 1fr; gap: 12px; padding: 8px 22px; font-size: 18px; }
#tick8 .f .k { font-family: var(--mono); font-size: 13px; letter-spacing: .14em; color: var(--dim); text-transform: uppercase; padding-top: 3px; }
#lv8 { position: absolute; left: 990px; top: 520px; width: 834px; display: flex; flex-direction: column; gap: 14px; }
#lv8 .tier { padding: 14px 22px; } #lv8 .tier .v { font-size: 21px; } #lv8 .tier .s { font-size: 16px; }

.loop { position: absolute; left: 1186px; top: 430px; width: 638px; height: 450px; padding: 24px 28px; box-sizing: border-box; }
.loop .st { display: flex; align-items: center; gap: 14px; padding: 12px 0; font-family: var(--mono); font-size: 22px; letter-spacing: .14em; color: var(--faint); border-bottom: 1px solid var(--line); }
.loop .st .dot { width: 14px; height: 14px; border-radius: 50%; background: var(--line-2); }
.loop .st.on { color: #eef2fa; } .loop .st.on .dot { background: var(--green); box-shadow: 0 0 14px rgba(66,190,101,.7); }
.loop .res { margin-top: 18px; font-size: 22px; color: #b9f0c9; }

.rctab { position: absolute; left: 96px; right: 96px; top: 250px; }
.rcr { display: grid; grid-template-columns: 190px 360px 1fr 470px; gap: 18px; padding: 14px 20px; border-bottom: 1px solid var(--line); font-size: 18px; align-items: start; }
.rcr.h { font-family: var(--mono); font-size: 13px; letter-spacing: .18em; color: var(--dim); text-transform: uppercase; }
.rcr .L { font-family: var(--mono); font-size: 16px; letter-spacing: .12em; color: var(--cyan); text-transform: uppercase; padding-top: 2px; }
.rcr .q { color: #eef2fa; } .rcr .sv { color: #cfe0ff; } .rcr .adj { color: var(--dim); }
.rcfoot { position: absolute; left: 96px; right: 96px; top: 800px; padding: 14px 20px; font-size: 18px; color: #dfe6f5; border-left: 4px solid var(--yellow); background: rgba(60,48,10,.45); border-radius: 8px; }

.kgrid { position: absolute; left: 96px; top: 250px; width: 1100px; display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.kt { padding: 14px 22px; display: flex; justify-content: space-between; align-items: baseline; }
.kt .k { font-size: 18px; color: #dfe6f5; } .kt .v { font-family: var(--mono); font-size: 30px; }
#coar { position: absolute; left: 1230px; top: 250px; width: 594px; padding: 24px 28px; box-sizing: border-box; border-color: rgba(51,177,255,.6); }
#coar .k { font-family: var(--mono); font-size: 14px; letter-spacing: .2em; color: var(--cyan); }
#coar .f { font-size: 19px; margin-top: 14px; line-height: 1.5; color: #dfe6f5; }
#coar .f .ln { border-top: 2px solid #8b97b3; margin: 6px 0; }
#coar .v { font-family: var(--mono); font-size: 72px; color: var(--green); margin-top: 14px; }
#fw11 { position: absolute; left: 1230px; top: 640px; width: 594px; padding: 18px 24px; box-sizing: border-box; }
#fw11 .k { font-family: var(--mono); font-size: 13px; letter-spacing: .2em; color: var(--dim); }
#fw11 .chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; } #fw11 .chip { font-size: 15px; padding: 5px 12px; }

.tco { position: absolute; top: 250px; width: 846px; height: 380px; padding: 22px 28px; box-sizing: border-box; }
.tco .k { font-family: var(--mono); font-size: 15px; letter-spacing: .2em; }
.tco ul { margin: 12px 0 0; padding-left: 24px; font-size: 21px; line-height: 1.6; color: #dfe6f5; }
.tco .tot { position: absolute; left: 28px; right: 28px; bottom: 18px; border-top: 1px solid var(--line-2); padding-top: 10px; font-family: var(--mono); font-size: 18px; letter-spacing: .12em; }
.pools { position: absolute; left: 96px; right: 96px; top: 660px; display: grid; grid-template-columns: repeat(6, 1fr); gap: 14px; }
.pools .panel { padding: 14px 16px; } .pools .k { font-family: var(--mono); font-size: 13px; letter-spacing: .16em; color: var(--cyan); }
.pools .v { font-size: 16px; margin-top: 6px; line-height: 1.35; color: #dfe6f5; }
.flow12 { position: absolute; left: 96px; right: 96px; top: 820px; display: flex; justify-content: center; gap: 18px; align-items: center; font-family: var(--mono); font-size: 20px; letter-spacing: .08em; }
.flow12 span.b { padding: 10px 18px; border-radius: 10px; border: 1px solid var(--line-2); background: rgba(16,24,44,.85); }
.flow12 span.g { border-color: var(--green); color: #b9f0c9; }

.truth { position: absolute; left: 200px; right: 200px; display: grid; grid-template-columns: 360px 1fr; gap: 30px; align-items: baseline; }
.truth .who { font-family: var(--mono); font-size: 20px; letter-spacing: .2em; text-transform: uppercase; color: var(--dim); text-align: right; }
.truth .say { font-size: 48px; font-weight: 400; }
#s14 .qq { font-size: 64px; font-weight: 600; letter-spacing: -0.02em; line-height: 1.22; max-width: 1560px; }
.assess { position: absolute; left: 96px; right: 96px; top: 330px; display: grid; grid-template-columns: 1fr 1fr; gap: 14px 30px; }
.as { display: grid; grid-template-columns: 54px 1fr; gap: 16px; align-items: center; padding: 12px 20px; }
.as .n { width: 44px; height: 44px; border-radius: 50%; background: var(--blue); display: grid; place-items: center; font-family: var(--mono); font-size: 18px; font-weight: 600; color: #fff; }
.as .t { font-size: 23px; }
.asout { position: absolute; left: 96px; right: 96px; top: 800px; text-align: center; font-size: 22px; color: #dfe6f5; }
#steps span { white-space: nowrap; font-size: 12px; padding: 7px 11px; letter-spacing: .14em; }
#s16 .a, #s16 .b, #s16 .c { font-size: 62px; letter-spacing: -0.02em; line-height: 1.2; }
#s16 .a { font-weight: 600; } #s16 .b { font-weight: 300; margin-top: 30px; } #s16 .c { font-weight: 600; margin-top: 6px; }
#s16 .end .brand { font-size: 150px; font-weight: 600; letter-spacing: -0.05em; }
#s16 .end .brand .ibm { font-weight: 300; color: #c9d3e8; margin-right: .18em; }
#s16 .end .tag2 { font-family: var(--mono); font-size: 24px; letter-spacing: .28em; text-transform: uppercase; color: var(--dim); margin-top: 34px; }
#s16 .disc { position: absolute; left: 0; right: 0; bottom: 60px; text-align: center; font-family: var(--mono); font-size: 14px; color: var(--faint); letter-spacing: .06em; }
"""
head = head.replace('/* Subtitles (CC) */', CSS + '\n/* Subtitles (CC) */')
head = head.replace('<title>SevOne Incident Part 2</title>', '<title>SevOne Agentic Assurance</title>')


def stephead(num, uc, title):
    return f'<div class="stephead"><div class="num" data-in="0.2">{num}<span class="uc">{uc}</span></div><div class="t" data-in="0.5" data-dur="0.8">{title}</div></div>'


INDS = [
    ('BANKING', 'Payments and digital channels', 'Branch · ATM · mobile → SD-WAN / MPLS → firewalls · load balancers → DC and cloud → payments',
     'Transaction latency, channel availability, operational-resilience exposure', ['latency', 'loss', 'WAN util.', 'interface errors', 'availability'], ''),
    ('TELECOM', 'Customer services and SLAs', 'Access → IP/MPLS core → backbone → peering and transit',
     'SLA penalties, service degradation, avoidable NOC escalations', ['loss', 'jitter', 'utilization', 'BGP peer state', 'SLA'], ''),
    ('RAIL', 'Operations communications', 'Stations · depots → WAN → operations-control systems → DC',
     'Communications degradation cascading into operational disruption', ['availability', 'latency', 'link errors', 'path redundancy'], 'Communications assurance, not a train-safety system'),
    ('ENERGY', 'Grid and site communications', 'Substations · sites → WAN → control centre → DC and cloud',
     'Loss of visibility across operational communications', ['availability', 'latency', 'utilization', 'redundancy'], 'Monitoring stays separate from safety and OT control'),
    ('GOVERNMENT', 'Citizen and critical services', 'Citizen portal → government DC → cloud → agency networks',
     'Citizen-service outages, emergency-service delays, accountability', ['availability', 'response time', 'SLA', 'capacity'], ''),
    ('AI & DATA', 'GPU clusters and data pipelines', 'Data sources → fabric → GPU cluster ↔ storage → cloud',
     'Expensive GPUs idle while data paths congest', ['east-west throughput', 'drops', 'latency', 'utilization'], 'AI infrastructure is also network infrastructure'),
]

ind_cards = ''.join(f'''<div data-in="{0.6 + i * 0.25:.2f}" data-fx="up"><div class="panel ind dim" id="ind{i}"><div class="k">{k}</div><div class="v">{v}</div><div class="path">{p}</div><div class="s"><b style="color:#ffb3b8;font-weight:600">Risk ·</b> {r}</div><div class="kpis">{''.join(f'<span>{x}</span>' for x in kp)}</div>{f'<div class="note">{n}</div>' if n else ''}</div></div>''' for i, (k, v, p, r, kp, n) in enumerate(INDS))

s1_tiles = ''.join(f'<div data-in="{1.4 + i * 0.35:.2f}" data-fx="up"><div class="panel ind" style="height:200px"><div class="k">{k}</div><div class="v">{v}</div><div class="s">{r}</div></div></div>' for i, (k, v, p, r, kp, n) in enumerate(INDS))

RCROWS = [
    ('Preventive', 'Should this change happen?', 'Baseline and capacity evidence informs pre-change decisions', 'IAM · PAM · change policy · CAB · agent guardrails'),
    ('Detective', 'Is something going wrong?', 'Metrics, flows, telemetry, baselines, thresholds, anomalies, synthetics', 'SIEM · ITDR · application and OT monitoring'),
    ('Diagnostic', 'What happened, and where?', 'Interface, device, path and flow context', 'AIOps · topology · tracing · logs'),
    ('Corrective', 'What should happen now?', 'Events and alerts feed downstream response', 'ITSM · SOAR · Ansible · Terraform · runbooks'),
    ('Verification', 'Did remediation work?', 'Re-measure behaviour against baseline and KPIs', 'ITSM closure controls · SRE error budgets'),
    ('Evidence', 'Can we show the outcome?', 'Historical performance, SLA and capacity records', 'CMDB · change records · audit logs · GRC'),
]
rc_rows = ''.join(f'<div class="rcr" data-in="{1.6 + i * 3.2:.1f}" data-fx="left"><div class="L">{a}</div><div class="q">{b}</div><div class="sv">{c}</div><div class="adj">{d}</div></div>' for i, (a, b, c, d) in enumerate(RCROWS))

KPIS = [('Critical services within SLA', '98.7%', 'green'), ('Critical paths within baseline', '94.2%', ''), ('Critical asset observability coverage', '97.8%', ''),
        ('Active network anomalies', '17', ''), ('High-impact anomalies', '2', 'red'), ('Capacity-at-risk circuits', '4', 'yellow'),
        ('Automated changes today', '126', ''), ('Changes followed by anomalies', '3', 'yellow'), ('Verified remediations', '11 / 12', 'green'), ('Network-related MTTR', '21 min', 'cyan')]
k_tiles = ''.join(f'<div class="panel kt" data-in="{1.2 + i * 0.35:.2f}" data-fx="up"><div class="k">{k}</div><div class="v {c}">{v}</div></div>' for i, (k, v, c) in enumerate(KPIS))

ASSESS = ['Current network visibility', 'AI and automation use cases', 'Critical network dependencies', 'Existing telemetry coverage', 'BGP, WAN and SD-WAN visibility',
          'Baseline and anomaly-detection maturity', 'Change-impact validation', 'Incident and remediation workflows', 'Observability gaps', 'Opportunities for closed-loop assurance']
as_items = ''.join(f'<div class="panel as" data-in="{1.5 + i * 1.6:.1f}" data-fx="up"><div class="n">{i + 1}</div><div class="t">{t}</div></div>' for i, t in enumerate(ASSESS))

SCENES = f"""  <!-- S0 · Cold open -->
  {sec(0)}
    <div class="logs" data-in="1.6" data-dur="2" data-fx="fade" id="logs0"></div>
    <div class="center">
      <div class="clock" data-in="0.5" data-dur="0.8">MONDAY · 09:20</div>
      <div class="l1" data-type="AI accelerates operations." data-in="1.8" data-dur="1.4"></div>
      <div class="l2" data-in="4.4" data-dur="0.9">It also accelerates <span class="red">change</span>.</div>
    </div>
  </section>

  <!-- S1 · Critical infrastructure -->
  {sec(1)}
    <div class="stephead" style="top:110px"><div class="eyebrow" data-in="0.3">Critical infrastructure runs on the network</div>
      <div class="h2" style="margin-top:16px;max-width:1700px" data-in="0.7" data-dur="0.8">Every critical service depends on the network, <span class="grad">and on the agents that now change it</span>.</div></div>
    <div class="ind-grid" style="top:330px">{s1_tiles}</div>
    <div class="envchips" style="bottom:130px">{''.join(f'<span class="chip" data-in="{9 + i * 0.3:.1f}" data-fx="up">{c}</span>' for i, c in enumerate(['On-prem data centres', 'Private cloud', 'AWS · Azure', 'WAN · MPLS', 'SD-WAN', 'BGP edge', 'DC fabrics', 'Wi-Fi', 'OT boundary']))}</div>
  </section>

  <!-- S2 · Agentic operations -->
  {sec(2)}
    {stephead('AGENTIC OPERATIONS', 'Human and policy → agent → approved automation → network', 'A routine optimization, <span class="cyan">done the right way</span>.')}
    <div class="panel prompt" data-in="1">
      <div class="k">ENGINEER → AI OPERATIONS AGENT</div>
      <div class="pq">“Optimize connectivity between Montréal and Toronto while maintaining application performance.”</div>
      <div class="a" data-in="10" data-fx="fade">agent ▸ analyzed 30 days of telemetry · proposes BGP local-preference change on 48 edge routers to prefer path B</div>
    </div>
    <div class="chain" style="top:560px">
      <div class="panel node" id="c2n0" data-in="18"><div class="k">01</div><div class="v">Human &amp; policy</div><div class="s">objective, guardrails</div></div><div class="arr" data-in="18.4">→</div>
      <div class="panel node" id="c2n1" data-in="19"><div class="k">02</div><div class="v">AI agent</div><div class="s">analysis, proposal</div></div><div class="arr" data-in="19.4">→</div>
      <div class="panel node" id="c2n2" data-in="20"><div class="k">03</div><div class="v">Change approval</div><div class="s">policy · CAB · ticket</div></div><div class="arr" data-in="20.4">→</div>
      <div class="panel node" id="c2n3" data-in="21"><div class="k">04</div><div class="v">Automation platform</div><div class="s">Ansible · Terraform · controller</div></div><div class="arr" data-in="21.4">→</div>
      <div class="panel node" id="c2n4" data-in="22"><div class="k">05</div><div class="v">Network</div><div class="s">48 edge routers</div></div>
    </div>
    <div class="caption" data-in="25" style="bottom:130px">No magic. <b>Approved, governed change</b>, executed through automation.</div>
  </section>

  <!-- S3 · The change -->
  {sec(3)}
    {stephead('01 — THE CHANGE', 'Technical execution', 'The automation platform reports <span class="green">success</span>.')}
    <div class="panel console" data-in="0.8">
      <div data-in="1.4" data-fx="fade"><span class="dimc">$</span> run playbook bgp-path-optimize.yml --limit edge-mtl-tor</div>
      <div data-in="3.0" data-fx="fade">BGP POLICY UPDATE</div>
      <div data-in="4.0" data-fx="fade">Devices targeted ........ 48</div>
      <div data-in="5.0" data-fx="fade">Configuration applied ... 48</div>
      <div data-in="6.0" data-fx="fade">Errors .................. <span class="ok">0</span></div>
      <div data-in="7.0" data-fx="fade">BGP sessions ............ <span class="ok">ESTABLISHED 96/96</span></div>
      <div data-in="8.0" data-fx="fade">Devices reachable ....... <span class="ok">48/48</span></div>
      <div data-in="9.2" data-fx="fade" style="margin-top:12px">STATUS: <span class="ok">SUCCESS</span></div>
    </div>
    <div class="panel" id="succ3" data-in="10.4" data-dur="0.3" data-fx="scale"><div class="v">✓ CHANGE<br>SUCCESSFUL</div><div class="s">no configuration errors<br>no devices down<br>BGP established</div></div>
    <div id="q3" data-in="23.6" data-dur="0.4" data-fx="scale">But did the <span class="red">business outcome</span> succeed?</div>
  </section>

  <!-- S4 · SevOne sees something different -->
  {sec(4)}
    {stephead('02 — DETECT', 'Baseline deviation · independent telemetry', 'The change succeeded. <span class="red">The outcome didn’t.</span>')}
    <div class="mtiles">
      <div class="panel mt" data-in="6"><div class="k">WAN utilization · MTL ↔ TOR</div><div class="row"><span class="mb">47%</span><span class="ar">→</span><span class="ma red" data-count="82" data-suf="%" data-cin="9" data-cdur="3">0</span></div></div>
      <div class="panel mt" data-in="6.3"><div class="k">Latency · payments path</div><div class="row"><span class="mb">18 ms</span><span class="ar">→</span><span class="ma red" data-count="63" data-suf=" ms" data-cin="10" data-cdur="3">0</span></div></div>
      <div class="panel mt" data-in="6.6"><div class="k">Packet loss</div><div class="row"><span class="mb">0.1%</span><span class="ar">→</span><span class="ma red" data-count="2.1" data-dec="1" data-suf="%" data-cin="11" data-cdur="3">0</span></div></div>
      <div class="panel mt" data-in="6.9"><div class="k">BGP sessions</div><div class="row"><span class="ma green" style="font-size:34px">ESTABLISHED</span></div></div>
    </div>
    <div class="panel" id="chart4" data-in="1"><h4>WAN utilization · Toronto edge · % · learned baseline band</h4><svg id="c4" width="1060" height="400" style="position:absolute;left:0;top:40px"></svg>
      <div id="dev4" data-in="10.2" data-dur="0.3" data-fx="scale">DEVIATION FROM BASELINE · 09:23</div></div>
    <div class="panel" id="split4" data-in="14">
      <div class="sp h"><div>Automation says</div><div>Network assurance says</div></div>
      <div class="sp" data-in="15" data-fx="left"><div class="l">✓ change applied</div><div class="r">⚠ behaviour abnormal</div></div>
      <div class="sp" data-in="16.2" data-fx="left"><div class="l">✓ BGP established</div><div class="r">⚠ traffic shifted</div></div>
      <div class="sp" data-in="17.4" data-fx="left"><div class="l">✓ devices operational</div><div class="r">⚠ latency rising</div></div>
      <div class="sp" data-in="18.6" data-fx="left" style="border:0"><div class="l">✓ zero errors</div><div class="r">⚠ service risk emerging</div></div>
    </div>
    <div class="foot" data-in="4" style="bottom:110px">Demo scenario values · telemetry via SNMP, flow and gNMI streaming (gNMI in Public Preview)</div>
  </section>

  <!-- S5 · Before it becomes an incident -->
  {sec(5)}
    {stephead('02 — DETECT', 'Degradation, not failure', 'Don’t wait for DOWN. <span class="cyan">Detect while services are still UP.</span>')}
    <div id="tl5"><svg id="tl5svg" width="1728" height="330" style="position:absolute;left:0;top:0"></svg><div id="tl5nodes"></div><div id="det5">SEVONE DETECTS · 09:24</div></div>
    <div class="evid">
      <div class="panel" data-in="16"><div class="k">BASELINES</div><div class="v">learned per path, per hour</div></div>
      <div class="panel" data-in="16.4"><div class="k">FLOW</div><div class="v">NetFlow · IPFIX: who moved where</div></div>
      <div class="panel" data-in="16.8"><div class="k">TELEMETRY</div><div class="v">SNMP · gNMI streaming (Public Preview)</div></div>
      <div class="panel" data-in="17.2"><div class="k">SYNTHETICS</div><div class="v">service-path tests from the user’s view</div></div>
    </div>
  </section>

  <!-- S6 · Six industries -->
  {sec(6)}
    {stephead('03 — IMPACT', 'Same signal · different business risk', 'One deviation. <span class="cyan">Six business consequences.</span>')}
    <div class="ind-grid">{ind_cards}</div>
  </section>

  <!-- S7 · Root cause -->
  {sec(7)}
    {stephead('04 — DIAGNOSE', 'Root-cause analysis · blast radius', 'From symptom to cause, <span class="cyan">with evidence</span>.')}
    <div id="rca7">
      <div class="panel rca" data-in="3" data-fx="left"><div class="k">SYMPTOM</div><div class="v">Latency 63 ms on the payments path (baseline 18 ms)</div></div>
      <div class="panel rca" data-in="6" data-fx="left"><div class="k">SCOPE</div><div class="v">Toronto edge · 3 WAN circuits · 2 critical services</div></div>
      <div class="panel rca" data-in="9" data-fx="left"><div class="k">PATH</div><div class="v">BGP best path moved from path A (10 Gb/s) to path B (1 Gb/s)</div></div>
      <div class="panel rca" data-in="12" data-fx="left"><div class="k">FLOW</div><div class="v">Top talkers on path B: replication 38% · payments 22%</div></div>
      <div class="panel rca" data-in="15" data-fx="left" style="border-color:rgba(241,194,27,.7)"><div class="k" style="color:var(--yellow)">CHANGE</div><div class="v">09:21 BGP policy update · CHG0052418 · AI-proposed, approved</div></div>
    </div>
    <div class="panel" id="br7" data-in="1.4"><h4>Blast radius</h4>
      <div class="brn" id="b0"><span>BGP path · path B</span><span class="m">route</span></div><div class="brd">↓</div>
      <div class="brn" id="b1"><span>WAN circuit · 1 Gb/s</span><span class="m">82% util.</span></div><div class="brd">↓</div>
      <div class="brn" id="b2"><span>Toronto edge</span><span class="m">queue drops</span></div><div class="brd">↓</div>
      <div class="brn" id="b3"><span>Cloud connectivity</span><span class="m">63 ms</span></div><div class="brd">↓</div>
      <div class="brn" id="b4"><span>Critical banking service</span><span class="m">at risk</span></div>
    </div>
    <div id="qs7">{''.join(f'<span class="chip" id="q7{i}" data-in="{28 + i * 0.6:.1f}" data-fx="up">{q}</span>' for i, q in enumerate(['What changed?', 'Where?', 'What is abnormal?', 'What could be affected?', 'How urgent?']))}</div>
  </section>

  <!-- S8 · Incident automation -->
  {sec(8)}
    {stephead('05 — RESPOND', 'Automatic ticket · routing · L1/L2 automated · L3 human', 'From evidence to action, <span class="cyan">inside your processes</span>.')}
    <div id="pipe" style="top:240px;height:250px"><svg id="pipesvg" width="1728" height="260"></svg>
      <div class="panel stage" style="left:0" data-in="1.4"><div class="n">01</div><div class="h">SevOne</div><div class="s">condition raised</div></div>
      <div class="panel stage" style="left:252px" data-in="2.4"><div class="n">02</div><div class="h">Event</div><div class="s">AIOps · correlation</div></div>
      <div class="panel stage" style="left:504px" data-in="3.4"><div class="n">03</div><div class="h">Ticket</div><div class="s">ServiceNow, auto</div></div>
      <div class="panel stage" style="left:756px" data-in="4.4"><div class="n">04</div><div class="h">Route</div><div class="s">NetOps · DevSecOps</div></div>
      <div class="panel stage auto" style="left:1008px" data-in="5.4"><div class="n">L1</div><div class="h">Triage</div><div class="s">evidence pack</div><span class="tag ok">AUTOMATED</span></div>
      <div class="panel stage auto" style="left:1260px" data-in="6.4"><div class="n">L2</div><div class="h">Propose</div><div class="s">rollback plan</div><span class="tag ok">AUTOMATED</span></div>
      <div class="panel stage human" style="left:1512px" data-in="7.4"><div class="n">L3</div><div class="h">Approve</div><div class="s">engineer decides</div><span class="tag watch">HUMAN</span></div>
    </div>
    <div class="panel" id="tick8" data-in="9">
      <div class="tbar">ServiceNow · Incident <span class="n">INC0051207</span><span class="st">AUTO-CREATED · 7 s</span></div>
      <div class="f" data-in="10" data-fx="fade"><div class="k">Config item</div><div>edge-tor-07 · synced from CMDB</div></div>
      <div class="f" data-in="10.6" data-fx="fade"><div class="k">Business service</div><div>Digital payments · Tier 1</div></div>
      <div class="f" data-in="11.2" data-fx="fade"><div class="k">Priority</div><div><span class="yellow">P2</span> · impact 2 · urgency 1</div></div>
      <div class="f" data-in="11.8" data-fx="fade"><div class="k">Related change</div><div>CHG0052418 · AI-proposed BGP update</div></div>
      <div class="f" data-in="12.4" data-fx="fade"><div class="k">Evidence</div><div>baseline chart · path diff · top flows</div></div>
    </div>
    <div id="lv8">
      <div class="panel tier auto" data-in="20"><div class="k">L1 · automated</div><div class="v">Triage: evidence pack attached, NetOps paged</div></div>
      <div class="panel tier auto" data-in="22"><div class="k">L2 · automated</div><div class="v">Diagnosis confirmed · rollback to path A proposed</div></div>
      <div class="panel tier human" data-in="27"><div class="k">L3 · human in the loop</div><div class="v">✓ Engineer approves the rollback</div><div class="s">automation executes · SevOne observes</div></div>
    </div>
  </section>

  <!-- S9 · Verify -->
  {sec(9)}
    {stephead('06 — VERIFY', 'Close the loop with measurement', 'A job says “done”. <span class="green">The network proves it.</span>')}
    <div class="mtiles">
      <div class="panel mt" data-in="1"><div class="k">WAN utilization</div><div class="row"><span class="mb">82%</span><span class="ar">→</span><span class="ma green" data-count="49" data-suf="%" data-cin="6" data-cdur="3">82%</span></div></div>
      <div class="panel mt" data-in="1.3"><div class="k">Latency</div><div class="row"><span class="mb">63 ms</span><span class="ar">→</span><span class="ma green" data-count="19" data-suf=" ms" data-cin="7" data-cdur="3">63 ms</span></div></div>
      <div class="panel mt" data-in="1.6"><div class="k">Packet loss</div><div class="row"><span class="mb">2.1%</span><span class="ar">→</span><span class="ma green" data-count="0.1" data-dec="1" data-suf="%" data-cin="8" data-cdur="3">2.1%</span></div></div>
      <div class="panel mt" data-in="1.9"><div class="k">Service state</div><div class="row"><span class="ma green" style="font-size:34px" data-in="11">NORMAL</span></div></div>
    </div>
    <div class="panel" id="chart9" data-in="0.6"><h4>WAN utilization · rollback at 09:31 · back inside the baseline band</h4><svg id="c9" width="1060" height="400" style="position:absolute;left:0;top:40px"></svg></div>
    <div class="panel loop" data-in="1"><h4>Assurance loop</h4>
      {''.join(f'<div class="st" id="lp{i}"><span class="dot"></span>{w}</div>' for i, w in enumerate(['OBSERVE', 'DETECT', 'UNDERSTAND', 'ACT', 'VERIFY']))}
      <div class="res" data-in="16">✓ INC0051207 closed only after SevOne confirms the baseline</div>
    </div>
  </section>

  <!-- S10 · Risk controls -->
  {sec(10)}
    {stephead('07 — CONTROL', 'Operational risk controls · due diligence', 'Network evidence across <span class="cyan">every control layer</span>.')}
    <div class="rctab"><div class="rcr h" data-in="1"><div>Control</div><div>Business question</div><div>SevOne / NPM contribution</div><div>Adjacent enterprise controls</div></div>{rc_rows}</div>
    <div class="rcfoot" data-in="22">Due diligence: telemetry coverage, baselines, change validation and evidence retention reviewed for every critical service. SevOne is an important source of evidence, not a compliance guarantee.</div>
  </section>

  <!-- S11 · Executive dashboard -->
  {sec(11)}
    {stephead('08 — VALUE', 'KPI setting · NPM framework · executive risk view', 'Network operational risk, <span class="cyan">on one page</span>.')}
    <div class="kgrid">{k_tiles}</div>
    <div class="panel" id="coar" data-in="10"><div class="k">CHANGE OUTCOME ASSURANCE RATE</div>
      <div class="f">changes with a validated post-change network state<div class="ln"></div>changes requiring network validation</div>
      <div class="v" data-count="98.4" data-dec="1" data-suf="%" data-cin="12" data-cdur="2.5">0</div></div>
    <div class="panel" id="fw11" data-in="4"><div class="k">KPIS SET AUTOMATICALLY PER SERVICE CLASS</div><div class="chips">{''.join(f'<span class="chip">{c}</span>' for c in ['Availability', 'Performance', 'Capacity', 'Stability', 'Change', 'Coverage'])}</div></div>
    <div class="foot" data-in="3" style="bottom:110px">Illustrative demo values</div>
  </section>

  <!-- S12 · TCO / OPEX -->
  {sec(12)}
    {stephead('08 — VALUE', 'TCO · OPEX · proof of value', 'Prove the savings. <span class="green">Don’t assume them.</span>')}
    <div class="panel tco" style="left:96px" data-in="1"><div class="k red">BEFORE</div><ul><li>Several monitoring tools, duplicate dashboards</li><li>Manual thresholds and KPI configuration</li><li>Manual tickets and CMDB reconciliation</li><li>Incident war rooms, manual reports</li></ul><div class="tot red">HIGH OPERATING EFFORT</div></div>
    <div class="panel tco" style="left:978px" data-in="5"><div class="k green">AFTER</div><ul><li>Centralized multivendor NPM, flow and telemetry</li><li>Automated baselines and KPI policies</li><li>Automatic tickets, CMDB sync, routing</li><li>Evidence for RCA, capacity and SLA</li></ul><div class="tot green">LOWER ADDRESSABLE OPEX</div></div>
    <div class="pools">{''.join(f'<div class="panel" data-in="{14 + i * 0.6:.1f}" data-fx="up"><div class="k">{k}</div><div class="v">{v}</div></div>' for i, (k, v) in enumerate([('TOOLING', 'licences + infra + support'), ('ADMINISTRATION', 'engineer hours × cost'), ('INCIDENTS', 'incidents × people × hours'), ('REPORTING', 'manual SLA reporting'), ('ONBOARDING', 'CMDB and device changes'), ('OUTAGES', 'only where data supports it')]))}</div>
    <div class="flow12" data-in="24"><span class="mb">TCO baseline</span>→<span class="mb">Proof of value</span>→<span class="mb">Measured delta</span>→<span class="b g">Business case</span></div>
  </section>

  <!-- S13 · Three truths -->
  {sec(13)}
    <div class="truth" style="top:260px" data-in="0.8"><div class="who">AI agent</div><div class="say">“I completed the task.”</div></div>
    <div class="truth" style="top:380px" data-in="4.6"><div class="who">Automation platform</div><div class="say">“The configuration was deployed.”</div></div>
    <div class="truth" style="top:500px" data-in="8.6"><div class="who" style="color:var(--cyan)">IBM SevOne</div><div class="say" style="font-weight:600">“Here is what happened <span class="grad">to the network</span>.”</div></div>
    <div class="caption" data-in="12.4" style="bottom:200px;font-size:34px">The business needs all three. <b>Only independent observability verifies the outcome.</b></div>
  </section>

  <!-- S14 · The question -->
  {sec(14)}
    <div class="center"><div class="qq" data-in="0.2" data-dur="0.6" data-fx="scale">If an AI agent changed <span class="red">500 network devices</span> tonight, how quickly could you determine whether <span class="grad">every change</span> produced the intended business outcome?</div></div>
  </section>

  <!-- S15 · Assessment -->
  {sec(15)}
    <div class="stephead"><div class="eyebrow" data-in="0.2">Concrete next step</div><div class="t" data-in="0.5" data-dur="0.8">Agentic Network Readiness &amp; <span class="cyan">Observability Assessment</span></div></div>
    <div class="assess">{as_items}</div>
    <div class="asout" data-in="19">Outcome: a gap map, prioritized use cases, and a proof-of-value plan with measured KPIs.</div>
  </section>

  <!-- S16 · Closing -->
  {sec(16)}
    <div class="center" id="close1">
      <div class="a" data-in="0.5" data-dur="0.9">In the age of Agentic AI, autonomy without observability is <span class="red">risk</span>.</div>
      <div class="b" data-in="5.4" data-dur="0.9">The future isn’t just autonomous networking.</div>
      <div class="c" data-in="8.4" data-dur="0.9">It’s autonomous networking with <span class="grad">continuous assurance</span>.</div>
    </div>
    <div class="center end" id="close2">
      <div class="brand" data-in="11" data-dur="0.45" data-fx="scale"><span class="ibm">IBM</span><span class="grad">SevOne</span></div>
      <div class="tag2" data-in="12.2">Observe · Baseline · Detect · Diagnose · Respond · Verify</div>
    </div>
    <div class="disc" data-in="12.8">Demo scenario. Devices, agents, tickets, KPIs and figures are simulated for illustration. Narration: synthetic voice.</div>
  </section>

"""

steps_html = '<div id="steps">' + ''.join(f'<span>{s}</span>' for s, _ in TL['steps']) + '</div>'
tail_markup = re.sub(r'<div id="steps">.*?</div>', steps_html, tail_markup, flags=re.S)
chap_html = '<div class="chap">\n    ' + ''.join(f'<button data-t="{t}">{n}</button>' for n, t in TL['chapters']) + '\n  </div>'
tail_markup = re.sub(r'<div class="chap">.*?</div>', chap_html, tail_markup, flags=re.S)
dur = TL['duration']
tail_markup = tail_markup.replace('max="166"', f'max="{dur}"').replace('<span>2:46</span>', f'<span>{dur // 60}:{dur % 60:02d}</span>')
tail_markup = tail_markup.replace('Play Part 2 with narration · 2 min 46 s', f'Play with narration · {dur // 60} min {dur % 60:02d} s')
tail_markup = tail_markup.replace('Part 2 · incident to resolution · subtitles on', 'Agentic network assurance · subtitles on')
tail_markup = tail_markup.replace('SEVONE · PART 2</div><h2>Five steps, incident to resolution</h2>', 'SEVONE · AGENTIC ASSURANCE</div><h2>Chapters in the film</h2>')
tail_markup = tail_markup.replace('Every scenario is simulated, including the ServiceNow, Teams and Slack screens.', 'Every scenario is simulated. Values are demo values, not customer results.')

script_head = script_head.replace('const DURATION = 166;', 'const TIMELINE = ' + json.dumps(TL, ensure_ascii=False) + ';\nconst DURATION = TIMELINE.duration;')
script_head = re.sub(r'const IMPACTS = \[.*?\];', 'const IMPACTS = TIMELINE.impacts;', script_head)
script_head = re.sub(r'/\*NARRATION\*/.*?/\*END_NARRATION\*/', '/*NARRATION*/[]/*END_NARRATION*/', script_head, flags=re.S)
UCX = {
 's3': ('An AI-proposed, approved BGP change runs on 48 routers.', 'The automation platform reports 48/48 applied, 0 errors, BGP established.', 'Technical success, but the business outcome is still unknown.'),
 's4': ('Traffic moves onto a constrained path; nothing is down.', 'SevOne compares live utilization, latency and loss with each path’s learned baseline.', 'Deviation flagged while BGP is still established.'),
 's5': ('Degradation builds minute by minute.', 'Baselines, flow, streaming telemetry and synthetics surface it at 09:24.', 'Detected before packet loss spreads and before users call.'),
 's6': ('The same deviation means different risks per industry.', 'Industry KPIs per critical path: banking, telecom, rail, energy, government, AI and data.', 'Network signals translated into business risk.'),
 's7': ('Teams need the cause, not just an alert.', 'Symptom → scope → path → flow → change, with the blast radius.', 'The 09:21 change identified with evidence.'),
 's8': ('Insight must enter existing processes.', 'SevOne event → automatic ServiceNow incident with CI and evidence → routing → L1/L2 automated → L3 approval.', 'Controlled rollback; SevOne stays the independent observer.'),
 's9': ('A job reporting success is not proof.', 'SevOne re-measures utilization, latency and loss against the baseline.', 'Ticket closes only after verified recovery.'),
 's10': ('Risk and audit teams need evidence.', 'Network evidence for preventive, detective, diagnostic, corrective, verification and evidence controls.', 'Measurable controls and due diligence.'),
 's11': ('Executives need one risk view.', 'KPIs set per service class plus the change outcome assurance rate.', 'Network operational risk on one page.'),
 's12': ('Savings claims need proof.', 'Baseline six cost pools, run a proof of value, measure the delta.', 'A TCO and OPEX case built on evidence.'),
 's15': ('Where do you stand today?', 'Ten-point Agentic Network Readiness & Observability Assessment.', 'Gap map, prioritized use cases, proof-of-value plan.'),
}
UC = [[str(i + 1).zfill(2), x['name'], x['purpose'], x['start'], *UCX[x['id']]] for i, x in enumerate([x for x in TL['scenes'] if x['id'] in UCX])]
script_head = re.sub(r'const USE_CASES = \[.*?\];', lambda m: 'const USE_CASES = ' + json.dumps(UC) + ';', script_head, flags=re.S)
assert 'TIMELINE.impacts' in script_head and 'const USE_CASES = [["01"' in script_head

DYN = r"""/* ---------- Build dynamic content ---------- */
const LOGS = [
 'agent> analyze telemetry window=30d scope=edge-mtl-tor',
 'agent> propose: set local-preference 200 on path B (48 routers)',
 'change> CHG0052418 approved by policy (risk: medium)',
 'automation> ansible-playbook bgp-path-optimize.yml --limit edge-mtl-tor',
 'edge-tor-07> route-map PREFER-B permit 10 · set local-preference 200',
 'edge-mtl-03> commit complete · BGP neighbor 10.20.0.1 Established',
 'automation> 48/48 hosts changed · 0 failed',
];
let logtxt = ''; for (let i = 0; i < 34; i++) logtxt += `[09:${fmt2(19 + (i >> 4))}:${fmt2((i * 7) % 60)}] ` + LOGS[i % LOGS.length] + '\n';
$('#logs0').textContent = logtxt;

// Utilization model shared by the detect and verify charts (minutes after 09:00)
const r4 = rand(5); const NOISE = Array.from({ length: 420 }, () => r4() - .5);
function util(m, recover) {
  const n = NOISE[Math.floor(m * 10) % 420] * 5 + Math.sin(m * 1.7) * 1.5;
  let v = 46 + Math.sin(m / 6) * 3 + n;
  if (m > 21) v += 36 * easeInOut(clamp((m - 21) / 3));
  if (recover && m > 31) v -= 33 * easeInOut(clamp((m - 31) / 2));
  return v;
}
function makeChart(svgId, recover) {
  const svg = $(svgId); const X0 = 70, X1 = 1030, Y0 = 340, Y1 = 20;
  const xm = m => X0 + (m / 40) * (X1 - X0), yv = v => Y0 - (v / 100) * (Y0 - Y1);
  [0, 25, 50, 75, 100].forEach(v => { svgEl('line', { x1: X0, x2: X1, y1: yv(v), y2: yv(v), stroke: 'rgba(120,145,200,.14)' }, svg); const t = svgEl('text', { x: X0 - 12, y: yv(v) + 5, 'text-anchor': 'end', fill: '#5d6984', 'font-size': 14, 'font-family': 'IBM Plex Mono, monospace' }, svg); t.textContent = v + '%'; });
  [0, 10, 20, 30, 40].forEach(m => { const t = svgEl('text', { x: xm(m), y: Y0 + 26, 'text-anchor': 'middle', fill: '#5d6984', 'font-size': 14, 'font-family': 'IBM Plex Mono, monospace' }, svg); t.textContent = '09:' + fmt2(m); });
  let band = ''; for (let m = 0; m <= 40; m += .5) band += (band ? 'L' : 'M') + xm(m) + ',' + yv(46 + Math.sin(m / 6) * 3 + 9);
  for (let m = 40; m >= 0; m -= .5) band += 'L' + xm(m) + ',' + yv(46 + Math.sin(m / 6) * 3 - 9);
  svgEl('path', { d: band + 'Z', fill: 'rgba(69,137,255,.14)' }, svg);
  const mk = (m, c, label, y) => { const g = svgEl('g', {}, svg); svgEl('line', { x1: xm(m), x2: xm(m), y1: Y1, y2: Y0, stroke: c, 'stroke-width': 2, 'stroke-dasharray': '4 5' }, g); const t = svgEl('text', { x: xm(m) + 8, y, fill: c, 'font-size': 14, 'font-family': 'IBM Plex Mono, monospace' }, g); t.textContent = label; return g; };
  const chg = mk(21, '#f1c21b', '09:21 BGP change', Y1 + 14);
  const rb = recover ? mk(31, '#42be65', '09:31 rollback', Y1 + 36) : null;
  let d = ''; for (let m = 0; m <= 40; m += .1) d += (d ? 'L' : 'M') + xm(m).toFixed(1) + ',' + yv(util(m, recover)).toFixed(1);
  const defs = svgEl('defs', {}, svg); const cp = svgEl('clipPath', { id: svgId.slice(1) + 'clip' }, defs); const cr = svgEl('rect', { x: 0, y: 0, width: 0, height: 400 }, cp);
  const line = svgEl('path', { d, fill: 'none', stroke: '#33b1ff', 'stroke-width': 3, 'clip-path': `url(#${svgId.slice(1)}clip)` }, svg);
  return { cr, xm, chg, rb, line };
}
const ch4 = makeChart('#c4', false), ch9 = makeChart('#c9', true);

// Detect timeline
const TL5 = [['09:21', 'BGP policy changed'], ['09:22', 'Traffic path shifts'], ['09:23', 'Utilization deviates'], ['09:24', 'Latency increases'], ['09:25', 'Packet loss spreads'], ['09:26', 'Business impact']];
const tl5 = $('#tl5svg'); const TX = i => 120 + i * 297;
svgEl('line', { x1: TX(0), x2: TX(5), y1: 133, y2: 133, stroke: 'rgba(120,145,200,.3)', 'stroke-width': 4 }, tl5);
const tl5bar = svgEl('line', { x1: TX(0), x2: TX(0), y1: 133, y2: 133, stroke: '#f1c21b', 'stroke-width': 5 }, tl5);
TL5.forEach(([tm, tx], i) => { const n = document.createElement('div'); n.className = 'tnode'; n.id = 'tn' + i; n.style.left = TX(i) + 'px'; n.innerHTML = `<div class="dot"></div><div class="tm">${tm}</div><div class="tx">${tx}</div>`; $('#tl5nodes').appendChild(n); });
$('#det5').style.left = TX(3) + 'px';

// Response pipeline
const pipe = $('#pipesvg');
const pipeLinks = [0, 1, 2, 3, 4, 5].map(i => { const x1 = 216 + i * 252, x2 = x1 + 36, y = 135;
  svgEl('line', { x1, x2, y1: y, y2: y, stroke: '#4589ff', 'stroke-width': 3, 'stroke-opacity': .6 }, pipe);
  svgEl('path', { d: `M${x2 - 8},${y - 7} L${x2},${y} L${x2 - 8},${y + 7}`, fill: 'none', stroke: '#4589ff', 'stroke-width': 3 }, pipe);
  return { x1, x2, y }; });
const pulse = svgEl('circle', { r: 9, fill: '#fff', opacity: 0 }, pipe);
const IND_T = [1, 10.6, 20.2, 29.8, 39.4, 49];

"""

CUSTOM = """const custom = {
  s0(lt) {},
  s1(lt) {},
""" + s2s3.replace("$('#sweep3')", "($('#sweep3') || {style:{}})") + """  s2(lt) {
    for (let i = 0; i < 5; i++) { const n = $('#c2n' + i); n && n.classList.toggle('hot', lt > 22 + i * 1.1 && lt < 24.2 + i * 1.1); }
  },
  s4(lt) { ch4.cr.setAttribute('width', ch4.xm(lerp(0, 28, easeInOut(clamp((lt - 2) / 11)))) + 2); },
  s5(lt) {
    const p = clamp((lt - 3) / 9); const reach = p * 3;
    for (let i = 0; i < 6; i++) { const n = $('#tn' + i); n.classList.toggle('on', i <= reach + .001 && i < 3); n.classList.toggle('hit', i === 3 && reach >= 3); n.classList.toggle('gone', i > 3 && lt > 13); }
    $('#tl5bar') ; tl5bar.setAttribute('x2', 120 + reach * 297);
    const d = $('#det5'); d.style.opacity = clamp((lt - 12) / .4); d.style.transform = `translateX(-50%) scale(${lerp(1.3, 1, easeOut(clamp((lt - 12) / .4)))})`;
  },
  s6(lt) {
    let a = -1; IND_T.forEach((t, i) => { if (lt >= t) a = i; });
    for (let i = 0; i < 6; i++) { const c = $('#ind' + i); c.classList.toggle('act', i === a); c.classList.toggle('dim', i !== a); }
  },
  s7(lt) {
    for (let i = 0; i < 5; i++) $('#b' + i).classList.toggle('hot', lt > 17 + i * 1.6);
    for (let i = 0; i < 5; i++) $('#q7' + i).classList.toggle('done', lt > 33);
  },
  s8(lt) {
    const k = lt - 1.6; if (k < 0) { pulse.setAttribute('opacity', 0); return; }
    const pos = Math.min(5.99, k / 1.05); const i = Math.floor(pos), f = pos - i; const L = pipeLinks[i];
    pulse.setAttribute('cx', lerp(L.x1 - 108, L.x2 + 108, f)); pulse.setAttribute('cy', L.y); pulse.setAttribute('opacity', k < 7 ? 1 : 0);
  },
  s9(lt) {
    ch9.cr.setAttribute('width', ch9.xm(lerp(0, 40, easeInOut(clamp((lt - 1) / 10)))) + 2);
    for (let i = 0; i < 5; i++) $('#lp' + i).classList.toggle('on', lt > 12 + i * .8);
  },
  s16(lt) {
    $('#close1').style.opacity = 1 - clamp((lt - 10.2) / .6);
    $('#close1').style.transform = `scale(${lerp(1, 1.04, clamp(lt / 10))})`;
  },
};

"""

# Background tint from the timeline; HUD from the timeline.
rest = re.sub(r"const K = \[.*?\];", "const K = TIMELINE.tint;", rest, flags=re.S)
rest = rest.replace("const showHud = t > 40 && t < 152;", "const showHud = t > TIMELINE.steps_visible[0] && t < TIMELINE.steps_visible[1];")
rest = rest.replace("t > 152.5 ? 0 : 1;", "t > TIMELINE.duration - 20 ? 0 : 1;")
rest = rest.replace("$('#hud').style.opacity = t < 9 ? 0 : 1;", "$('#hud').style.opacity = t < 12 ? 0 : 1;")
rest = rest.replace("const stepIdx = t < 64 ? 0 : t < 86 ? 1 : t < 108 ? 2 : t < 134 ? 3 : 4;", "let stepIdx = 0; TIMELINE.steps.forEach(([, s], i) => { if (t >= s) stepIdx = i; });")
rest = re.sub(r"  const clock = .*?\n  \$\('#tc'\)\.textContent = .*?;\n", "  $('#tc').textContent = 'MTL ↔ TOR · DEMO SCENARIO';\n", rest)
rest = rest.replace("clamp((t - 164) / 1.6)", "clamp((t - (TIMELINE.duration - 2)) / 1.6)")
for must in ['TIMELINE.tint', 'TIMELINE.steps_visible', 'stepIdx = 0', 'DEMO SCENARIO', 'TIMELINE.duration - 2']:
    assert must in rest, must

html = head + SCENES + tail_markup + script_head + DYN + engine + CUSTOM + rest
(HERE / 'film.html').write_text(html)
print('wrote film.html', len(html))
