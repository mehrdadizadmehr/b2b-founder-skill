---
name: b2b-board
description: >-
  Your board of directors for a B2B business. Puts the idea in front of a
  three-member board, each a sub-agent reading it through one published
  framework: the Positioning lens (from April Dunford's Obviously Awesome), the
  Chasm lens (from Geoffrey Moore's Crossing the Chasm) and the Monopoly lens
  (from Peter Thiel's Zero to One). Each member scores the idea, names the risks
  that would kill it and votes fund, fund with conditions, or pass. Use when the
  user says "test my B2B idea", "would companies buy this", "pressure-test this",
  "what would a board say", "is this a good business", or starts the B2B pack on
  a new idea (a distributor, an integrator, a manufacturer, an industrial service,
  B2B software).
argument-hint: "<the business idea, or leave blank to use the conversation>"
---

# b2b-board

The first meeting. Before anyone hires a sales rep, buys stock or signs a
factory lease, three board members tear the idea apart, each from a different
angle, and vote.

What the user typed after `/b2b-board`: `$ARGUMENTS`. If that is blank, take
the idea from the conversation.

## The rule about the three names

The lenses are summaries of **published frameworks**, nothing more. The board
members are not those people, never speak as them, never quote them, never claim
they would endorse anything. Write "the Positioning lens", never "April Dunford
says". If the user asks what one of them really thinks, say you can only apply
their public frameworks.

## Step 0: the idea file

Everything in the B2B pack reads `b2b/idea.md` in the user's project. If it does
not exist, write it now from the conversation:

```markdown
# <business name, or a working name>

- What it is: one sentence.
- Who buys it: the target ACCOUNT (industry, size, region), and the seats on
  the buying committee that decide (procurement, engineering, finance, plant...).
- What it sells, at what price and in what unit: a project, an order, a tonne,
  a contract-year. Typical deal size.
- How it is sold and delivered: direct sales, distributors, tenders, online;
  lead time; payment terms the market expects.
- What the account does today instead: the incumbent supplier, in-house, nothing.
- Budget and constraints: money, time, certifications already held, anything
  already decided.
```

If the account, the committee, the unit or the price is missing, ask for those
(at most three questions in one message), then write the file. Do not invent a
budget, a market size or a competitor.

## Step 1: brief the board

Write `b2b/board/brief.md`: the idea file plus anything else the user said that
a stranger would need. **Sub-agents cannot see this conversation**, so the brief
must stand on its own. Do not add your own opinion of the idea to it.

## Step 2: convene

Launch three sub-agents in ONE message (Agent tool, `subagent_type:
general-purpose`, `model: sonnet`, one per member; a board memo is short and
does not need the largest model, and three cheap calls keep this within a
personal Claude plan), each told: `Read b2b/board/brief.md and
b2b-board's lenses.md (path below), apply ONLY the <lens> lens, and write your
memo to b2b/board/<lens>.md.` The lens file is `lenses.md` in this skill's
folder (`${CLAUDE_SKILL_DIR}/lenses.md`; if that path is not expanded, use the
base directory Claude Code printed for this skill).

If the Agent tool is not available (plain chat), write the three memos
yourself, one lens at a time, each in a fresh pass over the brief, and say so;
the disagreements will be milder than with three separate readers.

Each memo, in this shape:

```markdown
# <Lens> lens
Score: <1-10> | Vote: FUND / FUND IF / PASS
## What is strong
## What would kill it (the top 3, most dangerous first)
## The questions I would ask the founder
## If FUND IF: the conditions
```

## Step 3: the chair's summary

Read the three memos (they are short) and write `b2b/board.md`:

1. The vote, e.g. "2 fund if, 1 pass", and the average score.
2. The risks more than one member raised: these go first. In B2B they are
   usually: no beachhead segment, the incumbent can match it, the sales cycle
   is longer than the cash, working capital, a certification not yet held.
3. Every condition, merged, as a checklist the rest of the pack can tick off
   (the CFO, the committee panel and pricing will test most of them).
4. One paragraph: the strongest version of this business the board can see.
   It may differ from what the user pitched (a narrower segment, a different
   unit of sale, a channel instead of direct). Say so plainly.

Keep the members' disagreements. A board that agrees on everything was not doing
its job.

## Rules

- Score the business, not the founder.
- No made-up facts. If a lens needs a number nobody has yet (number of accounts
  in the segment, incumbent's price, cost of a sales cycle), name it as an open
  question and say which skill answers it (`/b2b-competitors`, `/b2b-committee`,
  `/b2b-cfo`).
- A PASS is a result, not a failure. Say it plainly.

## Output

`b2b/idea.md`, `b2b/board/` (brief and three memos), `b2b/board.md`. Then say
the vote in one line and suggest the next step: `/b2b-competitors` to see who
already sells to these accounts, or `/b2b-committee` to put it in front of
sixteen simulated buying committees.

## Where the pack goes next

```
board -> competitors -> committee -> pricing -> offer -> cfo -> gtm -> brand -> ops -> launch -> plan
```

Every skill can also run on its own; each reads whatever is already in `b2b/`.
