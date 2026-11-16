import csv
import json
import os
import shutil
import tempfile
import unittest

from _load import load

pr = load("b2b-pricing", "pricing")


def raw(n=10):
    """Answer files as the committee panel writes them."""
    return [{"id": "A%03d" % i, "price_acceptable": 700 + i * 10, "price_walk_away": 900 + i * 10,
             "discount_expected_pct": 10, "outcome": "buy"} for i in range(n)]


def rows(n=10):
    """The same rows after read_rows normalised them."""
    return [{"id": r["id"], "acceptable": r["price_acceptable"], "walk_away": r["price_walk_away"],
             "discount": r["discount_expected_pct"], "outcome": r["outcome"]} for r in raw(n)]


class Analyse(unittest.TestCase):
    def test_quartiles_and_curve(self):
        res = pr.analyse(rows(), price=850, floor=780, keep=0.6)
        self.assertEqual(res["n"], 10)
        self.assertAlmostEqual(res["acceptable"]["median"], 745)
        self.assertAlmostEqual(res["walk_away"]["median"], 945)
        # 60% still in: walk-away >= p for at least 6 of 10 -> highest such p is 940
        self.assertEqual(res["ceiling"], 940)
        self.assertEqual(res["band"], (780, 940))
        self.assertAlmostEqual(res["list_price_for_median"], 745 / 0.9)
        self.assertEqual(res["at_price"]["still_in"], 1.0)
        self.assertEqual(res["at_price"]["fair"], 0.0)
        self.assertFalse(res["at_price"]["below_floor"])

    def test_floor_above_ceiling_is_reported(self):
        res = pr.analyse(rows(), price=1000, floor=990)
        text = pr.report(res)
        self.assertIn("The floor is above the ceiling", text)

    def test_swapped_answers_are_fixed(self):
        tmp = tempfile.mkdtemp()
        try:
            d = os.path.join(tmp, "answers")
            os.makedirs(d)
            for r in raw(6):
                r["price_acceptable"], r["price_walk_away"] = r["price_walk_away"], r["price_acceptable"]
                with open(os.path.join(d, r["id"] + ".json"), "w") as fh:
                    json.dump(r, fh)
            got = pr.read_rows(d)
            self.assertTrue(all(g["acceptable"] <= g["walk_away"] for g in got))
        finally:
            shutil.rmtree(tmp)

    def test_csv_input_and_too_few_rows(self):
        tmp = tempfile.mkdtemp()
        try:
            p = os.path.join(tmp, "q.csv")
            with open(p, "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=["price_acceptable", "price_walk_away", "discount_expected_pct"])
                w.writeheader()
                for r in raw(5):
                    w.writerow({k: r[k] for k in w.fieldnames})
            self.assertEqual(len(pr.read_rows(p)), 5)
            with open(p, "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=["price_acceptable", "price_walk_away"])
                w.writeheader()
                w.writerow({"price_acceptable": 1, "price_walk_away": 2})
            with self.assertRaises(pr.PricingError):
                pr.read_rows(p)
        finally:
            shutil.rmtree(tmp)

    def test_report_with_competitors(self):
        res = pr.analyse(rows(), price=850)
        text = pr.report(res, [{"name": "X", "price": 900, "note": "list"}])
        self.assertIn("| X | $900.00 | list |", text)
        self.assertIn("your price", text)


if __name__ == "__main__":
    unittest.main()
