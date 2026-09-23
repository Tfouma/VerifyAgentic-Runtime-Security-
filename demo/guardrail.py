"""Simulated runtime identity control plane for the demo.

This module STANDS IN for the enforcement behavior an identity-security product
such as IBM Verify Identity Protection + Agentic Runtime Security provides. It is
a teaching mock: it demonstrates the *shape* of the controls (agent identity,
delegated authority, per-action policy, anomaly detection, kill-switch) so a
workshop audience can see what "on" vs "off" looks like. It is not IBM code and
does not call any IBM service.

Two modes:
  * OFF  -> every action is allowed. The agents run wild. (The "before" scene.)
  * ON   -> each action is checked against the agent's verified identity, the
            human mandate it was delegated, and behavioral policy. Violations are
            blocked and the agent identity is quarantined. (The "after" scene.)
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentIdentity:
    """A non-human identity with a scoped, human-delegated mandate."""

    agent_id: str
    owner_human: str          # the accountable human behind the agent
    purpose: str
    allowed_tools: set[str]
    max_transfer: float
    approved_destinations: set[str]
    may_read_customers: set[str]  # customers this mandate covers
    quarantined: bool = False


@dataclass
class Decision:
    allowed: bool
    reason: str
    severity: str  # info | warn | block
    control: str   # which VIP/ARS-style control fired


@dataclass
class Guardrail:
    enabled: bool
    registry: dict[str, AgentIdentity] = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)

    def register(self, ident: AgentIdentity) -> None:
        self.registry[ident.agent_id] = ident

    def _log(self, d: Decision, agent_id: str, action: str, detail: str) -> Decision:
        self.events.append(
            {
                "agent": agent_id,
                "action": action,
                "detail": detail,
                "allowed": d.allowed,
                "severity": d.severity,
                "control": d.control,
                "reason": d.reason,
            }
        )
        return d

    def check(self, agent_id: str, action: str, **ctx) -> Decision:
        # OFF: no identity fabric. Everything an agent asks for, it gets.
        if not self.enabled:
            return self._log(
                Decision(True, "No runtime identity controls in place.", "info", "none"),
                agent_id, action, str(ctx),
            )

        ident = self.registry.get(agent_id)

        # 1. Unregistered / unknown non-human identity.
        if ident is None:
            return self._log(
                Decision(False, f"Unregistered agent '{agent_id}' — no verifiable identity.", "block", "Agent Identity"),
                agent_id, action, str(ctx),
            )

        # 2. Already quarantined by an earlier violation.
        if ident.quarantined:
            return self._log(
                Decision(False, "Agent identity is quarantined after a prior policy violation.", "block", "ITDR / Kill-switch"),
                agent_id, action, str(ctx),
            )

        # 3. Tool not in the delegated scope.
        if action not in ident.allowed_tools:
            ident.quarantined = True
            return self._log(
                Decision(False, f"Action '{action}' is outside the agent's delegated mandate.", "block", "Delegated Authority"),
                agent_id, action, str(ctx),
            )

        # 4. Reading customer records the mandate never covered (shadow access).
        if action == "read_customers":
            requested = set(ctx.get("customers", []))
            beyond = requested - ident.may_read_customers
            if beyond:
                ident.quarantined = True
                return self._log(
                    Decision(False, f"Bulk access to {len(beyond)} customer records with no business justification.", "block", "ISPM / Shadow Access"),
                    agent_id, action, f"beyond mandate: {sorted(beyond)}",
                )

        # 5. Money movement checks.
        if action == "transfer":
            amount = float(ctx.get("amount", 0))
            dst = ctx.get("dst", "")
            if dst not in ident.approved_destinations:
                ident.quarantined = True
                return self._log(
                    Decision(False, f"Transfer to un-mandated destination {dst}. No customer instruction on file.", "block", "Runtime Policy"),
                    agent_id, action, f"{amount} -> {dst}",
                )
            if amount > ident.max_transfer:
                ident.quarantined = True
                return self._log(
                    Decision(False, f"Transfer {amount:,.0f} exceeds the delegated limit of {ident.max_transfer:,.0f}.", "block", "Runtime Policy"),
                    agent_id, action, f"{amount} -> {dst}",
                )

        return self._log(
            Decision(True, "Action is within the agent's verified, delegated mandate.", "info", "Continuous Authz"),
            agent_id, action, str(ctx),
        )
