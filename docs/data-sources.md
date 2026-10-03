# Data sources

Canonical registry. **Add a row before adding a figure to the page.** Any number
on the site must resolve to an entry here, and the entry must resolve to a
document a reader can open.

Status values: `registered` (row exists, not yet used), `verified` (retrieved
and checked against the source), `used` (currently published on the page).

---

## Tier A — primary, official

Highest trust. Used for every result figure.

| Source | Publisher | What it carries | URL pattern | Status |
|---|---|---|---|---|
| House of Representatives results | Australian Electoral Commission | Primary vote, two-party preferred, seat margins, by division and state | `aec.gov.au` election results by year | registered |
| Senate results | Australian Electoral Commission | Senate primary and totals, state by state | `aec.gov.au` | registered |
| Party registration statements | Australian Electoral Commission | Registered party names, abbreviations, registered addresses | `aec.gov.au` | registered |
| Redistribution reports | Australian Electoral Commission | Boundary changes between cycles, seat name and number mapping | `aec.gov.au` | registered |
| Federal funding and disclosure returns | Australian Electoral Commission | Donations, membership, spending per party per cycle | `aec.gov.au` | registered |
| Parliamentary Hansard | Parliament of Australia | Debates, speeches, divisions — primary text for any claim about a statement | `hansard.aph.gov.au` | registered |
| Newspaper-submissions register | Australian Electoral Commission | Notices lodged by a party before an election | `aec.gov.au` | registered |

## Tier B — primary, commercial

Trustworthy but interested. Published methods matter.

| Source | Publisher | What it carries | URL pattern | Status |
|---|---|---|---|---|
| Pollster published tables | Various | Vote intention, fieldwork window, sample size, margin of error, house effects | per-house | registered |
| Poll aggregator | Roy Morgan | Rolling aggregate with model description | `roymorgan.com` | registered |

## Tier C — secondary

**Not usable as the source of a published figure.** May be used to locate a
primary source, or to describe an event with a caveat.

| Source | Type | Use |
|---|---|---|
| Major outlet political reporting | news | Pointer to a primary document; never the citation for a number |
| Wikipedia | tertiary | Orientation only; every figure traced onward to AEC before use |
| Archived news pages | news | Historical context, dated |

## Tier D — excluded

Never cite, never plot.

- Social media posts, including the party's and the subject's own accounts,
  except where the post itself is the subject of a factual claim, in which case
  cite the archived version with a capture date.
- Campaign material not lodged with the AEC.
- Paywalled analyst commentary without a published methodology.
- Any figure that cannot be traced past one hop to an original document.

---

## Recording a figure

Every dataset gets a row here with its own retrieval detail. The schema lives in
`standards.md`.

```
source_id:        aec-hor-2025
title:            House of Representatives results — 2025 federal election
publisher:        Australian Electoral Commission
tier:             A
retrieved:        2026-10-03
url:              <exact URL>
covers:           national; all states; by division
caveats:          party matched on AEC abbreviation for that election
files:            data/aec/2025/hor_results.csv
transformations:  percent rounded to 1dp; margins as signed integer votes
used_by:          chart-01, chart-02
```

---

## Retrieval log

Append-only. Every fetch recorded, including abandoned ones.

- 2026-10-03 — WHOIS check on candidate domains. `marginoferror.com.au` and
  `themarginoferror.com.au` no WHOIS match, treated as available.
  `firstpreference.com.au` and `margincall.com.au` registered. A no-match is not
  a reservation; the domain must be purchased.