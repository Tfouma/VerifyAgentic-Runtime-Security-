"""MCP Agent Gateway: the only door out of the sandbox.

For every tool call it runs the chain the demo shows:
  introspect caller → OPA (registration, egress) → SQL guard → tier gate and
  RFC 8693 exchange with RFC 9396 RAR at IBM Verify → step-up if needed →
  Vault mints a 5-minute credential → call the MCP server → revoke → CAEP event.

The agent never receives a downstream credential: it stays inside this module.
"""

from __future__ import annotations

import sqlite3

from . import jwt
from .core import AGENT_PARENT, SPIFFE, World

# (server, tool) -> (RAR type, action, Vault role, locations)
TOOLS = {
    ("jira", "read_issue"): ("jira", "read", "jira_lecteur", ["FIN"]),
    ("gitlab", "get_file"): ("gitlab", "read", "gitlab_lecteur", ["kyc/guides"]),
    ("databricks", "query"): ("databricks", "read", "dbx_lecteur", ["kyc_cote_risque_membre", "transactions_90j"]),
    ("databricks", "execute"): ("databricks", "write", "dbx_redacteur", ["kyc_cote_risque_membre"]),
    ("annuaire", "scim_get"): ("scim", "read", "scim_lecteur", ["Users"]),
    ("web", "fetch"): ("web", "read", "web_lecteur", ["https"]),
    ("paiements", "initier_virement"): ("paiements", "write", None, ["virements"]),
}
NODE = {"jira": "n-jira", "gitlab": "n-gitlab", "databricks": "n-dbx", "web": "n-web",
        "annuaire": "n-lookup", "paiements": "n-pay"}
EDGE = {"jira": "e-gw-jira", "gitlab": "e-gw-gitlab", "databricks": "e-gw-dbx", "web": "e-gw-web",
        "annuaire": "e-gw-lookup", "paiements": "e-gw-pay"}


class Gateway:
    def __init__(self, world: World):
        self.w = world

    def _caller(self, actor: dict) -> tuple[str, str, str]:
        agent = next((a for a, s in SPIFFE.items() if s == actor.get("sub")), actor.get("sub", "?"))
        node, edge = ("n-parent", "e-parent-gw") if agent == AGENT_PARENT else ("n-sub", "e-sub-gw")
        return agent, node, edge

    def _refuse(self, agent: str, title: str, detail: str, nodes: dict, edges: dict) -> dict:
        """A policy refusal: counts toward the three-strike rule."""
        n = self.w.refused[agent] = self.w.refused.get(agent, 0) + 1
        seuil = self.w.policy.data["seuil_refus"]
        self.w.bus.emit("deny", f"{title} · tentative refusée {n}/{seuil}", detail, src="OPA",
                        nodes=nodes, edges=edges)
        if n == seuil:
            self.w.antenna.receive("agent-risk", subject=agent, reason=f"{seuil} tentatives refusées par la politique")
        return {"ok": False, "erreur": detail, "refus": n}

    def tools(self) -> dict:
        listed = self.w.policy.listed_tools()
        self.w.bus.emit("info", "Outils exposés à l'agent",
                        "OPA ne liste que les serveurs MCP enregistrés : " + ", ".join(
                            f"{s}.{t}" for s, ts in listed.items() for t in ts) + ". paiements-core n'apparaît pas.",
                        src="OPA", nodes={"n-opa": "ok", "n-gw": "hot"}, edges={"e-opa-gw": "ok"})
        return listed

    def delegate(self, body: dict) -> dict:
        try:
            res = self.w.verify.delegate(body["subject_token"], body["actor_token"], SPIFFE[body["sous_agent"]], body["rar"])
        except (jwt.InvalidToken, KeyError) as exc:
            self.w.bus.emit("deny", "Délégation refusée", str(exc), src="IBM Verify", nodes={"n-shim": "deny"})
            return {"ok": False, "erreur": str(exc)}
        if res["result"] != "ok":
            self.w.bus.emit("deny", "Délégation refusée", res["reason"], src="IBM Verify", nodes={"n-shim": "deny"})
            return {"ok": False, "erreur": res["reason"]}
        self.w.bus.emit("allow", "Délégation au sous-agent (portée réduite)",
                        f"La cale de délégation lance un second bac à sable. {body['sous_agent']} reçoit un jeton "
                        "limité à la lecture, lié à son identité SPIFFE (may_act).",
                        src="IBM Verify", token=res["claims"],
                        nodes={"n-parent": "hot", "n-shim": "hot", "n-sub": "ok", "n-verify": "ok", "gi-exchange": "ok"},
                        edges={"e-parent-shim": "live", "e-shim-sub": "live", "e-gw-verify": "live"})
        return {"ok": True, "token": res["token"]}

    def call(self, body: dict) -> dict:
        w, bus = self.w, self.w.bus
        server, tool, args = body["server"], body["tool"], body.get("args", {})
        try:
            actor = w.verify.verify_attestation(body["actor_token"])
        except jwt.InvalidToken as exc:
            bus.emit("deny", "Identité de charge de travail invalide", str(exc), src="Passerelle",
                     nodes={"gi-introspect": "deny", "n-gw": "hot"})
            return {"ok": False, "erreur": str(exc)}
        agent, cnode, cedge = self._caller(actor)
        target, tedge = NODE.get(server, "n-gw"), EDGE.get(server)
        bus.emit("info", f"Appel d'outil : {server}.{tool}", _summary(server, tool, args), src=agent,
                 nodes={cnode: "hot", "n-gw": "hot", "gi-introspect": "hot"}, edges={cedge: "live"}, siem=False)

        # 1. introspect the delegated identity the agent presents
        try:
            w.verify.introspect(body["subject_token"])
        except jwt.InvalidToken as exc:
            bus.emit("deny", "Jeton refusé à l'introspection", f"{exc}. Aucun appel ne passe.", src="Passerelle",
                     nodes={cnode: "deny", "gi-introspect": "deny", "n-gw": "hot"}, edges={cedge: "deny"})
            return {"ok": False, "erreur": str(exc)}

        # 2. OPA: is the tool registered at all?
        spec = TOOLS.get((server, tool))
        if spec is None or not w.policy.tool_registered(server, tool):
            return self._refuse(agent, "Outil non enregistré",
                                f"{server}.{tool} n'est pas dans le registre MCP. Aucun jeton, aucun identifiant.",
                                {cnode: "warn", "n-opa": "deny", target: "deny", "n-gw": "hot"},
                                {cedge: "deny", "e-opa-gw": "deny", **({tedge: "deny"} if tedge else {})})

        # 3. OPA: egress grant (checked before Verify)
        if server == "web":
            ok, why = w.policy.egress_allowed(agent, args.get("url", ""))
            if not ok:
                return self._refuse(agent, "Sortie refusée", f"{args.get('url')} : {why}.",
                                    {cnode: "warn", "n-opa": "deny", "n-web": "deny", "n-gw": "hot"},
                                    {cedge: "deny", "e-opa-gw": "deny", "e-gw-web": "deny"})

        # 4. no destructive SQL, whoever asks
        if server == "databricks" and w.policy.destructive_sql(args.get("sql", "")):
            bus.emit("deny", "SQL destructif bloqué", args["sql"], src="Passerelle",
                     nodes={cnode: "deny", "gi-tier": "deny", "n-gw": "hot"}, edges={cedge: "deny"})
            return {"ok": False, "erreur": "SQL destructif interdit"}

        # 5. RFC 8693 exchange with RFC 9396 RAR (and step-up if required)
        rtype, action, role, locs = spec
        rar = [{"type": rtype, "actions": [action], "locations": locs}]
        if server == "databricks" and action == "write" and args.get("params"):
            rar[0]["identifier"] = args["params"][-1]
        desc = body.get("description", f"{server}.{tool}")
        res = w.verify.exchange(body["subject_token"], body["actor_token"], rar, audience=server, description=desc)
        if res["result"] == "step_up":
            ch = w.verify.challenges[res["challenge"]]
            ch.done.wait(timeout=body.get("attente_max", 240))
            if ch.status != "approved":
                # after a dual revoke, keep the revocation on screen: this event doesn't repaint the map
                paint = {} if ch.status == "failed" else {cnode: "deny", "gi-stepup": "deny", "n-gw": "hot"}
                bus.emit("deny", "Écriture annulée : approbation non obtenue", "Aucun identifiant n'a été émis.",
                         src="Passerelle", nodes=paint, edges={} if not paint else {cedge: "deny"})
                return {"ok": False, "erreur": "approbation non obtenue"}
            try:
                res = w.verify.exchange(body["subject_token"], body["actor_token"], rar, audience=server,
                                        challenge_id=ch.id, description=desc)
            except jwt.InvalidToken as exc:
                res = {"result": "deny", "reason": str(exc), "check": "introspection"}
        if res["result"] != "ok":
            bus.emit("deny", f"Refusé par IBM Verify ({res.get('check', 'politique')})", res["reason"], src="IBM Verify",
                     nodes={cnode: "deny", "n-verify": "deny", "gi-exchange": "deny", "gi-tier": "deny", "n-gw": "hot"},
                     edges={cedge: "deny", "e-gw-verify": "deny"})
            return {"ok": False, "erreur": res["reason"]}
        claims = res["claims"]
        bus.emit("allow", "Jeton délégué émis (RFC 8693 + RAR)",
                 f"sub={claims['sub']} · act={_act(claims['act'])} · {rtype}:{action} · 5 min · jti {claims['jti']}"
                 + (" · approuvé par l'humaine" if claims.get("acr") else ""),
                 src="IBM Verify", token=claims,
                 nodes={"n-verify": "ok", "gi-tier": "ok", "gi-exchange": "ok", "n-gw": "hot", cnode: "hot"},
                 edges={"e-gw-verify": "live", cedge: "live"})

        # 6. Vault mints the downstream credential, bound to the jti
        auth = "SPIFFE (JWT-SVID)" if agent != AGENT_PARENT else "client Agent Identity"
        try:
            lease = w.vault.mint(res["token"], role, auth)
        except (PermissionError, jwt.InvalidToken) as exc:
            bus.emit("deny", "Vault refuse d'émettre l'identifiant", str(exc), src="Vault", nodes={"n-vault": "deny"})
            return {"ok": False, "erreur": str(exc)}

        # 7. call the real (simulated) system with a credential the agent never sees
        try:
            out = w.mcp.call(server, tool, args, lease["secret"], role)
        except (PermissionError, sqlite3.Error) as exc:
            w.vault.revoke(lease["id"])
            bus.emit("deny", f"{server} a refusé l'opération", str(exc), src=server, nodes={target: "deny"})
            return {"ok": False, "erreur": str(exc)}
        finally:
            if not w.vault.leases[lease["id"]]["revoque"]:
                w.vault.revoke(lease["id"])
        bus.emit("allow", f"{server}.{tool} : réussi", _result(server, out)
                 + f" Identifiant Vault {lease['id']} ({auth}) utilisé une fois puis révoqué.",
                 src=server, nodes={target: "ok", "n-vault": "ok", "n-siem": "hot", "gi-caep": "hot", "n-gw": "hot"},
                 edges={"e-gw-vault": "live", tedge: "ok", "e-gw-siem": "live"})
        return {"ok": True, "resultat": out}


def _act(act: dict) -> str:
    chain = [act["sub"].split("/")[-1]]
    while "act" in act:
        act = act["act"]
        chain.append(act["sub"])
    return " ← ".join(chain)


def _summary(server: str, tool: str, args: dict) -> str:
    if server == "databricks":
        return " ".join(args.get("sql", "").split())
    return ", ".join(f"{k}={v}" for k, v in args.items()) or "—"


def _result(server: str, out) -> str:
    if server == "jira":
        return f"Billet {out['cle']} : « {out['titre']} »."
    if server == "gitlab":
        return f"Fichier {out['fichier']} ({len(out['contenu'].splitlines())} lignes)."
    if server == "annuaire":
        return f"{out['displayName']} ∈ {', '.join(out['groups'])}."
    if server == "databricks":
        if "lignes" in out:
            return f"{len(out['lignes'])} ligne(s) lue(s) : " + "; ".join(
                f"{r.get('membre_id')} cote {r.get('cote')}" for r in out["lignes"][:3]) + "."
        return f"{out['lignes_modifiees']} ligne modifiée."
    return "Réponse reçue."
