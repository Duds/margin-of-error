---
status: active
type: project
project: margin-of-error
owner: Dale Rogers
updated: 2026-10-03
domain: marginoferror.com.au
---

# AGENTS.md — Margin of Error

Single-page data journalism site on Pauline Hanson's One Nation. Editorial
control sits with the author; agents may draft, gather, chart and document,
but no factual claim ships without a primary-source citation in the repo.

## Identity

One scroll, one thesis. The site answers a single question about the party's
electoral footprint, using electoral commission data rather than commentary.

The name is literal and is the design thesis: the party sits close enough to
the noise floor of Australian polling that the gap between *measured* support
and *actual* results is the story. Every chart must respect that framing. If a
chart could have been published by either a partisan outlet or its opponent, it
is not yet specific enough.

## Non-negotiables

These are not style preferences. Violating them is a defect.

1. **Living persons.** Pauline Hanson is living. Under Australian defamation law
   (Broadcasting Services Act 1992, ss 17 to 23) truth is an absolute defence,
   so "true" is not sufficient: it must be traceable to a cited primary source
   that a reader can independently check.
2. **Primary source or absent.** Every number on the page resolves to a
   specific document in `docs/data-sources.md`, cited at the point of use. No
   figure reaches the page sourced from another news outlet's chart.
3. **Right of reply before publication.** Send the draft thesis and the specific
   claims to the party's registered address. Record the date sent, the date
   replied, and any reply verbatim in `docs/right-of-reply.md`. A reply is
   published, not summarised favourably.
4. **Neutral register.** Descriptive, not evaluative. "Lost Griffith by 630
   votes" is reporting. "Collapsed" and "dishonest" are advocacy. Cut the
   second category even where it is accurate.
5. **Uncertainty is always visible.** No bandless point estimate for any
   poll-derived figure. The margin of error appears wherever a number does.
   **Amended 2026-10-04.** Where a source does not publish a margin of error,
   the figure is not drawn as a bandless point estimate. It is drawn with a
   visible "no published margin" marker, and the absence is stated at the point
   of use as a limit on what the comparison can show. It is a property of the
   evidence on the table, not a finding about any publisher, and the page does
   not present it as one. Never compute a margin from an assumed sample size.
   See "Bands are honesty, not decoration" in the Gotchas.
6. **Corrections.** `docs/corrections.md` is append-only and public. Silent
   fixes are not fixes.

## Structure

- `AGENTS.md` — this file, the non-negotiables, and house rules
- `DESIGN.md` — visual system, tokens, chart and uncertainty-band spec
- `TASKS.md` — tiered work list plus append-only `## Events` log
- `_tasks/` — one detailed task file per unit of work, spawned from TASKS.md
- `docs/` — sourcing registry, standards, chart specs, right of reply
- `docs/archive/` — rejected and superseded work, retained under the rules in
  `docs/standards.md` under "Discarded work". Nothing here may be cited.

## Map

Start here in this order:

| File | Read it for |
|---|---|
| `DESIGN.md` | Tokens, the uncertainty-band motif, chart rules, accessibility floor |
| `docs/data-sources.md` | The canonical source registry. Add a row before adding a figure |
| `docs/standards.md` | Citation format, sourcing tiers, corrections, accessibility bar |
| `docs/chart-specs.md` | What each chart needs and what it must not claim |

## Stack

Provisional, pending the lock task in `_tasks/0002-lock-chart-stack.md`.

Precedent in the sibling project [rock-oracle](../rock-oracle) is a
self-contained vanilla HTML/CSS/JS site with no build step, which suits a
single page. Do not introduce a framework, a bundler or a framework CSS
utility library without writing the tradeoff into `_tasks/` first. Every
dependency must be open-licensed and must be vendored or served from a
verifiable CDN with an integrity hash recorded in `docs/data-sources.md`.

## House rules

- Kebab-case for front-end and documentation files and folders:
  `index.html`, `margin-of-error.css`, `motion.js`, `chart-01.svg`.
  `snake_case` for Python modules and data files: `chart_01.py`,
  `test_scales.py`, `data-sources.md`. **Two exemptions are load-bearing, not
  preference:**
  - **Python modules stay `snake_case`, including test files.** A hyphenated
    `test-scales.py` matches the `unittest` discovery pattern `test*.py` but
    then cannot be imported, because a hyphen is not a legal identifier. It is
    silently skipped: `python3 -m unittest discover -s tests` reports
    `NO TESTS RAN` and **exits 5**. Adding `tests/__init__.py` does not rescue
    it. Verified 2026-10-04. A rename here would switch the test suite off
    without throwing, which is the worst failure mode this repo has.
  - **Fonts and third-party assets keep their upstream names**, as shipped in
    `assets/fonts/`. Google Fonts naming is not ours to normalise.
- Numbers in code and data only. No hard-coded figures in markup or prose.
- Plain English. No jargon without a definition on first use. The audience is
  an interested reader, not a statistician.
- Prose is written for a reader who has not voted in twenty years. Explain
  first preference, the two-party swing, and vote efficiency once, properly.
- Commits imperative, under 72 characters. One task per commit where possible.
- No credentials, no personal data, no subscription addresses in this repo.

## Gotchas

- Preference data is not vote share. On and after 2022, Australian federal
  ballots exhaustively numbered and preferences dominate the count. Most
  published "primary vote" figures are now a simplification; state which
  measure each chart uses and say so in the caption.
- Polling is a moving target and pollsters revise. A number that was correct
  when published can be wrong now. Pin every poll to a `fielded` window and a
  `pub_date`, and prefer the house-published figure over a media summary.
- AEC redistributions change seat boundaries, so a seat's margin across
  electoral cycles is not always comparable. Label boundaries by the AEC
  redistribution in force at that election.
- Denominators differ between "party primary" and "party including
  preferences". Never mix them in one series without flagging the switch point.
- The party has been registered under several names across its history. Match
  on the AEC party abbreviation for the election in question, not on the
  modern name, or historical series silently drop rows.
- **Bands are honesty, not decoration.** Discovered 2026-10-03: Roy Morgan, the
  most complete Tier B polling source available, publishes no sample size, no
  margin of error and no publication date, and links no methodology page and no
  data download. So the uncertainty band the design system is built around
  cannot be drawn for a large share of the series. The comparison the page can
  make is what polling said against what the ballot produced, and it cannot
  extend to how precise each poll was. Draw the absence, state the limit, and
  never impute a margin from an assumed n.
- **Do not write about pollsters.** The page is about one party's measured
  support against its result. Whether a publisher discloses a sample size is a
  different subject, about different people, and an earlier framing that made
  it the finding was rejected on 2026-10-04. State the limit on the evidence in
  the page's own voice. Do not attribute a practice to pollsters as a class,
  and do not build an argument a critic would run better than the evidence
  supports.
- **Ingest by column name, never by offset.** Roy Morgan's monthly primary
  voting intention table has no discrete One Nation column. One Nation is
  folded into a combined "Other Parties (ALL)" column. For the April 2025
  wave that combined figure is 18.5% against One Nation at 7.5%, so a
  fixed-offset read overstates the party by more than double. Select columns by
  header and fail loudly on an unmapped column.
- **`aec.gov.au` returns HTTP 200 with a 404 body** for retired URL patterns.
  Any fetch script must validate on page title or body text, never on status
  code alone. The live archive is `results.aec.gov.au`, one directory per
  election event.
- **A gate that refuses to write also freezes what it gates.** Discovered
  2026-10-06: `tools/build.py` would not write `index.html` while a publication
  gate was red, so while the gate was red — which is its permanent state until
  task 0003 lands — the page could not be regenerated. Three fixes to the
  sources never reached the artefact, a session reported them as verified, and
  nothing could tell us. Publication is now gated on `--check` exiting 0, and
  the artefact is always buildable: `--draft` writes it marked `noindex` with a
  banner, so a page under review is current with its data without ever looking
  shippable. Never let a publication gate become a build gate.
- **Check the artefact, not just the source.** The provenance, caption and
  accessibility checks all read `charts/*.svg` and the template. A defect the
  *build* introduces is invisible to them. This is how `data-source-id` got
  suffixed like an element id — `roymorgan-pvi-narrow`, an id in no registry —
  while every source file stayed correct. `artefact_source_id_problems` and
  `test_committed_artefact_matches_a_fresh_build` now assert against
  `index.html` itself.
- **A CI step ordered after a step that fails by design never runs.** The drift
  check lived in its own workflow step, behind `--check`, which is red by
  intent. It was recorded as "verified to fail on a hand-edited artefact". It
  had never executed, because neither had CI: the workflow was never on
  `origin/main`. Put the checks that must produce signal *before* the known-red
  gate, and fold drift into `--check` so step ordering cannot hide it.
- **Validate the file that ships, not the file that is convenient.** Discovered
  2026-10-18: `tools/ingest_roymorgan.py` ran `validate()` over the monthly table
  only, never over `polls_roymorgan_oned.csv` — the file every chart figure is
  computed from. Nine cross-month waves had been written with a corrupted
  fieldwork window ('April 25 - May 1, 2022' became 2022-04-01 to 2022-04-25)
  because `parse_field_window()` applied the label's leading month to every day
  number. Nothing failed, because the one file with a guard could not contain the
  defect and the one file with the defect had no guard.
- **A figure nothing renders cannot be caught by a rendering check.** The same
  nine windows were invisible in the charts: the windows are never drawn and the
  figures are grouped by year, so not one plotted number moved. A wrong fieldwork
  window is still a wrong citation, because `docs/standards.md` requires the
  window in every polling citation. Check the data against its own labels; do not
  rely on the artefact to reveal it.
- **Registry families must be resolvable ids.** A `source_id:` line carrying a
  trailing parenthetical does not match the parser at all, so the family
  registered nothing and seven of nine AEC elections were unciteable. List a
  family's years in a `years:` field. A family with no `years:` registers
  nothing by design, and `test_every_ingested_aec_source_id_resolves` fails if
  the data cites an id the registry does not hold.- **Measure at the width your rule governs.** Discovered 2026-10-18, and it is
  the second time: task 0008 set the chart breakpoint at 1100px from readings
  taken at 320, 640 and 1280px, and never at 1100px itself. The wide variant
  reaches the 16px floor at 1135px, so 1100-1134px was rendering 15.48px. A
  threshold derived from measurements that exclude the threshold is a guess
  dressed as a finding. When you set a limit from data, measure at the limit and
  one step either side. `TestVariantBreakpoint` now derives it from the geometry
  (`--track-full` less two gutters equals the wide viewBox) so it cannot be
  re-derived from the wrong sample.
- **A guard can test the wrong neighbour and stay green on its own defect.**
  Found again 2026-10-18 in `chart_01.py`: panel 2's plot was lowered to clear
  its title only when `span_title_y < gap_bottom + 64`, which is false exactly
  when the title had been pushed furthest down — the only case needing the room.
  Every constant was reasonable; the comparison named the wrong reference. When
  you write a guard, ask *which* quantity it must be bounded by, and add a test
  that restores the superseded logic and asserts the guard fires on it. Passing
  a test that never exercised the defect is how this class survives.
- **When you fix a bug by moving code into a function, the move is where the
  next bug is.** Extracting the panel placement above turned up a second flaw in
  the same three lines: `span_title_y + 14` measured a one-line title's descent,
  but the title wraps to three lines on narrow, so it was measured from the wrong
  baseline — the same category of error as the bug being fixed. Re-derive the
  arithmetic when you extract it; do not transcribe it.
