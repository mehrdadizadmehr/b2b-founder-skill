---
name: b2b-pricing
description: >-
  Finds the price buying committees will actually sign. Reads the committee
  panel's three price answers per account (fair price, walk-away price,
  expected discount) into an acceptance curve and a band, sets it against what
  competitors charge and against the CFO's floor, and recommends a list price,
  a volume or tier ladder, payment-terms pricing and an opening offer to test.
  Use when the user says "how much should I charge", "price this", "is $X too
  expensive", "pricing strategy", "what price", "discount policy", "tender
  price", or after the committee panel.
argument-hint: "[current price]"
---

# b2b-pricing

Price is the fastest lever on the margin and the one founders guess most. In
B2B it is also negotiated: the list price, the price procurement pushes to, the
payment terms and the volume tiers are all one decision. This skill sets it from
three things you can check: what committees said, what competitors charge, and
what the business needs to earn.

Tool in this folder:

```bash
python3 "${CLAUDE_SKILL_DIR}/pricing.py" b2b/committee/answers --price 850 --floor 780 --competitors b2b/competitors.json --out b2b/pricing-curve.md
```

## Step 1: what committees said

If `/b2b-committee` ran, every account answered three price questions. Run the
tool on `b2b/committee/answers` (or a CSV with the columns `price_acceptable,
price_walk_away, discount_expected_pct` from real quotes and lost deals, which
beat simulated answers every time). It reports:

| output | meaning |
| --- | --- |
| Fair price (quartiles) | what the committee would call fair |
| Walk-away price (quartiles) | above this they stop talking |
| Acceptance curve | at each price: who calls it fair, who is still in the conversation |
| Expected discount | what procurement will push for; the list price to land at the fair median after it |
| Ceiling | the highest price that keeps `--keep` (default 60%) of accounts in the conversation |
| Band | from the CFO's floor (or the fair median) to the ceiling |

If the panel has not run, say so and offer `/b2b-committee --quick` first. Do
not invent a band.

## Step 2: the floor

From `b2b/numbers.json` if `/b2b-cfo` ran: the price at which the contribution
per unit still covers the margin the plan needs. Pass it as `--floor`. If the
floor is above the ceiling, say so first: the business as priced loses the
accounts it needs. The fixes are a cheaper unit cost, a different unit (bundle,
annual contract, volume tier), or a segment with a higher walk-away price.

## Step 3: what competitors charge

From `b2b/competitors.json` (or look them up now, from their own published
prices, tender awards and price signals, each with a link). Place the band
against them. Being cheaper than the catalogue giant and dearer than the cash
wholesaler is a position; say what the account gets for the difference.

## Step 4: the decision

Write `b2b/pricing.md`:

- **List price** and the **target net price** after the discount procurement
  expects. Never publish the net price as the list price; B2B buyers negotiate
  down, never up.
- **The ladder**: volume tiers or good / better / best (basic order, with
  terms, with a framework contract and priority stock), each priced from the
  band and the floor. Say what each tier adds and what it costs to deliver.
- **Terms pricing**: the price for payment on order, net 30 and net 60, derived
  from the CFO's receivable-days cost. Terms are money; price them.
- **Tender and framework pricing** if the segment buys that way: the walk-away
  quartiles tell you what a winning bid looks like.
- **Discount policy**: who may give what, and what the account gives back
  (volume commitment, a reference, payment up front).
- **The opening offer to test** on the first ten real accounts, and the number
  that says it worked (quotes signed at or above the target net price).

## Rules

- Every price traces to the curve, a competitor's link or the CFO's floor.
- Revenue is before tax; say if the market adds sales tax or withholding.
- Say once: simulated committees; real quotes replace them as soon as there
  are five.

## Output

`b2b/pricing-curve.md`, `b2b/pricing.md`. Next: `/b2b-offer` builds the
offer around the price; `/b2b-cfo` re-runs with the new price.
