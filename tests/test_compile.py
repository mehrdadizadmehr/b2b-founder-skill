import json
import os
import shutil
import tempfile
import unittest

from _load import load, example

cp = load("b2b-plan", "compile")


def numbers():
    with open(example("b2b-cfo", "example-distribution.json"), encoding="utf-8") as fh:
        return json.load(fh)


class Verdict(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.d = os.path.join(self.tmp, "b2b")
        os.makedirs(os.path.join(self.d, "committee"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _numbers(self, **over):
        n = numbers()
        n.update(over)
        with open(os.path.join(self.d, "numbers.json"), "w") as fh:
            json.dump(n, fh)

    def _panel(self, buys, pilots, passes):
        res = {"buys": buys, "pilots": pilots, "passes": passes, "answered": buys + pilots + passes,
               "win_rate": buys / float(buys + pilots + passes)}
        with open(os.path.join(self.d, "committee", "results.json"), "w") as fh:
            json.dump(res, fh)

    def test_incomplete_without_numbers(self):
        v, checks, n, p = cp.verdict(self.d)
        self.assertEqual(v, "Incomplete")
        self.assertEqual(checks, [])
        _, text = cp.compile_plan(self.d)
        self.assertIn("Run /b2b-cfo", text)

    def test_viable(self):
        self._numbers()
        self._panel(12, 8, 20)
        v, checks, _, _ = cp.verdict(self.d)
        self.assertEqual(v, "Viable", checks)
        self.assertEqual(len(checks), 5)  # contribution, year1, ltv/cac, payback, panel (no capacity given)
        self.assertTrue(all(ok for ok, _ in checks))

    def test_not_yet_on_low_win_rate(self):
        self._numbers()
        self._panel(3, 10, 27)
        v, checks, _, _ = cp.verdict(self.d)
        self.assertEqual(v, "Not yet")
        self.assertFalse(checks[-1][0])
        v2, _, _, _ = cp.verdict(self.d, min_win_rate=0.05)
        self.assertEqual(v2, "Viable")

    def test_not_yet_on_ltv_cac(self):
        self._numbers(sales_marketing_monthly=[{"label": "big team", "cost": 60000}])
        v, checks, _, _ = cp.verdict(self.d)
        self.assertEqual(v, "Not yet")
        self.assertTrue(any("returns" in t and not ok for ok, t in checks))

    def test_capacity_check_when_given(self):
        self._numbers(capacity_per_month=50)
        v, checks, _, _ = cp.verdict(self.d)
        self.assertEqual(v, "Not yet")
        self.assertTrue(any("capacity" in t and not ok for ok, t in checks))

    def test_plan_lists_missing_sections(self):
        self._numbers()
        with open(os.path.join(self.d, "idea.md"), "w") as fh:
            fh.write("# Parts Co\n\n- What it is: parts.\n")
        with open(os.path.join(self.d, "gtm.md"), "w") as fh:
            fh.write("# GTM\n\n## Beachhead\n\nSmall assembly shops.\n")
        v, text = cp.compile_plan(self.d)
        self.assertTrue(text.startswith("# Parts Co · Business plan"))
        self.assertIn("## Go-to-market", text)
        self.assertIn("### Beachhead", text)  # demoted
        self.assertIn("- Brand: run /b2b-brand", text)
        self.assertIn("Working capital at plan", text)


if __name__ == "__main__":
    unittest.main()
