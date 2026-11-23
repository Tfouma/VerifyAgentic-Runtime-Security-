#!/usr/bin/env node
/*
 * Records "The Agent That Went Rogue", the demo film for the workshop plan
 * (docs/WORKSHOP_PLAN.md, section 3A). It films the Breach Console
 * (demo/dashboard.html) and the Lateral Movement Map (demo/attack_map.html).
 *
 * Both pages run unmodified inside a 1920x1080 stage. The script only adds film
 * layers: title cards, captions, a pointer, highlight rings, and a camera that
 * zooms into each page. Playwright's fake clock holds each attack step on screen
 * while its caption plays.
 *
 * Captions tag scenes with three objectives for AI agent governance: visibility
 * and inventory, governance and accountability, lifecycle and controls. Set
 * FILM_CLIENT to prefix those tags with a client name for a client-specific cut.
 *
 * Set FILM_VOICE (for example af_heart) to add a narrated sound track. Each line
 * in LINES is spoken by the open-weight Kokoro model through narrate.py, locally,
 * and the film waits for the narrator before moving on. See narrate.py for setup.
 *
 * Needs Node 18+, Playwright with Chromium, and ffmpeg built with libx264.
 *   node demo/film/record_film.js [output.mp4]
 *   FILM_CLIENT=ACME node demo/film/record_film.js acme-cut.mp4
 *   FILM_VOICE=af_heart KOKORO_MODEL=... KOKORO_VOICES=... node demo/film/record_film.js
 * FILM_PYTHON names the Python that has kokoro-onnx installed (default python3).
 * FILM_SPEED=6 renders a fast, rough preview without narration.
 */
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');
const { chromium } = require('playwright');

const DEMO = path.resolve(__dirname, '..');
const OUT = path.resolve(process.argv[2] || path.join(__dirname, 'the-agent-that-went-rogue.mp4'));
const CLIENT = (process.env.FILM_CLIENT || '').trim();
const SPEED = Number(process.env.FILM_SPEED) || 1;
const VIEWPORT = { width: 1920, height: 1080 };
const FPS = 30;
const NARRATE = Boolean(process.env.FILM_VOICE);
const PYTHON = process.env.FILM_PYTHON || 'python3';
const NARRATE_PY = path.join(__dirname, 'narrate.py');
const NARRATION_GAP = 0.6; // seconds of quiet between a spoken line and the next beat

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

const STAGE_CSS = `
  html, body { margin: 0; height: 100%; overflow: hidden; background: #0a0e1a; }
  :root { --sans: "IBM Plex Sans", system-ui, sans-serif; --mono: "IBM Plex Mono", ui-monospace, monospace; }
  iframe { position: fixed; inset: 0; width: 100%; height: 100%; border: 0; transition: opacity 1s ease; }
  iframe.off { opacity: 0; }
  .ic { width: 1.1em; height: 1.1em; flex: none; fill: none; stroke: currentColor; stroke-width: 2;
        stroke-linecap: round; stroke-linejoin: round; }

  #card { position: fixed; inset: 0; z-index: 100; background: #04060c; display: flex; flex-direction: column;
          align-items: center; justify-content: center; gap: 24px; padding: 0 150px; text-align: center;
          transition: opacity 1.1s ease; }
  #card.hide { opacity: 0; }
  #card [data-k] { opacity: 0; transform: translateY(12px); transition: opacity 1s ease, transform 1s ease; }
  #card [data-k].show { opacity: 1; transform: none; }
  #card .ey { font-family: var(--mono); font-size: 18px; letter-spacing: .24em; text-transform: uppercase; color: #6b7896; }
  #card .l { font-family: var(--sans); font-weight: 500; font-size: 60px; line-height: 1.22; letter-spacing: -0.01em;
             color: #eef2fb; max-width: 1500px; }
  #card .l.alert { color: #ff5468; }
  #card .l.mid { font-size: 48px; }
  #card .fine { font-family: var(--sans); font-size: 20px; line-height: 1.6; color: #7d8aa8; max-width: 1200px; margin-top: 30px; }
  #card .objs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; margin-top: 30px; max-width: 1580px; text-align: left; }
  #card .obj { background: #0d1322; border: 1px solid #22304d; border-radius: 18px; padding: 30px 30px 34px; }
  #card .oi { width: 58px; height: 58px; border-radius: 15px; display: grid; place-items: center;
              background: rgba(79, 140, 255, .14); color: #7fa8ff; margin-bottom: 20px; }
  #card .oi .ic { width: 30px; height: 30px; }
  #card .on { font-family: var(--mono); font-size: 16px; letter-spacing: .14em; text-transform: uppercase; color: #8db4ff; margin-bottom: 10px; }
  #card .ot { font-family: var(--sans); font-size: 31px; font-weight: 600; color: #eef2fb; margin-bottom: 14px; }
  #card .od { font-family: var(--sans); font-size: 22px; line-height: 1.5; color: #aab6d0; }

  #cap { position: fixed; left: 50%; bottom: 34px; z-index: 90; width: max-content; max-width: 1440px;
         padding: 16px 30px 18px; border-radius: 16px; background: rgba(4, 6, 12, .93);
         border: 1px solid rgba(120, 150, 210, .22); box-shadow: 0 20px 44px -18px rgba(0, 0, 0, .9); text-align: center;
         opacity: 0; transform: translate(-50%, 10px); transition: opacity .4s ease, transform .4s ease; }
  #cap.show { opacity: 1; transform: translate(-50%, 0); }
  #cap .tag { display: none; align-items: center; justify-content: center; gap: 9px; margin-bottom: 8px;
              font-family: var(--mono); font-size: 16px; letter-spacing: .12em; text-transform: uppercase; color: #8db4ff; }
  #cap .tag.on { display: flex; }
  #cap .tag .ic { width: 20px; height: 20px; }
  #cap .txt { font-family: var(--sans); font-weight: 500; font-size: 33px; line-height: 1.35; color: #f3f6fd; }

  #ring { position: fixed; z-index: 80; border-radius: 14px; pointer-events: none; opacity: 0;
          box-shadow: 0 0 0 4000px rgba(2, 4, 9, .3), 0 0 0 3px rgba(79, 140, 255, .95), 0 0 36px 4px rgba(79, 140, 255, .4);
          transition: opacity .6s ease, top .8s cubic-bezier(.4,0,.2,1), left .8s cubic-bezier(.4,0,.2,1),
                      width .8s cubic-bezier(.4,0,.2,1), height .8s cubic-bezier(.4,0,.2,1); }
  #ring.show { opacity: 1; }
  #cursor { position: fixed; left: 0; top: 0; z-index: 95; width: 36px; height: 36px; pointer-events: none; opacity: 0;
            filter: drop-shadow(0 3px 6px rgba(0, 0, 0, .6)); transition: transform 1.1s cubic-bezier(.45,0,.2,1), opacity .4s ease; }
  #cursor.show { opacity: 1; }
  .ripple { position: fixed; z-index: 94; width: 22px; height: 22px; margin: -11px 0 0 -11px; border-radius: 50%;
            border: 2px solid rgba(255, 255, 255, .9); pointer-events: none; animation: ripple .6s ease-out forwards; }
  @keyframes ripple { from { transform: scale(.4); opacity: 1; } to { transform: scale(3.2); opacity: 0; } }
  #tick { position: fixed; right: 0; bottom: 0; width: 1px; height: 1px; z-index: 101; background: #04060c; }
`;

// Runs in the stage page. Everything is driven from Node, so nothing here uses
// page timers (the fake clock would freeze them).
function installStage() {
  const ICONS = {
    eye: '<path d="M2.5 12s3.5-6.5 9.5-6.5 9.5 6.5 9.5 6.5-3.5 6.5-9.5 6.5S2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>',
    userCheck: '<circle cx="10" cy="8" r="4"/><path d="M2.5 21c.9-4 3.8-6.5 7.5-6.5 1.4 0 2.7.4 3.8 1M15.5 18.5l2.2 2.2 4.3-4.5"/>',
    power: '<path d="M12 3v8.5"/><path d="M6.4 6.6a8 8 0 1 0 11.2 0"/>',
  };
  const ic = (n) => `<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">${ICONS[n]}</svg>`;
  const $ = (id) => document.getElementById(id);
  const CURSOR_TIP = [4.5, 3];
  let tip = [0, 0];
  const jump = (el, apply) => { const t = el.style.transition; el.style.transition = 'none'; apply(); void el.offsetWidth; el.style.transition = t; };
  const moveCursor = (x, y) => { tip = [x, y]; $('cursor').style.transform = `translate(${x - CURSOR_TIP[0]}px, ${y - CURSOR_TIP[1]}px)`; };
  $('cursor').innerHTML = '<svg viewBox="0 0 24 24" width="36" height="36"><path d="M3 2 L3 19 L7.6 14.9 L10.6 21.6 ' +
    'L13.6 20.3 L10.7 13.7 L17 13.4 Z" fill="#fff" stroke="#0a0e1a" stroke-width="1.4" stroke-linejoin="round"/></svg>';

  window.stage = {
    nudge() { $('tick').style.background = $('tick').style.background === 'rgb(5, 7, 13)' ? '#04060c' : '#05070d'; },
    show(page, instant) {
      const apply = () => { $('console').classList.toggle('off', page !== 'console'); $('map').classList.toggle('off', page !== 'map'); };
      if (instant) { jump($('console'), () => jump($('map'), apply)); } else apply();
    },
    card(html) {
      $('card').innerHTML = html;
      $('card').querySelectorAll('i[data-ic]').forEach((el) => { el.outerHTML = ic(el.dataset.ic); });
    },
    reveal(...keys) { keys.forEach((k) => $('card').querySelector(`[data-k="${k}"]`).classList.add('show')); },
    fadeCardText() { $('card').querySelectorAll('[data-k]').forEach((el) => el.classList.remove('show')); },
    cardIn() { $('card').classList.remove('hide'); },
    cardOut() { $('card').classList.add('hide'); },
    cap(text, tag) {
      const t = $('cap').querySelector('.tag');
      t.innerHTML = tag ? ic(tag.icon) + `<span>${tag.text}</span>` : '';
      t.classList.toggle('on', !!tag);
      $('cap').querySelector('.txt').textContent = text;
      $('cap').classList.add('show');
    },
    capHide() { const was = $('cap').classList.contains('show'); $('cap').classList.remove('show'); return was; },
    ring(r, pad) {
      const ring = $('ring');
      const place = () => Object.assign(ring.style, { left: r.left - pad + 'px', top: r.top - pad + 'px', width: r.width + 2 * pad + 'px', height: r.height + 2 * pad + 'px' });
      if (ring.classList.contains('show')) place(); else { jump(ring, place); ring.classList.add('show'); }
    },
    unring() { $('ring').classList.remove('show'); },
    cursorShow(x, y) { jump($('cursor'), () => moveCursor(x, y)); $('cursor').classList.add('show'); },
    cursorTo(x, y) { moveCursor(x, y); },
    cursorHide() { $('cursor').classList.remove('show'); },
    ripple() {
      const r = document.createElement('div');
      r.className = 'ripple'; r.style.left = tip[0] + 'px'; r.style.top = tip[1] + 'px';
      r.addEventListener('animationend', () => r.remove());
      document.body.appendChild(r);
    },
  };
}

// Runs inside each filmed page: hides scrollbars, freezes scrolling, and adds a
// camera that frames any set of elements by scaling and moving the page's .wrap.
function installCamera() {
  const st = document.createElement('style');
  st.textContent = `html, body { overflow: hidden !important; } ::-webkit-scrollbar { display: none; }
    .wrap { transform-origin: 0 0; transition: transform 1.4s cubic-bezier(.45,0,.2,1); }
    .film-press { transform: scale(.94); filter: brightness(1.15); }`;
  document.head.appendChild(st);
  Element.prototype.scrollIntoView = function () {}; // the camera decides what is in view
  const wrap = document.querySelector('.wrap');
  let cur = { x: 0, y: 0, s: 1 };
  const set = (t, instant) => {
    if (instant) wrap.style.transition = 'none';
    wrap.style.transform = `translate(${t.x}px, ${t.y}px) scale(${t.s})`;
    if (instant) { void wrap.offsetWidth; wrap.style.transition = ''; }
    cur = t;
  };
  // Where an element would sit with no camera transform applied.
  const untransformed = (r) => {
    const ox = wrap.offsetLeft, oy = wrap.offsetTop;
    const f = (v, o, c) => o + (v - o - c) / cur.s;
    return { l: f(r.left, ox, cur.x), t: f(r.top, oy, cur.y), r: f(r.right, ox, cur.x), b: f(r.bottom, oy, cur.y) };
  };
  window.film = {
    frame(sels, { maxScale = 1.9, fill = 0.92, safeH = 870, instant = false, minH = 0 } = {}) {
      const boxes = [].concat(sels).map((s) => untransformed(document.querySelector(s).getBoundingClientRect()));
      const l = Math.min(...boxes.map((b) => b.l)), t = Math.min(...boxes.map((b) => b.t));
      const r = Math.max(...boxes.map((b) => b.r));
      const b = Math.max(t + minH, ...boxes.map((b) => b.b)); // minH reserves room for content still to come
      const s = Math.min(maxScale, (innerWidth * fill) / (r - l), (safeH * fill) / (b - t));
      const ox = wrap.offsetLeft, oy = wrap.offsetTop;
      set({ x: innerWidth / 2 - ox - s * ((l + r) / 2 - ox), y: safeH / 2 - oy - s * ((t + b) / 2 - oy), s }, instant);
    },
    rect(sels) {
      const rs = [].concat(sels).map((s) => document.querySelector(s).getBoundingClientRect());
      const left = Math.min(...rs.map((r) => r.left)), top = Math.min(...rs.map((r) => r.top));
      return { left, top, width: Math.max(...rs.map((r) => r.right)) - left, height: Math.max(...rs.map((r) => r.bottom)) - top };
    },
    press(sel) { const el = document.querySelector(sel); el.classList.add('film-press'); el.click(); },
    release(sel) { document.querySelector(sel).classList.remove('film-press'); },
    click(sel) { document.querySelector(sel).click(); },
  };
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

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

function director(page, con, map, { durations = {}, cues = [], sinceFirstFrame = () => 0 } = {}) {
  let t0 = 0, T = 0, speechEnd = -Infinity;
  const now = () => ((Date.now() - t0) / 1000) * SPEED;
  const at = async (sec) => { const wait = t0 + (sec * 1000) / SPEED - Date.now(); if (wait > 0) await sleep(wait); };
  // Moves the schedule on, but never before the narrator has finished the current line.
  const after = (sec) => at((T = Math.max(T + sec, speechEnd + NARRATION_GAP)));
  const stage = (m, ...a) => page.evaluate(([m, a]) => window.stage[m](...a), [m, a]);
  const inFrame = (frame) => (m, ...a) => frame.evaluate(([m, a]) => window.film[m](...a), [m, a]);
  const inC = inFrame(con), inM = inFrame(map);

  // Starts a narrated line (when narrating) and notes where it falls in the film.
  const speak = (id) => {
    if (!(id in durations)) return;
    cues.push({ id, t: sinceFirstFrame() });
    speechEnd = now() + durations[id];
  };
  const caption = async (id) => {
    if (await stage('capHide')) await sleep(420 / SPEED);
    if (!id) return;
    const line = LINES[id];
    await stage('cap', line.text, line.tag ? tagFor(line.tag) : null);
    speak(id);
  };
  const ring = async (call, sels, pad = 8) => stage('ring', await call('rect', sels), pad);
  // Moves the pointer onto a control and clicks it the way a presenter would.
  const press = async (call, sel) => {
    const r = await call('rect', sel);
    const x = r.left + r.width / 2, y = r.top + r.height / 2;
    await stage('cursorShow', Math.max(40, x - 320), Math.min(1000, y + 260));
    await sleep(80 / SPEED);
    await stage('cursorTo', x, y);
    await sleep(1250 / SPEED);
    await stage('ripple');
    await call('press', sel);
    await sleep(220 / SPEED);
    await call('release', sel);
  };
  const step = (ms) => page.clock.runFor(ms); // releases the console's next scripted step

  return {
    start() { t0 = Date.now(); },
    async play() {
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
  };
}

function encode(frames, endMs, dir, out) {
  // Screencast frames arrive only when the screen changes, so each frame is held
  // until the next one; ffmpeg then resamples to a constant frame rate.
  const keep = frames.filter((f, i) => i === frames.length - 1 || frames[i + 1].t > f.t);
  const lines = ['ffconcat version 1.0'];
  keep.forEach((f, i) => {
    const next = i + 1 < keep.length ? keep[i + 1].t : endMs;
    lines.push(`file '${path.basename(f.file)}'`, `duration ${((next - f.t) / 1000).toFixed(4)}`);
  });
  lines.push(`file '${path.basename(keep[keep.length - 1].file)}'`); // concat demuxer needs the last file twice
  const list = path.join(dir, 'frames.ffconcat');
  fs.writeFileSync(list, lines.join('\n') + '\n');
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list,
    '-vf', `fps=${FPS},scale=1920:1080:flags=lanczos,format=yuv420p`,
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-movflags', '+faststart', out], { stdio: 'inherit' });
}

(async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'rogue-film-'));
  const stageFile = path.join(dir, 'stage.html');
  fs.writeFileSync(stageFile, `<!doctype html><html><head><meta charset="utf-8">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
    <style>${STAGE_CSS}</style></head><body>
    <iframe id="console" src="file://${path.join(DEMO, 'dashboard.html')}"></iframe>
    <iframe id="map" class="off" src="file://${path.join(DEMO, 'attack_map.html')}"></iframe>
    <div id="ring"></div><div id="cursor"></div>
    <div id="cap"><div class="tag"></div><div class="txt"></div></div>
    <div id="card"></div><div id="tick"></div></body></html>`);

  let durations = {};
  if (NARRATE) {
    if (SPEED !== 1) throw new Error('FILM_SPEED previews cannot be narrated');
    const linesFile = path.join(dir, 'lines.json');
    fs.writeFileSync(linesFile, JSON.stringify(Object.fromEntries(
      Object.entries(LINES).map(([id, line]) => [id, line.say || line.text])), null, 1));
    console.log(`Narrating ${Object.keys(LINES).length} lines with voice ${process.env.FILM_VOICE}`);
    execFileSync(PYTHON, ['-I', NARRATE_PY, 'synth', linesFile, dir], { stdio: 'inherit' });
    durations = JSON.parse(fs.readFileSync(path.join(dir, 'durations.json'), 'utf8'));
  }

  const browser = await chromium.launch();
  try {
    const context = await browser.newContext({ viewport: VIEWPORT, deviceScaleFactor: 1 });
    const page = await context.newPage();
    await page.clock.install({ time: new Date('2026-01-05T09:00:00Z') });
    await page.goto('file://' + stageFile);
    await page.waitForLoadState('load');
    const con = page.frames().find((f) => f.url().endsWith('/dashboard.html'));
    const map = page.frames().find((f) => f.url().endsWith('/attack_map.html'));
    const fonts = () => Promise.all(['400', '500', '600'].map((w) => document.fonts.load(`${w} 20px "IBM Plex Sans"`))
      .concat(['400', '500', '600'].map((w) => document.fonts.load(`${w} 12px "IBM Plex Mono"`)))).then(() => document.fonts.ready);
    for (const frame of [page.mainFrame(), con, map]) await frame.evaluate(fonts);
    await page.evaluate(installStage);
    await con.evaluate(installCamera);
    await map.evaluate(installCamera);
    await con.evaluate((sels) => window.film.frame(sels, { safeH: 1080, fill: 0.96, instant: true }), C.all);
    await map.evaluate((sel) => window.film.frame(sel, { instant: true }), M.diagram);
    await page.evaluate((html) => window.stage.card(html), OPENING);
    await page.clock.pauseAt(new Date('2026-01-05T10:00:00Z')); // from here, console steps advance only on cue

    const frames = [];
    let firstFrame;
    const gotFirst = new Promise((resolve) => { firstFrame = resolve; });
    const cdp = await context.newCDPSession(page);
    cdp.on('Page.screencastFrame', ({ data, sessionId }) => {
      const file = path.join(dir, `f${String(frames.length).padStart(6, '0')}.jpg`);
      fs.writeFileSync(file, Buffer.from(data, 'base64'));
      frames.push({ file, t: Date.now() });
      if (frames.length === 1) firstFrame();
      cdp.send('Page.screencastFrameAck', { sessionId }).catch(() => {});
    });
    await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 95, maxWidth: 1920, maxHeight: 1080 });
    await page.evaluate(() => window.stage.nudge()); // forces a first frame of the black card
    await gotFirst;

    const cues = [];
    const sinceFirstFrame = () => (Date.now() - frames[0].t) / 1000;
    const film = director(page, con, map, { durations, cues, sinceFirstFrame });
    film.start();
    await film.play();
    const end = Date.now();
    await cdp.send('Page.stopScreencast');
    await browser.close();

    const video = NARRATE ? path.join(dir, 'silent.mp4') : OUT;
    encode(frames, end, dir, video);
    if (NARRATE) {
      const cuesFile = path.join(dir, 'cues.json');
      const track = path.join(dir, 'narration.wav');
      fs.writeFileSync(cuesFile, JSON.stringify(cues));
      execFileSync(PYTHON, ['-I', NARRATE_PY, 'mix', cuesFile, dir, String((end - frames[0].t) / 1000), track], { stdio: 'inherit' });
      execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', video, '-i', track, '-map', '0:v', '-map', '1:a',
        '-c:v', 'copy', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '160k',
        '-shortest', '-movflags', '+faststart', OUT], { stdio: 'inherit' });
    }
    console.log(`Wrote ${OUT} from ${frames.length} captured frames${NARRATE ? `, with ${cues.length} narrated lines` : ''}`);
  } finally {
    await browser.close().catch(() => {});
    fs.rmSync(dir, { recursive: true, force: true });
  }
})().catch((err) => { console.error(err); process.exit(1); });
