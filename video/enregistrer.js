// Records the demo video by driving the real live console (livedemo) in step-by-step mode.
//
//   node video/enregistrer.js            (after python3 video/generer_voix.py)
//
// Output: video/build/brut.webm (silent screen recording) and video/build/chronologie.json
// (when each narration clip starts). video/assembler.py then adds the voice-over.

const { chromium } = require("playwright");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const BUILD = path.join(__dirname, "build");
const PORT = 8766;
const BASE = `http://127.0.0.1:${PORT}`;
const W = 1920, H = 1080;
const manifest = JSON.parse(fs.readFileSync(path.join(BUILD, "voix", "manifeste.json"), "utf8"));

const sleep = ms => new Promise(r => setTimeout(r, ms));
const api = async (p, body) => (await fetch(BASE + p, body === undefined ? {} : {
  method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })).json();

const SLIDES = {
  titre: `<div class="ey">Démonstration · préparée pour Desjardins</div>
    <h2>Agent IA gouverné<br>en bac à sable</h2>
    <p>Identité des agents, délégation et contrôle à chaque action, pour une coopérative financière.</p>
    <div class="foot">IBM Verify · HashiCorp Vault · passerelle MCP · OPA · Microsoft Entra ID<br>Institution, personnes et données fictives</div>`,
  demande: `<div class="ey">La demande</div>
    <h2>Une tâche en quatre étapes,<br>sans aucun secret dans le bac à sable</h2>
    <ol><li>Lire le billet <b>FIN-2417</b> dans Jira</li><li>Récupérer le guide <b>KYC-RR-07</b> dans GitLab</li>
    <li>Déléguer la collecte des preuves à un <b>sous-agent en lecture seule</b></li>
    <li>Écrire la nouvelle cote dans Databricks, <b>avec approbation humaine</b></li></ol>`,
  recap: `<div class="ey">Ce que vous venez de voir</div>
    <h2>Chaque action de l'agent est prouvable</h2>
    <ol><li>Aucun secret dans le bac à sable</li><li>Un jeton délégué de 5 minutes par appel (RFC 8693 + RAR)</li>
    <li>Des sous-agents qui ne dépassent jamais leur parent</li><li>Une personne dans la boucle pour chaque écriture</li>
    <li>Suspension de l'agent et double révocation automatiques</li><li>Un journal complet pour l'audit</li></ol>`,
  suite: `<div class="ey">Prochaine étape proposée</div>
    <h2>Commencer petit, sur un flux réel</h2>
    <ol><li>Inventaire des agents et des identités non humaines</li>
    <li>Preuve de valeur de 4 à 6 semaines dans un environnement isolé</li>
    <li>Déploiement progressif des contrôles</li></ol>
    <div class="foot">Démonstration pédagogique · ce n'est pas un logiciel IBM · capacités des produits à confirmer avec IBM</div>`,
};

(async () => {
  const srv = spawn("python3", ["-m", "livedemo", "--port", String(PORT), "--rythme", "0.9", "--pas-a-pas"], { cwd: ROOT, stdio: "inherit" });
  await sleep(1500);
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, recordVideo: { dir: BUILD, size: { width: W, height: H } } });
  const t0 = Date.now();
  const page = await ctx.newPage();
  const timeline = [];

  const say = async seg => {
    for (const clip of manifest[seg]) {
      await page.evaluate(t => window.demo.caption(t), clip.texte);
      timeline.push({ seg, fichier: clip.fichier, texte: clip.texte, debut: (Date.now() - t0) / 1000, duree: clip.duree });
      await sleep(clip.duree * 1000 + 300);
    }
    await page.evaluate(() => window.demo.caption(""));
  };
  const slide = html => page.evaluate(h => window.demo.slide(h), html || "");
  const settle = async () => {             // until the agent parks, asks for approval, or finishes
    await sleep(400);
    for (let i = 0; i < 400; i++) {
      const s = await api("/api/state");
      if (s.en_attente || s.defi || !s.en_cours) break;
      await sleep(150);
    }
    await sleep(900);                      // let the console repaint
  };
  const step = async () => { await api("/api/etape", {}); await settle(); };
  const run = async name => { await page.click(`#scenarios .btn[data-key=${name}]`); await settle(); };
  const login = async () => { await page.click("#loginBtn"); await sleep(1400); };
  const reset = async () => { await page.click("#resetBtn"); await sleep(900); };
  const typeCode = async code => { await page.fill("#codeIn", ""); await page.type("#codeIn", code, { delay: 110 }); await sleep(300); await page.click("#approveBtn"); await sleep(1300); };

  await page.goto(BASE);
  await slide(SLIDES.titre); await sleep(1200);
  await say("intro");
  await slide(SLIDES.demande); await say("demande");
  await slide(null); await sleep(600);
  await say("console");
  await login(); await say("connexion");

  // 1. normal path
  await run("normal");
  await step(); await say("n_jira");
  await step(); await say("n_gitlab");
  await step(); await say("n_deleg");
  await step(); await say("n_scim");
  await step(); await say("n_query");
  await step(); await say("n_refus");
  await step();                            // subagent hands back, parent parks
  await step();                            // parent asks to write -> approval pending
  await say("n_stepup");
  await typeCode(await page.evaluate(() => window.demo.code()));
  await settle(); await say("n_approuve");
  await say("n_fin");

  // 2. poisoned runbook
  await say("p_intro");
  await reset(); await login();
  await run("poison");
  await step();                            // read ticket
  await step(); await say("p_cache");      // runbook with hidden instruction
  await step(); await say("p_refus1");
  await step(); await say("p_refus2");
  await step(); await say("p_susp");
  await step(); await say("p_fin");

  // 3. failed approvals
  await say("a_intro");
  await reset(); await login();
  await run("approbations");
  await step();
  await step();                            // write -> approval pending
  const codes = ["123123", "456456", "789789"];
  const clips = manifest.a_codes;
  await page.evaluate(t => window.demo.caption(t), clips[0].texte);
  timeline.push({ seg: "a_codes", fichier: clips[0].fichier, texte: clips[0].texte, debut: (Date.now() - t0) / 1000, duree: clips[0].duree });
  for (const c of codes) await typeCode(c);
  await page.evaluate(() => window.demo.caption(""));
  await sleep(800); await say("a_revoke");
  await step(); await say("a_fin");

  // 4. unregistered payment tool
  await say("o_intro");
  await reset(); await login();
  await run("outil");
  await step(); await say("o_liste");
  await step(); await say("o_fin");

  await slide(SLIDES.recap); await say("recap");
  await slide(SLIDES.suite); await say("suite"); await sleep(1500);

  const vpath = await page.video().path();
  await ctx.close(); await browser.close(); srv.kill();
  fs.renameSync(vpath, path.join(BUILD, "brut.webm"));
  fs.writeFileSync(path.join(BUILD, "chronologie.json"), JSON.stringify(timeline, null, 1));
  console.log(`Vidéo brute : ${((Date.now() - t0) / 60000).toFixed(1)} min, ${timeline.length} clips`);
})();
