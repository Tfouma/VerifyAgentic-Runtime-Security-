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

### A. Recorded video (about 3 minutes). Storyboard:

| Time | Scene | On screen | Voiceover (short version) |
|------|-------|-----------|--------------------------|
| 0:00–0:20 | **Cold open** | Black screen, then the Breach Console | "Your bank just deployed AI agents to help customers. Here's what happens when one of them turns." |
| 0:20–0:40 | **Meet the agents** | Agent Fleet panel | "One customer-service agent, trusted and registered. Two helpers it recruits. Nobody registered those." |
| 0:40–1:30 | **Controls OFF** | Click *Run attack* and watch four ALLOWED steps land | "A hidden instruction in a support ticket. Every customer record pulled. Accounts ranked. Two hundred and fifty thousand gone. Then one-eighty more. Nothing stopped it." |
| 1:30–1:45 | **The number** | Impact panel: 5 records, **$430,000** | Silence. Let it land. |
| 1:45–2:35 | **Controls ON** | Flip the switch, replay, and watch four BLOCKED steps | "Same agents. Same attack. This time, every action is checked against who the agent is and what a human actually authorized it to do." |
| 2:35–2:50 | **The contrast** | 0 records, **$0** | "Zero records. Zero dollars. Every agent quarantined, with a full audit trail back to an accountable human." |
| 2:50–3:00 | **Call to action** | Title card | "Your agents are already in production. Is anything checking them?" |

**How to record:** screen-capture the published Breach Console at 1080p (OBS or
QuickTime), full-screen browser, zoom 110–125%. Record OFF and ON as separate takes.
Add the voiceover afterwards.

### B. Live workshop (about 90 minutes)

| Block | Time | Content |
|-------|------|---------|
| **1. The shift** | 10 min | AI agents are now an identity problem. They log in, hold tokens, call APIs and act on behalf of people. Most IAM programmes were built for humans. |
| **2. Show the video** | 5 min | Play the 3-minute film. Don't explain it yet. |
| **3. Live replay** | 15 min | Run the Breach Console live. Pause on each step and ask the room, *"Would you catch this today?"* |
| **4. Unpack the controls** | 20 min | Open the Lateral Movement Map. Step through the chain with controls off, then on. Show where each lateral hop lands and which of the five controls in section 4 fires. |
| **5. Their environment** | 25 min | Discovery conversation (questions in section 5). Whiteboard their agent landscape. |
| **6. Path forward** | 15 min | Propose an **identity posture assessment** for their agent estate, then a scoped Tier B proof of value. |

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
