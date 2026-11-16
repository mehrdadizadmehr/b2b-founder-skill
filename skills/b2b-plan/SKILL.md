---
name: b2b-plan
description: >-
  Your business planner. Compiles everything the other b2b skills wrote (the
  board's verdict, the competitors, the committee panel, pricing, the offer,
  the CFO's numbers, go-to-market, brand, operations and the launch plan) into
  one business plan with a verdict at the top that is computed from the
  numbers, never written by hand: Viable, Not yet (with the failing numbers)
  or Incomplete. Adds an executive summary and a one-page version for a
  partner, lender, supplier or investor. Use when the user says "write my
  business plan", "put it all together", "is it viable", "give me the plan",
  or at the end of the B2B pack.
argument-hint: "[--min-win-rate 0.2] [--min-ltv-cac 3] [--max-payback 18]"
---

# b2b-plan

The last step. One document a founder can act on, or hand to a partner, a
lender or a key supplier, built only from what the pack found.

Tool in this folder:

```bash
python3 "${CLAUDE_SKILL_DIR}/compile.py" --dir b2b
```

## Step 1: see what is there

```bash
python3 "${CLAUDE_SKILL_DIR}/compile.py" --dir b2b --check
```

prints the verdict and each check. The checks, all computed:

1. Each unit earns money before fixed costs (`b2b/numbers.json`).
2. Year 1 makes an operating profit.
3. The break-even fits inside capacity, if a capacity was given.
4. A won account returns at least 3x its acquisition cost (LTV/CAC), if the
   sales cost was given. Change the bar with `--min-ltv-cac` and say why.
5. CAC is paid back within 18 months, if given (`--max-payback`).
6. Enough simulated committees buy (`b2b/committee/results.json`; default bar
   20%, change it with `--min-win-rate` and say why).

If there are no numbers, the verdict is Incomplete: offer to run `/b2b-cfo`.
List the other missing sections with the skill that fills each. Do not fill a
missing section yourself from guesses.

## Step 2: the summary

Write `b2b/summary.md`, half a page, plain words:

- What the business is, who the account is and who on the committee decides,
  in two sentences.
- The verdict and the numbers behind it (margin, break-even, year 1, cash
  needed including working capital, CAC and LTV).
- What the committee panel and the board agreed on, and where they disagreed.
- The beachhead segment and the channel.
- The biggest risk and what will be done about it.
- What the founder needs to start (cash from the CFO, the first pilot from
  launch, the certification from ops).
- The one thing to do this week.

If the verdict is Not yet, the summary leads with what has to change and which
skill changes it. Never soften a failing check.

## Step 3: compile

```bash
python3 "${CLAUDE_SKILL_DIR}/compile.py" --dir b2b
```

writes `b2b/business-plan.md`: title, the verdict and its checks, the key
numbers table, the idea, then every section the pack produced (summary, board,
competition, committee panel, pricing, offer, numbers, go-to-market, brand,
operations, launch), and what is not done yet.

## Step 4: the one-pager

Write `b2b/one-pager.md` for someone deciding in two minutes: the problem the
account has, the account and the committee, the offer, price and terms, the
numbers table, the evidence (panel result, competitor gap, any real pilot or
signed quote), what the money is for (equipment vs working capital), and the
ask. Same numbers as the plan, word for word.

## Rules

- The verdict comes from `compile.py`. Never write Viable by hand, and never
  round a failing number into a passing one.
- Say once, clearly: the panel is simulated committees and the numbers are
  projections; real accounts and real quotes confirm them. Not financial,
  legal or tax advice.
- If the user wants a PDF or a deck, offer to export the plan, but keep the
  markdown as the source of truth.

## Output

`b2b/summary.md`, `b2b/business-plan.md`, `b2b/one-pager.md`. Then give the
user the verdict in one line and the one thing to do this week.
