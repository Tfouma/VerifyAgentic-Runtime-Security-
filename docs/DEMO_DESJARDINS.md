# Démo pour Desjardins : agent IA gouverné en bac à sable

**Guide du présentateur.** Une vidéo de 6 minutes et une démo fonctionnelle en direct qui
montrent comment IBM Verify, HashiCorp Vault, une passerelle MCP et OPA encadrent un agent
d'IA qui agit au nom d'une conseillère, dans un dossier « connaître son client » (CSC).

| Livrable | Emplacement | Usage |
|----------|-------------|-------|
| **Vidéo narrée (FR, 1080p, ~6 min)** | [`video/demo-agent-gouverne.mp4`](../video/demo-agent-gouverne.mp4) | À projeter en ouverture, ou à envoyer après la rencontre |
| **Sous-titres** | [`video/demo-agent-gouverne.srt`](../video/demo-agent-gouverne.srt) | Pour une diffusion sans son ou une traduction |
| **Démo fonctionnelle** | [`livedemo/`](../livedemo) | À faire rouler en direct, pas à pas, devant le client |
| **Vue d'architecture (EN)** | [`demo/sandbox_flow.html`](../demo/sandbox_flow.html) | Onglets Délégation et Cycle de vie des politiques, pour les questions techniques |
| **Cas d'usage détaillé (EN)** | [`USE_CASE_SANDBOXED_AGENT_BANKING.md`](USE_CASE_SANDBOXED_AGENT_BANKING.md) | Référence pour l'équipe d'architecture |

> **À lire avant la rencontre**
> - L'institution, la conseillère (« Camille Roy »), les membres et les données sont
>   **fictifs**. La démo n'utilise **ni le nom ni la marque de Desjardins**, volontairement :
>   on présente un scénario représentatif, pas une maquette de leurs systèmes.
> - C'est un **modèle pédagogique**, pas un logiciel IBM. Il reproduit le fonctionnement des
>   contrôles. Confirmez les noms de produits, l'offre et les capacités actuelles (Agent
>   Identity, registre des agents, Antenna SSF) avec votre contact IBM avant la rencontre.
> - La voix de la vidéo est une **voix de synthèse** (français de France). Pour une voix
>   québécoise ou la vôtre, voir « Régénérer la vidéo » plus bas.
> - Ne citez pas de statistiques de fuites sans source à jour (p. ex. le rapport *Cost of a
>   Data Breach* d'IBM de l'année en cours).

---

## 1. Le message en une phrase

*« L'agent n'a aucun secret. Chaque action qu'il fait est déléguée par une personne,
limitée à un seul outil pendant cinq minutes, vérifiée par IBM Verify, et consignée pour
l'audit. S'il déraille, il est suspendu en quelques secondes. »*

---

## 2. Lancer la démo fonctionnelle

Il faut Python 3.9 ou plus récent, sans aucune dépendance.

```bash
python3 -m livedemo --ouvrir             # http://127.0.0.1:8765
python3 -m livedemo --pas-a-pas --ouvrir # recommandé devant un client
```

**Dans la console :**
1. Cliquez sur **Se connecter avec Entra ID**.
2. Cochez **Pas à pas**. L'agent s'arrête avant chaque étape. Cliquez sur **Étape suivante**
   ou appuyez sur la **barre d'espace** quand vous êtes prêt à continuer.
3. Choisissez un scénario.
4. Quand l'approbation apparaît, le code arrive dans le **courriel simulé** sous le champ
   de saisie. Tapez-le puis cliquez sur **Approuver**, ou tapez un faux code pour le
   scénario 3.
5. Cliquez sur **Réinitialiser** entre les scénarios. Après le scénario 2, l'agent reste
   suspendu 5 minutes, à moins de cliquer sur **Rétablir l'agent (administrateur)**.

Cliquez sur n'importe quel événement du journal pour afficher son jeton décodé et le
chemin correspondant dans le schéma.

### Ce qui est réel et ce qui est simulé

| Réel dans la démo | Simulé |
|-------------------|--------|
| Jetons JWT signés et vérifiés (un émetteur, une clé) | Microsoft Entra ID, IBM Verify, Vault, OPA : des stand-ins locaux |
| Échange de jetons RFC 8693 avec `subject`, `actor`, `act` imbriqué et `authorization_details` (RFC 9396) | Jira, GitLab, Databricks : des serveurs MCP locaux |
| Identifiants de 5 minutes, liés au `jti`, révoqués après usage | Le comportement de l'agent (scripté, pour être reproductible) |
| Base de données SQLite ; un identifiant en lecture ouvre une connexion **réellement** en lecture seule | Le courriel contenant le code d'approbation |
| Politique OPA lue depuis [`livedemo/policies/politique.json`](../livedemo/policies/politique.json) | |
| Suspension de l'agent, double révocation des sessions, rétablissement après 5 minutes | |

Les tests ([`tests/test_livedemo.py`](../tests/test_livedemo.py)) déroulent les quatre
scénarios de bout en bout par HTTP : `python3 -m unittest discover tests`.

---

## 3. Déroulé proposé (60 minutes)

| Bloc | Durée | Contenu |
|------|-------|---------|
| Contexte | 5 min | Les agents d'IA deviennent des identités. Ils se connectent, détiennent des jetons et agissent au nom de personnes. |
| **Vidéo** | 6 min | Projeter sans commenter. |
| **Démo en direct, pas à pas** | 15 min | Scénarios 1 et 2, en demandant à chaque étape : *« Le verriez-vous aujourd'hui ? »* |
| Questions techniques | 10 min | Onglet Délégation de `sandbox_flow.html`, jetons décodés dans le journal |
| Découverte | 15 min | Questions de la section 6 |
| Prochaines étapes | 5 min | Section 8 |

---

## 4. Les quatre scénarios : quoi dire

### Scénario 1 · Parcours normal (le cœur de la démo)
1. **Connexion** : *« La conseillère se connecte comme d'habitude. Le bac à sable ne reçoit que
   ce jeton. Aucune clé d'API, aucun mot de passe. »*
2. **Lecture du billet** : ouvrez le jeton dans le journal. *« `sub` : la conseillère. `act` :
   l'agent. Une seule action, cinq minutes. »*
3. **Délégation** : *« Le sous-agent a sa propre identité (SPIFFE) et un jeton réduit à la
   lecture. »*
4. **Refus du sous-agent** : *« Il tente d'écrire. IBM Verify refuse à l'échange de jetons, donc
   aucun identifiant n'existe. C'est ce qui empêche un `DROP TABLE` ou un `terraform
   destroy`. »*
5. **Approbation** : *« Double contrôle : l'agent prépare, une personne décide. »*
6. **Résultat** : montrez la ligne en vert dans la table (`approuve_par`) et les identifiants
   Vault tous **révoqués**.

### Scénario 2 · Guide empoisonné
*« Quelqu'un a caché une instruction dans le guide. »* Trois sorties sont refusées par OPA
(les pastilles rouges 1-2-3), puis un signal de risque suspend l'agent **partout à la fois**.
*« Même piégé, il n'avait aucun secret à voler. L'accès de la conseillère reste intact. »*

### Scénario 3 · Approbations échouées
Tapez trois faux codes. *« Trois échecs sur une modification de données, c'est un indice de
prise de contrôle de compte. On coupe la session dans IBM Verify et dans Entra ID. »* Le badge
de session passe au rouge et il faut se reconnecter.

### Scénario 4 · Outil non enregistré
*« Un agent CSC tente un virement. L'outil n'est même pas listé. Ajouter une capacité passe
par une demande de fusion révisée par deux personnes. »*

---

## 5. Correspondance avec les produits

| Dans la démo | Produit visé | À confirmer |
|--------------|--------------|-------------|
| Connexion de la conseillère | Microsoft Entra ID (fédéré avec IBM Verify) | Configuration de la confiance STS |
| Échange de jetons, RAR, approbation, registre des agents | IBM Verify, Agent Identity | Disponibilité (aperçu privé dans watsonx Orchestrate au moment de la rédaction), prise en charge du RAR et du `act` imbriqué |
| Identifiants de 5 minutes | HashiCorp Vault (IBM) | Moteurs de secrets pour Jira, GitLab et Databricks |
| Passerelle MCP | Passerelle MCP d'agents, ou Red Hat MCP Gateway + Authorino sur OpenShift | Environnements d'exécution pris en charge |
| Enregistrement des outils, sorties | OPA | Intégration à la passerelle retenue |
| Suspension, double révocation | Signaux partagés (SSF / CAEP), IBM Verify Antenna | Statut du produit |
| Bac à sable | NVIDIA OpenShell ou équivalent | Environnement d'exécution cible chez le client |

---

## 6. Questions de découverte

- Combien d'agents d'IA ou de copilotes sont déjà utilisés par vos employés ? Qui en est
  responsable ?
- Comment s'authentifient-ils ? Comptes de service partagés, clés d'API, ou jetons personnels ?
- Si un agent modifie une donnée membre, pouvez-vous retracer la personne qui l'a autorisé ?
- Vos agents peuvent-ils lancer d'autres agents ? Avec quels droits ?
- Où s'arrête votre gestion des accès actuelle : à la connexion, ou à chaque action ?
- Qui approuve aujourd'hui l'ajout d'un outil ou d'un connecteur à un agent ?

## 7. Contexte réglementaire à valider avec la conformité

Points d'ancrage possibles, **à confirmer avec les équipes de conformité et juridiques du
client** :
- **Loi 25** (protection des renseignements personnels au Québec) : minimisation des accès
  et traçabilité des traitements.
- **Obligations « connaître son client »** sous la LRPCFAT (CANAFE) : chaque changement de
  cote documente le billet, les preuves, l'agent et l'approbateur.
- **Attentes de l'AMF** en gestion des risques liés aux TIC et à l'utilisation de l'IA :
  inventaire des agents, surveillance humaine, journalisation.
- **Double contrôle et séparation des tâches** : l'agent prépare, une personne approuve, un
  sous-agent ne peut jamais écrire.

## 8. Objections fréquentes

| Objection | Réponse |
|-----------|---------|
| « Nos agents ne font que lire. » | Le scénario 2 commence par une lecture légitime. L'attaque arrive par le contenu lu. |
| « On a déjà l'authentification multifacteur. » | Elle protège la connexion d'une personne. Ici, tout se passe *après* la connexion, à chaque appel de l'agent. |
| « Ça va ralentir les équipes. » | Les lectures passent sans friction. Seules les écritures sensibles demandent une approbation. |
| « On le construira nous-mêmes. » | Il faut l'échange de jetons, le RAR, le registre des agents, les identifiants temporaires, les signaux partagés et l'audit, pour chaque plateforme d'agents. |

## 9. Prochaines étapes à proposer

1. **Inventaire** des agents et des identités non humaines (IBM Verify Identity Protection).
2. **Preuve de valeur** de 4 à 6 semaines sur un flux réel, dans un environnement isolé, avec
   un vrai locataire IBM Verify, Vault et la passerelle.
3. **Déploiement progressif** des contrôles.

Pour la preuve de valeur, on remplace les stand-ins de [`livedemo/core.py`](../livedemo/core.py)
par les vrais points de terminaison (IBM Verify, Vault, passerelle), et l'agent scripté par
un vrai agent (p. ex. Claude Code dans OpenShell). La console et les scénarios restent les
mêmes.

---

## 10. Régénérer la vidéo

La vidéo est produite en pilotant la vraie console (mode pas à pas) avec Playwright, puis en
ajoutant la narration.

```bash
# 1. Voix (hors ligne, Piper TTS). Le texte est dans video/narration.json.
PIPER_BIN=/chemin/piper PIPER_MODEL=/chemin/fr-voix.onnx python3 video/generer_voix.py
# 2. Enregistrement de l'écran (1920x1080)
node video/enregistrer.js
# 3. Mixage de la voix + export MP4 et SRT
FFMPEG=/chemin/ffmpeg python3 video/assembler.py
```

Pour utiliser votre propre voix, enregistrez un fichier WAV par phrase de
`video/narration.json` (nommé `<segment>-<n>.wav`, p. ex. `intro-0.wav`) dans
`video/build/voix/`, puis lancez `VOIX_PERSO=1 python3 video/generer_voix.py` pour mesurer
les durées, et reprenez les étapes 2 et 3. La vidéo se cale automatiquement sur votre voix.
