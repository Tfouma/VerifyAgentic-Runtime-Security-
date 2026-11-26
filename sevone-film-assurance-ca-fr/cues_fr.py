# French narration (Québec-friendly). (start in seconds, text). Same timeline as the English CA edition.
CUES = [
    (0.8, "Lundi, neuf heures vingt."),
    (3.4, "L'IA accélère les opérations. Elle accélère aussi le changement."),
    (8.0, "Et le changement va désormais à la vitesse machine."),
    (13.0, "Banques, télécoms, chemins de fer, transport aérien, énergie, gouvernements et IA : tout repose sur le réseau."),
    (20.4, "Sur site et en infonuagique, sur le WAN, le SD-WAN et les centres de données."),
    (26.0, "Des agents d'IA aident maintenant les ingénieurs à diagnostiquer, à générer des configurations et à appliquer des changements."),
    (33.8, "Une immense occasion, et un nouveau risque opérationnel."),
    # Architecture
    (41.0, "Voici le réseau. Trois centres de données, à Montréal, Toronto et Vancouver, maillés en haute disponibilité sur un cœur MPLS."),
    (48.6, "Chaque paire est reliée à cent gigabits, avec un lien de relève à vingt-cinq gigabits. Le chemin A porte les paiements."),
    (56.8, "New York, Chicago, Atlanta et San Francisco se connectent en SD-WAN, avec BGP vers le nuage."),
    (64.2, "SevOne voit tout."),
    # Agentic operations
    (69.0, "Prenons une optimisation de routine."),
    (71.2, "Un ingénieur demande à un agent d'IA d'améliorer la connectivité entre Montréal et Toronto, sans nuire aux applications."),
    (79.6, "L'agent analyse la télémétrie et propose de modifier la préférence BGP sur quarante-huit routeurs."),
    (86.4, "Selon la politique de changement, la modification est approuvée, puis exécutée par la plateforme d'automatisation."),
    (93.2, "L'humain et la politique, puis l'agent, puis l'automatisation approuvée. Exactement comme il se doit."),
    # AI-built configuration
    (101.0, "L'agent rédige lui-même la configuration."),
    (103.8, "Une route-map BGP qui augmente la préférence locale sur le chemin B."),
    (108.2, "Et une politique SD-WAN, avec une classe de SLA pour les paiements."),
    (113.0, "La syntaxe est valide. Les sessions BGP restent actives. Le changement est approuvé."),
    (119.0, "Il est poussé sur quarante-huit routeurs et dans le gestionnaire SD-WAN."),
    (124.4, "Toutes les vérifications que l'agent sait faire réussissent."),
    # The change
    (135.0, "Quarante-huit équipements sont mis à jour."),
    (138.0, "Aucune erreur de configuration. Aucun équipement en panne. Les sessions BGP restent établies."),
    (144.2, "La plateforme d'automatisation annonce un succès."),
    (157.8, "Mais le résultat d'affaires est-il au rendez-vous ?"),
    # Detect
    (163.4, "La télémétrie réseau indépendante raconte une autre histoire."),
    (167.0, "Le trafic a basculé vers un chemin plus contraint."),
    (172.6, "L'utilisation du WAN passe de quarante-sept à quatre-vingt-deux pour cent. La latence, de dix-huit à soixante-trois millisecondes. La perte de paquets atteint deux pour cent."),
    (182.6, "Pourtant, BGP reste établi, et tous les équipements sont en service."),
    (187.4, "SevOne compare le comportement réel à la ligne de base de chaque chemin, et signale l'écart en quelques minutes."),
    (195.4, "Voilà la distinction essentielle : un succès technique ne garantit pas le succès d'affaires."),
    # Before it becomes an incident
    (208.0, "C'est là que l'observabilité change l'équation du risque."),
    (212.0, "Lignes de base, flux et télémétrie en continu révèlent la dégradation pendant que les services fonctionnent."),
    (219.6, "SevOne lève l'alerte à neuf heures vingt-quatre, avant que la perte ne s'étende et avant le premier appel client."),
    (227.6, "N'attendez pas la panne. Détectez la dégradation pendant que tout fonctionne encore."),
    # Seven industries
    (238.0, "Pour une banque, ce même écart devient de la latence transactionnelle et un enjeu de résilience opérationnelle."),
    (247.4, "Pour un opérateur télécom, ce sont des pénalités de SLA et des escalades évitables."),
    (256.8, "Pour le ferroviaire, la visibilité des communications empêche une dégradation de devenir une perturbation."),
    (266.2, "Pour le transport aérien, aérogares, portes et bagages dépendent du réseau : une dégradation devient des retards en cascade."),
    (275.6, "Pour l'énergie, cette visibilité reste distincte des systèmes de sécurité et de contrôle."),
    (285.0, "Pour les gouvernements et les services essentiels, c'est une preuve de disponibilité et de reddition de comptes."),
    (294.4, "Et pour les plateformes d'IA, des chemins congestionnés laissent des GPU coûteux en attente. L'infrastructure d'IA est aussi une infrastructure réseau."),
    # Root cause
    (308.0, "Question suivante : que s'est-il passé, et où ?"),
    (311.8, "SevOne remonte du symptôme à la portée, au chemin, aux flux, puis au changement qui en est la cause."),
    (319.8, "Latence sur le chemin des paiements. Trois circuits WAN en bordure de Toronto. Le meilleur chemin BGP a basculé vers le lien de relève à vingt-cinq gigabits."),
    (329.0, "La réplication et les paiements le partagent. Le déclencheur : le changement de neuf heures vingt et une."),
    (336.4, "Quoi, où, quelle anomalie, quel impact, quelle urgence : des réponses fondées sur des preuves, pas sur des opinions."),
    # What went wrong
    (353.0, "Alors, qu'est-ce qui a mal tourné ? Trois problèmes, chacun valide en soi."),
    (358.4, "Un : la route-map s'applique à tous les préfixes, pas seulement au trafic de masse. Paiements et réplication passent sur le lien de relève de vingt-cinq gigabits."),
    (367.6, "Deux : la classe de SLA tolère cent cinquante millisecondes et cinq pour cent de perte. Le chemin dégradé semble conforme, donc rien n'est redirigé."),
    (378.6, "Trois : chaque changement a été validé pour la syntaxe. Aucun pour le résultat."),
    (384.6, "SevOne a révélé les trois : les flux sur le chemin B, la latence et la perte des tunnels SD-WAN, et l'écart à la ligne de base."),
    # Respond
    (397.0, "Détecter ne suffit pas à réduire le risque. L'information doit entrer dans vos processus."),
    (403.6, "SevOne lève l'événement. Un incident ServiceNow s'ouvre automatiquement, avec l'élément de configuration, la priorité et les preuves."),
    (412.4, "NetOps est alerté. DevSecOps est informé du changement initié par l'IA."),
    (417.8, "Les niveaux un et deux sont automatisés : triage, corrélation et proposition de retour arrière."),
    (423.8, "Le niveau trois est humain. Un ingénieur approuve le retour arrière."),
    (428.2, "La plateforme d'automatisation l'exécute. SevOne reste l'observateur indépendant."),
    # Verify
    (442.0, "Et une remédiation n'est pas terminée parce qu'une tâche réussit. Le réseau est mesuré de nouveau."),
    (449.4, "L'utilisation revient à quarante-neuf pour cent. La latence à dix-neuf millisecondes. La perte disparaît."),
    (456.8, "Alors seulement, le billet se ferme. Observer, détecter, comprendre, agir et vérifier."),
    # Risk controls
    (472.0, "Voilà comment la preuve réseau soutient les contrôles de risque."),
    (475.8, "Les contrôles préventifs encadrent ce qui peut changer. Les contrôles de détection révèlent les anomalies."),
    (482.0, "Le diagnostic les explique. Les flux correctifs répondent. La vérification confirme le rétablissement."),
    (488.6, "Et l'historique devient une preuve pour l'audit, les régulateurs et la diligence raisonnable."),
    (494.4, "SevOne est une source importante de cette preuve, aux côtés des dossiers de changement, d'ITSM et de sécurité."),
    (501.6, "Il ne remplace pas ces contrôles. Il les rend mesurables."),
    # Executive dashboard
    (512.0, "La direction obtient une vue unique du risque opérationnel réseau."),
    (515.6, "Les indicateurs sont définis par classe de service : disponibilité, performance, capacité, stabilité, changement et couverture."),
    (523.2, "Et un nouvel indicateur pour l'ère agentique : le taux d'assurance des résultats de changement."),
    (528.6, "La part des changements dont le résultat réseau a vraiment été vérifié."),
    # TCO / OPEX
    (542.0, "Le dossier d'affaires va au-delà des pannes évitées."),
    (545.6, "Outils consolidés, lignes de base automatisées, billets automatiques et synchronisation CMDB réduisent l'effort de chaque incident."),
    (553.8, "Mais n'estimez pas les économies à partir d'hypothèses marketing."),
    (557.6, "Mesurez les coûts actuels : outils, administration, incidents, rapports et intégration."),
    (564.6, "Faites une preuve de valeur, mesurez l'écart, et bâtissez le dossier sur des faits."),
    (571.6, "C'est ainsi qu'on prouve un coût total et des dépenses d'exploitation plus bas."),
    # Three truths
    (587.0, "L'agent d'IA vous dit que la tâche est terminée."),
    (590.8, "La plateforme d'automatisation vous dit que le changement est appliqué."),
    (594.8, "SevOne vous dit ce qui est arrivé au réseau."),
    (598.6, "L'entreprise a besoin des trois. Seule l'observabilité indépendante vérifie le résultat."),
    # The question
    (609.4, "Si un agent d'IA modifiait cinq cents équipements réseau cette nuit, combien de temps vous faudrait-il pour savoir si chaque changement a produit le résultat attendu ?"),
    # Assessment
    (629.4, "Commencez par une évaluation de la préparation et de l'observabilité de votre réseau agentique."),
    (634.6, "Visibilité, cas d'usage de l'IA, dépendances critiques, couverture de télémétrie, et visibilité BGP et WAN."),
    (643.4, "Lignes de base, validation des changements, processus d'incident, angles morts, et assurance en boucle fermée."),
    # Closing
    (657.0, "À l'ère de l'IA agentique, l'autonomie sans observabilité, c'est un risque."),
    (661.8, "L'avenir n'est pas seulement le réseau autonome."),
    (664.8, "C'est le réseau autonome, avec une assurance continue."),
    (669.8, "IBM SevOne."),
]

# Technical terms always pronounced in English (phonemized with en-us inside the French line).
EN_TERMS = ["IBM SevOne", "IBM", "SevOne", "SD-WAN", "WAN", "MPLS", "BGP", "SLA", "GPU", "CMDB", "ITSM",
            "NetOps", "DevSecOps", "ServiceNow", "route-map"]

# How an English term is fed to the en-us phonemizer when its spelling misleads it.
EN_SAY = {"ITSM": "I T S M"}

# Chatterbox only (it takes text, not phonemes). Subtitles keep the written form.
SPOKEN = {
    "SevOne": "Sev One", "SD-WAN": "S D WAN", "IA": "I A", "route-map": "route map",
}
