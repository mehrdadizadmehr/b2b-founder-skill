---
name: b2b-committee
description: >-
  The buying-committee panel. Deals a panel of simulated ACCOUNTS (default 16,
  --quick for 8, --full for 40) from the user's ideal customer profile, each a company with a
  size, a category spend, a current supplier situation and an objection, and a
  buying committee inside it (procurement, engineering, quality, finance...).
  A sub-agent plays the whole committee of an account (four accounts per
  sub-agent by default, so a run is four cheap calls), holds the purchase
  meeting on the same pitch, and files buy, pilot or pass with the expected
  annual value, the sales cycle, who blocked and the price it would accept.
  Tallies win rate by segment and situation, the blocking seats, the objections
  in the committee's words and the price band for b2b-pricing. Use when the user
  says "would companies buy this", "test it on customers", "run the panel",
  "simulate buyers", "who is my customer", "validate demand", or "ICP".
argument-hint: "[--quick | --full | --n N] [--batch K] [--seed S]"
---

# b2b-committee

The part that replaces guessing. A B2B sale is won or lost in a meeting the
vendor never attends: procurement, the engineer, quality and the budget owner
arguing about you. This skill runs that meeting in sixteen different
companies drawn from your ideal customer profile (eight for a first look, forty
for a full run). You are the moderator. You never answer for an account.

It is sized for a personal Claude plan. A B2B market is small and its variety
lives inside the account, not between accounts, so more committees stop
teaching you anything after about 3 to 5 per segment x situation that matters.
Spend the budget on a truer customer profile instead.

What the user typed after `/b2b-committee`: `$ARGUMENTS`

## The tool

All bookkeeping goes through `committee.py` in this skill's folder:

```bash
python3 "${CLAUDE_SKILL_DIR}/committee.py" <command>
```

Below, `PANEL` means exactly that. If the path is not expanded, use the base
directory Claude Code printed for this skill. State lives in `b2b/committee/`.

## Step 1: the ideal customer profile

Write `b2b/customer.json` (shape: `customer.example.json` in this folder):

- `business`, `currency`, and `target`: who the buying account is, one specific
  line (industry, size, what they buy today and from whom).
- `segments`: 2 to 4 account types with a `share`, `employees` [low, high],
  `annual_spend` [low, high] on this category, and a `how` line.
- `roles`: the 2 to 6 seats on the buying committee, each with what it `cares`
  about. These are the same for every account; they are the people who decide.
- `situations`: 3 to 6 supplier situations with a `share` and a `how` line
  (loyal to the incumbent, just burned, buys from many wholesalers, new
  project with no supplier yet, bound by a framework contract...).
- `objections`: the 5 to 10 things these committees really say to a new vendor.
- `triggers` (optional): what starts a search for a new supplier.
- `regions` (optional): where the accounts are.

Ground it in something real. Use what the user knows about their accounts, and
if `/b2b-competitors` ran, the complaints in `b2b/competitors.md`. If the user
has real data (lost-deal notes, RFQs, support tickets, CRM exports), prefer it
to your guesses and say which parts are guesses. Show the user the profile in a
few lines and let them correct it before you deal: a wrong account profile makes
the whole panel wrong.

## Step 2: the pitch

Write `b2b/pitch.md`: what the committee would actually see on first contact.
What is sold, in what unit, at what price, lead time, payment terms, minimums,
certifications held, warranty, how to order. Four to eight plain lines, no
superlatives, nothing the business cannot deliver on day one. Every account
sees exactly this.

## Step 3: size the panel

Count the segments and situations in `b2b/customer.json` that the user cares
about and allow 3 to 5 accounts for each pair that matters; the dealing keeps
the shares, so rare pairs get one or two and common ones more. In practice:

| mode | accounts | sub-agents (batch 4) | when |
| --- | --- | --- | --- |
| `--quick` | 8 | 2 | an idea you are only thinking about |
| default | 16 | 4 | a real profile, first serious read |
| `--full` | 40 | 10 (or 40 at `--batch 1`) | you have budget and want the segment table dense |

Tell the user the size and the number of sub-agent calls in one line before you
deal; they may change it with `--n`.

## Step 4: deal and run

```bash
PANEL init --customer b2b/customer.json --pitch b2b/pitch.md --n 16
PANEL prompts --batch 4
```

`init` deals the account cards (same seed, same accounts; the seed is recorded).
`prompts --batch 4` writes one brief per four accounts and lists them in waves
of 8. One sub-agent holds the four meetings in turn and writes four answer files;
the pitch and the committee are sent once instead of four times, which is where
the saving comes from. `--batch 1` gives every account its own sub-agent: more
independent, about four times the calls; use it for `--full` when the budget
allows. For each wave, send ONE message with one Agent tool call per brief in
that wave (the Agent tool is called Task in older Claude Code versions):

- `subagent_type`: `general-purpose`
- `model`: `sonnet` (a committee meeting does not need the largest model; this
  is the other half of the saving; the user can say otherwise)
- `description`: `committee <label>`
- `prompt`: `Read <brief path> and follow it exactly. It is your whole brief.`

Wait for the whole wave before the next one. After the last wave:

```bash
PANEL check      # lists missing or broken answers
PANEL prompts    # rewrites briefs for those only; run them once more
PANEL tally
```

If a sub-agent printed its JSON in its reply instead of writing the file (it
happens), file its own reply with `PANEL save <id>` and the reply on stdin;
`save` refuses anything that is not a valid answer. An account that fails
twice is left out and counted in the results. Never write an answer for an
account yourself.

Rough budget, so the user can decide: a four-account brief costs a sub-agent
about 70k tokens on sonnet and takes half a minute (measured); the default run
is 4 such calls, `--quick` 2, `--full` 10. That fits a personal Claude plan in
one sitting. Sub-agents write
one file per account into `b2b/committee/answers/`; in the default permission
mode that is one approval per file, so suggest accept-edits mode (Shift+Tab)
for the run.

If the Agent tool is not available at all (plain chat, no Claude Code), run the
briefs yourself one at a time in the conversation and file each answer with
`PANEL save <id>`. Say plainly that the answers are then less independent,
because the moderator and the committee are the same model in the same thread.

## Step 5: read it to the user

`PANEL tally` writes `b2b/committee/results.md` and `results.json`. Give the
user:

1. The headline: "4 buy · 3 pilot · 9 pass", the win rate and the engaged rate.
2. What an account is worth: mean year-1 value of a buyer, share of its
   category spend, median sales cycle, the discount procurement expects.
3. Who buys and who doesn't: the segment and situation rows that differ most.
   The segment with the highest buy rate is the beachhead candidate.
4. Who blocks: the seat that killed most deals, and what it cares about.
5. Why they pass: the top three reasons with one quote each, as written.
6. What would flip a pass or a pilot: the most repeated answers (references,
   a certification, payment terms, a trial order).
7. One sentence on what to change before spending a sales cycle, and which
   skill does it (pricing, offer, gtm).

## Honest limits, say them once

These are simulated committees. They are good at surfacing objections, blocking
seats, segments and wording you had not thought of, and bad at predicting real
win rates: language models lean agreeable, so treat the win rate as an upper
bound and the sales cycle as a lower bound. Confirm the big calls with real
accounts (a paid pilot, a letter of intent, a quote they sign) before hiring
a sales team or buying stock. Do not present panel quotes as customer
testimonials.

## The brief every account gets

`committee.py` fills the card into a fixed template (see `BRIEF` and
`BATCH_BRIEF` in the script): the account (segment, size, spend, situation, trigger, region, the
first objection), every committee seat and what it cares about, the pitch word
for word, an instruction to hold the meeting honestly and not to invent facts
about the vendor, and the exact JSON to write: outcome, annual value, sales
cycle, reason code, reason, blocker seat, objection, what would change its mind,
each seat's stance, and three price answers (acceptable, walk-away, expected
discount). Never edit a brief for one account.

## Output

`b2b/customer.json`, `b2b/pitch.md`, `b2b/committee/` (accounts, briefs,
answers, results). Next: `/b2b-pricing` reads the price answers, `/b2b-offer`
and `/b2b-gtm` read the objections and the blocking seats.
