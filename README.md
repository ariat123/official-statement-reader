# Official statement reader

A skill that reads a municipal bond official statement and writes a deal summary where every line cites the page it came from. A small script then checks each citation against the PDF.

**Sample output:** [North Slope Borough 2022 GO bonds, deal summary (PDF)](examples/north-slope-borough-2022/summary.pdf). Two pages of summary, then the exact quote behind every line.

## Why I built it

Before each pricing at KeyBanc, I pulled comps for our underwriter, then opened each comp's official statement to check its maturity schedule. That reading is the slow part, and it's what this skill does.

An official statement runs 150 to 300 pages, so the summary cites a page for every line. I tested it on North Slope Borough's 2022 GO offering, a deal where I led the analyst work.

## What you get

| Section | What it covers |
|---|---|
| Deal at a glance | Issuer, series and par, OS date, delivery, underwriter, advisor, counsel, paying agent |
| Security and purpose | The pledge, what can and can't pay debt service, authorization, projects |
| Structure | Coupons, maturities, yields at key years, call terms, tax status, debt service shape |
| Ratings | Each agency on these bonds, plus any rating in the document that isn't on these bonds |
| Sources and uses | Par, premium, project fund deposits, costs of issuance, underwriter's discount |
| Credit points to check | Debt after the issue, debt ratios, tax base concentration, collections, tax limits, big commitments |
| Comp profile | The keys I matched comps on (size, maturities, tax status, sale method, state, rating, security, call terms), each cited, plus the search they imply |
| Not in this document | What a reader might expect that the OS doesn't state, and where it looked |

## How it checks itself

- **Every quote must be on the page it cites.** `scripts/check_citations.py` opens the cited PDF page and looks for the exact text.
- **Every number in a line must appear in that line's quotes.** A typo like 3.902% for 3.920% fails.
- **Calculated figures are marked** and show their arithmetic.
- **Look-alikes get flagged.** The North Slope OS lists a Moody's Aa2 in its audited financials, but the 2022 bonds were rated only by S&P, Fitch and Kroll. The summary says so instead of reporting a Moody's rating.

On the sample, 36 of 36 lines pass ([check output](examples/north-slope-borough-2022/citation_check.txt)). In a test with three planted errors (a wrong yield, a wrong page and a wrong page label), the checker caught all three.

## Run it

**In an agent that takes skill files:** load `SKILL.md`, attach the official statement PDF, and ask for a summary.

**Locally** (Python 3 and `pdftotext` from poppler, no other packages):

```bash
python3 scripts/os_pages.py official_statement.pdf work/
python3 scripts/check_citations.py work/pages.jsonl examples/north-slope-borough-2022/summary.json
python3 scripts/render_summary.py examples/north-slope-borough-2022/summary.json work/summary.html
```

The North Slope official statement is public on [MSRB EMMA](https://emma.msrb.org). Search CUSIP 662523P78 and open the Official Statement. It isn't copied into this repo.

## Limits

- It doesn't pull licensed data such as MMD spreads or dealer pricing.
- It doesn't pick the comps for you. It gives the keys and the search.
- The checker proves a quote is on the cited page, not that the reading is right. A person still reviews the summary before it's used.
- The sample was written by running the skill in Claude Code on the public OS, then machine-checked.
