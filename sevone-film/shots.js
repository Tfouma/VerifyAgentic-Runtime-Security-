// Quick still frames for review: node shots.mjs out_dir t1 t2 ...
const { chromium } = require('playwright');
const path = require('node:path');
(async () => {
const [out, ...ts] = process.argv.slice(2);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
p.on('pageerror', e => console.error('PAGEERR', e.message));
await p.goto('file://' + path.resolve('film.html') + '?render=1');
await p.evaluate(() => document.fonts.ready);
for (const t of ts) { await p.evaluate(t => window.__seek(t), +t); await p.screenshot({ path: `${out}/t${String(t).padStart(6,'0')}.png` }); }
await b.close();
})();
