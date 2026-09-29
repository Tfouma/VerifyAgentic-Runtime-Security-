import json
import threading
import time
import unittest
import urllib.request

from livedemo import jwt
from livedemo.core import AGENT_PARENT, AGENT_SUB, SPIFFE, USER, World
from livedemo.server import serve


class LiveDemoScenarios(unittest.TestCase):
    """Run every scenario end to end over HTTP, like the console does."""

    @classmethod
    def setUpClass(cls):
        cls.httpd = serve(0, 0.0)
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()
        cls.base = cls.httpd.app.base

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def post(self, path, body=None):
        req = urllib.request.Request(self.base + path, data=json.dumps(body or {}).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        return json.loads(urllib.request.urlopen(req).read())

    def get(self, path):
        return json.loads(urllib.request.urlopen(self.base + path).read())

    def run_scenario(self, name, codes=None):
        self.post("/api/reset")
        self.post("/api/login")
        self.assertTrue(self.post("/api/run", {"scenario": name})["ok"])
        deadline = time.time() + 30
        while time.time() < deadline:
            st = self.get("/api/state")
            if st["defi"]:
                for code in codes or [st["courriel"][-1]["code"]]:
                    self.post("/api/approve", {"code": code})
            if not st["en_cours"]:
                break
            time.sleep(0.02)
        return self.get("/api/state"), self.get("/api/events")

    def test_normal_path_writes_only_after_approval(self):
        st, evs = self.run_scenario("normal")
        row = next(r for r in st["table"] if r["membre_id"] == "M-20418")
        self.assertEqual(row["cote"], "ÉLEVÉE")
        self.assertEqual(row["approuve_par"], USER)
        titles = [e["title"] for e in evs]
        self.assertIn("Refusé par IBM Verify (RAR)", titles)       # subagent write refused
        self.assertIn("Approbation accordée", titles)
        self.assertTrue(all(l["revoque"] for l in st["baux"]))     # no credential left alive

    def test_poisoned_runbook_suspends_agent(self):
        st, evs = self.run_scenario("poison")
        parent = next(a for a in st["registre"] if a["id"] == AGENT_PARENT)
        self.assertEqual(parent["statut"], "suspendu")
        self.assertEqual(st["refus"], 3)
        self.assertFalse(any(l["role"] == "web_lecteur" for l in st["baux"]))  # nothing ever fetched
        self.assertEqual(evs[-2]["detail"], "agent suspendu, refusé par la politique")

    def test_failed_approvals_revoke_both_sessions(self):
        st, evs = self.run_scenario("approbations", codes=["000000", "111111", "222222"])
        self.assertIsNone(st["session"])
        self.assertEqual(st["table"][0]["cote"], "MOYENNE")
        self.assertIn("Révocation double : IBM Verify + Entra ID", [e["title"] for e in evs])

    def test_unregistered_payment_tool_refused(self):
        st, evs = self.run_scenario("outil")
        self.assertTrue(any(e["title"].startswith("Outil non enregistré") for e in evs))
        self.assertEqual(st["baux"], [])


class Mechanics(unittest.TestCase):
    def setUp(self):
        self.w = World()
        self.user = self.w.entra.login()

    def test_tampered_token_rejected(self):
        head, body, sig = self.user.split(".")
        forged = f"{head}.{body[:-2]}xx.{sig}"
        with self.assertRaises(jwt.InvalidToken):
            self.w.verify.introspect(forged)

    def test_subagent_cannot_exceed_delegation(self):
        d = self.w.verify.delegate(self.user, self.w.attest(AGENT_PARENT), SPIFFE[AGENT_SUB],
                                   [{"type": "scim", "actions": ["read"], "locations": ["Users"]}])
        res = self.w.verify.exchange(d["token"], self.w.attest(AGENT_SUB),
                                     [{"type": "databricks", "actions": ["read"], "locations": ["x"]}], audience="databricks")
        self.assertEqual(res["result"], "deny")   # databricks read is in its grants but was not delegated

    def test_reader_credential_cannot_write(self):
        res = self.w.verify.exchange(self.user, self.w.attest(AGENT_PARENT),
                                     [{"type": "databricks", "actions": ["read"], "locations": ["x"]}], audience="databricks")
        lease = self.w.vault.mint(res["token"], "dbx_lecteur", "test")
        with self.assertRaises(Exception):
            self.w.mcp.call("databricks", "query", {"sql": "UPDATE kyc_cote_risque_membre SET cote = 'X'"},
                            lease["secret"], "dbx_lecteur")
        self.assertEqual(self.w.mcp.table()[0]["cote"], "MOYENNE")

    def test_expired_credential_refused(self):
        res = self.w.verify.exchange(self.user, self.w.attest(AGENT_PARENT),
                                     [{"type": "jira", "actions": ["read"], "locations": ["FIN"]}], audience="jira")
        lease = self.w.vault.mint(res["token"], "jira_lecteur", "test")
        self.w.vault.leases[lease["id"]]["expire_a"] = time.time() - 1
        with self.assertRaises(PermissionError):
            self.w.mcp.call("jira", "read_issue", {}, lease["secret"], "jira_lecteur")


if __name__ == "__main__":
    unittest.main()
