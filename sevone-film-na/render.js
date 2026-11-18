// Frame-accurate renderer: seeks the film to each frame time, screenshots it and pipes
// the frames into ffmpeg. Runs several workers in parallel, then joins the parts and
// muxes the soundtrack.
//
//   node render.js [fps=30] [workers=3] [out=sevone-agentic-observability-na.mp4]
//   CC=1 node render.js 30 3 sevone-agentic-observability-na-captioned.mp4   (burns subtitles in)
// Without CC=1, subtitles.srt is added as a selectable subtitle track instead.
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('node:child_process');
const path = require('node:path');
const fs = require('node:fs');

const FPS = +(process.argv[2] || 30);
const WORKERS = +(process.argv[3] || 3);
const OUT = process.argv[4] || 'sevone-agentic-observability-na.mp4';
const CC = process.env.CC === '1';
const DURATION = 166;
const TOTAL = Math.round(DURATION * FPS);
const tmp = fs.mkdtempSync(path.join(require('node:os').tmpdir(), 'sevone-'));

async function worker(id, from, to) {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('pageerror', e => console.error(`[w${id}] page error:`, e.message));
  await page.goto('file://' + path.resolve(__dirname, 'film.html') + '?render=1' + (CC ? '&cc=1' : ''));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  const part = path.join(tmp, `part${id}.mp4`);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(FPS), part], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = from; f < to; f++) {
    await page.evaluate(t => window.__seek(t), f / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - from) % 150 === 0) console.log(`[w${id}] frame ${f - from}/${to - from} · ${((Date.now() - t0) / 1000).toFixed(0)} s`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  return part;
}

(async () => {
  const per = Math.ceil(TOTAL / WORKERS);
  const parts = await Promise.all([...Array(WORKERS)].map((_, i) => worker(i, i * per, Math.min(TOTAL, (i + 1) * per))));
  const list = path.join(tmp, 'list.txt');
  fs.writeFileSync(list, parts.map(p => `file '${p}'`).join('\n'));
  const srt = path.resolve(__dirname, 'subtitles.srt');
  const softSubs = !CC && fs.existsSync(srt);
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-i', path.resolve(__dirname, 'soundtrack.wav'),
    ...(softSubs ? ['-i', srt] : []),
    '-map', '0:v', '-map', '1:a', ...(softSubs ? ['-map', '2:s', '-c:s', 'mov_text', '-metadata:s:s:0', 'language=eng', '-metadata:s:s:0', 'title=English'] : []),
    '-c:v', 'copy', '-af', 'loudnorm=I=-14:TP=-1.0', '-c:a', 'aac', '-b:a', '256k', '-metadata:s:a:0', 'language=eng', '-movflags', '+faststart', '-t', String(DURATION), OUT], { stdio: 'inherit' });
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log('wrote', OUT);
})();
