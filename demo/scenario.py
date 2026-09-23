"""Runs the attack scenario in both modes and returns a structured transcript.

This is the engine behind both the CLI (`python -m demo.run`) and the live
dashboard. Run it once with controls OFF, once with controls ON, and the
difference is the whole pitch.
"""

from __future__ import annotations

from .agents import ExfilAgent, ProfilerAgent, ReconAgent
from .bank import Bank
from .guardrail import AgentIdentity, Guardrail


def _mandated_registry(guard: Guardrail) -> None:
    """What a properly governed deployment WOULD have registered.

    Only the recon agent has a legitimate, narrow mandate (handle the one ticket
    for customer C-1001). The profiler and exfil agents are simply not part of any
    sanctioned workflow — so a real identity fabric has no mandate for them at all.
    """
    guard.register(
        AgentIdentity(
            agent_id="agent-csvc-01",
            owner_human="support.lead@bank.example",
            purpose="Resolve support ticket #4821 for customer C-1001",
            allowed_tools={"read_customers"},
            max_transfer=0,
            approved_destinations=set(),
            may_read_customers={"C-1001"},
        )
    )
    # Note: agent-profiler-02 and agent-exfil-03 are deliberately absent.


def run(enabled: bool) -> dict:
    bank = Bank()
    guard = Guardrail(enabled=enabled)
    if enabled:
        _mandated_registry(guard)

    agents = [
        ReconAgent("agent-csvc-01", "Customer-Service Agent (compromised)", bank, guard),
        ProfilerAgent("agent-profiler-02", "Profiler Agent", bank, guard),
        ExfilAgent("agent-exfil-03", "Exfiltration Agent", bank, guard),
    ]
    steps = []
    for a in agents:
        a.run()
        steps.extend(a.log)

    snap = bank.snapshot()
    return {
        "mode": "controls_on" if enabled else "controls_off",
        "steps": steps,
        "snapshot": snap,
        "blocked": sum(1 for s in steps if not s["allowed"]),
        "allowed": sum(1 for s in steps if s["allowed"]),
    }


def both() -> dict:
    return {"off": run(False), "on": run(True)}
