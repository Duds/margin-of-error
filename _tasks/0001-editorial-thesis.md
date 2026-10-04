# 0001 — Editorial thesis and the question the page answers

- **Status:** complete (thesis fixed, framing fixed, scope written)
- **Depends on:** nothing
- **Blocks:** 0002, 0004, 0005, 0007
- **Task file:** [`0001-editorial-thesis.md`](0001-editorial-thesis.md)

## Why this is first

A single-page site fails by trying to say five things. The thesis fixes which
one thing it says, and every later decision — which polls, which seats, which
chart — follows from it. Doing this after the charts are built means rebuilding
them.

## Definition of done

- [ ] One question, written as a single sentence, that a reader could answer
      with a yes or no after reading the page.
- [ ] One paragraph of scope: what the page covers and, explicitly, what it
      does not.
- [ ] A list of the charts the thesis actually requires, with each one's
      finding stated as a sentence in `docs/chart-specs.md`.
- [ ] Confirmed the thesis is answerable from primary sources alone. If it
      needs a pollster's internal data or a leaked document, it is the wrong
      thesis for this format.

## Current state

**Thesis fixed 2026-10-03.** Candidate (a), the gap between polling and
results. The reasoning that settled it:

- It is the literal meaning of the site's name, so the branding and the
  argument are the same thing.
- The data is public: AEC results and published polling are both obtainable.
- It survives the political situation changing. Whether the party is rising or
  falling, the question of whether polling matches the vote remains answerable.

Candidate (b), seat-level behaviour of a low-single-digit vote, remains the
stronger *data* story but is a mechanism explanation rather than a finding, so
it is demoted to supporting material. Candidate (c) is withdrawn.

The feasibility angle, now archived at
`docs/archive/2026-10-03-political-feasibility-report.md`, is **rejected as the
thesis**. It forecasts ("a majority government is
statistically and structurally impossible") rather than measures, and a
forecast is not answerable with a yes or a no. See "Disposition of the
feasibility material" below.

## The thesis, written as a single sentence

> Across federal elections since 1996, does polling overstate or understate
> Pauline Hanson's One Nation relative to its actual result, and how much
> weight can that comparison carry?

Answerable yes or no. The first half is the empirical test. The second half is
about the strength of the page's own conclusion, and it is where the sourcing
landed us. **Revised 2026-10-04.** See "The thesis revision" below.

## The thesis revision, and why it was forced

The original second clause was "and does the published margin of error explain
the gap". It had to be abandoned, for a reason worth recording:

Roy Morgan, the most complete Tier B source available, publishes **no sample
size, no margin of error, and no publication date** for its primary voting
intention poll. No methodology page is linked and no data download exists. The
clause therefore had no published input for the largest house in the series.

What replaces it is a statement about the evidence, not about any publisher:

> How much weight can that comparison carry?

The published record supports a comparison of what polling **said** against what
the ballot produced. It does not support a claim about how **precise** each
poll was, because the sources do not state it. So the page reports the
comparison it can make and states the limit of that comparison, in its own
voice, in its own captions. The limit is a property of the evidence on the
table. It is not evidence about anybody's conduct, and the page does not treat
it as such.

### Why this framing and not the other one

An earlier draft of this decision made the missing margin the finding itself,
which would have made the page partly a piece about pollsters' disclosure
practice. That framing was rejected on 2026-10-04. Three reasons:

1. **It is a different subject.** The page is about how one party's measured
   support relates to its result. Whether a publisher discloses a sample size
   is a separate question about a separate set of people, and it would pull the
   page into an argument with a commercial industry it otherwise has no stake
   in.
2. **It invites the charge it provokes.** A page that criticises pollsters for
   not publishing margins can be answered by pointing out that plenty do. The
   page would then be running a weak version of an argument a critic would have
   run better.
3. **It is not what the evidence supports.** One publisher's metadata is not
   evidence about the industry's practice. It was never strong enough to carry
   the thesis, whatever the framing.

The honest version is narrower and stronger: the record states what it states,
the page says what that record can and cannot show, and the reader is not asked
to take anything on trust that a document does not say.

A line that stays regardless: **never impute a margin from an assumed sample
size.** Inventing a precision no source stated is the precise failure mode this
project exists to expose, and it is a lie told in the visual language of
honesty. Where the record is silent, the chart shows silence.

## Framing decision: open test, not verdict

**Decided 2026-10-03.** You hold the view that polling overstates this party.
The page tests that view rather than asserting it. Stated as an expectation the
reader can check, not as a conclusion the reader must accept.

This is the framing, and it is a hard commitment:

> Across federal elections since 1996, did polling overstate or understate
> Pauline Hanson's One Nation relative to its actual result, and how much
> weight can that comparison carry?

The page reports what polling said, what the ballot produced, and the gap
between them. It publishes whichever way the data falls. A result showing
polling was accurate is a publishable finding on an equal footing with one
showing it was not, because the credibility of the series is the product.

Two obligations follow from the open framing:

1. **Scope the polls honestly.** The finding must hold across houses, or be
   explicitly scoped to the houses that publish per-poll figures. Averaging
   across houses and reporting the spread is stronger than picking one house
   and hoping. If one house's method is the outlier, that is a finding too.
   Where a source does not publish a sample size or margin, that is recorded
   as a limit on the comparison, in the page's own voice, not as a claim about
   the source.
2. **Compare like with like.** Polling reports a primary vote; results publish
   a primary vote. The Farrer result exposes the trap: the party won a seat on
   39.53% primary, converted to 57.55% two-party preferred. Comparing polling
   on primary against a result quoted on preferred is a category error, not a
   finding. Each series states its measure in the caption.

### Why not a verdict

A flat claim that polling overstates this party can be dismissed by producing
one poll that did not, and such a poll is cheap to produce. "Here are N polls
from M houses, and here is how often the result landed inside the interval"
cannot be dismissed the same way, because the reader can re-run it. Same data,
materially different defensibility against a hostile reader.

## Scope

**In scope.** Published House of Representatives primary vote for the party
against its actual primary vote at each federal election since 1996. Pollster
house-published tables only. National series first, with the seat-level seat
conversion as a single supporting chart if the data sources cleanly.

**Out of scope, explicitly.** Senate results (a different electoral system, a
different denominator, not comparable on one axis). Party capability, staffing
and volunteer coverage (no primary source, unverifiable). Leadership succession
speculation. Any claim about a named living person's character. Any figure
sourced from a news outlet's chart rather than the originating document.

## Verified ground truth

Checked against AEC primary sources on 2026-10-03. Retrieval detail in
`docs/data-sources.md`.

| Fact | Value | Source id |
|---|---|---|
| Lower house seats held | **1** | `aec-by-farrer-2026` |
| Seat won at | Farrer by-election, 25 May 2026 | `aec-by-farrer-2026` |
| Member | David Farley (One Nation) | `aec-by-farrer-2026` |
| Farrer two-party preferred | 58,294 (57.55%), margin 15,302 | `aec-by-farrer-2026` |
| Farrer primary | 40,042 (39.53%) | `aec-by-farrer-2026` |
| Seats won at 2025 general election | **0** | `aec-hor-2025-party-rep` |
| General elections swept 2005–2025 for a One Nation win | **none** | by-election sweep, `docs/data-sources.md` |

The prototype's "2 seats" and the feasibility report's "0 seats" were both
wrong. The correct figure is 1, and the by-election sweep found no other.

Note the shape of this. A by-election in a regional NSW division is not the
same event as a general-election result, and the 39.53% primary is not a
national figure. Neither belongs on the primary-vote series. If by-election
results appear on the page at all they need their own chart with their own
denominator, which is scope the thesis does not currently carry.

## Disposition of the feasibility material

The prototype files `.css`, `.js` and `index.html`, plus the reference report,
were built to a different thesis and a different design system. They are not a
starting point. Specifically:

- `.css` and `.js` were orphaned and have since been **deleted** (2026-10-04).
  `index.html` never linked them; it loaded Tailwind and Chart.js from CDN.
- `index.html` is a **prose draft only**. Its five-part scrollytelling structure
  and sentences are reusable. Its figures are not: none of them resolve to a
  row in `docs/data-sources.md`. It has since been superseded as the real
  `index.html`, which is now generated from `src/index.template.html` by
  `tools/build.py`.
- `docs/archive/2026-10-03-political-feasibility-report.md` is archived as a
  discarded direction. It is not cited and its numbers do not reach the page.
  It was moved out of `docs/reference/` on 2026-10-04 and its banner now
  records the corrected seat arithmetic, which the original banner predated.

Defects found in the prototype, recorded so they are not reintroduced:

| Defect | Note |
|---|---|
| Hard-coded figures in markup | 76, 2, 34, 7,050, 21,150, 2,800, 87%, 14.3%. House rule is numbers in code and data only |
| No uncertainty shown | Non-negotiable 5. Zero bands on the prototype |
| Fabricated poll results | `#pollResults` renders "1,482 verified responses" and a fixed 64.2/24.5/9.1/2.2 split, hard-coded, unchanged by voting. Invented numbers presented as collected data |
| Chart mixes four measures | Two-party swing, wartime swing, federal swing, a 1998 **state** peak and a required percentage-point surge on one axis labelled "Swing / Primary" |
| Design system inverted | Dark mode, orange, Tailwind, `rounded-2xl`, `shadow-xl`. All four are named in `DESIGN.md` as things not to generate. Orange is the party's brand colour |
| Seat count contradicts the reference report | Page says 2 lower house seats, report says 0. **Both wrong. Verified 1 against AEC on 2026-10-03. See `docs/data-sources.md` retrieval log** |

## Definition of done — checked

- [x] One question, answerable with a yes or no after reading the page.
- [x] One paragraph of scope, with explicit exclusions.
- [x] Framing committed: open test, publishes either result.
- [x] Confirmed answerable from primary sources alone. AEC results are Tier A,
      pollster published tables are Tier B, both in `docs/data-sources.md`.
- [ ] Charts the thesis requires, with each finding stated in
      `docs/chart-specs.md`. Task 0007 onward.

## Definition of done — remaining

The one open box is the chart list, which needs the polling dataset in hand to
scope honestly. Do not guess it. Task 0004 builds the dataset, then 0002 locks
the chart stack, then 0007 writes the specs.

## Open questions

- Does the thesis need a comparator party to mean anything? "Polling
  overstates this party" is more legible alongside "polling is accurate for
  the major parties", but that widens the scope considerably.
- Is one election cycle enough, or does the series need to run from the
  party's founding? A founding-to-present series is stronger but the early
  years have different boundaries and party naming.
- How current does the polling series need to be to be worth publishing? A
  six-month-old poll is not a finding.
- **New, 2026-10-03.** Which measure is the comparison against: primary vote,
  or two-party preferred? Primary is the measure pollsters report, so primary
  is the honest comparison, but it undersells conversion at seat level. The
  page may have to report both measures with the switch point flagged, which
  `AGENTS.md` gotchas already require.
- **New, 2026-10-03.** Do by-election results belong on the page at all? The
  single verified seat came from a by-election, so omitting them makes the
  seat count read as zero and omitting the count makes the seat series look
  flatter than it is.
- **RESOLVED, 2026-10-04.** The second half of the thesis could not be executed
  as written. Roy Morgan, the most complete Tier B source available, publishes
  no sample size and no margin of error, so "does the published margin of
  error explain the gap" had no published input for that house. Decided: the
  thesis is revised to "how much weight can that comparison carry?", and the
  missing margin is handled as a stated limit on the evidence rather than as a
  finding about pollsters. An intermediate framing on 2026-10-03 made the
  absence the finding itself and was **rejected on 2026-10-04** as a different
  subject that would invite the charge it provokes. Non-negotiable 5 is amended
  to match, requiring a visible "no published margin" marker rather than a
  bandless point estimate. Imputing a margin from an assumed sample size is
  prohibited outright and that part stands regardless of framing. See "The
  thesis revision" and the Gotchas entry "Bands are honesty, not decoration"
  in `AGENTS.md`.