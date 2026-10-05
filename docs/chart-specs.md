# Chart specs

What each chart needs, what it may claim, and what it must not claim. A chart
not listed here does not ship.

Written before the thesis is finalised, so the entries are provisional in shape
and pending in detail. Task 0001 rewrites this file.

---

## Universal requirements

Applies to every chart below.

- Inline SVG, `role="img"`, with `<title>` and `<desc>`.
- A caption that states the **finding**, not the subject of the chart. "Polling
  has not tracked the vote" beats "Vote intention versus result".
- Source note directly beneath, per `standards.md`.
- Uncertainty bands wherever a poll-derived number appears.
- Subject series in `--color-ink`, context in `--color-ink-muted`. No party
  brand colour.
- Direct labels instead of a legend where there are fewer than 8 series.
- A linked data table. Every chart.
- At least one annotation with a leader line, saying what a reader should notice.

---

## Chart 01 — Polling against the ballot box

**Built 2026-10-04. Spec of record:**
`docs/superpowers/specs/2026-10-04-chart-01-polling-vs-result-design.md`.
This entry is retained for the reasoning, not as the build spec.

**Numbering note.** The chart built as `charts/chart_01.py` is *not* the form
originally sketched here — a single line of point estimates against results. The
built form is two panels: polling minus result from a zero rule, and the span of
polling values before each election with the result marked against it. The form
changed because the band this spec assumed **does not exist**: no wave in the
series publishes a margin of error, a sample size or a publication date, so
there is no band to draw and none is imputed.

- **Question it answers:** did polling overstate or understate the party's vote,
  and by how much?
- **Data:** `data/polls_roymorgan_oned.csv` (48 waves, 2018 to 2022) and
  `data/roymorgan_election_results.csv`.
- **Form:** two panels in one figure. Panel 1 is the finding — polling minus
  result in percentage points, from a zero rule, so the axis is centred on the
  quantity being measured. Panel 2 is the evidence — where polling sat across
  the preceding waves, as a span rather than a line, with the result marked.
- **The finding, computed at build time:** polling ran **0.60 points high in
  2019** and **1.29 points low in 2022**. Wrong in both directions, which is
  what makes this an open test rather than a verdict.
- **The marker.** "N of M waves publish no margin of error, no sample size and
  no publication date," in the figure, the caption and the `desc`. It is not
  optional and not decorative. It marks the edge of what the comparison can
  show, in the page's own voice. **It is not a claim about pollsters and must
  not be captioned as one.**
- **Must not:** impute a margin from an assumed sample size, ever. A fabricated
  band is a fabricated number in the visual language of honesty.
- **Must not:** smooth the line, truncate the y-axis, or omit an election
  because it is inconvenient. Dropping an election is the single most
  dishonest thing this chart could do.
- **Must not:** draw a line between the waves. They are fortnightly snapshots
  with no model between them, and a line asserts values nobody measured. A span
  states what was published and nothing more.
- **The trap:** if the y-axis starts at 3%, the difference between a 4% poll and
  a 5.5% result inflates to fill the screen. Start at zero.

**Gated.** `tools/build.py --check` refuses this chart while its only source is
`roymorgan-pvi`, which is marked `cross_check_only: yes` in the registry. It
clears when task 0003 confirms the 2019 and 2022 results against the AEC.

## Chart 05 — Withdrawn

**Created 2026-10-03, withdrawn 2026-10-04.** Kept here so the reasoning is not
re-litigated.

The chart would have counted how many published polling waves carry a sample
size and a margin of error, by house and by year. It was a chart about pollsters'
disclosure practice.

**Rejected.** It made the page a piece about the polling industry rather than
about one party's measured support against its result. It is a different
subject with a different set of people in it, and it invited the obvious
rebuttal that plenty of pollsters do publish these figures, which would have
left the page running a weaker version of an argument a critic could have run
better. One publisher's metadata was never strong enough to carry that claim.

The underlying fact is not discarded. It survives as a stated limit on the
evidence, carried in Chart 01's caption and in the page's own voice. See "Where
there is no band" in `DESIGN.md` and the Gotchas entry "Bands are honesty, not
decoration" in `AGENTS.md`.

## Chart 02 (spec numbering) — Seat margin

> **RENUMBERED 2026-10-05 to avoid a collision.** This entry was "Chart 02".
> The seat-efficiency chart moved forward from editorial Chart 04 and was built
> as `charts/chart_02.py`, because build order and spec numbering are different
> things and the file name follows build order. Two entries now claim 02.
>
> **This entry is now editorial Chart 06 — Seat margin, by division. Not built.**
> Nothing references it under the name 02 except history.

**Provisional purpose.** Where the party's support actually converts to seats,
at the level an individual seat is won or lost.

- **Question it answers:** at what primary vote does a seat become winnable?
- **Data:** seat-level results by division across cycles, with boundary mapping.
- **Form:** one small multiple per state, or a ranked bar of the party's closest
  results with the margin in votes labelled.
- **Must not:** compare seat margins across a redistribution without saying so.
  A margin measured against different boundaries is not a trend.
- **Must not:** use the national series as a substitute for this. The built
  Chart 02 answers a different question at national level; this one is about
  individual divisions.
- **Depends on:** the boundary-mapping helper in `TASKS.md` BACKLOG.
- **Distinct from** the built Chart 02, which is national vote share against
  national seat share. That one shares no data with this one.

## Chart 03 — Preference flow

**Provisional purpose.** What happens to a low-single-digit primary vote when
preferences are counted.

- **Question it answers:** how much of a primary vote survives to final.
- **Data:** preference data, which is only exhaustively available under the
  exhaustive-ordering system from 2022. For earlier cycles this is partial or
  modelled, and the chart must say which.
- **Form:** a single election's flow, or the party's national two-candidate
  preference over cycles.
- **Must not:** present modelled preference data as observed. If the pre-2022
  figures are estimates, they are hatched differently and labelled as estimates.
- **Open question:** whether this is answerable to a standard worth publishing.

## Chart 04 — Seat share against vote share

> **BUILT as `charts/chart_02.py`, 2026-10-04.** Spec of record:
> `docs/superpowers/specs/2026-10-04-chart-01-polling-vs-result-design.md`,
> section "Chart 02 — Seat efficiency". Numbering here is retained for
> continuity; build order is 01 then 02.
>
> **AWAITING A KEEP-OR-CUT DECISION.** Dale will decide whether it stays after
> seeing it rendered. It shares no data and no code with Chart 01 beyond
> `charts/stats.py`, so cutting it costs nothing and the polling chart is
> unaffected.
>
> **Note on the gate.** This chart is *not* behind the cross-check gate. Its
> figures come from the AEC's own per-election files, so it passes
> `tools/build.py --check` today. Chart 01 is the one that stays red pending
> task 0003. The two can therefore ship independently.

**Provisional purpose.** Vote efficiency: seats won per point of vote.

- **Question it answers:** is the party getting more or less out of its vote than
  it should?
- **Data:** `data/aec_election_results.csv` — national vote share and seat share
  by election, 2001 to 2025, both from the AEC.
- **Form:** two lines on one axis, with the gap shaded. The gap is the story, so
  shade it rather than annotating it.
- **Built form.** Nine general elections. The vote line climbs from 4.34% to
  6.40%; the seat line is flat at zero across all nine. Each share is measured
  against the House as it was then — 150 seats to 2016, 151 from 2019.
- **Must not:** use seat share from a chamber that is not a single elected body.
  House and Senate are not comparable and must not share an axis.
- **Must not:** plot the Farrer 2026 by-election on the general-election line.
  Different electorate, different field, different denominator. It is an
  annotation on the chart, never a point on the series. Its figures live in
  `data/aec_by_election.csv`, which carries
  `plottable_on_general_election_series = no` and the build checks that flag.
- **Must not:** join the 2004 to 2016 block into one continuous line with the
  years either side. Those five elections sit at 0.17 to 1.29 per cent against
  4.34 in 2001, which is slate coverage rather than a collapse and recovery. The
  block is drawn as a marked span.

---

## Charts considered and rejected

Kept so the reasoning is not re-litigated.

| Chart | Rejected because |
|---|---|
| Map of party vote by division | Clichéd, low information density, and the choropleth implies a spatial pattern that a statewide uniform swing will produce anyway |
| Pollster house effects | Interesting, but it evaluates pollsters rather than the party, which is outside the thesis |
| Donations and funding | A different thesis. Possibly its own site |
| Leader approval | Not available as a primary series at the required granularity |
| Seat-by-seat swing heatmap | Impressive and unreadable at the scale a single page allows |

---

## Deliberate omissions

Not oversights. Each was considered and ruled out.

- **No social media embed.** The subject's accounts are not a primary source.
- **No stock imagery.** A party leader's photograph imports tone. The page is
  figures.
- **No live or auto-updating widget.** A number that moves under the reader is a
  number that cannot be cited. The page is dated and fixed, like a newspaper.
- **No interactive filter.** Filtering a chart is how a reader finds the version
  that supports their prior. The page shows what it shows.