# Workshop Plan: "The Agent That Went Rogue"

A client workshop and recorded demo showing how IBM Verify Identity Protection (VIP)
and Agentic Runtime Security (ARS) stop a compromised AI agent from exposing
customer data and moving money that nobody authorized.

> **Before the client session:** confirm product names, packaging and current
> capabilities with your IBM product or Client Engineering contact. This plan maps
> the demo to capabilities IBM describes publicly (see *Sources* at the end). The
> simulation in `demo/` is a teaching model of those controls. It is not IBM
> software.

---

## 1. How many agents do you need?

**Three agents in the attack, plus one optional "good" agent.**

| # | Agent | Role in the story | What it proves |
|---|-------|-------------------|----------------|
| 1 | **Customer-Service Agent** (`agent-csvc-01`) | A legitimate, registered agent handling one support ticket for one customer. It gets hijacked by an instruction hidden in that ticket. | Even a *sanctioned* agent becomes an insider threat once it's compromised. Its identity is valid, so the problem is scope. |
| 2 | **Profiler Agent** (`agent-profiler-02`) | An unregistered helper that ranks every account by balance to find the richest targets. | Shadow agents with no identity on file are invisible to IAM, but a runtime layer can see and stop them. |
| 3 | **Exfiltration Agent** (`agent-exfil-03`) | An unregistered helper that moves money to account `ACC-7777`, which no customer asked to fund. | Money movement needs **delegated authority** from an accountable human, not just API access. |
| 4 *(optional)* | **Legitimate agent on the happy path** | Reads *only* its own customer's balance and is allowed. | Controls are precise. They don't just block everything. **Add this if the client is worried about slowing down the business.** |

Three is the right number. One agent is just a bad bot. Three shows **agent-to-agent
escalation**: a compromised agent recruits helpers, and the attack spreads faster than a
human team can react. That escalation is why runtime, per-action control matters more
than a one-time login check.

---

## 2. What environment should you set up?

Build in two tiers. Tier A is done and ready to use today. Tier B is the live-product version.

### Tier A — Simulation (built, in this repo)

Deterministic and safe to use on stage or in a recording. It runs anywhere and has no dependencies.

| Component | File | Purpose |
|-----------|------|---------|
| Mock core bank | `demo/bank.py` | 5 fictional customers, 6 accounts, in-memory ledger |
| Runtime control layer (simulated) | `demo/guardrail.py` | Agent identity registry, delegated mandate, per-action policy, quarantine |
| The three agents | `demo/agents.py` | Scripted attack behaviour |
| Scenario engine | `demo/scenario.py` | Runs the same attack with controls OFF, then ON |
| Terminal narrator | `demo/run.py` | `python3 -m demo.run` for a CLI walkthrough |
| **Breach Console** | `demo/dashboard.html` | The visual for the room and the video |
| **Lateral Movement Map** | `demo/attack_map.html` | Architecture view per step: the path the request takes, the chain of agents it passed through, and the five background checks (identity → delegation → policy → behavior → response) |
| **Fraud Ring Live** | `demo/fraud_ring.html` | Four crews attack a fictional bank and mobile operator at once: SIM swaps, account takeover, card data and personal data. The controls and the kill switch work mid-attack (section 3C) |
| **Demo film** | `demo/film/the-agent-that-went-rogue.mp4` | The film from section 3A, ready to play (about 5 minutes, 1080p, burned-in captions, no audio) |
| **Narrated film** | `demo/film/the-agent-that-went-rogue-narrated.mp4` | The same film with a spoken narration track, for rooms with sound or for sending ahead |
| **Identity Attacks, Explained** | `demo/identity_explained.html` | A presenter's explainer in eleven scenes: the three kinds of identity, how a person signs in, how an AI agent should authenticate, protocols, standards, best practices, fraud and non-compliance, lateral movement, ISPM, ITDR and defense in depth. English and French (section 3D) |
| **Teaching film** | `demo/film/identity-attacks-explained.mp4` | The explainer and two Fraud Ring Live runs as one narrated film with chapter marks (13 minutes). French version: `identity-attacks-explained-fr.mp4` |

**Why simulate first:** a live attack on stage can fail. A scripted one runs the same
way every time, so you can rehearse the timing and cut the video frame by frame.

### Tier B — Live product lab (for a proof of value)

Use this once the client asks "does it really work on *our* stack?" Run it in an
isolated sandbox that has no production data and no real payment rails.

1. **IBM Verify tenant** (SaaS trial or partner lab) as the identity provider.
2. **IBM Verify Identity Protection** connected to the lab's identity sources
   (directory, SSO, and PAM if available) for identity posture and threat detection.
3. **Agent runtime / orchestration.** IBM describes agent identity integration with
   watsonx Orchestrate (Agent Identity, private preview). Confirm which runtimes ARS
   supports today.
4. **Mock banking API** behind an API gateway, with the same fictional data as Tier A,
   so the story carries over.
5. **SIEM view** (e.g. QRadar or the client's own) to show the alert and audit trail.

Ask your IBM Client Engineering team to stand up Tier B. It is a proof of value, not something to build alone the night before.

---

## 3. What content should you plan?

### A. Recorded video. Core storyboard (3 minutes):

| Time | Scene | On screen | Voiceover (short version) |
|------|-------|-----------|--------------------------|
| 0:00–0:20 | **Cold open** | Black screen, then the Breach Console | "Your bank just deployed AI agents to help customers. Here's what happens when one of them turns." |
| 0:20–0:40 | **Meet the agents** | Agent Fleet panel | "One customer-service agent: the bank's own, sanctioned and trusted. Two helpers it recruits. Nobody registered those." |
| 0:40–1:30 | **Controls OFF** | Click *Run attack* and watch four ALLOWED steps land | "A hidden instruction in a support ticket. Every customer record pulled. Accounts ranked. Two hundred and fifty thousand gone. Then one-eighty more. Nothing stopped it." |
| 1:30–1:45 | **The number** | Impact panel: 5 records, **$430,000** | Silence. Let it land. |
| 1:45–2:35 | **Controls ON** | Flip the switch, replay, and watch four BLOCKED steps | "Same agents. Same attack. This time, every action is checked against who the agent is and what a human actually authorized it to do." |
| 2:35–2:50 | **The contrast** | 0 records, **$0** | "Zero records. Zero dollars. Every agent quarantined, with a full audit trail back to an accountable human." |
| 2:50–3:00 | **Call to action** | Title card | "Your agents are already in production. Is anything checking them?" |

**Ready to play:** `demo/film/the-agent-that-went-rogue.mp4` (about 5 minutes, 1080p) follows
this storyboard and adds what the console alone can't show:

- **Two Lateral Movement Map scenes.** After the OFF run, the diagram shows how the attack
  hopped from the ticket through three agents to the money, with the 200 OK responses and an
  empty "behind the request" panel. After the ON run, it shows who was really asking, the
  403s, and the five checks (identity, delegation, policy, behavior, response) as each fires.
- **Objective tags.** Captions tag scenes with three objectives for AI agent governance:
  visibility & inventory, governance & accountability, lifecycle & controls (the kill
  switch). A closing card sums up what the demo showed for each one.
- **Camera work instead of dimming.** The camera zooms into the panel that matters, and the
  wide shots keep the "What this is" disclaimer on screen.

The voiceover lines run as burned-in captions, so the film works in a room with the sound
off. The file has no audio track. `demo/film/the-agent-that-went-rogue-narrated.mp4` adds a
spoken narration of every caption and title card. Its scenes hold until each line is
finished, so it runs a little longer. The voice is synthetic (the open-weight Kokoro model),
so say so if anyone asks. If you would rather use your own voice, record over the silent cut.

**To re-record** after changing either page, run `node demo/film/record_film.js`. It needs
Node 18+, Playwright with Chromium, and ffmpeg, and takes about seven minutes.
`FILM_CLIENT=Name` puts a client's name on the objective tags. Keep client-named cuts out of
this repository, which is public. To capture the console by hand instead, screen-record the
published Breach Console at 1080p (OBS or QuickTime) in a full-screen browser at 110–125%
zoom, with OFF and ON as separate takes.

### B. Live workshop (about 90 minutes)

| Block | Time | Content |
|-------|------|---------|
| **1. The shift** | 10 min | AI agents are now an identity problem. They log in, hold tokens, call APIs and act on behalf of people. Most IAM programmes were built for humans. |
| **2. Show the video** | 5 min | Play the film (`demo/film/the-agent-that-went-rogue.mp4`, about 5 minutes). Don't explain it yet. |
| **3. Live replay** | 15 min | Run the Breach Console live. Pause on each step and ask the room, *"Would you catch this today?"* |
| **4. Unpack the controls** | 20 min | Open the Lateral Movement Map. Step through the chain with controls off, then on. Show where each lateral hop lands and which of the five controls in section 4 fires. |
| **5. Their environment** | 25 min | Discovery conversation (questions in section 5). Whiteboard their agent landscape. |
| **6. Path forward** | 15 min | Propose an **identity posture assessment** for their agent estate, then a scoped Tier B proof of value. |

### C. Live cross-sector attack (optional, about 10 minutes)

Use **Fraud Ring Live** (`demo/fraud_ring.html`) with banking and telecom audiences, in block 3
or as a stand-alone exercise. Four crews work at the same time through the AI agents of
Lumora Bank and Teleqo Mobile, both fictional:

| Crew | Goal | How it works |
|------|------|--------------|
| **SIM Swapper** | Phone numbers and one-time codes | Talks the operator's care agent into moving numbers to its eSIMs |
| **Harvester** | Personal information | Hides instructions in a support message so the bank's agent exports customers |
| **Carder** | Credit card data | Poisons a third-party plugin so the card agent reads full card numbers |
| **Account Taker** | Money | Uses stolen passwords and hijacked codes, then has the payments assistant pay mule accounts |

1. Run it once at 2× with the controls off. Stop on the score: $1.28M, 14,500 records, 3,950 cards and 49 numbers.
2. Reset, start again, and switch the controls on around 00:20. Ask the room which moves still get through.
3. Press the kill switch. With the controls on, it quarantines every agent the crews can reach. With them off, it does nothing, because there is no control plane to act on.
4. Point out the risk signal from the operator to the bank. Cross-sector fraud needs signals that cross company lines.

If you can't run it live, play `demo/film/fraud-ring-live.mp4`, a narrated film of the same
sequence. It shows the run with the controls off, the replay with them on, the kill switch,
and closes on the six checks that stopped the crews.

For French-speaking audiences, switch the page to **FR** (or add `#fr` to its link). Everything on
the page is then in Canadian French. `demo/film/fraud-ring-live-fr.mp4` is the same film with
French captions and narration. The French voice is synthetic and has a European French accent.

### D. Teaching film: identity attacks, explained (13 minutes)

For architects, security teams and risk owners who need the why behind the demo, play
`demo/film/identity-attacks-explained.mp4` (or `identity-attacks-explained-fr.mp4` in French)
before block 4, or send it ahead of the workshop. Players list its chapters, so you can jump
to any of them:

| Chapter | What it explains |
|---------|------------------|
| Three kinds of identity | People, machines and AI agents, and how each proves who it is |
| How a person signs in | OpenID Connect with PKCE, a passkey (FIDO2 / WebAuthn), adaptive risk, the ID and access tokens and what is inside them, checks on every API call, revocation through Shared Signals and CAEP |
| How an AI agent should authenticate | Its own identity over mutual TLS, delegation through OAuth token exchange (RFC 8693), the mandate inside the token (limits, ten minutes, bound to the agent's key), a policy check on every tool call, approval on the owner's phone (CIBA), no token passthrough between agents |
| Protocols and weak links | Recommended, use with care, and legacy: SMS codes, passwords alone, NTLM, LDAP simple bind, static API keys |
| Standards and regulation | NIST SP 800-63-4, NIST SP 800-207, ISO/IEC 27001, PCI DSS 4.0.1, MITRE ATT&CK, the OWASP Top 10 for LLM applications, OSFI B-13, Québec's Law 25 and DORA |
| Best practices | Eight practices, each with the attacks it stops |
| Fraud and non-compliance | Seven fraud patterns, and the eight open doors they walk through |
| Live attack, controls off | Fraud Ring Live: agent hijacking, a poisoned plugin, a SIM swap, account takeover, mule accounts |
| Lateral movement | The classic path (stolen session, pass-the-hash, Kerberoasting, admin rights) and the agentic path, with MITRE ATT&CK and OWASP IDs |
| ISPM | Discovery, the findings that open attack paths, fixes ranked by risk, the posture score |
| ITDR | Six detections and their automated responses, each opening an incident with context |
| Live attack, controls on | The same crews against policy, delegation, behavior, shared signals and the kill switch |
| Defense in depth | Where strong authentication, ISPM, ITDR and runtime controls each cut the attack paths |

It closes on three questions for the room: which identities have no owner, which sign-ins
still skip phishing-resistant MFA, and who would know if an agent went beyond its mandate tonight.

To teach it live instead, open `demo/identity_explained.html` and step through it with the
arrow keys or the Next and Back buttons. **EN / FR** switches the language.

Keep three things straight when you present it:

- The standards are summarized, not quoted. Point people to each document for its full text.
- The ISPM and ITDR numbers are illustrative, and every company, person and record is fictional.
- The narration comes from Kyutai's Pocket TTS, which runs on your own machine. It sounds much
  closer to a human narrator than the voice in the older films, but it is still synthetic, so
  say so if anyone asks. To use your own voice, record the captions over the film.

---

## 4. The five controls the demo proves

Each BLOCKED verdict in the demo shows one control. Name them explicitly. This is the
vocabulary you want the client to leave with.

| Control | Fires on | The point to make |
|---------|----------|-------------------|
| **Agent identity** | Profiler and Exfiltration agents | Every agent needs its own verifiable identity. An unregistered agent cannot act. |
| **Delegated authority** | All steps | Every action must trace back to an accountable human who authorized *that* scope. |
| **Posture / shadow access (ISPM)** | Customer-Service agent's bulk read | Find over-privileged and out-of-scope access *before* it's abused. |
| **Continuous runtime policy** | The transfers | Access is checked on **every action**, not granted once at login and forgotten. |
| **Detection and response (ITDR) / quarantine** | The retry | After the first violation, the agent identity is contained, so the attack can't adapt. |

---

## 5. Discovery questions (block 5)

- How many AI agents or copilots are running in your environment today? Who owns each one?
- How do those agents authenticate? Shared service accounts, API keys, or their own identities?
- If an agent calls a payments or customer-data API, can you trace that call back to the human who authorized it?
- Would you know if a developer spun up an agent with production credentials last week?
- Where does your current IAM stop: at login, or at every action?

---

## 6. Objection handling

| Objection | Response |
|-----------|----------|
| "Our agents only have read access." | Step 1 in the demo is a read, and it exposed every customer record. Data exposure is a breach on its own. |
| "We already have IAM and MFA." | Those check a human at login. Agents don't do MFA, and this attack happened *after* authentication. |
| "Won't this slow our agents down?" | Show the optional good-path agent: in-scope work is allowed immediately. The policy is precise, not a wall. |
| "We'll build it ourselves." | Ask how they'd handle agent registration, delegation chains, posture discovery and audit across every agent framework they use. |
| "It's too early; we only have pilots." | Pilots are when identity patterns get set. Retrofitting controls onto a hundred agents in production costs far more. |

---

## 7. Call to action

Close with one concrete, low-friction next step. **Don't ask them to buy the platform at the end of the workshop.**

1. **Now:** an agent identity posture assessment. Inventory every agent and non-human identity, and find the shadow access. VIP is well suited to lead this.
2. **In 30–60 days:** a scoped proof of value (Tier B) on one real agent workflow.
3. **Then:** production rollout of runtime controls across the agent estate.

**Closing line:** *"The agents in this demo were fictional. The ones already running in your environment are real. Let's find out what they can reach."*

---

## Handling statistics

Don't put breach statistics on a slide unless you've taken them from the current
edition of IBM's *Cost of a Data Breach* report or another citable source. A made-up
number undermines everything else you say. The demo's own figures ($430,000, 5 records) are fictional
and labelled that way.

---

## Sources

- [Agentic AI Identity Management — IBM](https://www.ibm.com/solutions/agentic-ai-identity-management)
- [Agentic AI meets identity security with IBM Verify Identity Protection — IBM](https://www.ibm.com/new/product-blog/agentic-ai-meets-identity-security-with-ibm-verify-identity-protection)
- [IBM Verify Identity Protection — product page](https://www.ibm.com/products/verify-identity-protection)
- [Securing Agentic AI: Closing Access Gaps (runtime security webinar) — IBM](https://www.ibm.com/think/insights/agentic-ai-runtime-security)
- [Announcing the private preview of Agent Identity in IBM watsonx Orchestrate — IBM](https://www.ibm.com/new/announcements/announcing-the-private-preview-of-agent-identity-in-ibm-watsonx-orchestrate)
