import unittest

from demo.scenario import run


class ScenarioTest(unittest.TestCase):
    def test_controls_off_breach_succeeds(self):
        r = run(False)
        self.assertEqual(r["blocked"], 0)
        self.assertEqual(r["snapshot"]["moved"], 430_000)
        self.assertEqual(r["snapshot"]["records_exposed"], 5)

    def test_controls_on_everything_blocked(self):
        r = run(True)
        self.assertEqual(r["allowed"], 0)
        self.assertEqual(r["snapshot"]["moved"], 0)
        # A blocked read must not touch a single customer record.
        self.assertEqual(r["snapshot"]["records_exposed"], 0)

    def test_ledger_is_conserved(self):
        for enabled in (False, True):
            snap = run(enabled)["snapshot"]
            total = sum(a["balance"] for a in snap["accounts"])
            seed = sum(a["seed"] for a in snap["accounts"])
            self.assertAlmostEqual(total, seed)


if __name__ == "__main__":
    unittest.main()
