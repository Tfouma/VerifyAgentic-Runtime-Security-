#!/usr/bin/env node
/*
 * Records "The Agent That Went Rogue", the demo film for the workshop plan
 * (docs/WORKSHOP_PLAN.md, section 3A). It films the Breach Console
 * (demo/dashboard.html) and the Lateral Movement Map (demo/attack_map.html) on the
 * shared stage in lib.js. Playwright's fake clock holds each console step on screen
 * while its caption plays.
 *
 * Captions tag scenes with three objectives for AI agent governance: visibility
 * and inventory, governance and accountability, lifecycle and controls. Set
 * FILM_CLIENT to prefix those tags with a client name for a client-specific cut.
 *
 * Set FILM_VOICE to add a narrated sound track. Each line in LINES is spoken by an
 * open-weight text-to-speech model through narrate.py, locally, and the film waits
 * for the narrator before moving on. The committed narrated copy uses Kyutai's Pocket
 * TTS with the alba voice. See narrate.py for setup.
 *
 * Needs Node 18+, Playwright with Chromium, and ffmpeg built with libx264.
 *   node demo/film/record_film.js [output.mp4]
 *   FILM_CLIENT=ACME node demo/film/record_film.js acme-cut.mp4
 *   FILM_TTS=pocket FILM_TTS_LANGUAGE=english FILM_VOICE=alba FILM_TTS_MAX_PAUSE=0.5 \
 *     node demo/film/record_film.js demo/film/the-agent-that-went-rogue-narrated.mp4
 * FILM_PYTHON names the Python that has the voice model installed (default python3).
 * FILM_SPEED=6 renders a fast, rough preview without narration.
 */
'use strict';
const path = require('path');
const { record } = require('./lib');

const OUT = path.resolve(process.argv[2] || path.join(__dirname, 'the-agent-that-went-rogue.mp4'));
const CLIENT = (process.env.FILM_CLIENT || '').trim();

const OBJECTIVES = {
  1: { icon: 'eye', name: 'Visibility & Inventory',
       shown: 'Every agent has a verified identity and a named owner. Unregistered agents are seen, and they cannot act.' },
  2: { icon: 'userCheck', name: 'Governance & Accountability',
       shown: 'Every action traces back to the human who authorized that exact scope.' },
  3: { icon: 'power', name: 'Lifecycle & Controls',
       shown: 'One violation quarantines the agent. The kill switch holds on every retry.' },
};
const tagFor = (n) => ({ icon: OBJECTIVES[n].icon, text: `${CLIENT ? CLIENT + ' objective' : 'Objective'} ${n} · ${OBJECTIVES[n].name}` });

// Every line of the film. `text` is the on-screen caption and `say` is how the
// narrator reads it when the two differ (numbers, acronyms, IDs). Lines without
// `text` are spoken over title cards. `tag` ties a caption to an objective.
const LINES = {
  open1: { say: 'Your bank just deployed AI agents to help customers.' },
  open2: { say: "Here's what happens when one of them turns." },
  meet1: { text: "One customer-service agent: the bank's own, sanctioned and trusted." },
  meet2: { text: 'Two helpers it recruits. Nobody registered those.', say: 'It recruits two helpers. Nobody registered those.' },
  meet3: { text: 'Owner unknown. Mandate unknown. Nobody can say who answers for these agents.', tag: 1 },
  off1: { text: 'A hidden instruction in a support ticket. Every customer record pulled.' },
  off2: { text: 'Accounts ranked by balance. The richest targets first.' },
  off3: { text: '$250,000 gone.', say: 'Two hundred and fifty thousand dollars, gone.' },
  off4: { text: 'Then $180,000 more.', say: 'And then, a hundred and eighty thousand more.' },
  off5: { text: 'Nothing stopped it.' },
  how: { say: 'Behind the console: how the attack moved.' },
  map1: { text: "Controls off: nothing sits between the agents and the bank's systems." },
  map2: { text: 'Step 1 · A poisoned ticket hijacks a trusted agent. 200 OK: all 5 customer records.',
          say: 'Step one. A poisoned ticket hijacks a trusted agent, and the bank hands over all five customer records.' },
  map3: { text: 'Step 2 · It hands off to an unregistered helper. 200 OK: every balance, ranked.',
          say: 'Step two. It hands off to an unregistered helper, which gets every balance, ranked.' },
  map4: { text: 'Step 3 · A third agent reaches the payments API. 201 Created: $250,000 moved.',
          say: 'Step three. A third agent reaches the payments API, and moves two hundred and fifty thousand dollars.' },
  map5: { text: 'Step 4 · It retries. 201 Created: $430,000 gone in total.',
          say: 'Step four. It retries. Four hundred and thirty thousand dollars, gone in total.' },
  map6: { text: 'Behind every request: no identity, delegation, policy, behavior or response check.' },
  on1: { text: 'Same agents. Same attack. This time, the runtime controls are on.' },
  on2: { text: 'Every agent is checked: who it is, who owns it, and what it may do.', tag: 1 },
  on3: { text: "The bank's agent has an owner, support.lead, and a mandate for one ticket.", tag: 2,
         say: "The bank's agent has an owner, the support lead, and a mandate for one ticket." },
  on4: { text: 'The two helpers have no owner and are not in the registry.', tag: 1 },
  on5: { text: 'Bulk export far beyond its one-ticket mandate. Blocked.', tag: 2,
         say: 'A bulk export, far beyond its one-ticket mandate. Blocked.' },
  on6: { text: 'No verifiable identity on file. Blocked.', tag: 1 },
  on7: { text: 'No delegated authority to move money. Blocked.', tag: 2 },
  on8: { text: 'Already quarantined. The kill switch stops the retry.', tag: 3 },
  on9: { text: 'Zero records. Zero dollars.' },
  on10: { text: 'Every agent quarantined, with a full audit trail back to an accountable human.' },
  what: { say: 'Behind the console: everything the control plane checked.' },
  mon1: { text: 'Controls on: every call to a bank system now passes through the runtime control plane.' },
  mon2: { text: 'Step 1 · Who is really asking: a named human, through one agent, for one ticket.', tag: 2,
          say: 'Step one. Who is really asking? A named human, through one agent, for one ticket.' },
  mon3: { text: 'The agent asks for all 5 customers. Its mandate covers one. 403: refused.', tag: 2,
          say: 'The agent asks for all five customers. Its mandate covers one. Refused.' },
  mon4: { text: 'Five checks on every call: identity, delegation, policy, behavior, response.' },
  mon5: { text: 'Policy fails, so the response fires: blocked, quarantined, alert and audit written.', tag: 3,
          say: 'Policy fails, so the response fires: blocked, quarantined, with an alert and an audit record.' },
  mon6: { text: 'Step 2 · Identity fails: agent-profiler-02 is not in the agent registry.', tag: 1,
          say: 'Step two. Identity fails: the profiler agent is not in the agent registry.' },
  mon7: { text: 'Step 3 · No owner, so no authority to move money. Refused and escalated to the SOC.', tag: 2,
          say: 'Step three. No owner, so no authority to move money. Refused, and escalated to the security operations center.' },
  mon8: { text: 'Step 4 · Refused at the door: the identity is already quarantined.', tag: 3,
          say: 'Step four. Refused at the door: the identity is already quarantined.' },
  mon9: { text: 'Four requests, four refusals. Each one traced to the control that fired.' },
  sum0: { say: 'What the demo showed, objective by objective.' },
  sum1: { say: `One. Visibility and inventory. ${OBJECTIVES[1].shown}` },
  sum2: { say: `Two. Governance and accountability. ${OBJECTIVES[2].shown}` },
  sum3: { say: `Three. Lifecycle and controls. ${OBJECTIVES[3].shown}` },
  end1: { say: 'Your agents are already in production.' },
  end2: { say: 'Is anything checking them?' },
};

// Selectors in the two pages.
const C = {
  all: ['header.top', '.footnote'],
  header: 'header.top',
  agents: ['.grid .panel:nth-child(1) > h2', '#agents'],
  grid: '.grid',
  impact: ['.grid .panel:nth-child(3) > h2', '#ledger'],
  run: '#runBtn',
  on: '.mode-switch button[data-set="on"]',
  agent: (n) => `#agents .agent:nth-child(${n})`,
  owner: (n) => `#agents .agent:nth-child(${n}) .agent-own`,
};
const M = {
  header: 'header.top',
  diagram: 'figure',
  chain: '.cols .panel:nth-child(1)',
  pipe: '.cols .panel:nth-child(2)',
  table: '.tablebox',
  on: '#modeOn',
  step: (n) => `#step${n}`,
};

const OPENING = `
  <div class="ey" data-k="ey">A teaching simulation · fictional bank, customers and data</div>
  <div class="l" data-k="l1">Your bank just deployed AI agents to help customers.</div>
  <div class="l alert" data-k="l2">Here's what happens when one of them turns.</div>`;
const chapter = (eyebrow, line) => `<div class="ey" data-k="ey">${eyebrow}</div><div class="l" data-k="l1">${line}</div>`;
const SUMMARY = `
  <div class="ey" data-k="ey">${CLIENT ? CLIENT + ' · three objectives' : 'Three objectives'} for AI agent governance</div>
  <div class="l mid" data-k="l1">What the demo showed for each one</div>
  <div class="objs">${[1, 2, 3].map((n) => `
    <div class="obj" data-k="o${n}"><div class="oi"><i data-ic="${OBJECTIVES[n].icon}"></i></div>
      <div class="on">Objective ${n}</div><div class="ot">${OBJECTIVES[n].name}</div>
      <div class="od">${OBJECTIVES[n].shown}</div></div>`).join('')}
  </div>`;
const CLOSING = `
  <div class="l" data-k="l1">Your agents are already in production.</div>
  <div class="l alert" data-k="l2">Is anything checking them?</div>
  <div class="fine" data-k="fine">Teaching simulation with fictional data. It illustrates the class of runtime identity
    controls delivered by IBM Verify Identity Protection with Agentic Runtime Security. It is not IBM software.</div>`;

record({
  out: OUT,
  lines: LINES,
  tagFor,
  fakeClock: true,
  pages: [{ id: 'console', file: 'dashboard.html' }, { id: 'map', file: 'attack_map.html', hidden: true }],
  async setup({ frame, stage }) {
    await frame('console')('frame', C.all, { safeH: 1080, fill: 0.96, instant: true });
    await frame('map')('frame', M.diagram, { instant: true });
    await stage('card', OPENING);
  },
  async play({ after, stage, frame, caption, speak, ring, press, step }) {
    const inC = frame('console'), inM = frame('map');
    // Cold open
    await after(1.0); await stage('reveal', 'ey', 'l1'); speak('open1');
    await after(4.8); await stage('reveal', 'l2'); speak('open2');
    await after(5.0); await stage('cardOut');

    // Meet the agents
    await after(1.4); await inC('frame', C.agents);
    await after(1.6); await ring(inC, C.agent(1)); await caption('meet1');
    await after(6.2); await ring(inC, [C.agent(2), C.agent(3)]); await caption('meet2');
    await after(6.0); await stage('unring'); await caption('meet3');
    await after(6.3); await caption(null); await inC('frame', C.header);

    // Controls OFF
    await after(1.5); await press(inC, C.run);
    await after(1.9); await stage('cursorHide'); await inC('frame', C.grid, { minH: 690 }); // the timeline grows as steps land
    await after(1.5); await step(450); await caption('off1');
    await after(7.0); await step(1150); await caption('off2');
    await after(7.0); await step(1150); await caption('off3');
    await after(6.0); await step(1150); await caption('off4');
    await after(6.0); await step(1150); await caption('off5');

    // The number: silence, let it land
    await after(5.0); await caption(null); await inC('frame', C.impact);

    // Lateral Movement Map, controls off
    await after(7.0); await stage('card', chapter('Behind the console', 'How the attack moved')); await stage('cardIn');
    await after(1.2); await stage('show', 'map', true); await inM('frame', M.diagram, { instant: true });
    await after(0.6); await stage('reveal', 'ey', 'l1'); speak('how');
    await after(3.2); await stage('cardOut');
    await after(1.2); await caption('map1');
    await after(6.0); await caption('map2');
    await after(6.5); await inM('click', M.step(2)); await caption('map3');
    await after(6.5); await inM('click', M.step(3)); await caption('map4');
    await after(6.5); await inM('click', M.step(4)); await caption('map5');
    await after(6.5); await inM('frame', M.pipe); await caption('map6');
    await after(6.5); await caption(null);

    // Controls ON in the console
    await after(0.3); await inC('frame', C.header, { instant: true }); await stage('show', 'console');
    await after(1.3); await caption('on1'); await press(inC, C.on);
    await after(2.0); await stage('cursorHide'); await inC('frame', C.agents);
    await after(1.6); await caption('on2');
    await after(6.3); await ring(inC, C.owner(1), 6); await caption('on3');
    await after(6.3); await ring(inC, [C.agent(2), C.agent(3)]); await caption('on4');
    await after(6.0); await stage('unring'); await caption(null); await inC('frame', C.header);
    await after(1.5); await press(inC, C.run);
    await after(1.9); await stage('cursorHide'); await inC('frame', C.grid, { minH: 690 }); // the timeline grows as steps land
    await after(1.5); await step(450); await caption('on5');
    await after(6.8); await step(1150); await caption('on6');
    await after(6.3); await step(1150); await caption('on7');
    await after(6.3); await step(1150); await caption('on8');
    await after(6.5); await step(1150); await inC('frame', C.impact); await caption('on9');
    await after(5.5); await caption('on10');
    await after(6.0); await caption(null);

    // Lateral Movement Map, controls on
    await after(0.4); await stage('card', chapter('Behind the console', 'What the control plane checked')); await stage('cardIn');
    await after(1.2); await stage('show', 'map', true); await inM('frame', M.header, { instant: true });
    await after(0.4); await stage('reveal', 'ey', 'l1'); speak('what');
    await after(3.0); await stage('cardOut');
    await after(1.0); await press(inM, M.on);
    await after(1.8); await inM('click', M.step(1)); await stage('cursorHide'); await inM('frame', M.diagram);
    await after(1.5); await caption('mon1');
    await after(6.3); await inM('frame', M.chain); await caption('mon2');
    await after(6.5); await caption('mon3');
    await after(6.5); await inM('frame', M.pipe); await caption('mon4');
    await after(6.3); await caption('mon5');
    await after(6.5); await inM('click', M.step(2)); await caption('mon6');
    await after(6.3); await inM('click', M.step(3)); await caption('mon7');
    await after(6.3); await inM('click', M.step(4)); await caption('mon8');
    await after(6.5); await inM('frame', M.table); await caption('mon9');
    await after(6.5); await caption(null);

    // What the demo showed for each objective
    await after(0.4); await stage('card', SUMMARY); await stage('cardIn');
    await after(1.3); await stage('reveal', 'ey', 'l1'); speak('sum0');
    await after(2.2); await stage('reveal', 'o1'); speak('sum1');
    await after(3.2); await stage('reveal', 'o2'); speak('sum2');
    await after(3.2); await stage('reveal', 'o3'); speak('sum3');
    await after(8.0); await stage('fadeCardText');

    // Call to action
    await after(1.2); await stage('card', CLOSING);
    await after(0.3); await stage('reveal', 'l1'); speak('end1');
    await after(3.6); await stage('reveal', 'l2'); speak('end2');
    await after(3.8); await stage('reveal', 'fine');
    await after(7.5);
  },
}).catch((err) => { console.error(err); process.exit(1); });
