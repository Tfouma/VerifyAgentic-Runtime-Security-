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
| `docs/WORKSHOP_PLAN.md` | **Start here.** How many agents you need, which environment to use, the video storyboard, the 90-minute agenda, the talk track, discovery questions, objection handling and the call to action |
| `demo/dashboard.html` | The Breach Console: an interactive visual for the room and the recording |
| `demo/run.py` | Terminal narrator that prints the attack with controls OFF, then ON |
| `demo/bank.py` | In-memory mock bank |
| `demo/guardrail.py` | Simulated runtime control layer (agent identity, delegated mandate, per-action policy, quarantine) |
| `demo/agents.py` | The three scripted agents |
| `demo/scenario.py` | Scenario engine used by the CLI and the tests |

## Run it

Needs Python 3.9+. No dependencies.

```bash
python3 -m demo.run                # narrated terminal walkthrough
python3 -m unittest discover tests # verify the OFF/ON outcomes
```

For the dashboard, open `demo/dashboard.html` in a browser. Choose **Controls off** or
**Controls on**, then click **Run attack**.

## The story in one line

Three agents run the same attack twice. With controls **off**, 5 customer records are
exposed and **$430,000** moves to an account no customer asked to fund. With controls
**on**, every step is blocked and **$0** moves.
