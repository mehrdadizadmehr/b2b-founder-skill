#!/usr/bin/env python3
"""B2B unit economics for b2b-cfo. Standard library only, no network.

Takes one JSON file describing the business and prints the numbers a CFO checks
before a sales team is hired or stock is bought: what one unit earns, the
margin at the volume you plan, the break-even volume, year 1 month by month
with the working capital B2B customers tie up, the cash needed, the cost of
winning a customer (CAC), what a customer is worth (LTV) and how long it takes
to earn the acquisition cost back.

    python3 b2b_economics.py b2b/numbers.json
    python3 b2b_economics.py b2b/numbers.json --out b2b/cfo.md
    python3 b2b_economics.py b2b/numbers.json --json
    python3 b2b_economics.py b2b/numbers.json --price 90 --volume 0.8 --dso 90

The input (see the three example files in this folder):

    business            name, for the report
    currency            symbol for the report (default "$")
    model               "deal" (projects, contracts, SaaS: one unit = one deal or
                        contract-year), "distribution" (reselling: one unit = one
                        order), or "manufacturing" (one unit = one tonne, batch, piece)
    unit                what one unit is called: "project", "order", "tonne"
    price               revenue per unit, before tax
    gross_margin_pct    0.35 = 35% of price is left after the direct cost of the unit
      OR variable       [{label, cost}] the direct cost of ONE unit (materials,
                        freight, duties, subcontractors, commissions, card fees)
    fixed_monthly       [{label, cost}] paid every month whatever you sell: rent,
                        salaries (not sales), software, insurance, warehouse
    sales_marketing_monthly
                        [{label, cost}] the monthly cost of winning customers: sales
                        salaries and commissions, trade shows, ads, travel. Counted as
                        fixed cost too; kept apart so CAC can be computed.
    startup             [{label, cost}] one-off spend before the first sale: deposits,
                        machines, certifications, first inventory, website, legal
    plan_per_month      units a month once up and running
    ramp_per_month      12 numbers: units in each month of year 1 (default: plan)
    capacity_per_month  the most units a month you can deliver (optional)
    receivable_days     days customers take to pay (DSO). B2B is rarely 0.
    inventory_days      days of stock you hold (DIO). 0 for pure services.
    payable_days        days you take to pay suppliers (DPO).
    new_customers_per_month
                        how many NEW accounts you win a month at plan (optional;
                        default: every unit is a new account). Needed for CAC.
    customer_years      how many years a won account keeps buying (default 1).
                        Needed for LTV.

Every number in the report comes from that file. Nothing is looked up or
guessed. If a field is missing the tool says so instead of filling it in.

--price, --volume and --dso run a what-if without editing the file: --price
replaces the price, --volume scales every volume (0.8 = 20 percent fewer
units), --dso replaces receivable_days.
"""

import argparse
import json
import math
import sys

MODELS = ("deal", "distribution", "manufacturing")


class NumbersError(Exception):
    pass


def _sum(items, field):
    total = 0.0
    for i, it in enumerate(items or []):
        if not isinstance(it, dict) or "cost" not in it:
            raise NumbersError("%s[%d] needs a 'cost'" % (field, i))
        try:
            total += float(it["cost"])
        except (TypeError, ValueError):
            raise NumbersError("%s[%d].cost is not a number: %r" % (field, i, it["cost"]))
    return total


def _num(spec, key, default=None, required=False):
    if key not in spec or spec[key] is None:
        if required:
            raise NumbersError("numbers.json needs '%s'" % key)
        return default
    try:
        return float(spec[key])
    except (TypeError, ValueError):
        raise NumbersError("'%s' is not a number: %r" % (key, spec[key]))


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise NumbersError("no such file: %s" % path)
    except json.JSONDecodeError as e:
        raise NumbersError("%s is not valid JSON: %s" % (path, e))


def analyse(spec, price=None, volume=1.0, dso=None, cost_factor=1.0):
    """Return a dict of every number in the report. Pure function, easy to test."""
    model = spec.get("model")
    if model not in MODELS:
        raise NumbersError("'model' must be one of %s" % ", ".join(MODELS))
    unit = spec.get("unit") or {"deal": "deal", "distribution": "order", "manufacturing": "unit"}[model]
    p = float(price) if price is not None else _num(spec, "price", required=True)
    if p <= 0:
        raise NumbersError("price must be above zero")
    if "variable" in spec and spec["variable"] is not None:
        var_cost = _sum(spec["variable"], "variable") * cost_factor
        margin_given = False
    elif "gross_margin_pct" in spec:
        m = _num(spec, "gross_margin_pct")
        if not (0 <= m < 1):
            raise NumbersError("gross_margin_pct is a fraction between 0 and 1, e.g. 0.35")
        base_price = _num(spec, "price", required=True)
        var_cost = base_price * (1 - m) * cost_factor
        margin_given = True
    else:
        raise NumbersError("give 'gross_margin_pct' or a 'variable' cost list")
    contribution = p - var_cost
    fixed_core = _sum(spec.get("fixed_monthly"), "fixed_monthly")
    sm = _sum(spec.get("sales_marketing_monthly"), "sales_marketing_monthly")
    fixed = fixed_core + sm
    startup = _sum(spec.get("startup"), "startup")
    plan = _num(spec, "plan_per_month", required=True) * volume
    ramp = spec.get("ramp_per_month")
    if ramp is None:
        ramp = [plan / volume] * 12
    if len(ramp) != 12:
        raise NumbersError("ramp_per_month needs exactly 12 numbers (one per month of year 1)")
    try:
        ramp = [float(v) * volume for v in ramp]
    except (TypeError, ValueError):
        raise NumbersError("ramp_per_month has a value that is not a number")
    capacity = _num(spec, "capacity_per_month")
    rec_days = float(dso) if dso is not None else _num(spec, "receivable_days", 0.0)
    inv_days = _num(spec, "inventory_days", 0.0)
    pay_days = _num(spec, "payable_days", 0.0)
    new_cust = _num(spec, "new_customers_per_month")
    cust_years = _num(spec, "customer_years", 1.0)

    breakeven = (fixed / contribution) if contribution > 0 else math.inf
    rev_plan = plan * p
    gp_plan = plan * contribution
    op_plan = gp_plan - fixed
    margin_at_plan = (op_plan / rev_plan) if rev_plan else 0.0

    def working_capital(units):
        rev_day = units * p / 30.0
        cogs_day = units * var_cost / 30.0
        return rev_day * rec_days + cogs_day * inv_days - cogs_day * pay_days

    months, cum, wc_prev, low, payback = [], -startup, 0.0, -startup, None
    for i, u in enumerate(ramp, 1):
        rev, gp = u * p, u * contribution
        op = gp - fixed
        wc = working_capital(u)
        cash = op - (wc - wc_prev)
        wc_prev = wc
        cum += cash
        low = min(low, cum)
        if payback is None and cum >= 0:
            payback = i
        months.append({"month": i, "units": u, "revenue": rev, "gross_profit": gp, "fixed": fixed,
                       "operating_profit": op, "working_capital": wc, "cash_flow": cash, "cumulative": cum})
    year1_profit = sum(m["operating_profit"] for m in months)
    year1_revenue = sum(m["revenue"] for m in months)

    # customers
    cac = ltv = cac_payback = units_per_cust_year = gp_per_cust_year = None
    if sm > 0:
        # new accounts a month at plan; fewer sales (--volume) also means fewer new accounts
        n_new = (new_cust * volume) if new_cust else plan
        if n_new > 0 and cust_years > 0:
            cac = sm / n_new
            # steady state: active accounts = n_new * 12 * customer_years, so one account
            # buys plan / (n_new * customer_years) units a year
            units_per_cust_year = plan / (n_new * cust_years)
            gp_per_cust_year = units_per_cust_year * contribution
            ltv = gp_per_cust_year * cust_years
            cac_payback = (cac / (gp_per_cust_year / 12.0)) if gp_per_cust_year > 0 else math.inf

    wc_plan = working_capital(plan)
    flags = []
    if contribution <= 0:
        flags.append("Each %s LOSES money before fixed costs: the price does not cover its direct cost." % unit)
    if capacity is not None and not math.isinf(breakeven) and breakeven > capacity:
        flags.append("Break-even (%s %ss a month) is above capacity (%s): this cannot break even as planned."
                     % ("{:,.0f}".format(math.ceil(breakeven)), unit, "{:,.0f}".format(capacity)))
    if year1_profit < 0:
        flags.append("Year 1 makes an operating loss.")
    if payback is None:
        flags.append("The startup spend and working capital are not earned back within year 1.")
    if cac is not None and ltv is not None and cac > 0 and ltv / cac < 3:
        flags.append("LTV/CAC is %.1f: a won account returns less than 3x what it costs to win." % (ltv / cac))
    if cac_payback is not None and cac_payback > 18:
        flags.append("CAC payback is %.0f months: too long to fund from operations." % cac_payback if not math.isinf(cac_payback)
                     else "CAC is never paid back: no gross profit per account.")
    if wc_plan > 0 and wc_plan > startup:
        flags.append("Working capital at plan (%s) is bigger than the startup spend: customers' payment terms, not"
                     " equipment, are the main cash need." % "{:,.0f}".format(wc_plan))

    return {
        "business": spec.get("business", "the business"), "currency": spec.get("currency", "$"), "model": model,
        "unit": unit, "price": p, "variable_cost": var_cost, "margin_given": margin_given,
        "contribution": contribution, "contribution_pct": (contribution / p) if p else 0.0,
        "fixed_core": fixed_core, "sales_marketing": sm, "fixed": fixed, "startup": startup,
        "plan_per_month": plan, "capacity_per_month": capacity,
        "breakeven_per_month": breakeven, "revenue_at_plan": rev_plan, "operating_profit_at_plan": op_plan,
        "margin_at_plan": margin_at_plan,
        "receivable_days": rec_days, "inventory_days": inv_days, "payable_days": pay_days,
        "working_capital_at_plan": wc_plan,
        "months": months, "year1_revenue": year1_revenue, "year1_profit": year1_profit,
        "year1_after_startup": year1_profit - startup,
        "cash_needed": -low if low < 0 else 0.0, "payback_month": payback,
        "new_customers_per_month": new_cust, "customer_years": cust_years,
        "units_per_customer_year": units_per_cust_year, "gross_profit_per_customer_year": gp_per_cust_year,
        "cac": cac, "ltv": ltv, "ltv_cac": (ltv / cac) if (cac and ltv is not None) else None,
        "cac_payback_months": cac_payback,
        "flags": flags,
        "variable_items": spec.get("variable") or [], "fixed_items": spec.get("fixed_monthly") or [],
        "sales_marketing_items": spec.get("sales_marketing_monthly") or [], "startup_items": spec.get("startup") or [],
    }


def what_ifs(spec):
    base = analyse(spec)
    rows = [("As planned", base)]
    rows.append(("Price -10%", analyse(spec, price=base["price"] * 0.9)))
    rows.append(("Volume -20%", analyse(spec, volume=0.8)))
    rows.append(("Unit costs +15%", analyse(spec, cost_factor=1.15)))
    rows.append(("Customers pay 30 days later", analyse(spec, dso=base["receivable_days"] + 30)))
    return rows


def report(r, what_if_rows=None):
    cur = r["currency"]

    def money(v, dec=0):
        sign = "-" if v < 0 else ""
        return "%s%s%s" % (sign, cur, ("{:,.%df}" % dec).format(abs(v)))

    pct = lambda v: "%.0f%%" % (v * 100)
    u = r["unit"]
    L = ["# %s · unit economics (%s model)" % (r["business"], r["model"]), ""]
    if r["flags"]:
        L += ["**Watch:**", ""] + ["- %s" % f for f in r["flags"]] + [""]
    L += ["## One %s" % u, "", "| | |", "| --- | ---: |", "| Price | %s |" % money(r["price"], 2)]
    if r["margin_given"]:
        L.append("| Direct cost (from gross margin) | %s |" % money(r["variable_cost"], 2))
    else:
        for it in r["variable_items"]:
            L.append("| %s | %s |" % (it.get("label", "cost"), money(float(it["cost"]), 2)))
    L.append("| **Contribution per %s** | **%s** (%s of price) |" % (u, money(r["contribution"], 2), pct(r["contribution_pct"])))
    L += ["", "## Every month, whatever you sell", "", "| | |", "| --- | ---: |"]
    for it in r["fixed_items"]:
        L.append("| %s | %s |" % (it.get("label", "cost"), money(float(it["cost"]))))
    for it in r["sales_marketing_items"]:
        L.append("| %s (sales & marketing) | %s |" % (it.get("label", "cost"), money(float(it["cost"]))))
    L.append("| **Fixed costs** | **%s** a month |" % money(r["fixed"]))
    be = r["breakeven_per_month"]
    L += ["", "## Break-even and the plan", "", "| | |", "| --- | ---: |",
          "| Break-even | %s %ss a month |" % ("never (no contribution)" if math.isinf(be) else "{:,.0f}".format(math.ceil(be)), u),
          "| Planned volume | %s %ss a month |" % ("{:,.0f}".format(r["plan_per_month"]), u)]
    if r["capacity_per_month"] is not None:
        L.append("| Capacity | %s %ss a month |" % ("{:,.0f}".format(r["capacity_per_month"]), u))
    L += ["| Revenue at plan | %s a month |" % money(r["revenue_at_plan"]),
          "| Operating profit at plan | %s a month |" % money(r["operating_profit_at_plan"]),
          "| **Profit margin at plan** | **%s** |" % pct(r["margin_at_plan"])]
    L += ["", "## Working capital (the B2B cash trap)", "",
          "Customers pay in %d days, stock sits %d days, suppliers are paid in %d days." % (
              r["receivable_days"], r["inventory_days"], r["payable_days"]),
          "At plan volume that ties up **%s** in receivables and stock, net of payables." % money(r["working_capital_at_plan"])]
    if r["cac"] is not None:
        L += ["", "## Winning an account", "", "| | |", "| --- | ---: |",
              "| Sales & marketing a month | %s |" % money(r["sales_marketing"]),
              "| New accounts a month at plan | %s |" % "{:,.1f}".format(r["new_customers_per_month"] or r["plan_per_month"]),
              "| **Cost to win an account (CAC)** | **%s** |" % money(r["cac"]),
              "| Gross profit per account per year | %s |" % money(r["gross_profit_per_customer_year"]),
              "| Years an account keeps buying | %.1f |" % r["customer_years"],
              "| **Lifetime gross profit (LTV)** | **%s** |" % money(r["ltv"]),
              "| LTV / CAC | %s |" % ("%.1fx" % r["ltv_cac"] if r["ltv_cac"] is not None else "n/a"),
              "| CAC paid back in | %s |" % ("never" if math.isinf(r["cac_payback_months"]) else "%.0f months" % r["cac_payback_months"])]
    else:
        L += ["", "_No `sales_marketing_monthly` given, so CAC and LTV are not computed. Add the cost of the sales effort to see them._"]
    L += ["", "## Year 1, month by month", "",
          "| month | %ss | revenue | gross profit | fixed | operating profit | working capital | cash flow | cumulative |" % u,
          "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for m in r["months"]:
        L.append("| %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            m["month"], "{:,.0f}".format(m["units"]), money(m["revenue"]), money(m["gross_profit"]), money(m["fixed"]),
            money(m["operating_profit"]), money(m["working_capital"]), money(m["cash_flow"]), money(m["cumulative"])))
    L += ["", "| | |", "| --- | ---: |",
          "| Year 1 revenue | %s |" % money(r["year1_revenue"]),
          "| Year 1 operating profit | %s |" % money(r["year1_profit"]),
          "| Startup spend | %s |" % money(r["startup"]),
          "| Year 1 after the startup spend | %s |" % money(r["year1_after_startup"]),
          "| **Cash needed before it pays for itself** | **%s** (startup + losses + working capital) |" % money(r["cash_needed"]),
          "| Startup money and working capital earned back | %s |" % ("month %d" % r["payback_month"] if r["payback_month"] else "not in year 1")]
    if what_if_rows:
        L += ["", "## What if", "", "| scenario | margin at plan | break-even / month | year 1 profit | cash needed | LTV/CAC |",
              "| --- | ---: | ---: | ---: | ---: | ---: |"]
        for name, w in what_if_rows:
            wbe = w["breakeven_per_month"]
            L.append("| %s | %s | %s | %s | %s | %s |" % (
                name, pct(w["margin_at_plan"]), "never" if math.isinf(wbe) else "{:,.0f}".format(math.ceil(wbe)),
                money(w["year1_profit"]), money(w["cash_needed"]), ("%.1fx" % w["ltv_cac"]) if w["ltv_cac"] is not None else "n/a"))
    L += ["", "_Every number above comes from numbers.json. Revenue is before tax. Projections, not a forecast; real quotes,"
          " signed terms and an accountant confirm them._"]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("path")
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--price", type=float)
    ap.add_argument("--volume", type=float, default=1.0)
    ap.add_argument("--dso", type=float)
    a = ap.parse_args(argv)
    try:
        spec = load(a.path)
        r = analyse(spec, price=a.price, volume=a.volume, dso=a.dso)
        if a.json:
            print(json.dumps({k: v for k, v in r.items() if not k.endswith("_items")}, indent=1, default=str))
            return 0
        rows = what_ifs(spec) if (a.price is None and a.volume == 1.0 and a.dso is None) else None
        text = report(r, rows)
        if a.out:
            with open(a.out, "w", encoding="utf-8") as fh:
                fh.write(text)
            print("Wrote %s. Margin at plan %.0f%%, break-even %s %ss/month, cash needed %s%s." % (
                a.out, r["margin_at_plan"] * 100,
                "never" if math.isinf(r["breakeven_per_month"]) else "{:,.0f}".format(math.ceil(r["breakeven_per_month"])),
                r["unit"], r["currency"], "{:,.0f}".format(r["cash_needed"])))
        else:
            print(text)
    except NumbersError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
