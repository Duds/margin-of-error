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
- 2026-10-03 — Verified lower house seat count from AEC tally room. Resolves
  the contradiction between the prototype (2 seats) and the feasibility report
  (0 seats). **Both were wrong. The correct figure is 1.**

```
source_id:        aec-hor-2025-party-rep
title:            2025 federal election — House of Representatives,
                  party representation summary, final results
publisher:        Australian Electoral Commission
tier:             A
retrieved:        2026-10-03
url:              https://results.aec.gov.au/31496/Website/HouseDefault-31496.htm
covers:           national; seats won by party, by state and nationally
caveats:          page footer states "These results are final", updated
                  Tue, 10 Jun 2025 10:49:32 AM AEST
finding:          No One Nation seats. Seats won: ALP 94, Liberal/National
                  Coalition 43, The Greens 1, Centre Alliance 1, KAP 1,
                  Independent 10. Total 150.
```

```
source_id:        aec-by-farrer-2026
title:            2026 Farrer by-election — House of Representatives,
                  two candidate preferred and first preference count, final
publisher:        Australian Electoral Commission
tier:             A
retrieved:        2026-10-03
url:              https://results.aec.gov.au/31633/Website/HouseDivisionPage-31633-118.htm
covers:           Farrer division, NSW
caveats:          page footer states "These results are final", updated
                  Mon, 25 May 2026 1:25:07 PM AEST. A by-election has no
                  previous-election comparison, so the swing column reads
                  0.00 and must not be plotted as a swing
finding:          David Farley (One Nation) elected. TCP 58,294 (57.55%),
                  margin 15,302. First preferences 40,042 (39.53%).
```

```
source_id:        aec-hor-2025-fp-by-party
title:            2025 federal election — House of Representatives,
                  first preferences by party
publisher:        Australian Electoral Commission
tier:             A
retrieved:        2026-10-04
url:              https://results.aec.gov.au/31496/Website/Downloads/
                  HouseFirstPrefsByPartyDownload-31496.csv
event_id:         31496
caveats:          identical schema to every other year; declared individually
                  because the build resolves each id on a chart against this
                  registry, and a family pattern would resolve nothing
transformations:  none; TotalPercentage as published
used_by:          chart-02
finding:          ON 6.40% primary, 0 seats. The party's best federal primary
                  vote in the series, and still nothing.
```

- 2026-10-04 — **House primary vote and seats won, nine general elections,
  2001 to 2025.** Replaces the Roy Morgan cross-check as the source for
  Chart 02. Both figures come from one AEC file per election.

```
source_id:        aec-hor-<year>-fp-by-party   (2004, 2007, 2010, 2013, 2016,
                                               2019, 2022; 2025 above)
title:            <year> federal election — House of Representatives,
                  first preferences by party
publisher:        Australian Electoral Commission
tier:             A
retrieved:        2026-10-04
url:              https://results.aec.gov.au/<eventId>/Website/Downloads/
                  HouseFirstPrefsByPartyDownload-<eventId>.csv
event_ids:        2004 12246, 2007 13745, 2010 15508, 2013 17496,
                  2016 20499, 2019 24310, 2022 27966, 2025 31496
covers:           national; first preferences by party, with elected count
caveats:          every file opens with a bracketed metadata banner line
                  before the header, so DictReader straight onto the file
                  reads the banner as the header
transformations:  TotalPercentage as published, 2dp; seats from the Elected
                  column, cross-checked against the separate party
                  representation download
used_by:          chart-02
files:            data/aec/raw/house-first-prefs-by-party-<year>.csv
finding:          Party recorded under a different name in every era. HAN in
                  2001 and 2004, ON from 2007; "Pauline Hanson's One Nation"
                  only from 2019. Matching on the modern name drops five of
                  the nine elections. Seats won: zero at every election.
```

```
source_id:        aec-hor-2001-fp-by-party
title:            2001 federal election — House of Representatives, national
                  first preferences by party
publisher:        Australian Electoral Commission
tier:             A
retrieved:        2026-10-04
url:              https://www.aec.gov.au/About_AEC/Publications/statistics/
                  files/aec-2001-election-statistics.zip
covers:           national; first preferences by party; members elected
caveats:          the AEC publishes no CSV for 2001 and its live tally room
                  (results.aec.gov.au/10822) carries a standing disclaimer
                  that its results "are not final". These figures come from
                  the official published statistics instead, which are
                  final. The file is fixed-width and repeats the party once
                  per state, so the national row must be selected by section:
                  scanning for the first matching line returns Queensland's
                  7.07% against the national 4.34%
transformations:  none; National Summary block of v1_6.txt, party code HAN
used_by:          chart-02
files:            data/aec/raw/2001/house-first-prefs-by-party-2001.txt,
                  house-members-elected-2001.txt, party-representation-2001.txt,
                  code-2001.txt
finding:          HAN 4.34% primary, 0 of 150 seats. The AEC's own code table
                  (code-2001.txt) records HAN as "Pauline Hanson's One
                  Nation". Confirms Roy Morgan's 4.3% cross-check. Two
                  independent tables agree: the House party representation
                  table has no HAN column at all, and the members elected
                  list carries 150 members with no HAN code.
```

- 2026-10-04 — **The House has not always had 151 seats.** Verified by summing
  every party's national total in each AEC party representation download:

```
source_id:        aec-hor-<year>-party-rep
title:            <year> federal election — House of Representatives,
                  party representation
publisher:        Australian Electoral Commission
tier:             A
retrieved:        2026-10-04
used_by:          chart-02
finding:          150 seats in 2001, 2004, 2007, 2010, 2013 and 2016;
                  151 from 2019. A seat share computed against a fixed 151
                  understates every earlier share by a twentieth, and the
                  error is invisible because the seat line is drawn against
                  zero either way.
```

- 2026-10-03 — By-election sweep. Checked every federal House by-election in
  the AEC archive from 2005 to 2026 (24 events). One Nation candidates stood
  in Cook 2024, Dunkley 2024, Fadden 2023, Aston 2023 and Farrer 2026. Only
  Farrer 2026 was won. No One Nation seat was won at a general election in
  that period. Note: there is no Newcastle by-election in the AEC archive; if
  a second seat is being recalled, the recall does not correspond to any AEC
  by-election record.

- 2026-10-03 — **Preference-flow finding, directly relevant to the thesis.**
  Farley converted 39.53% primary to 57.55% TCP, a gain of 18.02 percentage
  points. A bandless primary-vote chart would understate what this party can
  achieve in a single division. This is the strongest candidate evidence so far
  that primary vote alone is the wrong measure and that seat results are not
  predicted by primary vote alone. Requires confirmation that the same
  conversion pattern holds at scale before it can be a finding.

## Task 0004 — polling source assessment

Attempted 2026-10-03. **Blocking finding: the schema cannot be filled from
Tier B public pages.** Recorded so the same gap is not re-investigated.

The required schema is `fielded_start`, `fielded_end`, `pub_date`, `house`,
`n`, `margin_of_error`. Roy Morgan's published primary voting intention poll is
the most complete Tier B source available, and it does not carry two of those
six fields.

```
source_id:        roymorgan-pvi
title:            Federal Voting - Primary Voting Intention (%), with
                  long-term trend 2013-2025 and recent election results
                  1996-2025
publisher:        Roy Morgan Research
tier:             B
retrieved:        2026-10-03
url:              https://www.roymorgan.com/morgan-poll/primary-voting-intention/
covers:           national primary vote intention, monthly, 2013 to 2025
```

What the page publishes:

| Field | Published | Detail |
|---|---|---|
| `fielded_start` / `fielded_end` | yes | Month and day range per wave, e.g. "March 15/16 & 22/23, 2014". Multi-mode waves are marked "(Multi-mode)" |
| `house` | yes | Roy Morgan |
| `pvi_oned` | yes, in two tables | Election results table has a discrete One Nation column. Monthly table does not |
| `pub_date` | no | No publication date on any wave |
| `n` | **no** | Absent from the entire page |
| `margin_of_error` | **no** | Absent from the entire page |

Verified absences by direct string search over the full page for `sample size`,
`interviewed`, `n = <number>`, `margin of sampling error` and `margin of error`.
Zero matches. There is no methodology page linked for this poll, and no CSV,
XLSX, JSON or PDF download of the underlying data.

### Consequences for the thesis

1. **The band cannot be drawn.** `docs/chart-specs.md` Chart 01 requires a
   confidence interval on every poll-derived point, and non-negotiable 5 in
   `AGENTS.md` forbids a bandless point estimate for any poll-derived figure. A
   band computed from a default maximum sample size would be fabricated
   precision, which is the exact failure the project exists to expose.
2. **The central question is unanswerable as framed.** The thesis asks whether
   the published margin of error explains the gap. Roy Morgan does not publish
   the margin of error, so the second half of the thesis has no published input
   for this house. This is a structural problem with the thesis, not a data
   collection gap.
3. **A denominator switch is embedded in the source.** The monthly table
   reports One Nation inside "Other Parties (ALL)". For the April 27 2025 wave
   the combined figure is 18.5% with One Nation highlighted in the release text
   at 7.5%. Using the combined figure as if it were One Nation would overstate
   the party by more than double. `AGENTS.md` gotchas flag this exact trap.

### Election result figures confirmed from this source

These are One Nation primary vote at federal general elections, from the
"Recent Election Results (%) 1996-2025" table on the same page. They require
confirmation against AEC directly before use, per `AGENTS.md` non-negotiable 2,
but they are internally consistent and the 2025 figure reconciles:

| Election | Date | ON primary % |
|---|---|---|
| 1996 | March 2 | 0.3 |
| 2001 | November 10 | 4.3 |
| 2007 | November 24 | 0.3 |
| 2013 | September 7 | 0.2 |
| 2019 | May 18 | 3.1 |
| 2022 | May 21 | 5.0 |
| 2025 | May 3 | 6.4 |

The 2007 (0.3%) and 2013 (0.2%) figures are far below the 12.3% quota and
must not be assumed to mean the same party fielding the same ballot paper as in
2025. Candidate slate coverage and registered name both differ across those
cycles, and either would depress the figure. `AGENTS.md` gotchas flag this as
the silent-row-loss trap: series construction must match on the AEC party
abbreviation for each election and confirm the candidate count, not on the
modern name. Do not present 1996 to 2025 as a continuous series until each
row is verified against AEC with its registered name and fielded candidate
count recorded.
---

## Ingested datasets

Produced by `tools/ingest_roymorgan.py` from `roymorgan-pvi`. Reproducible: run
against a saved copy of the page and the output is identical.

| File | Rows | What it is |
|---|---|---|
| `data/polls_roymorgan.csv` | 138 | Monthly PVI waves: field window, ALP, and the combined "Other Parties (ALL)" / "Indepen-dents (ALL)" cells. **`pvi_oned` is empty on every row by construction.** |
| `data/roymorgan_election_results.csv` | 10 | Discrete One Nation primary vote by federal election, 1996 to 2025. **Cross-check only; every row requires AEC confirmation.** |

Three fields are null on every poll row and must stay that way:

| Field | Status | Why |
|---|---|---|
| `n` | not published | absent from the entire page |
| `margin_of_error` | not published | absent; no methodology page linked |
| `pub_date` | not published | no publication date on any wave |

`AGENTS.md` non-negotiable 5 prohibits imputing a margin from an assumed sample
size. A band derived from a guessed `n` is fabricated precision in the visual
language of honesty, which is the specific failure this project exists to
expose.

### The denominator trap, enforced in code

The monthly table has **no discrete One Nation column**. The party is folded
into "Other Parties (ALL)", which reads **18.5** for the April 27 2025 wave.
One Nation's own figure for that wave is **7.5**, and the publisher's footnote
says the combined cell "includes support for One Nation (highlighted in the
release) of 7.5%". The party is therefore a **subset** of that cell, not the
cell. Reading it as the party would overstate One Nation by more than double,
and would fail silently.

`select_column()` in `tools/ingest_roymorgan.py` selects by header text and
raises `UnmappedColumn` rather than defaulting. It refuses a **discrete** party
request that resolves to an **aggregate** column, while still permitting a
deliberate request for the aggregate by name — the guard is on the mismatch,
not on aggregates. `validate()` fails outright if `pvi_oned` is ever populated
on the monthly table. 7 regression tests cover this.

### A discontinuity in the election series

| Election | Year | ON primary % |
|---|---|---|
| 2025 | May 3 | 6.4 |
| 2022 | May 21 | 5.0 |
| 2019 | May 18 | 3.1 |
| 2016 | July 2 | 1.3 |
| 2013 | September 7 | 0.2 |
| 2010 | August 21 | 0.2 |
| 2007 | November 24 | 0.3 |
| 2004 | October 9 | 1.2 |
| 2001 | November 10 | 4.3 |
| 1996 | March 2 | 0.3 |

The 2004-2016 block sits at 0.2-1.3 while 2001 and 2019-2025 sit at 3.1-6.4.
That is not a smooth trend; it is a different measure of the same name. Below
the 12.3% Senate-registration quota a party can still contest, but slate
coverage and registered name differ across those cycles. Per `AGENTS.md`
gotchas, series construction must match on the **AEC party abbreviation for
each election** and record the fielded candidate count, not on the modern name.
Do not present 1996 to 2025 as one continuous series until each row is verified
against AEC.

---

## Vendored dependencies (fonts)

Every third-party asset served by the page, per `AGENTS.md`. All are SIL Open
Font Licence 1.1, vendored locally rather than loaded from a CDN, so the page
has no third-party runtime dependency at all.

```
source_id:        font-newsreader-opsz
title:            Newsreader variable (optical size + weight)
publisher:        Production Type / Fontsource
tier:             A (open licensed asset, not a data source)
licence:          OFL-1.1. Full text at assets/fonts/LICENSE-newsreader.txt
version:          5.3.0 (@fontsource-variable/newsreader)
files:            assets/fonts/newsreader-latin-opsz-normal.woff2   128 KB
                  assets/fonts/newsreader-latin-opsz-italic.woff2  143 KB
sha256 (first 16): 6e4f2958c3a7c4a8  normal
                   5dfcd10d24af8c82  italic
axes:             wght 200-800, opsz 6-72 (default 18). Verified with fontTools.
subset:           latin only. No latin-ext.
retrieved:        2026-10-04
used_by:          page shell (h1, h2, h3, lede)
caveats:          The opsz cut SUPERSEDES the wght-only cut rather than being
                  an addition to it, so only one Newsreader file is shipped.
                  Selected over wght because the optical axis is what makes the
                  face read as a broadsheet at display sizes. Costs 271 KB
                  against 119 KB; affordable only after the budget was raised
                  to 400 KB.
```

```
source_id:        font-plex-sans-variable
title:            IBM Plex Sans variable (weight)
publisher:        IBM / Fontsource
tier:             A
licence:          OFL-1.1. Full text at assets/fonts/LICENSE-ibm-plex-sans.txt
version:          5.3.0 (@fontsource-variable/ibm-plex-sans)
files:            assets/fonts/ibm-plex-sans-latin-wght-normal.woff2   44 KB
sha256 (first 16): e2291e842cf5af16
axes:             wght 100-700. Verified with fontTools.
subset:           latin only.
retrieved:        2026-10-04
used_by:          body prose, captions, source notes, UI
caveats:          Body is set at 18px per DESIGN.md. Never below 16px.
```

```
source_id:        font-plex-mono-400-500
title:            IBM Plex Mono, static 400 and 500
publisher:        IBM / Fontsource
tier:             A
licence:          OFL-1.1. Full text at assets/fonts/LICENSE-ibm-plex-mono.txt
version:          5.3.0 (@fontsource/ibm-plex-mono)
files:            assets/fonts/ibm-plex-mono-latin-400-normal.woff2   14 KB
                  assets/fonts/ibm-plex-mono-latin-500-normal.woff2   14 KB
sha256 (first 16): 08949f728dc52d52  400
                   01d285447409c8a5  500
axes:             none. Static cuts; IBM Plex Mono has no variable build on
                  Fontsource, which is why these are two files.
subset:           latin only.
retrieved:        2026-10-04
used_by:          every figure, axis tick, data table, kicker
caveats:          Always paired with font-variant-numeric: tabular-nums so
                  columns align on the decimal. The 500 weight is preloaded
                  for no face today; drop it if nothing uses it.
```

**No other runtime dependency exists.** Task 0002 locked the chart stack as
stdlib Python generating SVG at build time, and motion as
`IntersectionObserver` plus CSS with no library, so there is no charting
package, no framework and no CDN. The five files above are the entire
third-party surface of the page.

---

## Placeholder figures (NOT SOURCED, NOT FOR PUBLICATION)

`charts/chart_01.py` carries unsourced values carried over from the discarded
prototype. They exist only to exercise the build. They have **no entry** in any
source tier above, which is why they must not ship.

| Figure | Status |
|---|---|
| `charts/chart-01.svg`, `charts/chart-01-narrow.svg` | PLACEHOLDER. Delete and regenerate under task 0007 once tasks 0003 and 0004 supply sourced data. |

Both SVGs declare `data-unsourced="true"` on their root `<svg>` element, which
is what `tools/build.py` checks. They are listed here so the unsourced figures
are auditable from the registry rather than being a private note in a Python
file — the build refuses a `data-unsourced="true"` chart that this section does
not mention.

The guard landed 2026-10-04. `tools/build.py` now refuses any chart that
declares neither a `data-source-id` nor `data-unsourced="true"`, refuses a
source id with no entry in this registry, refuses a chart claiming both, and
refuses a band polygon whose points share one x — the task 0002 defect where a
published margin rendered invisibly. It also refuses placeholder prose in the
template, which the chart checks could not see.
