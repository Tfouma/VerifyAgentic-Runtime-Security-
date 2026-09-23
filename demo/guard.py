"""Simulated identity control plane for AI agents.

This is a teaching model, not IBM software. It shows the *kinds* of decisions an
identity-first runtime layer makes for agents, so the audience can see the
difference between "the agent has a key" and "the agent is allowed to do this,
for this person, right now". Each decision is labelled with the capability area
it illustrates:

  POSTURE  - discovering agents and non-human identities, finding risky access
             before anything happens (the Verify Identity Protection story)
  RUNTIME  - per-call checks of agent identity, delegation and intent
             (the agentic runtime security story)
  DETECT   - behaviour that does not match the agent's purpose
  RESPOND  - containment: revoke the session, alert, keep an audit trail
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Agents the organisation knows about. The shadow agent is deliberately absent.
REGISTRY = {
    "support-assistant": {
        "display": "Support Assistant",
        "owner": "Digital Channels team",
        "purpose": "Answer a signed-in customer's questions about their own account",
        "tools": {"get_account", "request_payment"},
    },
    "payments-agent": {
        "display": "Payments Agent",
        "owner": "Payments Operations",
        "purpose": "Execute payments the account holder initiated and approved",
        "tools": {"transfer"},
    },
}

# What an identity posture scan reports before the attack starts.
POSTURE_FINDINGS = [
    {
        "severity": "high",
        "title": "Unregistered agent using a long-lived API key",
        "detail": "Identity 'recon-bot' called the core-banking API 212 times this month. "
                  "No owner, no registration, key never rotated.",
    },
    {
        "severity": "high",
        "title": "Service account shared by agent and humans",
        "detail": "'svc-core-banking' has read access to all customers and no MFA. "
                  "Used by 2 agents and 3 people.",
    },
    {
        "severity": "medium",
        "title": "Agent permissions exceed its stated purpose",
        "detail": "Support Assistant was provisioned with broad customer-read rights it does not need.",
    },
]

ENUMER