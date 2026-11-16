# The B2B Founder skill

Eleven Claude skills that test a business-to-business idea before you hire a
sales rep, buy stock or sign a factory lease. A fork of
[founder-skill](https://github.com/Jakeschincariol/founder-skill) rebuilt for
companies that sell to companies: distributors, integrators, manufacturers,
industrial services and B2B software. Free, MIT, no signup, no API key.

`skills/b2b-board` `skills/b2b-competitors` `skills/b2b-committee`
`skills/b2b-pricing` `skills/b2b-offer` `skills/b2b-cfo` `skills/b2b-gtm`
`skills/b2b-brand` `skills/b2b-ops` `skills/b2b-launch` `skills/b2b-plan`

## In plain words

Eleven colleagues who try your idea before you spend real money. They live in
Claude Code and write everything into a `b2b/` folder in your project, so each
one reads what the others wrote. Run them in this order.

1. **The board** (`/b2b-board`). You describe the idea in a few lines. Three
   board members, each using one well-known framework (positioning, crossing
   the chasm, monopoly), score it, say what could kill it and vote: fund, fund
   with conditions, or pass.
2. **Competitors** (`/b2b-competitors`). Finds who already sells to these
   customers, at what price, on what payment terms and lead times, and what
   their customers complain about. Every claim has a link.
3. **The buying committee** (`/b2b-committee`). The heart of the pack. You
   describe your ideal customer: what kind of companies, how big, how much they
   spend a year on this, who they buy from now, who sits in their purchase
   meeting and what objections they raise. The tool deals 16 imaginary
   companies from that profile. Claude sends one small helper per four
   companies to act out the purchase meeting: procurement, the engineer,
   quality and finance argue and decide. For each company you get buy, pilot or
   pass, how much a year, how many months the sale takes, who blocked it and
   what price it would accept. Then a table: which segment buys most, which
   seat blocks most, why they pass and what would change their mind.
4. **Pricing** (`/b2b-pricing`). Turns the committees' price answers into an
   acceptance curve: the fair price, the ceiling above which 40% walk away,
   the discount procurement expects, list price versus net price. Set against
   competitors and your cost floor.
5. **The offer** (`/b2b-offer`). Builds a package every seat can say yes to:
   a paid pilot, certificates, payment terms, a guarantee, references. Re-tests
   it on a quick panel.
6. **The CFO** (`/b2b-cfo`). Takes your numbers and works out what each sale
   leaves, break-even, year 1 month by month, cost to win a customer against
   what it returns, and above all **working capital**: if customers pay in 45
   days and you hold 75 days of stock, how much cash is locked up. In the
   example that ships with the pack it is five times the startup spend.
7. **Go-to-market** (`/b2b-gtm`). The first segment to win, the sales channel,
   how to build the target-account list, a dated 90-day plan, ten opening
   messages and the most you can afford to spend winning a customer.
8. **Brand** (`/b2b-brand`). Name candidates with trademark and domain checks,
   and a voice both the engineer and procurement trust.
9. **Operations** (`/b2b-ops`). Order to cash, suppliers and their terms, stock
   or capacity, quality and traceability, licences, people, risks. Feeds real
   costs back to the CFO.
10. **Launch** (`/b2b-launch`). First a test with real customers: a few paid
    pilots or signed quotes. Then the countdown and the first 90 days.
11. **The plan** (`/b2b-plan`). Compiles everything into one document and gives
    a verdict computed from the numbers, never written by hand: **Viable**,
    **Not yet** or **Incomplete**. Six checks, including a panel win rate above
    20% and customer-acquisition payback under 18 months.

**Cost.** Only the board and the committee send out helpers: 7 calls in all, on
the cheaper model. The rest is an ordinary conversation. The whole path fits a
Pro plan in one sitting.

**What it is not.** Real customers. Simulated committees are good at finding
objections, blocking seats and the price band; but models are polite, so read
the win rate as a ceiling and confirm the big decisions with five real calls.
That is why the launch skill starts with exactly that test.

**Simplest start:** `/b2b-board` with one paragraph of idea, then
`/b2b-committee --quick`. If it does not survive those two, do not run the rest.

## What changed from the consumer version

| consumer founder-skill | this pack | why |
| --- | --- | --- |
| 100 simulated buyers, one person each, 100 sub-agent calls | 16 simulated **accounts** (8 quick, 40 full), each a company with a **buying committee** (procurement, engineering, quality, finance...), four accounts per sub-agent, so **4 calls** | a B2B sale is decided in a meeting the vendor never attends, and a B2B market is small: variety lives inside the account |
| buy / pass | **buy / pilot / pass**, with expected annual value, sales cycle, the blocking seat and each seat's stance | pilots and blockers are where B2B deals live |
| Van Westendorp price sensitivity | **fair price, walk-away price, expected discount** → acceptance curve, ceiling, list vs net price, terms pricing | committees negotiate; consumers do not |
| cups per day | **three models**: deal, distribution, manufacturing, with **working capital** (receivable, inventory, payable days), **CAC, LTV, CAC payback** | B2B businesses die of payment terms and sales cost, not of margin |
| Offers / Monopoly / Product lenses | **Positioning (Dunford) / Chasm (Moore) / Monopoly (Thiel)** lenses | beachhead, whole product and the incumbent alternative are the B2B questions |
| 30-day marketing campaign | **beachhead, channel, target-account list, 90-day plan, sales stages, CAC ceiling** | direct sales, distributors and tenders, not ads |
| verdict: Profitable | verdict: **Viable** with six checks incl. LTV/CAC ≥ 3, CAC payback ≤ 18 months, committee win rate ≥ 20% | computed, never written |

## Install

As a plugin, in Claude Code:

```
/plugin marketplace add mehrdadizadmehr/b2b-founder-skill
/plugin install b2b-founder-skill@b2b-founder-skill
```

Plugin skills are namespaced (`/b2b-founder-skill:b2b-board`). Copy the folders
instead if you want plain `/b2b-board`:

```bash
cp -r b2b-founder-skill/skills/b2b-* ~/.claude/skills/
```

Project-local: copy the same folders into your repo's `.claude/skills/`. No
Claude Code at all? Paste any single `SKILL.md` at the top of a chat and it runs
as a mode. You lose the sub-agents and the Python tools, but the method works.

The tools need Python 3.8 or newer. Nothing to pip install. None touch the
network.

## The eleven

| command | job | what it does |
| --- | --- | --- |
| `/b2b-board` | Board of Directors | Three board members, each a sub-agent applying one published framework (Positioning from *Obviously Awesome*, Chasm from *Crossing the Chasm*, Monopoly from *Zero to One*), score the idea, name what would kill it and vote. |
| `/b2b-competitors` | Competitor Scout | Maps who already sells to the target accounts: direct, indirect, in-house and do-nothing, with price signals, terms, lead times, certifications, channel and what customers complain about, every fact linked. Writes the competitor price file. |
| `/b2b-committee` | Buying-Committee Panel | Deals 16 accounts from your ideal customer profile (3 to 5 per segment x situation), each with a committee inside; a sub-agent holds four purchase meetings and files buy / pilot / pass, annual value, sales cycle, who blocked and the price it would accept for each. |
| `/b2b-pricing` | Pricing Strategist | Turns the committees' price answers into an acceptance curve and a band, sets it against competitors and the CFO's floor, prices payment terms and tiers, and picks what to test. |
| `/b2b-offer` | Offer Architect | Builds the offer each committee seat can say yes to (paid pilot, certificate pack, terms, SLA, references, guarantee), scores it on the value equation and the whole product, re-tests it on the panel. |
| `/b2b-cfo` | CFO | Unit economics for deal, distribution or manufacturing: contribution, margin at plan, break-even, working capital, CAC, LTV, payback, year 1 month by month, cash needed, what-ifs incl. slower-paying customers. |
| `/b2b-gtm` | Go-to-Market Lead | Beachhead segment, positioning per committee seat, the channel the accounts buy through, a target-account list method, a dated 90-day plan, ten opening messages, sales stages, the CAC ceiling. |
| `/b2b-brand` | Brand Designer | Name candidates with trademark, company-register and domain checks, a voice engineers and procurement both trust, and a brief for the website, templates and physical brand. |
| `/b2b-ops` | Operations Manager | Order-to-cash cycle, suppliers and their terms, inventory or capacity, quality and traceability, certifications and licences, people, tools, a risk register; feeds real costs and terms back to the CFO. |
| `/b2b-launch` | Launch Lead | A real-account test first (paid pilots, sample orders, signed quotes), then a dated countdown, the first-order run sheet and the first 90 days. |
| `/b2b-plan` | Business Planner | Compiles everything into one plan with a verdict computed from the numbers: Viable, Not yet or Incomplete; plus a summary and a one-pager. |

## How to use it

Run them in this order. Each one reads what the others wrote, in a `b2b/`
folder in your project.

```
board -> competitors -> committee -> pricing -> offer -> cfo -> gtm -> brand -> ops -> launch -> plan
```

Three worked examples ship with the tools, one per model:

- **Distribution**: a locally stocked online distributor of electronic components
  for small manufacturers, average order $850 at a 22% gross margin
  (`skills/b2b-cfo/example-distribution.json`, plus the customer profile, pitch
  and competitor file in `b2b-committee/` and `b2b-competitors/`).
- **Deal**: an industrial automation integrator, $48,000 average project
  (`example-deal.json`).
- **Manufacturing**: a compostable food-packaging maker selling to food brands,
  $4,200 a tonne (`example-manufacturing.json`).

With the distribution example: each order leaves $187, break-even is 79 orders
a month, the margin at the planned 180 orders a month is 12%, year 1 makes
$73,510 on operations, a won account costs $542 and returns $2,805 (5.2x), paid
back in 7 months. And the number the consumer version would never show: at
plan, 45-day customer terms and 75 days of stock tie up $408,510 of working
capital, five times the startup spend. The founder needs about $436,000, not
$82,000. That is the B2B story, and it is why this pack exists.

Run `/b2b-committee --quick` (8 accounts, 2 sub-agent calls) on an idea you are
only thinking about to find out whether you should keep thinking about it.

## Built for a personal Claude plan

The consumer version spends 100 sub-agent calls on one panel. This pack is sized
so that the whole pipeline runs on a Pro plan in one sitting:

| step | sub-agent calls | model | rough tokens |
| --- | ---: | --- | ---: |
| `/b2b-board` | 3 | sonnet | 60–100k |
| `/b2b-committee --quick` | 2 | sonnet | 50–80k |
| `/b2b-committee` (16 accounts) | 4 | sonnet | 100–160k |
| `/b2b-committee --full` (40) | 10 | sonnet | 250–400k |
| the other eight skills | 0 | your session | a normal conversation each |

Three things make it light. Accounts are dealt 3 to 5 per segment x situation
instead of a flat 100, because objections in a buying committee saturate after
about fifteen companies. Four accounts share one brief, so the pitch and the
committee are sent once, not four times (`--batch 1` gives every account its
own sub-agent when you have the budget). And the sub-agents run on the cheaper
model, since a committee memo does not need the largest one. With no Agent tool
at all (plain chat), every skill still runs; the committee and the board are
then played in the conversation and say so.

## The tools

Four of them, all standard-library Python. None touch the network.

```bash
python3 skills/b2b-cfo/b2b_economics.py b2b/numbers.json --out b2b/cfo.md          # margins, working capital, CAC/LTV, year 1
python3 skills/b2b-committee/committee.py init --customer b2b/customer.json --pitch b2b/pitch.md --n 16
python3 skills/b2b-committee/committee.py prompts --batch 4                                      # 4 briefs, 4 accounts each
python3 skills/b2b-pricing/pricing.py b2b/committee/answers --price 850 --floor 780 --competitors b2b/competitors.json
python3 skills/b2b-plan/compile.py --dir b2b                                          # the plan and its verdict
```

**`b2b_economics.py`** reads one JSON with a `model` field (`deal`,
`distribution`, `manufacturing`) and reports contribution, break-even, margin at
plan, working capital, CAC, LTV, CAC payback, year 1 by month with cumulative
cash, cash needed, payback and four what-ifs (`--price`, `--volume`, `--dso`
for ad-hoc ones). Every number traces to an input; a missing field is an error,
never a guess.

**`committee.py`** deals account cards from your ideal customer profile (same
seed, same accounts), writes briefs with the whole committee in them (one
account per brief, or several with `--batch`), checks the answers and tallies
them by segment, situation, spend band and blocking seat. It never answers for
an account.

**`pricing.py`** reads three price answers per account (from the panel, or a
CSV from real quotes and lost deals) and reports the fair and walk-away
quartiles, the acceptance curve, the ceiling that keeps 60% of accounts in the
conversation, the list price that lands at the fair median after the expected
discount, and the position against competitors.

**`compile.py`** assembles the plan and computes the verdict from six checks.

```bash
python3 -m unittest discover -s tests -v
```

## Fine print

**The board applies published frameworks. It is not those people.** The three
lenses are short summaries, in our words, of ideas from *Obviously Awesome* by
April Dunford, *Crossing the Chasm* by Geoffrey Moore and *Zero to One* by
Peter Thiel with Blake Masters. The board never speaks as them, quotes them or
claims they endorse anything. This project is not affiliated with any of them.

**The committee panel is simulated companies, not customers.** It is a fast,
cheap way to find blocking seats, objections, the beachhead and the price band
before you spend a sales cycle. It is not a forecast: language models lean
agreeable, so read the win rate as an upper bound and the sales cycle as a
lower bound, and confirm the big calls with real accounts. `/b2b-launch`
starts with exactly that test. Panel answers are research; never use them as
testimonials.

**The numbers are only as good as the inputs.** The CFO marks every estimate
as an estimate and asks for real quotes and the terms customers actually pay
on. Check costs with suppliers and the structure, payroll, duties and tax with
an accountant.

**Research uses public sources, with links.** No invented competitors, prices,
certifications or quotes. No scraping against a site's terms.

**Not financial, legal or tax advice.** Licences, standards, trademarks,
contracts and claims depend on where you are. The skills tell you what to check
and where; a professional confirms it.

## Files

```
skills/b2b-board/        SKILL.md, lenses.md
skills/b2b-competitors/  SKILL.md, competitors.example.json
skills/b2b-committee/    SKILL.md, committee.py, customer.example.json, pitch.example.md
skills/b2b-pricing/      SKILL.md, pricing.py
skills/b2b-offer/        SKILL.md
skills/b2b-cfo/          SKILL.md, b2b_economics.py, example-deal.json, example-distribution.json, example-manufacturing.json
skills/b2b-gtm/          SKILL.md
skills/b2b-brand/        SKILL.md
skills/b2b-ops/          SKILL.md
skills/b2b-launch/       SKILL.md
skills/b2b-plan/         SKILL.md, compile.py
tests/                   the tests for every tool
```

Your own files live in `b2b/` in your project. The skills read each other's.

## Credit

A fork of [founder-skill](https://github.com/Jakeschincariol/founder-skill) by
Jake Schincariol (MIT). The buying-committee idea owes a debt to the
prospect-panel pattern in
[onewave-ai/claude-skills](https://github.com/onewave-ai/claude-skills).

## License

MIT. Take it, change it, ship it.
