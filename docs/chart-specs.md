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

## Chart 01 — The band

**Provisional purpose.** The signature chart: the party's polling trajectory
with its confidence intervals, against its actual result at each election.

- **Question it answers:** how wide is the polling uncertainty band, and does the
  result sit inside it?
- **Data:** `polls` (fielded window, n, margin) and `aec` results by cycle.
- **Form:** line of point estimates with a band, with election results marked as
  discrete points on the same axis.
- **Must not:** smooth the line, truncate the y-axis, or omit a cycle because it
  is inconvenient. Dropping an election is the single most dishonest thing this
  chart could do.
- **The trap:** if the y-axis starts at 3%, the difference between a 4% poll and
  a 5.5% result inflates to fill the screen. Start at zero, or annotate the
  truncation explicitly and visibly.

## Chart 02 — Seat margin

**Provisional purpose.** Where the party's support actually converts to seats.

- **Question it answers:** at what primary vote does a seat become winnable?
- **Data:** seat-level results by division across cycles, with boundary mapping.
- **Form:** one small multiple per state, or a ranked bar of the party's closest
  results with the margin in votes labelled.
- **Must not:** compare seat margins across a redistribution without saying so.
  A margin measured against different boundaries is not a trend.
- **Depends on:** the boundary-mapping helper in `TASKS.md` BACKLOG.

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

**Provisional purpose.** Vote efficiency: seats won per point of vote.

- **Question it answers:** is the party getting more or less out of its vote than
  it should?
- **Data:** national vote share and seat share by cycle.
- **Form:** two lines on one axis, with the gap shaded. The gap is the story, so
  shade it rather than annotating it.
- **Must not:** use seat share from a chamber that is not a single elected body.
  House and Senate are not comparable and must not share an axis.

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