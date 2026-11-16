---
name: b2b-cfo
description: >-
  Your CFO for a B2B business. Builds the unit economics before money is spent,
  for three business models: deal (projects, contracts, B2B software),
  distribution (reselling orders with stock) and manufacturing (units, batches,
  tonnes). Reports what one unit earns after direct costs, the profit margin at
  plan, the break-even volume, year 1 month by month, the working capital that
  customers' payment terms and stock tie up, the cash needed, the cost of winning
  an account (CAC), what an account is worth (LTV) and the CAC payback, with
  what-ifs for price, volume, costs and slower-paying customers. Every number
  traces to an input the user can check. Use when the user says "do the
  numbers", "is this profitable", "break-even", "unit economics", "how much do I
  need to start", "CAC", "working capital", or "run the CFO".
argument-hint: "[path to numbers.json]"
---

# b2b-cfo

The person who asks "and when do they pay?" B2B businesses die of working
capital more often than of margin: the customer pays in 60 days, the supplier
wants it in 30, and the stock sits in between. This skill finds the margin,
the cash and the cost of a customer, with every number traceable to an input.

Tool in this folder:

```bash
python3 "${CLAUDE_SKILL_DIR}/b2b_economics.py" b2b/numbers.json --out b2b/cfo.md
```

## Step 1: pick the model

| model | one unit is | examples | typical trap |
| --- | --- | --- | --- |
| `deal` | a project, a contract, a contract-year | an automation integrator, an engineering service, B2B software | lumpy revenue, long sales cycle, 60-day invoices |
| `distribution` | an order | a components distributor, an industrial supplies reseller | thin margin, stock days, credit to customers |
| `manufacturing` | a tonne, a batch, a piece | a packaging maker, a parts producer | capex, capacity, raw material terms |

## Step 2: gather the inputs

Write `b2b/numbers.json` (shape: the three `example-*.json` files in this
folder). It needs:

| field | what goes in it |
| --- | --- |
| `model`, `unit`, `currency` | see above |
| `price` | revenue per unit before tax (average deal value, average order value, price per tonne) |
| `gross_margin_pct` or `variable` | the direct cost of ONE unit: hardware at cost, materials, freight, duties, subcontractors, commissions, card fees |
| `fixed_monthly` | paid every month regardless: rent, non-sales salaries, software, insurance, warehouse |
| `sales_marketing_monthly` | the cost of winning accounts: sales salaries and commissions, trade shows, ads, travel, proposal time. Kept apart so CAC can be computed; counted as fixed too |
| `startup` | one-off spend before the first sale: machines, first inventory, certifications, deposits, legal, website |
| `plan_per_month` | units a month once up and running |
| `ramp_per_month` | 12 numbers: realistic units in each month of year 1 |
| `capacity_per_month` | the most units a month you can deliver, if there is a limit |
| `receivable_days` | days customers take to pay (DSO). Ask; B2B is rarely 0 |
| `inventory_days` | days of stock held (DIO) |
| `payable_days` | days you take to pay suppliers (DPO) |
| `new_customers_per_month` | new accounts won a month at plan (for CAC) |
| `customer_years` | how long a won account keeps buying (for LTV) |

Where the numbers come from, in this order:

1. The user's own quotes, supplier price lists, leases, the terms their market
   actually pays on (ask: "what did your last customer's invoice say, net what?").
2. Public prices the user can check (a supplier's catalogue, a landlord's
   listing, a payment processor's fees, a machine maker's list price, published
   salary bands). Write the source next to the number in `b2b/cfo-sources.md`.
3. Your estimate, clearly marked as an estimate, with the reasoning. Never
   present an estimate as a fact.

Ask the user for anything only they know. Use the price from `b2b/pricing.md`
or `b2b/pitch.md` if those exist.

**The ramp and the terms are where plans lie.** Month 1 is almost never the
plan volume; in the deal model the first order lands after a sales cycle. If
the committee panel ran, use its win rate, year-1 value per account and median
sales cycle to sanity-check the ramp and `new_customers_per_month`
(`b2b/committee/results.md`), and say how you did it.

## Step 3: run it

```bash
python3 "${CLAUDE_SKILL_DIR}/b2b_economics.py" b2b/numbers.json --out b2b/cfo.md
```

It writes: the per-unit table and contribution, fixed costs, break-even units a
month, the margin at plan, working capital at plan, CAC / LTV / LTV-to-CAC /
CAC payback, year 1 month by month with working-capital build and cumulative
cash, the cash needed before it pays for itself, the payback month, and a
what-if table (price -10%, volume -20%, unit costs +15%, customers paying 30
days later). It flags a price below direct cost, a break-even above capacity,
a losing year 1, LTV/CAC under 3, CAC payback over 18 months and working
capital bigger than the startup spend.

What-ifs without editing the file:

```bash
python3 "${CLAUDE_SKILL_DIR}/b2b_economics.py" b2b/numbers.json --price 900
python3 "${CLAUDE_SKILL_DIR}/b2b_economics.py" b2b/numbers.json --volume 0.7
python3 "${CLAUDE_SKILL_DIR}/b2b_economics.py" b2b/numbers.json --dso 90
```

## Step 4: the CFO's note

Add a short section at the top of `b2b/cfo.md`, in plain words:

- **The margin**: the profit margin at plan and the contribution per unit.
- **The cash**: how much the founder needs before it pays for itself, and how
  much of that is working capital rather than equipment. In B2B this is the
  number that surprises.
- **The customer**: CAC, LTV, payback. Whether the sales effort pays for itself.
- **The line to watch**: the one assumption that moves the result most (terms,
  the ramp, the hardware cost, the win rate), with the what-if that proves it.
- **Three ways to improve it**, each with the number it changes and by how much
  (run the what-if, do not guess): shorter terms, a deposit on order, supplier
  credit, a cheaper unit, a higher-spend segment.
- Whether the board's conditions about money (`b2b/board.md`) are met.

## Rules

- Every number in your note comes from the tool's output or an input you can
  name.
- Revenue is before tax; say if the market adds sales tax or withholding.
- Not financial, tax or legal advice. Say once that an accountant should check
  the structure, payroll, import duties and tax before money moves.

## Output

`b2b/numbers.json`, `b2b/cfo.md`, `b2b/cfo-sources.md`. Next: `/b2b-plan` uses
these numbers for the verdict; `/b2b-pricing` if the margin is thin;
`/b2b-ops` to replace estimates with supplier quotes.
