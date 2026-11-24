#!/usr/bin/env node
/*
 * Records "Fraud Ring Live", a film of demo/fraud_ring.html: four attacker crews go
 * after a fictional bank and mobile operator with the runtime controls off, then
 * again with them on and the kill switch. It uses the shared stage in lib.js.
 *
 * The page runs unmodified. Instead of letting it play on its own clock, the film
 * fires the page's scripted moves one at a time, so each move stays on screen while
 * its line is read, and runs the page's clock between them.
 *
 * FILM_LANG=fr records the Canadian French version: the page opens at #fr, and the
 * captions, title cards and narration are in French. Use a French voice such as
 * ff_siwis for the narration.
 *
 *   node demo/film/record_fraud_ring.js [output.mp4]       captions only
 *   FILM_VOICE=af_heart FILM_PYTHON=... KOKORO_MODEL=... KOKORO_VOICES=... \
 *     node demo/film/record_fraud_ring.js                     with narration
 *   FILM_LANG=fr FILM_VOICE=ff_siwis ... node demo/film/record_fraud_ring.js
 * See record_film.js for the requirements and narrate.py for the voice setup.
 */
'use strict';
const path = require('path');
const { record } = require('./lib');

const LANG = (process.env.FILM_LANG || 'en').trim().toLowerCase() === 'fr' ? 'fr' : 'en';
const OUT = path.resolve(process.argv[2] || path.join(__dirname, LANG === 'fr' ? 'fraud-ring-live-fr.mp4' : 'fraud-ring-live.mp4'));

// Every line of the film. `text` is the on-screen caption and `say` is how the
// narrator reads it when the two differ. Lines without `text` go with title cards.
const LINES_EN = {
  open1: { say: 'Four attacker crews. One bank. One mobile operator.' },
  open2: { say: "Here's what they can take in under a minute." },
  intro1: { text: 'Lumora Bank and Teleqo Mobile are fictional. Both run AI agents for support, cards, payments and customer care.' },
  intro2: { text: 'Right now, nothing sits between those agents and the systems they can reach.' },
  crew1: { text: 'The SIM Swapper wants phone numbers, and the one-time codes they receive.' },
  crew2: { text: 'The Harvester wants personal data.' },
  crew3: { text: 'The Carder wants card numbers.' },
  crew4: { text: 'The Account Taker wants money.' },
  go: { text: 'Controls off. The attack starts.' },
  x1: { text: 'Hidden instructions: the support agent exports 12,400 customer profiles.',
        say: "Hidden instructions in a support message. The bank's agent exports twelve thousand four hundred customer profiles." },
  x2: { text: 'A poisoned plugin: the card agent reads 3,950 full card numbers.',
        say: 'A poisoned plugin. The card agent reads three thousand nine hundred and fifty full card numbers.' },
  x3: { text: "A fake customer: the operator's care agent moves a phone number to the crew's eSIM.",
        say: "A fake customer. The operator's care agent moves a phone number to the crew's e-SIM." },
  x4: { text: 'The export tool: 2,100 more profiles.', say: 'The export tool. Two thousand one hundred more profiles.' },
  x5: { text: "36 more numbers move to the crew's eSIMs.", say: "Thirty-six more numbers move to the crew's e-SIMs." },
  x6: { text: 'With the hijacked codes, 18 bank accounts are taken over.', say: 'With the hijacked codes, eighteen bank accounts are taken over.' },
  x7: { text: 'Card testing: 1,120 stolen cards still work.', say: 'Card testing. One thousand one hundred and twenty stolen cards still work.' },
  x8: { text: '$480,000 goes to six mule accounts.', say: 'Four hundred and eighty thousand dollars go to six mule accounts.' },
  x9: { text: 'An unregistered bot moves 12 more numbers.', say: 'An unregistered bot moves twelve more numbers.' },
  x10: { text: 'The card list leaves the bank by email.' },
  x11: { text: '$804,500 more leaves in 214 small transfers.',
         say: 'And more than eight hundred thousand dollars leaves in small transfers.' },
  offEnd1: { text: 'Under a minute: $1.28 million, 14,500 personal records, 3,950 cards and 49 phone numbers.',
             say: 'In under a minute: one point two eight million dollars, fourteen thousand five hundred personal records, three thousand nine hundred and fifty cards, and forty-nine phone numbers.' },
  offEnd2: { text: "Most of it went through the companies' own AI agents." },
  on0: { text: 'Same crews. Same moves. This time, the runtime controls are on.' },
  y1: { text: 'Policy: a bulk export is far beyond one support conversation. Blocked.' },
  y2: { text: 'Policy: the card agent may see only the last four digits. The plugin is disconnected.',
        say: 'Policy again. The card agent may see only the last four digits, and the plugin is disconnected.' },
  y3: { text: "Delegation: the line's owner never approved the move. Request held.",
        say: "Delegation. The line's owner never approved the move, so the request is held." },
  y3b: { text: 'Teleqo warns Lumora Bank that someone is trying to move these numbers.' },
  y4: { text: 'The support agent is already quarantined. Refused at the door.' },
  y5: { text: 'Behavior: 36 eSIM moves from one session is not normal. The care agent is quarantined.',
        say: 'Behavior. Thirty-six e-SIM moves from one session is not normal. The care agent is quarantined.' },
  y6: { text: "Acting on the operator's warning, the bank asks each customer to approve on their own device. Sign-ins denied." },
  kill: { text: 'Now the kill switch. It quarantines every agent the crews can reach.' },
  y7: { text: 'Card testing finds nothing to test. No card numbers were exposed.' },
  rest: { text: 'Every move after that is refused: quarantined agents, and a bot with no identity.' },
  onEnd: { text: '11 attacks blocked. 6 agents and tools quarantined. 2 risk signals shared. Nothing taken.',
           say: 'Eleven attacks blocked. Six agents and tools quarantined. Two risk signals shared. Nothing taken.' },
  checks: { say: 'Six checks did the work: identity, delegation, policy, behavior, response, and a warning shared between the two companies.' },
  end1: { say: 'Fraud crosses company lines.' },
  end2: { say: 'Your controls should too.' },
};

// Canadian French. Numbers are spelled out in `say` so the voice reads them cleanly.
const LINES_FR = {
  open1: { say: "Quatre équipes d'attaquants. Une banque. Un opérateur mobile." },
  open2: { say: "Voici ce qu'elles peuvent prendre en moins d'une minute." },
  intro1: { text: 'La Banque Lumora et Teleqo Mobile sont fictives. Toutes deux utilisent des agents IA pour le soutien, les cartes, les paiements et le service à la clientèle.' },
  intro2: { text: "Pour l'instant, rien ne se trouve entre ces agents et les systèmes qu'ils peuvent atteindre." },
  crew1: { text: "Le Pirate SIM veut des numéros de téléphone, et les codes à usage unique qu'ils reçoivent.",
           say: "Le pirate sim veut des numéros de téléphone, et les codes à usage unique qu'ils reçoivent." },
  crew2: { text: 'Le Moissonneur veut des données personnelles.' },
  crew3: { text: 'Le Voleur de cartes veut des numéros de carte.' },
  crew4: { text: "Le Vide-comptes veut de l'argent." },
  go: { text: "Sans contrôles. L'attaque commence." },
  x1: { text: "Instructions cachées : l'agent de soutien exporte 12 400 profils clients.",
        say: "Des instructions cachées dans un message au soutien. L'agent de la banque exporte douze mille quatre cents profils clients." },
  x2: { text: "Un module piégé : l'agent des cartes lit 3 950 numéros de carte complets.",
        say: "Un module piégé. L'agent des cartes lit trois mille neuf cent cinquante numéros de carte complets." },
  x3: { text: "Un faux client : l'agent de l'opérateur transfère un numéro vers l'eSIM de l'équipe.",
        say: "Un faux client. L'agent de l'opérateur transfère un numéro de téléphone vers la carte sim virtuelle de l'équipe." },
  x4: { text: "L'outil d'exportation : 2 100 autres profils.", say: "L'outil d'exportation. Deux mille cent autres profils." },
  x5: { text: "36 autres numéros passent sur les eSIM de l'équipe.", say: "Trente-six autres numéros passent sur les cartes sim virtuelles de l'équipe." },
  x6: { text: 'Avec les codes détournés, 18 comptes bancaires sont piratés.', say: 'Avec les codes détournés, dix-huit comptes bancaires sont piratés.' },
  x7: { text: 'Test de cartes : 1 120 cartes volées fonctionnent encore.', say: 'Test de cartes. Plus de mille cartes volées fonctionnent encore.' },
  x8: { text: '480 000 $ partent vers des comptes de complices.', say: 'Quatre cent quatre-vingt mille dollars partent vers des comptes de complices.' },
  x9: { text: 'Un robot non enregistré détourne encore 12 numéros.', say: 'Un robot non enregistré détourne encore douze numéros.' },
  x10: { text: 'La liste des cartes quitte la banque par courriel.' },
  x11: { text: '804 500 $ de plus partent en 214 petits virements.', say: 'Et plus de huit cent mille dollars partent en petits virements.' },
  offEnd1: { text: "En moins d'une minute : 1,28 million $, 14 500 profils clients, 3 950 cartes et 49 numéros de téléphone.",
             say: "En moins d'une minute : près d'un million trois cent mille dollars, quatorze mille cinq cents profils clients, trois mille neuf cent cinquante cartes, et quarante-neuf numéros de téléphone." },
  offEnd2: { text: 'Presque tout est passé par les propres agents IA des entreprises.' },
  on0: { text: "Mêmes équipes. Mêmes gestes. Cette fois, les contrôles d'exécution sont activés." },
  y1: { text: 'Politique : une exportation massive dépasse de loin une conversation de soutien. Bloquée.' },
  y2: { text: "Politique : l'agent des cartes ne voit que les quatre derniers chiffres. Le module est déconnecté.",
        say: "Politique, encore. L'agent des cartes ne voit que les quatre derniers chiffres, et le module est déconnecté." },
  y3: { text: "Délégation : le titulaire de la ligne n'a jamais approuvé le transfert. Demande retenue.",
        say: "Délégation. Le titulaire de la ligne n'a jamais approuvé le transfert, alors la demande est retenue." },
  y3b: { text: "Teleqo prévient la Banque Lumora que quelqu'un tente de transférer ces numéros." },
  y4: { text: "L'agent de soutien est déjà en quarantaine. Refusé à l'entrée." },
  y5: { text: "Comportement : 36 transferts d'eSIM dans une même session, ce n'est pas normal. L'agent est mis en quarantaine.",
        say: "Comportement. Trente-six transferts de cartes sim virtuelles dans une même session, ce n'est pas normal. L'agent est mis en quarantaine." },
  y6: { text: "Grâce à l'alerte de l'opérateur, la banque demande à chaque client d'approuver sur son propre appareil. Connexions refusées." },
  kill: { text: 'Maintenant, le coupe-circuit. Il met en quarantaine chaque agent que les équipes peuvent atteindre.' },
  y7: { text: "Le test de cartes ne trouve rien à tester. Aucun numéro de carte n'a été exposé." },
  rest: { text: 'Tout ce qui suit est refusé : des agents en quarantaine, et un robot sans identité.' },
  onEnd: { text: "11 attaques bloquées. 6 agents et outils en quarantaine. 2 signaux de risque partagés. Rien n'a été pris.",
           say: "Onze attaques bloquées. Six agents et outils en quarantaine. Deux signaux de risque partagés. Rien n'a été pris." },
  checks: { say: 'Six vérifications ont fait le travail : identité, délégation, politique, comportement, réponse, et une alerte partagée entre les deux entreprises.' },
  end1: { say: 'La fraude traverse les frontières entre entreprises.' },
  end2: { say: 'Vos contrôles doivent en faire autant.' },
};

const CHECKS_EN = [
  { icon: 'idcard', name: 'Identity', who: 'SIM Swapper', what: 'Turned away an unregistered bot with a leaked partner key.' },
  { icon: 'userCheck', name: 'Delegation', who: 'SIM Swapper', what: 'Held a number move that the line’s owner never approved.' },
  { icon: 'clipboard', name: 'Policy', who: 'Harvester · Carder', what: 'Refused a bulk export of customers and full card numbers.' },
  { icon: 'activity', name: 'Behavior', who: 'SIM Swapper · Carder', what: 'Caught 36 eSIM moves from one session, and card testing.' },
  { icon: 'power', name: 'Response', who: 'Every crew', what: 'Quarantined agents on the first violation. The kill switch cut off the rest.' },
  { icon: 'signal', name: 'Shared signal', who: 'Account Taker', what: 'Carried the operator’s SIM-change warning to the bank, which denied the sign-ins.' },
];
const CHECKS_FR = [
  { icon: 'idcard', name: 'Identité', who: 'Pirate SIM', what: 'A refusé un robot non enregistré muni d’une clé partenaire divulguée.' },
  { icon: 'userCheck', name: 'Délégation', who: 'Pirate SIM', what: 'A retenu un transfert de numéro que le titulaire n’avait jamais approuvé.' },
  { icon: 'clipboard', name: 'Politique', who: 'Moissonneur · Voleur de cartes', what: 'A refusé une exportation massive de clients et la lecture des numéros de carte complets.' },
  { icon: 'activity', name: 'Comportement', who: 'Pirate SIM · Voleur de cartes', what: 'A repéré 36 transferts d’eSIM dans une même session, et le test de cartes.' },
  { icon: 'power', name: 'Réponse', who: 'Toutes les équipes', what: 'A mis les agents en quarantaine dès la première infraction. Le coupe-circuit a isolé le reste.' },
  { icon: 'signal', name: 'Signal partagé', who: 'Vide-comptes', what: 'A transmis l’alerte de changement de SIM de l’opérateur à la banque, qui a refusé les connexions.' },
];

const checksCard = (eyebrow, title, list) => `
  <div class="ey" data-k="ey">${eyebrow}</div>
  <div class="l mid" data-k="l1">${title}</div>
  <div class="objs six">${list.map((c, i) => `
    <div class="obj" data-k="o${i + 1}"><div class="oi"><i data-ic="${c.icon}"></i></div>
      <div class="on">${c.who}</div><div class="ot">${c.name}</div><div class="od">${c.what}</div></div>`).join('')}
  </div>`;

const CARDS = {
  en: {
    opening: `
      <div class="ey" data-k="ey">A teaching simulation · fictional companies, customers and data</div>
      <div class="l" data-k="l1">Four attacker crews. One bank. One mobile operator.</div>
      <div class="l alert" data-k="l2">Here's what they can take in under a minute.</div>`,
    checks: checksCard('What stopped the crews', 'Six checks, on every call', CHECKS_EN),
    closing: `
      <div class="l" data-k="l1">Fraud crosses company lines.</div>
      <div class="l alert" data-k="l2">Your controls should too.</div>
      <div class="fine" data-k="fine">Teaching simulation. Lumora Bank, Teleqo Mobile and all data are fictional. It illustrates
        runtime identity controls for AI agents, the class of control delivered by IBM Verify Identity Protection with Agentic
        Runtime Security, plus a SIM-swap signal shared by the mobile operator. It is not IBM software.</div>`,
  },
  fr: {
    opening: `
      <div class="ey" data-k="ey">Une simulation pédagogique · entreprises, clients et données fictifs</div>
      <div class="l" data-k="l1">Quatre équipes d’attaquants. Une banque. Un opérateur mobile.</div>
      <div class="l alert" data-k="l2">Voici ce qu’elles peuvent prendre en moins d’une minute.</div>`,
    checks: checksCard('Ce qui a stoppé les équipes', 'Six vérifications, à chaque appel', CHECKS_FR),
    closing: `
      <div class="l" data-k="l1">La fraude traverse les frontières entre entreprises.</div>
      <div class="l alert" data-k="l2">Vos contrôles doivent en faire autant.</div>
      <div class="fine" data-k="fine">Simulation pédagogique. La Banque Lumora, Teleqo Mobile et toutes les données sont fictives.
        Elle illustre des contrôles d’identité à l’exécution pour les agents IA, la catégorie de contrôles offerte par IBM Verify
        Identity Protection avec Agentic Runtime Security, ainsi qu’un signal d’échange de carte SIM partagé par l’opérateur
        mobile. Ce n’est pas un logiciel IBM.</div>`,
  },
};

// French captions get non-breaking spaces before colons and inside numbers.
const frenchCaption = (s) => s.replace(/ :/g, ' :').replace(/(\d) (\d)/g, '$1 $2').replace(/(\d) \$/g, '$1 $');
const LINES = LANG === 'fr'
  ? Object.fromEntries(Object.entries(LINES_FR).map(([id, l]) => [id, l.text ? { ...l, text: frenchCaption(l.text) } : l]))
  : LINES_EN;
const CARD = CARDS[LANG];

// Selectors in fraud_ring.html.
const F = {
  wide: ['header.top', '.main'],
  top: 'header.top',
  live: ['.score', '.mapcard'],
  map: '.mapcard',
  crew: (n) => `.crew:nth-child(${n})`,
  pair: (a, b) => [`.crew:nth-child(${a})`, `.crew:nth-child(${b})`],
  feed: '.feed',
  verdict: ['.score', '#verdict'],
  take: '.take',
  run: '#runBtn',
  on: '#modeOn',
  kill: '#killBtn',
  reset: '#resetBtn',
};

// Runs inside fraud_ring.html and calls the page's own functions, so the film shows
// exactly what the page does when someone presents it, in the page's language.
function installSimHooks() {
  let raf = 0;
  const showClock = () => { document.getElementById('clock').textContent = mmss(S.t); };
  window.filmSim = {
    begin() {
      announceStart();
      S.running = true;
      renderRun();
    },
    // Fires the next scripted move, then runs the clock toward the move after it.
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
  pages: [{ id: 'sim', file: 'fraud_ring.html', wrap: true, hash: LANG === 'fr' ? 'fr' : '' }],
  async setup({ frames, frame, stage }) {
    await frames.sim.evaluate(installSimHooks);
    await frame('sim')('frame', F.wide, { safeH: 1080, fill: 0.96, instant: true });
    await stage('card', CARD.opening);
  },
  async play({ after, stage, frame, caption, speak, ring, press, sleep }) {
    const cam = frame('sim'), sim = frame('sim', 'filmSim');
    const move = (holdMs = 5200) => sim('next', holdMs);

    // Cold open
    await after(1.0); await stage('reveal', 'ey', 'l1'); speak('open1');
    await after(3.6); await stage('reveal', 'l2'); speak('open2');
    await after(4.4); await stage('cardOut');

    // The companies and the crews
    await after(1.4); await caption('intro1');
    await after(6.5); await cam('frame', F.map); await caption('intro2');
    await after(5.5); await caption(null); await cam('frame', F.pair(1, 2), { maxScale: 1.6 });
    await after(1.6); await ring(cam, F.crew(1)); await caption('crew1');
    await after(4.4); await ring(cam, F.crew(2)); await caption('crew2');
    await after(3.2); await stage('unring'); await cam('frame', F.pair(3, 4), { maxScale: 1.6 });
    await after(1.6); await ring(cam, F.crew(3)); await caption('crew3');
    await after(3.2); await ring(cam, F.crew(4)); await caption('crew4');
    await after(3.2); await stage('unring'); await caption(null); await cam('frame', F.top);

    // Controls off
    await after(1.6); await caption('go'); await press(cam, F.run, { tap: true }); await sim('begin');
    await after(2.2); await stage('cursorHide'); await cam('frame', F.live);
    await after(1.6); await move(); await caption('x1');
    await after(5.0); await move(); await caption('x2');
    await after(5.0); await move(); await caption('x3');
    await after(5.0); await move(); await caption('x4');
    await after(4.5); await move(); await caption('x5');
    await after(4.5); await cam('frame', F.feed); await move(); await caption('x6');
    await after(4.5); await move(); await caption('x7');
    await after(4.5); await cam('frame', F.live); await move(); await caption('x8');
    await after(4.5); await move(); await caption('x9');
    await after(4.5); await move(); await caption('x10');
    await after(4.5); await move(); await caption('x11');
    await after(4.5); await sim('end'); await cam('frame', F.verdict); await caption('offEnd1');
    await after(7.0); await cam('frame', F.take); await caption('offEnd2');
    await after(5.5); await caption(null); await cam('frame', F.top);

    // Controls on, then the kill switch
    await after(1.6); await press(cam, F.reset);
    await after(1.2); await caption('on0'); await press(cam, F.on);
    await after(1.0); await press(cam, F.run, { tap: true }); await sim('begin');
    await after(2.2); await stage('cursorHide'); await cam('frame', F.live);
    await after(1.6); await move(); await caption('y1');
    await after(5.0); await move(); await caption('y2');
    await after(5.0); await move(); await caption('y3');
    await after(4.5); await caption('y3b');
    await after(4.5); await move(); await caption('y4');
    await after(4.5); await move(); await caption('y5');
    await after(4.5); await move(); await caption('y6');
    await after(5.0); await caption(null); await cam('frame', F.top);
    await after(1.6); await caption('kill'); await press(cam, F.kill);
    await after(2.2); await stage('cursorHide'); await cam('frame', F.live);
    await after(1.6); await move(); await caption('y7');
    await after(4.5); await caption('rest');
    for (let i = 0; i < 4; i += 1) { await sleep(1300); await move(1300); }
    await after(3.0); await sim('end'); await cam('frame', F.verdict); await caption('onEnd');
    await after(6.0); await caption(null);

    // What stopped the crews
    await after(0.6); await stage('card', CARD.checks); await stage('cardIn');
    await after(1.3); await stage('reveal', 'ey', 'l1'); speak('checks');
    for (let i = 1; i <= 6; i += 1) { await sleep(900); await stage('reveal', `o${i}`); }
    await after(6.0); await stage('fadeCardText');

    // Close
    await after(1.2); await stage('card', CARD.closing);
    await after(0.3); await stage('reveal', 'l1'); speak('end1');
    await after(2.6); await stage('reveal', 'l2'); speak('end2');
    await after(3.6); await stage('reveal', 'fine');
    await after(7.0);
  },
}).catch((err) => { console.error(err); process.exit(1); });
