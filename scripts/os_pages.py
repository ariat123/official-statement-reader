#!/usr/bin/env python3
"""Split an official statement PDF into pages tagged with both page numbers.

Each page gets its PDF page number (what a PDF viewer shows) and the page
label printed on the page itself (cover, i, 4, A-1-12, ...). Citations in the
summary use both, so a reader can find the page either way.

Usage:
    python3 os_pages.py official_statement.pdf out_dir/

Writes out_dir/pages.jsonl (one JSON object per page) and out_dir/pages.md
(the same text with a header line above each page, for an agent to read).
Needs `pdftotext` (poppler) on PATH.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

# A printed page label sits alone on the last line of the page:
# "4", "-i-", "A-1-12", "B-1", "D-3", "A-2-ii".
LABEL_RE = re.compile(r"^-?\s*([ivxlc]+|\d{1,3}|[A-F](?:-\d)?-(?:\d{1,3}|[ivxlc]+))\s*-?$", re.I)


def extract_pages(pdf_path):
    out = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        check=True, capture_output=True, text=True,
    ).stdout
    pages = out.split("\f")
    if pages and not pages[-1].strip():
        pages = pages[:-1]
    return pages


def printed_label(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return None
    m = LABEL_RE.match(lines[-1])
    return m.group(1) if m else None


APPENDIX_RE = re.compile(r"^APPENDIX\s+([A-F](?:-\d)?)\b")


def build(pdf_path):
    pages = extract_pages(pdf_path)
    labels = [printed_label(p) for p in pages]
    records = []
    appendix = None
    for i, text in enumerate(pages):
        m = APPENDIX_RE.match(text.strip())
        if m:
            appendix = m.group(1)
        label, how = labels[i], "printed"
        if label is None:
            # Page 1 of the body often has no number printed. If the next
            # page says "2", this one is "1".
            nxt = labels[i + 1] if i + 1 < len(labels) else None
            if nxt and nxt.isdigit() and int(nxt) > 1:
                label, how = str(int(nxt) - 1), "inferred from next page"
            elif i == 0:
                label, how = "cover", "first page"
            else:
                label, how = "unnumbered", "none printed"
        # Inside an appendix that restarts its own numbering (an audit report
        # is "15", not "D-15"), prefix the appendix so the label is unique.
        if appendix and (label.isdigit() or re.fullmatch(r"[ivxlc]+", label, re.I)):
            label = f"{appendix}: {label}"
        blank = "INTENTIONALLY LEFT BLANK" in text.upper() and len(text.strip()) < 80
        records.append({
            "pdf_page": i + 1,
            "page_label": label,
            "label_source": how,
            "blank": blank,
            "text": text,
        })
    return records


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    pdf_path, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    records = build(pdf_path)
    with open(out_dir / "pages.jsonl", "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    with open(out_dir / "pages.md", "w") as f:
        for r in records:
            if r["blank"]:
                continue
            f.write(f"\n=== PDF p.{r['pdf_page']} | OS page {r['page_label']} ===\n")
            f.write(r["text"].rstrip() + "\n")
    print(f"{len(records)} pages -> {out_dir}/pages.jsonl, pages.md")


if __name__ == "__main__":
    main()
