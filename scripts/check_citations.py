#!/usr/bin/env python3
"""Check every citation in a summary against the official statement's pages.

For each claim in summary.json:
  1. Each cited quote must appear on the cited PDF page (whitespace, quote
     marks and dashes are normalized; nothing else is).
  2. If the page has a printed or inferred label, the cited label must match.
  3. Every number written in the claim must appear in one of its quotes,
     unless the claim is marked "derived" and shows its arithmetic in "calc".

Usage:
    python3 check_citations.py pages.jsonl summary.json

Prints one line per claim and exits 1 if anything fails.
"""

import json
import re
import sys

TRANSLATE = str.maketrans({
    "“": '"', "”": '"', "‘": "'", "’": "'",
    "‐": "-", "‑": "-", "–": "-", "—": "-", "―": "-",
    " ": " ",
})

# Numbers worth checking: money, percents, decimals, years, counts with commas.
# Tokens glued to letters ("2022A", "FY2021", "Aa2") are names, not numbers.
NUM_RE = re.compile(r"(?<![A-Za-z\d.])\$?\d[\d,]*(?:\.\d+)?%?(?![A-Za-z\d])")


def norm(s):
    s = s.translate(TRANSLATE)
    return re.sub(r"\s+", " ", s).strip().lower()


def bare(n):
    """Compare numbers without $ or %, so '$71,530,000' matches '71,530,000'."""
    return n.replace("$", "").replace("%", "").rstrip(".,")


def numbers_in(text):
    out = []
    for m in NUM_RE.finditer(text):
        tok = bare(m.group(0))
        if not tok or len(tok.replace(",", "").replace(".", "")) < 2:
            continue  # skip single digits like "1" in "Series 1"
        out.append(tok)
    return out


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    pages = {}
    with open(sys.argv[1]) as f:
        for line in f:
            r = json.loads(line)
            pages[r["pdf_page"]] = r
    summary = json.load(open(sys.argv[2]))

    failures, total = 0, 0
    for section in summary["sections"]:
        for claim in section["claims"]:
            total += 1
            problems = []
            quote_numbers = set()
            for c in claim["cites"]:
                page = pages.get(c["pdf_page"])
                if page is None:
                    problems.append(f"PDF p.{c['pdf_page']} does not exist")
                    continue
                if norm(c["quote"]) not in norm(page["text"]):
                    problems.append(f"quote not found on PDF p.{c['pdf_page']}: \"{c['quote'][:60]}\"")
                if page["label_source"] in ("printed", "inferred from next page"):
                    if str(c.get("page_label")) != page["page_label"]:
                        problems.append(
                            f"label {c.get('page_label')!r} but PDF p.{c['pdf_page']} is page {page['page_label']!r}")
                quote_numbers.update(numbers_in(c["quote"]))
            if not claim.get("derived"):
                for n in numbers_in(claim["text"]):
                    if n not in quote_numbers:
                        problems.append(f"number {n} in claim is not in any cited quote")
            elif not claim.get("calc"):
                problems.append("derived claim has no calc shown")
            if not claim["cites"]:
                problems.append("no citation")
            status = "PASS" if not problems else "FAIL"
            failures += bool(problems)
            print(f"{status}  {claim['id']:<4} {claim['text'][:70]}")
            for p in problems:
                print(f"        - {p}")
    print(f"\n{total - failures}/{total} claims passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
