#!/usr/bin/env python3
"""Compiles the business plan for b2b-plan. Standard library only, no network.

Reads everything the other ten skills wrote into b2b/ and assembles one
document, b2b/business-plan.md, with a verdict at the top. The verdict is
computed from the numbers, never written by hand:

    Viable     every check that has data passes
    Not yet      at least one check fails (each failure is listed with its number)
    Incomplete   there are no numbers yet (run b2b-cfo first)

The checks:
    1. each unit earns money before fixed costs          (b2b/numbers.json)
    2. year 1 makes an operating profit                   (b2b/numbers.json)
    3. break-even fits inside capacity, if capacity is given
    4. LTV/CAC is at least --min-ltv-cac (default 3), if sales cost is given
    5. CAC is paid back within --max-payback months (default 18), if given
    6. enough simulated committees buy                    (b2b/committee/results.json,
                                                           --min-win-rate, default 20%)

    python3 compile.py                      # reads ./b2b, writes ./b2b/business-plan.md
    python3 compile.py --dir path/to/b2b --min-win-rate 0.3
    python3 compile.py --check              # print the verdict and exit 0 (Viable) or 1
"""

import argparse
import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SECTIONS = [  # (file in b2b/, heading, which skill writes it)
    ("summary.md", "Summary", "b2b-plan"),
    ("board.md", "What the board said", "b2b-board"),
    ("competitors.md", "The competition", "b2b-competitors"),
    ("committee/results.md", "The buying-committee panel", "b2b-committee"),
    ("pricing.md", "Pricing", "b2b-pricing"),
    ("offer.md", "The offer", "b2b-offer"),
    ("cfo.md", "The numbers", "b2b-cfo"),
    ("gtm.md", "Go-to-market", "b2b-gtm"),
    ("brand.md", "Brand", "b2b-brand"),
    ("ops.md", "Operations", "b2b-ops"),
    ("launch.md", "Launch plan", "b2b-launch"),
]


def _load_economics():
    path = os.path.join(HERE, "..", "b2b-cfo", "b2b_economics.py")
    spec = importlib.util.spec_from_file_location("b2b_economics", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read().strip()
    except FileNotFoundError:
        return None


def _strip_h1(text):
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    return "\n".join(("#" + l) if l.startswith("#") else l for l in lines).strip()


def verdict(d, min_win_rate=0.2, min_ltv_cac=3.0, max_payback=18.0):
    """Return (verdict, checks, numbers, panel). checks = [(ok, text)]."""
    checks = []
    numbers = panel = None
    raw = _read(os.path.join(d, "numbers.json"))
    if raw:
        ue = _load_economics()
        numbers = ue.analyse(json.loads(raw))
        cur = numbers["currency"]
        money = lambda v: "%s%s" % (cur, "{:,.0f}".format(abs(v)))
        u = numbers["unit"]
        c = numbers["contribution"]
        checks.append((c > 0, "Each %s earns %s before fixed costs (%.0f%% contribution)." % (u, money(c), numbers["contribution_pct"] * 100)
                       if c > 0 else "Each %s LOSES %s before fixed costs." % (u, money(c))))
        y = numbers["year1_profit"]
        checks.append((y > 0, "Year 1 operating profit: %s." % money(y) if y > 0 else "Year 1 operating LOSS: %s." % money(y)))
        be, cap = numbers["breakeven_per_month"], numbers["capacity_per_month"]
        if cap is not None:
            fits = not math.isinf(be) and be <= float(cap)
            checks.append((fits, "Break-even is %s %ss a month against a capacity of %s." % (
                "never reached" if math.isinf(be) else "{:,.0f}".format(math.ceil(be)), u, "{:,.0f}".format(cap))))
        if numbers["ltv_cac"] is not None:
            r = numbers["ltv_cac"]
            checks.append((r >= min_ltv_cac, "A won account returns %.1fx its acquisition cost (LTV %s, CAC %s; the bar is %.0fx)." % (
                r, money(numbers["ltv"]), money(numbers["cac"]), min_ltv_cac)))
        if numbers["cac_payback_months"] is not None:
            pb = numbers["cac_payback_months"]
            checks.append((pb <= max_payback, "CAC is paid back in %s (the bar is %.0f months)." % (
                "never" if math.isinf(pb) else "%.0f months" % pb, max_payback)))
    raw = _read(os.path.join(d, "committee", "results.json"))
    if raw:
        panel = json.loads(raw)
        r = panel["win_rate"]
        checks.append((r >= min_win_rate, "%d of %d simulated committees buy (%.0f%%, the bar is %.0f%%); %d more would pilot." % (
            panel["buys"], panel["answered"], r * 100, min_win_rate * 100, panel["pilots"])))
    if numbers is None:
        v = "Incomplete"
    elif all(ok for ok, _ in checks):
        v = "Viable"
    else:
        v = "Not yet"
    return v, checks, numbers, panel


def compile_plan(d, min_win_rate=0.2, min_ltv_cac=3.0, max_payback=18.0):
    idea = _read(os.path.join(d, "idea.md"))
    name = None
    if idea:
        first = idea.splitlines()[0]
        name = first[2:].strip() if first.startswith("# ") else None
    v, checks, numbers, panel = verdict(d, min_win_rate, min_ltv_cac, max_payback)
    title = name or (numbers["business"] if numbers and numbers.get("business") else "Your business")
    L = ["# %s · Business plan" % title, ""]
    L.append("**Verdict: %s**" % v)
    L.append("")
    for ok, text in checks:
        L.append("- %s %s" % ("✓" if ok else "✗", text))
    if v == "Incomplete":
        L.append("- No numbers yet. Run /b2b-cfo, then compile again.")
    L.append("")
    if numbers:
        cur = numbers["currency"]
        money = lambda val: "%s%s%s" % ("-" if val < 0 else "", cur, "{:,.0f}".format(abs(val)))
        be = numbers["breakeven_per_month"]
        L += ["| key number | |", "| --- | ---: |",
              "| Model | %s, one unit = one %s |" % (numbers["model"], numbers["unit"]),
              "| Price | %s a %s |" % (money(numbers["price"]), numbers["unit"]),
              "| Contribution | %s per %s (%.0f%%) |" % (money(numbers["contribution"]), numbers["unit"], numbers["contribution_pct"] * 100),
              "| Profit margin at plan | %.0f%% |" % (numbers["margin_at_plan"] * 100),
              "| Break-even | %s %ss a month |" % ("never" if math.isinf(be) else "{:,.0f}".format(math.ceil(be)), numbers["unit"]),
              "| Year 1 revenue | %s |" % money(numbers["year1_revenue"]),
              "| Year 1 operating profit | %s |" % money(numbers["year1_profit"]),
              "| Startup spend | %s |" % money(numbers["startup"]),
              "| Working capital at plan | %s |" % money(numbers["working_capital_at_plan"]),
              "| Cash needed before it pays for itself | %s |" % money(numbers["cash_needed"]),
              "| Earned back | %s |" % ("month %d" % numbers["payback_month"] if numbers["payback_month"] else "not in year 1")]
        if numbers["cac"] is not None:
            L.append("| CAC / LTV | %s / %s (%.1fx) |" % (money(numbers["cac"]), money(numbers["ltv"]), numbers["ltv_cac"]))
        if panel:
            L.append("| Committee panel | %d buy · %d pilot · %d pass |" % (panel["buys"], panel["pilots"], panel["passes"]))
        L.append("")
    if idea:
        L += ["## The idea", "", _strip_h1(idea), ""]
    missing = []
    for fname, heading, skill in SECTIONS:
        text = _read(os.path.join(d, fname))
        if text:
            L += ["## %s" % heading, "", _strip_h1(text), ""]
        else:
            missing.append((heading, skill))
    if missing:
        L += ["## Not done yet", ""]
        for heading, skill in missing:
            L.append("- %s: run /%s" % (heading, skill))
        L.append("")
    L.append("_The panel is simulated buying committees and the numbers are projections from your inputs. Confirm demand with"
             " real accounts (a paid pilot, a signed quote) and costs with real supplier quotes before you spend. Not financial,"
             " legal or tax advice._")
    return v, "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dir", default="b2b")
    ap.add_argument("--min-win-rate", type=float, default=0.2)
    ap.add_argument("--min-ltv-cac", type=float, default=3.0)
    ap.add_argument("--max-payback", type=float, default=18.0)
    ap.add_argument("--check", action="store_true", help="print the verdict only; exit 0 if Viable")
    ap.add_argument("--out", help="default: <dir>/business-plan.md")
    a = ap.parse_args(argv)
    if not os.path.isdir(a.dir):
        print("error: no %s/ folder here. Run the other b2b skills first." % a.dir, file=sys.stderr)
        return 2
    v, text = compile_plan(a.dir, a.min_win_rate, a.min_ltv_cac, a.max_payback)
    if a.check:
        _, checks, _, _ = verdict(a.dir, a.min_win_rate, a.min_ltv_cac, a.max_payback)
        print("Verdict: %s" % v)
        for ok, t in checks:
            print("  %s %s" % ("✓" if ok else "✗", t))
        return 0 if v == "Viable" else 1
    out = a.out or os.path.join(a.dir, "business-plan.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("Verdict: %s. Wrote %s" % (v, out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
