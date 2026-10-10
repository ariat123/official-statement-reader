---
name: official-statement-reader
description: Read a municipal bond official statement (POS or final OS) and write a one-to-two page deal summary in which every line cites the page it came from, plus the deal profile used to find comparable deals on EMMA. Use when someone uploads or links an official statement and wants the deal terms, structure, security, ratings, sources and uses, or credit points, or wants to find comps for it.
---

# Official statement reader

An official statement runs 150 to 300 pages. The deal terms a banker or investor needs fill about two of them, scattered across the cover, the inside cover, the body and the appendices. This skill pulls those terms out and cites every one, so a reader can check any line in seconds.

## Inputs

- The official statement PDF (preliminary or final). EMMA (emma.msrb.org) has it for free under the issue's Official Statement link.
- Optional: the official statements of comparable deals (see "Comp profile").

## Rules that override everything else

1. **Every claim cites a page.** Give the printed page (cover, inside cover, 4, A-1-17, D: 15) and the PDF page number, and keep a short exact quote from that page that supports the claim.
2. **Every number appears in the quote.** Copy figures exactly as printed (3.440%, not 3.44%). If a number is calculated (a total, a ratio), mark it derived and show the arithmetic.
3. **Don't fill gaps.** If the OS doesn't state something (pricing date, spreads to a benchmark, takedown), list it under "Not in this document" and say where you looked. Never estimate it.
4. **Watch for look-alikes.** Appendices repeat facts about other bonds and other years. A rating in the audited financials, a coupon on prior bonds, or a debt figure from last fiscal year is not a fact about this issue. Check which bonds and which date a figure belongs to before using it.
5. **Preliminary vs final.** In a POS, coupons, yields, sizes and the underwriter's discount are usually blank or marked "preliminary, subject to change." Say so instead of reporting them as final.

## Steps

1. **Map the pages.** Note where printed numbering starts (body page 1 is often unnumbered) and where each appendix restarts its own numbering. If you can run code, `scripts/os_pages.py` does this and writes `pages.md` with a header on every page.
2. **Read in this order:** cover, inside cover (maturity schedule), table of contents, then the body sections the table of contents points to: the bonds, security, sources and uses, debt summary, tax matters, underwriting, ratings. Go to Appendix A (issuer information) for the tax base, largest taxpayers, collections, reserves and big commitments. Use the audited financials only when the body sends you there.
3. **Fill the summary** using the template below. Short plain sentences. One idea per line.
4. **Build the comp profile** (section G).
5. **Check.** For every claim, re-open the cited page and confirm the quote and every number. If you can run code, write the claims to JSON and run `scripts/check_citations.py`. It fails any claim whose quote isn't on the cited page or whose numbers aren't in its quotes.
6. **Flag what a careful reader would catch:** anything unusual (no call option, a short final maturity, concentrated taxpayers, a large off-balance-sheet commitment) and any look-alike figure you excluded under rule 4.

## Output template

Title: issuer, series, par, OS date.

- **A. Deal at a glance:** issuer; series and par; OS date and expected delivery; underwriter; municipal advisor; bond counsel and disclosure counsel; underwriter's counsel; paying agent.
- **B. Security and purpose:** pledge (unlimited tax GO, limited tax GO, revenue pledge); what can and can't pay debt service; authorization (election, resolution); projects funded.
- **C. Structure:** coupons; maturity range by series; yield range and key maturities; call provisions; interest dates; denominations; tax status; debt service shape.
- **D. Ratings:** each agency and rating on these bonds. Note any rating elsewhere in the document that is not on these bonds.
- **E. Sources and uses:** par, premium or discount, project fund deposits, costs of issuance, underwriter's discount.
- **F. Credit points to check:** debt outstanding after the issue; debt to assessed value and per capita; tax base and concentration; collections; tax limits and whether debt service sits outside them; reserves; big commitments.
- **G. Comp profile:** see below.
- **Not in this document:** what a reader might expect that the OS doesn't state, and where you looked.

Each line ends with its citation, for example `(p. 13, PDF 19)`.

## Comp profile

This follows how comps were pulled for pricing on the sell side: before pricing and again on pricing day, using negotiated deals that priced that week. A desk's own platform supplies the scales and benchmark spreads. This section covers only what public data supports.

**1. Pull the comp keys from this OS, each with its citation**, most important first:

1. Par size, total and by series.
2. Maturities: first and final maturity, and where the big maturities sit.
3. Tax status of each series. Taxable pieces get taxable comps.
4. Method of sale. Use only what the OS shows, such as a named underwriter buying at a set price, or a notice of sale and bid results. Don't label a deal negotiated or competitive unless the OS supports it.
5. State. Some states' bonds trade on their own curve, California and New York for example. Note whether this deal's state is one of them, and don't invent a list.
6. Ratings on these bonds.
7. Security: GO or revenue.
8. Call terms.

**2. Write the comp search** the keys imply, for EMMA or the desk's own platform:

- Similar size and similar maturities.
- Same tax status.
- Negotiated sales only. Use competitive deals only if nothing else fits, and say so.
- Rating within about a notch either side. Widen if the list is thin, and say so.
- Priced recently. For pricing, that means the same week.
- Skip states that trade on their own curve.
- GO is preferred for a GO deal, but a revenue deal of similar size and maturities can still be a comp.

**3. Confirm each candidate.** Open its official statement and check the maturity schedule (amounts, coupons, yields) against the scale you're using. Then record its size, sale method, rating, security and call terms the same way, with citations. Drop a comp that doesn't fit and say why.

**Leave blank:** spreads to MMD or any other licensed benchmark, unless the user supplies that data.
