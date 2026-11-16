#!/usr/bin/env python3
"""The buying-committee panel for b2b-committee. Standard library only, no network.

B2B deals are not decided by one person. Each simulated "buyer" here is an
ACCOUNT: a company drawn from your ideal customer profile, with a buying
committee inside it (procurement, the technical lead, the budget owner, the
end user...). One sub-agent plays the whole committee of one account, argues
it out the way a real purchase meeting does, and files one verdict: buy, pilot
or pass, with the expected annual value, the sales cycle, who blocked, and the
price the committee would accept.

    python3 committee.py init --customer b2b/customer.json --pitch b2b/pitch.md [--n 16] [--seed 7]
    python3 committee.py prompts [--batch 4] [--wave 8]   # briefs for the accounts still to run, in waves
    python3 committee.py check                 # which answers are missing or broken
    python3 committee.py save A003 < reply.txt # file an answer a sub-agent printed instead of writing
    python3 committee.py tally [--out b2b/committee/results.md]
    python3 committee.py status

State lives in b2b/committee/ (--dir to change it): panel.json, accounts.json,
briefs/<id>.md (or briefs/B01.md for a batch of accounts), answers/<id>.json,
results.md, results.json.

Cost: one sub-agent per account is the most independent run; --batch 4 puts four
accounts in one brief so one sub-agent holds four meetings in turn, which cuts the
calls and the repeated pitch by about four. The default panel is 16 accounts
(3 to 5 per segment x situation that matters), sized for a personal Claude plan.

The tool never answers for an account. Every number in results.md is counted
from the answer files the sub-agents wrote. Simulated committees are a fast,
cheap way to find objections, blockers and the price band before you spend a
sales cycle. They are not customers: confirm what matters with real accounts
(a paid pilot, a letter of intent, a quote they actually sign).
"""

import argparse
import json
import os
import random
import sys

REASONS = ["price", "incumbent", "trust", "quality", "lead_time", "compliance",
           "integration", "payment_terms", "timing", "need", "other"]
OUTCOMES = ["buy", "pilot", "pass"]
STANCES = ["for", "against", "neutral"]
ANSWER_FIELDS = {"id", "outcome", "reason_code", "reason"}
WAVE = 8
BATCH = 1


class PanelError(Exception):
    pass


# ── dealing ─────────────────────────────────────────────────────────────────────
def _quota(items, n, key="share"):
    """Split n across items by their shares, exactly (largest remainder)."""
    total = sum(float(it.get(key, 1)) for it in items) or 1.0
    raw = [n * float(it.get(key, 1)) / total for it in items]
    counts = [int(r) for r in raw]
    order = sorted(range(len(items)), key=lambda i: raw[i] - counts[i], reverse=True)
    for i in order[: n - sum(counts)]:
        counts[i] += 1
    return counts


def validate_customer(c):
    for k in ("business", "target", "segments", "roles", "situations", "objections"):
        if k not in c or c[k] in ("", [], None):
            raise PanelError("customer.json needs '%s'" % k)
    for s in c["segments"]:
        for f in ("name", "employees", "annual_spend"):
            if f not in s:
                raise PanelError("every segment needs a name, employees [low, high] and annual_spend [low, high]")
        if len(s["employees"]) != 2 or len(s["annual_spend"]) != 2:
            raise PanelError("segment '%s': employees and annual_spend are [low, high]" % s["name"])
    if not (2 <= len(c["roles"]) <= 6):
        raise PanelError("roles: give the 2 to 6 seats on the buying committee")
    for r in c["roles"]:
        if "name" not in r or "cares" not in r:
            raise PanelError("every role needs a name and what it cares about ('cares')")
    for s in c["situations"]:
        if "name" not in s:
            raise PanelError("every situation needs a name")


def _round_sig(v, digits=2):
    if v <= 0:
        return 0
    import math
    mag = 10 ** (int(math.floor(math.log10(v))) - digits + 1)
    return int(round(v / mag) * mag)


def deal(customer, n=16, seed=7):
    """Deal n account cards. Same customer + n + seed = the same cards, every time."""
    validate_customer(customer)
    if n < 1:
        raise PanelError("--n must be at least 1")
    rng = random.Random(seed)
    segs = []
    for s, k in zip(customer["segments"], _quota(customer["segments"], n)):
        segs += [s] * k
    sits = []
    for s, k in zip(customer["situations"], _quota(customer["situations"], n)):
        sits += [s] * k
    rng.shuffle(segs)
    rng.shuffle(sits)
    objections = customer["objections"]
    triggers = customer.get("triggers") or []
    regions = customer.get("regions") or []
    cards = []
    for i in range(n):
        s, b = segs[i], sits[i]
        emp = rng.randint(int(s["employees"][0]), int(s["employees"][1]))
        lo, hi = float(s["annual_spend"][0]), float(s["annual_spend"][1])
        cards.append({
            "id": "A%03d" % (i + 1),
            "segment": s["name"],
            "segment_how": s.get("how", ""),
            "employees": emp,
            "annual_spend": _round_sig(rng.uniform(lo, hi)),
            "situation": b["name"],
            "situation_how": b.get("how", ""),
            "objection": objections[rng.randrange(len(objections))],
            "trigger": triggers[rng.randrange(len(triggers))] if triggers else "",
            "region": regions[rng.randrange(len(regions))] if regions else "",
        })
    return cards


# ── state ───────────────────────────────────────────────────────────────────────
def _path(d, *p):
    return os.path.join(d, *p)


def _read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _write_json(path, obj):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


def init(d, customer_path, pitch_path, n=16, seed=None):
    try:
        customer = _read_json(customer_path)
    except FileNotFoundError:
        raise PanelError("no such file: %s" % customer_path)
    try:
        with open(pitch_path, encoding="utf-8") as fh:
            pitch = fh.read().strip()
    except FileNotFoundError:
        raise PanelError("no such file: %s (write the pitch first: what you sell, the price, terms, lead time)" % pitch_path)
    if not pitch:
        raise PanelError("the pitch is empty")
    if seed is None:
        seed = random.SystemRandom().randrange(1, 10 ** 6)
    cards = deal(customer, n, seed)
    _write_json(_path(d, "panel.json"), {"n": n, "seed": seed, "customer": customer, "pitch": pitch})
    _write_json(_path(d, "accounts.json"), cards)
    os.makedirs(_path(d, "briefs"), exist_ok=True)
    os.makedirs(_path(d, "answers"), exist_ok=True)
    return cards


def load_state(d):
    try:
        return _read_json(_path(d, "panel.json")), _read_json(_path(d, "accounts.json"))
    except FileNotFoundError:
        raise PanelError("no panel in %s: run init first" % d)


# ── briefs ──────────────────────────────────────────────────────────────────────
ACCOUNT = """A {segment} with about {employees} staff{region_line}. {segment_how}
It spends about {currency}{annual_spend:,} a year on this category today.
Situation: {situation}. {situation_how}
{trigger_line}The first thing the committee says when a new vendor like this shows up: "{objection}"
It is one of these companies: {target}."""

SHARED = """=== THE COMMITTEE (play every seat) ===
{roles}
=== END ===

=== WHAT IS BEING OFFERED (you see it for the first time, the way a cold email, a trade-show visit or a tender reply lands) ===
{pitch}
=== END ===

Hold the purchase meeting. Each seat speaks from what it cares about, with this company's budget, incumbent supplier, risk appetite and procurement rules. Do not be agreeable. Do not invent facts about the vendor beyond what is written above; if something you would need to know is missing (certifications, references, lead time, payment terms), that is an objection, not a guess. Decide as the committee would: "buy" means a purchase order or contract within a normal sales cycle; "pilot" means a small paid trial or a sample order first; "pass" means no."""

ANSWER = """{{
  "id": "{id}",
  "outcome": "buy" or "pilot" or "pass",
  "annual_value": the expected purchase from this vendor in the first 12 months in {currency} (0 if pass; a pilot is small),
  "sales_cycle_months": how many months from this first contact to a signed order (a number; 0 if pass),
  "reason_code": one of {reasons},
  "reason": "the committee's decision in one or two sentences, in its own words",
  "blocker_role": "the seat that blocks or decides the outcome, exactly as named above, or empty",
  "objection": "the objection that weighs most, in the committee's words",
  "would_change_my_mind": "the one thing the vendor could do or prove that flips the outcome, or empty",
  "committee": {{ {committee_json} }},
  "price_acceptable": the price (same unit as the pitch) the committee would accept as fair (a number),
  "price_walk_away": the price above which it would not consider the vendor at all (a number),
  "discount_expected_pct": the discount in percent procurement would push for before signing (a number, 0 if none)
}}"""

BRIEF = """You are the buying committee of one company on a simulated B2B panel. A founder wants to know, before spending a sales cycle, whether companies like yours would buy. Your answer is only useful if it is honest: most vendors never get past procurement, and a polite "send us a proposal" is worse than a clear no.

=== THE ACCOUNT ===
{account}
=== END ===

{shared}

Create the file {out} with your file-writing tool (do not just print the answer in your reply) containing ONLY this JSON, no markdown fence, nothing else:
{answer}
"""

BATCH_BRIEF = """You are playing the buying committees of {k} DIFFERENT companies on a simulated B2B panel, one purchase meeting at a time. A founder wants to know, before spending a sales cycle, whether companies like these would buy. Your answers are only useful if they are honest: most vendors never get past procurement, and a polite "send us a proposal" is worse than a clear no.

The companies share nothing but the offer they are shown. Hold each meeting fresh, from that company's own situation; do not let one verdict colour the next, and do not spread the outcomes for variety. If four companies would all pass, all four pass.

{shared}

{accounts}

For EACH account above, create its file with your file-writing tool (do not just print the answers in your reply) containing ONLY this JSON, with that account's id, no markdown fence, nothing else:
{answer}
"""


def _roles_text(roles):
    return "\n".join("- %s: cares about %s." % (r["name"], r["cares"]) for r in roles)


def _card_text(c, cust, cur):
    return ACCOUNT.format(
        target=cust["target"], currency=cur,
        region_line=(" in %s" % c["region"]) if c.get("region") else "",
        trigger_line=("What started the search: %s.\n" % c["trigger"]) if c.get("trigger") else "",
        **c)


def write_briefs(d, wave=WAVE, batch=BATCH):
    """Write a brief for every account without a valid answer.

    batch=1: one brief per account (briefs/<id>.md), the most independent run.
    batch=k: k accounts per brief (briefs/B01.md...), one sub-agent plays them in turn.
    Returns waves of (label, brief path); a batch label is "B01:A001+A002+...".
    """
    if batch < 1:
        raise PanelError("--batch must be at least 1")
    state, cards = load_state(d)
    cust = state["customer"]
    cur = cust.get("currency", "$")
    shared = SHARED.format(roles=_roles_text(cust["roles"]), pitch=state["pitch"])
    committee_json = ", ".join('"%s": "for" or "against" or "neutral"' % r["name"] for r in cust["roles"])
    reasons = " / ".join(REASONS)
    pending = [c for c in cards if _answer_ok(_path(d, "answers", c["id"] + ".json"), c["id"], cust["roles"]) is not None]
    todo = []
    if batch == 1:
        for c in pending:
            out = os.path.abspath(_path(d, "answers", c["id"] + ".json"))
            brief = BRIEF.format(account=_card_text(c, cust, cur), shared=shared, out=out,
                                 answer=ANSWER.format(id=c["id"], currency=cur, reasons=reasons, committee_json=committee_json))
            bp = _path(d, "briefs", c["id"] + ".md")
            with open(bp, "w", encoding="utf-8") as fh:
                fh.write(brief)
            todo.append((c["id"], bp))
    else:
        groups = [pending[i:i + batch] for i in range(0, len(pending), batch)]
        for g_no, group in enumerate(groups, 1):
            blocks = []
            for k, c in enumerate(group, 1):
                out = os.path.abspath(_path(d, "answers", c["id"] + ".json"))
                blocks.append("=== ACCOUNT %d of %d: id %s, write %s ===\n%s\n=== END ===" % (
                    k, len(group), c["id"], out, _card_text(c, cust, cur)))
            brief = BATCH_BRIEF.format(
                k=len(group), shared=shared, accounts="\n\n".join(blocks),
                answer=ANSWER.format(id="the account's id", currency=cur, reasons=reasons, committee_json=committee_json))
            label = "B%02d" % g_no
            bp = _path(d, "briefs", label + ".md")
            with open(bp, "w", encoding="utf-8") as fh:
                fh.write(brief)
            todo.append(("%s:%s" % (label, "+".join(c["id"] for c in group)), bp))
    return [todo[i:i + wave] for i in range(0, len(todo), wave)]


# ── answers ─────────────────────────────────────────────────────────────────────
def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _answer_ok(path, pid, roles=None):
    """None if the answer file is valid, else a short reason."""
    if not os.path.exists(path):
        return "missing"
    try:
        a = _read_json(path)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return "not valid JSON"
    if not isinstance(a, dict):
        return "not a JSON object"
    missing = ANSWER_FIELDS - set(a)
    if missing:
        return "missing %s" % ", ".join(sorted(missing))
    if a["id"] != pid:
        return "id is %r, expected %r" % (a["id"], pid)
    if a["outcome"] not in OUTCOMES:
        return "outcome must be one of %s" % "/".join(OUTCOMES)
    if a["reason_code"] not in REASONS:
        return "reason_code %r is not one of %s" % (a["reason_code"], "/".join(REASONS))
    if not str(a["reason"]).strip():
        return "empty reason"
    if a["outcome"] != "pass" and _num(a.get("annual_value")) is None:
        return "annual_value must be a number when the outcome is buy or pilot"
    if "committee" in a and not isinstance(a["committee"], dict):
        return "committee must be an object of role -> for/against/neutral"
    return None


def save(d, pid, text):
    _, cards = load_state(d)
    if pid not in {c["id"] for c in cards}:
        raise PanelError("no account %s on this panel" % pid)
    start = text.find("{")
    if start < 0:
        raise PanelError("no JSON object in the reply")
    try:
        obj, _ = json.JSONDecoder().raw_decode(text[start:])
    except json.JSONDecodeError as e:
        raise PanelError("the reply's JSON does not parse: %s" % e)
    path = _path(d, "answers", pid + ".json")
    _write_json(path, obj)
    prob = _answer_ok(path, pid)
    if prob:
        os.remove(path)
        raise PanelError("%s's answer is not valid (%s); re-run its brief instead" % (pid, prob))
    return path


def check(d):
    _, cards = load_state(d)
    probs = []
    for c in cards:
        p = _answer_ok(_path(d, "answers", c["id"] + ".json"), c["id"])
        if p:
            probs.append((c["id"], p))
    return probs


# ── tally ───────────────────────────────────────────────────────────────────────
def _rate(rows, outcome="buy"):
    return (sum(1 for r in rows if r["outcome"] == outcome) / len(rows)) if rows else 0.0


def _mean(vals):
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else None


def _median(vals):
    vals = sorted(v for v in vals if v is not None)
    if not vals:
        return None
    m = len(vals) // 2
    return vals[m] if len(vals) % 2 else (vals[m - 1] + vals[m]) / 2


def tally(d):
    state, cards = load_state(d)
    cust = state["customer"]
    by_id = {c["id"]: c for c in cards}
    rows, skipped = [], []
    for c in cards:
        path = _path(d, "answers", c["id"] + ".json")
        p = _answer_ok(path, c["id"])
        if p:
            skipped.append((c["id"], p))
            continue
        a = _read_json(path)
        rows.append(dict(by_id[c["id"]], **{k: v for k, v in a.items() if k != "id"}, id=c["id"]))
    if not rows:
        raise PanelError("no valid answers yet: run the briefs first (committee.py prompts)")

    def group(key):
        out = {}
        for r in rows:
            out.setdefault(r[key], []).append(r)
        return sorted(((k, len(v), _rate(v, "buy"), _rate(v, "pilot")) for k, v in out.items()), key=lambda t: -(t[2] + t[3]))

    spends = sorted(r["annual_spend"] for r in rows)
    cut1, cut2 = spends[len(spends) // 3], spends[2 * len(spends) // 3]
    cur = cust.get("currency", "$")
    for r in rows:
        r["spend_band"] = ("under %s%s" % (cur, "{:,}".format(cut1))) if r["annual_spend"] < cut1 else (
            ("%s%s and up" % (cur, "{:,}".format(cut2))) if r["annual_spend"] >= cut2
            else "%s%s to %s%s" % (cur, "{:,}".format(cut1), cur, "{:,}".format(cut2)))

    buys = [r for r in rows if r["outcome"] == "buy"]
    pilots = [r for r in rows if r["outcome"] == "pilot"]
    passes = [r for r in rows if r["outcome"] == "pass"]

    def reasons(rs):
        out = {}
        for r in rs:
            out.setdefault(r["reason_code"], []).append(r)
        return sorted(((k, v) for k, v in out.items()), key=lambda kv: -len(kv[1]))

    blockers = {}
    for r in passes + pilots:
        b = (r.get("blocker_role") or "").strip()
        if b:
            blockers[b] = blockers.get(b, 0) + 1
    stance = {}
    for r in rows:
        for role, s in (r.get("committee") or {}).items():
            if s in STANCES:
                st = stance.setdefault(role, {"for": 0, "against": 0, "neutral": 0})
                st[s] += 1

    engaged = buys + pilots
    res = {
        "business": cust["business"], "currency": cur, "seed": state["seed"], "dealt": len(cards),
        "answered": len(rows), "skipped": skipped,
        "buys": len(buys), "pilots": len(pilots), "passes": len(passes),
        "win_rate": len(buys) / len(rows), "engaged_rate": len(engaged) / len(rows),
        "by_segment": group("segment"), "by_situation": group("situation"), "by_spend": group("spend_band"),
        "blockers": sorted(blockers.items(), key=lambda kv: -kv[1]),
        "stance": stance,
        "why_not": [(k, len(v), [r["reason"] for r in v[:2]], [r["id"] for r in v[:2]]) for k, v in reasons(passes)],
        "why_yes": [(k, len(v), [r["reason"] for r in v[:2]], [r["id"] for r in v[:2]]) for k, v in reasons(buys)],
        "flip": [r["would_change_my_mind"] for r in passes + pilots if (r.get("would_change_my_mind") or "").strip()],
        "annual_value_per_buyer": _mean([_num(r.get("annual_value")) for r in buys]),
        "annual_value_per_pilot": _mean([_num(r.get("annual_value")) for r in pilots]),
        "pipeline_year1": sum(_num(r.get("annual_value")) or 0 for r in engaged),
        "sales_cycle_months": _median([_num(r.get("sales_cycle_months")) for r in engaged]),
        "share_of_wallet": _mean([(_num(r.get("annual_value")) or 0) / r["annual_spend"] for r in buys if r["annual_spend"]]),
        "price_acceptable_median": _median([_num(r.get("price_acceptable")) for r in rows]),
        "price_walk_away_median": _median([_num(r.get("price_walk_away")) for r in rows]),
        "discount_expected_pct": _mean([_num(r.get("discount_expected_pct")) for r in engaged]),
        "price_answers": sum(1 for r in rows if all(_num(r.get(k)) is not None for k in ("price_acceptable", "price_walk_away"))),
    }
    return res


def results_md(res):
    pct = lambda v: "%.0f%%" % (v * 100)
    cur = res["currency"]
    money = lambda v: "%s%s" % (cur, "{:,.0f}".format(v))
    L = ["# Buying-committee panel: %s" % res["business"], ""]
    L.append("**%d buy · %d pilot · %d pass** out of %d simulated accounts: win rate %s, %s engage (buy or pilot). Seed %s, so the same accounts can be dealt again."
             % (res["buys"], res["pilots"], res["passes"], res["answered"], pct(res["win_rate"]), pct(res["engaged_rate"]), res["seed"]))
    if res["skipped"]:
        L.append("")
        L.append("%d of %d accounts have no valid answer and are left out: %s." % (
            len(res["skipped"]), res["dealt"], ", ".join("%s (%s)" % s for s in res["skipped"][:10])))
    L.append("")
    L.append("These are simulated committees, not customers. Use this to find blockers, objections and the price band,"
             " then confirm the big ones with real accounts (a paid pilot, a signed quote) before you hire a sales team.")
    if res["pipeline_year1"]:
        L += ["", "## What the engaged accounts are worth", ""]
        if res["annual_value_per_buyer"] is not None:
            L.append("- A buying account expects to spend **%s** in year 1 (mean)%s." % (
                money(res["annual_value_per_buyer"]),
                (", about %s of its category spend" % pct(res["share_of_wallet"])) if res["share_of_wallet"] is not None else ""))
        if res["annual_value_per_pilot"] is not None:
            L.append("- A pilot is worth **%s** (mean)." % money(res["annual_value_per_pilot"]))
        if res["sales_cycle_months"] is not None:
            L.append("- Median sales cycle: **%.0f months** from first contact to order." % res["sales_cycle_months"])
        if res["discount_expected_pct"] is not None:
            L.append("- Procurement expects a **%.0f%%** discount before signing." % res["discount_expected_pct"])
        L.append("- Year-1 value of every engaged account on this panel: %s." % money(res["pipeline_year1"]))
    for title, key in (("By segment", "by_segment"), ("By situation", "by_situation"), ("By category spend", "by_spend")):
        L += ["", "## %s" % title, "", "| group | accounts | buy | pilot |", "| --- | ---: | ---: | ---: |"]
        for k, n, b, p in res[key]:
            L.append("| %s | %d | %s | %s%s |" % (k, n, pct(b), pct(p), "  (thin)" if n < 5 else ""))
    if res["stance"]:
        L += ["", "## The committee, seat by seat", "", "| seat | for | neutral | against |", "| --- | ---: | ---: | ---: |"]
        for role, st in sorted(res["stance"].items(), key=lambda kv: -kv[1]["against"]):
            L.append("| %s | %d | %d | %d |" % (role, st["for"], st["neutral"], st["against"]))
    if res["blockers"]:
        L += ["", "## Who blocks", ""]
        for role, n in res["blockers"]:
            L.append("- %s blocked or decided %d of the %d non-buying accounts." % (role, n, res["pilots"] + res["passes"]))
    L += ["", "## Why they pass", "", "| reason | accounts | in their words |", "| --- | ---: | --- |"]
    for k, n, quotes, ids in res["why_not"]:
        L.append("| %s | %d | %s |" % (k, n, " · ".join('"%s" (%s)' % (q.replace("|", "/"), i) for q, i in zip(quotes, ids))))
    L += ["", "## Why they buy", "", "| reason | accounts | in their words |", "| --- | ---: | --- |"]
    for k, n, quotes, ids in res["why_yes"]:
        L.append("| %s | %d | %s |" % (k, n, " · ".join('"%s" (%s)' % (q.replace("|", "/"), i) for q, i in zip(quotes, ids))))
    if res["flip"]:
        L += ["", "## What would flip a pass or a pilot into a buy", ""]
        for f in res["flip"][:12]:
            L.append("- %s" % f)
    if res["price_answers"]:
        L += ["", "## Price", "",
              "%d accounts gave price answers. Median acceptable price %s, median walk-away price %s. Run b2b-pricing's pricing.py on the answers folder for the full band." % (
                  res["price_answers"], money(res["price_acceptable_median"]), money(res["price_walk_away_median"]))]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dir", default=os.path.join("b2b", "committee"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init")
    i.add_argument("--customer", required=True)
    i.add_argument("--pitch", required=True)
    i.add_argument("--n", type=int, default=16)
    i.add_argument("--seed", type=int)
    p = sub.add_parser("prompts")
    p.add_argument("--wave", type=int, default=WAVE)
    p.add_argument("--batch", type=int, default=BATCH, help="accounts per brief (one sub-agent plays them in turn)")
    sub.add_parser("check")
    sv = sub.add_parser("save")
    sv.add_argument("id")
    t = sub.add_parser("tally")
    t.add_argument("--out")
    sub.add_parser("status")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "init":
            cards = init(a.dir, a.customer, a.pitch, a.n, a.seed)
            st, _ = load_state(a.dir)
            print("dealt %d accounts (seed %s) into %s. Next: committee.py prompts" % (len(cards), st["seed"], a.dir))
        elif a.cmd == "prompts":
            waves = write_briefs(a.dir, a.wave, a.batch)
            n = sum(len(w) for w in waves)
            if not n:
                print("every account has a valid answer. Next: committee.py tally")
            else:
                print("%d briefs in %d waves of up to %d (%d accounts per brief). Launch one wave at a time:" % (n, len(waves), a.wave, a.batch))
                for k, w in enumerate(waves, 1):
                    print("wave %d: %s" % (k, " ".join("%s=%s" % job for job in w)))
        elif a.cmd == "check":
            probs = check(a.dir)
            if not probs:
                print("all answers present and valid")
            for pid, prob in probs:
                print("%s: %s" % (pid, prob))
            return 1 if probs else 0
        elif a.cmd == "save":
            print("saved %s" % save(a.dir, a.id, sys.stdin.read()))
        elif a.cmd == "tally":
            res = tally(a.dir)
            text = results_md(res)
            out = a.out or _path(a.dir, "results.md")
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(text)
            _write_json(_path(a.dir, "results.json"), res)
            print("%d buy · %d pilot · %d pass (win rate %.0f%%). Wrote %s" % (
                res["buys"], res["pilots"], res["passes"], res["win_rate"] * 100, out))
        elif a.cmd == "status":
            st, cards = load_state(a.dir)
            probs = check(a.dir)
            print("%d accounts dealt (seed %s), %d answered, %d to go" % (len(cards), st["seed"], len(cards) - len(probs), len(probs)))
    except PanelError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
