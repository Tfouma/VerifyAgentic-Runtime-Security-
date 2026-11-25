"""Applies the French translation to build_film.py (source text) and timeline.json.

    python3 translate_fr.py        # run once on fresh copies of the CA edition sources

Then: python3 build_film.py ../sevone-film-part2/film.html && python3 translate_fr.py --page
(--page translates the player, panel and HUD strings that come from the shared engine.)
"""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent

SRC = [
 # --- industries
 ("('BANKING', 'Payments and digital channels', 'Branch · ATM · mobile → SD-WAN / MPLS → firewalls · load balancers → DC and cloud → payments',", "('BANQUE', 'Paiements et canaux numériques', 'Succursale · GAB · mobile → SD-WAN / MPLS → pare-feu · répartiteurs → CD et nuage → paiements',"),
 ("'Transaction latency, channel availability, operational-resilience exposure', ['latency', 'loss', 'WAN util.', 'interface errors', 'availability'], ''),", "'Latence transactionnelle, disponibilité des canaux, résilience opérationnelle', ['latence', 'perte', 'util. WAN', 'erreurs d’interface', 'disponibilité'], ''),"),
 ("('TELECOM', 'Customer services and SLAs', 'Access → IP/MPLS core → backbone → peering and transit',", "('TÉLÉCOM', 'Services clients et SLA', 'Accès → cœur IP/MPLS → dorsale → peering et transit',"),
 ("'SLA penalties, service degradation, avoidable NOC escalations', ['loss', 'jitter', 'utilization', 'BGP peer state', 'SLA'], ''),", "'Pénalités de SLA, dégradation de service, escalades évitables', ['perte', 'gigue', 'utilisation', 'état des pairs BGP', 'SLA'], ''),"),
 ("('RAIL', 'Operations communications', 'Stations · depots → WAN → operations-control systems → DC',", "('FERROVIAIRE', 'Communications d’exploitation', 'Gares · dépôts → WAN → systèmes de contrôle d’exploitation → CD',"),
 ("'Communications degradation cascading into operational disruption', ['availability', 'latency', 'link errors', 'path redundancy'], 'Communications assurance, not a train-safety system'),", "'Dégradation des communications devenant perturbation opérationnelle', ['disponibilité', 'latence', 'erreurs de lien', 'redondance'], 'Assurance des communications, pas un système de sécurité ferroviaire'),"),
 ("('ENERGY', 'Grid and site communications', 'Substations · sites → WAN → control centre → DC and cloud',", "('ÉNERGIE', 'Communications du réseau et des sites', 'Postes · sites → WAN → centre de contrôle → CD et nuage',"),
 ("'Loss of visibility across operational communications', ['availability', 'latency', 'utilization', 'redundancy'], 'Monitoring stays separate from safety and OT control'),", "'Perte de visibilité sur les communications d’exploitation', ['disponibilité', 'latence', 'utilisation', 'redondance'], 'La surveillance reste distincte de la sécurité et du contrôle OT'),"),
 ("('GOVERNMENT', 'Citizen and critical services', 'Citizen portal → government DC → cloud → agency networks',", "('GOUVERNEMENT', 'Services aux citoyens et essentiels', 'Portail citoyen → CD gouvernemental → nuage → réseaux des organismes',"),
 ("'Citizen-service outages, emergency-service delays, accountability', ['availability', 'response time', 'SLA', 'capacity'], ''),", "'Pannes de services, retards des services d’urgence, reddition de comptes', ['disponibilité', 'temps de réponse', 'SLA', 'capacité'], ''),"),
 ("('AI & DATA', 'GPU clusters and data pipelines', 'Data sources → fabric → GPU cluster ↔ storage → cloud',", "('IA ET DONNÉES', 'Grappes GPU et pipelines de données', 'Sources de données → fabric → grappe GPU ↔ stockage → nuage',"),
 ("'Expensive GPUs idle while data paths congest', ['east-west throughput', 'drops', 'latency', 'utilization'], 'AI infrastructure is also network infrastructure'),", "'Des GPU coûteux inactifs quand les chemins saturent', ['débit est-ouest', 'pertes', 'latence', 'utilisation'], 'L’infrastructure d’IA est aussi une infrastructure réseau'),"),
 ('<b style="color:#ffb3b8;font-weight:600">Risk ·</b>', '<b style="color:#ffb3b8;font-weight:600">Risque ·</b>'),
 # --- risk controls
 ("('Preventive', 'Should this change happen?', 'Baseline and capacity evidence informs pre-change decisions', 'IAM · PAM · change policy · CAB · agent guardrails'),", "('Préventif', 'Ce changement doit-il avoir lieu ?', 'Lignes de base et capacité éclairent la décision', 'IAM · PAM · politique de changement · CAB · garde-fous'),"),
 ("('Detective', 'Is something going wrong?', 'Metrics, flows, telemetry, baselines, thresholds, anomalies, synthetics', 'SIEM · ITDR · application and OT monitoring'),", "('Détection', 'Quelque chose se dégrade-t-il ?', 'Métriques, flux, télémétrie, lignes de base, anomalies, tests synthétiques', 'SIEM · ITDR · surveillance applicative et OT'),"),
 ("('Diagnostic', 'What happened, and where?', 'Interface, device, path and flow context', 'AIOps · topology · tracing · logs'),", "('Diagnostic', 'Que s’est-il passé, et où ?', 'Contexte interface, équipement, chemin et flux', 'AIOps · topologie · traçage · journaux'),"),
 ("('Corrective', 'What should happen now?', 'Events and alerts feed downstream response', 'ITSM · SOAR · Ansible · Terraform · runbooks'),", "('Correctif', 'Que faire maintenant ?', 'Événements et alertes alimentent la réponse', 'ITSM · SOAR · Ansible · Terraform · procédures'),"),
 ("('Verification', 'Did remediation work?', 'Re-measure behaviour against baseline and KPIs', 'ITSM closure controls · SRE error budgets'),", "('Vérification', 'La remédiation a-t-elle fonctionné ?', 'Nouvelle mesure face à la ligne de base et aux KPI', 'Contrôles de fermeture ITSM · budgets d’erreur SRE'),"),
 ("('Evidence', 'Can we show the outcome?', 'Historical performance, SLA and capacity records', 'CMDB · change records · audit logs · GRC'),", "('Preuve', 'Peut-on démontrer le résultat ?', 'Historique de performance, de SLA et de capacité', 'CMDB · dossiers de changement · journaux d’audit · GRC'),"),
 # --- KPIs
 ("KPIS = [('Critical services within SLA', '98.7%', 'green'), ('Critical paths within baseline', '94.2%', ''), ('Critical asset observability coverage', '97.8%', ''),", "KPIS = [('Services critiques dans le SLA', '98,7 %', 'green'), ('Chemins critiques dans la ligne de base', '94,2 %', ''), ('Couverture d’observabilité des actifs critiques', '97,8 %', ''),"),
 ("('Active network anomalies', '17', ''), ('High-impact anomalies', '2', 'red'), ('Capacity-at-risk circuits', '4', 'yellow'),", "('Anomalies réseau actives', '17', ''), ('Anomalies à fort impact', '2', 'red'), ('Circuits à capacité à risque', '4', 'yellow'),"),
 ("('Automated changes today', '126', ''), ('Changes followed by anomalies', '3', 'yellow'), ('Verified remediations', '11 / 12', 'green'), ('Network-related MTTR', '21 min', 'cyan')]", "('Changements automatisés aujourd’hui', '126', ''), ('Changements suivis d’anomalies', '3', 'yellow'), ('Remédiations vérifiées', '11 / 12', 'green'), ('MTTR lié au réseau', '21 min', 'cyan')]"),
 # --- assessment
 ("ASSESS = ['Current network visibility', 'AI and automation use cases', 'Critical network dependencies', 'Existing telemetry coverage', 'BGP, WAN and SD-WAN visibility',", "ASSESS = ['Visibilité actuelle du réseau', 'Cas d’usage IA et automatisation', 'Dépendances réseau critiques', 'Couverture de télémétrie existante', 'Visibilité BGP, WAN et SD-WAN',"),
 ("'Baseline and anomaly-detection maturity', 'Change-impact validation', 'Incident and remediation workflows', 'Observability gaps', 'Opportunities for closed-loop assurance']", "'Maturité des lignes de base et de la détection', 'Validation de l’impact des changements', 'Processus d’incident et de remédiation', 'Angles morts d’observabilité', 'Occasions d’assurance en boucle fermée']"),
 # --- S0 / S1
 ('MONDAY · 09:20', 'LUNDI · 09 h 20'),
 ('data-type="AI accelerates operations."', 'data-type="L’IA accélère les opérations."'),
 ('It also accelerates <span class="red">change</span>.', 'Elle accélère aussi le <span class="red">changement</span>.'),
 ('Critical infrastructure runs on the network', 'Les infrastructures critiques reposent sur le réseau'),
 ('Every critical service depends on the network, <span class="grad">and on the agents that now change it</span>.', 'Chaque service critique dépend du réseau, <span class="grad">et des agents qui le modifient désormais</span>.'),
 ("['On-prem data centres', 'Private cloud', 'AWS · Azure', 'WAN · MPLS', 'SD-WAN', 'BGP edge', 'DC fabrics', 'Wi-Fi', 'OT boundary']", "['Centres de données sur site', 'Nuage privé', 'AWS · Azure', 'WAN · MPLS', 'SD-WAN', 'Bordure BGP', 'Fabrics de CD', 'Wi-Fi', 'Frontière OT']"),
 # --- S17 architecture
 ("stephead('THE NETWORK', 'Canadian data centers · U.S. sites · BGP · SD-WAN', 'Three Canadian data centers. Four U.S. sites. <span class=\"cyan\">One hybrid WAN.</span>')", "stephead('LE RÉSEAU', 'Centres de données canadiens · sites américains · BGP · SD-WAN', 'Canada et États-Unis : <span class=\"cyan\">un seul WAN hybride</span>.')"),
 ('<h4>Topology · MPLS core · SD-WAN overlay · BGP edge</h4>', '<h4>Topologie · cœur MPLS · superposition SD-WAN · bordure BGP</h4>'),
 ('<div class="k">Data centers</div><div class="v">Montréal · Toronto · Vancouver</div>', '<div class="k">Centres de données</div><div class="v">Montréal · Toronto · Vancouver</div>'),
 ('<div class="k">U.S. sites</div>', '<div class="k">Sites américains</div>'),
 ('<div class="k">Core</div><div class="v">MPLS · path A 10 Gb/s · path B 1 Gb/s</div>', '<div class="k">Cœur</div><div class="v">MPLS · chemin A 10 Gb/s · chemin B 1 Gb/s</div>'),
 ('<div class="k">Routing</div><div class="v">BGP AS 65010 · iBGP between DCs · eBGP to 2 ISPs</div>', '<div class="k">Routage</div><div class="v">BGP AS 65010 · iBGP entre CD · eBGP vers 2 FAI</div>'),
 ('<div class="k">Overlay</div><div class="v">SD-WAN · MPLS + internet transports</div>', '<div class="k">Superposition</div><div class="v">SD-WAN · transports MPLS + Internet</div>'),
 ('<div class="k">Critical flows</div><div class="v">payments · replication · VoIP · SAP</div>', '<div class="k">Flux critiques</div><div class="v">paiements · réplication · VoIP · SAP</div>'),
 ('<div class="k">Observed by</div><div class="v">SevOne · SNMP · flow · gNMI · SD-WAN tunnels</div>', '<div class="k">Observé par</div><div class="v">SevOne · SNMP · flux · gNMI · tunnels SD-WAN</div>'),
 ('<h4>Architecture</h4>', '<h4>Architecture</h4>'),
 # --- S2
 ("stephead('AGENTIC OPERATIONS', 'Human and policy → agent → approved automation → network', 'A routine optimization, <span class=\"cyan\">done the right way</span>.')", "stephead('OPÉRATIONS AGENTIQUES', 'Humain et politique → agent → automatisation approuvée → réseau', 'Une optimisation de routine, <span class=\"cyan\">faite dans les règles</span>.')"),
 ('ENGINEER → AI OPERATIONS AGENT', 'INGÉNIEUR → AGENT D’IA DES OPÉRATIONS'),
 ('“Optimize connectivity between Montréal and Toronto while maintaining application performance.”', '« Optimise la connectivité entre Montréal et Toronto sans dégrader la performance des applications. »'),
 ('agent ▸ analyzed 30 days of telemetry · proposes BGP local-preference change on 48 edge routers to prefer path B', 'agent ▸ 30 jours de télémétrie analysés · propose de modifier la local-preference BGP sur 48 routeurs pour privilégier le chemin B'),
 ('<div class="v">Human &amp; policy</div><div class="s">objective, guardrails</div>', '<div class="v">Humain et politique</div><div class="s">objectif, garde-fous</div>'),
 ('<div class="v">AI agent</div><div class="s">analysis, proposal</div>', '<div class="v">Agent d’IA</div><div class="s">analyse, proposition</div>'),
 ('<div class="v">Change approval</div><div class="s">policy · CAB · ticket</div>', '<div class="v">Approbation</div><div class="s">politique · CAB · billet</div>'),
 ('<div class="v">Automation platform</div><div class="s">Ansible · Terraform · controller</div>', '<div class="v">Automatisation</div><div class="s">Ansible · Terraform · contrôleur</div>'),
 ('<div class="v">Network</div><div class="s">48 edge routers</div>', '<div class="v">Réseau</div><div class="s">48 routeurs de bordure</div>'),
 ('No magic. <b>Approved, governed change</b>, executed through automation.', 'Pas de magie. <b>Un changement approuvé et encadré</b>, exécuté par l’automatisation.'),
 # --- S18 config
 ("stephead('01 — THE CHANGE', 'AI-generated configuration · BGP + SD-WAN', 'The agent writes the config, <span class=\"cyan\">and pushes it</span>.')", "stephead('01 — LE CHANGEMENT', 'Configuration générée par l’IA · BGP + SD-WAN', 'L’agent rédige la configuration, <span class=\"cyan\">et la pousse</span>.')"),
 ('<h4>BGP · IOS-XE · 48 edge routers</h4>', '<h4>BGP · IOS-XE · 48 routeurs de bordure</h4>'),
 ('<h4>SD-WAN · centralized policy · SD-WAN Manager</h4>', '<h4>SD-WAN · politique centralisée · SD-WAN Manager</h4>'),
 ('✓ Syntax valid<', '✓ Syntaxe valide<'), ('✓ Lint passed<', '✓ Lint réussi<'), ('✓ Dry run: BGP peers stay up<', '✓ Simulation : pairs BGP actifs<'),
 ('✓ Approved · CHG0052418<', '✓ Approuvé · CHG0052418<'), ('✓ Pushed: 48 routers + SD-WAN Manager<', '✓ Poussé : 48 routeurs + SD-WAN Manager<'),
 ('Every check the agent knows how to run <b>passes</b>.', 'Toutes les vérifications que l’agent sait faire <b>réussissent</b>.'),
 # --- S3
 ("stephead('01 — THE CHANGE', 'Technical execution', 'The automation platform reports <span class=\"green\">success</span>.')", "stephead('01 — LE CHANGEMENT', 'Exécution technique', 'La plateforme d’automatisation annonce un <span class=\"green\">succès</span>.')"),
 ('<div class="v">✓ CHANGE<br>SUCCESSFUL</div><div class="s">no configuration errors<br>no devices down<br>BGP established</div>', '<div class="v">✓ CHANGEMENT<br>RÉUSSI</div><div class="s">aucune erreur de configuration<br>aucun équipement en panne<br>BGP établi</div>'),
 ('But did the <span class="red">business outcome</span> succeed?', 'Mais le <span class="red">résultat d’affaires</span> est-il au rendez-vous ?'),
 # --- S4
 ("stephead('02 — DETECT', 'Baseline deviation · independent telemetry', 'The change succeeded. <span class=\"red\">The outcome didn’t.</span>')", "stephead('02 — DÉTECTER', 'Écart à la ligne de base · télémétrie indépendante', 'Le changement a réussi. <span class=\"red\">Pas le résultat.</span>')"),
 ('<div class="k">WAN utilization · MTL ↔ TOR</div>', '<div class="k">Utilisation WAN · MTL ↔ TOR</div>'),
 ('<div class="k">Latency · payments path</div>', '<div class="k">Latence · chemin des paiements</div>'),
 ('<div class="k">Packet loss</div><div class="row"><span class="mb">0.1%</span>', '<div class="k">Perte de paquets</div><div class="row"><span class="mb">0,1 %</span>'),
 ('<div class="k">BGP sessions</div><div class="row"><span class="ma green" style="font-size:34px">ESTABLISHED</span>', '<div class="k">Sessions BGP</div><div class="row"><span class="ma green" style="font-size:34px">ÉTABLIES</span>'),
 ('<h4>WAN utilization · Toronto edge · % · learned baseline band</h4>', '<h4>Utilisation WAN · bordure de Toronto · % · bande de la ligne de base</h4>'),
 ('DEVIATION FROM BASELINE · 09:23', 'ÉCART À LA LIGNE DE BASE · 09 h 23'),
 ('<div class="sp h"><div>Automation says</div><div>Network assurance says</div></div>', '<div class="sp h"><div>L’automatisation dit</div><div>L’assurance réseau dit</div></div>'),
 ('<div class="l">✓ change applied</div><div class="r">⚠ behaviour abnormal</div>', '<div class="l">✓ changement appliqué</div><div class="r">⚠ comportement anormal</div>'),
 ('<div class="l">✓ BGP established</div><div class="r">⚠ traffic shifted</div>', '<div class="l">✓ BGP établi</div><div class="r">⚠ trafic déplacé</div>'),
 ('<div class="l">✓ devices operational</div><div class="r">⚠ latency rising</div>', '<div class="l">✓ équipements en service</div><div class="r">⚠ latence en hausse</div>'),
 ('<div class="l">✓ zero errors</div><div class="r">⚠ service risk emerging</div>', '<div class="l">✓ zéro erreur</div><div class="r">⚠ risque de service émergent</div>'),
 ('Demo scenario values · telemetry via SNMP, flow and gNMI streaming (gNMI in Public Preview)', 'Valeurs de scénario de démonstration · télémétrie SNMP, flux et gNMI (gNMI en préversion publique)'),
 # --- S5
 ("stephead('02 — DETECT', 'Degradation, not failure', 'Don’t wait for DOWN. <span class=\"cyan\">Detect while services are still UP.</span>')", "stephead('02 — DÉTECTER', 'Dégradation, pas panne', 'N’attendez pas la panne. <span class=\"cyan\">Détectez pendant que tout fonctionne.</span>')"),
 ('SEVONE DETECTS · 09:24', 'SEVONE DÉTECTE · 09 h 24'),
 ('<div class="k">BASELINES</div><div class="v">learned per path, per hour</div>', '<div class="k">LIGNES DE BASE</div><div class="v">apprises par chemin, par heure</div>'),
 ('<div class="k">FLOW</div><div class="v">NetFlow · IPFIX: who moved where</div>', '<div class="k">FLUX</div><div class="v">NetFlow · IPFIX : qui est allé où</div>'),
 ('<div class="k">TELEMETRY</div><div class="v">SNMP · gNMI streaming (Public Preview)</div>', '<div class="k">TÉLÉMÉTRIE</div><div class="v">SNMP · gNMI en continu (préversion publique)</div>'),
 ('<div class="k">SYNTHETICS</div><div class="v">service-path tests from the user’s view</div>', '<div class="k">TESTS SYNTHÉTIQUES</div><div class="v">chemins de service vus par l’utilisateur</div>'),
 # --- S6
 ("stephead('03 — IMPACT', 'Same signal · different business risk', 'One deviation. <span class=\"cyan\">Six business consequences.</span>')", "stephead('03 — IMPACT', 'Même signal · risques d’affaires différents', 'Un écart. <span class=\"cyan\">Six conséquences d’affaires.</span>')"),
 # --- S7
 ("stephead('04 — DIAGNOSE', 'Root-cause analysis · blast radius', 'From symptom to cause, <span class=\"cyan\">with evidence</span>.')", "stephead('04 — DIAGNOSTIQUER', 'Analyse de cause racine · rayon d’impact', 'Du symptôme à la cause, <span class=\"cyan\">preuves à l’appui</span>.')"),
 ('<div class="k">SYMPTOM</div><div class="v">Latency 63 ms on the payments path (baseline 18 ms)</div>', '<div class="k">SYMPTÔME</div><div class="v">Latence de 63 ms sur le chemin des paiements (ligne de base 18 ms)</div>'),
 ('<div class="k">SCOPE</div><div class="v">Toronto edge · 3 WAN circuits · 2 critical services</div>', '<div class="k">PORTÉE</div><div class="v">Bordure de Toronto · 3 circuits WAN · 2 services critiques</div>'),
 ('<div class="k">PATH</div><div class="v">BGP best path moved from path A (10 Gb/s) to path B (1 Gb/s)</div>', '<div class="k">CHEMIN</div><div class="v">Meilleur chemin BGP : du chemin A (10 Gb/s) au chemin B (1 Gb/s)</div>'),
 ('<div class="k">FLOW</div><div class="v">Top talkers on path B: replication 38% · payments 22%</div>', '<div class="k">FLUX</div><div class="v">Principaux flux sur le chemin B : réplication 38 % · paiements 22 %</div>'),
 ('<div class="k" style="color:var(--yellow)">CHANGE</div><div class="v">09:21 BGP policy update · CHG0052418 · AI-proposed, approved</div>', '<div class="k" style="color:var(--yellow)">CHANGEMENT</div><div class="v">09 h 21 politique BGP · CHG0052418 · proposé par l’IA, approuvé</div>'),
 ('<h4>Blast radius</h4>', '<h4>Rayon d’impact</h4>'),
 ('<span>BGP path · path B</span><span class="m">route</span>', '<span>Chemin BGP · chemin B</span><span class="m">route</span>'),
 ('<span>WAN circuit · 1 Gb/s</span><span class="m">82% util.</span>', '<span>Circuit WAN · 1 Gb/s</span><span class="m">util. 82 %</span>'),
 ('<span>Toronto edge</span><span class="m">queue drops</span>', '<span>Bordure de Toronto</span><span class="m">rejets en file</span>'),
 ('<span>Cloud connectivity</span><span class="m">63 ms</span>', '<span>Connectivité infonuagique</span><span class="m">63 ms</span>'),
 ('<span>Critical banking service</span><span class="m">at risk</span>', '<span>Service bancaire critique</span><span class="m">à risque</span>'),
 ("enumerate(['What changed?', 'Where?', 'What is abnormal?', 'What could be affected?', 'How urgent?'])", "enumerate(['Qu’est-ce qui a changé ?', 'Où ?', 'Quelle anomalie ?', 'Quel impact ?', 'Quelle urgence ?'])"),
 # --- S19 issues
 ("stephead('04 — DIAGNOSE', 'Valid configuration · wrong outcome', 'Valid config. <span class=\"red\">Wrong outcome.</span> Three issues, explained.')", "stephead('04 — DIAGNOSTIQUER', 'Configuration valide · mauvais résultat', 'Configuration valide. <span class=\"red\">Mauvais résultat.</span> Trois problèmes expliqués.')"),
 ('ISSUE 1 · BGP ROUTE-MAP SCOPE', 'PROBLÈME 1 · PORTÉE DE LA ROUTE-MAP BGP'),
 ('The route-map matches every prefix', 'La route-map s’applique à tous les préfixes'),
 ('Payments and replication move to the 1 Gb/s path B along with the bulk traffic it was meant for.', 'Paiements et réplication passent sur le chemin B à 1 Gb/s, avec le trafic de masse visé.'),
 ('Flow top talkers on path B: replication 38%, payments 22%. BGP best path changed on 96 sessions (gNMI BGP data, Public Preview).', 'Principaux flux sur le chemin B : réplication 38 %, paiements 22 %. Meilleur chemin BGP modifié sur 96 sessions (données BGP gNMI, préversion publique).'),
 ('Match only the bulk-traffic prefix-list; keep payments on path A.', 'Cibler uniquement la prefix-list du trafic de masse ; garder les paiements sur le chemin A.'),
 ('ISSUE 2 · SD-WAN SLA THRESHOLDS', 'PROBLÈME 2 · SEUILS DE SLA SD-WAN'),
 ('The SLA class is far looser than reality', 'La classe de SLA est bien trop permissive'),
 ('Payments normally run at 18 ms and 0.1% loss. At 63 ms and 2.1% the path still counts as compliant, so SD-WAN never steers away.', 'Les paiements tournent normalement à 18 ms et 0,1 % de perte. À 63 ms et 2,1 %, le chemin reste « conforme » : le SD-WAN ne redirige rien.'),
 ('SD-WAN tunnel monitoring TOR–MTL: latency 63 ms, loss 2.1%, jitter rising, while the policy reports the SLA met.', 'Surveillance des tunnels SD-WAN TOR–MTL : latence 63 ms, perte 2,1 %, gigue en hausse, alors que la politique déclare le SLA respecté.'),
 ('Derive SLA thresholds from SevOne baselines, e.g. 40 ms and 0.5% loss.', 'Dériver les seuils des lignes de base SevOne, p. ex. 40 ms et 0,5 % de perte.'),
 ('ISSUE 3 · NO OUTCOME CHECK', 'PROBLÈME 3 · AUCUNE VÉRIFICATION DU RÉSULTAT'),
 ('Success was defined as “config applied”', 'Le succès = « configuration appliquée »'),
 ('success criteria:\nsyntax ✓ · lint ✓ · peers up ✓', 'critères de succès :\nsyntaxe ✓ · lint ✓ · pairs actifs ✓'),
 ('Nobody checked utilization, latency, loss or flows on the new path, or what the BGP and SD-WAN changes did together.', 'Personne n’a vérifié l’utilisation, la latence, la perte ou les flux du nouveau chemin, ni l’effet combiné des changements BGP et SD-WAN.'),
 ('Baseline deviation at 09:23, two minutes after CHG0052418, correlated with the change and its actor.', 'Écart à la ligne de base à 09 h 23, deux minutes après CHG0052418, corrélé au changement et à son auteur.'),
 ('Add a post-change outcome gate: query SevOne before a change is marked successful.', 'Ajouter une validation du résultat : interroger SevOne avant de déclarer un changement réussi.'),
 ('<div class="lb">What it did</div>', '<div class="lb">Effet</div>'),
 ('data-fx="fade">How SevOne saw it</div>', 'data-fx="fade">Ce que SevOne a vu</div>'),
 ('data-fx="fade">Fix</div>', 'data-fx="fade">Correctif</div>'),
 ('SevOne doesn’t read intent. <b>It measures the outcome</b>, and the outcome exposed all three.', 'SevOne ne lit pas l’intention. <b>Il mesure le résultat</b>, et le résultat a révélé les trois.'),
 # --- S8
 ("stephead('05 — RESPOND', 'Automatic ticket · routing · L1/L2 automated · L3 human', 'From evidence to action, <span class=\"cyan\">inside your processes</span>.')", "stephead('05 — RÉPONDRE', 'Billet automatique · acheminement · N1/N2 automatisés · N3 humain', 'De la preuve à l’action, <span class=\"cyan\">dans vos processus</span>.')"),
 ('<div class="h">SevOne</div><div class="s">condition raised</div>', '<div class="h">SevOne</div><div class="s">condition levée</div>'),
 ('<div class="h">Event</div><div class="s">AIOps · correlation</div>', '<div class="h">Événement</div><div class="s">AIOps · corrélation</div>'),
 ('<div class="h">Ticket</div><div class="s">ServiceNow, auto</div>', '<div class="h">Billet</div><div class="s">ServiceNow, auto</div>'),
 ('<div class="h">Route</div><div class="s">NetOps · DevSecOps</div>', '<div class="h">Acheminer</div><div class="s">NetOps · DevSecOps</div>'),
 ('<div class="n">L1</div><div class="h">Triage</div><div class="s">evidence pack</div><span class="tag ok">AUTOMATED</span>', '<div class="n">N1</div><div class="h">Triage</div><div class="s">dossier de preuves</div><span class="tag ok">AUTOMATISÉ</span>'),
 ('<div class="n">L2</div><div class="h">Propose</div><div class="s">rollback plan</div><span class="tag ok">AUTOMATED</span>', '<div class="n">N2</div><div class="h">Proposer</div><div class="s">plan de retour</div><span class="tag ok">AUTOMATISÉ</span>'),
 ('<div class="n">L3</div><div class="h">Approve</div><div class="s">engineer decides</div><span class="tag watch">HUMAN</span>', '<div class="n">N3</div><div class="h">Approuver</div><div class="s">l’ingénieur décide</div><span class="tag watch">HUMAIN</span>'),
 ('ServiceNow · Incident <span class="n">INC0051207</span><span class="st">AUTO-CREATED · 7 s</span>', 'ServiceNow · Incident <span class="n">INC0051207</span><span class="st">CRÉÉ AUTOMATIQUEMENT · 7 s</span>'),
 ('<div class="k">Config item</div><div>edge-tor-07 · synced from CMDB</div>', '<div class="k">Élément de config.</div><div>edge-tor-07 · synchronisé depuis la CMDB</div>'),
 ('<div class="k">Business service</div><div>Digital payments · Tier 1</div>', '<div class="k">Service d’affaires</div><div>Paiements numériques · niveau 1</div>'),
 ('<div class="k">Priority</div><div><span class="yellow">P2</span> · impact 2 · urgency 1</div>', '<div class="k">Priorité</div><div><span class="yellow">P2</span> · impact 2 · urgence 1</div>'),
 ('<div class="k">Related change</div><div>CHG0052418 · AI-proposed BGP update</div>', '<div class="k">Changement lié</div><div>CHG0052418 · mise à jour BGP proposée par l’IA</div>'),
 ('<div class="k">Evidence</div><div>baseline chart · path diff · top flows</div>', '<div class="k">Preuves</div><div>graphique de base · écart de chemin · principaux flux</div>'),
 ('<div class="k">L1 · automated</div><div class="v">Triage: evidence pack attached, NetOps paged</div>', '<div class="k">N1 · automatisé</div><div class="v">Triage : dossier de preuves joint, NetOps alerté</div>'),
 ('<div class="k">L2 · automated</div><div class="v">Diagnosis confirmed · rollback to path A proposed</div>', '<div class="k">N2 · automatisé</div><div class="v">Diagnostic confirmé · retour au chemin A proposé</div>'),
 ('<div class="k">L3 · human in the loop</div><div class="v">✓ Engineer approves the rollback</div><div class="s">automation executes · SevOne observes</div>', '<div class="k">N3 · humain dans la boucle</div><div class="v">✓ L’ingénieur approuve le retour arrière</div><div class="s">l’automatisation exécute · SevOne observe</div>'),
 # --- S9
 ("stephead('06 — VERIFY', 'Close the loop with measurement', 'A job says “done”. <span class=\"green\">The network proves it.</span>')", "stephead('06 — VÉRIFIER', 'Boucler par la mesure', 'Une tâche dit « terminé ». <span class=\"green\">Le réseau le prouve.</span>')"),
 ('<div class="k">WAN utilization</div><div class="row">', '<div class="k">Utilisation WAN</div><div class="row">'),
 ('<div class="k">Latency</div><div class="row">', '<div class="k">Latence</div><div class="row">'),
 ('<div class="k">Packet loss</div><div class="row"><span class="mb">2.1%</span>', '<div class="k">Perte de paquets</div><div class="row"><span class="mb">2,1 %</span>'),
 ('<div class="k">Service state</div><div class="row"><span class="ma green" style="font-size:34px" data-in="11">NORMAL</span>', '<div class="k">État du service</div><div class="row"><span class="ma green" style="font-size:34px" data-in="11">NORMAL</span>'),
 ('<h4>WAN utilization · rollback at 09:31 · back inside the baseline band</h4>', '<h4>Utilisation WAN · retour arrière à 09 h 31 · de retour dans la ligne de base</h4>'),
 ('<h4>Assurance loop</h4>', '<h4>Boucle d’assurance</h4>'),
 ("enumerate(['OBSERVE', 'DETECT', 'UNDERSTAND', 'ACT', 'VERIFY'])", "enumerate(['OBSERVER', 'DÉTECTER', 'COMPRENDRE', 'AGIR', 'VÉRIFIER'])"),
 ('✓ INC0051207 closed only after SevOne confirms the baseline', '✓ INC0051207 fermé seulement après confirmation de SevOne'),
 # --- S10
 ("stephead('07 — CONTROL', 'Operational risk controls · due diligence', 'Network evidence across <span class=\"cyan\">every control layer</span>.')", "stephead('07 — CONTRÔLER', 'Contrôles du risque opérationnel · diligence raisonnable', 'La preuve réseau à <span class=\"cyan\">chaque niveau de contrôle</span>.')"),
 ('<div>Control</div><div>Business question</div><div>SevOne / NPM contribution</div><div>Adjacent enterprise controls</div>', '<div>Contrôle</div><div>Question d’affaires</div><div>Apport SevOne / NPM</div><div>Contrôles d’entreprise associés</div>'),
 ('Due diligence: telemetry coverage, baselines, change validation and evidence retention reviewed for every critical service. SevOne is an important source of evidence, not a compliance guarantee.', 'Diligence raisonnable : couverture de télémétrie, lignes de base, validation des changements et conservation des preuves revues pour chaque service critique. SevOne est une source de preuves importante, pas une garantie de conformité.'),
 # --- S11
 ("stephead('08 — VALUE', 'KPI setting · NPM framework · executive risk view', 'Network operational risk, <span class=\"cyan\">on one page</span>.')", "stephead('08 — VALEUR', 'Indicateurs · cadre NPM · vue de direction', 'Le risque opérationnel réseau, <span class=\"cyan\">sur une seule page</span>.')"),
 ('<div class="k">CHANGE OUTCOME ASSURANCE RATE</div>', '<div class="k">TAUX D’ASSURANCE DES RÉSULTATS DE CHANGEMENT</div>'),
 ('<div class="f">changes with a validated post-change network state<div class="ln"></div>changes requiring network validation</div>', '<div class="f">changements dont l’état réseau post-changement est validé<div class="ln"></div>changements exigeant une validation réseau</div>'),
 ('<div class="k">KPIS SET AUTOMATICALLY PER SERVICE CLASS</div>', '<div class="k">INDICATEURS DÉFINIS AUTOMATIQUEMENT PAR CLASSE DE SERVICE</div>'),
 ("for c in ['Availability', 'Performance', 'Capacity', 'Stability', 'Change', 'Coverage']", "for c in ['Disponibilité', 'Performance', 'Capacité', 'Stabilité', 'Changement', 'Couverture']"),
 ('data-in="3" style="bottom:110px">Illustrative demo values</div>', 'data-in="3" style="bottom:110px">Valeurs de démonstration illustratives</div>'),
 # --- S12
 ("stephead('08 — VALUE', 'TCO · OPEX · proof of value', 'Prove the savings. <span class=\"green\">Don’t assume them.</span>')", "stephead('08 — VALEUR', 'Coût total · dépenses d’exploitation · preuve de valeur', 'Prouvez les économies. <span class=\"green\">Ne les supposez pas.</span>')"),
 ('<div class="k red">BEFORE</div><ul><li>Several monitoring tools, duplicate dashboards</li><li>Manual thresholds and KPI configuration</li><li>Manual tickets and CMDB reconciliation</li><li>Incident war rooms, manual reports</li></ul><div class="tot red">HIGH OPERATING EFFORT</div>', '<div class="k red">AVANT</div><ul><li>Plusieurs outils de surveillance, tableaux en double</li><li>Seuils et indicateurs configurés à la main</li><li>Billets manuels et rapprochement CMDB</li><li>Cellules de crise, rapports manuels</li></ul><div class="tot red">EFFORT D’EXPLOITATION ÉLEVÉ</div>'),
 ('<div class="k green">AFTER</div><ul><li>Centralized multivendor NPM, flow and telemetry</li><li>Automated baselines and KPI policies</li><li>Automatic tickets, CMDB sync, routing</li><li>Evidence for RCA, capacity and SLA</li></ul><div class="tot green">LOWER ADDRESSABLE OPEX</div>', '<div class="k green">APRÈS</div><ul><li>NPM, flux et télémétrie multifournisseurs centralisés</li><li>Lignes de base et indicateurs automatisés</li><li>Billets automatiques, synchro CMDB, acheminement</li><li>Preuves pour l’analyse de cause, la capacité et les SLA</li></ul><div class="tot green">DÉPENSES D’EXPLOITATION ADRESSABLES RÉDUITES</div>'),
 ("[('TOOLING', 'licences + infra + support'), ('ADMINISTRATION', 'engineer hours × cost'), ('INCIDENTS', 'incidents × people × hours'), ('REPORTING', 'manual SLA reporting'), ('ONBOARDING', 'CMDB and device changes'), ('OUTAGES', 'only where data supports it')]", "[('OUTILS', 'licences + infra + soutien'), ('ADMINISTRATION', 'heures d’ingénieur × coût'), ('INCIDENTS', 'incidents × personnes × heures'), ('RAPPORTS', 'rapports de SLA manuels'), ('INTÉGRATION', 'changements CMDB et équipements'), ('PANNES', 'seulement si les données le permettent')]"),
 ('<div class="flow12" data-in="24"><span class="mb">TCO baseline</span>→<span class="mb">Proof of value</span>→<span class="mb">Measured delta</span>→<span class="b g">Business case</span></div>', '<div class="flow12" data-in="24"><span class="b">Coût actuel mesuré</span>→<span class="b">Preuve de valeur</span>→<span class="b">Écart mesuré</span>→<span class="b g">Dossier d’affaires</span></div>'),
 # --- S13
 ('<div class="who">AI agent</div><div class="say">“I completed the task.”</div>', '<div class="who">Agent d’IA</div><div class="say">« J’ai terminé la tâche. »</div>'),
 ('<div class="who">Automation platform</div><div class="say">“The configuration was deployed.”</div>', '<div class="who">Automatisation</div><div class="say">« La configuration est déployée. »</div>'),
 ('<div class="say" style="font-weight:600">“Here is what happened <span class="grad">to the network</span>.”</div>', '<div class="say" style="font-weight:600">« Voici ce qui est arrivé <span class="grad">au réseau</span>. »</div>'),
 ('The business needs all three. <b>Only independent observability verifies the outcome.</b>', 'L’entreprise a besoin des trois. <b>Seule l’observabilité indépendante vérifie le résultat.</b>'),
 # --- S14
 ('If an AI agent changed <span class="red">500 network devices</span> tonight, how quickly could you determine whether <span class="grad">every change</span> produced the intended business outcome?', 'Si un agent d’IA modifiait <span class="red">500 équipements réseau</span> cette nuit, combien de temps vous faudrait-il pour savoir si <span class="grad">chaque changement</span> a produit le résultat attendu ?'),
 # --- S15
 ('<div class="eyebrow" data-in="0.2">Concrete next step</div><div class="t" data-in="0.5" data-dur="0.8">Agentic Network Readiness &amp; <span class="cyan">Observability Assessment</span></div>', '<div class="eyebrow" data-in="0.2">Prochaine étape concrète</div><div class="t" data-in="0.5" data-dur="0.8">Évaluation de la préparation et de <span class="cyan">l’observabilité du réseau agentique</span></div>'),
 ('Outcome: a gap map, prioritized use cases, and a proof-of-value plan with measured KPIs.', 'Résultat : une cartographie des écarts, des cas d’usage priorisés et un plan de preuve de valeur avec indicateurs mesurés.'),
 # --- S16
 ('In the age of Agentic AI, autonomy without observability is <span class="red">risk</span>.', 'À l’ère de l’IA agentique, l’autonomie sans observabilité, c’est un <span class="red">risque</span>.'),
 ('The future isn’t just autonomous networking.', 'L’avenir n’est pas seulement le réseau autonome.'),
 ('It’s autonomous networking with <span class="grad">continuous assurance</span>.', 'C’est le réseau autonome avec une <span class="grad">assurance continue</span>.'),
 ('Observe · Baseline · Detect · Diagnose · Respond · Verify', 'Observer · Référencer · Détecter · Diagnostiquer · Répondre · Vérifier'),
 ('Demo scenario. Devices, agents, tickets, KPIs and figures are simulated for illustration. Narration: synthetic voice.', 'Scénario de démonstration. Équipements, agents, billets, indicateurs et chiffres sont simulés à titre illustratif. Narration : voix de synthèse.'),
 # --- dynamic JS text (topology, charts, timeline)
 ("dal: [", "dal: ["),
 ("van: [140, 150, 'DC Vancouver', 'dc'], tor: [640, 200, 'DC Toronto', 'dc'], mtl: [1030, 140, 'DC Montréal', 'dc'],", "van: [140, 150, 'CD Vancouver', 'dc'], tor: [640, 200, 'CD Toronto', 'dc'], mtl: [1030, 140, 'CD Montréal', 'dc'],"),
 ("cloud: [380, 60, 'Cloud · AWS · Azure', 'cloud'], isp: [860, 50, 'Internet · 2 ISPs', 'isp'],", "cloud: [380, 60, 'Nuage · AWS · Azure', 'cloud'], isp: [860, 50, 'Internet · 2 FAI', 'isp'],"),
 ("'PATH A · MPLS 10 Gb/s'", "'CHEMIN A · MPLS 10 Gb/s'"),
 ("'PATH B · 1 Gb/s'", "'CHEMIN B · 1 Gb/s'"),
 ("t2.textContent = 'UNITED STATES'; }", "t2.textContent = 'ÉTATS-UNIS'; }"),
 ("[['MPLS core', '#4589ff', ''], ['Path B', '#a56eff', '12 6'], ['SD-WAN overlay', '#33b1ff', '9 7'], ['BGP · cloud / ISP', '#8b97b3', '3 5']]", "[['Cœur MPLS', '#4589ff', ''], ['Chemin B', '#a56eff', '12 6'], ['Superposition SD-WAN', '#33b1ff', '9 7'], ['BGP · nuage / FAI', '#8b97b3', '3 5']]"),
 ("const chg = mk(21, '#f1c21b', '09:21 BGP change', Y1 + 14);", "const chg = mk(21, '#f1c21b', '09 h 21 changement BGP', Y1 + 14);"),
 ("const rb = recover ? mk(31, '#42be65', '09:31 rollback', Y1 + 36) : null;", "const rb = recover ? mk(31, '#42be65', '09 h 31 retour arrière', Y1 + 36) : null;"),
 ("const TL5 = [['09:21', 'BGP policy changed'], ['09:22', 'Traffic path shifts'], ['09:23', 'Utilization deviates'], ['09:24', 'Latency increases'], ['09:25', 'Packet loss spreads'], ['09:26', 'Business impact']];", "const TL5 = [['09 h 21', 'Politique BGP modifiée'], ['09 h 22', 'Le trafic change de chemin'], ['09 h 23', 'L’utilisation s’écarte'], ['09 h 24', 'La latence augmente'], ['09 h 25', 'La perte s’étend'], ['09 h 26', 'Impact d’affaires']];"),
 ("t.textContent = '09:' + fmt2(m);", "t.textContent = '09 h ' + fmt2(m);"),
]

TL_FR = {
 'title': "Quand l'IA modifie le réseau, qui vérifie le résultat ? (version Canada–États-Unis)",
 'names': {'s0': 'Ouverture', 's1': 'Infrastructures critiques', 's17': 'Architecture réseau', 's2': 'Opérations agentiques encadrées', 's18': 'Configuration BGP et SD-WAN par l’IA',
           's3': 'Le changement', 's4': 'SevOne voit autre chose', 's5': 'Avant l’incident', 's6': 'Six secteurs, six conséquences', 's7': 'Cause racine et rayon d’impact',
           's19': 'Ce qui a mal tourné', 's8': 'Automatisation des incidents', 's9': 'Vérifier le résultat', 's10': 'Contrôles de risque', 's11': 'Tableau de bord de la direction',
           's12': 'Coût total et dépenses d’exploitation', 's13': 'Trois vérités', 's14': 'La question', 's15': 'Prochaine étape', 's16': 'Conclusion'},
 'steps': ['01 CHANGEMENT', '02 DÉTECTER', '03 IMPACT', '04 DIAGNOSTIC', '05 RÉPONDRE', '06 VÉRIFIER', '07 CONTRÔLER', '08 VALEUR'],
 'chapters': ['Intro', 'Architecture', 'Config', 'Changement', 'Détection', 'Secteurs', 'Cause racine', 'Problèmes', 'Réponse', 'Vérification', 'Contrôles', 'Indicateurs', 'Coûts', 'Question', 'Évaluation'],
}

PAGE = [
 ("'MTL ↔ TOR · DEMO SCENARIO'", "'MTL ↔ TOR · SCÉNARIO DÉMO'"),
 ('<html lang="en">', '<html lang="fr">'),
 ("(dec ? v.toFixed(dec) : Math.round(v).toLocaleString('en-US')) + (el.dataset.suf || '')", "(dec ? v.toFixed(dec).replace('.', ',') : Math.round(v).toLocaleString('fr-CA')) + (el.dataset.suf || '').replace('%', '\u00a0%')"),
 ('<span class="mb">47%</span>', '<span class="mb">47 %</span>'), ('<span class="mb">82%</span>', '<span class="mb">82 %</span>'),
 ('>Play</button>', '>Lecture</button>'),
 ("$('#pp').textContent = 'Pause';", "$('#pp').textContent = 'Pause';"),
 ("$('#pp').textContent = 'Play';", "$('#pp').textContent = 'Lecture';"),
 ('title="Subtitles">CC</button>', 'title="Sous-titres">ST</button>'),
 ('<button id="ucb">Use cases</button>', '<button id="ucb">Chapitres</button>'),
 ('Play with narration ·', 'Lecture avec narration ·'),
 ('Agentic network assurance · subtitles on', 'Assurance réseau agentique · sous-titres activés'),
 ('SEVONE · AGENTIC ASSURANCE</div><h2>Chapters in the film</h2>', 'SEVONE · ASSURANCE AGENTIQUE</div><h2>Chapitres du film</h2>'),
 ('Every scenario is simulated. Values are demo values, not customer results.', 'Tout le scénario est simulé. Les valeurs sont des valeurs de démonstration, pas des résultats clients.'),
 ('>Close</button>', '>Fermer</button>'),
 ('<dt>Situation</dt>', '<dt>Situation</dt>'),
 ('<dt>How SevOne helps</dt>', '<dt>Ce que fait SevOne</dt>'),
 ('<dt>Outcome</dt>', '<dt>Résultat</dt>'),
 ('<button>Watch ·', '<button>Voir ·'),
 ('Each card is one chapter. Choose <b>Watch</b> to jump to it.', 'Chaque carte est un chapitre. Choisissez <b>Voir</b> pour y aller.'),
 ('aria-label="Use cases"', 'aria-label="Chapitres"'),
 ('aria-label="Seek"', 'aria-label="Position"'),
]


def apply(text, pairs, strict=True):
    for a, b in pairs:
        if a == b: continue
        n = text.count(a)
        if n == 0:
            if strict: raise SystemExit(f'not found: {a[:90]}')
            continue
        text = text.replace(a, b)
    return text


if '--page' in sys.argv:
    p = HERE / 'film.html'
    p.write_text(apply(p.read_text(), PAGE, strict=False))
    print('page translated')
else:
    p = HERE / 'build_film.py'
    p.write_text(apply(p.read_text(), [x for x in SRC if x[0] != 'dal: [']))
    tl = json.loads((HERE / 'timeline.json').read_text())
    tl['title'] = TL_FR['title']
    for s in tl['scenes']: s['name'] = TL_FR['names'][s['id']]
    tl['steps'] = [[n, s[1]] for n, s in zip(TL_FR['steps'], tl['steps'])]
    tl['chapters'] = [[n, c[1]] for n, c in zip(TL_FR['chapters'], tl['chapters'])]
    (HERE / 'timeline.json').write_text(json.dumps(tl, indent=1, ensure_ascii=False))
    print('source translated')
