---
name: b2b-brand
description: >-
  Your brand designer for a B2B company. Names the business (with the
  trademark, domain and company-register checks to run before falling in love
  with a name), writes the voice a procurement manager and an engineer both
  trust, a one-line promise, and briefs the look: the website a committee
  checks before replying, the proposal and datasheet templates, the
  certificates page, trade-show stand and vehicle livery if relevant. Use when
  the user says "name my company", "brand this", "logo", "brand identity",
  "what should the website say", "tagline", or "brand voice".
argument-hint: "[name ideas, if any]"
---

# b2b-brand

In B2B, brand is the answer to "who are these people?" asked by a committee
that has never met you. This skill makes the name, the voice and the look
specific to the positioning the pack already found, not a mood board.

## Step 1: read the brief

`b2b/idea.md`, `b2b/gtm.md` (the positioning line, the beachhead, the message
per seat), `b2b/competitors.md` (names and looks to stay clear of), and the
panel's trust objections (`b2b/committee/results.md`). If the positioning is
missing, ask for it or run `/b2b-gtm` first.

## Step 2: name candidates

Ten candidates across styles (descriptive, evocative, invented, the founder's
name, a place, an acronym the industry would use). For each: what it says, how
it sounds on the phone to procurement, how it reads on a purchase order, a
datasheet header and a van, and the risk. B2B names must be spellable after
hearing them once. Shortlist three and run the checks the user must finish
themselves:

- **Trademark**: search the official register for each market in the class of
  goods and services (USPTO, EUIPO, UKIPO, CIPO, WIPO Global Brand Database;
  the national office where the user is). Give the search links and classes.
- **Company register**: the name is free to register as a company where the
  user is.
- **Domain**: the .com and the local domain (check, do not assume); alternatives.
- **Handles**: LinkedIn company page first; others as the channel needs.
- **Confusion**: no name close to a competitor in `b2b/competitors.md` or to a
  well-known brand in the industry.

## Step 3: voice and promise

- The promise: one line, what the account can count on (what the offer
  guarantees, from `b2b/offer.md`), no superlatives.
- The voice: three adjectives and three "never" rules, with one example
  sentence each as it would appear in a quote email, a datasheet and a
  LinkedIn post. Engineers distrust marketing language; procurement distrusts
  vagueness. Write for both.
- The tagline, if one is earned; many B2B brands are better without.

## Step 4: the look

A brief a designer could start from:

- Colours and type: trust and clarity over fashion; legible on a datasheet and
  a stand banner. Note what the competitors use so the new brand reads apart.
- The logo: works in one colour on a packing label, an invoice and a stamp.
- The website a committee checks before replying: the pages they look for
  (what you sell, certifications and quality, references, lead time and terms,
  who you are, how to request a quote). Which objection each page answers.
- Templates: quote and proposal, datasheet or spec sheet, certificate of
  conformance, invoice. The same name, number and terms everywhere.
- Physical: packaging and labels, the trade-show stand, vehicle livery, if the
  business has them.

## Rules

- No invented awards, certifications or client logos. "Trusted by" needs real
  accounts that agreed.
- Trademarks, company names and claims (organic, compostable, certified) are
  legal matters; say once that a professional confirms them where the user is.

## Output

`b2b/brand.md`. Next: `/b2b-ops` (how it runs) or `/b2b-launch` (the first
pilot).
