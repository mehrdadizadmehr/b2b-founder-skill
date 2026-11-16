#!/usr/bin/env python3
"""B2B price band for b2b-pricing. Standard library only, no network.

Consumers answer "too cheap / too expensive". Buying committees answer "what we
would accept as fair", "where we stop talking" and "the discount procurement
will push for". This tool reads those three answers per account (from the
committee panel, or a CSV from real quotes and lost deals) and turns them into
an acceptance curve and a recommended band.

    python3 pricing.py b2b/committee/answers --price 100
    python3 pricing.py b2b/committee/answers --price 100 --floor 70 --competitors b2b/competitors.json
    python3 pricing.py quotes.csv --price 100 --keep 0.6 --out b2b/pricing-curve.md

Input, one row per account:
    price_acceptable        the price the committee calls fair
    price_walk_away         the price above which it stops considering you
    discount_expected_pct   the discount procurement expects (optional)

A folder is read as the committee panel's answers/*.json. A .csv needs those
column names in its header.

--price      the price you are planning, so the report says where it sits
--floor      the lowest price that still earns the margin the CFO needs
--keep       the share of accounts that must still be in the conversation at
             the recommended ceiling (default 0.6)
--competitors  a JSON list [{"name", "price", "note"}] from b2b-competitors
"""

import argparse
import csv
import glob
import json
import os
import sys


class PricingError(Exception):
    pass


def _num(v):
    try:
        f = float(v)
        return f if f >= 0 else None
    except (TypeError, ValueError):
        return None


def read_rows(path):
    rows = []
    if os.path.isdir(path):
        for f in sorted(glob.glob(os.path.join(path, "*.json"))):
            try:
                with open(f, encoding="utf-8") as fh:
                    a = json.load(fh)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if isinstance(a, dict):
                rows.append(a)
    elif path.lower().endswith(".csv"):
        with open(path, encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
    else:
        raise PricingError("give the answers folder or a .csv")
    out = []
    for a in rows:
        acc, walk = _num(a.get("price_acceptable")), _num(a.get("price_walk_away"))
        if acc is None or walk is None:
            continue
        if walk < acc:
            acc, walk = walk, acc  # an account that mixed the two up
        out.append({"id": a.get("id", ""), "acceptable": acc, "walk_away": walk,
                    "discount": _num(a.get("discount_expected_pct")), "outcome": a.get("outcome")})
    if len(out) < 5:
        raise PricingError("only %d usable rows (need at least 5 with price_acceptable and price_walk_away)" % len(out))
    return out


def _pct(vals, q):
    vals = sorted(vals)
    if not vals:
        return None
    k = (len(vals) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(vals) - 1)
    return vals[lo] + (vals[hi] - vals[lo]) * (k - lo)


def analyse(rows, price=None, floor=None, keep=0.6):
    acc = [r["acceptable"] for r in rows]
    walk = [r["walk_away"] for r in rows]
    disc = [r["discount"] for r in rows if r["discount"] is not None]
    n = len(rows)

    def still_in(p):
        return sum(1 for w in walk if w >= p) / n

    def fair(p):
        return sum(1 for a in acc if a >= p) / n

    lo, hi = min(acc), max(walk)
    grid = sorted({round(lo + (hi - lo) * i / 10, 2) for i in range(11)} | ({round(price, 2)} if price else set()))
    curve = [(p, fair(p), still_in(p)) for p in grid]
    # ceiling: the highest price that keeps `keep` of accounts in the conversation
    cands = sorted(set(walk))
    ceiling = None
    for p in cands:
        if still_in(p) >= keep:
            ceiling = p
    median_fair = _pct(acc, 0.5)
    res = {
        "n": n, "keep": keep,
        "acceptable": {"p25": _pct(acc, 0.25), "median": median_fair, "p75": _pct(acc, 0.75)},
        "walk_away": {"p25": _pct(walk, 0.25), "median": _pct(walk, 0.5), "p75": _pct(walk, 0.75)},
        "discount_expected_pct": (sum(disc) / len(disc)) if disc else None,
        "curve": curve, "ceiling": ceiling, "floor": floor, "price": price,
        "band": None, "list_price_for_median": None, "at_price": None,
    }
    if ceiling is not None:
        band_lo = max(floor, median_fair) if floor is not None else median_fair
        res["band"] = (min(band_lo, ceiling), ceiling)
    if res["discount_expected_pct"]:
        d = res["discount_expected_pct"] / 100.0
        if d < 1:
            res["list_price_for_median"] = median_fair / (1 - d)
    if price is not None:
        res["at_price"] = {"fair": fair(price), "still_in": still_in(price),
                           "below_floor": (floor is not None and price < floor)}
    return res


def report(res, competitors=None, currency="$"):
    money = lambda v: "%s%s" % (currency, "{:,.2f}".format(v))
    pct = lambda v: "%.0f%%" % (v * 100)
    L = ["# Price band from %d accounts" % res["n"], ""]
    a, w = res["acceptable"], res["walk_away"]
    L += ["| | lower quartile | median | upper quartile |", "| --- | ---: | ---: | ---: |",
          "| Price the committee calls fair | %s | **%s** | %s |" % (money(a["p25"]), money(a["median"]), money(a["p75"])),
          "| Price where it stops talking | %s | **%s** | %s |" % (money(w["p25"]), money(w["median"]), money(w["p75"]))]
    if res["discount_expected_pct"] is not None:
        L += ["", "Procurement expects a **%.0f%%** discount before signing. To land at the median fair price after that discount, the list price is **%s**."
              % (res["discount_expected_pct"], money(res["list_price_for_median"]))]
    L += ["", "## Acceptance curve", "", "| price | call it fair | still in the conversation |", "| ---: | ---: | ---: |"]
    for p, f, s in res["curve"]:
        mark = "  ← your price" if res["price"] is not None and abs(p - res["price"]) < 1e-9 else ""
        L.append("| %s | %s | %s%s |" % (money(p), pct(f), pct(s), mark))
    L += ["", "## The band", ""]
    if res["floor"] is not None:
        L.append("- Floor (the CFO's margin): **%s**. Below this the business does not earn its margin." % money(res["floor"]))
    if res["ceiling"] is not None:
        L.append("- Ceiling: **%s**, the highest price that keeps %s of accounts in the conversation." % (money(res["ceiling"]), pct(res["keep"])))
    if res["band"]:
        lo, hi = res["band"]
        L.append("- **Recommended band: %s to %s.** Test the top of it first; B2B buyers negotiate down, never up." % (money(lo), money(hi)))
    if res["floor"] is not None and res["ceiling"] is not None and res["floor"] > res["ceiling"]:
        L.append("- **The floor is above the ceiling.** The price the margin needs loses most accounts. Cut the direct cost,"
                 " change the unit (bundle, contract, volume tier) or pick a segment with a higher walk-away price.")
    if res["at_price"]:
        ap_ = res["at_price"]
        L += ["", "## Your price: %s" % money(res["price"]), "",
              "- %s of accounts call it fair; %s are still in the conversation at this price." % (pct(ap_["fair"]), pct(ap_["still_in"]))]
        if ap_["below_floor"]:
            L.append("- **It is below the CFO's floor.** You would win accounts and lose money on each.")
    if competitors:
        L += ["", "## Against the competitors", "", "| competitor | price | note |", "| --- | ---: | --- |"]
        for c in sorted(competitors, key=lambda c: float(c.get("price") or 0)):
            L.append("| %s | %s | %s |" % (c.get("name", "?"), money(float(c["price"])) if _num(c.get("price")) is not None else "?",
                                           (c.get("note") or "").replace("|", "/")))
    L += ["", "_From simulated committees unless the rows came from real quotes. Real quotes and lost-deal reviews beat"
          " this every time; replace the inputs with them as soon as you have five._"]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("path", help="answers folder or .csv")
    ap.add_argument("--price", type=float)
    ap.add_argument("--floor", type=float)
    ap.add_argument("--keep", type=float, default=0.6)
    ap.add_argument("--competitors")
    ap.add_argument("--currency", default="$")
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        rows = read_rows(a.path)
        res = analyse(rows, a.price, a.floor, a.keep)
        comps = None
        if a.competitors:
            with open(a.competitors, encoding="utf-8") as fh:
                comps = json.load(fh)
        if a.json:
            print(json.dumps(res, indent=1))
            return 0
        text = report(res, comps, a.currency)
        if a.out:
            with open(a.out, "w", encoding="utf-8") as fh:
                fh.write(text)
            print("Wrote %s" % a.out)
        else:
            print(text)
    except (PricingError, FileNotFoundError, json.JSONDecodeError) as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
