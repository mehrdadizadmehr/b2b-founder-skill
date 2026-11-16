---
name: b2b-competitors
description: >-
  Maps who already sells to the target accounts and the gap they leave. Finds
  the direct competitors, the indirect ones, the in-house alternative and
  "do nothing", from public sources only, and records what each sells, list
  prices or price signals, lead times, payment terms, certifications, channel,
  how they position themselves and what their customers complain about, every
  fact with a link. Ends with a positioning map, a competitor price file for
  b2b-pricing and the gap the new business can own. Use when the user says "who
  are my competitors", "is this market crowded", "who else supplies them",
  "competitor analysis", "find the gap", or "who am I up against".
argument-hint: "[region or market]"
---

# b2b-competitors

Every target account already solves this somehow: an incumbent supplier, an
in-house team, a catalogue giant, or living with the problem. This skill finds
out how, what they pay, what they put up with, and what would make them switch.

## The rules

- **Public sources only, every fact linked.** Company websites, price lists and
  catalogues, distributor portals, tender archives and award notices, trade
  directories, LinkedIn company pages (headcount, roles hired), trade-press,
  review sites, forum threads, annual reports. If a source cannot be reached,
  say so. Never invent a competitor, a price, a certification or a quote.
- **Read, do not scrape.** Read pages as a person would. Respect each site's
  terms.
- **Quotes are verbatim**, short, with the link. They are research, never
  testimonials.
- **Price signals count.** B2B prices are often hidden. Record what you can:
  list prices, tender awards, "from" prices, distributor margins, a competitor's
  revenue divided by its customer count, a job ad that reveals deal sizes. Mark
  each as list / observed / inferred.

## Step 1: who is there

From `b2b/idea.md` (write it first if missing; see `/b2b-board` step 0):

| type | what it means | example for an electronics distributor |
| --- | --- | --- |
| Direct | sells the same thing to the same accounts | other local component distributors |
| Indirect | a different route to the same job | the international catalogue giants, brokers |
| In-house | the account does it itself | the buyer's own purchasing team sourcing from 10 wholesalers |
| Do nothing | the account lives with the problem | over-ordering safety stock to cover late deliveries |

Aim for 5 to 10 direct and indirect, plus the in-house and do-nothing options
described honestly. For an integrator or a manufacturer add the OEM's own
service arm and the account's existing contractors.

## Step 2: what each one is

For every competitor, a card in `b2b/competitors.md`:

- What they sell and to whom (segments, account sizes, regions).
- Price signals, with the type (list / observed / inferred) and the link.
- Lead time, minimum order, payment terms, warranty, certifications (ISO, CE,
  UL, EN 13432, vendor partner status) as published.
- Channel: direct sales, distributors, online, tenders.
- How they position themselves, in their own words (the homepage headline).
- Size signals: headcount, years in business, notable customers they name.
- What their customers complain about, verbatim with links: late deliveries,
  counterfeit parts, no local support, slow quotes, rigid minimums.

## Step 3: the price file

Write `b2b/competitors.json`, a list of `{"name", "price", "note"}` in the same
unit as the idea's price (an order of a defined basket, a project of a defined
scope, a tonne). `b2b-pricing` reads it. Only include prices you can link or
clearly infer; put the method in `note`. Example in this folder:
`competitors.example.json`.

## Step 4: the map and the gap

- A positioning map on the two axes the accounts care about most (from the
  complaints: price vs lead time, breadth vs traceability, local support vs
  catalogue size). Place each competitor and the new business.
- The gap: the segment and the job where the complaints cluster and no
  competitor is strong. Say which committee seat feels it (the engineer, the
  quality manager, procurement). Say honestly if there is no gap.
- Switching costs the accounts face (vendor approval, requalification,
  integration) and how competitors lock accounts in.
- Three open questions only a real account can answer; `b2b-committee` asks them.

## Output

`b2b/competitors.md`, `b2b/competitors.json`. Then say the gap in one line and
suggest `/b2b-committee` to see whether the accounts agree.
