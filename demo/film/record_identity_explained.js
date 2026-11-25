#!/usr/bin/env node
/*
 * Records "Identity Attacks, Explained", the long-form teaching film: how people and
 * AI agents authenticate, the protocols and standards behind it, best practices,
 * fraud and non-compliance, lateral movement, ISPM and ITDR. It films the explainer
 * (demo/identity_explained.html) and two runs of Fraud Ring Live (demo/fraud_ring.html),
 * on the shared stage in lib.js.
 *
 * FILM_LANG=fr records the Canadian French version: both pages open at #fr, and the
 * captions, title cards and narration are in French.
 *
 * Narration: set FILM_VOICE. The film was made with Kyutai's Pocket TTS, which sounds
 * far more natural than the older Kokoro voices:
 *   FILM_TTS=pocket FILM_TTS_LANGUAGE=english FILM_VOICE=alba FILM_TTS_MAX_PAUSE=0.5 \
 *     FILM_PYTHON=/path/to/venv/bin/python node demo/film/record_identity_explained.js
 *   FILM_LANG=fr FILM_TTS=pocket FILM_TTS_LANGUAGE=french_24l FILM_VOICE=estelle ... (French)
 * See narrate.py for the setup. Without FILM_VOICE the film runs with captions only,
 * paced for reading.
 */
'use strict';
const path = require('path');
const { record } = require('./lib');

const LANG = (process.env.FILM_LANG || 'en').trim().toLowerCase() === 'fr' ? 'fr' : 'en';
const NARRATED = Boolean(process.env.FILM_VOICE);
const OUT = path.resolve(process.argv[2] || path.join(__dirname, LANG === 'fr' ? 'identity-attacks-explained-fr.mp4' : 'identity-attacks-explained.mp4'));

// Caption tags: the fraud pattern or control a live scene shows.
const TAG = {
  en: {
    hijack: { icon: 'alert', text: 'Fraud pattern · agent hijacking' },
    supply: { icon: 'alert', text: 'Fraud pattern · poisoned plugin' },
    sim: { icon: 'alert', text: 'Fraud pattern · SIM swap' },
    ato: { icon: 'alert', text: 'Fraud pattern · account takeover' },
    mule: { icon: 'alert', text: 'Fraud pattern · mule accounts' },
    policy: { icon: 'clipboard', text: 'Control · policy' },
    delegation: { icon: 'userCheck', text: 'Control · delegation' },
    signal: { icon: 'signal', text: 'Control · shared signal' },
    behavior: { icon: 'activity', text: 'Detection · behavior' },
    stepup: { icon: 'key', text: 'Response · approval on the customer’s own device' },
    kill: { icon: 'power', text: 'Response · kill switch' },
  },
  fr: {
    hijack: { icon: 'alert', text: 'Schéma de fraude · détournement d’agent' },
    supply: { icon: 'alert', text: 'Schéma de fraude · module piégé' },
    sim: { icon: 'alert', text: 'Schéma de fraude · échange de SIM' },
    ato: { icon: 'alert', text: 'Schéma de fraude · prise de contrôle de compte' },
    mule: { icon: 'alert', text: 'Schéma de fraude · comptes de mules' },
    policy: { icon: 'clipboard', text: 'Contrôle · politique' },
    delegation: { icon: 'userCheck', text: 'Contrôle · délégation' },
    signal: { icon: 'signal', text: 'Contrôle · signal partagé' },
    behavior: { icon: 'activity', text: 'Détection · comportement' },
    stepup: { icon: 'key', text: 'Réponse · approbation sur l’appareil du client' },
    kill: { icon: 'power', text: 'Réponse · coupe-circuit' },
  },
}[LANG];

// Every line of the film. `text` is the caption, `say` is what the narrator reads when
// it differs (fuller sentences, numbers spelled out, acronyms spelled the way they are
// spoken). Lines without `text` are spoken over title cards or a scene's own title.
const LINES_EN = {
  open1: { say: "Attackers don't break in, anymore." },
  open2: { say: 'They log in.' },
  open3: { say: 'This film explains how sign-in really works, how attackers abuse it, and the controls that stop them.' },

  ids0: { say: "Every request that reaches a bank's systems carries an identity. There are three kinds." },
  ids1: { say: 'People: employees, customers and partners.' },
  ids2: { say: 'Machines: servers, scripts and service accounts, with their certificates, keys and secrets.' },
  ids3: { say: 'And A.I. agents, which act for a person and call tools, data and other agents. In most large organizations, machine and agent identities already outnumber people, and many have no owner.' },

  human0: { say: 'First, how a person signs in, step by step.' },
  h1: { text: '1 · The app sends the person to the identity provider: OpenID Connect, with a PKCE secret.',
        say: "Step one. The app doesn't check passwords itself. It sends the person to the identity provider, using OpenID Connect, with a one-time secret called P.K.C.E., so a stolen code is useless." },
  h2: { text: '2 · The person proves who they are with a passkey: FIDO2 and WebAuthn, phishing-resistant.',
        say: "Step two. The person proves who they are, ideally with a pass key, built on FIDO2 and Web Authen. The private key never leaves the phone, and it only answers the real bank's site. A fake site gets nothing." },
  h3: { text: '3 · A risk engine weighs device, place and behavior: allow, ask for more, or deny.',
        say: 'Step three. A risk engine weighs the context: device, place, time, usual behavior. Normal? Access is granted. Unusual? It asks for stronger proof, or denies.' },
  h4: { text: '4 · Tokens: the ID token says who signed in; the access token says what the app may do, for minutes.',
        say: 'Step four. The identity provider issues tokens. The I.D. token says who signed in, and how. The access token says what the app may do, on which system, for a few minutes.' },
  h5: { text: '5 · Every API call checks the token: signature, issuer, audience, expiry and scope.',
        say: "Step five. Every call to the bank's A.P.I. checks the token: signature, issuer, audience, expiry and scope. On every call, not just at sign-in." },
  h6: { text: '6 · If risk changes, the session and its tokens are revoked at once: Shared Signals and CAEP.',
        say: 'Step six. The session stays under watch. If risk changes, say the phone number just moved to a new SIM card, the session and its tokens are revoked at once, through standards like Shared Signals.' },

  agent0: { say: 'Now, the same question for an A.I. agent. It needs more than a login.' },
  a1: { text: '1 · The agent has its own identity: registered, owned, proven with a certificate. Never a borrowed password.',
        say: "First, the agent has its own identity: registered, with a named human owner, and proven with a certificate over mutual T.L.S. Never a shared password, or a person's token." },
  a2: { text: '2 · A person delegates one task. Token exchange issues a token that names both: the person and the agent.',
        say: 'Second, a person delegates one task: pay one supplier invoice, up to two thousand dollars. Through OAuth token exchange, the agent gets a token that names both: the person, and the agent acting for them.' },
  a3: { text: "3 · That token is the mandate: one task, one system, a limit, ten minutes, bound to the agent's key.",
        say: "That token is the mandate: one task, one system, an amount limit, ten minutes. And it's bound to the agent's own key, so a stolen copy is useless." },
  a4: { text: '4 · Every tool call passes a policy check: who, for whom, what, how much. $1,840 to a known supplier: allowed.',
        say: 'Third, every call passes a policy check. Who is the agent? For whom? What action, and how much? Eighteen hundred and forty dollars to a known supplier: allowed.' },
  a5: { text: '5 · $48,000 to a new payee is out of mandate. The person is asked on their own phone (CIBA), and refuses.',
        say: "Now the agent tries to send forty-eight thousand dollars to a new payee. That's outside the mandate, so the person is asked to approve on their own phone, through a request called C.I.B.A. They refuse. The payment is blocked." },
  a6: { text: '6 · Agent to agent, a token cannot be passed along. Each hop exchanges it for its own, narrower token.',
        say: "And when one agent calls another, it can't hand over its token: the token was issued for one audience only. Each hop exchanges it for its own, narrower token, as the Model Context Protocol requires. Every decision lands in the audit trail." },

  proto0: { say: 'Here are the protocols behind all of this, and the weak links attackers look for.' },
  p1: { text: 'Sign-in and federation: OpenID Connect and SAML. Authorization: OAuth 2.0, with PKCE and bound tokens.',
        say: 'For sign-in and federation: OpenID Connect, and the older SAML. For authorization: OAuth two, with P.K.C.E., and tokens bound to their holder.' },
  p2: { text: 'Proof of identity: passkeys and smart cards first, app codes and push next. SMS codes and passwords alone: weakest.',
        say: 'To prove identity: pass keys and smart cards first. Authenticator codes and push approvals next. Text message codes, and passwords alone, are the weakest. A SIM swap or a fake site can steal them.' },
  p3: { text: 'Inside the network: Kerberos and LDAP. NTLM is legacy, and a stolen hash is enough to sign in.',
        say: 'Inside the company network, Windows directories use Kerberos and el-dap. The older N.T.L.M. protocol is still everywhere, and attackers love it. A stolen password hash is enough to sign in.' },
  p4: { text: 'Machines and agents: mutual TLS, signed assertions, token exchange, workload identity. Static API keys leak.',
        say: 'Machines and agents should use mutual T.L.S., signed assertions, token exchange and workload identity. Static A.P.I. keys and secrets in code never expire on their own, and they leak.' },
  p5: { text: 'Lifecycle and signals: SCIM creates and removes accounts, Shared Signals spread risk, CIBA asks the owner.',
        say: 'For the lifecycle: Skim creates and removes accounts automatically. Shared Signals spread risk events between systems, in real time. And C.I.B.A. asks the right person for approval, on their own device.' },
  p6: { text: 'The red ones are where most identity attacks begin.' },

  std0: { say: 'Standards and regulators set the rules.' },
  n1: { text: 'NIST SP 800-63-4: assurance levels for digital identity. The highest requires phishing-resistant authenticators.',
        say: 'NIST special publication eight hundred, sixty-three, revision four, defines assurance levels for digital identity. At the highest level, phishing-resistant authenticators are required.' },
  n2: { text: 'NIST SP 800-207, Zero Trust: the network earns no trust. Every request is authenticated and authorized.',
        say: 'Zero Trust, in NIST eight hundred, two-oh-seven: being inside the network earns no trust. Every request is authenticated and authorized.' },
  n3: { text: 'ISO/IEC 27001 governs identities and access. PCI DSS 4.0: unique IDs, MFA into card data, tight rules on shared accounts.',
        say: 'I.S.O. twenty-seven-oh-oh-one requires managed identities and access rights. For card data, PCI D.S.S. version four requires a unique I.D. per user, multi-factor authentication into the card environment, and tight rules on shared accounts.' },
  n4: { text: 'MITRE ATT&CK names every attacker move. The OWASP Top 10 for LLMs warns of prompt injection and excessive agency.',
        say: 'MITRE Attack gives every attacker move a common name, like valid accounts, or lateral movement. For A.I. applications, the OWASP top ten warns about prompt injection, and excessive agency: more power than the task needs.' },
  n5: { text: "Regulators expect it too: OSFI B-13 in Canada, Québec's Law 25 for personal information, DORA in Europe.",
        say: "And regulators expect it. In Canada, the oz-fee guideline B-13 covers technology and cyber risk, identity and access included. Quebec's Law 25 protects personal information. And in Europe, DORA." },

  prac0: { say: 'Eight practices put these rules to work.' },
  b1: { text: '1 · Phishing-resistant MFA, admins and payments first.   2 · Least privilege, admin rights just in time.',
        say: 'One: phishing-resistant M.F.A., starting with administrators and payments. Two: least privilege, with admin rights granted just in time, then taken back.' },
  b2: { text: '3 · One identity per machine and agent, each with an owner.   4 · Short-lived tokens, bound to their holder.',
        say: 'Three: one identity per machine and per agent, each with a named owner. No shared accounts, no shared keys. Four: short-lived tokens, for one audience, bound to their holder.' },
  b3: { text: '5 · Delegation with limits, human approval for high risk.   6 · Retire NTLM, basic authentication and SMS codes.',
        say: 'Five: delegation with limits, and a human approval for high-risk actions. Six: retire legacy protocols: N.T.L.M., basic authentication, and text message codes for high-risk use.' },
  b4: { text: '7 · Continuous evaluation: revoke when risk changes.   8 · Log every decision, review access, rehearse the kill switch.',
        say: 'Seven: continuous evaluation, so sessions and tokens are revoked the moment risk changes. Eight: log every decision, review access regularly, and rehearse the kill switch.' },

  f1: { text: 'Fraud: someone takes money, data or an account. Non-compliance: a rule not applied, the door left open.',
        say: "Two words often confused. Fraud is someone taking money, data or an account that isn't theirs. Non-compliance is a rule that isn't applied: an open door. Most frauds walk through one." },
  f2: { text: 'Fraud patterns: account takeover, SIM swap, MFA fatigue, help-desk deception, mule accounts, card testing, agent hijacking.',
        say: 'The fraud patterns: account takeover with a stolen password or session. SIM swaps, to steal one-time codes. M.F.A. fatigue: push after push until someone accepts. Help-desk deception. Mule accounts. Card testing. And now, hidden instructions that turn an A.I. agent.' },
  f3: { text: 'The open doors: shared accounts, MFA gaps, dormant accounts, standing admin rights, broken segregation of duties, agents beyond mandate.',
        say: 'The open doors: shared accounts. M.F.A. not enforced. Dormant accounts of people who left. Service accounts used by people. Standing admin rights. One person creating a payee and approving the payment. And agents acting beyond their mandate.' },
  live1: { say: 'Here is what that looks like when four crews attack a bank and a mobile operator at the same time.' },
  fx1: { text: "Hidden instructions make the bank's support agent export 12,400 customer profiles.", tag: 'hijack',
         say: "Agent hijacking. Hidden instructions make the bank's support agent export twelve thousand four hundred customer profiles." },
  fx2: { text: 'A poisoned plugin: the card agent reads 3,950 full card numbers.', tag: 'supply',
         say: 'A poisoned plugin. The card agent reads three thousand nine hundred and fifty full card numbers.' },
  fx3: { text: "A fake customer gets the operator's agent to move a phone number to the crew's eSIM.", tag: 'sim',
         say: "A SIM swap. A fake customer gets the operator's agent to move a phone number to the crew's e-SIM." },
  fx4: { text: 'With the hijacked one-time codes, 18 bank accounts are taken over.', tag: 'ato',
         say: 'Account takeover. With the hijacked one-time codes, eighteen bank accounts are taken over.' },
  fx5: { text: '$480,000 leaves for accounts the crew controls.', tag: 'mule',
         say: 'Mule accounts. Four hundred and eighty thousand dollars leaves for accounts the crew controls.' },
  fx6: { text: 'Under a minute: $1.28 million, 14,500 personal records, 3,950 cards and 49 phone numbers.',
         say: 'In under a minute: one point two eight million dollars, fourteen thousand five hundred personal records, three thousand nine hundred and fifty cards, and forty-nine phone numbers.' },

  l1: { text: 'Lateral movement: from one foothold, the attacker hops from identity to identity toward the crown jewels.',
        say: 'Lateral movement turns a small foothold into a major breach. The attacker collects credentials and tokens, and hops from identity to identity, toward the crown jewels: payments, card data, customer records.' },
  l2: { text: 'Classic path: stolen session, pass-the-hash over NTLM, Kerberoasting a service account, then admin rights.',
        say: 'The classic path. A phishing page steals a session. On the network, the attacker replays a password hash over N.T.L.M.: pass-the-hash. Then cracks a service account offline: Kerberoasting. That account is an administrator, with a way into the payment servers.' },
  l3: { text: 'Agentic path: prompt injection, a handoff to an unregistered helper, borrowed authority. Every hop uses a valid identity.',
        say: 'The agentic path is faster. Hidden instructions hijack a trusted agent. It hands off to a helper nobody registered, which borrows its authority to reach the payments agent. Every hop uses a valid identity, so nothing looks like a break-in.' },

  i1: { text: 'ISPM, Identity Security Posture Management, works before any attack: it discovers every identity and all its access.',
        say: 'I S P M, identity security posture management, works before the attack. It continuously discovers every identity, people, machines and agents, across directories, cloud identity providers, applications and agent registries, with all their access.' },
  i2: { text: 'Then it finds the open doors: no MFA, dormant accounts, shadow admins, weak service accounts, NTLM, ownerless agents.',
        say: 'Then it finds the open doors: accounts without M.F.A., dormant accounts that still work, shadow admins hidden in nested groups, service accounts open to Kerberoasting, N.T.L.M. still in use, and agents with no owner, or standing payment rights.' },
  i3: { text: 'Each finding maps to an attack path, so the fixes are ranked by risk.',
        say: 'Each finding maps to a path an attacker would use, so fixes are ranked by risk: enforce pass keys, disable dormant accounts, harden service accounts, and give every agent an owner.' },
  i4: { text: 'As fixes land, the posture score rises and the attack paths shrink. Illustrative values.',
        say: "As the fixes land, the posture score rises, and the attack paths shrink. That's also the evidence auditors and regulators ask for." },

  t1: { text: 'ITDR, Identity Threat Detection and Response, watches identity activity live, and responds in seconds.',
        say: 'Some attackers will come anyway. I T D R, identity threat detection and response, watches identity activity as it happens: sign-ins, tokens, privilege changes and agent actions. It spots attack patterns and responds in seconds.' },
  t2: { text: 'MFA fatigue: push blocked, passkey required. Token replay: session and tokens revoked.',
        say: 'Fourteen push requests denied, then one accepted from a new device: M.F.A. fatigue. Push is blocked, and a pass key required. A session token replayed from another network: token theft. The session and its tokens are revoked.' },
  t3: { text: 'Kerberoasting burst: service account password rotated. Pass-the-hash to 30 servers: host isolated, account disabled.',
        say: "A burst of Kerberos service-ticket requests: Kerberoasting. The targeted account's password is rotated. One laptop signing in to thirty servers over N.T.L.M.: pass-the-hash. The host is isolated, and the account disabled." },
  t4: { text: 'Agent beyond mandate: blocked and quarantined. SIM swap reported by the operator: transfers held.',
        say: "An agent asking for a bulk export: excessive agency. It's blocked, quarantined, and its owner is told. And a SIM swap reported by the mobile operator: the bank holds transfers until the customer approves on their own device." },
  t5: { text: 'Every response opens an incident with the full context for the security team.',
        say: 'Every response opens an incident, with the full context, for the security operations team.' },
  live2: { say: 'Back to the live attack. Same crews, same moves. This time, the identity controls are on.' },
  y1: { text: 'A bulk export is far beyond one support conversation. Blocked.', tag: 'policy',
        say: 'Policy. A bulk export is far beyond one support conversation. Blocked.' },
  y2: { text: 'The card agent may see only the last four digits. The plugin is disconnected.', tag: 'policy',
        say: 'Policy again. The card agent may see only the last four digits, and the plugin is disconnected.' },
  y3: { text: "The line's owner never approved the move. Request held.", tag: 'delegation',
        say: "Delegation. The line's owner never approved the move, so the request is held." },
  y3b: { text: 'The operator warns the bank: someone is trying to move these numbers.', tag: 'signal' },
  y5: { text: '36 eSIM moves from one session is not normal. The care agent is quarantined.', tag: 'behavior',
        say: 'Behavior. Thirty-six e-SIM moves from one session is not normal. The care agent is quarantined.' },
  y6: { text: "Acting on the operator's warning, the bank asks each customer to approve on their own device. Sign-ins denied.", tag: 'stepup' },
  kill: { text: 'The kill switch quarantines every agent the crews can reach.', tag: 'kill',
          say: 'Now the kill switch. It quarantines every agent the crews can reach.' },
  onEnd: { text: '11 attacks blocked. 6 agents and tools quarantined. 2 risk signals shared. Nothing taken.',
           say: 'Eleven attacks blocked. Six agents and tools quarantined. Two risk signals shared. Nothing taken.' },

  z0: { say: 'Put together, four layers cut both attack paths.' },
  z1: { text: 'Strong authentication: passkeys and bound tokens make a stolen session useless.',
        say: 'Strong authentication, with pass keys and bound tokens, makes a stolen session useless.' },
  z2: { text: 'ISPM closes the doors: weak service accounts, shadow admins, agents without owners.',
        say: 'Posture management closes the doors attackers need next: weak service accounts, shadow admins, and agents without owners.' },
  z3: { text: 'ITDR catches what still gets through, like pass-the-hash, and responds in seconds.',
        say: 'Detection and response catches what still gets through, like pass-the-hash, and responds in seconds.' },
  z4: { text: 'Runtime controls check every agent action against the mandate a person gave it.',
        say: 'And runtime controls check every action an agent takes against the mandate a person gave it. Every decision leaves evidence.' },

  q0: { say: 'Now, three questions for your team.' },
  q1: { say: 'Which identities have no owner?' },
  q2: { say: 'Which sign-ins still skip phishing-resistant M.F.A.?' },
  q3: { say: 'And if an agent went beyond its mandate tonight, who would know?' },
  end1: { say: "Attackers don't break in. They log in." },
  end2: { say: 'Make every identity prove itself, every time.' },
};

// Canadian French. `say` spells out numbers and writes English acronyms the way a
// French speaker says them, so the voice reads them cleanly.
const LINES_FR = {
  open1: { say: 'Les attaquants n’entrent plus par effraction.' },
  open2: { say: 'Ils se connectent.' },
  open3: { say: 'Ce film explique comment fonctionne vraiment l’authentification, comment les attaquants la détournent, et les contrôles qui les arrêtent.' },

  ids0: { say: 'Chaque requête qui atteint les systèmes d’une banque porte une identité. Il en existe trois types.' },
  ids1: { say: 'Les personnes : employés, clients et partenaires.' },
  ids2: { say: 'Les machines : serveurs, scripts et comptes de service, avec leurs certificats, leurs clés et leurs secrets.' },
  ids3: { say: 'Et les agents d’intelligence artificielle, qui agissent au nom d’une personne et appellent des outils, des données et d’autres agents. Dans la plupart des grandes organisations, les identités machines et les agents sont déjà plus nombreux que les personnes, et beaucoup n’ont pas de propriétaire.' },

  human0: { say: 'D’abord, comment une personne se connecte, étape par étape.' },
  h1: { text: '1 · L’application envoie la personne vers le fournisseur d’identité : OpenID Connect, avec un secret PKCE.',
        say: 'Première étape. L’application ne vérifie pas elle-même le mot de passe. Elle envoie la personne vers le fournisseur d’identité, avec OpenID Connect et un secret à usage unique appelé pé ka cé eu : un code volé ne sert à rien.' },
  h2: { text: '2 · La personne prouve son identité avec une clé d’accès : FIDO2 et WebAuthn, résistante à l’hameçonnage.',
        say: 'Deuxième étape. La personne prouve son identité, idéalement avec une clé d’accès, basée sur Fido deux et Web Authen. La clé privée ne quitte jamais le téléphone, et elle ne répond qu’au vrai site de la banque. Un faux site n’obtient rien.' },
  h3: { text: '3 · Un moteur de risque évalue l’appareil, le lieu et le comportement : accepter, exiger plus, ou refuser.',
        say: 'Troisième étape. Un moteur de risque évalue le contexte : appareil, lieu, heure, comportement habituel. Tout est normal ? L’accès est accordé. C’est inhabituel ? Il exige une preuve plus forte, ou il refuse.' },
  h4: { text: '4 · Les jetons : le jeton d’identité dit qui s’est connecté ; le jeton d’accès dit ce que l’application peut faire, pour quelques minutes.',
        say: 'Quatrième étape. Le fournisseur d’identité émet des jetons. Le jeton d’identité dit qui s’est connecté, et comment. Le jeton d’accès dit ce que l’application peut faire, sur quel système, pour quelques minutes.' },
  h5: { text: '5 · Chaque appel d’API vérifie le jeton : signature, émetteur, audience, expiration et portée.',
        say: 'Cinquième étape. Chaque appel à l’A.P.I. de la banque vérifie le jeton : signature, émetteur, audience, expiration et portée. À chaque appel, pas seulement à la connexion.' },
  h6: { text: '6 · Si le risque change, la session et ses jetons sont révoqués aussitôt : Shared Signals et CAEP.',
        say: 'Sixième étape. La session reste surveillée. Si le risque change, par exemple si le numéro vient de passer sur une autre carte SIM, la session et ses jetons sont révoqués aussitôt, grâce à des normes de partage de signaux de risque.' },

  agent0: { say: 'Maintenant, la même question pour un agent d’intelligence artificielle. Il lui faut plus qu’une connexion.' },
  a1: { text: '1 · L’agent a sa propre identité : enregistrée, avec un propriétaire, prouvée par un certificat. Jamais un mot de passe emprunté.',
        say: 'D’abord, l’agent a sa propre identité : enregistrée, avec un propriétaire humain nommé, et prouvée par un certificat en té èl èsse mutuel. Jamais un mot de passe partagé, ni le jeton d’une personne.' },
  a2: { text: '2 · Une personne délègue une tâche. L’échange de jetons émet un jeton qui nomme les deux : la personne et l’agent.',
        say: 'Ensuite, une personne délègue une seule tâche : payer une facture de fournisseur, jusqu’à deux mille dollars. Grâce à l’échange de jetons, l’agent reçoit un jeton qui nomme les deux : la personne, et l’agent qui agit pour elle.' },
  a3: { text: '3 · Ce jeton est le mandat : une tâche, un système, un plafond, dix minutes, lié à la clé de l’agent.',
        say: 'Ce jeton, c’est le mandat : une tâche, un système, un plafond, dix minutes. Et il est lié à la clé de l’agent : une copie volée ne sert à rien.' },
  a4: { text: '4 · Chaque appel d’outil passe un contrôle de politique : qui, pour qui, quoi, combien. 1 840 $ à un fournisseur connu : autorisé.',
        say: 'Puis, chaque appel passe un contrôle de politique. Qui est l’agent ? Pour qui ? Quelle action, et quel montant ? Mille huit cent quarante dollars à un fournisseur connu : autorisé.' },
  a5: { text: '5 · 48 000 $ à un nouveau bénéficiaire, c’est hors mandat. La personne est sollicitée sur son téléphone (CIBA) et refuse.',
        say: 'Maintenant, l’agent tente d’envoyer quarante-huit mille dollars à un nouveau bénéficiaire. C’est hors mandat : la personne doit approuver sur son propre téléphone, par une demande appelée cé i bé a. Elle refuse. Le paiement est bloqué.' },
  a6: { text: '6 · D’agent à agent, un jeton ne se transmet pas. Chaque saut l’échange contre son propre jeton, plus restreint.',
        say: 'Et quand un agent en appelle un autre, il ne peut pas lui remettre son jeton : ce jeton a été émis pour un seul destinataire. Chaque saut l’échange contre son propre jeton, plus restreint, comme l’exige le protocole èm cé pé. Chaque décision est inscrite au journal d’audit.' },

  proto0: { say: 'Voici les protocoles derrière tout cela, et les maillons faibles que cherchent les attaquants.' },
  p1: { text: 'Connexion et fédération : OpenID Connect et SAML. Autorisation : OAuth 2.0, avec PKCE et des jetons liés.',
        say: 'Pour la connexion et la fédération : OpenID Connect, et le plus ancien SAML. Pour l’autorisation : le protocole de délégation d’accès, avec pé ka cé eu, et des jetons liés à leur détenteur.' },
  p2: { text: 'Preuve d’identité : clés d’accès et cartes à puce d’abord, codes et notifications ensuite. Codes SMS et mots de passe seuls : les plus faibles.',
        say: 'Pour prouver son identité : les clés d’accès et les cartes à puce d’abord. Ensuite, les codes d’application et les notifications. Les codes par texto et les mots de passe seuls sont les plus faibles : un échange de carte SIM ou un faux site peut les voler.' },
  p3: { text: 'Dans le réseau : Kerberos et LDAP. NTLM est un héritage : un hachage volé suffit pour se connecter.',
        say: 'Dans le réseau de l’entreprise, les annuaires Windows utilisent Kerberos et LDAP. Le vieux protocole ène té èle ème est encore partout, et les attaquants l’adorent : le hachage d’un mot de passe volé suffit pour se connecter.' },
  p4: { text: 'Machines et agents : TLS mutuel, assertions signées, échange de jetons, identité de charge de travail. Les clés d’API statiques fuient.',
        say: 'Les machines et les agents devraient utiliser le té èl èsse mutuel, des assertions signées, l’échange de jetons et une identité de charge de travail. Les clés statiques et les secrets dans le code n’expirent jamais d’eux-mêmes, et ils finissent par fuir.' },
  p5: { text: 'Cycle de vie et signaux : SCIM crée et retire les comptes, Shared Signals diffuse le risque, CIBA demande au titulaire.',
        say: 'Pour le cycle de vie : un protocole de provisionnement crée et retire les comptes automatiquement. Des normes de partage de signaux diffusent les événements de risque entre les systèmes, en temps réel. Et cé i bé a demande l’approbation à la bonne personne, sur son propre appareil.' },
  p6: { text: 'En rouge : c’est là que commencent la plupart des attaques d’identité.' },

  std0: { say: 'Les normes et les régulateurs fixent les règles.' },
  n1: { text: 'NIST SP 800-63-4 : des niveaux d’assurance pour l’identité numérique. Le plus élevé exige des authentifiants résistants à l’hameçonnage.',
        say: 'La publication spéciale huit cent soixante-trois du NIST, quatrième révision, définit des niveaux d’assurance pour l’identité numérique. Au niveau le plus élevé, les authentifiants résistants à l’hameçonnage sont obligatoires.' },
  n2: { text: 'NIST SP 800-207, Zero Trust : le réseau ne donne aucune confiance. Chaque requête est authentifiée et autorisée.',
        say: 'Le Zero Trust, décrit dans la publication huit cent, deux cent sept, du NIST : être dans le réseau ne donne aucune confiance. Chaque requête est authentifiée et autorisée.' },
  n3: { text: 'ISO/IEC 27001 encadre les identités et les accès. PCI DSS 4.0 : identifiant unique, MFA pour les données de cartes, règles strictes sur les comptes partagés.',
        say: 'La norme ISO vingt-sept mille un exige une gestion des identités et des droits d’accès. Pour les données de cartes, la norme PCI DSS version quatre exige un identifiant unique par utilisateur, l’authentification multifacteur pour accéder à l’environnement des cartes, et des règles strictes sur les comptes partagés.' },
  n4: { text: 'MITRE ATT&CK nomme chaque geste d’attaquant. Le top 10 OWASP pour les LLM met en garde contre l’injection d’instructions et le pouvoir d’action excessif.',
        say: 'Le référentiel Mitre Attaque donne un nom commun à chaque geste d’attaquant, comme l’usage de comptes valides ou le mouvement latéral. Pour les applications d’intelligence artificielle, le top dix de l’OWASP met en garde contre l’injection d’instructions et le pouvoir d’action excessif : plus de pouvoir que la tâche n’en demande.' },
  n5: { text: 'Les régulateurs l’exigent aussi : ligne directrice B-13 du BSIF au Canada, Loi 25 au Québec, DORA en Europe.',
        say: 'Et les régulateurs l’exigent. Au Canada, la ligne directrice bé treize du BSIF encadre les risques technologiques et cyber, identités et accès compris. Au Québec, la Loi vingt-cinq protège les renseignements personnels. Et en Europe, le règlement DORA.' },

  prac0: { say: 'Voici huit pratiques qui mettent ces règles en œuvre.' },
  b1: { text: '1 · MFA résistante à l’hameçonnage, administrateurs et paiements d’abord.   2 · Moindre privilège, droits d’administration juste à temps.',
        say: 'Un : une authentification multifacteur résistante à l’hameçonnage, en commençant par les administrateurs et les paiements. Deux : le moindre privilège, avec des droits d’administration accordés juste à temps, puis retirés.' },
  b2: { text: '3 · Une identité par machine et par agent, avec un propriétaire.   4 · Des jetons de courte durée, liés à leur détenteur.',
        say: 'Trois : une identité par machine et par agent, chacune avec un propriétaire nommé. Ni comptes ni clés partagés. Quatre : des jetons de courte durée, pour un seul destinataire, liés à leur détenteur.' },
  b3: { text: '5 · Délégation avec limites, approbation humaine pour le haut risque.   6 · Retirer NTLM, l’authentification de base et les codes SMS.',
        say: 'Cinq : une délégation avec des limites, et une approbation humaine pour les actions à haut risque. Six : retirer les protocoles hérités : ène té èle ème, l’authentification de base, et les codes par texto pour les usages à risque.' },
  b4: { text: '7 · Évaluation continue : révoquer dès que le risque change.   8 · Journaliser chaque décision, revoir les accès, répéter l’arrêt d’urgence.',
        say: 'Sept : l’évaluation continue, pour couper les sessions et les jetons dès que le risque change. Huit : journaliser chaque décision, revoir les accès régulièrement, et répéter l’arrêt d’urgence.' },

  f1: { text: 'Fraude : quelqu’un prend de l’argent, des données ou un compte. Non-conformité : une règle non appliquée, la porte restée ouverte.',
        say: 'Deux mots souvent confondus. La fraude, c’est quelqu’un qui prend de l’argent, des données ou un compte qui ne lui appartient pas. La non-conformité, c’est une règle qui n’est pas appliquée : une porte ouverte. La plupart des fraudes passent par l’une d’elles.' },
  f2: { text: 'Fraudes : prise de contrôle de compte, échange de SIM, fatigue MFA, tromperie du centre d’assistance, comptes de mules, test de cartes, détournement d’agent.',
        say: 'Les schémas de fraude : la prise de contrôle de compte, avec un mot de passe ou une session volés. L’échange de carte SIM, pour voler les codes à usage unique. La fatigue MFA : notification après notification, jusqu’à ce que quelqu’un accepte. Les faux appels au centre d’assistance. Les comptes de complices. Le test de cartes. Et maintenant, des instructions cachées qui retournent un agent d’intelligence artificielle.' },
  f3: { text: 'Les portes ouvertes : comptes partagés, MFA non imposée, comptes dormants, droits d’administration permanents, séparation des tâches rompue, agents hors mandat.',
        say: 'Les portes ouvertes : des comptes partagés. Une MFA non imposée. Les comptes dormants de personnes parties. Des comptes de service utilisés par des personnes. Des droits d’administration permanents. Une même personne qui crée un bénéficiaire et approuve le paiement. Et des agents qui dépassent leur mandat.' },
  live1: { say: 'Voici ce que cela donne quand quatre équipes attaquent en même temps une banque et un opérateur mobile.' },
  fx1: { text: 'Des instructions cachées font exporter 12 400 profils clients à l’agent de soutien de la banque.', tag: 'hijack',
         say: 'Détournement d’agent. Des instructions cachées font exporter douze mille quatre cents profils clients à l’agent de soutien de la banque.' },
  fx2: { text: 'Un module piégé : l’agent des cartes lit 3 950 numéros de carte complets.', tag: 'supply',
         say: 'Un module piégé. L’agent des cartes lit trois mille neuf cent cinquante numéros de carte complets.' },
  fx3: { text: 'Un faux client obtient de l’agent de l’opérateur le transfert d’un numéro vers l’eSIM de l’équipe.', tag: 'sim',
         say: 'Un échange de SIM. Un faux client obtient de l’agent de l’opérateur le transfert d’un numéro vers la carte sim virtuelle de l’équipe.' },
  fx4: { text: 'Avec les codes détournés, 18 comptes bancaires sont piratés.', tag: 'ato',
         say: 'La prise de contrôle de compte. Avec les codes détournés, dix-huit comptes bancaires sont piratés.' },
  fx5: { text: '480 000 $ partent vers des comptes que l’équipe contrôle.', tag: 'mule',
         say: 'Des comptes de complices. Quatre cent quatre-vingt mille dollars partent vers des comptes que l’équipe contrôle.' },
  fx6: { text: 'En moins d’une minute : 1,28 million $, 14 500 profils clients, 3 950 cartes et 49 numéros de téléphone.',
         say: 'En moins d’une minute : près d’un million trois cent mille dollars, quatorze mille cinq cents profils clients, trois mille neuf cent cinquante cartes, et quarante-neuf numéros de téléphone.' },

  l1: { text: 'Mouvement latéral : depuis une brèche, l’attaquant saute d’identité en identité vers les joyaux de la couronne.',
        say: 'Le mouvement latéral transforme une petite brèche en incident majeur. L’attaquant récolte des identifiants et des jetons, et saute d’identité en identité, vers les joyaux de la couronne : les paiements, les données de cartes, les dossiers clients.' },
  l2: { text: 'Chemin classique : session volée, pass-the-hash en NTLM, Kerberoasting d’un compte de service, puis droits d’administrateur.',
        say: 'Le chemin classique. Une page d’hameçonnage vole une session. Sur le réseau, l’attaquant réutilise le hachage d’un mot de passe, en ène té èle ème. Puis, avec des tickets Kerberos, il casse sur sa propre machine le mot de passe d’un compte de service. Ce compte est administrateur, avec un accès aux serveurs de paiement.' },
  l3: { text: 'Chemin agentique : injection d’instructions, relais vers un assistant non enregistré, autorité empruntée. Chaque saut utilise une identité valide.',
        say: 'Le chemin agentique va plus vite. Des instructions cachées détournent un agent de confiance. Il passe la main à un assistant que personne n’a enregistré, qui emprunte son autorité pour atteindre l’agent des paiements. Chaque saut utilise une identité valide : rien ne ressemble à une effraction.' },

  i1: { text: 'L’ISPM, gestion de la posture de sécurité des identités, agit avant toute attaque : elle découvre chaque identité et tous ses accès.',
        say: 'L’i èsse pé ème, la gestion de la posture de sécurité des identités, agit avant toute attaque. Elle découvre en continu chaque identité : personnes, machines et agents, dans les annuaires, les fournisseurs d’identité infonuagiques, les applications et les registres d’agents, avec tous leurs accès.' },
  i2: { text: 'Puis elle trouve les portes ouvertes : sans MFA, comptes dormants, administrateurs fantômes, comptes de service faibles, NTLM, agents sans propriétaire.',
        say: 'Ensuite, elle trouve les portes ouvertes : des comptes sans MFA, des comptes dormants qui fonctionnent encore, des administrateurs fantômes cachés dans des groupes imbriqués, des comptes de service faciles à casser, le vieux ène té èle ème encore utilisé, et des agents qui n’ont pas de propriétaire, ou qui gardent des droits de paiement permanents.' },
  i3: { text: 'Chaque constat correspond à un chemin d’attaque : les correctifs sont classés par risque.',
        say: 'Chaque constat correspond à un chemin qu’un attaquant utiliserait. Les correctifs sont donc classés par risque : imposer les clés d’accès, désactiver les comptes dormants, durcir les comptes de service, et donner un propriétaire à chaque agent.' },
  i4: { text: 'À mesure que les correctifs s’appliquent, le score monte et les chemins d’attaque rétrécissent. Valeurs illustratives.',
        say: 'À mesure que les correctifs sont appliqués, le score de posture monte, et les chemins d’attaque rétrécissent. C’est aussi la preuve que demandent les auditeurs et les régulateurs.' },

  t1: { text: 'L’ITDR, détection et réponse aux menaces d’identité, surveille l’activité en direct, et répond en quelques secondes.',
        say: 'Certains attaquants viendront quand même. L’i té dé erre, la détection et la réponse aux menaces liées aux identités, surveille l’activité en direct : connexions, jetons, changements de droits et actions des agents. Elle repère les schémas d’attaque et répond en quelques secondes.' },
  t2: { text: 'Fatigue MFA : notifications bloquées, clé d’accès exigée. Jeton rejoué : session et jetons révoqués.',
        say: 'Quatorze notifications refusées, puis une acceptée depuis un nouvel appareil : la fatigue MFA. Les notifications sont bloquées, et une clé d’accès est exigée. Un jeton de session rejoué depuis un autre réseau : un vol de jeton. La session et ses jetons sont révoqués.' },
  t3: { text: 'Rafale de Kerberoasting : mot de passe du compte de service renouvelé. Pass-the-hash vers 30 serveurs : poste isolé, compte désactivé.',
        say: 'Une rafale de demandes de tickets Kerberos : quelqu’un tente de casser un compte de service. Son mot de passe est renouvelé. Un portable qui se connecte à trente serveurs en ène té èle ème : c’est un hachage volé qu’on réutilise. Le poste est isolé, et le compte désactivé.' },
  t4: { text: 'Agent hors mandat : bloqué et mis en quarantaine. Échange de SIM signalé par l’opérateur : virements retenus.',
        say: 'Un agent qui demande une exportation massive : pouvoir d’action excessif. Il est bloqué, mis en quarantaine, et son propriétaire est prévenu. Et un échange de SIM signalé par l’opérateur mobile : la banque retient les virements jusqu’à ce que le client approuve sur son propre appareil.' },
  t5: { text: 'Chaque réponse ouvre un incident, avec tout le contexte, pour l’équipe de sécurité.',
        say: 'Chaque réponse ouvre un incident, avec tout le contexte, pour l’équipe des opérations de sécurité.' },
  live2: { say: 'Retour à l’attaque en direct. Mêmes équipes, mêmes gestes. Cette fois, les contrôles d’identité sont activés.' },
  y1: { text: 'Une exportation massive dépasse de loin une conversation de soutien. Bloquée.', tag: 'policy',
        say: 'Politique. Une exportation massive dépasse de loin une conversation de soutien. Bloquée.' },
  y2: { text: 'L’agent des cartes ne voit que les quatre derniers chiffres. Le module est déconnecté.', tag: 'policy',
        say: 'Politique, encore. L’agent des cartes ne voit que les quatre derniers chiffres, et le module est déconnecté.' },
  y3: { text: 'Le titulaire de la ligne n’a jamais approuvé le transfert. Demande retenue.', tag: 'delegation',
        say: 'Délégation. Le titulaire de la ligne n’a jamais approuvé le transfert, alors la demande est retenue.' },
  y3b: { text: 'L’opérateur prévient la banque : quelqu’un tente de transférer ces numéros.', tag: 'signal' },
  y5: { text: '36 transferts d’eSIM dans une même session, ce n’est pas normal. L’agent est mis en quarantaine.', tag: 'behavior',
        say: 'Comportement. Trente-six transferts de cartes sim virtuelles dans une même session, ce n’est pas normal. L’agent est mis en quarantaine.' },
  y6: { text: 'Grâce à l’alerte de l’opérateur, la banque demande à chaque client d’approuver sur son propre appareil. Connexions refusées.', tag: 'stepup',
        say: 'Grâce à l’alerte de l’opérateur, la banque demande à chaque client de confirmer sur son propre appareil. Les connexions sont refusées.' },
  kill: { text: 'Le coupe-circuit met en quarantaine chaque agent que les équipes peuvent atteindre.', tag: 'kill',
          say: 'Maintenant, le coupe-circuit. Il met en quarantaine chaque agent que les équipes peuvent atteindre.' },
  onEnd: { text: '11 attaques bloquées. 6 agents et outils en quarantaine. 2 signaux de risque partagés. Rien n’a été pris.',
           say: 'Onze attaques bloquées. Six agents et outils en quarantaine. Deux signaux de risque partagés. Rien n’a été pris.' },

  z0: { say: 'Ensemble, quatre couches de protection bloquent les deux chemins d’attaque.' },
  z1: { text: 'Authentification forte : clés d’accès et jetons liés rendent une session volée inutile.',
        say: 'L’authentification forte, avec des clés d’accès et des jetons liés, rend une session volée inutile.' },
  z2: { text: 'L’ISPM ferme les portes : comptes de service faibles, administrateurs fantômes, agents sans propriétaire.',
        say: 'La gestion de la posture ferme les portes dont les attaquants ont besoin : comptes de service faibles, administrateurs fantômes, et agents qui n’ont pas de propriétaire.' },
  z3: { text: 'L’ITDR attrape ce qui passe quand même, comme le pass-the-hash, et répond en quelques secondes.',
        say: 'La détection et la réponse attrapent ce qui passe quand même, comme un hachage volé qu’on réutilise, et répondent en quelques secondes.' },
  z4: { text: 'Les contrôles d’exécution vérifient chaque action d’agent par rapport au mandat donné par une personne.',
        say: 'Et les contrôles d’exécution vérifient chaque action d’un agent par rapport au mandat qu’une personne lui a donné. Chaque décision laisse une preuve.' },

  q0: { say: 'Trois questions pour votre équipe.' },
  q1: { say: 'Quelles identités n’ont pas de propriétaire ?' },
  q2: { say: 'Quelles connexions se passent encore d’une MFA résistante à l’hameçonnage ?' },
  q3: { say: 'Et si un agent dépassait son mandat cette nuit, qui le saurait ?' },
  end1: { say: 'Les attaquants n’entrent pas par effraction. Ils se connectent.' },
  end2: { say: 'Exigez que chaque identité fasse ses preuves, à chaque fois.' },
};

// Chapter marks written into the video file.
const CHAPTER = {
  en: { intro: 'Introduction', ids: 'Three kinds of identity', human: 'How a person signs in', agent: 'How an AI agent should authenticate',
        protocols: 'Protocols and weak links', standards: 'Standards and regulation', practices: 'Best practices',
        fraud: 'Fraud and non-compliance', off: 'Live attack, controls off', lateral: 'Lateral movement', ispm: 'ISPM',
        itdr: 'ITDR', on: 'Live attack, controls on', layers: 'Defense in depth', close: 'Three questions' },
  fr: { intro: 'Introduction', ids: 'Trois types d’identité', human: 'Comment une personne se connecte', agent: 'Comment un agent IA doit s’authentifier',
        protocols: 'Protocoles et maillons faibles', standards: 'Normes et réglementation', practices: 'Bonnes pratiques',
        fraud: 'Fraude et non-conformité', off: 'Attaque en direct, sans contrôles', lateral: 'Mouvement latéral', ispm: 'ISPM',
        itdr: 'ITDR', on: 'Attaque en direct, avec contrôles', layers: 'Défense en profondeur', close: 'Trois questions' },
}[LANG];

const CARDS = {
  en: {
    opening: `
      <div class="ey" data-k="ey">A teaching film · fictional bank, operator, people and data</div>
      <div class="l" data-k="l1">Attackers don't break in anymore.</div>
      <div class="l alert" data-k="l2">They log in.</div>
      <div class="fine" data-k="fine">Authentication flows · protocols · standards · best practices · fraud and non-compliance ·
        lateral movement · ISPM · ITDR</div>`,
    live1: `<div class="ey" data-k="ey">Live simulation · controls off</div><div class="l" data-k="l1">Four crews. One bank. One mobile operator.</div>`,
    live2: `<div class="ey" data-k="ey">Live simulation · controls on</div><div class="l" data-k="l1">Same crews. Same moves. Controls on.</div>`,
    questions: { ey: 'For your team', title: 'Three questions', items: [
      ['idcard', 'Ownership', 'Which identities have no owner?'],
      ['key', 'Authentication', 'Which sign-ins still skip phishing-resistant MFA?'],
      ['power', 'Agents', 'If an agent went beyond its mandate tonight, who would know?'],
    ] },
    closing: `
      <div class="l" data-k="l1">Attackers don't break in. They log in.</div>
      <div class="l alert" data-k="l2">Make every identity prove itself, every time.</div>
      <div class="fine" data-k="fine">Teaching film. Lumora Bank, Teleqo Mobile, the people and all data are fictional, and the ISPM
        and ITDR values are illustrative. It explains public identity standards and the class of controls delivered by IBM Verify
        Identity Protection (ISPM and ITDR), with runtime identity controls for AI agents. The screens are illustrations, not IBM
        software. Standards are summarized; see each document for its full text.</div>`,
  },
  fr: {
    opening: `
      <div class="ey" data-k="ey">Un film pédagogique · banque, opérateur, personnes et données fictifs</div>
      <div class="l" data-k="l1">Les attaquants n’entrent plus par effraction.</div>
      <div class="l alert" data-k="l2">Ils se connectent.</div>
      <div class="fine" data-k="fine">Flux d’authentification · protocoles · normes · bonnes pratiques · fraude et non-conformité ·
        mouvement latéral · ISPM · ITDR</div>`,
    live1: `<div class="ey" data-k="ey">Simulation en direct · sans contrôles</div><div class="l" data-k="l1">Quatre équipes. Une banque. Un opérateur mobile.</div>`,
    live2: `<div class="ey" data-k="ey">Simulation en direct · avec contrôles</div><div class="l" data-k="l1">Mêmes équipes. Mêmes gestes. Contrôles activés.</div>`,
    questions: { ey: 'Pour votre équipe', title: 'Trois questions', items: [
      ['idcard', 'Responsabilité', 'Quelles identités n’ont pas de propriétaire ?'],
      ['key', 'Authentification', 'Quelles connexions se passent encore d’une MFA résistante à l’hameçonnage ?'],
      ['power', 'Agents', 'Si un agent dépassait son mandat cette nuit, qui le saurait ?'],
    ] },
    closing: `
      <div class="l" data-k="l1">Les attaquants n’entrent pas par effraction. Ils se connectent.</div>
      <div class="l alert" data-k="l2">Exigez que chaque identité fasse ses preuves, à chaque fois.</div>
      <div class="fine" data-k="fine">Film pédagogique. La Banque Lumora, Teleqo Mobile, les personnes et toutes les données sont
        fictives, et les valeurs ISPM et ITDR sont illustratives. Il explique des normes publiques d’identité et la catégorie de
        contrôles offerte par IBM Verify Identity Protection (ISPM et ITDR), avec des contrôles d’identité à l’exécution pour les
        agents IA. Les écrans sont des illustrations, pas un logiciel IBM. Les normes sont résumées ; consultez chaque document
        pour son texte complet.</div>`,
  },
}[LANG];

const questionsCard = ({ ey, title, items }) => `
  <div class="ey" data-k="ey">${ey}</div>
  <div class="l mid" data-k="l1">${title}</div>
  <div class="objs">${items.map(([icon, name, q], i) => `
    <div class="obj" data-k="o${i + 1}"><div class="oi"><i data-ic="${icon}"></i></div>
      <div class="on">${name}</div><div class="ot">${q}</div></div>`).join('')}
  </div>`;

// French captions and cards get non-breaking spaces before : ; ? ! and inside numbers.
const frenchSpaces = (s) => s.replace(/ ([:;?!])/g, ' $1').replace(/(\d) (\d{3})/g, '$1 $2').replace(/(\d) ([$%])/g, '$1 $2');
const LINES = Object.fromEntries(Object.entries(LANG === 'fr' ? LINES_FR : LINES_EN).map(([id, l]) =>
  [id, { ...l, ...(l.text && LANG === 'fr' ? { text: frenchSpaces(l.text) } : {}), ...(l.tag ? { tag: TAG[l.tag] } : {}) }]));
const card = (html) => (LANG === 'fr' ? frenchSpaces(html) : html);

// Selectors in fraud_ring.html.
const F = {
  top: 'header.top',
  wide: ['header.top', '.main'],
  live: ['.score', '.mapcard'],
  verdict: ['.score', '#verdict'],
  run: '#runBtn',
  on: '#modeOn',
  kill: '#killBtn',
  reset: '#resetBtn',
};

// Runs inside fraud_ring.html: fires the page's scripted moves one at a time, in the
// page's own language, and runs its clock between them (as in record_fraud_ring.js).
function installSimHooks() {
  let raf = 0;
  const showClock = () => { document.getElementById('clock').textContent = mmss(S.t); };
  window.filmSim = {
    begin() { announceStart(); S.running = true; renderRun(); },
    next(holdMs) {
      cancelAnimationFrame(raf);
      const ev = SCRIPT[S.next++];
      S.t = ev.t;
      showClock();
      fire(ev);
      const target = S.next < SCRIPT.length ? SCRIPT[S.next].t : END_T;
      const from = S.t, start = performance.now();
      const tick = (now) => {
        const k = Math.min(1, (now - start) / holdMs);
        S.t = from + (target - from) * k;
        showClock();
        if (k < 1) raf = requestAnimationFrame(tick);
      };
      raf = requestAnimationFrame(tick);
    },
    end() { cancelAnimationFrame(raf); finish(); },
  };
}

record({
  out: OUT,
  lines: LINES,
  tagFor: (t) => t,
  pages: [
    { id: 'xp', file: 'identity_explained.html', hash: LANG === 'fr' ? 'fr' : '' },
    { id: 'sim', file: 'fraud_ring.html', wrap: true, hash: LANG === 'fr' ? 'fr' : '', hidden: true },
  ],
  async setup({ frames, frame, stage }) {
    await frames.sim.evaluate(installSimHooks);
    await frame('sim')('frame', F.wide, { safeH: 1080, fill: 0.96, instant: true });
    await frame('xp', 'explain')('film');
    await frame('xp', 'explain')('go', 'ids', 0, true);
    await stage('card', card(CARDS.opening));
  },
  async play({ after, stage, frame, caption, speak, press, sleep, chapter }) {
    const xp = frame('xp', 'explain'), cam = frame('sim'), sim = frame('sim', 'filmSim');
    // Pacing: with a narrator, each beat waits for the line before it to finish; with
    // captions only, it waits long enough to read the line.
    let last = null;
    const readTime = (id) => Math.max(3.2, (LINES[id].text || LINES[id].say).length / 15);
    const beat = (pause = 0.5) => after(NARRATED || !last ? pause : readTime(last) + pause);
    const scene = async (steps, ids, { first = 0.9, pause = 0.5 } = {}) => {
      for (let i = 0; i < ids.length; i += 1) {
        await beat(i === 0 ? first : pause);
        if (steps[i] != null) await xp('step', steps[i]);
        if (LINES[ids[i]].text) await caption(ids[i]); else { await caption(null); speak(ids[i]); }
        last = ids[i];
      }
    };
    const toScene = async (name, pause = 1.0) => { await beat(pause); await caption(null); await xp('go', name, 0); last = null; };
    const move = (holdMs = 5200) => sim('next', holdMs);

    // Cold open
    chapter(CHAPTER.intro);
    await after(1.0); await stage('reveal', 'ey', 'l1'); speak('open1'); last = 'open1';
    await beat(0.5); await stage('reveal', 'l2'); speak('open2'); last = 'open2';
    await beat(0.9); await stage('reveal', 'fine'); speak('open3'); last = 'open3';
    await beat(1.4); await stage('cardOut');

    // 1 · Three kinds of identity
    chapter(CHAPTER.ids);
    await scene([null, 1, 2, 3], ['ids0', 'ids1', 'ids2', 'ids3'], { first: 1.4 });

    // 2 · How a person signs in
    await toScene('human'); chapter(CHAPTER.human);
    await scene([null, 1, 2, 3, 4, 5, 6], ['human0', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']);

    // 3 · How an AI agent should authenticate
    await toScene('agent'); chapter(CHAPTER.agent);
    await scene([null, 1, 2, 3, 4, 5, 6], ['agent0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6']);

    // 4 · Protocols
    await toScene('protocols'); chapter(CHAPTER.protocols);
    await scene([null, 1, 2, 3, 4, 5, 6], ['proto0', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6']);

    // 5 · Standards
    await toScene('standards'); chapter(CHAPTER.standards);
    await scene([null, 1, 2, 3, 4, 5], ['std0', 'n1', 'n2', 'n3', 'n4', 'n5']);

    // 6 · Best practices
    await toScene('practices'); chapter(CHAPTER.practices);
    await scene([null, 1, 2, 3, 4], ['prac0', 'b1', 'b2', 'b3', 'b4']);

    // 7 · Fraud and non-compliance, then the live attack with the controls off
    await toScene('fraud'); chapter(CHAPTER.fraud);
    await scene([1, 2, 3], ['f1', 'f2', 'f3']);
    await beat(1.0); await caption(null);
    await stage('card', card(CARDS.live1)); await stage('cardIn'); chapter(CHAPTER.off);
    await after(1.2); await stage('show', 'sim', true); await cam('frame', F.top, { instant: true });
    await stage('reveal', 'ey', 'l1'); speak('live1'); last = 'live1';
    await beat(0.8); await stage('cardOut');
    await after(1.3); await press(cam, F.run, { tap: true }); await sim('begin');
    await after(1.6); await stage('cursorHide'); await cam('frame', F.live);
    await after(1.4); await move(); await caption('fx1'); last = 'fx1';
    await beat(0.4); await move(); await caption('fx2'); last = 'fx2';
    await beat(0.4); await move(); await caption('fx3'); last = 'fx3';
    await beat(0.4); await caption(null);
    for (let i = 0; i < 2; i += 1) { await move(1300); await sleep(1300); }
    await move(); await caption('fx4'); last = 'fx4';
    await beat(0.4); await caption(null); await move(1300); await sleep(1300);
    await move(); await caption('fx5'); last = 'fx5';
    await beat(0.4); await caption(null);
    for (let i = 0; i < 3; i += 1) { await move(1100); await sleep(1100); }
    await sim('end'); await cam('frame', F.verdict); await caption('fx6'); last = 'fx6';

    // 8 · Lateral movement
    await beat(1.0); await caption(null); await xp('go', 'lateral', 0, true); await stage('show', 'xp'); chapter(CHAPTER.lateral);
    await scene([1, 2, 3], ['l1', 'l2', 'l3'], { first: 1.6 });

    // 9 · ISPM
    await toScene('ispm', 1.4); chapter(CHAPTER.ispm);
    await scene([1, 2, 3, 4], ['i1', 'i2', 'i3', 'i4']);

    // 10 · ITDR, then the live attack with the controls on
    await toScene('itdr'); chapter(CHAPTER.itdr);
    await scene([1, 2, 3, 4, 5], ['t1', 't2', 't3', 't4', 't5']);
    await beat(1.0); await caption(null);
    await stage('card', card(CARDS.live2)); await stage('cardIn'); chapter(CHAPTER.on);
    await after(1.2); await stage('show', 'sim', true); await cam('frame', F.top, { instant: true });
    await stage('reveal', 'ey', 'l1'); speak('live2'); last = 'live2';
    await beat(0.8); await stage('cardOut');
    await after(1.2); await press(cam, F.reset);
    await after(1.0); await press(cam, F.on);
    await after(0.8); await press(cam, F.run, { tap: true }); await sim('begin');
    await after(1.6); await stage('cursorHide'); await cam('frame', F.live);
    await after(1.4); await move(); await caption('y1'); last = 'y1';
    await beat(0.4); await move(); await caption('y2'); last = 'y2';
    await beat(0.4); await move(); await caption('y3'); last = 'y3';
    await beat(0.4); await caption('y3b'); last = 'y3b';
    await beat(0.4); await caption(null); await move(1300); await sleep(1300);
    await move(); await caption('y5'); last = 'y5';
    await beat(0.4); await move(); await caption('y6'); last = 'y6';
    await beat(0.6); await caption(null); await cam('frame', F.top);
    await after(1.4); await caption('kill'); last = 'kill'; await press(cam, F.kill);
    await after(1.8); await stage('cursorHide'); await cam('frame', F.live);
    await beat(0.6); await caption(null);
    for (let i = 0; i < 5; i += 1) { await move(1200); await sleep(1200); }
    await sim('end'); await cam('frame', F.verdict); await caption('onEnd'); last = 'onEnd';

    // 11 · Defense in depth
    await beat(1.0); await caption(null); await xp('go', 'layers', 0, true); await stage('show', 'xp'); chapter(CHAPTER.layers);
    await scene([null, 1, 2, 3, 4], ['z0', 'z1', 'z2', 'z3', 'z4'], { first: 1.6 });

    // Three questions, then the close
    await beat(1.2); await caption(null);
    await stage('card', card(questionsCard(CARDS.questions))); await stage('cardIn'); chapter(CHAPTER.close);
    await after(1.3); await stage('reveal', 'ey', 'l1'); speak('q0'); last = 'q0';
    for (let i = 1; i <= 3; i += 1) { await beat(0.3); await stage('reveal', `o${i}`); speak(`q${i}`); last = `q${i}`; }
    await beat(1.6); await stage('fadeCardText');
    await after(1.2); await stage('card', card(CARDS.closing));
    await after(0.3); await stage('reveal', 'l1'); speak('end1'); last = 'end1';
    await beat(0.7); await stage('reveal', 'l2'); speak('end2'); last = 'end2';
    await beat(1.2); await stage('reveal', 'fine');
    await after(8.0);
  },
}).catch((err) => { console.error(err); process.exit(1); });
