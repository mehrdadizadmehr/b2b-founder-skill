import json
import os
import shutil
import tempfile
import unittest

from _load import load, example

cm = load("b2b-committee", "committee")
CUSTOMER = example("b2b-committee", "customer.example.json")
PITCH = example("b2b-committee", "pitch.example.md")
ROLES = ["Procurement manager", "Design or production engineer", "Quality manager", "Owner or finance lead"]


def answer(card, outcome="buy", **over):
    a = {"id": card["id"], "outcome": outcome, "annual_value": 0 if outcome == "pass" else 50000,
         "sales_cycle_months": 0 if outcome == "pass" else 3, "reason_code": "price", "reason": "Because.",
         "blocker_role": "" if outcome == "buy" else ROLES[0], "objection": "o", "would_change_my_mind": "references",
         "committee": {r: "for" for r in ROLES}, "price_acceptable": 800, "price_walk_away": 950, "discount_expected_pct": 5}
    a.update(over)
    return a


class Dealing(unittest.TestCase):
    def setUp(self):
        with open(CUSTOMER, encoding="utf-8") as fh:
            self.c = json.load(fh)

    def test_same_seed_same_cards(self):
        self.assertEqual(cm.deal(self.c, 40, 7), cm.deal(self.c, 40, 7))
        self.assertNotEqual(cm.deal(self.c, 40, 7), cm.deal(self.c, 40, 8))

    def test_segment_quota_follows_shares(self):
        cards = cm.deal(self.c, 40, 7)
        n = sum(1 for c in cards if c["segment"].startswith("Contract electronics"))
        self.assertEqual(n, 16)  # 0.4 of 40

    def test_card_fields(self):
        c = cm.deal(self.c, 5, 1)[0]
        for k in ("id", "segment", "employees", "annual_spend", "situation", "objection", "trigger", "region"):
            self.assertIn(k, c)
        self.assertTrue(c["id"].startswith("A"))

    def test_validation(self):
        bad = dict(self.c)
        bad["roles"] = [{"name": "only one", "cares": "x"}]
        with self.assertRaises(cm.PanelError):
            cm.deal(bad, 5, 1)
        del bad["roles"]
        with self.assertRaises(cm.PanelError):
            cm.deal(bad, 5, 1)


class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.d = os.path.join(self.tmp, "committee")
        self.cards = cm.init(self.d, CUSTOMER, PITCH, n=10, seed=3)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_briefs_contain_committee_and_pitch(self):
        waves = cm.write_briefs(self.d, wave=4)
        self.assertEqual([len(w) for w in waves], [4, 4, 2])
        with open(waves[0][0][1], encoding="utf-8") as fh:
            text = fh.read()
        for r in ROLES:
            self.assertIn(r, text)
        self.assertIn("12,000 line items", text)
        self.assertIn('"outcome": "buy" or "pilot" or "pass"', text)
        self.assertIn(os.path.abspath(os.path.join(self.d, "answers", "A001.json")), text)

    def _write(self, card, **kw):
        cm._write_json(os.path.join(self.d, "answers", card["id"] + ".json"), answer(card, **kw))

    def test_check_and_tally(self):
        outcomes = ["buy", "buy", "buy", "pilot", "pilot", "pass", "pass", "pass", "pass"]
        for card, o in zip(self.cards, outcomes):
            self._write(card, outcome=o)
        probs = cm.check(self.d)
        self.assertEqual(probs, [("A010", "missing")])
        res = cm.tally(self.d)
        self.assertEqual((res["buys"], res["pilots"], res["passes"], res["answered"]), (3, 2, 4, 9))
        self.assertAlmostEqual(res["win_rate"], 3 / 9)
        self.assertAlmostEqual(res["engaged_rate"], 5 / 9)
        self.assertEqual(res["blockers"], [(ROLES[0], 6)])
        self.assertEqual(res["stance"][ROLES[1]]["for"], 9)
        self.assertEqual(res["price_acceptable_median"], 800)
        text = cm.results_md(res)
        self.assertIn("3 buy · 2 pilot · 4 pass", text)
        self.assertIn("Who blocks", text)
        self.assertIn("A010 (missing)", text)

    def test_invalid_answers_are_rejected(self):
        c = self.cards[0]
        p = os.path.join(self.d, "answers", c["id"] + ".json")
        cm._write_json(p, answer(c, outcome="maybe"))
        self.assertIn("outcome", cm._answer_ok(p, c["id"]))
        cm._write_json(p, answer(c, reason_code="vibes"))
        self.assertIn("reason_code", cm._answer_ok(p, c["id"]))
        cm._write_json(p, answer(c, annual_value="lots"))
        self.assertIn("annual_value", cm._answer_ok(p, c["id"]))
        cm._write_json(p, answer(c, id="A999"))
        self.assertIn("id is", cm._answer_ok(p, c["id"]))

    def test_save_from_reply_text(self):
        c = self.cards[0]
        reply = "Here is my answer:\n" + json.dumps(answer(c)) + "\nDone."
        cm.save(self.d, c["id"], reply)
        self.assertIsNone(cm._answer_ok(os.path.join(self.d, "answers", c["id"] + ".json"), c["id"]))
        with self.assertRaises(cm.PanelError):
            cm.save(self.d, c["id"], json.dumps(answer(c, outcome="maybe")))
        self.assertFalse(os.path.exists(os.path.join(self.d, "answers", c["id"] + ".json")))

    def test_prompts_only_for_missing(self):
        for card in self.cards[:7]:
            self._write(card)
        waves = cm.write_briefs(self.d)
        self.assertEqual(sum(len(w) for w in waves), 3)

    def test_tally_without_answers_errors(self):
        with self.assertRaises(cm.PanelError):
            cm.tally(self.d)


if __name__ == "__main__":
    unittest.main()
