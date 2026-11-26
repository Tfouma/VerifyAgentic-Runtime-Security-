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
 * See narrate.py for the voice setup and record_film.js for the requirements.
 */
'use strict';
const path = require('path');
const { record } = require('./lib');

const NARRATED = Boolean(process.env.FILM_VOICE);
const OUT = path.resolve(process.argv[2] || path.join(__dirname, 'agentic-runtime-security-step-by-step.mp4'));

// `text` is the caption, `say` what the narrator reads (acronyms spelled the way they
// are spoken). Lines without `text` are spoken over a title card.
const LINES = {
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

const CHAPTERS = [
  ['map', 'The map'], ['s1', 'Step 1 · Sign in'], ['s2', 'Step 2 · Chat with the agent'], ['s3', 'Step 3 · Tool call'],
  ['s4a', 'Step 4a · Is the agent live?'], ['s4b', 'Step 4b · Token exchange'], ['s4c', 'Step 4c · One token per action'],
  ['s5', 'Step 5 · Vault decides'], ['s6', 'Step 6 · Read or write'], ['feed', 'Activity feed'], ['kills', 'Three kill switches'],
  ['observe', 'IBM Verify Identity Protection'], ['recap', 'In one line'],
];

const OPENING = `
  <div class="ey" data-k="ey">Agentic runtime security · reference architecture</div>
  <div class="l" data-k="l1">One request. Six steps. Three kill switches.</div>
  <div class="l alert" data-k="l2">How an AI agent acts for a bank employee, without ever holding a secret.</div>`;
const CLOSING = `
  <div class="l" data-k="l1">The agent never holds a secret.</div>
  <div class="l alert" data-k="l2">And every action names who it acts for.</div>
  <div class="fine" data-k="fine">Walkthrough of the bank's agentic runtime security reference architecture. Solid components were
    built and demoed in the lab; dashed components are recommended additions. Token values are illustrative. Product names belong
    to their owners.</div>`;

record({
  out: OUT,
  lines: LINES,
  pages: [{ id: 'arch', file: 'agentic_runtime_architecture.html' }],
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
