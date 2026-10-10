#!/usr/bin/env python3
"""Render summary.json as a printable HTML page (summary first, quotes after).

Usage:
    python3 render_summary.py summary.json out.html [check_result_line]

Print to PDF with any browser, for example:
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless \
        --no-pdf-header-footer --print-to-pdf=summary.pdf out.html
"""

import html
import json
import sys


def cite_text(c):
    label = c["page_label"]
    if label in ("cover", "unnumbered"):
        label = "inside cover" if c["pdf_page"] == 2 else label
        return f"{label}, PDF {c['pdf_page']}"
    return f"p. {label}, PDF {c['pdf_page']}"


def cites_for(claim):
    seen, out = set(), []
    for c in claim["cites"]:
        t = cite_text(c)
        if t not in seen:
            seen.add(t)
            out.append(t)
    return "; ".join(out)


CSS = """
@page { size: Letter; margin: 0.45in 0.55in; }
:root { --ink:#1a1d21; --muted:#5f6670; --rule:#d9dde2; --accent:#1f4e79; --flag:#8a4b00; }
* { box-sizing: border-box; }
body { font-family: -apple-system, "Helvetica Neue", Arial, sans-serif; color: var(--ink);
       font-size: 9.6pt; line-height: 1.33; margin: 0; background: #fff; }
.wrap { max-width: 7.3in; margin: 0 auto; }
h1 { font-size: 15pt; margin: 0 0 3pt; line-height: 1.2; }
.sub { color: var(--muted); font-size: 9pt; margin-bottom: 8pt; }
.check { border: 1px solid var(--rule); border-left: 3px solid var(--accent); padding: 5pt 8pt;
         font-size: 9pt; margin: 0 0 10pt; }
h2 { break-after: avoid; font-size: 10pt; color: var(--accent); margin: 8pt 0 3pt; padding-bottom: 2pt;
     border-bottom: 1px solid var(--rule); text-transform: uppercase; letter-spacing: .03em; }
ul { margin: 0; padding-left: 13pt; }
li { margin: 2pt 0; }
.c { color: var(--muted); font-size: 8.5pt; white-space: nowrap; }
.id { color: var(--muted); font-size: 8pt; margin-right: 3pt; }
.flag { color: var(--flag); font-weight: 600; }
.derived { color: var(--muted); font-size: 8.5pt; }
.ev { page-break-before: always; }
table { border-collapse: collapse; width: 100%; font-size: 8pt; }
td, th { border-bottom: 1px solid var(--rule); padding: 3pt 4pt; vertical-align: top; text-align: left; }
th { color: var(--muted); font-weight: 600; }
td:nth-child(2) { white-space: nowrap; }
td.q { font-family: Menlo, Consolas, monospace; font-size: 7.5pt; word-break: break-word; }
.note { border-left: 3px solid var(--accent); background:#f4f7fa; padding: 5pt 8pt; margin: 5pt 0 0; font-size: 9pt; }
.foot { color: var(--muted); font-size: 8pt; margin-top: 10pt; }
"""


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    s = json.load(open(sys.argv[1]))
    check_line = sys.argv[3] if len(sys.argv) > 3 else ""
    d = s["document"]
    e = html.escape
    parts = [f"<!doctype html><html><head><meta charset='utf-8'><title>{e(s.get('short_title', 'OS summary'))}</title>",
             f"<style>{CSS}</style></head><body><div class='wrap'>",
             f"<h1>{e(s.get('short_title', d['title']))}</h1>",
             f"<div class='sub'>{e(s.get('subtitle', ''))}</div>"]
    if check_line:
        parts.append(f"<div class='check'>{e(check_line)}</div>")
    for sec in s["sections"]:
        parts.append(f"<h2>{e(sec['title'])}</h2><ul>")
        for c in sec["claims"]:
            text = e(c["text"])
            if c.get("flag"):
                text = f"<span class='flag'>{e(c['flag'])}</span> " + text
            extra = f" <span class='derived'>[calc: {e(c['calc'])}]</span>" if c.get("derived") else ""
            parts.append(f"<li><span class='id'>{e(c['id'])}</span>{text}{extra} "
                         f"<span class='c'>({e(cites_for(c))})</span></li>")
        parts.append("</ul>")
        if sec.get("note"):
            parts.append(f"<div class='note'>{e(sec['note'])}</div>")
    if s.get("not_in_document"):
        parts.append("<h2>Not in this document</h2><ul>")
        for n in s["not_in_document"]:
            parts.append(f"<li><b>{e(n['item'])}.</b> {e(n['where_checked'])}</li>")
        parts.append("</ul>")
    parts.append("<div class='ev'><h2>Evidence: the quote behind every line</h2>"
                 "<table><tr><th>Line</th><th>Page</th><th>Exact text on that page</th></tr>")
    for sec in s["sections"]:
        for c in sec["claims"]:
            for i, q in enumerate(c["cites"]):
                parts.append(f"<tr><td>{e(c['id']) if i == 0 else ''}</td><td>{e(cite_text(q))}</td>"
                             f"<td class='q'>{e(q['quote'])}</td></tr>")
    parts.append("</table>")
    if s.get("footer"):
        parts.append(f"<div class='foot'>{e(s['footer'])}</div>")
    parts.append("</div></div></body></html>")
    open(sys.argv[2], "w").write("\n".join(parts))
    print(f"wrote {sys.argv[2]}")


if __name__ == "__main__":
    main()
