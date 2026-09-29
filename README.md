# Agentic Breach Demo — IBM Verify Identity Protection + Agentic Runtime Security

A workshop kit and simulation for showing clients how runtime identity controls stop a
compromised AI agent from exposing customer data and diverting funds.

**Everything here is fictional and simulated.** The bank, customers, accounts and balances
exist only in memory. Nothing touches a real system. The "controls on" mode models the
enforcement pattern of a runtime identity layer for AI agents. It is an independent
illustration, not IBM software.

## What's inside

| Path | What it is |
|------|------------|
| `docs/DEMO_DESJARDINS.md` | **Démo client en français** : guide du présentateur pour la vidéo et la démo fonctionnelle |
| `livedemo/` | Démo fonctionnelle en direct (FR) : `python3 -m livedemo --ouvrir`. Jetons signés, échange RFC 8693 avec RAR, identifiants de 5 minutes, politique OPA, approbation humaine, suspension et double révocation, sur une base SQLite |
| `video/` | Vidéo narrée en français (`demo-agent-gouverne.mp4`, sous-titres `.srt`) et scripts pour la régénérer |
| `docs/WORKSHOP_PLAN.md` | **Start here.** How many agents you need, which environment to use, the video storyboard, the 90-minute agenda, the talk track, discovery questions, objection handling and the call to action |
| `docs/USE_CASE_DEVIN_ZERO_TRUST.md` | Use case: zero trust for Devin (AI software engineer) with IBM Agent Identity in a bank. Actors, threat model, architecture, flows, policy matrix, regulatory mapping and rollout |
| `docs/USE_CASE_ENTERPRISE_AI_AGENTS_ZERO_TRUST.md` | Use case: zero trust for the AI agents employees use (ChatGPT, Gemini, Claude, Claude Code, Codex, Cursor, Devin, OpenClaw and others). Agent categories, access patterns, per-tool controls, scenarios, tiers and rollout |
| `docs/USE_CASE_SANDBOXED_AGENT_BANKING.md` | Use case: sandboxed KYC agent acting for an analyst (Entra ID sign-in, IBM Verify token exchange and RAR, Vault 5-minute credentials, MCP gateway, OPA, human approval for writes, shared-signals response). Banking version of IBM's NVIDIA OpenShell demo |
| `demo/sandbox_flow.html` | Governed Agent Sandbox: interactive architecture with Overview, Delegation and Policy lifecycle tabs and four scenarios (KYC remediation, poisoned runbook, failed approvals, unregistered tool) |
| `demo/dashboard.html` | The Breach Console: an interactive visual for the room and the recording |
| `demo/attack_map.html` | Lateral Movement Map: architecture view of each step, including the request chain across agents and the background checks that run on every call |
| `demo/run.py` | Terminal narrator that prints the attack with controls OFF, then ON |
| `demo/bank.py` | In-memory mock bank |
| `demo/guardrail.py` | Simulated runtime control layer (agent identity, delegated mandate, per-action policy, quarantine) |
| `demo/agents.py` | The three scripted agents |
| `demo/scenario.py` | Scenario engine used by the CLI and the tests |

## Run it

Needs Python 3.9+. No dependencies.

```bash
python3 -m demo.run                # narrated terminal walkthrough
python3 -m unittest discover tests # verify the OFF/ON outcomes and the live demo scenarios
python3 -m livedemo --ouvrir       # French live console (http://127.0.0.1:8765)
```

For the dashboard, open `demo/dashboard.html` in a browser. Choose **Controls off** or
**Controls on**, then click **Run attack**. To explain what happens behind each step,
open `demo/attack_map.html` and step through it or click **Play chain**.

## The story in one line

Three agents run the same attack twice. With controls **off**, 5 customer records are
exposed and **$430,000** moves to an account no customer asked to fund. With controls
**on**, every step is blocked and **$0** moves.
