---
name: b2b-ops
description: >-
  Your operations manager for a B2B business. Works out how it actually runs
  from the first order: suppliers and their terms, inventory and procurement
  rules, the order-to-cash cycle (quote, order, delivery, invoice, collection),
  quality and traceability, who does what, the tools (ERP, CRM, quoting), the
  certifications, licences and import rules to check, delivery capacity, and a
  risk register with what to do when each thing goes wrong. Feeds real costs
  and real terms back to the CFO. Use when the user says "how do I run this",
  "operations", "suppliers", "inventory", "staffing", "SOPs", "certifications",
  "what do I need to start", or "order to cash".
argument-hint: "[region or country]"
---

# b2b-ops

A plan that works on paper fails on the first late shipment with a customer's
line down. This skill makes sure the first order, month and quarter can
actually be run, that the terms in the CFO's numbers are the terms suppliers
and customers will really sign, and that the promises in the offer can be kept.

## Step 1: the order-to-cash cycle

From `b2b/idea.md`, `b2b/offer.md` and `b2b/numbers.json`, write the cycle as
steps with an owner and a time: enquiry → quote → order confirmation →
sourcing or production → quality check → delivery → invoice → collection →
after-sales. Mark which steps the account sees, which seat it touches
(procurement for the PO, the engineer for the spec, finance for the invoice),
and where the days in `receivable_days`, `inventory_days` and `payable_days`
come from. If the cycle says customers will pay in 60 days and numbers.json
says 30, fix numbers.json and say the CFO should re-run.

## Step 2: suppliers and terms

For every input in the CFO's direct costs and every piece of equipment: two
or three real suppliers or channels the user can contact, their public prices
or how to get a quote, minimums, lead times, payment terms and the proof of
origin or quality they provide. Link the sources. Where only a quote will tell,
say so and add it to the open questions. Supplier credit is working capital:
record the terms you can realistically get as a new account (usually payment
up front at first).

## Step 3: inventory and capacity

- Distribution: which lines to stock (the fast movers for the beachhead's
  BOMs), reorder points, safety stock for the lead-time guarantee in the
  offer, dead-stock rules. The stock value this implies goes to `startup` and
  `inventory_days`.
- Manufacturing: capacity per shift, changeover, yield, raw material lead
  time, maintenance. `capacity_per_month` comes from here.
- Deal / integrator: engineering hours per project, how many projects run at
  once, subcontractor bench. `capacity_per_month` comes from here.

## Step 4: quality, traceability and compliance

What the committee's quality seat will ask for and how it is produced: lot
traceability, certificates of conformance, test reports, inspection steps,
returns and non-conformance handling. The certifications, licences and
registrations to check for the business and the product where the user is
(company registration, tax and VAT, import licences and customs codes, ISO
9001, product standards such as CE / UL / EN 13432 / ASTM D6400, industry
registrations). Give the authority and the link for each; the user confirms.

## Step 5: people and tools

Who does what in the first month and at plan volume: roles, hours, the wage
assumption with a public source. Which role is the single point of failure.
The tools to run it (quoting, CRM, ERP or inventory, accounting, e-invoicing
where required) with public prices, preferring the smallest set that works.

## Step 6: the risk register

Ten to fifteen risks, each with likelihood, impact, the early signal and the
response: a supplier fails, a shipment is late with a customer's line down, a
counterfeit or a non-conforming batch, a customer does not pay, a key engineer
leaves, a certification lapses, currency or duty changes, the incumbent cuts
price, capacity is hit earlier than planned.

## Rules

- Real suppliers, real terms, linked. Mark every estimate.
- Every cost and every term found here updates `b2b/numbers.json`; say so and
  say the CFO should re-run.
- Licences, standards and labour rules depend on where the user is; say once
  that the authority or a professional confirms them.

## Output

`b2b/ops.md`, updates to `b2b/numbers.json`. Next: `/b2b-cfo` re-run, then
`/b2b-launch`.
