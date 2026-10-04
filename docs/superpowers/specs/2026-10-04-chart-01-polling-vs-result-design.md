# Chart 01 — Polling against result, 2018 to 2022

**Status:** design approved by Dale, 2026-10-04. Spec written, pending review.
**Task:** 0007 in `TASKS.md`. Supersedes the Chart 01 placeholder.
**Related:** `docs/chart-specs.md` Chart 01, `AGENTS.md` non-negotiables 2 and 5.

---

## What this chart is

The page's spine. It answers the thesis question — did polling overstate or
understate One Nation's primary vote relative to its result — and it answers it
with a finding that goes both ways.

Between 2018 and 2022, Roy Morgan published 48 fortnightly estimates of the
party's primary vote, with **no margin of error, no sample size and no
publication date** on any of them. Averaged over the twelve waves before each
election, polling put the party at 3.70% for 2019 and 3.71% for 2022. The party
recorded 3.1% and 5.0%. Polling was **0.60 percentage points high in 2019** and
**1.29 points low in 2022**.

That is the whole finding. Polling was not biased in one direction. It was
slightly wrong in opposite directions in two consecutive elections, and the
published data gives no way to know how precise either estimate was.

## What this chart does not claim

Stated explicitly because each of these is the misreading a critic will reach
for, and the design has to close it.

- **Not** that polling is generally biased for or against this party. Two
  elections, opposite directions, n = 2.
- **Not** anything about pollster competence. `AGENTS.md` forbids the page being
  about pollsters, and the limit stated here is a property of the evidence on the
  table, not a finding about a publisher.
- **Not** that 2018 to 2022 is the whole record. The series starts in 2018
  because that is where it starts. Earlier waves exist on the same page and are
  blank for this party; the 2022 to 2025 monthly table is a different table and
  reports the party only inside a combined figure.
- **Not** a claim about the 2025 election. No usable polling exists for it.
- **Not** that the gap is caused by anything. The chart measures a difference
  and stops.

## Data

### Source

`https://www.roymorgan.com/morgan-poll/primary-voting-intention`, Tier B,
registered as `roymorgan-pvi` in `docs/data-sources.md`.

The page carries a **second table** with a discrete One Nation column, 132 rows
spanning 2013 to 2022. `tools/ingest_roymorgan.py` does not currently read it.
Per-year count of waves carrying a discrete figure, measured 2026-10-04:

| Year | Waves with a discrete figure |
|---|---|
| 2013 | 0 of 7 |
| 2014 | 0 of 26 |
| 2015 | 0 of 26 |
| 2016 | 1 of 12 |
| 2017 | absent from the table |
| 2018 | 4 of 4 |
| 2019 | 6 of 6 |
| 2020 | 8 of 8 |
| 2021 | 16 of 16 |
| 2022 | 15 of 15 |

2018 to 2022 is the contiguous, complete range. That is the series, and its
start date is a property of the source, not a choice made here.

**Wave count, and why it is 48 and not 49.** The table yields 49 rows carrying a
discrete One Nation figure between 2018 and 2022, but one of them is the row
labelled `2019 Federal Election - May 18, 2019`, which is a result rather than a
poll. **48 are polls.** The first pass of this spec said 49 because the election
row was counted; caught by recomputing from the source rather than trusting the
earlier figure. It is recorded here because the corrected number is the one that
appears on the page, and because a count that is off by one because it included
the thing it was counting alongside is the same class of slip as a mean that
drifts from its inputs.

### The 2019 window is shorter than twelve

Only **5** poll waves precede the 2019 election; 12 precede the 2022 election.
The trailing-twelve rule is therefore "up to twelve preceding waves", and the
count actually used is computed per election and stated in the caption.

This is not smoothed over and the shorter window is not quietly padded to twelve.
A 5-wave mean and a 12-wave mean are different quantities, so the chart labels
each with the wave count it used, and build assertion 2 enforces that the number
in the label is the number used in the arithmetic.

### Election results

| Election | Date | ON primary % | Status |
|---|---|---|---|
| 2019 | 18 May 2019 | 3.1 | Roy Morgan, cross-check only |
| 2022 | 21 May 2022 | 5.0 | Roy Morgan, cross-check only |

**Both require AEC confirmation before publication.** See "The gate" below.

### Fields that do not exist and will not be imputed

| Field | Status | Consequence |
|---|---|---|
| `n` | not published | no sample size, so no computed margin |
| `margin_of_error` | not published | no band |
| `pub_date` | not published | waves are ordered by field window, not publication |

`AGENTS.md` non-negotiable 5 prohibits imputing a margin from an assumed sample
size. These fields are written null in the CSV and must stay null.

## How every number is produced

This section exists because of a specific failure. The archived feasibility model
was run, and the prose describing it said booth coverage was "below 15%". The
model's own output was **1.33%** — a tenfold overstatement introduced between
running a model and writing about it, silently. The approved chart carries the
identical exposure: a mean of twelve waves can drift from the twelve waves it
came from just as easily.

**Therefore: no figure in this chart, its caption, or its prose is ever
transcribed. Every one is computed at build time from the ingested CSV.**

```
data/polls_roymorgan_oned.csv        # 48 discrete waves, written by the ingest
        |
        v
charts/stats.py  window_mean()      # trailing-N mean, from the file
        |
        +--> charts/chart_01.py     # spine: gap bars
        +--> charts/chart_01.py     # support: pre-election spans
        +--> index.html prose        # the same call, injected at build
```

If the ingest changes, every derived number changes with it, and the prose
fails the build rather than going quietly stale.

## Form

### Spine chart — the gap

Two bars, poll-minus-result in percentage points, from a zero line.

A zero line is the reference, so the chart is honest about its axis by
construction: the axis is centred on the quantity being measured, and needs no
"axis does not start at zero" caveat. The two bars fall on opposite sides, which
is the finding and is legible at phone width without annotation.

- **Question:** did polling overstate or understate the party's vote?
- **Form:** two bars, one per election, from a zero rule.
- **Must not:** sort, truncate away the zero rule, or annotate one bar's
  direction in words the axis already shows.

### Supporting panel — the evidence, in the same figure

Beneath the gap bars, **a vertical span per election** showing the range across
the preceding waves, with the result marked against it.

**Not a line across 48 waves.** A line implies we know the value between
fortnightly snapshots, and we do not. There is no model between them and the
chart would be asserting one.

The payoff is visible without annotation: for 2022 the published range tops out
at 5.0 and the result sits *at* 5.0, at the very top of everything polling had
published. That is the strongest single fact in the dataset and the span form
shows it directly.

**Change from the first draft, made 2026-10-04 after approval.** This was
originally specced as a second, separate figure. It is now a second panel
**within** the spine figure. Claim and evidence read together, one heading, one
caption, one source note, and the page resolves to two charts rather than three.
At narrow width the two panels stack.

---

## Chart 02 — Seat efficiency

Added 2026-10-04 at Dale's direction: *"lets add the seat-efficiency chart
alongside."* This is editorial **Chart 04** in `docs/chart-specs.md` (seat share
against vote share), moved earlier in build order because the data exists now.

**Provisional, and Dale will decide whether it stays after seeing it rendered.**
It is built behind the same gates as Chart 01 and carries an explicit note in
`docs/chart-specs.md` that it is awaiting a keep-or-cut decision. If it goes,
Chart 01 is unaffected: they share no data and no code beyond `stats.py`.

### What it answers

At what primary vote does this party convert into seats?

### Data

National primary vote by election, and seats won at each federal general
election. Both need AEC confirmation. Available now from the Roy Morgan
cross-check table (national primary, ten elections) and from the AEC party
registration already recorded as `aec-hor-2025-party-rep` (seats won: 0).

### Form

Two lines on one axis, **both measured as a share of the same 151-seat body**:
national primary vote percentage, and seat share as seats ÷ 151. The gap between
them is shaded.

Both series are percentages of one elected body, so a single axis is honest
rather than a convenience. One seat is 0.66%.

### The claim

> Between 1996 and 2025 the party's best federal primary vote was 6.4% in 2025.
> Across all ten general elections in that period it won **no seats at all**. Its
> only seat came at a single division at a by-election.

### What it must not claim

- **The by-election is outside the series.** Farrer 2026 is a different event on
  a different denominator and is annotated as such, never plotted as if a
  by-election were comparable to a general election. `AGENTS.md` gotchas.
- **Not** that the vote line predicts seats. The chart is descriptive: a party
  can be rising and still hold nothing.
- **Not** that 1996 to 2025 is homogeneous. The 2004 to 2016 block sits at 0.2 to
  1.3% with thinner slate coverage, so the discontinuity must be marked. This is
  the same break recorded in `docs/data-sources.md`.
- **Not** a claim about vote efficiency against other parties. One party, ten
  elections, no comparison group. If that is wanted it needs its own source and
  its own spec.

### The by-election annotation

Farrer, 25 May 2026, David Farley, 39.53% primary converting to 57.55% two-party
preferred. **Six times the national share produced the party's only seat**, in a
single regional division. That is the mechanism the chart cannot show, because
the mechanism is local concentration — a national average has no resolution for
it. Stated in the annotation, not plotted on the axis.

This also corrects a drift from the discarded prototype, which put the party's
realistic ceiling at "1 to 4 regional **Queensland** seats". The one verified win
is in **NSW**. See `docs/archive/2026-10-04-phon-feasibility-model.py`.

### The gate

Same as Chart 01: `requires_aec_confirmation` on every row, build refuses a chart
resolving only to cross-check-only source ids. Nothing ships until confirmed.

## Uncertainty: the honest part (Chart 01)

Every poll-derived figure on this page carries the "no published margin" marker.
That is non-negotiable 5 as amended, and here it is not a formality — it is the
majority of what this chart has to say.

- Each poll point carries a distinct open-circle glyph in `--color-ink-muted`.
- The caption states, computed not typed: **"N of M waves publish no margin of
  error, no sample size or publication date."** For this dataset N = M = 48.
- The marker marks the edge of what the comparison can show. It is not
  decorative and it is not a claim about any publisher.

## The gate, and what applies to both charts

**Nothing ships until the 2019 and 2022 results are confirmed against AEC, and
Chart 02's national primary and seat counts likewise.**

Dale's instruction, 2026-10-04: *"Nothing is shipping to prod yet. We will wait
for AEC confirmation before anything ships. But we need to build the chart with
what we have now, and we will update it when we get the better information."*

So the chart is **built now** behind an explicit, machine-checked gate, and the
gate fails the build rather than being bypassed:

- Each result row carries `requires_aec_confirmation = yes` while unconfirmed.
- `tools/build.py` refuses any chart whose `data-source-id` resolves only to
  source ids marked cross-check-only or unconfirmed.
- When task 0003 delivers AEC-confirmed figures, the CSV rows change, the
  registry gains the `aec-hor-*` entries, and the chart picks them up. No chart
  code changes.

This is the same shape as the print hatch: the correct value is in the data, not
in the code, so a data update needs no code change.

## Assertions added to the build

Seven new checks beyond the six already in place. Each must be verified to fail
on the input it catches, per the session's standing rule that a guard never seen
to fire is indistinguishable from one that does not work.

Assertions 1, 3 and 4 apply to **both** charts. 2, 5, 6 and 7 are Chart 01
specific. Two further assertions apply to Chart 02 only:

8. **Seat share is computed as seats ÷ 151, never as a percentage of any other
   denominator**, and House and Senate must never share an axis. `AGENTS.md`
   gotchas names this as a trap and `docs/chart-specs.md` Chart 04 repeats it.
9. **The by-election row may not be plotted on the general-election line.** It
   is an annotation only. A by-election has a different electorate, a different
   field and a different denominator; plotting it as a point on the series would
   assert comparability that does not exist.

1. A `data-source-id` on this chart may not resolve solely to cross-check-only
   source ids while `requires_aec_confirmation=yes` is set on any row.
2. The window size actually used for each election's mean must equal the wave
   count stated beside that mean. A drift between "twelve waves" in a caption and
   an actual 5 is the tenfold failure mode, caught mechanically. The 2019 window
   is 5 and the 2022 window is 12, so this assertion has two different expected
   values, and it is the check that would have caught the 49-versus-48 slip.
3. Every poll row used must carry `margin_of_error` null **and**
   `publishes_margin_of_error = no`. A populated margin is either a real change
   of source or an imputed value, and the second is prohibited.
4. No poll-derived figure may be written as a literal in any chart or template.
   Enforced by asserting the computed values appear in the generated SVG and that
   the generator source contains no numeric literal in the data block.
5. Every wave in the chart's range must have a field window. An undated poll
   cannot be ordered.
6. No wave outside 2018 to 2022 may appear without an explicit `blank_reason`.
7. The caption's wave count must equal the CSV row count used.

## Errors and edge cases

| Condition | Behaviour |
|---|---|
| A wave has no field window | Build fails. An undated poll cannot be placed. |
| The 2017 gap is a parsing artefact, not real | Ingest warns; the series range is re-derived from data, never hard-coded. |
| Fewer than N waves precede an election | That is the 2019 case, at 5. The mean uses what exists, the wave count is labelled, and assertion 2 binds the label to the arithmetic. No shorter window is silently presented as twelve. |
| No waves at all precede an election | That election is omitted from the chart and the caption says which, rather than drawn as a zero or a guess. |
| Roy Morgan restructures the page | `SourceShapeChanged`; the column mapping is re-verified by hand. Columns are selected by header, never by offset. |
| AEC figures differ from Roy Morgan's | AEC wins. The registry records the discrepancy; `docs/corrections.md` gains an entry if a figure was ever published. |

## Testing

- Existing 42 tests continue to pass.
- Chart 02 gets its own test that a by-election row entering the plotted series
  fails the build, since that is the mistake most likely to be made silently.
- The discrete-table reader gets its own tests, mirroring the monthly ones: the
  aggregate-column refusal must hold on this table too, since a careless mapping
  could resolve the party's column to a combined one.
- Each of the seven build assertions has a test proving it fails.
- `window_mean()` gets edge cases: empty, single wave, fewer than N, and a window
  that straddles an election.
- Visual verification in a browser at 320px, 640px and 1280px, plus reduced
  motion. The label floor is 16px at wide, 10.7px at 320px viewport.

## What this does not cover

Recorded so scope is explicit.

- **The 2025 election.** No usable polling exists. Out of scope.
- **Seat efficiency at division level.** Chart 02 covers national vote against
  national seat share only. The eight 2022 division primaries in the archived
  prototype would support a per-division version, and are logged in `TASKS.md`
  BACKLOG pending AEC verification. Not in scope here.
- **A national polling aggregate across houses.** Only Roy Morgan has a discrete
  column for this party; combining houses would mix methodologies and is out of
  scope.
- **Any claim about the 2013 to 2017 blanks.** They are recorded as a source
  property, not interpreted.