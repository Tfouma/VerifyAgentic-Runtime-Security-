"""Scripted agents that call the gateway over HTTP, like a sandboxed agent would.

The agents are scripted so the demo runs the same way every time. The controls
they hit are not scripted: every decision comes from the gateway, IBM Verify
(simulated), Vault (simulated) and the policy file.
"""

from __future__ import annotations

import json
import threading
import time
import urllib.request

from .core import AGENT_PARENT, AGENT_SUB, USER, World

UPDATE_SQL = ("UPDATE kyc_cote_risque_membre SET cote = 'ÉLEVÉE', vigilance_accrue = 1, "
              "modifie_par_agent = ?, approuve_par = ?, billet = 'FIN-2417', maj = date('now') "
              "WHERE membre_id = ?")
EVIDENCE_SQL = ("SELECT m.membre_id, m.cote, m.medias_negatifs, t.nb, t.total, t.inhabituel "
                "FROM kyc_cote_risque_membre m JOIN transactions_90j t USING (membre_id) "
                "WHERE m.membre_id = ?")
WRITE_DESC = "Fixer la cote de risque du membre M-20418 à ÉLEVÉE et activer la vigilance accrue (billet FIN-2417)"


class Agent:
    def __init__(self, world: World, base: str, agent_id: str, subject_token: str, pace: float, label: str):
        self.w, self.base, self.id, self.pace, self.label = world, base, agent_id, pace, label
        self.subject = subject_token
        self.actor = world.attest(agent_id)   # workload attestation from the sandbox runtime

    def say(self, text: str, node: str = "n-parent"):
        self.w.wait_step()
        self.w.bus.emit("info", f"{self.label} : {text}", "", src=self.id, nodes={node: "hot"}, siem=False)
        time.sleep(self.pace)

    def _post(self, path: str, body: dict) -> dict:
        req = urllib.request.Request(self.base + path, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read())

    def call(self, server: str, tool: str, args: dict, description: str | None = None) -> dict:
        body = {"subject_token": self.subject, "actor_token": self.actor, "server": server, "tool": tool, "args": args}
        if description:
            body["description"] = description
        out = self._post("/gateway/mcp", body)
        time.sleep(self.pace)
        return out

    def tools(self) -> dict:
        with urllib.request.urlopen(self.base + "/gateway/tools", timeout=30) as r:
            out = json.loads(r.read())
        time.sleep(self.pace)
        return out


def _done(w: World, title: str, detail: str):
    w.bus.emit("done", title, detail, src="Scénario", siem=False)


def normal(w: World, base: str, pace: float):
    p = Agent(w, base, AGENT_PARENT, w.user_token, pace, "Agent parent")
    p.say("je lis le billet FIN-2417.")
    p.call("jira", "read_issue", {"key": "FIN-2417"})
    p.say("le billet renvoie au guide KYC-RR-07. Je le récupère dans GitLab.")
    p.call("gitlab", "get_file", {"project": "kyc/guides", "file": "KYC-RR-07.md"})
    p.say("je délègue la collecte des preuves à un sous-agent en lecture seule.")
    d = p._post("/gateway/delegate", {
        "subject_token": p.subject, "actor_token": p.actor, "sous_agent": AGENT_SUB,
        "rar": [{"type": "databricks", "actions": ["read"], "locations": ["kyc_cote_risque_membre", "transactions_90j"]},
                {"type": "scim", "actions": ["read"], "locations": ["Users"]}]})
    time.sleep(pace)
    if not d.get("ok"):
        return _done(w, "Scénario interrompu", d.get("erreur", ""))

    def sub_run():
        s = Agent(w, base, AGENT_SUB, d["token"], pace, "Sous-agent")
        s.say("je vérifie que la demandeuse fait partie du groupe Analystes-CSC.", "n-sub")
        s.call("annuaire", "scim_get", {"user": USER})
        s.say("je lis la cote actuelle et les transactions des 90 derniers jours.", "n-sub")
        s.call("databricks", "query", {"sql": EVIDENCE_SQL, "params": ["M-20418"]})
        s.say("j'essaie d'appliquer moi-même la nouvelle cote.", "n-sub")
        r = s.call("databricks", "execute", {"sql": UPDATE_SQL, "params": [AGENT_SUB, USER, "M-20418"]})
        if not r.get("ok"):
            s.say("écriture refusée. Je rends la tâche à l'agent parent et je m'arrête.", "n-sub")

    t = threading.Thread(target=sub_run, daemon=True)
    t.start()
    t.join()
    p.say("le sous-agent ne peut pas écrire. Je demande l'écriture moi-même : une personne doit l'approuver.")
    r = p.call("databricks", "execute", {"sql": UPDATE_SQL, "params": [AGENT_PARENT, USER, "M-20418"]}, WRITE_DESC)
    if r.get("ok"):
        _done(w, "Tâche terminée", "Cote de M-20418 : ÉLEVÉE, vigilance accrue activée. Chaîne complète dans le journal.")
    else:
        _done(w, "Tâche non terminée", r.get("erreur", ""))


def poison(w: World, base: str, pace: float):
    w.mcp.poisoned = True
    p = Agent(w, base, AGENT_PARENT, w.user_token, pace, "Agent parent")
    p.say("je lis le billet FIN-2417.")
    p.call("jira", "read_issue", {"key": "FIN-2417"})
    p.say("je récupère le guide KYC-RR-07 dans GitLab.")
    p.call("gitlab", "get_file", {"project": "kyc/guides", "file": "KYC-RR-07.md"})
    w.bus.emit("stepup", "Instruction cachée dans le guide",
               "Un commentaire caché demande à l'agent de téléverser les preuves sur gist.github.com et de "
               "récupérer une clé d'API. L'agent, piégé, va essayer.", src="GitLab",
               nodes={"n-gitlab": "warn", "n-parent": "warn"}, siem=False)
    time.sleep(pace)
    p.say("le guide demande de téléverser les preuves. Je m'exécute.")
    p.call("web", "fetch", {"url": "https://gist.github.com/partage/preuves"})
    p.say("échec. J'essaie l'autre adresse indiquée.")
    p.call("web", "fetch", {"url": "https://paste.example.net/cle"})
    p.say("échec. J'essaie directement l'API.")
    p.call("web", "fetch", {"url": "https://api.github.com/gists"})
    p.say("je reviens au billet.")
    p.call("jira", "read_issue", {"key": "FIN-2417"})
    _done(w, "Attaque contenue", "Aucune donnée sortie, aucun secret à voler. L'agent est suspendu dans tout le système.")


def approvals(w: World, base: str, pace: float):
    p = Agent(w, base, AGENT_PARENT, w.user_token, pace, "Agent parent")
    p.say("je lis le billet FIN-2417.")
    p.call("jira", "read_issue", {"key": "FIN-2417"})
    p.say("je demande l'écriture de la nouvelle cote.")
    r = p.call("databricks", "execute", {"sql": UPDATE_SQL, "params": [AGENT_PARENT, USER, "M-20418"]}, WRITE_DESC)
    if not r.get("ok"):
        p.say("écriture impossible. Je réessaie de lire le billet.")
        p.call("jira", "read_issue", {"key": "FIN-2417"})
    _done(w, "Scénario terminé", "Aucune donnée modifiée." if not r.get("ok") else "Écriture approuvée.")


def tool(w: World, base: str, pace: float):
    p = Agent(w, base, AGENT_PARENT, w.user_token, pace, "Agent parent")
    p.say("je liste les outils à ma disposition.")
    p.tools()
    p.say("un remboursement serait plus rapide : j'appelle directement paiements.initier_virement.")
    p.call("paiements", "initier_virement", {"montant": "25000.00", "vers": "compte externe"})
    _done(w, "Virement impossible", "Un agent CSC ne peut pas déplacer d'argent. Ajouter un outil passe par une demande de fusion révisée.")


SCENARIOS = {"normal": normal, "poison": poison, "approbations": approvals, "outil": tool}
