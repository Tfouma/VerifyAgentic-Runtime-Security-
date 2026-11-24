'use strict';
/*
 * Shared machinery for the demo films in this folder. A film runs demo pages
 * unmodified in iframes on a 1920x1080 stage, and adds film layers on top: title
 * cards, captions, a pointer, highlight rings, and a camera inside each page. With
 * FILM_VOICE set it narrates every line through narrate.py and paces the film so
 * each line finishes before the next beat. Frames come from Chromium's screencast
 * and are encoded to H.264 with ffmpeg.
 *
 * Environment: FILM_VOICE, KOKORO_MODEL, KOKORO_VOICES, FILM_PYTHON (narration),
 * FILM_SPEED (fast preview without narration). See narrate.py for the voice setup.
 */
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');
const { chromium } = require('playwright');

const DEMO = path.resolve(__dirname, '..');
const SPEED = Number(process.env.FILM_SPEED) || 1;
const NARRATE = Boolean(process.env.FILM_VOICE);
const PYTHON = process.env.FILM_PYTHON || 'python3';
const NARRATE_PY = path.join(__dirname, 'narrate.py');
const NARRATION_GAP = 0.6; // seconds of quiet between a spoken line and the next beat
const VIEWPORT = { width: 1920, height: 1080 };
const FPS = 30;

// The skeleton a published Artifact page gets, for pages that need standards mode.
const PAGE_HEAD = '<!doctype html><html><head><meta charset="utf-8">' +
  '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">' +
  '<style>:root{color-scheme:light}body{margin:0;font:14px system-ui}[hidden]{display:none!important}</style></head><body>';
const PAGE_TAIL = '</body></html>';

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
  #card .objs.six { gap: 22px; margin-top: 22px; }
  #card .objs.six .obj { padding: 24px 26px 26px; }
  #card .objs.six .oi { width: 50px; height: 50px; margin-bottom: 14px; }
  #card .objs.six .ot { font-size: 28px; margin-bottom: 10px; }
  #card .objs.six .od { font-size: 20px; }

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
// page timers (a fake clock would freeze them).
function installStage() {
  const SHIELD = '<path d="M12 3l7.5 3v5.5c0 4.6-3.1 8.3-7.5 9.5-4.4-1.2-7.5-4.9-7.5-9.5V6z"/>';
  const ICONS = {
    eye: '<path d="M2.5 12s3.5-6.5 9.5-6.5 9.5 6.5 9.5 6.5-3.5 6.5-9.5 6.5S2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>',
    userCheck: '<circle cx="10" cy="8" r="4"/><path d="M2.5 21c.9-4 3.8-6.5 7.5-6.5 1.4 0 2.7.4 3.8 1M15.5 18.5l2.2 2.2 4.3-4.5"/>',
    power: '<path d="M12 3v8.5"/><path d="M6.4 6.6a8 8 0 1 0 11.2 0"/>',
    idcard: '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2.2"/><path d="M5.8 16c.5-1.6 1.7-2.5 3.2-2.5s2.7.9 3.2 2.5M14 10h4M14 13.5h3"/>',
    clipboard: '<rect x="5" y="4.5" width="14" height="17" rx="2"/><path d="M9 4.5V3h6v1.5M8.5 10h7M8.5 14h7M8.5 18h4"/>',
    activity: '<path d="M3 12h4l3-8 4 16 3-8h4"/>',
    signal: '<path d="M4.9 15a8 8 0 0 1 0-8M19.1 7a8 8 0 0 1 0 8M8 12.8a3.8 3.8 0 0 1 0-3.6M16 9.2a3.8 3.8 0 0 1 0 3.6"/><circle cx="12" cy="11" r="1.6"/><path d="M12 13v8"/>',
    lock: '<rect x="4.5" y="10.5" width="15" height="10.5" rx="2"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/>',
    shieldCheck: SHIELD + '<path d="M8.8 12.2l2.2 2.2 4.4-4.6"/>',
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
    // Shows one of the filmed pages and fades the others out.
    show(id, instant) {
      const frames = [...document.querySelectorAll('iframe')];
      const apply = () => frames.forEach((f) => f.classList.toggle('off', f.id !== id));
      if (!instant) return apply();
      const saved = frames.map((f) => f.style.transition);
      frames.forEach((f) => { f.style.transition = 'none'; });
      apply();
      void document.body.offsetWidth;
      frames.forEach((f, i) => { f.style.transition = saved[i]; });
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
    tap(sel) { document.querySelector(sel).classList.add('film-press'); },
    release(sel) { document.querySelector(sel).classList.remove('film-press'); },
    click(sel) { document.querySelector(sel).click(); },
  };
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

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

// The helpers a film's setup and play steps use.
function makeDirector(page, frames, { lines, tagFor, durations, cues, sinceFirstFrame }) {
  let t0 = 0, T = 0, speechEnd = -Infinity;
  const now = () => ((Date.now() - t0) / 1000) * SPEED;
  const at = async (sec) => { const wait = t0 + (sec * 1000) / SPEED - Date.now(); if (wait > 0) await sleep(wait); };
  // Moves the schedule on, but never before the narrator has finished the current line.
  const after = (sec) => at((T = Math.max(T + sec, speechEnd + NARRATION_GAP)));
  const stage = (m, ...a) => page.evaluate(([m, a]) => window.stage[m](...a), [m, a]);
  // Calls window[ns][method] inside one of the filmed pages.
  const frame = (name, ns = 'film') => (m, ...a) => frames[name].evaluate(([ns, m, a]) => window[ns][m](...a), [ns, m, a]);

  // Starts a narrated line (when narrating) and notes where it falls in the film.
  const speak = (id) => {
    if (!(id in durations)) return;
    cues.push({ id, t: sinceFirstFrame() });
    speechEnd = now() + durations[id];
  };
  const caption = async (id) => {
    if (await stage('capHide')) await sleep(420 / SPEED);
    if (!id) return;
    const line = lines[id];
    await stage('cap', line.text, line.tag ? tagFor(line.tag) : null);
    speak(id);
  };
  const ring = async (call, sels, pad = 8) => stage('ring', await call('rect', sels), pad);
  // Moves the pointer onto a control and presses it the way a presenter would. With
  // tap, the button only looks pressed and the film triggers the action itself.
  const press = async (call, sel, { tap = false } = {}) => {
    const r = await call('rect', sel);
    const x = r.left + r.width / 2, y = r.top + r.height / 2;
    await stage('cursorShow', Math.max(40, x - 320), Math.min(1000, y + 260));
    await sleep(80 / SPEED);
    await stage('cursorTo', x, y);
    await sleep(1250 / SPEED);
    await stage('ripple');
    await call(tap ? 'tap' : 'press', sel);
    await sleep(220 / SPEED);
    await call('release', sel);
  };
  const step = (ms) => page.clock.runFor(ms); // with fakeClock: releases the page's next timer

  return {
    start() { t0 = Date.now(); },
    api: { after, at, stage, frame, frames, speak, caption, ring, press, step, sleep: (ms) => sleep(ms / SPEED) },
  };
}

/*
 * Records one film.
 *   out       output .mp4
 *   pages     [{ id, file, hidden, wrap, hash }] demo pages to load, in stage order.
 *             wrap gives a page the published Artifact skeleton (standards mode);
 *             hash opens it at #hash (for example #fr for the French page).
 *   lines     { id: { text, say, tag } } captions and narration
 *   tagFor    turns a line's tag into { icon, text } for the caption's tag row
 *   fakeClock install Playwright's fake clock so step(ms) releases page timers
 *   setup     async (api) => {}: frames the opening shot and sets the first card
 *   play      async (api) => {}: the film itself
 */
async function record({ out, pages, lines = {}, tagFor = () => null, fakeClock = false, setup, play }) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'film-'));
  const iframes = pages.map((pg) => {
    let src = path.join(DEMO, pg.file);
    if (pg.wrap) {
      const wrapped = path.join(dir, `${pg.id}.html`);
      fs.writeFileSync(wrapped, PAGE_HEAD + fs.readFileSync(src, 'utf8') + PAGE_TAIL);
      src = wrapped;
    }
    return `<iframe id="${pg.id}"${pg.hidden ? ' class="off"' : ''} src="file://${src}${pg.hash ? '#' + pg.hash : ''}"></iframe>`;
  }).join('\n');
  const stageFile = path.join(dir, 'stage.html');
  fs.writeFileSync(stageFile, `<!doctype html><html><head><meta charset="utf-8">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
    <style>${STAGE_CSS}</style></head><body>
    ${iframes}
    <div id="ring"></div><div id="cursor"></div>
    <div id="cap"><div class="tag"></div><div class="txt"></div></div>
    <div id="card"></div><div id="tick"></div></body></html>`);

  let durations = {};
  if (NARRATE) {
    if (SPEED !== 1) throw new Error('FILM_SPEED previews cannot be narrated');
    const linesFile = path.join(dir, 'lines.json');
    fs.writeFileSync(linesFile, JSON.stringify(Object.fromEntries(
      Object.entries(lines).map(([id, line]) => [id, line.say || line.text])), null, 1));
    console.log(`Narrating ${Object.keys(lines).length} lines with voice ${process.env.FILM_VOICE}`);
    execFileSync(PYTHON, ['-I', NARRATE_PY, 'synth', linesFile, dir], { stdio: 'inherit' });
    durations = JSON.parse(fs.readFileSync(path.join(dir, 'durations.json'), 'utf8'));
  }

  const browser = await chromium.launch();
  try {
    const context = await browser.newContext({ viewport: VIEWPORT, deviceScaleFactor: 1 });
    const page = await context.newPage();
    if (fakeClock) await page.clock.install({ time: new Date('2026-01-05T09:00:00Z') });
    await page.goto('file://' + stageFile);
    await page.waitForLoadState('load');
    const frames = {};
    for (const pg of pages) frames[pg.id] = await (await page.$(`#${pg.id}`)).contentFrame();
    const fonts = () => Promise.all(['400', '500', '600'].map((w) => document.fonts.load(`${w} 20px "IBM Plex Sans"`))
      .concat(['400', '500', '600'].map((w) => document.fonts.load(`${w} 12px "IBM Plex Mono"`)))).then(() => document.fonts.ready);
    for (const f of [page.mainFrame(), ...Object.values(frames)]) await f.evaluate(fonts);
    await page.evaluate(installStage);
    for (const f of Object.values(frames)) await f.evaluate(installCamera);

    const shots = [];
    const cues = [];
    const sinceFirstFrame = () => (Date.now() - shots[0].t) / 1000;
    const director = makeDirector(page, frames, { lines, tagFor, durations, cues, sinceFirstFrame });
    if (setup) await setup(director.api);
    if (fakeClock) await page.clock.pauseAt(new Date('2026-01-05T10:00:00Z')); // page timers now advance only on cue

    let firstShot;
    const gotFirst = new Promise((resolve) => { firstShot = resolve; });
    const cdp = await context.newCDPSession(page);
    cdp.on('Page.screencastFrame', ({ data, sessionId }) => {
      const file = path.join(dir, `f${String(shots.length).padStart(6, '0')}.jpg`);
      fs.writeFileSync(file, Buffer.from(data, 'base64'));
      shots.push({ file, t: Date.now() });
      if (shots.length === 1) firstShot();
      cdp.send('Page.screencastFrameAck', { sessionId }).catch(() => {});
    });
    await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 95, maxWidth: 1920, maxHeight: 1080 });
    await page.evaluate(() => window.stage.nudge()); // forces a first frame of the opening card
    await gotFirst;

    director.start();
    await play(director.api);
    const end = Date.now();
    await cdp.send('Page.stopScreencast');
    await browser.close();

    const video = NARRATE ? path.join(dir, 'silent.mp4') : out;
    encode(shots, end, dir, video);
    if (NARRATE) {
      const cuesFile = path.join(dir, 'cues.json');
      const track = path.join(dir, 'narration.wav');
      fs.writeFileSync(cuesFile, JSON.stringify(cues));
      execFileSync(PYTHON, ['-I', NARRATE_PY, 'mix', cuesFile, dir, String((end - shots[0].t) / 1000), track], { stdio: 'inherit' });
      execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', video, '-i', track, '-map', '0:v', '-map', '1:a',
        '-c:v', 'copy', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '160k',
        '-shortest', '-movflags', '+faststart', out], { stdio: 'inherit' });
    }
    console.log(`Wrote ${out} from ${shots.length} captured frames${NARRATE ? `, with ${cues.length} narrated lines` : ''}`);
  } finally {
    await browser.close().catch(() => {});
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

module.exports = { record };
