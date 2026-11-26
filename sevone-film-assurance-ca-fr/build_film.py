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

/* ---------- Canada-US architecture edition ---------- */
#arch17 { position: absolute; left: 96px; top: 250px; width: 1180px; height: 640px; padding: 18px 20px; box-sizing: border-box; }
#arch17 svg { position: absolute; left: 0; top: 40px; }
#facts17 { position: absolute; left: 1300px; top: 250px; width: 524px; padding: 18px 22px; box-sizing: border-box; }
#facts17 .kv { grid-template-columns: 150px 1fr; font-size: 17px; padding: 9px 0; }
#facts17 .kv .k { font-size: 12px; }
.code { position: absolute; top: 250px; width: 846px; height: 470px; padding: 18px 24px; box-sizing: border-box; background: rgba(6,10,20,.92); }
.code h4 { margin-bottom: 12px; }
.code .ln { font-family: var(--mono); font-size: 19px; line-height: 1.62; color: #cfe0ff; white-space: pre; }
.code .ln .c { color: #6f7f9f; } .code .ln .kw { color: #78a9ff; } .code .ln .v { color: #f1c21b; }
.vchips { position: absolute; left: 96px; right: 96px; top: 752px; display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; }
.vchips .chip { font-family: var(--mono); font-size: 16px; border-color: rgba(66,190,101,.6); color: #b9f0c9; background: rgba(8,40,22,.7); }
.iss { position: absolute; top: 250px; width: 560px; height: 470px; padding: 20px 22px; box-sizing: border-box; border-color: rgba(250,77,86,.45); }
.iss .k { font-family: var(--mono); font-size: 14px; letter-spacing: .18em; color: #ff8389; }
.iss .h { font-size: 24px; font-weight: 600; margin-top: 8px; line-height: 1.25; }
.iss .cl { font-family: var(--mono); font-size: 15px; color: #ffd7d9; background: rgba(218,30,40,.18); border-left: 3px solid var(--red); padding: 8px 12px; margin-top: 12px; border-radius: 4px; white-space: pre-wrap; }
.iss .lb { font-family: var(--mono); font-size: 12px; letter-spacing: .18em; color: var(--dim); text-transform: uppercase; margin-top: 14px; }
.iss .tx { font-size: 17px; color: #dfe6f5; margin-top: 4px; line-height: 1.4; }
.iss .tx.ev { color: #cfe0ff; } .iss .tx.fx { color: #b9f0c9; }
.iss .lb.sv { color: var(--cyan); } .iss .lb.fxl { color: var(--green); }

/* ---------- Assurance film ---------- */
.ind-grid { position: absolute; left: 80px; right: 80px; top: 250px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
.ind { padding: 18px 20px; height: 300px; box-sizing: border-box; transition: none; }
.ind .k { font-family: var(--mono); font-size: 15px; letter-spacing: .22em; color: var(--cyan); }
.ind .v { font-size: 23px; font-weight: 600; margin-top: 10px; line-height: 1.2; }
.ind .s { font-size: 15.5px; color: var(--dim); margin-top: 10px; line-height: 1.4; }
.ind.dim { opacity: .38; }
.ind.act { border-color: var(--cyan); box-shadow: 0 0 40px rgba(51,177,255,.25); background: rgba(20,36,66,.92); }
.ind .path { font-family: var(--mono); font-size: 13px; color: #9fb4da; margin-top: 10px; line-height: 1.45; }
.ind .kpis { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.ind .kpis span { font-family: var(--mono); font-size: 12px; padding: 3px 8px; border-radius: 6px; border: 1px solid var(--line-2); color: #cfe0ff; }
.ind .note { font-family: var(--mono); font-size: 12px; color: var(--yellow); margin-top: 8px; }
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
    ('BANQUE', 'Paiements et canaux numériques', 'Succursale · GAB · mobile → SD-WAN / MPLS → pare-feu · répartiteurs → CD et nuage → paiements',
     'Latence transactionnelle, disponibilité des canaux, résilience opérationnelle', ['latence', 'perte', 'util. WAN', 'erreurs d’interface', 'disponibilité'], ''),
    ('TÉLÉCOM', 'Services clients et SLA', 'Accès → cœur IP/MPLS → dorsale → peering et transit',
     'Pénalités de SLA, dégradation de service, escalades évitables', ['perte', 'gigue', 'utilisation', 'état des pairs BGP', 'SLA'], ''),
    ('FERROVIAIRE', 'Communications d’exploitation', 'Gares · dépôts → WAN → systèmes de contrôle d’exploitation → CD',
     'Dégradation des communications devenant perturbation opérationnelle', ['disponibilité', 'latence', 'erreurs de lien', 'redondance'], 'Assurance des communications, pas un système de sécurité ferroviaire'),
    ('TRANSPORT AÉRIEN', 'Aéroports et transporteurs', 'Aérogares · portes · bagages → WAN / SD-WAN → centre de contrôle des opérations → CD et nuage',
     'Retards en cascade : enregistrement, embarquement, bagages, opérations au sol', ['disponibilité', 'latence', 'gigue', 'perte', 'redondance'], 'Assurance réseau, pas un système de contrôle de la circulation aérienne'),
    ('ÉNERGIE', 'Communications du réseau et des sites', 'Postes · sites → WAN → centre de contrôle → CD et nuage',
     'Perte de visibilité sur les communications d’exploitation', ['disponibilité', 'latence', 'utilisation', 'redondance'], 'La surveillance reste distincte de la sécurité et du contrôle OT'),
    ('GOUVERNEMENT', 'Services aux citoyens et essentiels', 'Portail citoyen → CD gouvernemental → nuage → réseaux des organismes',
     'Pannes de services, retards des services d’urgence, reddition de comptes', ['disponibilité', 'temps de réponse', 'SLA', 'capacité'], ''),
    ('IA ET DONNÉES', 'Grappes GPU et pipelines de données', 'Sources de données → fabric → grappe GPU ↔ stockage → nuage',
     'Des GPU coûteux inactifs quand les chemins saturent', ['débit est-ouest', 'pertes', 'latence', 'utilisation'], 'L’infrastructure d’IA est aussi une infrastructure réseau'),
]

ind_cards = ''.join(f'''<div data-in="{0.6 + i * 0.25:.2f}" data-fx="up"><div class="panel ind dim" id="ind{i}"><div class="k">{k}</div><div class="v">{v}</div><div class="path">{p}</div><div class="s"><b style="color:#ffb3b8;font-weight:600">Risque ·</b> {r}</div><div class="kpis">{''.join(f'<span>{x}</span>' for x in kp)}</div>{f'<div class="note">{n}</div>' if n else ''}</div></div>''' for i, (k, v, p, r, kp, n) in enumerate(INDS))

s1_tiles = ''.join(f'<div data-in="{1.4 + i * 0.35:.2f}" data-fx="up"><div class="panel ind" style="height:215px"><div class="k">{k}</div><div class="v">{v}</div><div class="s">{r}</div></div></div>' for i, (k, v, p, r, kp, n) in enumerate(INDS))

RCROWS = [
    ('Préventif', 'Ce changement doit-il avoir lieu ?', 'Lignes de base et capacité éclairent la décision', 'IAM · PAM · politique de changement · CAB · garde-fous'),
    ('Détection', 'Quelque chose se dégrade-t-il ?', 'Métriques, flux, télémétrie, lignes de base, anomalies, tests synthétiques', 'SIEM · ITDR · surveillance applicative et OT'),
    ('Diagnostic', 'Que s’est-il passé, et où ?', 'Contexte interface, équipement, chemin et flux', 'AIOps · topologie · traçage · journaux'),
    ('Correctif', 'Que faire maintenant ?', 'Événements et alertes alimentent la réponse', 'ITSM · SOAR · Ansible · Terraform · procédures'),
    ('Vérification', 'La remédiation a-t-elle fonctionné ?', 'Nouvelle mesure face à la ligne de base et aux KPI', 'Contrôles de fermeture ITSM · budgets d’erreur SRE'),
    ('Preuve', 'Peut-on démontrer le résultat ?', 'Historique de performance, de SLA et de capacité', 'CMDB · dossiers de changement · journaux d’audit · GRC'),
]
rc_rows = ''.join(f'<div class="rcr" data-in="{1.6 + i * 3.2:.1f}" data-fx="left"><div class="L">{a}</div><div class="q">{b}</div><div class="sv">{c}</div><div class="adj">{d}</div></div>' for i, (a, b, c, d) in enumerate(RCROWS))

KPIS = [('Services critiques dans le SLA', '98,7 %', 'green'), ('Chemins critiques dans la ligne de base', '94,2 %', ''), ('Couverture d’observabilité des actifs critiques', '97,8 %', ''),
        ('Anomalies réseau actives', '17', ''), ('Anomalies à fort impact', '2', 'red'), ('Circuits à capacité à risque', '4', 'yellow'),
        ('Changements automatisés aujourd’hui', '126', ''), ('Changements suivis d’anomalies', '3', 'yellow'), ('Remédiations vérifiées', '11 / 12', 'green'), ('MTTR lié au réseau', '21 min', 'cyan')]
k_tiles = ''.join(f'<div class="panel kt" data-in="{1.2 + i * 0.35:.2f}" data-fx="up"><div class="k">{k}</div><div class="v {c}">{v}</div></div>' for i, (k, v, c) in enumerate(KPIS))

ASSESS = ['Visibilité actuelle du réseau', 'Cas d’usage IA et automatisation', 'Dépendances réseau critiques', 'Couverture de télémétrie existante', 'Visibilité BGP, WAN et SD-WAN',
          'Maturité des lignes de base et de la détection', 'Validation de l’impact des changements', 'Processus d’incident et de remédiation', 'Angles morts d’observabilité', 'Occasions d’assurance en boucle fermée']
as_items = ''.join(f'<div class="panel as" data-in="{1.5 + i * 1.6:.1f}" data-fx="up"><div class="n">{i + 1}</div><div class="t">{t}</div></div>' for i, t in enumerate(ASSESS))

SCENES = f"""  <!-- S0 · Cold open -->
  {sec(0)}
    <div class="logs" data-in="1.6" data-dur="2" data-fx="fade" id="logs0"></div>
    <div class="center">
      <div class="clock" data-in="0.5" data-dur="0.8">LUNDI · 09 h 20</div>
      <div class="l1" data-type="L’IA accélère les opérations." data-in="1.8" data-dur="1.4"></div>
      <div class="l2" data-in="4.4" data-dur="0.9">Elle accélère aussi le <span class="red">changement</span>.</div>
    </div>
  </section>

  <!-- S1 · Critical infrastructure -->
  {sec(1)}
    <div class="stephead" style="top:110px"><div class="eyebrow" data-in="0.3">Les infrastructures critiques reposent sur le réseau</div>
      <div class="h2" style="margin-top:16px;max-width:1700px" data-in="0.7" data-dur="0.8">Chaque service critique dépend du réseau, <span class="grad">et des agents qui le modifient désormais</span>.</div></div>
    <div class="ind-grid" style="top:330px">{s1_tiles}</div>
    <div class="envchips" style="bottom:130px">{''.join(f'<span class="chip" data-in="{9 + i * 0.3:.1f}" data-fx="up">{c}</span>' for i, c in enumerate(['Centres de données sur site', 'Nuage privé', 'AWS · Azure', 'WAN · MPLS', 'SD-WAN', 'Bordure BGP', 'Fabrics de CD', 'Wi-Fi', 'Frontière OT']))}</div>
  </section>

  <!-- S17 · Network architecture -->
  {sec(17)}
    {stephead('LE RÉSEAU', 'Centres de données canadiens · sites américains · BGP · SD-WAN', 'Canada et États-Unis : <span class="cyan">un maillage à haute disponibilité</span>.')}
    <div class="panel" id="arch17" data-in="1"><h4>Topologie · cœur MPLS · superposition SD-WAN · bordure BGP</h4><svg id="arch17svg" width="1180" height="600"></svg></div>
    <div class="panel" id="facts17" data-in="1.6"><h4>Architecture</h4><div class="kv" data-in="3.0" data-fx="left"><div class="k">Centres de données</div><div class="v">Montréal · Toronto · Vancouver</div></div><div class="kv" data-in="4.1" data-fx="left"><div class="k">Sites américains</div><div class="v">New York · Chicago · Atlanta · San Francisco</div></div><div class="kv" data-in="5.2" data-fx="left"><div class="k">Cœur</div><div class="v">Maillage MPLS entre CD · 100 Gb/s par paire · relève 25 Gb/s</div></div><div class="kv" data-in="6.3" data-fx="left"><div class="k">Routage</div><div class="v">BGP AS 65010 · iBGP entre CD · eBGP vers 2 FAI</div></div><div class="kv" data-in="7.4" data-fx="left"><div class="k">Superposition</div><div class="v">SD-WAN · transports MPLS + Internet</div></div><div class="kv" data-in="8.5" data-fx="left"><div class="k">Flux critiques</div><div class="v">paiements · réplication · VoIP · SAP</div></div><div class="kv" data-in="9.6" data-fx="left"><div class="k">Observé par</div><div class="v">SevOne · SNMP · flux · gNMI · tunnels SD-WAN</div></div></div>
  </section>

  <!-- S2 · Agentic operations -->
  {sec(2)}
    {stephead('OPÉRATIONS AGENTIQUES', 'Humain et politique → agent → automatisation approuvée → réseau', 'Une optimisation de routine, <span class="cyan">faite dans les règles</span>.')}
    <div class="panel prompt" data-in="1">
      <div class="k">INGÉNIEUR → AGENT D’IA DES OPÉRATIONS</div>
      <div class="pq">« Optimise la connectivité entre Montréal et Toronto sans dégrader la performance des applications. »</div>
      <div class="a" data-in="10" data-fx="fade">agent ▸ 30 jours de télémétrie analysés · propose de modifier la local-preference BGP sur 48 routeurs pour privilégier le chemin B</div>
    </div>
    <div class="chain" style="top:560px">
      <div class="panel node" id="c2n0" data-in="18"><div class="k">01</div><div class="v">Humain et politique</div><div class="s">objectif, garde-fous</div></div><div class="arr" data-in="18.4">→</div>
      <div class="panel node" id="c2n1" data-in="19"><div class="k">02</div><div class="v">Agent d’IA</div><div class="s">analyse, proposition</div></div><div class="arr" data-in="19.4">→</div>
      <div class="panel node" id="c2n2" data-in="20"><div class="k">03</div><div class="v">Approbation</div><div class="s">politique · CAB · billet</div></div><div class="arr" data-in="20.4">→</div>
      <div class="panel node" id="c2n3" data-in="21"><div class="k">04</div><div class="v">Automatisation</div><div class="s">Ansible · Terraform · contrôleur</div></div><div class="arr" data-in="21.4">→</div>
      <div class="panel node" id="c2n4" data-in="22"><div class="k">05</div><div class="v">Réseau</div><div class="s">48 routeurs de bordure</div></div>
    </div>
    <div class="caption" data-in="25" style="bottom:130px">Pas de magie. <b>Un changement approuvé et encadré</b>, exécuté par l’automatisation.</div>
  </section>

  <!-- S18 · AI-built configuration -->
  {sec(18)}
    {stephead('01 — LE CHANGEMENT', 'Configuration générée par l’IA · BGP + SD-WAN', 'L’agent rédige la configuration, <span class="cyan">et la pousse</span>.')}
    <div class="panel code" style="left:96px" data-in="1"><h4>BGP · IOS-XE · 48 routeurs de bordure</h4><div class="ln" data-in="2.0" data-fx="fade" data-dur="0.25"><span class="c">! generated by ai-ops-agent · CHG0052418</span></div><div class="ln" data-in="2.5" data-fx="fade" data-dur="0.25"><span class="kw">ip prefix-list</span> ANY seq 5 permit <span class="v">0.0.0.0/0 le 32</span></div><div class="ln" data-in="2.9" data-fx="fade" data-dur="0.25">!</div><div class="ln" data-in="3.4" data-fx="fade" data-dur="0.25"><span class="kw">route-map</span> PREFER-PATH-B permit 10</div><div class="ln" data-in="3.8" data-fx="fade" data-dur="0.25"> match ip address prefix-list <span class="v">ANY</span></div><div class="ln" data-in="4.2" data-fx="fade" data-dur="0.25"> set local-preference <span class="v">200</span></div><div class="ln" data-in="4.7" data-fx="fade" data-dur="0.25">!</div><div class="ln" data-in="5.2" data-fx="fade" data-dur="0.25"><span class="kw">router bgp</span> 65010</div><div class="ln" data-in="5.6" data-fx="fade" data-dur="0.25"> neighbor 10.20.0.2 description TOR-MTL-PATH-B</div><div class="ln" data-in="6.0" data-fx="fade" data-dur="0.25"> neighbor 10.20.0.2 route-map PREFER-PATH-B in</div></div>
    <div class="panel code" style="left:978px" data-in="6.6"><h4>SD-WAN · politique centralisée · SD-WAN Manager</h4><div class="ln" data-in="7.6" data-fx="fade" data-dur="0.25"><span class="c">! SD-WAN Manager · centralized policy</span></div><div class="ln" data-in="8.0" data-fx="fade" data-dur="0.25"><span class="kw">policy</span></div><div class="ln" data-in="8.4" data-fx="fade" data-dur="0.25"> <span class="kw">sla-class</span> PAYMENTS-SLA</div><div class="ln" data-in="8.9" data-fx="fade" data-dur="0.25">  latency <span class="v">150</span></div><div class="ln" data-in="9.3" data-fx="fade" data-dur="0.25">  loss <span class="v">5</span></div><div class="ln" data-in="9.7" data-fx="fade" data-dur="0.25">  jitter 100</div><div class="ln" data-in="10.1" data-fx="fade" data-dur="0.25"> !</div><div class="ln" data-in="10.5" data-fx="fade" data-dur="0.25"> <span class="kw">app-route-policy</span> TOR-MTL-APPS</div><div class="ln" data-in="11.0" data-fx="fade" data-dur="0.25">  sequence 10</div><div class="ln" data-in="11.4" data-fx="fade" data-dur="0.25">   match app-list PAYMENTS</div><div class="ln" data-in="11.8" data-fx="fade" data-dur="0.25">   action sla-class PAYMENTS-SLA preferred-color mpls</div></div>
    <div class="vchips"><span class="chip" data-in="13.0" data-fx="up">✓ Syntaxe valide</span><span class="chip" data-in="14.3" data-fx="up">✓ Lint réussi</span><span class="chip" data-in="15.6" data-fx="up">✓ Simulation : pairs BGP actifs</span><span class="chip" data-in="16.9" data-fx="up">✓ Approuvé · CHG0052418</span><span class="chip" data-in="18.2" data-fx="up">✓ Poussé : 48 routeurs + SD-WAN Manager</span></div>
    <div class="caption" data-in="24" style="bottom:130px">Toutes les vérifications que l’agent sait faire <b>réussissent</b>.</div>
  </section>

  <!-- S3 · The change -->
  {sec(3)}
    {stephead('01 — LE CHANGEMENT', 'Exécution technique', 'La plateforme d’automatisation annonce un <span class="green">succès</span>.')}
    <div class="panel console" data-in="0.8">
      <div data-in="1.4" data-fx="fade"><span class="dimc">$</span> run playbook bgp-path-optimize.yml --limit edge-mtl-tor</div>
      <div data-in="3.0" data-fx="fade">BGP + SD-WAN POLICY UPDATE</div>
      <div data-in="4.0" data-fx="fade">Devices targeted ........ 48</div>
      <div data-in="5.0" data-fx="fade">Configuration applied ... 48</div>
      <div data-in="6.0" data-fx="fade">Errors .................. <span class="ok">0</span></div>
      <div data-in="7.0" data-fx="fade">BGP sessions ............ <span class="ok">ESTABLISHED 96/96</span></div>
      <div data-in="8.0" data-fx="fade">Devices reachable ....... <span class="ok">48/48</span></div>
      <div data-in="9.2" data-fx="fade" style="margin-top:12px">STATUS: <span class="ok">SUCCESS</span></div>
    </div>
    <div class="panel" id="succ3" data-in="10.4" data-dur="0.3" data-fx="scale"><div class="v">✓ CHANGEMENT<br>RÉUSSI</div><div class="s">aucune erreur de configuration<br>aucun équipement en panne<br>BGP établi</div></div>
    <div id="q3" data-in="23.6" data-dur="0.4" data-fx="scale">Mais le <span class="red">résultat d’affaires</span> est-il au rendez-vous ?</div>
  </section>

  <!-- S4 · SevOne sees something different -->
  {sec(4)}
    {stephead('02 — DÉTECTER', 'Écart à la ligne de base · télémétrie indépendante', 'Le changement a réussi. <span class="red">Pas le résultat.</span>')}
    <div class="mtiles">
      <div class="panel mt" data-in="6"><div class="k">Utilisation WAN · MTL ↔ TOR</div><div class="row"><span class="mb">47%</span><span class="ar">→</span><span class="ma red" data-count="82" data-suf="%" data-cin="9" data-cdur="3">0</span></div></div>
      <div class="panel mt" data-in="6.3"><div class="k">Latence · chemin des paiements</div><div class="row"><span class="mb">18 ms</span><span class="ar">→</span><span class="ma red" data-count="63" data-suf=" ms" data-cin="10" data-cdur="3">0</span></div></div>
      <div class="panel mt" data-in="6.6"><div class="k">Perte de paquets</div><div class="row"><span class="mb">0,1 %</span><span class="ar">→</span><span class="ma red" data-count="2.1" data-dec="1" data-suf="%" data-cin="11" data-cdur="3">0</span></div></div>
      <div class="panel mt" data-in="6.9"><div class="k">Sessions BGP</div><div class="row"><span class="ma green" style="font-size:34px">ÉTABLIES</span></div></div>
    </div>
    <div class="panel" id="chart4" data-in="1"><h4>Utilisation WAN · bordure de Toronto · % · bande de la ligne de base</h4><svg id="c4" width="1060" height="400" style="position:absolute;left:0;top:40px"></svg>
      <div id="dev4" data-in="10.2" data-dur="0.3" data-fx="scale">ÉCART À LA LIGNE DE BASE · 09 h 23</div></div>
    <div class="panel" id="split4" data-in="14">
      <div class="sp h"><div>L’automatisation dit</div><div>L’assurance réseau dit</div></div>
      <div class="sp" data-in="15" data-fx="left"><div class="l">✓ changement appliqué</div><div class="r">⚠ comportement anormal</div></div>
      <div class="sp" data-in="16.2" data-fx="left"><div class="l">✓ BGP établi</div><div class="r">⚠ trafic déplacé</div></div>
      <div class="sp" data-in="17.4" data-fx="left"><div class="l">✓ équipements en service</div><div class="r">⚠ latence en hausse</div></div>
      <div class="sp" data-in="18.6" data-fx="left" style="border:0"><div class="l">✓ zéro erreur</div><div class="r">⚠ risque de service émergent</div></div>
    </div>
    <div class="foot" data-in="4" style="bottom:110px">Valeurs de scénario de démonstration · télémétrie SNMP, flux et gNMI (gNMI en préversion publique)</div>
  </section>

  <!-- S5 · Before it becomes an incident -->
  {sec(5)}
    {stephead('02 — DÉTECTER', 'Dégradation, pas panne', 'N’attendez pas la panne. <span class="cyan">Détectez pendant que tout fonctionne.</span>')}
    <div id="tl5"><svg id="tl5svg" width="1728" height="330" style="position:absolute;left:0;top:0"></svg><div id="tl5nodes"></div><div id="det5">SEVONE DÉTECTE · 09 h 24</div></div>
    <div class="evid">
      <div class="panel" data-in="16"><div class="k">LIGNES DE BASE</div><div class="v">apprises par chemin, par heure</div></div>
      <div class="panel" data-in="16.4"><div class="k">FLUX</div><div class="v">NetFlow · IPFIX : qui est allé où</div></div>
      <div class="panel" data-in="16.8"><div class="k">TÉLÉMÉTRIE</div><div class="v">SNMP · gNMI en continu (préversion publique)</div></div>
      <div class="panel" data-in="17.2"><div class="k">TESTS SYNTHÉTIQUES</div><div class="v">chemins de service vus par l’utilisateur</div></div>
    </div>
  </section>

  <!-- S6 · Seven industries -->
  {sec(6)}
    {stephead('03 — IMPACT', 'Même signal · risques d’affaires différents', 'Un écart. <span class="cyan">Sept conséquences d’affaires.</span>')}
    <div class="ind-grid">{ind_cards}</div>
  </section>

  <!-- S7 · Root cause -->
  {sec(7)}
    {stephead('04 — DIAGNOSTIQUER', 'Analyse de cause racine · rayon d’impact', 'Du symptôme à la cause, <span class="cyan">preuves à l’appui</span>.')}
    <div id="rca7">
      <div class="panel rca" data-in="3" data-fx="left"><div class="k">SYMPTÔME</div><div class="v">Latence de 63 ms sur le chemin des paiements (ligne de base 18 ms)</div></div>
      <div class="panel rca" data-in="6" data-fx="left"><div class="k">PORTÉE</div><div class="v">Bordure de Toronto · 3 circuits WAN · 2 services critiques</div></div>
      <div class="panel rca" data-in="9" data-fx="left"><div class="k">CHEMIN</div><div class="v">Meilleur chemin BGP : du chemin A (100 Gb/s) au chemin B, relève 25 Gb/s</div></div>
      <div class="panel rca" data-in="12" data-fx="left"><div class="k">FLUX</div><div class="v">Principaux flux sur le chemin B : réplication 38 % · paiements 22 %</div></div>
      <div class="panel rca" data-in="15" data-fx="left" style="border-color:rgba(241,194,27,.7)"><div class="k" style="color:var(--yellow)">CHANGEMENT</div><div class="v">09 h 21 politique BGP · CHG0052418 · proposé par l’IA, approuvé</div></div>
    </div>
    <div class="panel" id="br7" data-in="1.4"><h4>Rayon d’impact</h4>
      <div class="brn" id="b0"><span>Chemin BGP · chemin B</span><span class="m">route</span></div><div class="brd">↓</div>
      <div class="brn" id="b1"><span>Relève TOR–MTL · 25 Gb/s</span><span class="m">util. 82 %</span></div><div class="brd">↓</div>
      <div class="brn" id="b2"><span>Bordure de Toronto</span><span class="m">rejets en file</span></div><div class="brd">↓</div>
      <div class="brn" id="b3"><span>Connectivité infonuagique</span><span class="m">63 ms</span></div><div class="brd">↓</div>
      <div class="brn" id="b4"><span>Service bancaire critique</span><span class="m">à risque</span></div>
    </div>
    <div id="qs7">{''.join(f'<span class="chip" id="q7{i}" data-in="{28 + i * 0.6:.1f}" data-fx="up">{q}</span>' for i, q in enumerate(['Qu’est-ce qui a changé ?', 'Où ?', 'Quelle anomalie ?', 'Quel impact ?', 'Quelle urgence ?']))}</div>
  </section>

  <!-- S19 · What went wrong -->
  {sec(19)}
    {stephead('04 — DIAGNOSTIQUER', 'Configuration valide · mauvais résultat', 'Configuration valide. <span class="red">Mauvais résultat.</span> Trois problèmes expliqués.')}
    <div class="panel iss" style="left:96px" data-in="6" data-fx="up"><div class="k">PROBLÈME 1 · PORTÉE DE LA ROUTE-MAP BGP</div><div class="h">La route-map s’applique à tous les préfixes</div><div class="cl">match ip address prefix-list ANY
(0.0.0.0/0 le 32) → local-pref 200</div>
<div class="lb">Effet</div><div class="tx">Paiements et réplication passent sur le chemin B, la relève à 25 Gb/s, avec le trafic de masse visé.</div><div class="lb sv" data-in="9.0" data-fx="fade">Ce que SevOne a vu</div><div class="tx ev" data-in="9.0" data-fx="fade">Principaux flux sur le chemin B : réplication 38 %, paiements 22 %. Meilleur chemin BGP modifié sur 96 sessions (données BGP gNMI, préversion publique).</div>
<div class="lb fxl" data-in="11.0" data-fx="fade">Correctif</div><div class="tx fx" data-in="11.0" data-fx="fade">Cibler uniquement la prefix-list du trafic de masse ; garder les paiements sur le chemin A.</div></div><div class="panel iss" style="left:680px" data-in="15.4" data-fx="up"><div class="k">PROBLÈME 2 · SEUILS DE SLA SD-WAN</div><div class="h">La classe de SLA est bien trop permissive</div><div class="cl">sla-class PAYMENTS-SLA
latency 150 · loss 5</div>
<div class="lb">Effet</div><div class="tx">Les paiements tournent normalement à 18 ms et 0,1 % de perte. À 63 ms et 2,1 %, le chemin reste « conforme » : le SD-WAN ne redirige rien.</div><div class="lb sv" data-in="18.4" data-fx="fade">Ce que SevOne a vu</div><div class="tx ev" data-in="18.4" data-fx="fade">Surveillance des tunnels SD-WAN TOR–MTL : latence 63 ms, perte 2,1 %, gigue en hausse, alors que la politique déclare le SLA respecté.</div>
<div class="lb fxl" data-in="20.4" data-fx="fade">Correctif</div><div class="tx fx" data-in="20.4" data-fx="fade">Dériver les seuils des lignes de base SevOne, p. ex. 40 ms et 0,5 % de perte.</div></div><div class="panel iss" style="left:1264px" data-in="26.4" data-fx="up"><div class="k">PROBLÈME 3 · AUCUNE VÉRIFICATION DU RÉSULTAT</div><div class="h">Le succès = « configuration appliquée »</div><div class="cl">critères de succès :
syntaxe ✓ · lint ✓ · pairs actifs ✓</div>
<div class="lb">Effet</div><div class="tx">Personne n’a vérifié l’utilisation, la latence, la perte ou les flux du nouveau chemin, ni l’effet combiné des changements BGP et SD-WAN.</div><div class="lb sv" data-in="29.4" data-fx="fade">Ce que SevOne a vu</div><div class="tx ev" data-in="29.4" data-fx="fade">Écart à la ligne de base à 09 h 23, deux minutes après CHG0052418, corrélé au changement et à son auteur.</div>
<div class="lb fxl" data-in="31.4" data-fx="fade">Correctif</div><div class="tx fx" data-in="31.4" data-fx="fade">Ajouter une validation du résultat : interroger SevOne avant de déclarer un changement réussi.</div></div>
    <div class="caption" data-in="33" style="bottom:120px">SevOne ne lit pas l’intention. <b>Il mesure le résultat</b>, et le résultat a révélé les trois.</div>
  </section>

  <!-- S8 · Incident automation -->
  {sec(8)}
    {stephead('05 — RÉPONDRE', 'Billet automatique · acheminement · N1/N2 automatisés · N3 humain', 'De la preuve à l’action, <span class="cyan">dans vos processus</span>.')}
    <div id="pipe" style="top:240px;height:250px"><svg id="pipesvg" width="1728" height="260"></svg>
      <div class="panel stage" style="left:0" data-in="1.4"><div class="n">01</div><div class="h">SevOne</div><div class="s">condition levée</div></div>
      <div class="panel stage" style="left:252px" data-in="2.4"><div class="n">02</div><div class="h">Événement</div><div class="s">AIOps · corrélation</div></div>
      <div class="panel stage" style="left:504px" data-in="3.4"><div class="n">03</div><div class="h">Billet</div><div class="s">ServiceNow, auto</div></div>
      <div class="panel stage" style="left:756px" data-in="4.4"><div class="n">04</div><div class="h">Acheminer</div><div class="s">NetOps · DevSecOps</div></div>
      <div class="panel stage auto" style="left:1008px" data-in="5.4"><div class="n">N1</div><div class="h">Triage</div><div class="s">dossier de preuves</div><span class="tag ok">AUTOMATISÉ</span></div>
      <div class="panel stage auto" style="left:1260px" data-in="6.4"><div class="n">N2</div><div class="h">Proposer</div><div class="s">plan de retour</div><span class="tag ok">AUTOMATISÉ</span></div>
      <div class="panel stage human" style="left:1512px" data-in="7.4"><div class="n">N3</div><div class="h">Approuver</div><div class="s">l’ingénieur décide</div><span class="tag watch">HUMAIN</span></div>
    </div>
    <div class="panel" id="tick8" data-in="9">
      <div class="tbar">ServiceNow · Incident <span class="n">INC0051207</span><span class="st">CRÉÉ AUTOMATIQUEMENT · 7 s</span></div>
      <div class="f" data-in="10" data-fx="fade"><div class="k">Élément de config.</div><div>edge-tor-07 · synchronisé depuis la CMDB</div></div>
      <div class="f" data-in="10.6" data-fx="fade"><div class="k">Service d’affaires</div><div>Paiements numériques · niveau 1</div></div>
      <div class="f" data-in="11.2" data-fx="fade"><div class="k">Priorité</div><div><span class="yellow">P2</span> · impact 2 · urgence 1</div></div>
      <div class="f" data-in="11.8" data-fx="fade"><div class="k">Changement lié</div><div>CHG0052418 · mise à jour BGP proposée par l’IA</div></div>
      <div class="f" data-in="12.4" data-fx="fade"><div class="k">Preuves</div><div>graphique de base · écart de chemin · principaux flux</div></div>
    </div>
    <div id="lv8">
      <div class="panel tier auto" data-in="20"><div class="k">N1 · automatisé</div><div class="v">Triage : dossier de preuves joint, NetOps alerté</div></div>
      <div class="panel tier auto" data-in="22"><div class="k">N2 · automatisé</div><div class="v">Diagnostic confirmé · retour au chemin A proposé</div></div>
      <div class="panel tier human" data-in="27"><div class="k">N3 · humain dans la boucle</div><div class="v">✓ L’ingénieur approuve le retour arrière</div><div class="s">l’automatisation exécute · SevOne observe</div></div>
    </div>
  </section>

  <!-- S9 · Verify -->
  {sec(9)}
    {stephead('06 — VÉRIFIER', 'Boucler par la mesure', 'Une tâche dit « terminé ». <span class="green">Le réseau le prouve.</span>')}
    <div class="mtiles">
      <div class="panel mt" data-in="1"><div class="k">Utilisation WAN</div><div class="row"><span class="mb">82%</span><span class="ar">→</span><span class="ma green" data-count="49" data-suf="%" data-cin="6" data-cdur="3">82%</span></div></div>
      <div class="panel mt" data-in="1.3"><div class="k">Latence</div><div class="row"><span class="mb">63 ms</span><span class="ar">→</span><span class="ma green" data-count="19" data-suf=" ms" data-cin="7" data-cdur="3">63 ms</span></div></div>
      <div class="panel mt" data-in="1.6"><div class="k">Perte de paquets</div><div class="row"><span class="mb">2,1 %</span><span class="ar">→</span><span class="ma green" data-count="0.1" data-dec="1" data-suf="%" data-cin="8" data-cdur="3">2.1%</span></div></div>
      <div class="panel mt" data-in="1.9"><div class="k">État du service</div><div class="row"><span class="ma green" style="font-size:34px" data-in="11">NORMAL</span></div></div>
    </div>
    <div class="panel" id="chart9" data-in="0.6"><h4>Utilisation WAN · retour arrière à 09 h 31 · de retour dans la ligne de base</h4><svg id="c9" width="1060" height="400" style="position:absolute;left:0;top:40px"></svg></div>
    <div class="panel loop" data-in="1"><h4>Boucle d’assurance</h4>
      {''.join(f'<div class="st" id="lp{i}"><span class="dot"></span>{w}</div>' for i, w in enumerate(['OBSERVER', 'DÉTECTER', 'COMPRENDRE', 'AGIR', 'VÉRIFIER']))}
      <div class="res" data-in="16">✓ INC0051207 fermé seulement après confirmation de SevOne</div>
    </div>
  </section>

  <!-- S10 · Risk controls -->
  {sec(10)}
    {stephead('07 — CONTRÔLER', 'Contrôles du risque opérationnel · diligence raisonnable', 'La preuve réseau à <span class="cyan">chaque niveau de contrôle</span>.')}
    <div class="rctab"><div class="rcr h" data-in="1"><div>Contrôle</div><div>Question d’affaires</div><div>Apport SevOne / NPM</div><div>Contrôles d’entreprise associés</div></div>{rc_rows}</div>
    <div class="rcfoot" data-in="22">Diligence raisonnable : couverture de télémétrie, lignes de base, validation des changements et conservation des preuves revues pour chaque service critique. SevOne est une source de preuves importante, pas une garantie de conformité.</div>
  </section>

  <!-- S11 · Executive dashboard -->
  {sec(11)}
    {stephead('08 — VALEUR', 'Indicateurs · cadre NPM · vue de direction', 'Le risque opérationnel réseau, <span class="cyan">sur une seule page</span>.')}
    <div class="kgrid">{k_tiles}</div>
    <div class="panel" id="coar" data-in="10"><div class="k">TAUX D’ASSURANCE DES RÉSULTATS DE CHANGEMENT</div>
      <div class="f">changements dont l’état réseau post-changement est validé<div class="ln"></div>changements exigeant une validation réseau</div>
      <div class="v" data-count="98.4" data-dec="1" data-suf="%" data-cin="12" data-cdur="2.5">0</div></div>
    <div class="panel" id="fw11" data-in="4"><div class="k">INDICATEURS DÉFINIS AUTOMATIQUEMENT PAR CLASSE DE SERVICE</div><div class="chips">{''.join(f'<span class="chip">{c}</span>' for c in ['Disponibilité', 'Performance', 'Capacité', 'Stabilité', 'Changement', 'Couverture'])}</div></div>
    <div class="foot" data-in="3" style="bottom:110px">Valeurs de démonstration illustratives</div>
  </section>

  <!-- S12 · TCO / OPEX -->
  {sec(12)}
    {stephead('08 — VALEUR', 'Coût total · dépenses d’exploitation · preuve de valeur', 'Prouvez les économies. <span class="green">Ne les supposez pas.</span>')}
    <div class="panel tco" style="left:96px" data-in="1"><div class="k red">AVANT</div><ul><li>Plusieurs outils de surveillance, tableaux en double</li><li>Seuils et indicateurs configurés à la main</li><li>Billets manuels et rapprochement CMDB</li><li>Cellules de crise, rapports manuels</li></ul><div class="tot red">EFFORT D’EXPLOITATION ÉLEVÉ</div></div>
    <div class="panel tco" style="left:978px" data-in="5"><div class="k green">APRÈS</div><ul><li>NPM, flux et télémétrie multifournisseurs centralisés</li><li>Lignes de base et indicateurs automatisés</li><li>Billets automatiques, synchro CMDB, acheminement</li><li>Preuves pour l’analyse de cause, la capacité et les SLA</li></ul><div class="tot green">DÉPENSES D’EXPLOITATION ADRESSABLES RÉDUITES</div></div>
    <div class="pools">{''.join(f'<div class="panel" data-in="{14 + i * 0.6:.1f}" data-fx="up"><div class="k">{k}</div><div class="v">{v}</div></div>' for i, (k, v) in enumerate([('OUTILS', 'licences + infra + soutien'), ('ADMINISTRATION', 'heures d’ingénieur × coût'), ('INCIDENTS', 'incidents × personnes × heures'), ('RAPPORTS', 'rapports de SLA manuels'), ('INTÉGRATION', 'changements CMDB et équipements'), ('PANNES', 'seulement si les données le permettent')]))}</div>
    <div class="flow12" data-in="24"><span class="b">Coût actuel mesuré</span>→<span class="b">Preuve de valeur</span>→<span class="b">Écart mesuré</span>→<span class="b g">Dossier d’affaires</span></div>
  </section>

  <!-- S13 · Three truths -->
  {sec(13)}
    <div class="truth" style="top:260px" data-in="0.8"><div class="who">Agent d’IA</div><div class="say">« J’ai terminé la tâche. »</div></div>
    <div class="truth" style="top:380px" data-in="4.6"><div class="who">Automatisation</div><div class="say">« La configuration est déployée. »</div></div>
    <div class="truth" style="top:500px" data-in="8.6"><div class="who" style="color:var(--cyan)">IBM SevOne</div><div class="say" style="font-weight:600">« Voici ce qui est arrivé <span class="grad">au réseau</span>. »</div></div>
    <div class="caption" data-in="12.4" style="bottom:200px;font-size:34px">L’entreprise a besoin des trois. <b>Seule l’observabilité indépendante vérifie le résultat.</b></div>
  </section>

  <!-- S14 · The question -->
  {sec(14)}
    <div class="center"><div class="qq" data-in="0.2" data-dur="0.6" data-fx="scale">Si un agent d’IA modifiait <span class="red">500 équipements réseau</span> cette nuit, combien de temps vous faudrait-il pour savoir si <span class="grad">chaque changement</span> a produit le résultat attendu ?</div></div>
  </section>

  <!-- S15 · Assessment -->
  {sec(15)}
    <div class="stephead"><div class="eyebrow" data-in="0.2">Prochaine étape concrète</div><div class="t" data-in="0.5" data-dur="0.8">Évaluation de la préparation et de <span class="cyan">l’observabilité du réseau agentique</span></div></div>
    <div class="assess">{as_items}</div>
    <div class="asout" data-in="19">Résultat : une cartographie des écarts, des cas d’usage priorisés et un plan de preuve de valeur avec indicateurs mesurés.</div>
  </section>

  <!-- S16 · Closing -->
  {sec(16)}
    <div class="center" id="close1">
      <div class="a" data-in="0.5" data-dur="0.9">À l’ère de l’IA agentique, l’autonomie sans observabilité, c’est un <span class="red">risque</span>.</div>
      <div class="b" data-in="5.4" data-dur="0.9">L’avenir n’est pas seulement le réseau autonome.</div>
      <div class="c" data-in="8.4" data-dur="0.9">C’est le réseau autonome avec une <span class="grad">assurance continue</span>.</div>
    </div>
    <div class="center end" id="close2">
      <div class="brand" data-in="11" data-dur="0.45" data-fx="scale"><span class="ibm">IBM</span><span class="grad">SevOne</span></div>
      <div class="tag2" data-in="12.2">Observer · Référencer · Détecter · Diagnostiquer · Répondre · Vérifier</div>
    </div>
    <div class="disc" data-in="12.8">Scénario de démonstration. Équipements, agents, billets, indicateurs et chiffres sont simulés à titre illustratif. Narration : voix de synthèse.</div>
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
 's17': ('Qui est concerné, et où ?', 'CD à Montréal, Toronto et Vancouver en maillage haute disponibilité : 100 Gb/s par paire, relève 25 Gb/s ; sites américains en SD-WAN ; BGP vers les FAI et le nuage.', 'Un réseau hybride entièrement observé.'),
 's18': ('L’agent rédige la configuration BGP et SD-WAN.', 'Route-map qui hausse la préférence locale sur le chemin B ; classe de SLA SD-WAN pour les paiements ; syntaxe, lint, essai à blanc et approbation réussis.', 'Poussée sur 48 routeurs et dans le gestionnaire SD-WAN.'),
 's19': ('Configuration valide, mauvais résultat.', 'Portée de la route-map trop large ; seuils de SLA SD-WAN trop permissifs ; aucune vérification du résultat après le changement.', 'Les trois révélés par les flux SevOne, les métriques des tunnels SD-WAN et l’écart à la ligne de base.'),
 's3': ('Un changement BGP proposé par l’IA et approuvé s’exécute sur 48 routeurs.', 'La plateforme d’automatisation annonce 48/48 appliqués, 0 erreur, BGP établi.', 'Succès technique, mais le résultat d’affaires reste inconnu.'),
 's4': ('Le trafic passe sur la relève à 25 Gb/s ; rien n’est en panne.', 'SevOne compare utilisation, latence et perte à la ligne de base apprise de chaque chemin.', 'Écart signalé alors que BGP reste établi.'),
 's5': ('La dégradation s’installe minute après minute.', 'Lignes de base, flux, télémétrie en continu et tests synthétiques la révèlent à 9 h 24.', 'Détectée avant que la perte ne s’étende et avant les appels.'),
 's6': ('Le même écart, des risques différents selon le secteur.', 'KPI sectoriels par chemin critique : banque, télécom, ferroviaire, transport aérien, énergie, gouvernement, IA et données.', 'Les signaux réseau traduits en risque d’affaires.'),
 's7': ('Les équipes ont besoin de la cause, pas seulement d’une alerte.', 'Symptôme → portée → chemin → flux → changement, avec le rayon d’impact.', 'Le changement de 9 h 21 identifié, preuves à l’appui.'),
 's8': ('L’information doit entrer dans les processus existants.', 'Événement SevOne → incident ServiceNow automatique avec CI et preuves → acheminement → N1/N2 automatisés → approbation N3.', 'Retour arrière contrôlé ; SevOne reste l’observateur indépendant.'),
 's9': ('Une tâche réussie n’est pas une preuve.', 'SevOne mesure de nouveau utilisation, latence et perte face à la ligne de base.', 'Le billet se ferme seulement après un rétablissement vérifié.'),
 's10': ('Les équipes de risque et d’audit ont besoin de preuves.', 'Preuves réseau pour les contrôles préventifs, de détection, de diagnostic, correctifs, de vérification et de preuve.', 'Des contrôles mesurables et une diligence raisonnable.'),
 's11': ('La direction a besoin d’une vue unique du risque.', 'KPI par classe de service, plus le taux d’assurance des résultats de changement.', 'Le risque opérationnel réseau sur une page.'),
 's12': ('Les économies doivent être prouvées.', 'Mesurer six postes de coûts, faire une preuve de valeur, mesurer l’écart.', 'Un dossier de coût total et d’OPEX fondé sur des preuves.'),
 's15': ('Où en êtes-vous aujourd’hui ?', 'Évaluation en dix points de la préparation et de l’observabilité du réseau agentique.', 'Carte des écarts, cas d’usage priorisés, plan de preuve de valeur.'),
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
  [0, 10, 20, 30, 40].forEach(m => { const t = svgEl('text', { x: xm(m), y: Y0 + 26, 'text-anchor': 'middle', fill: '#5d6984', 'font-size': 14, 'font-family': 'IBM Plex Mono, monospace' }, svg); t.textContent = '09 h ' + fmt2(m); });
  let band = ''; for (let m = 0; m <= 40; m += .5) band += (band ? 'L' : 'M') + xm(m) + ',' + yv(46 + Math.sin(m / 6) * 3 + 9);
  for (let m = 40; m >= 0; m -= .5) band += 'L' + xm(m) + ',' + yv(46 + Math.sin(m / 6) * 3 - 9);
  svgEl('path', { d: band + 'Z', fill: 'rgba(69,137,255,.14)' }, svg);
  const mk = (m, c, label, y) => { const g = svgEl('g', {}, svg); svgEl('line', { x1: xm(m), x2: xm(m), y1: Y1, y2: Y0, stroke: c, 'stroke-width': 2, 'stroke-dasharray': '4 5' }, g); const t = svgEl('text', { x: xm(m) + 8, y, fill: c, 'font-size': 14, 'font-family': 'IBM Plex Mono, monospace' }, g); t.textContent = label; return g; };
  const chg = mk(21, '#f1c21b', '09 h 21 changement BGP', Y1 + 14);
  const rb = recover ? mk(31, '#42be65', '09 h 31 retour arrière', Y1 + 36) : null;
  let d = ''; for (let m = 0; m <= 40; m += .1) d += (d ? 'L' : 'M') + xm(m).toFixed(1) + ',' + yv(util(m, recover)).toFixed(1);
  const defs = svgEl('defs', {}, svg); const cp = svgEl('clipPath', { id: svgId.slice(1) + 'clip' }, defs); const cr = svgEl('rect', { x: 0, y: 0, width: 0, height: 400 }, cp);
  const line = svgEl('path', { d, fill: 'none', stroke: '#33b1ff', 'stroke-width': 3, 'clip-path': `url(#${svgId.slice(1)}clip)` }, svg);
  return { cr, xm, chg, rb, line };
}
const ch4 = makeChart('#c4', false), ch9 = makeChart('#c9', true);

// Detect timeline
const TL5 = [['09 h 21', 'Politique BGP modifiée'], ['09 h 22', 'Le trafic change de chemin'], ['09 h 23', 'L’utilisation s’écarte'], ['09 h 24', 'La latence augmente'], ['09 h 25', 'La perte s’étend'], ['09 h 26', 'Impact d’affaires']];
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
const IND_T = [1, 10.4, 19.8, 29.2, 38.6, 48, 57.4];

// Canada–U.S. architecture topology
const A17 = $('#arch17svg');
const N17 = { van: [140, 150, 'CD Vancouver', 'dc'], tor: [640, 200, 'CD Toronto', 'dc'], mtl: [1030, 140, 'CD Montréal', 'dc'],
  cloud: [380, 60, 'Nuage · AWS · Azure', 'cloud'], isp: [860, 50, 'Internet · 2 FAI', 'isp'],
  sfo: [140, 470, 'San Francisco', 'site'], chi: [520, 430, 'Chicago', 'site'], nyc: [1000, 440, 'New York', 'site'], atl: [760, 540, 'Atlanta', 'site'] };
const L17 = [ ['van','tor','#4589ff',6,'',0], ['tor','mtl','#4589ff',6,'CHEMIN A',0], ['van','mtl','#4589ff',6,'',0],
  ['van','tor','#a56eff',2.5,'',1], ['tor','mtl','#a56eff',2.5,'CHEMIN B',1], ['van','mtl','#a56eff',2.5,'',1],
  ['sfo','van','#33b1ff',2,'',2], ['chi','tor','#33b1ff',2,'',2], ['atl','tor','#33b1ff',2,'',2], ['nyc','mtl','#33b1ff',2,'',2], ['nyc','tor','#33b1ff',1.5,'',2],
  ['van','cloud','#8b97b3',1.5,'',3], ['tor','cloud','#8b97b3',1.5,'',3], ['tor','isp','#8b97b3',1.5,'eBGP',3], ['mtl','isp','#8b97b3',1.5,'',3] ];
{ const by = 330; svgEl('line', { x1: 0, x2: 1180, y1: by, y2: by, stroke: '#fa4d56', 'stroke-opacity': .5, 'stroke-dasharray': '8 7', 'stroke-width': 1.5 }, A17);
  const t1 = svgEl('text', { x: 20, y: by - 10, fill: '#ff8389', 'font-size': 13, 'letter-spacing': '.2em', 'font-family': 'IBM Plex Mono, monospace' }, A17); t1.textContent = 'CANADA';
  const t2 = svgEl('text', { x: 20, y: by + 22, fill: '#8b97b3', 'font-size': 13, 'letter-spacing': '.2em', 'font-family': 'IBM Plex Mono, monospace' }, A17); t2.textContent = 'ÉTATS-UNIS'; }
const pk17 = L17.map(([a, b, c, w, lab, kind], i) => {
  let [x1, y1] = N17[a], [x2, y2] = N17[b];
  if (kind === 1) { // 25 Gb/s backup drawn parallel to its 100 Gb/s primary (HA mesh)
    const dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy), o = 26, nx = -dy / L * o, ny = dx / L * o, mx = (x1 + x2) / 2 - 603, my = (y1 + y2) / 2 - 163, sg = (nx * mx + ny * my) >= 0 ? 1 : -1; // outward from the DC triangle
    x1 += nx * sg; y1 += ny * sg; x2 += nx * sg; y2 += ny * sg; }
  const g = svgEl('g', { 'data-in': String(kind === 0 ? 2 : kind === 1 ? 3.2 : kind === 2 ? 4.2 : 5.2), 'data-fx': 'fade' }, A17);
  svgEl('line', Object.assign({ x1, y1, x2, y2, stroke: c, 'stroke-opacity': .55, 'stroke-width': w }, kind >= 1 ? { 'stroke-dasharray': kind === 2 ? '9 7' : kind === 3 ? '3 5' : '12 6' } : {}), g);
  if (lab) { const t = svgEl('text', { x: (x1 + x2) / 2, y: (y1 + y2) / 2 + (kind === 1 ? 24 : -14), 'text-anchor': 'middle', fill: c, 'font-size': 14, 'font-family': 'IBM Plex Mono, monospace' }, g); t.textContent = lab; }
  const p = svgEl('circle', { r: 4, fill: kind === 3 ? '#c6d0e6' : c }, g);
  return { x1, y1, x2, y2, p, sp: .18 + (i % 4) * .06, off: i * .29 };
});
for (const k in N17) { const [x, y, label, kind] = N17[k];
  const g = svgEl('g', { transform: `translate(${x},${y})` }, A17);
  if (kind === 'dc') svgEl('rect', { x: -16, y: -16, width: 32, height: 32, rx: 6, fill: '#4589ff', stroke: '#04060d', 'stroke-width': 3 }, g);
  else if (kind === 'site') svgEl('circle', { r: 10, fill: '#33b1ff', stroke: '#04060d', 'stroke-width': 3 }, g);
  else svgEl('circle', { r: 12, fill: kind === 'cloud' ? '#a56eff' : '#8b97b3', stroke: '#04060d', 'stroke-width': 3 }, g);
  const t = svgEl('text', { y: kind === 'dc' ? -26 : -18, 'text-anchor': 'middle', fill: '#dfe6f5', 'font-size': kind === 'dc' ? 18 : 15, 'font-weight': kind === 'dc' ? 600 : 400, 'font-family': 'IBM Plex Sans, sans-serif' }, g); t.textContent = label; }
{ const lg = svgEl('g', { transform: 'translate(20,585)' }, A17);
  [['Cœur MPLS · 100 Gb/s', '#4589ff', ''], ['Relève · 25 Gb/s', '#a56eff', '12 6'], ['Superposition SD-WAN', '#33b1ff', '9 7'], ['BGP · nuage / FAI', '#8b97b3', '3 5']].forEach(([n, c, d], i) => {
    svgEl('line', Object.assign({ x1: i * 262, x2: i * 262 + 28, y1: -5, y2: -5, stroke: c, 'stroke-width': 3 }, d ? { 'stroke-dasharray': d } : {}), lg);
    const t = svgEl('text', { x: i * 262 + 38, y: 0, fill: '#8b97b3', 'font-size': 14, 'font-family': 'IBM Plex Mono, monospace' }, lg); t.textContent = n; }); }


"""

CUSTOM = """const custom = {
  s0(lt) {},
  s1(lt) {},
""" + s2s3.replace("$('#sweep3')", "($('#sweep3') || {style:{}})") + """  s2(lt) {
    for (let i = 0; i < 5; i++) { const n = $('#c2n' + i); n && n.classList.toggle('hot', lt > 22 + i * 1.1 && lt < 24.2 + i * 1.1); }
  },
  s17(lt) { pk17.forEach(l => { const a = ((lt * l.sp + l.off) % 1); l.p.setAttribute('cx', lerp(l.x1, l.x2, a)); l.p.setAttribute('cy', lerp(l.y1, l.y2, a)); }); },
  s4(lt) { ch4.cr.setAttribute('width', ch4.xm(lerp(0, 28, easeInOut(clamp((lt - 2) / 11)))) + 2); },
  s5(lt) {
    const p = clamp((lt - 3) / 9); const reach = p * 3;
    for (let i = 0; i < 6; i++) { const n = $('#tn' + i); n.classList.toggle('on', i <= reach + .001 && i < 3); n.classList.toggle('hit', i === 3 && reach >= 3); n.classList.toggle('gone', i > 3 && lt > 13); }
    $('#tl5bar') ; tl5bar.setAttribute('x2', 120 + reach * 297);
    const d = $('#det5'); d.style.opacity = clamp((lt - 12) / .4); d.style.transform = `translateX(-50%) scale(${lerp(1.3, 1, easeOut(clamp((lt - 12) / .4)))})`;
  },
  s6(lt) {
    let a = -1; IND_T.forEach((t, i) => { if (lt >= t) a = i; });
    for (let i = 0; i < 7; i++) { const c = $('#ind' + i); c.classList.toggle('act', i === a); c.classList.toggle('dim', i !== a); }
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
