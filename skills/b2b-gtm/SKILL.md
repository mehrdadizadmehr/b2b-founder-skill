---
name: b2b-gtm
description: >-
  Your go-to-market lead. Turns the committee panel and the competitor map into
  a beachhead segment, positioning, the channel the accounts actually buy
  through (direct sales, distributors, tenders, partners, inbound), a named
  target-account list method, a 90-day outbound and content plan with dated
  steps, the first ten messages per committee seat, a sales process with stages
  and exit criteria, and the most you can spend to win an account. Every message
  answers an objection a real or simulated committee raised. Use when the user
  says "how do I get customers", "go-to-market", "sales plan", "which channel",
  "outbound", "how do I reach procurement", "marketing plan", or "positioning".
argument-hint: "[budget or target accounts per month]"
---

# b2b-gtm

A B2B business no account has heard of does not exist, and one that chases
every account at once runs out of cash in the chasm. This skill plans how the
first twenty accounts hear about it, who sells to them and how, using what the
rest of the pack learned instead of a generic playbook.

## Step 1: read the evidence

- `b2b/committee/results.md`: which segment and situation buy most (the
  beachhead), which seat blocks, the objections and what flips them.
- `b2b/competitors.md`: how competitors position and sell (so you do not sound
  like them), and the gap.
- `b2b/offer.md` and `b2b/pricing.md`: what is being sold, at what price and
  terms.
- `b2b/numbers.json` and `b2b/cfo.md`: LTV and the CAC the plan can afford.

If none of these exist, say what is missing and offer to run
`/b2b-committee --quick` first. Do not invent an audience.

## Step 2: the beachhead and the positioning

Pick one segment × one situation × one region to win first, from the panel rows
with the highest buy rate and enough accounts to matter. Then one line:

```
For <the beachhead account>, who <their problem in their words>,
<business> is the <category you chose> that <the gap>, unlike <the incumbent alternative>.
```

Give three versions, recommend one, and say which panel and competitor
evidence supports it. Then one message per committee seat: what the engineer
hears, what procurement hears, what finance hears.

## Step 3: the channel

Match the channel to the deal size and the committee:

| deal size and buyer | channel that fits |
| --- | --- |
| large, committee, long cycle | founder-led direct sales, then a seller; tenders where the segment buys that way |
| many small accounts, repeat orders | inbound (catalogue, search, marketplace listings) plus inside sales; distributors or resellers for reach |
| technical product, needs integration | partners (integrators, OEM channels), reference projects, trade fairs |
| regulated or sustainability-driven purchase | the standards body, certification listings, the account's sustainability team as the entry seat |

Say which channels the accounts in the panel actually use (from their
situations and the competitors' channels), the cost of each, and the one to
start with. Distributors take margin: put it in `b2b/numbers.json`.

## Step 4: the target-account list

How to build a named list of the first 200 beachhead accounts from public
sources (trade directories, industry associations, exhibitor lists, tender
archives, LinkedIn company search, map listings), the firmographic filters,
and the trigger events to watch (a new line, a hire, a tender, a competitor
price increase). The list itself is the user's to build; give the method and
the first filters.

## Step 5: the 90-day plan

Dated, in weekly blocks, with owners:

- Weeks 1 to 2: list, messaging per seat, one reference case (the pilot from
  `/b2b-launch`), the proposal template from `/b2b-offer`.
- Weeks 3 to 8: outbound cadence (how many accounts a week, which seat first,
  the sequence of touches), the first trade event or association meeting,
  the content that answers the top three objections (a traceability
  explainer, a lead-time guarantee page, a case study).
- Weeks 9 to 13: review win rate by segment against the panel, adjust the
  beachhead or the seat you enter through.

Ten opening messages: one per seat per channel, each answering one objection
from the panel in the account's own words. No superlatives. Nothing the offer
cannot deliver.

## Step 6: the sales process and the numbers

Stages from first contact to signed order (contact → discovery → technical
validation / sample → proposal → procurement → order), with the exit criterion
for each and the committee seat that owns it. Then the funnel math: from the
panel's win rate and median sales cycle, how many accounts must enter each
month to hit `plan_per_month`, and what that costs. The ceiling on CAC comes
from the CFO's LTV (`b2b/cfo.md`): spend less than a third of it.

## Output

`b2b/gtm.md`. Then say the beachhead and the channel in one line and suggest
`/b2b-brand` (a name and a look the segment trusts) or `/b2b-launch` (the
first paid pilot).
