import json
import math
import unittest

from _load import load, example

ue = load("b2b-cfo", "b2b_economics")


def spec(name):
    with open(example("b2b-cfo", name), encoding="utf-8") as fh:
        return json.load(fh)


class Distribution(unittest.TestCase):
    def setUp(self):
        self.s = spec("example-distribution.json")
        self.r = ue.analyse(self.s)

    def test_contribution_from_gross_margin(self):
        self.assertAlmostEqual(self.r["contribution"], 850 * 0.22)
        self.assertAlmostEqual(self.r["contribution_pct"], 0.22)

    def test_fixed_includes_sales_marketing(self):
        self.assertAlmostEqual(self.r["fixed"], 8100 + 6500)
        self.assertAlmostEqual(self.r["sales_marketing"], 6500)

    def test_breakeven(self):
        self.assertAlmostEqual(self.r["breakeven_per_month"], 14600 / 187.0)

    def test_working_capital(self):
        # receivables 45d on revenue, inventory 75d on COGS, payables 30d on COGS
        rev_day = 180 * 850 / 30.0
        cogs_day = 180 * 663 / 30.0
        self.assertAlmostEqual(self.r["working_capital_at_plan"], rev_day * 45 + cogs_day * 75 - cogs_day * 30)

    def test_cac_ltv(self):
        self.assertAlmostEqual(self.r["cac"], 6500 / 12.0)
        units_per_cust_year = 180 / (12 * 3.0)
        self.assertAlmostEqual(self.r["ltv"], units_per_cust_year * 187 * 3)
        self.assertGreater(self.r["ltv_cac"], 3)

    def test_year1_is_sum_of_months(self):
        self.assertEqual(len(self.r["months"]), 12)
        self.assertAlmostEqual(self.r["year1_profit"], sum(m["operating_profit"] for m in self.r["months"]))

    def test_cash_needed_includes_working_capital(self):
        self.assertGreater(self.r["cash_needed"], self.r["startup"])
        self.assertTrue(any("Working capital" in f for f in self.r["flags"]))

    def test_dso_what_if_needs_more_cash(self):
        slow = ue.analyse(self.s, dso=75)
        self.assertGreater(slow["cash_needed"], self.r["cash_needed"])
        self.assertAlmostEqual(slow["year1_profit"], self.r["year1_profit"])

    def test_volume_what_if_scales_ramp_and_accounts(self):
        w = ue.analyse(self.s, volume=0.5)
        self.assertAlmostEqual(w["plan_per_month"], 90)
        self.assertAlmostEqual(w["months"][0]["units"], 7.5)
        self.assertAlmostEqual(w["cac"], 6500 / 6.0)

    def test_report_mentions_model_and_cac(self):
        text = ue.report(self.r, ue.what_ifs(self.s))
        self.assertIn("distribution model", text)
        self.assertIn("Cost to win an account (CAC)", text)
        self.assertIn("Customers pay 30 days later", text)


class Deal(unittest.TestCase):
    def test_variable_list_and_capacity(self):
        r = ue.analyse(spec("example-deal.json"))
        self.assertAlmostEqual(r["contribution"], 48000 - 35500)
        self.assertEqual(r["capacity_per_month"], 2)
        self.assertLess(r["year1_profit"], 0)
        self.assertIn("Year 1 makes an operating loss.", r["flags"])

    def test_cost_factor(self):
        s = spec("example-deal.json")
        base, up = ue.analyse(s), ue.analyse(s, cost_factor=1.15)
        self.assertAlmostEqual(up["variable_cost"], base["variable_cost"] * 1.15)


class Manufacturing(unittest.TestCase):
    def test_runs_and_flags_capacity_when_breakeven_above_it(self):
        s = spec("example-manufacturing.json")
        r = ue.analyse(s)
        self.assertAlmostEqual(r["contribution"], 1000)
        s["capacity_per_month"] = 20
        r2 = ue.analyse(s)
        self.assertTrue(any("above capacity" in f for f in r2["flags"]))


class Errors(unittest.TestCase):
    def test_missing_model(self):
        with self.assertRaises(ue.NumbersError):
            ue.analyse({"price": 1, "gross_margin_pct": 0.5, "plan_per_month": 1})

    def test_missing_margin_and_variable(self):
        with self.assertRaises(ue.NumbersError):
            ue.analyse({"model": "deal", "price": 1, "plan_per_month": 1})

    def test_bad_ramp_length(self):
        with self.assertRaises(ue.NumbersError):
            ue.analyse({"model": "deal", "price": 10, "gross_margin_pct": 0.5, "plan_per_month": 1, "ramp_per_month": [1, 2]})

    def test_no_sales_cost_means_no_cac(self):
        r = ue.analyse({"model": "deal", "price": 10, "gross_margin_pct": 0.5, "plan_per_month": 1})
        self.assertIsNone(r["cac"])
        self.assertIsNone(r["ltv_cac"])

    def test_negative_contribution_is_infinite_breakeven(self):
        r = ue.analyse({"model": "deal", "price": 10, "variable": [{"label": "x", "cost": 12}], "plan_per_month": 1})
        self.assertTrue(math.isinf(r["breakeven_per_month"]))
        self.assertTrue(any("LOSES" in f for f in r["flags"]))


if __name__ == "__main__":
    unittest.main()
