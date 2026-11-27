#!/usr/bin/env node
/*
 * Records "Agentic Runtime Security, Step by Step": a narrated walkthrough of the bank's
 * reference architecture (demo/agentic_runtime_architecture.html, redrawn from the
 * reference slide). The camera follows one request through steps 1 to 6, then covers
 * the activity feed, the three kill switches and IBM Verify Identity Protection.
 *
 *   node demo/film/record_runtime_architecture.js [output.mp4]       captions only
 *   FILM_TTS=pocket FILM_TTS_LANGUAGE=english FILM_VOICE=alba FILM_TTS_MAX_PAUSE=0.5 \
 *     FILM_PYTHON=/path/to/venv/bin/python node demo/film/record_runtime_architecture.js
 *   FILM_LANG=fr FILM_TTS=pocket FILM_TTS_LANGUAGE=french_24l FILM_VOICE=estelle ... \
 *     node demo/film/record_runtime_architecture.js                 in French (the page opens at #fr)
 * See narrate.py for the voice setup and record_film.js for the requirements.
 */
'use strict';
const path = require('path');
const { record } = require('./lib');

const LANG = (process.env.FILM_LANG || 'en').trim().toLowerCase() === 'fr' ? 'fr' : 'en';
const NARRATED = Boolean(process.env.FILM_VOICE);
const OUT = path.resolve(process.argv[2] || path.join(__dirname,
  LANG === 'fr' ? 'agentic-runtime-security-step-by-step-fr.mp4' : 'agentic-runtime-security-step-by-step.mp4'));

// `text` is the caption, `say` what the narrator reads (acronyms spelled the way they
// are spoken). Lines without `text` are spoken over a title card.
const LINES_EN = {
  open1: { say: 'One request. Six steps. Three kill switches.' },
  open2: { say: 'Here is how an A.I. agent acts for a bank employee, without ever holding a secret.' },

  ov1: { text: "The bank's reference architecture for agentic runtime security, step by step.",
         say: "This is the bank's reference architecture for agentic runtime security. Let's walk through it, step by step." },
  ov2: { text: 'Left: the employees, the workforce identity provider they sign in with, and the agentic control plane where the agent runs.',
         say: 'On the left: the bank employees, the workforce identity provider they sign in with, and the control plane where the agent runs.' },
  ov3: { text: 'Right: IBM Verify for agent identity and delegation, and the bank environment with the tools server, Vault and the payments database.',
         say: 'On the right: I.B.M. Verify, which gives the agent its own identity and handles delegation. And the bank environment, with the tools server, HashiCorp Vault, and the payments database.' },
  ov4: { text: 'Across the top, IBM Verify Identity Protection watches every agent identity in the chain.',
         say: 'Across the top, I.B.M. Verify Identity Protection watches every agent identity in the chain.' },
  ov5: { text: 'Solid boxes were built and demoed in the lab. Dashed boxes are recommended additions. Grey dashed arrows show trust.',
         say: 'Solid boxes were built and demoed in the lab. Dashed boxes are recommended additions. And the dashed grey arrows show trust, through published public keys.' },

  s1a: { text: 'Step 1 · The employee signs in to the workforce identity provider, with multi-factor authentication.',
         say: 'Step one. An employee signs in to the bank\'s workforce identity provider, such as Okta, Microsoft Entra I.D., Ping, or I.B.M. Verify, with multi-factor authentication.' },
  s1b: { text: 'The job role becomes a groups claim. Relationship managers view, initiate and cancel. Tellers only view.',
         say: 'The job role becomes a groups claim, in a signed token. A relationship manager can view accounts, and initiate and cancel payments. A teller can only view accounts.' },
  s1c: { text: 'The provider publishes its public keys, so other services can verify its tokens.' },

  s2a: { text: 'Step 2 · The employee chats with the Payments Assistant. The model picks the tools, and never sees a token.',
         say: 'Step two. The employee chats with the Payments Assistant, a registered agent. The language model picks the tools, but it never sees a token.' },
  s2b: { text: "The identity connection keeps each employee's own token. No shared service account.",
         say: "The identity connection keeps each employee's own token. Everyone signs in as themselves. There is no shared service account." },

  s3a: { text: "Step 3 · The tool call reaches the banking tools MCP server with the employee's token. The server stores no secrets.",
         say: "Step three. When the model picks a tool, the call goes to the banking tools M.C.P. server, carrying the employee's token. The server keeps no secrets of its own." },
  s3b: { text: 'Recommended addition: an MCP gateway such as IBM ContextForge, with guardrails, role-based access, rate limits and audit.',
         say: 'A recommended addition: an M.C.P. gateway, such as I.B.M. Context Forge, gives every tool one governed endpoint, with guardrails, role-based access, rate limits and audit.' },

  s4a1: { text: 'Step 4a · Is the agent live? The agent registry knows the agent, its owner and its state: active or suspended.',
          say: 'Step four A. The tools server asks I.B.M. Verify whether the agent is live. The agent registry knows the agent, its owner, and its state: active, or suspended.' },
  s4a2: { text: 'An active agent gets its own token, as the actor. Suspend it, and the chain stops here: kill switch 1.',
          say: "An active agent gets its own token, as the actor. Suspend it, and the chain stops right here. That's kill switch one." },
  s4b1: { text: 'Step 4b · Token exchange: employee token + agent token → one token. Subject: the employee. Actor: the agent.',
          say: "Step four B. Token exchange, on behalf of the employee. The employee's token and the agent's token become one token. Its subject is the employee. Its actor is the agent." },
  s4b2: { text: "No impersonation. And Verify first checks the identity provider's signature with its published keys.",
          say: "There's no impersonation: the agent never becomes the employee. And before exchanging anything, Verify checks the identity provider's signature, with its published keys." },
  s4c1: { text: 'Step 4c · One token per action. Its authorization details name exactly which database login it may get: view or initiate.',
          say: 'Step four C. For each action, Verify issues one more token, with rich authorization details. It names exactly which database login this one action may get: view, or initiate.' },

  s5a: { text: 'Step 5 · The tools server asks HashiCorp Vault Enterprise for a database login, with the per-action token.',
         say: 'Step five. The tools server asks HashiCorp Vault Enterprise for a database login, and presents the per-action token.' },
  s5b: { text: "Vault checks Verify's signature offline. Its trust profile maps the user to the subject and the agent to the actor.",
         say: "Vault checks Verify's signature offline, with the published keys. Its trust profile maps the user to the token's subject, and the agent to its actor, and it requires the authorization details. Entities link the employees and the agent to their Verify identities." },
  s5c: { text: "Then Vault decides: employee's policy ∩ agent's ceiling ∩ token's request. All three must say yes.",
         say: "Then Vault decides. The employee's policy, intersected with the agent's ceiling, intersected with the token's request. All three must say yes." },
  s5d: { text: 'Manager initiates a payment: allowed. Manager cancels one: denied, the agent may never cancel. Teller initiates: denied.',
         say: 'A relationship manager asks the agent to initiate a payment: allowed. The same manager asks it to cancel one: denied, because this agent may never cancel. A teller asks it to initiate a payment: denied, because tellers can only view.' },
  s5e: { text: "Allowed: Vault's database engine creates a database user that lives two minutes, with only that role. The audit log records it.",
         say: "When the answer is yes, Vault's database engine creates a database user that lives for two minutes, with only that role. The audit log records the employee, the agent, and the Verify transaction." },
  s5f: { text: "Disable the agent's entity in Vault, and no login is issued: kill switch 2.",
         say: "And if Vault disables the agent's entity, no login is issued at all. That's kill switch two." },

  s6a: { text: 'Step 6 · The tools server reads or writes the payments database with the two-minute user. Then the user is gone.',
         say: 'Step six. The tools server reads or writes the payments database with that two-minute user. Two minutes later, the user is gone. Nothing to steal, nothing to reuse.' },

  feed: { text: 'Every action goes to the activity feed: employee, agent, token and decision, for the SIEM and SOAR.',
          say: 'Every action also goes to the activity feed: the employee, the agent, the token, and the decision. The S.I.E.M. and SOAR tools see the whole chain.' },

  kills: { text: 'Three kill switches: 0 in the agent platform, 1 in IBM Verify, 2 in Vault. Any one of them cuts the chain.',
           say: 'Three kill switches, in three places. Zero: stop the agent in its platform. One: suspend it in I.B.M. Verify. Two: disable its entity in Vault. Any one of them cuts the chain.' },

  obs1: { text: 'IBM Verify Identity Protection discovers every agent and its identities, registered or shadow.',
          say: 'Across all of it, I.B.M. Verify Identity Protection discovers every agent and its identities, registered or shadow, with owner, delegations and credentials.' },
  obs2: { text: 'It maps who each agent acts for and what it can reach: employee → agent → token → Vault login → data.',
          say: 'It maps who each agent acts for, and what it can reach: employee, agent, token, Vault login, data.' },
  obs3: { text: 'It detects unusual delegation, privilege drift, static secrets and MFA gaps, and responds through SIEM / SOAR playbooks.',
          say: 'It detects unusual delegation, privilege drift, static secrets or service accounts outside Vault, and M.F.A. gaps. And it responds, through S.I.E.M. and SOAR playbooks that trigger the kill switches.' },

  recap: { text: 'Verified at every hop. Short-lived credentials. Every action names the employee and the agent. Three kill switches.',
           say: 'So every token is verified at every hop. Every credential is short-lived. Every action names both the employee and the agent. And three kill switches stand ready.' },

  end1: { say: 'The agent never holds a secret.' },
  end2: { say: 'And every action names who it acts for.' },
};

// Canadian French. `say` writes product names the way the French voice says them
// correctly (IBM Vérifaï, Hachicorpe Volte) and avoids English acronyms it misreads.
const LINES_FR = {
  open1: { say: 'Une requête. Six étapes. Et trois façons de tout arrêter.' },
  open2: { say: 'Voici comment un agent d’intelligence artificielle agit pour un employé de la banque, sans jamais détenir de secret.' },

  ov1: { text: 'L’architecture de référence de la banque pour la sécurité des agents à l’exécution, étape par étape.',
         say: 'Voici l’architecture de référence de la banque pour la sécurité des agents à l’exécution. Parcourons-la, étape par étape.' },
  ov2: { text: 'À gauche : les employés, le fournisseur d’identité avec lequel ils se connectent, et le plan de contrôle où l’agent s’exécute.',
         say: 'À gauche : les employés de la banque, le fournisseur d’identité avec lequel ils se connectent, et le plan de contrôle où l’agent s’exécute.' },
  ov3: { text: 'À droite : IBM Verify pour l’identité et la délégation des agents, et l’environnement de la banque, avec le serveur d’outils, Vault et la base des paiements.',
         say: 'À droite : IBM Vérifaï, qui attribue une identité propre à l’agent et gère la délégation. Et l’environnement de la banque, avec le serveur d’outils, Hachicorpe, Volte, et la base de données des paiements.' },
  ov4: { text: 'En haut, IBM Verify Identity Protection surveille chaque identité d’agent de la chaîne.',
         say: 'En haut, IBM Vérifaï Aïdenntiti Protèkcheune surveille chaque identité d’agent de la chaîne.' },
  ov5: { text: 'Trait plein : construit et démontré en labo. Pointillé : ajouts recommandés. Flèches grises pointillées : la confiance.',
         say: 'Les boîtes en trait plein ont été construites et démontrées en laboratoire. Les boîtes pointillées sont des ajouts recommandés. Et les flèches grises pointillées montrent la confiance, fondée sur la vérification des signatures.' },

  s1a: { text: 'Étape 1 · L’employé se connecte au fournisseur d’identité de la banque, avec l’authentification multifacteur.',
         say: 'Première étape. Un employé se connecte au fournisseur d’identité de la banque, comme Okta, Microsoft Entra, Ping, ou IBM Vérifaï, avec l’authentification multifacteur.' },
  s1b: { text: 'Le rôle devient une revendication de groupe. Directeurs de comptes : consulter, initier, annuler. Caissiers : consulter seulement.',
         say: 'Son rôle devient une revendication de groupe, dans un jeton signé. Un directeur de comptes peut consulter les comptes, et initier ou annuler des paiements. Un caissier peut seulement consulter les comptes.' },
  s1c: { text: 'Le fournisseur publie ses clés publiques, pour que d’autres services puissent vérifier ses jetons.',
         say: 'Le fournisseur publie aussi de quoi vérifier ses signatures, pour que d’autres services puissent valider ses jetons.' },

  s2a: { text: 'Étape 2 · L’employé converse avec l’Assistant paiements. Le modèle choisit les outils, et ne voit jamais de jeton.',
         say: 'Deuxième étape. L’employé converse avec l’Assistant paiements, un agent enregistré. Le modèle de langage choisit les outils, mais il ne voit jamais de jeton.' },
  s2b: { text: 'La connexion d’identité garde le jeton propre à chaque employé. Aucun compte de service partagé.',
         say: 'La connexion d’identité garde le jeton propre à chaque employé. Chacun se connecte en son nom. Il n’y a aucun compte de service partagé.' },

  s3a: { text: 'Étape 3 · L’appel d’outil arrive au serveur MCP des outils bancaires, avec le jeton de l’employé. Le serveur ne stocke aucun secret.',
         say: 'Troisième étape. Quand le modèle choisit un outil, l’appel part vers le serveur èm cé pé des outils bancaires, avec le jeton de l’employé. Le serveur ne garde aucun secret.' },
  s3b: { text: 'Ajout recommandé : une passerelle MCP comme IBM ContextForge, avec garde-fous, contrôle d’accès, limites de débit et audit.',
         say: 'Ajout recommandé : une passerelle èm cé pé, comme IBM Context Forge, donne à chaque outil un point d’accès gouverné, avec des garde-fous, un contrôle d’accès par rôle, des limites de débit, et un audit.' },

  s4a1: { text: 'Étape 4a · L’agent est-il actif ? Le registre connaît l’agent, son propriétaire et son état : actif ou suspendu.',
          say: 'Étape quatre A. Le serveur d’outils demande à IBM Vérifaï si l’agent est actif. Le registre des agents connaît l’agent, son propriétaire, et son état : actif, ou suspendu.' },
  s4a2: { text: 'Un agent actif obtient son propre jeton, comme acteur. Suspendez-le, et la chaîne s’arrête ici : coupe-circuit 1.',
          say: 'Un agent actif obtient son propre jeton, en tant qu’acteur. Suspendez-le, et la chaîne s’arrête ici. C’est le coupe-circuit numéro un.' },
  s4b1: { text: 'Étape 4b · Échange de jetons : jeton de l’employé + jeton de l’agent → un seul jeton. Sujet : l’employé. Acteur : l’agent.',
          say: 'Étape quatre B. L’échange de jetons, au nom de l’employé. Le jeton de l’employé et celui de l’agent deviennent un seul jeton. Son sujet, c’est l’employé. Son acteur, c’est l’agent.' },
  s4b2: { text: 'Aucune usurpation. Et Verify vérifie d’abord la signature du fournisseur d’identité avec ses clés publiées.',
          say: 'L’agent ne se fait jamais passer pour l’employé. Et avant tout échange, IBM Vérifaï contrôle la signature du fournisseur d’identité.' },
  s4c1: { text: 'Étape 4c · Un jeton par action. Ses détails d’autorisation indiquent exactement quelle connexion il peut obtenir : consulter ou initier.',
          say: 'Étape quatre C. Pour chaque action, un nouveau jeton est émis par IBM Vérifaï, avec des détails d’autorisation enrichis. Il indique exactement quelle connexion à la base de données cette action peut obtenir : consulter, ou initier.' },

  s5a: { text: 'Étape 5 · Le serveur d’outils demande à HashiCorp Vault Enterprise une connexion à la base de données, avec le jeton par action.',
         say: 'Cinquième étape. Le serveur d’outils demande à Hachicorpe, Volte Enterprise, une connexion à la base de données, et présente le jeton par action.' },
  s5b: { text: 'Vault vérifie la signature de Verify hors ligne. Son profil de confiance associe l’utilisateur au sujet, et l’agent à l’acteur.',
         say: 'Volte contrôle la signature d’IBM Vérifaï sur place, avec les clés publiées, sans aucun appel réseau. Son profil de confiance associe l’utilisateur au sujet du jeton, et l’agent à son acteur, et il exige les détails d’autorisation. Les entités relient les employés et l’agent à leurs identités Vérifaï.' },
  s5c: { text: 'Puis Vault décide : politique de l’employé ∩ plafond de l’agent ∩ demande du jeton. Les trois doivent dire oui.',
         say: 'Puis Volte décide. La politique de l’employé, croisée avec le plafond de l’agent, croisée avec la demande du jeton. Les trois doivent dire oui.' },
  s5d: { text: 'Le directeur initie un paiement : autorisé. Il en annule un : refusé, l’agent ne peut jamais annuler. Un caissier initie : refusé.',
         say: 'Un directeur de comptes demande à l’agent d’initier un paiement : autorisé. Le même directeur lui demande d’en annuler un : refusé, car cet agent ne peut jamais annuler. Un caissier lui demande d’initier un paiement : refusé, car les caissiers peuvent seulement consulter.' },
  s5e: { text: 'Autorisé : le moteur de base de données de Vault crée un utilisateur qui vit deux minutes, avec ce seul rôle. Le journal d’audit le consigne.',
         say: 'Quand la réponse est oui, le moteur de base de données de Volte crée un utilisateur qui vit deux minutes, avec ce seul rôle. Le journal d’audit consigne l’employé, l’agent, et la transaction Vérifaï.' },
  s5f: { text: 'Désactivez l’entité de l’agent dans Vault, et aucune connexion n’est émise : coupe-circuit 2.',
         say: 'Et si l’agent est désactivé dans Volte, plus aucune connexion n’est émise. C’est le coupe-circuit numéro deux.' },

  s6a: { text: 'Étape 6 · Le serveur d’outils lit ou écrit dans la base des paiements avec l’utilisateur de deux minutes. Puis l’utilisateur disparaît.',
         say: 'Sixième étape. Le serveur d’outils lit ou écrit dans la base de données des paiements avec cet utilisateur de deux minutes. Deux minutes plus tard, l’utilisateur n’existe plus. Rien à voler, rien à réutiliser.' },

  feed: { text: 'Chaque action va au flux d’activité : employé, agent, jeton et décision, pour le SIEM et le SOAR.',
          say: 'Chaque action va aussi au flux d’activité : l’employé, l’agent, le jeton, et la décision. Les outils de surveillance et de réponse de la sécurité voient toute la chaîne.' },

  kills: { text: 'Trois coupe-circuits : 0 dans la plateforme des agents, 1 dans IBM Verify, 2 dans Vault. Un seul suffit pour couper la chaîne.',
           say: 'Il y a trois coupe-circuits, placés à trois endroits. Zéro : arrêter l’agent dans sa plateforme. Un : le suspendre dans IBM Vérifaï. Deux : désactiver son entité dans Volte. Un seul suffit pour couper la chaîne.' },

  obs1: { text: 'IBM Verify Identity Protection découvre chaque agent et ses identités, enregistrées ou fantômes.',
          say: 'Sur toute la chaîne, IBM Vérifaï Aïdenntiti Protèkcheune découvre chaque agent et ses identités, enregistrées ou fantômes, avec leur propriétaire, leurs délégations et leurs identifiants.' },
  obs2: { text: 'Il cartographie pour qui chaque agent agit et ce qu’il peut atteindre : employé → agent → jeton → connexion Vault → données.',
          say: 'Il cartographie pour qui chaque agent agit, et ce qu’il peut atteindre : employé, agent, jeton, connexion Volte, et enfin les données.' },
  obs3: { text: 'Il détecte les délégations inhabituelles, la dérive des privilèges, les secrets statiques et les lacunes de MFA, et répond par des playbooks SIEM / SOAR.',
          say: 'Il détecte les délégations inhabituelles, la dérive des privilèges, les secrets statiques ou les comptes de service hors de Volte, et les lacunes d’authentification multifacteur. Et il répond, par des scénarios automatisés qui déclenchent les coupe-circuits.' },

  recap: { text: 'Vérifié à chaque saut. Des identifiants de courte durée. Chaque action nomme l’employé et l’agent. Trois coupe-circuits.',
           say: 'Ainsi, chaque jeton est vérifié à chaque saut. Chaque identifiant est de courte durée. Chaque action nomme à la fois l’employé et l’agent. Et trois coupe-circuits sont prêts.' },

  end1: { say: 'L’agent ne détient jamais de secret.' },
  end2: { say: 'Et chaque action nomme pour qui il agit.' },
};

const CHAPTERS_EN = [
  ['map', 'The map'], ['s1', 'Step 1 · Sign in'], ['s2', 'Step 2 · Chat with the agent'], ['s3', 'Step 3 · Tool call'],
  ['s4a', 'Step 4a · Is the agent live?'], ['s4b', 'Step 4b · Token exchange'], ['s4c', 'Step 4c · One token per action'],
  ['s5', 'Step 5 · Vault decides'], ['s6', 'Step 6 · Read or write'], ['feed', 'Activity feed'], ['kills', 'Three kill switches'],
  ['observe', 'IBM Verify Identity Protection'], ['recap', 'In one line'],
];

const CHAPTERS_FR = [
  ['map', 'Vue d’ensemble'], ['s1', 'Étape 1 · Connexion'], ['s2', 'Étape 2 · Conversation avec l’agent'], ['s3', 'Étape 3 · Appel d’outil'],
  ['s4a', 'Étape 4a · L’agent est-il actif ?'], ['s4b', 'Étape 4b · Échange de jetons'], ['s4c', 'Étape 4c · Un jeton par action'],
  ['s5', 'Étape 5 · Vault décide'], ['s6', 'Étape 6 · Lire ou écrire'], ['feed', 'Flux d’activité'], ['kills', 'Trois coupe-circuits'],
  ['observe', 'IBM Verify Identity Protection'], ['recap', 'En une ligne'],
];

const OPENING_EN = `
  <div class="ey" data-k="ey">Agentic runtime security · reference architecture</div>
  <div class="l" data-k="l1">One request. Six steps. Three kill switches.</div>
  <div class="l alert" data-k="l2">How an AI agent acts for a bank employee, without ever holding a secret.</div>`;
const CLOSING_EN = `
  <div class="l" data-k="l1">The agent never holds a secret.</div>
  <div class="l alert" data-k="l2">And every action names who it acts for.</div>
  <div class="fine" data-k="fine">Walkthrough of the bank's agentic runtime security reference architecture. Solid components were
    built and demoed in the lab; dashed components are recommended additions. Token values are illustrative. Product names belong
    to their owners.</div>`;

const OPENING_FR = `
  <div class="ey" data-k="ey">Sécurité des agents à l’exécution · architecture de référence</div>
  <div class="l" data-k="l1">Une requête. Six étapes. Trois coupe-circuits.</div>
  <div class="l alert" data-k="l2">Comment un agent IA agit pour un employé de la banque, sans jamais détenir de secret.</div>`;
const CLOSING_FR = `
  <div class="l" data-k="l1">L’agent ne détient jamais de secret.</div>
  <div class="l alert" data-k="l2">Et chaque action nomme pour qui il agit.</div>
  <div class="fine" data-k="fine">Parcours de l’architecture de référence de la banque pour la sécurité des agents à l’exécution. Les composants
    en trait plein ont été construits et démontrés en laboratoire; les composants pointillés sont des ajouts recommandés. Les valeurs
    de jetons sont illustratives. Les noms de produits appartiennent à leurs propriétaires.</div>`;

// French captions and cards get non-breaking spaces before : ; ? ! and inside numbers.
const frenchSpaces = (t) => t.replace(/ ([:;?!])/g, '\u00a0$1').replace(/(\d) (\d{3})/g, '$1\u00a0$2');
const LINES = LANG === 'fr'
  ? Object.fromEntries(Object.entries(LINES_FR).map(([id, l]) => [id, l.text ? { ...l, text: frenchSpaces(l.text) } : l]))
  : LINES_EN;
const CHAPTERS = LANG === 'fr' ? CHAPTERS_FR.map(([k, t]) => [k, frenchSpaces(t)]) : CHAPTERS_EN;
const OPENING = LANG === 'fr' ? frenchSpaces(OPENING_FR) : OPENING_EN;
const CLOSING = LANG === 'fr' ? frenchSpaces(CLOSING_FR) : CLOSING_EN;

record({
  out: OUT,
  lines: LINES,
  pages: [{ id: 'arch', file: 'agentic_runtime_architecture.html', hash: LANG === 'fr' ? 'fr' : '' }],
  async setup({ frame, stage }) {
    await frame('arch', 'arch')('film');
    await frame('arch', 'arch')('go', 'map', true);
    await stage('card', OPENING);
  },
  async play({ after, stage, frame, caption, speak, chapter }) {
    const arch = frame('arch', 'arch');
    const titles = Object.fromEntries(CHAPTERS);
    let last = null;
    const readTime = (id) => Math.max(3.4, (LINES[id].text || LINES[id].say).length / 15);
    const beat = (pause = 0.5) => after(NARRATED || !last ? pause : readTime(last) + pause);
    const say = async (id, pause = 0.5) => {
      await beat(pause);
      if (LINES[id].text) await caption(id); else { await caption(null); speak(id); }
      last = id;
    };
    // Moves the walkthrough to a step (camera, highlights, side panel), then speaks.
    const step = async (name, ids, { pause = 0.6, settle = 1.0 } = {}) => {
      await beat(pause);
      await caption(null); // the last step's caption leaves with its scene
      if (titles[name]) chapter(titles[name]);
      await arch('go', name);
      await after(settle);
      for (const id of ids) await say(id, 0.45);
    };

    // Cold open
    chapter('Introduction');
    await after(1.0); await stage('reveal', 'ey', 'l1'); speak('open1'); last = 'open1';
    await beat(0.6); await stage('reveal', 'l2'); speak('open2'); last = 'open2';
    await beat(1.2); await stage('cardOut');

    // The map
    await step('map', ['ov1'], { pause: 1.0 });
    await step('left', ['ov2']);
    await step('right', ['ov3']);
    await step('band', ['ov4']);
    await step('legend', ['ov5']);

    // One request, step by step
    await step('s1', ['s1a', 's1b', 's1c'], { settle: 1.4 });
    await step('s2', ['s2a', 's2b'], { settle: 1.4 });
    await step('s3', ['s3a', 's3b'], { settle: 1.4 });
    await step('s4a', ['s4a1', 's4a2'], { settle: 1.4 });
    await step('s4b', ['s4b1', 's4b2'], { settle: 1.4 });
    await step('s4c', ['s4c1'], { settle: 1.4 });
    await step('s5', ['s5a', 's5b'], { settle: 1.4 });
    await step('s5x', ['s5c', 's5d'], { settle: 1.4 });
    await step('s5y', ['s5e', 's5f'], { settle: 1.4 });
    await step('s6', ['s6a'], { settle: 1.4 });

    // Around the request
    await step('feed', ['feed'], { settle: 1.4 });
    await step('kills', ['kills'], { settle: 1.4 });
    await step('observe', ['obs1', 'obs2', 'obs3'], { settle: 1.4 });
    await step('recap', ['recap'], { settle: 1.4 });

    // Close
    await beat(1.6); await caption(null);
    await stage('card', CLOSING); await stage('cardIn');
    await after(1.2); await stage('reveal', 'l1'); speak('end1'); last = 'end1';
    await beat(0.6); await stage('reveal', 'l2'); speak('end2'); last = 'end2';
    await beat(1.2); await stage('reveal', 'fine');
    await after(7.0);
  },
}).catch((err) => { console.error(err); process.exit(1); });
