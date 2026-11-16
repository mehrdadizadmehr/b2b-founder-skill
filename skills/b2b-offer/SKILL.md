---
name: b2b-offer
description: >-
  Builds the offer a buying committee can say yes to. Lists every obstacle each
  seat (procurement, engineering, quality, finance, the end user) hits between
  first contact and a signed order, turns each into a part of the offer (a
  paid pilot, a sample order, a certificate pack, payment terms, a service
  level, a guarantee the CFO can afford, references), scores it on the value
  equation and the whole-product checklist, and re-tests it on a quick
  committee panel. Use when the user says "make my offer better", "why won't
  they buy", "what should I include", "guarantee", "pilot", "SLA", "the
  proposal", or after the panel shows committees passing.
argument-hint: "[what you sell]"
---

# b2b-offer

Most B2B vendors sell a product. Good ones sell an offer: the product plus
everything that makes the purchase meeting an easy yes for every seat in the
room. This skill builds that, using the Chasm lens's whole-product idea and
the value-equation method from `../b2b-board/lenses.md` and the consumer offer
tradition (a summary of the framework in Alex Hormozi's *$100M Offers*, adapted
to committees; never present it as his words).

## Step 1: read what is already known

- `b2b/idea.md` and `b2b/pitch.md`: what is sold today.
- `b2b/committee/results.md`: why committees pass, in their words; which seat
  blocks. This is the raw material: every top objection and every blocking
  seat should be answered by something in the offer.
- `b2b/numbers.json`: what each extra costs, so the stack stays profitable.
- `b2b/board.md`: the board's conditions.
- `b2b/pricing.md`: the band and the terms pricing.

## Step 2: the problem list, seat by seat

For each committee seat, every obstacle between it and a signed order, in its
words: before buying (never heard of you, vendor approval, no references, wrong
payment terms), during (lead time, integration, training, downtime during
switch), after (what if a part is wrong, who answers the phone, what if you go
out of business). Aim for 15 to 30 across the seats. Pull from the panel
objections and the competitor complaints first.

## Step 3: solutions, trimmed and stacked

Turn each problem into a solution, then keep the ones that are cheap to deliver
and valuable to that seat:

| B2B offer part | answers | costs |
| --- | --- | --- |
| Paid pilot or sample order at a fixed price | risk, "who are you" | margin on a small order |
| Certificate pack and traceability on every delivery | quality's objection | admin time |
| Net 30 after two orders, net 60 for framework accounts | procurement | the CFO's receivable days |
| Stock reservation or a service level with a credit if missed | engineering, plant | safety stock, a reserve |
| Named reference accounts in the same segment | everyone | asking the first three customers |
| Onboarding: vendor forms filled, parts cross-referenced, first BOM free | switching cost | hours |
| A guarantee the CFO can afford (replace within 48h, credit for late delivery) | risk | priced in numbers.json |
| Exit terms: no lock-in for the first year | finance | nothing |

Score the stack on the value equation: the outcome the account gets, how
likely it looks (proof, references, certifications), how long until it works,
and how much effort the switch asks. Most B2B offers fail on likelihood (no
proof) or effort (vendor approval and requalification). Say which part moves
which lever.

## Step 4: urgency and the name

Real urgency only: a pilot slot count the business can actually serve, an
onboarding window before a season or a price-list change, a founding-account
price for the first N accounts with a stated end. Never fake scarcity. Give
the offer a name a procurement manager could write in a purchase order.

## Step 5: the proposal skeleton

Write the offer as the account would receive it: one page, the unit, the
price and terms from `b2b/pricing.md`, what is included, the pilot, the
guarantee, the references, the next step. This is `b2b/pitch.md` version 2.

## Step 6: re-test

Update `b2b/pitch.md` with the offer and re-run `/b2b-committee --quick` with
the same seed (`--seed` from `b2b/committee/panel.json`) into a new folder:
`committee.py --dir b2b/committee-v2 init ...`. Compare the win rate, the
engaged rate and the blocking seats to the first run. Report the change
honestly, including a stack that did nothing.

## Rules

- Every offer part costs something; put the cost in `b2b/numbers.json` (a
  variable cost, a fixed cost or receivable days) and say the CFO should re-run.
- Promise only what the operations plan can deliver (`b2b/ops.md`).
- Guarantees and SLAs have legal weight; say once that a lawyer should read them.

## Output

`b2b/offer.md`, `b2b/pitch.md` (updated), `b2b/committee-v2/` if re-tested.
Next: `/b2b-cfo` with the offer's costs, `/b2b-gtm` to take it to the accounts.
