# Implementation plan — Chart 01 and Chart 02

**Spec:** `docs/superpowers/specs/2026-10-04-chart-01-polling-vs-result-design.md`
**Approved by Dale:** 2026-10-04. Chart 02 is provisional pending a visual decision.
**Task:** 0007 in `TASKS.md`.

Written by hand because the `writing-plans` skill referenced by the brainstorming
skill is not installed on this machine. It follows the spec; where the two could
differ, the spec wins.

---

## Standing rules for every task below

Non-negotiable for the whole plan, because every step was preceded by a real
failure of exactly this kind:

1. **Test every new guard by proving it fails.** A guard never seen to fire is
   indistinguishable from one that does not work. Each assertion in step 6 gets a
   test that feeds it bad input and asserts a problem comes back.
2. **No figure is transcribed.** Nothing derived is typed as a literal. It is
   computed at build time from the ingested CSV.
3. **Run the smallest command that covers the change** after each step, and do
   not move on until it passes.
4. **Commit per task**, imperative subject under 72 characters, per `AGENTS.md`.

Baseline before starting: `python3 tools/build.py --check` passes,
`python3 -m unittest discover -s tests` runs 42 tests, all green.

---

## Task 1 — Ingest the discrete One Nation table

**Why first:** everything downstream reads the file this produces.

`tools/ingest_roymorgan.py` gains a reader for the second table on the Roy Morgan
page — 132 rows, 2013 to 2022, with a discrete One Nation column at index 4.

**Steps**

1. Add `ingest_discrete_oned(tables, warnings)`. Identify the table the way
   `ingest_election_results` now does: **by having a discrete One Nation column**,
   not by guessing from header text. There are two such tables; this is the one
   that is *not* the election-results table, so select on `len(rows)` being the
   larger, and assert exactly two candidates so a page restructure fails loudly.
2. Reuse `select_column(header, "One Nation", ...)`. The aggregate-column refusal
   applies here unchanged — a careless mapping could resolve to a combined
   column, which is the trap this whole script exists to prevent.
3. **Exclude election rows.** A row whose label matches `Election` is a result,
   not a poll. This is the 49-versus-48 error: counting the result among the
   polls. Excluding them is a named rule in the code, not an incidental filter.
4. Write `data/polls_roymorgan_oned.csv`, one row per poll wave:
   `house`, `wave_label`, `year`, `fielded_start`, `fielded_end`, `n`,
   `margin_of_error`, `pub_date`, `pvi_oned`, `publishes_n`,
   `publishes_margin_of_error`, `publishes_pub_date`, `source_id`, `retrieved`.
   The three unpublished fields are written **empty**.
5. **Derive the series range from the data, never hard-code it.** Emit a warning
   naming the contiguous complete years and any year with zero usable waves
   (2013 to 2016, and 2017 absent). The 2017 gap must be reported as a source
   property, not interpreted.
6. Verify the 2017 gap is real and not a parsing artefact by re-reading the saved
   HTML for any 2017-dated row. If rows exist that the parser drops, fix the
   parser. **This is the one thing in the plan that could invalidate the series
   range, so it is checked before anything is built on top.**

**Verify**

```bash
python3 tools/ingest_roymorgan.py --html <saved-page.html>
```

Expect 48 data rows. Confirm: `pvi_oned` non-empty on all 48; `n`,
`margin_of_error`, `pub_date` empty on all 48; years 2018 to 2022 only.

**Tests** — mirroring the monthly ones: no `election` row reaches the output;
a discrete-column request still refuses an aggregate column; an unknown column
raises `UnmappedColumn`; the range is derived rather than fixed.

**Commit** `Ingest discrete One Nation polling, 2018 to 2022`

---

## Task 2 — `charts/stats.py`

**Why:** the single place a derived number is computed. Everything else calls it.

New module. Pure functions, no I/O beyond reading the CSV, stdlib only.

```python
load_polls(path) -> list[Poll]        # n, margin_of_error, pub_date stay None
contiguous_years(polls) -> tuple[int, int]
waves_before(polls, year, window) -> list[Poll]   # trailing, excludes the result
window_mean(polls, year, window) -> Mean | None   # mean, n, window, low, high
gaps(results, polls, window) -> list[Gap]          # poll - result, per election
```

`Mean` carries `value`, `n_used`, `window`, `low`, `high`. `Gap` carries `year`,
`result`, `mean`, `n_used`, `signed_gap`.

**Rules encoded here, not in the caller:**

- `window_mean` returns `None` when no waves precede the year. It never
  substitutes a shorter window silently.
- `n_used` is the count **actually used**, which is not always `window`. The 2019
  case is 5 of 12, and that number travels with the result so the caption can be
  generated from it.
- `low` and `high` come from the same waves as the mean. A range over different
  waves than the mean is the tenfold failure mode.
- Every return that carries a number also carries `n_used`. A caller cannot get
  a bare float, so no caller can accidentally label it with the wrong count.

**Tests** — empty input, single wave, fewer waves than the window, a window
straddling an election, `n_used` differing from `window`, and that `low`/`high`
are computed from the same set as the mean.

**Commit** `Add stats module for computed polling figures`

---

## Task 3 — Chart 01 generator

Rewrites `charts/chart_01.py`. Two panels in one figure: the gap bars, and
beneath them the per-election spans.

1. Delete the placeholder `SERIES` block. It exists only to prove the pipeline.
2. Load `data/polls_roymorgan_oned.csv` and `data/roymorgan_election_results.csv`.
   Call `charts/stats.py` for every figure.
3. **Panel 1, the gap:** two bars from a zero rule, poll-minus-result in
   percentage points. Axis centred on zero by construction, so no truncation
   caveat is needed.
4. **Panel 2, the evidence:** per election, a vertical span from `low` to `high`
   across the preceding waves, with the result marked. For 2022 the span tops out
   at the result.
5. Each panel labelled with the wave count it used: "5 waves", "12 waves".
6. Keep the wide and narrow variants from one pass, existing viewBoxes. Keep
   `data-source-id="roymorgan-pvi"` and `data-unsourced` **off** — this chart is
   sourced, so it declares its ids and the registry must resolve them.
7. Both hatch patterns still emitted, for the print block.
8. `<desc>` states the finding, the wave count, and that no wave carries a
   published margin. Written from the computed values.

**Verify** regenerate, then `--check`; eyeball the SVG text for the computed
numbers matching `stats.py` output.

**Tests** — the generator's declared source ids resolve; no numeric literal from
the dataset appears in the generator source; both variants emit.

**Commit** `Build Chart 01 from ingested polling data`

---

## Task 4 — Chart 02 generator

New `charts/chart_02.py`. Two lines on one axis, both as a share of the
151-seat House, gap shaded.

1. National primary vote by election from the cross-check table.
2. Seats won at each general election. **0 for every election from 1996 to
   2025**, per `aec-hor-2025-party-rep`. The chart's claim rests on a flat line,
   so it must be sourced as carefully as any other figure.
3. Seat share computed as `seats / 151`. One seat is 0.66%.
4. **Farrer 2026 appears as an annotation only.** Never a point on the series.
5. Mark the 2004 to 2016 discontinuity; it is the same break recorded in
   `docs/data-sources.md`.
6. Emit `data-unsourced="false"` with its source ids, and register the chart in
   the placeholder-figures section of `docs/data-sources.md` as **sourced**, so
   the existing build assertion passes rather than being worked around.
7. Wide and narrow variants. Label floor 16px wide, 10.7px at 320px viewport.

**Verify** regenerate, `--check`, and confirm the by-election string appears in
the SVG but no by-election point exists on the axis.

**Tests** — a by-election row entering the plotted series fails the build;
seat share uses 151 and only 151; House and Senate never share an axis.

**Commit** `Build Chart 02, seat share against vote share`

---

## Task 5 — Template prose

`src/index.template.html` gains a second `<!-- chart:02 -->` placeholder and
replaces the placeholder caption with the real one.

**The caption's figures are injected, not typed.** The build substitutes them
from `stats.py`. If `stats.py` changes, the caption changes; if the substitution
fails, the build fails. This is the direct defence against the booth-coverage
drift, where a prose figure came to differ from the model that produced it.

Caption must state, from computed values:

- the wave count and the window used per election
- "N of M waves publish no margin of error, no sample size or publication date"
- the finding in one sentence, with its direction per election
- that it is not a claim about any publisher's competence

**Verify** `--check`; confirm no digit in the caption is a literal in the
template; confirm the placeholder-prose assertion still passes.

**Commit** `Write Chart 01 and 02 captions from computed values`

---

## Task 6 — The nine build assertions

All in `tools/build.py`. Each verified to fail.

1. A chart may not resolve solely to cross-check-only source ids while any row
   carries `requires_aec_confirmation=yes`. **This is the gate.**
2. The wave count stated in a caption equals the count used in the arithmetic.
   Two expected values (5 and 12), and it is the check that would have caught
   49-versus-48.
3. Every poll row used has `margin_of_error` null and
   `publishes_margin_of_error=no`. A populated margin is either a source change
   or an imputation; the second is prohibited.
4. No poll-derived figure is a literal in any chart or template.
5. Every wave used has a field window.
6. No wave outside the contiguous range appears without a `blank_reason`.
7. Caption wave count equals the CSV row count used.
8. Seat share is `seats / 151` and only 151. House and Senate never share an axis.
9. A by-election row never enters the plotted general-election series.

**The gate is a real gate.** While 2019 and 2022 results remain
cross-check-only, `--check` **fails**, and that failure is the correct state, not
a bug to be suppressed. Expect CI to be red on this commit series until task 0003
delivers AEC figures, and say so plainly in the commit message rather than
loosening the assertion.

**Tests** — each assertion gets a test proving it fails on bad input. For the
gate specifically, assert it fails with cross-check-only ids and passes once an
`aec-hor-*` id is present.

**Commit** `Refuse unconfirmed election results and unsourced figures`

---

## Task 7 — Prose, registry, TASKS

1. `docs/data-sources.md` — register `polls_roymorgan_oned.csv`, its row count,
   the contiguous range, and the three null fields with the reason each is null.
2. `docs/right-of-reply.md` — unchanged; the chart makes no claim about the
   party beyond measurement.
3. `TASKS.md` — 0007 status, Events entry recording the finding and both charts.
4. `docs/chart-specs.md` — Chart 01 marked as built; Chart 04 pointer updated.

**Commit** `Register the polling dataset and update task records`

---

## Task 8 — Browser verification

Not automatable, and the reason the print check exists separately. Measure, do
not assume:

- 320px, 640px, 1280px. Label floor 16px wide, 10.7px at 320px viewport.
- Both charts render; both variants switch at the 640px breakpoint.
- `prefers-reduced-motion` honoured.
- The claim is legible with images off: `<title>` and `<desc>` on every chart.
- The by-election annotation is visible and clearly not a data point.

Screenshot each width. If the label floor is breached, fix the viewBox rather
than accepting the measurement — the task 0006 note records why.

**Commit** `Verify both charts in a browser at three widths`

---

## Deliberately not in this plan

- **Task 0003**, AEC confirmation. The gate waits on it. Nothing here can
  substitute for it and no step pretends otherwise.
- **The print check.** On hold by Dale's decision, 2026-10-04.
- **Per-division seat efficiency.** Needs the archived model's eight 2022
  primaries verified against AEC first. In `TASKS.md` BACKLOG.
- **Any national polling aggregate across houses.** Only Roy Morgan has a
  discrete column for this party.

## The order this must be done in

1, then 2, then 3 and 4 in either order, then 5, then 6, then 7, then 8.

Steps 1 and 2 are the foundation and nothing works without them. Step 6 is last
because its gate deliberately fails until task 0003 lands, and putting it last
means the red CI is a known, explained state rather than a surprise mid-build.