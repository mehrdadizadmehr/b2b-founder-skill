---
name: b2b-launch
description: >-
  Your launch lead for a B2B business. Builds a dated, step-by-step launch
  plan: a cheap real-world test first (paid pilots, sample orders, letters of
  intent or signed quotes from real accounts, so real committees confirm what
  the simulated panel said), then the countdown to the first delivery with
  owners and deadlines, the first-order run sheet, and the first 90 days of
  what to measure and what to change. Use when the user says "how do I launch",
  "launch plan", "when can I start", "pilot", "first customers", "go live", or
  "soft launch".
argument-hint: "[target first-delivery date]"
---

# b2b-launch

Launching is a project with a date, and in B2B the cheapest test is a real
account paying for a small version. This skill turns everything else in the
pack into a dated plan, starting with the test that must pass before the big
money (stock, a machine, a sales hire) goes out.

## Step 1: test before you spend

Pick the cheapest real test that fits the model, and run it before signing the
big costs in `b2b/numbers.json`:

| model | the test |
| --- | --- |
| distribution | ten beachhead accounts, each a paid sample order at the list price from a small starter stock; measure reorders in 60 days |
| deal / integrator | three paid pilots or paid feasibility studies at the planned day rate, with a signed scope |
| manufacturing | five signed letters of intent or trial-order POs at the target price, plus a tolled or outsourced first batch before the line is bought |
| B2B software | five accounts paying for a founding-member contract before the feature set is finished |

Write the success line before running it (for example: 5 of 10 sample accounts
reorder within 60 days at or above the target net price), and compare the
result with the panel's win rate (`b2b/committee/results.md`). If real
committees fall well short of the panel, trust the real committees and go back
to `/b2b-offer` or `/b2b-pricing`.

## Step 2: the countdown

From today to the first delivery, with real dates (ask for the target date;
default to the earliest realistic one given lead times and certifications in
`b2b/ops.md`). Weekly blocks, each task with an owner and a deadline:

- Legal and registration, bank, insurance, certifications in progress (from
  `b2b/ops.md`).
- Suppliers signed, starter stock or first materials ordered, with lead times.
- The offer, the proposal template, the website pages a committee checks
  (from `b2b/offer.md`, `b2b/brand.md`).
- The target-account list and the first outbound wave (from `b2b/gtm.md`).
- The pilot accounts: who, what they buy, what they pay, what they agreed to
  give back (a reference, feedback, a reorder decision date).
- Operations ready: the order-to-cash steps tested end to end on one internal
  order.

## Step 3: the first-order run sheet

Hour by hour for the first real order: who confirms it, who sources it, the
quality check, the paperwork (certificate, delivery note, invoice with the
agreed terms), the delivery, the follow-up call, what gets logged. The second
run sheet: the first thing that goes wrong (a late part, a wrong spec) and
who calls the account.

## Step 4: the first 90 days

What to measure weekly and the number that means "change something":

- Pipeline: accounts contacted, meetings, samples or pilots, proposals, orders,
  by segment, against the panel's win rate and the funnel in `b2b/gtm.md`.
- Orders: value, margin per order against `b2b/cfo.md`, on-time delivery,
  non-conformances.
- Cash: receivable days actually experienced against `numbers.json`, overdue
  invoices, stock days.
- Which committee seat blocked each lost deal, in their words; feed it back to
  `/b2b-offer`.

Three review points (day 30, 60, 90) with the decision each one makes: keep
the beachhead, change the seat you enter through, change the price or terms,
or stop.

## Rules

- Dates are real dates. Owners are named roles.
- No launch before the test in step 1 has a result, unless the user decides
  otherwise; then say so in the plan.
- Contracts, pilots and letters of intent have legal weight; say once that a
  lawyer should read the templates.

## Output

`b2b/launch.md`. Next: `/b2b-plan` to compile everything with the verdict.
