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

## Registry field contract

Every dataset gets a block here with its own retrieval detail. `tools/build.py`
parses these blocks, so the format is load-bearing, not house style: an entry
the parser cannot read registers nothing, and a chart citing it is refused as an
unknown id.

| Field | Required | Read by |
|---|---|---|
| `source_id:` | yes | the parser. **Must be the whole line** — `^source_id:[ \t]*(\S+)[ \t]*$`. A trailing parenthetical makes the line unmatched and the entry invisible. Put extra detail in `years:` or `caveats:`. |
| `years:` | only for a `<year>` family | expands the family into concrete ids. Without it a family registers nothing. |
| `cross_check_only:` | when yes | the publication gate. `yes` refuses a chart whose every source is so marked. |
| `tier:`, `publisher:`, `url:`, `retrieved:`, `covers:`, `caveats:`, `transformations:`, `files:`, `finding:`, `used_by:` | prose | humans. Not parsed. |

A `<year>` family is for a source repeated per election with an identical
schema:

```
source_id:        aec-hor-<year>-fp-by-party
years:            2004, 2007, 2010, 2013, 2016, 2019, 2022
```

registers `aec-hor-2004-fp-by-party` through `aec-hor-2022-fp-by-party`. Cite the
expanded id on the chart, never the pattern. `test_every_ingested_aec_source_id_resolves`
fails if `data/aec_election_results.csv` cites an id this file does not hold, so
adding an election row means adding its years here.

Every id a chart cites must appear here. The check runs twice and the second
run is the one that matters: `unsourced_figure_problems` reads the source SVG,
and `artefact_source_id_problems` reads the built `index.html`, because the
build rewrites ids and can produce a citation that never existed in any source
file. See "Check the artefact, not just the source" in `AGENTS.md`.

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
source_id:        aec-hor-<year>-fp-by-party
years:            2004, 2007, 2010, 2013, 2016, 2019, 2022
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
used_by:          chart-01 (result axis: 2019, 2022), chart-02
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
years:            2001, 2004, 2007, 2010, 2013, 2016, 2019, 2022
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
cross_check_only: yes
retrieved:        2026-10-03
url:              https://www.roymorgan.com/morgan-poll/primary-voting-intention/
covers:           national primary vote intention, monthly, 2013 to 2025
caveats:          **cross_check_only: yes.** A source of record for published
                  polling figures, but not for an election result. Roy Morgan
                  publishes its own cross-check of the count; it is not the
                  Australian Electoral Commission's record, so any figure
                  presented as what the ballot produced must come from the AEC
                  instead. The marker stays. Chart 01 cleared the publication
                  gate on 2026-10-18 not by removing it but by citing the AEC
                  id of each result beside this id for its polling axis — the
                  gate refuses only a chart whose EVERY source is a cross-check.
                  Do not remove the marker to make a build pass; that is the
                  gate being worked around rather than satisfied.
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

Produced by `tools/ingest_roymorgan.py` from `roymorgan-pvi`, and by
`tools/ingest_aec_seats.py` from the AEC downloads. Reproducible: run against
the saved sources in `data/aec/raw/` and the output is identical.

| File | Rows | What it is |
|---|---|---|
| `data/polls_roymorgan.csv` | 138 | Monthly PVI waves: field window, ALP, and the combined "Other Parties (ALL)" / "Indepen-dents (ALL)" cells. **`pvi_oned` is empty on every row by construction.** |
| `data/polls_roymorgan_oned.csv` | 48 | **Discrete One Nation primary vote by fortnightly wave, 2018 to 2022.** Read from the second table on the same page, which carries a real One Nation column the monthly table lacks. 132 rows span 2013 to 2022; three are election results and are excluded by matching `\bElection\b`; the remainder that are blank for this party carry no figure. **This is the series every polling figure on the page is computed from.** |
| `data/roymorgan_election_results.csv` | 10 | Discrete One Nation primary vote by federal election, 1996 to 2025. **Cross-check only; not a source of record for a result.** Superseded for both charts by `data/aec_election_results.csv` since task 0003 landed on 2026-10-18. Retained for the 1996 row the AEC archive does not hold, and as the cross-check the AEC series was measured against: the two agree to within 0.04 points at every election. |
| `data/aec_election_results.csv` | 9 | **Primary vote and seats won at each federal general election, 2001 to 2025, from the AEC.** Both figures in one row, so the chart needs no cross-check. **Result axis of Chart 01 (2019, 2022) and both axes of Chart 02.** 1996 is absent: the AEC archive begins at 2001. |
| `data/aec_by_election.csv` | 1 | **The Farrer 2026 by-election, kept in its own file.** A different kind of event on a different denominator, so a shared file would invite the comparison the chart must not make. Carries `plottable_on_general_election_series = no`, which the build checks. |

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

### Where the discrete series starts, and why

The 48 usable waves are **contiguous from 2018 to 2022**. Earlier rows on that
page are blank for this party, and 2017 is absent altogether. That is a
property of the source, recorded rather than interpreted: the page carries no
figures for this party before 2018 and does not say why, and this project does
not guess. `charts/stats.py::contiguous_years()` derives the span from the data
rather than hard-coding it, so the series range stated on the page is the range
the data actually has.

Consequence for the windows: 2019 has **5** preceding waves and 2022 has **12**,
so the two figures on the page are means over different numbers of
observations. Every mean is returned with `n_used` beside it, and the build
refuses a page that states one count beside a mean taken over another.

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

**Superseded 2026-10-05.** The table below is Roy Morgan's cross-check. The
figures the page now states come from `data/aec_election_results.csv`, and the
two agree to within **0.04 percentage points** at every one of the nine
elections. The shape is identical; the figures are not the same figures, and
the AEC's are the ones that ship.

**The AEC series, which is what ships:**

| Election | Year | AEC ab | ON primary % | Seats | House size |
|---|---|---|---|---|---|
| 2025 | May 3 | ON | 6.40 | 0 | 151 |
| 2022 | May 21 | ON | 4.96 | 0 | 151 |
| 2019 | May 18 | ON | 3.08 | 0 | 151 |
| 2016 | July 2 | ON | 1.29 | 0 | 150 |
| 2013 | September 7 | ON | 0.17 | 0 | 150 |
| 2010 | August 21 | ON | 0.22 | 0 | 150 |
| 2007 | November 24 | ON | 0.26 | 0 | 150 |
| 2004 | October 9 | HAN | 1.19 | 0 | 150 |
| 2001 | November 10 | HAN | 4.34 | 0 | 150 |

Three things this table settled, none of which were known before it was pulled:

- **The House did not always have 151 seats.** It returned 150 from 2001 to
  2016 and 151 from 2019, verified by summing every party's national total in
  each AEC party representation download. A seat share taken against a fixed
  151 understates every earlier share by a fifth, and the error is invisible
  because the seat line is drawn against zero either way.
- **1996 has no AEC record.** The archive begins at 2001, so the "1996 to 2025"
  span in the superseded table below cannot be sourced from the AEC at all.
- **The party is named differently in every era.** `HAN` in 2001 and 2004, `ON`
  from 2007, and "Pauline Hanson's One Nation" only from 2019. Matching on the
  modern name drops five of the nine elections. This is the `AGENTS.md` gotcha
  about matching on the AEC abbreviation per election, and it was live.

The 2004-2016 block sits at 0.17-1.29 while 2001 and 2019-2025 sit at 3.08-6.40.
That is not a smooth trend; it is a different measure of the same name. Below
the 12.3% Senate-registration quota a party can still contest, but slate
coverage and registered name differ across those cycles. Do not present 2001 to
2025 as one continuous series without saying so — the chart marks the block
rather than joining it into a single line.

The superseded Roy Morgan cross-check, retained because the polling chart
compares against it:

| Election | Year | RM ON primary % |
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

**This section is now empty, and that is the intended state.**

It listed `charts/chart-01.svg` and its narrow variant as PLACEHOLDER, unsourced
figures carried over from the discarded prototype. Both were regenerated on
2026-10-04 from the ingested Roy Morgan series, declare
`data-source-id="roymorgan-pvi"`, and resolve to the `roymorgan-pvi` entry
above. Chart 02 was built the same way and declares the AEC ids.

The section is kept rather than deleted because `tools/build.py` refuses a
`data-unsourced="true"` chart that this section does not mention. If a chart
ever reverts to placeholder figures it must be recorded here, and an empty table
is the state that means nothing is unsourced.

| Figure | Status |
|---|---|
| _(none)_ | No figure is unsourced. |

The guard landed 2026-10-04. `tools/build.py` now refuses any chart that
declares neither a `data-source-id` nor `data-unsourced="true"`, refuses a
source id with no entry in this registry, refuses a chart claiming both, and
refuses a band polygon whose points share one x — the task 0002 defect where a
published margin rendered invisibly. It also refuses placeholder prose in the
template, which the chart checks could not see.
