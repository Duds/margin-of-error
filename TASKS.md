# TASKS — Margin of Error

Tiered task list. Context notes in the `>` block under each item carry
session-to-session continuity; update them when the state changes.

Each active task has a detailed file in `_tasks/`. TASKS.md is the index.

---

## NOW (Active)

- **0001 — Editorial thesis and the question the page answers** (COMPLETE)
  > File: [`_tasks/0001-editorial-thesis.md`](_tasks/0001-editorial-thesis.md)
  > Thesis: across federal elections since 1996, did polling overstate or
  > understate the party's vote relative to its actual result, and how much
  > weight can that comparison carry? Scope is House of Representatives primary
  > vote, pollster published tables only. Senate, party capability and volunteer
  > coverage explicitly excluded. The page is **not** about pollsters.
  > Framing: **open test, not verdict.** The page publishes whichever way the
  > data falls, including showing polling was accurate.
  > The feasibility angle is **rejected as the thesis**. It forecasts rather
  > than measures. The document that made the argument now lives at
  > `docs/archive/2026-10-03-political-feasibility-report.md` (moved out of
  > `docs/reference/` on 2026-10-04, banner strengthened with the corrected
  > seat arithmetic). The prototype files `.css` and `.js` at the
  > repo root were orphaned artefacts of that discarded direction: neither was
  > referenced by any HTML, CSS or Python file, and `.css` pulled three Google
  > Fonts families the real page does not use. **Both deleted 2026-10-04.** They
  > were untracked, so the deletion was not recoverable and was gated on a
  > reference check first. See BACKLOG for the record.
  > `index.html` is **no longer an orphan.** It was a prototype prose draft,
  > and is now the generated output of the 0006 build. Its prose was rewritten
  > by hand into `src/index.template.html`; nothing of the prototype's figures
  > survived. Seat count in the prototype corrected to 1, verified against AEC.
- **0006 — Build the page shell** — typography, grid, source-note component.
  **(COMPLETE 2026-10-04)**
  > Built and verified in a browser at 320px, 1280px and reduced-motion. Files:
  > `src/index.template.html` (hand-written prose + `<!-- chart:NN -->`
  > placeholders), `src/margin-of-error.css` (420 lines: tokens, reset, grid,
  > typography, figures, focus, motion, print — **not** tokens only as first
  > recorded), `src/motion.js` (no library), `tools/build.py` (injects charts,
  > validates, `--check` for CI), `charts/scales.py` +
  > `charts/chart_01.py`, `tests/test_scales.py`
  > (21 tests passing, via stdlib `unittest`). `index.html` is generated and
  > committed.
  > The template/output separation held: prose stayed in the template, and the
  > four layout defects below were all found by measuring the rendered page
  > rather than by reading CSS.
  > Originally scoped as:
  > **Template/output separation, established:** `src/index.template.html` is
  > hand-written and never generated; `index.html` is generated output and
  > never hand-edited; `<svg>` blocks inject at `<!-- chart:NN -->`.
  >
  > **Fonts vendored,** five latin files, **345.9KB total** (354,180 bytes), all
  > OFL-1.1, registered in `docs/data-sources.md`. Newsreader `opsz` roman +
  > italic chosen over the
  > lighter `wght` cut, affordable only because the budget was raised to 400KB.
  > `crossorigin` on the preloads is load-bearing and must not be removed.
  >
  > **Four layout defects found by measuring, not by reading CSS:**
  > 1. A `<figure>` sized by an `<svg>` with only a `viewBox` collapses to the
  >    300x150 replaced-element default, so the chart rendered 185px in a 285px
  >    column. Fixed with `width: 100%` on the figure.
  > 2. `margin-block` on `figure` left the browser default 40px inline margins,
  >    pushing the page 20px past a 320px viewport. Fixed with a full `margin`.
  > 3. A figure nested inside `.col-prose` is trapped in columns 2 to 8 and can
  >    never reach the 1120px breakout track: measured 520px wide at 1280px, with
  >    labels at 7.4px. Charts are now siblings of the prose section.
  > 4. The wide viewBox was 1120 while the track renders 1072 (24px padding each
  >    side), so 16px labels came out at 15.3px, under the DESIGN.md floor.
  >    viewBox is now 1072 and labels measure exactly 16px.
  >
  > Depends on: 0002 (satisfied).
  > **Carried forward: RESOLVED 2026-10-04.** The build now refuses an unsourced
  > chart. It had previously been recorded that "the build does NOT yet refuse to
  > publish an unsourced chart", which was the correct gap at the time and is no
  > longer true. See the `## BACKLOG` citation-resolver entry for what landed.

---

## NEXT (Ready to Start)

- **0002 — Lock the chart stack** — `vanilla-svg` vs `Observable Plot` vs `D3`. **(COMPLETE, locked 2026-10-03)**
  > **PROPOSED 2026-10-03, awaiting sign-off. Recommendation revised the same
  > day** after four options were costed. Now: **build-time SVG generation in
  > Python, stdlib only, no charting library, no client-side JS, no bundler.**
  > Full reasoning and measurements in
  > [`_tasks/0002-lock-chart-stack.md`](_tasks/0002-lock-chart-stack.md).
  > **Superseded recommendation:** hand-built inline SVG on a d3 subset. It was
  > right on payload but wrong on principle: a hand-inlined chart path in
  > `index.html` is a transformation done by hand, which `docs/standards.md`
  > forbids, and it makes the page's most load-bearing number the one artefact
  > with no code path from raw data. Python also wins on the original metric,
  > 0KB client JS against 9KB for the d3 subset.
  > **Verified personally,** not taken on trust: a 68-line stdlib generator
  > produced a 1,919 byte chart (704 bytes gzipped) carrying `role="img"`,
  > `<title>`, `<desc>`, the native hatch `<pattern>`, and zero raw hex, then
  > rendered and inspected in a real browser.
  > **Two bugs found while proving it,** both to carry into 0007: axis padding
  > unpacked in the wrong order gave an inverted plot area, and **a lone banded
  > poll collapses to a zero-width polygon, hiding a margin that was actually
  > published.** The second is the worst bug class this site has, so 0007 needs
  > an assertion that no band element has zero width.
  > Rejected with numbers: matplotlib (zero `role`/`title`/`desc` in output,
  > text-to-paths by default, 133MB), vega-lite build-time (9.4KB, emits no
  > `<defs>`/`<pattern>`, custom themes silently no-op), vega-embed runtime
  > (297KB gzip), Observable Plot (91KB gzip), Chart.js (canvas cannot carry
  > `role="img"`).
  > **Awaiting:** sign-off, plus one open decision — whether the generated SVG
  > is inlined into `index.html` by the build (keeps `var()` fills working) or
  > referenced as a committed `.svg` file via `<img>` (breaks CSS variable
  > inheritance across the document boundary). This determines whether
  > `index.html` is hand-written or generated, so it must land before 0006.
  > **RESOLVED 2026-10-03: inlined into `index.html` by the build**, so `var()`
  > token fills inherit from the page stylesheet and a token change re-skins
  > every chart without regenerating. The accepted cost is that `index.html`
  > becomes a generated artefact, mitigated by the template/output separation
  > now specified in the 0006 entry under NOW.
- **0003 — Source the AEC data** — **(COMPLETE 2026-10-18.)**
  > `tools/ingest_aec_seats.py` reads all nine general elections, 2001 to 2025,
  > from AEC primary sources; both axes (national primary and seats won) come
  > from `HouseFirstPrefsByPartyDownload`, and the chamber size from the party
  > representation download. Roy Morgan agrees with the AEC to within 0.04 points
  > at every one of the nine.
  > **Closed 2026-10-18 by moving Chart 01's result axis onto `data/aec_election_results.csv`.**
  > `stats.load_results()` now reads the AEC series and carries each row's
  > registry `source_id` through `Gap.result_source_id`, so the chart cites the
  > elections it actually drew rather than a typed list. `roymorgan-pvi` stays
  > `cross_check_only: yes` — correctly, since it is a cross-check for a *result*
  > and a source of record for *polling* — and the chart clears the gate by
  > citing a confirmed AEC id beside it. That is the rule working as designed,
  > not the marker being removed.
  > **The spec's claim that no chart code would change was wrong**, and the
  > correction is worth keeping: `charts/chart_01.py` read
  > `primary_vote_oned_pct` and `requires_aec_confirmation`, neither of which the
  > AEC file has, so pointing it at the AEC data raised `KeyError`. Two column
  > names that look interchangeable are two different sources, which is why
  > `load_results()` now refuses a file without `primary_vote_pct` by name.
  > Also found on the way: the source-file provenance check tested
  > `sid not in registry` as a raw substring while the artefact check used the
  > parsed entries, so the two disagreed about family-expanded ids —
  > `aec-hor-2019-fp-by-party` was registered and refused at the same time. Both
  > now resolve through `_registry_entries()`.
  > **`tools/build.py --check` exits 0 for the first time.** The gate-red test
  > class was inverted rather than deleted, and the gate is still proven to fire
  > by citing only the cross-checked series.
  > AEC publishes results by election, one event id per cycle. Historical series
  > must match on AEC party abbreviation per election, not the modern name, or
  > rows drop silently: HAN in 2001 and 2004, ON from 2007.
  > **1996 cannot be sourced.** The AEC archive begins at 2001, so the spec's
  > "1996 to 2025, ten general elections" is unsourceable as written. The series
  > is nine.
- **0004 — Establish the polling dataset** — fieldwork dates, house, n, margin.
  > **INGEST BUILT 2026-10-04. The structural blocker stands.**
  > `tools/ingest_roymorgan.py` reads the Roy Morgan PVI page and writes
  > `data/polls_roymorgan.csv` (138 waves) and
  > `data/roymorgan_election_results.csv` (10 elections). Both are reproducible
  > from a saved page. **No sample size, no margin of error and no publication
  > date exist to ingest** — re-verified on the live page by string search for
  > `sample size`, `margin of error`, `margin of sampling error`, `interviewed`,
  > `confidence interval`, `plus or minus` and `+/-`: zero matches. Those fields
  > are written null and stay null.
  > **The trap is now enforced in code, not prose.** The monthly table has no
  > discrete One Nation column. The nearest cell, "Other Parties (ALL)", reads
  > 18.5 for the April 2025 wave against One Nation at 7.5, and the
  > publisher's own footnote says the combined figure "includes support for One
  > Nation (highlighted in the release) of 7.5%" — so the party is a subset of
  > that cell, not the cell. `select_column()` selects by header text, raises
  > `UnmappedColumn` on anything absent, and refuses a **discrete** party
  > request that resolves to an **aggregate** column. `validate()` additionally
  > fails if `pvi_oned` is ever populated on the monthly table.
  > **CORRECTION, 2026-10-04, after Dale asked about the prototype: the
  > monthly claim above is too strong and partly wrong.** Roy Morgan's page
  > carries a **second, separate** table with a discrete One Nation column —
  > 132 rows spanning 2013 to 2022. The ingest did not read it, because it keys
  > off the election-results table. Per-year count of waves carrying a discrete
  > figure:
  >
  > | Year | Waves with a discrete One Nation figure |
  > |---|---|
  > | 2013 | 0 of 7 |
  > | 2014 | 0 of 26 |
  > | 2015 | 0 of 26 |
  > | 2016 | 1 of 12 |
  > | 2018 | 4 of 4 |
  > | 2019 | 6 of 6 |
  > | 2020 | 8 of 8 |
  > | 2021 | 16 of 16 |
  > | 2022 | 15 of 15 |
  >
  > **2017 is absent entirely**, and 2013 to 2016 are almost entirely blank.
  > So the true position is: **a discrete party polling series for 2018 to 2022,
  > monthly, plus nothing useful before 2018 and nothing after 2022** (the
  > 2022-2025 monthly table is the combined-column one). That is five years of
  > real discrete polling, not zero, and it is the axis the original thesis
  > actually needs.
  > Still unknown and still disqualifying: **no margin of error, no sample
  > size, no publication date.** So the series cannot carry a band. It CAN carry
  > polling-against-result over 2018-2022 with an honest "no published margin"
  > marker, which is what non-negotiable 5 as amended now requires.
  > **Next: extend the ingest to read that table, verify the 2017 gap is real
  > and not a parsing artefact, and confirm the 2018-2022 figures against the
  > release text for a sample of waves before any of it is plotted.**
  > Next: register the dataset in `docs/data-sources.md` and decide the chart
  > form before building anything on top of it.
- **0005 — Right of reply** — send the draft thesis and named claims.
  > Blocking publication, not blocking development. Send before the copy is
  > final, so a substantive response can shape the framing.
  > Depends on: 0001.
- **0007 — Chart one: polling against result** — **DESIGN AND SPEC APPROVED
  2026-10-04. IMPLEMENTATION PLAN WRITTEN.**
  > Spec: `docs/superpowers/specs/2026-10-04-chart-01-polling-vs-result-design.md`
  > Plan: `docs/superpowers/plans/2026-10-04-chart-01-polling-vs-result-plan.md`
  > Eight tasks, ordered 1 to 8. **Note:** the `writing-plans` skill the
  > brainstorming skill names is not installed on this machine, so the plan was
  > written by hand against the spec rather than by that skill.
  > **Two facts found while writing the plan against the live page, both of
  > which the earlier note had wrong.** There are **two** election rows in the
  > 2013-2022 discrete table, not one — the 2016 and 2019 federal elections —
  > and the 2019 one sits *inside* the 2019 year group. So the exclusion rule has
  > to match `\bElection\b` rather than counting rows, and 2019 yields **5 poll
  > waves**, which is why the window is 5 and not 6. Also confirmed: **2017 is
  > genuinely absent** from the table, not a parsing artefact — zero occurrences
  > of the string anywhere in it. That was the one finding that could have
  > invalidated the series range, so it was checked before anything was built.
  >
  > **Expect CI to go red at plan Task 6 and stay red until task 0003 delivers
  > AEC figures.** That is the gate working, not a broken build, and the
  > assertion must not be loosened to make it green.
  > **The spine is polling-against-result, 2018 to 2022.** 48 fortnightly waves
  > with a discrete One Nation figure against two election results. Mean of the
  > preceding waves: 3.70% for 2019 (result 3.1, gap **+0.60pp**), 3.71% for 2022
  > (result 5.0, gap **−1.29pp**). **Polling was wrong in both directions**, which
  > is the "open test, not verdict" thesis actually working — a chart drawn
  > before looking at the data would likely have implied consistent overshoot.
  > Form: spine chart of poll-minus-result from a zero rule, with the evidence
  > beneath it as a per-election vertical span of the preceding range, not a line
  > across 48 waves (a line would assert values between fortnightly snapshots
  > that nobody measured). **Refined after approval:** the spans moved from a
  > separate figure to a second panel within the spine, so claim and evidence
  > read together and the page resolves to two charts.
  > **Chart 02 (seat efficiency) added at Dale's direction** and specced in the
  > same document: national primary vote against seat share, both as a share of
  > the 151-seat House, gap shaded. That is editorial Chart 04 moved earlier
  > because the data exists now. **Provisional — Dale decides after seeing it
  > rendered.** Shares no data or code with Chart 01 beyond `stats.py`, so
  > cutting it later costs nothing.
  > **Two corrections found by recomputing from source during spec review.**
  > The wave count is **48, not 49** — the table yields 49 rows with a discrete
  > figure but one is the 2019 election *result*, not a poll. And the 2019 window
  > is **5 waves, not 12**, because only five polls precede that election. Both
  > were wrong in the first draft and caught by recomputing rather than trusting
  > the earlier figure. Neither is smoothed over: each mean is labelled with the
  > wave count it actually used.
  > **The gate:** nothing ships until task 0003 confirms the 2019 and 2022
  > results against AEC. Dale, 2026-10-04: "Nothing is shipping to prod yet...
  > but we need to build the chart with what we have now, and we will update it
  > when we get the better information." So the chart is built now behind a
  > machine-checked gate that fails the build rather than being bypassed, and
  > AEC figures drop in with no chart code change.
  > Depends on: 0001, 0003, 0004.
  > **The build blocker is cleared.** It was previously "blocked on a build
  > assertion, not on data": `charts/chart_01.py` held unsourced placeholder
  > values and passed every check, so nothing stopped an unsourced chart from
  > shipping. Both halves are now implemented and tested — the sourced-data
  > assertion and the zero-width band assertion (BACKLOG: citation resolver).
  > **0007 is now blocked on data only:** tasks 0003 and 0004 must supply the
  > polling series and the AEC results.
  > **STATUS 2026-10-18: BUILT, AND THE GATE IS CLEAR.**
  > Both charts are built on branch `charts-01-polling-vs-result`. The captions
  > state computed figures, not typed ones, and the build assertions refuse an
  > unsourced or mismatched figure — each one proven to fire by mutating a
  > single input in a scratch copy.
  > **Correction 2026-10-06: the paragraph below claiming four defects were
  > fixed and verified was true of the sources and false of the page.** The
  > committed `index.html` still carried three of them, because the gate refused
  > to write while red, so the artefact could not be regenerated at all. Fixed
  > by `--draft`, and asserted by `test_committed_artefact_matches_a_fresh_build`.
  > **`tools/build.py --check` exits 0 since 2026-10-18.** Task 0003 closed by
  > moving Chart 01's result axis onto the AEC series, so the chart now cites a
  > source of record beside the cross-checked poll series and the gate passes on
  > its own terms. `roymorgan-pvi` is still `cross_check_only: yes`, and a test
  > asserts both halves: that the real check is green, and that the gate still
  > refuses a chart citing only the cross-check. Publication still needs 0005,
  > the right of reply, which is an editorial action and not a build one.
  > **The figures moved when the axis did.** Against the AEC's record polling ran
  > 0.62 points high in 2019 and 1.25 points low in 2022, where against Roy
  > Morgan's cross-check of the count it read 0.60 and 1.29. The difference is
  > the cross-check's rounding and never exceeds 0.04 points.
  > **Chart 02 (seat efficiency) was never behind that gate.** Its figures come
  > from the AEC's own per-election files. It is still awaiting Dale's
  > keep-or-cut decision.
  >
  > **Task 0008 VERIFIED 2026-10-05.** Measured in a browser at 320, 640 and
  > 1280px. Four defects found, all by measuring rather than reading, and none
  > of them visible in the source:
  > 1. **At 640px the wide variant rendered 8.61px labels** — the worst of any
  >    width, and under the DESIGN.md floor of 16px. The breakpoint showed the
  >    wide copy in a 577px track when it is drawn for 1072. Raised to 1100px,
  >    so narrow serves 320 and 640 (10.10px and 21.98px) and wide only at
  >    1280 (16.0px, exactly the floor).
  > 2. **`--band-hatch` was never declared.** DESIGN.md specifies it as
  >    `url(#hatch-mo)` and nine Chart 02 polygons used it, but no rule defined
  >    it, so it resolved to an empty value and the shaded region between the
  >    two series painted nothing. Not an error: the SVG renders, the attribute
  >    is present, and an absent fill is simply no paint.
  > 3. **The narrow variant referenced the wide chart's pattern id.** Its own
  >    pattern is `#hatch-mo-narrow`, so `#hatch-mo` resolved against an id not
  >    in its SVG — again invisible, and at the width most readers see.
  > 4. **`aria-labelledby` was only rewritten for its first token.** With
  >    `aria-labelledby="chart-01-title chart-01-desc"`, the title was suffixed
  >    and the desc was not, so each narrow chart pointed at the **wide** chart's
  >    description while its own went unreferenced. Every id resolves, because
  >    the wide desc genuinely exists; only a screen reader announces it.
  >
  > Reduced motion honoured: zero animations and zero transitions under
  > `prefers-reduced-motion: reduce`. No JS dependency: `main` is fully opaque
  > with 3,134 characters and nothing is left hidden. Both charts keep two
  > variants in the accessibility tree at every width.
  >
  > Confirmed the by-election reads as an annotation: its text sits at y=81-122,
  > entirely above the series range of y=223-440, and the chart carries exactly
  > 18 markers for 9 elections — no tenth point.
  > Depends on: 0001, 0003, 0004.
- **0008 — Responsive chart contract** — MOSTLY RESOLVED by 0006, remainder
  is chart-specific.
  > **Resolved and now house rules**, each measured in a browser:
  >
  > - **viewBox must equal the rendered track width**, not the nominal one.
  >   The 1120px track renders 1072 (24px padding each side), so a 1120 viewBox
  >   gave 15.3px labels, under the 16px floor. viewBox is now 1072 and labels
  >   measure exactly 16px.
  > - **Two variants per chart, from one generator.** A single 1072px chart
  >   scaled into a 280px phone column renders 16px labels at about 4px. So each
  >   generator emits `chart-NN.svg` and `chart-NN-narrow.svg`. Confirmed by
  >   Dale on 2026-10-04 in preference to horizontal scrolling or relying on the
  >   data table.
  > - **Both variants ship in the DOM as siblings**, CSS-switched at 1100px
  >   (raised from 640px on 2026-10-05 — see the label-floor finding under
  >   0007), so a screen reader always finds a chart. Not `<picture>`: verified
  >   that it does not media-switch two inline `<svg>` elements. Narrow ids are
  >   suffixed and its `url(#...)` references rewritten, or both charts would
  >   claim the same `id` and the narrow `aria-labelledby` would resolve to the
  >   wide chart's title. **Only the `id` attribute is suffixed, never
  >   `data-source-id`**, which is provenance and not an element id; suffixing it
  >   produced an unresolvable citation and froze the artefact.
  > - **Charts are siblings of `.col-prose`, never children.** A nested figure
  >   is trapped in columns 2 to 8 and can never reach the breakout track.
  > - **`<figure>` needs `width: 100%`**, or it is sized by its SVG and
  >    collapses to the 300x150 replaced-element default.
  >
  > **Still open, and genuinely chart-specific:**
  > - Direct-label collision at 280px. Only the y-axis thinning (every 2nd tick)
  >   and x-axis thinning are implemented; a real chart with 8 election labels
  >   and an annotation will need its own collision rules. Measure on 0007.
  > - Whether an annotation's leader line still routes at narrow width.
  > - **Print stylesheet. Implemented by 0006, hatch closed 2026-10-04,
  >   never physically tested.**
  >   The `@media print` block at `src/margin-of-error.css:373-446` covers
  >   every rule `DESIGN.md:209-216` specifies: white paper, 11pt body,
  >   `print-color-adjust: exact`, full source URLs appended to
  >   `.source-note a[href^="http"]`, `break-inside: avoid` on figures,
  >   `break-after: avoid` on headings, and `@page size: A4 portrait`.
  >   The hatch density gap is now closed: both densities are emitted and the
  >   print block swaps to the coarser one, because a media query cannot change
  >   a `<pattern>`'s geometry. The build now also refuses a dangling
  >   `url(#...)` from the stylesheet, since a typo there drops the band to no
  >   fill on paper and no test on screen would catch it.
  >   **Outstanding: a physical A4 print check — ON HOLD by decision,
  >   2026-10-04.** Deliberately not scheduled. Needs a printer and a page that
  >   is not yet publishable. The code is correct by construction: both
  >   densities emitted, build refuses a dangling reference, 5 tests cover it.
  >   Recorded as code-complete and untested, not as done. Deferred is not the
  >   same as verified.
  >
  > Depends on: 0002 (satisfied), 0006 (satisfied), 0007 for the remainder.

---

## BLOCKED

- **Seat-count contradiction** — **RESOLVED 2026-10-03.** Prototype claimed 2
  lower house seats, the feasibility report claimed 0. Both wrong. Correct
  figure is 1, won at the Farrer by-election, 25 May 2026, by David Farley
  (One Nation), 57.55% TCP, margin 15,302. Verified against AEC final results.
  Evidence in `docs/data-sources.md` under `aec-hor-2025-party-rep` and
  `aec-by-farrer-2026`. Both prior figures deleted from the prototype.
  > Follow-on: the 2026 Farrer win converted 39.53% primary to 57.55% two-party
  > preferred. Primary vote alone does not predict seat outcomes for this
  > party, which limits a primary-only comparison and needs to be handled in
  > the chart specs.

- **Right of reply: how to reach the party** — **AEC search done 2026-10-04,
  address is not published. Now an editorial decision, not a research task.**
  > The AEC was searched directly and the registered address is **not
  > available** in any published form. `Party Returns.csv`, unpacked from the
  > bulk `All-Annual-Data.zip`, carries financial columns and no address.
  > Full URL-by-URL record in `docs/right-of-reply.md`.
  > Three options, none of which should be chosen unilaterally:
  > 1. **Write to the party's own published contact channel.** Fastest, and it
  >    is the party's own published point rather than an address lifted from a
  >    news report, which `TASKS.md` forbids. Leaves a gap against
  >    non-negotiable 3, which asks for the **registered** address.
  > 2. **Ask the AEC's party registration team** how a member of the public may
  >    obtain a registered party's address. Short, specific, statutory hook.
  >    Satisfies the standard as written.
  > 3. **FOI request** for the registration statement. Slow, and the address is
  >    the only thing needed.
  > **Recommendation: 1 and 2 together.** Option 1 starts the clock now, option 2
  > closes the gap in the standard. The clock under s 17 of the *Broadcasting
  >    Services Act 1992* only starts when the claim is put to the party, so
  >    delay is the real cost here, not the choice of channel.
  > **This is the top publication blocker and needs Dale's decision.**
- **Domain registration** — `marginoferror.com.au` appeared unregistered at
  > 2026-10-03 WHOIS check but is not held. Until it is purchased it is
  > available to anyone, including a hostile party. Treat as highest risk.
  > **RESOLVED 2026-10-04: domain purchased by Dale.** The hijack risk that
  > made this the highest-risk open item is closed. Two things remain and
  > neither is urgent: confirm the renewal is set to auto-renew, and note that
  > the domain being held does not yet make the page publishable — the right of
  > reply is still outstanding.

---

## BACKLOG

- **Corrections policy page** — `docs/corrections.md` exists as an internal
  register; it needs a public-facing version and a route for readers to report
  an error.
- **Delete the orphaned prototype files `.css` and `.js`** — **DONE 2026-10-04.**
  Both removed. Verified unreferenced first: neither file appears in any HTML,
  CSS or Python file, and the real stylesheet declares only Newsreader, IBM Plex
  Sans and IBM Plex Mono, none of the three Google families `.css` pulled
  (Fraunces, Inter, JetBrains Mono). `.js` held a Chart.js bar chart keyed on
  `#journalismSwingsChart` and an interactive poll widget, both rejected in 0001.
  Neither file was tracked by git, so the deletion was unrecoverable and was
  gated on that check. `python3 tools/build.py --check` still passes.
- **Salvageable seat primaries from the archived model** — the prototype's
  `CORE_TARGET_SEATS` carries real 2022 AEC division primary votes (Flynn 12.0,
  Capricornia 14.6, Maranoa 11.8, Wright 12.1, Hunter 9.8, Paterson 7.9,
  Durack 9.6, Hinkler 8.7). **Measurements, not forecasts**, and the input
  Chart 02 and Chart 04 need. Verify every division against AEC before any use;
  the archived banner records why the rest of that file cannot be cited.
- **Seat boundary handling** — AEC redistributions change seat names and
  boundaries. A helper that resolves a historical seat to its current
  equivalent is needed before any cross-cycle seat comparison chart ships.
- **Small multiples by state** — one small multiple per state beats a
  multi-line spaghetti chart, and Queensland is the story. Prioritise QLD, NSW,
  VIC, WA.
- **Vote efficiency calculator** — the metric that explains how a low-single-digit
  primary vote becomes seats. Needs the seat-level vote conversion data.
- **Print hatch density** — **CODE DONE 2026-10-04. Verification ON HOLD.**
  The last unimplemented line of the print spec. A media query cannot change a
  `<pattern>`'s geometry, so the generator now emits both densities and the
  print block swaps the fill: the same two-variants-one-generator contract the
  charts already use for wide/narrow. Screen 4px/1.0 stroke, print 6px/1.6, and
  the band edge goes solid rather than dashed because on paper the boundary
  carries the meaning.
  **ON HOLD, 2026-10-04, by Dale's decision.** The remaining step is a physical
  A4 print check and it is deliberately not scheduled: it is manual, it needs a
  printer and a page that is not yet publishable, and the code is correct by
  construction — both densities are emitted, the build refuses a dangling
  reference, and 5 tests cover the contract. Nothing is lost by deferring.
  Recorded as code-complete and untested, never as done.
- **`forced-colors` mode** — specified at `DESIGN.md:202` (hatch texture and
  `--color-rule` must survive) and **implemented nowhere**: there is no
  `forced-colors` media query in any stylesheet. Distinct from reduced motion,
  which 0006 did implement (`src/margin-of-error.css:362`).
- **Citation resolver** — **DONE 2026-10-04.** `tools/build.py` now carries the
  check. Five assertions, each verified to fail on the input it exists to catch:
  - a chart declaring neither `data-source-id` nor `data-unsourced="true"` is
    refused — the case that matters, a chart that looks finished and cites nothing
  - a `data-source-id` with no entry in `docs/data-sources.md` is refused
  - a chart claiming both sourced and unsourced is refused
  - a `data-unsourced="true"` chart absent from the registry is refused, so
    unsourced figures stay auditable rather than a private note in a Python file
  - **a band polygon whose points share one x is refused** — the task 0002
    defect, now asserted on the committed SVG rather than trusting anyone
    remembered to run the generator. A published margin rendering invisibly is
    the worst bug class this site has, and it does not throw.
  Plus a sixth, found while implementing: **placeholder prose in the template**.
  The chart checks could not see it, so `index.html` was shipping a visible
  "PLACEHOLDER SOURCE NOTE" in the figure caption while passing every other
  rule. Provenance is declared on the `<svg>` root, so it stays greppable
  without a manifest to drift out of sync. 9 regression tests cover these; the
  suite was 30 then and is 161 at 2026-10-06.
- **Mobile layout verification** — **DONE 2026-10-05/06.** Measured at 320, 480,
  640, 900, 1100, 1280 and 1600px: zero label overlaps, nothing outside the
  viewBox, all nine bands resolving in every variant, and no horizontal overflow
  at any width. This is what raised the chart breakpoint from 640px to 1100px —
  the wide variant rendered 8.61px labels at 640px, under the DESIGN.md floor of
  16px. The `680px` in the original note was a guess at the grid breakpoint; the
  chart switch is what actually mattered and it is now measured. The draft banner
  was separately checked at 320 and 1280 (no overflow, text constrained to the
  66ch measure).
- **Accessibility audit** — axe or equivalent, plus manual keyboard traversal.
  The build enforces the floor mechanically (`lang="en-AU"`, one `h1`, one
  `main`, `role="img"`/`<title>`/`<desc>` on every chart, no unfilled
  placeholder, no raw hex), but no third-party audit and no keyboard pass has
  been run.
- **CI** — **WRITTEN, NEVER RAN, AND TWO STEPS COULD NOT FIRE.**
  `.github/workflows/ci.yml` runs on push to and pull request against `main`:
  the geometry and guard-rail tests, then `build.py --check`. No `pip install`,
  so the guard on the page's accuracy has no supply chain to go stale. Python
  pinned to 3.13 (the generators use PEP 604 unions, so 3.10 is the floor).
  **Correction 2026-10-06.** The entry previously read "DONE" and claimed the
  drift check "was verified to fail on both a hand-edited artefact and a stale
  template." Neither claim survived checking:
  1. **CI has never executed once.** The workflow is not on `origin/main`, and
     the branch carrying it has never been pushed — 18 commits on `main` and 10
     on `charts-01-polling-vs-result` are unpushed. A workflow that has never
     run cannot have verified anything.
  2. **The drift step was unreachable.** Steps run sequentially under `set -e`,
     and `--check` fails by design while task 0003 is open. With `--check`
     first, every later step was skipped on every run that could ever have
     happened. The 144 (now 161) tests were in the same position.
  3. **`--check` never checked drift.** It validated the freshly built string and
     compared it to nothing. The drift comparison existed only in the YAML.
  **Fixed 2026-10-06.** Drift is now measured inside `validate()` via
  `drift_problems()`, so no step ordering can hide it, and the tests run before
  `--check` so a known-red gate does not cost the test signal. Both were proven
  to fire by mutating a hand-edited artefact in a scratch copy.
  **Still to do:** push the branch and open the PR, which is the only way CI runs
  for the first time. Until then this entry describes a pipeline that has never
  executed.
- **Performance budget** — target LCP under 2.0s on a 4G connection. Fonts
  self-hosted, subset to the Latin subset used. **Budget raised to 400KB
  critical path, 2026-10-03.**
  **Resolved by decision, not by measurement.** The original "sub-200KB" was
  never reachable with the three faces `DESIGN.md` specifies: the latin
  subset is 177KB, or 191KB with IBM Plex Mono 500. The budget was the thing
  that was wrong, so it was raised rather than the design compromised.
  **400KB** carries the faces at 191KB plus markup, CSS and the 0.4KB of
  motion with roughly 2x headroom, and leaves room for the Newsreader
  optical-size cut if it is ever wanted (opsz roman 128KB against wght 56KB;
  opsz italic 143KB against wght 63KB).
  **This resolves the font fork in favour of the design.** With 400KB the
  `opsz` cut is affordable, and it is the correct file for a broadsheet at
  large sizes, because the optical axis is what makes the face read as a
  newspaper rather than a blog. Cost is 271KB for the display face alone
  against 119KB for `wght`. Task 0006 vendors whichever is confirmed.
  Still open, and *not* settled by raising the number: **LCP under 2.0s on
  4G.** 400KB of fonts on a 4G connection is slow. Fonts must not block
  render, so 0006 specifies `font-display: swap` plus `preload` for the roman
  faces only. That is a loading strategy, not a size reduction, and it is
  the part that actually protects LCP.

---

## Events

Append-only. Newest last.

- 2026-10-03 — Project created. Name chosen over `Swingometer`, `First
  Preference`, `Hanson Ledger` and four other directions. WHOIS check found
  `marginoferror.com.au` and `themarginoferror.com.au` unregistered;
  `firstpreference.com.au` and `margincall.com.au` taken. Scaffold created:
  `AGENTS.md`, `DESIGN.md`, `TASKS.md`, `_tasks/`, `docs/`. Design thesis
  fixed: subject in `--color-ink`, context in `--color-ink-muted`, no party
  brand colour used, teal/red diverging pair chosen over green/red for
  colour-vision safety.
- 2026-10-03 — Flagged three correctness traps in `AGENTS.md` gotchas: the
  preference flow change from 2022, silent row loss when matching historical
  series on the modern party name, and denominator switches between primary and
  primary-plus-preferences.
- 2026-10-03 — Thesis decision. Task 0001 closed on the question: does polling
  overstate or understate the party's vote relative to its actual result, and
  does the published margin of error explain the gap. Scope is House of
  Representatives primary vote, federal elections since 1996, pollster
  published tables only. Senate, party capability and volunteer coverage
  explicitly excluded as unverifiable or non-comparable.
- 2026-10-03 — Feasibility angle rejected as the thesis. The argument that a
  One Nation majority is "statistically and structurally impossible" is a
  forecast, not a measurement, so it fails the yes-or-no test in task 0001.
  `docs/reference/political-feasibility-report` retained as an archived
  discarded direction, not cited.
- 2026-10-03 — Prototype `.css` and `.js` confirmed orphaned. `index.html`
  links neither; it loads Tailwind and Chart.js from CDN. Prototype also
  contains a fabricated reader poll ("1,482 verified responses", fixed
  64.2/24.5/9.1/2.2 split, hard-coded and unchanged by voting) and a chart
  mixing two-party swing, wartime swing, federal swing, a 1998 state peak and a
  required percentage-point surge on one axis. None of the prototype's figures
  reach `docs/data-sources.md`. Prototype retained as a prose draft only.
- 2026-10-03 — Seat count verified against AEC primary source, resolving the
  contradiction between the prototype and the feasibility report. **Both were
  wrong. The party holds 1 lower house seat**, won by David Farley (One Nation)
  at the Farrer by-election, 25 May 2026, 58,294 TCP votes (57.55%), margin
  15,302. The 2025 general election party representation summary lists no One
  Nation seats (ALP 94, Coalition 43, Greens 1, Centre Alliance 1, KAP 1,
  Independent 10). All 24 federal House by-elections in the AEC archive from
  2005 were swept: One Nation candidates stood in Cook and Dunkley 2024,
  Fadden and Aston 2023 and Farrer 2026, and won only Farrer. There is no
  Newcastle by-election in the AEC archive, so the second seat being recalled
  does not correspond to any AEC by-election record. The correct figure is 1
  and both prior figures are deleted.
- 2026-10-03 — Preference-flow finding logged. Farley converted 39.53% primary
  to 57.55% TCP, a gain of 18.02 percentage points. This is direct evidence
  that primary vote alone does not predict seat outcomes for this party, and it
  cuts against the prototype's framing. Needs confirmation at scale before it
  can be published as a finding.
- 2026-10-03 — **Thesis revised** after the 0004 sourcing assessment. Second
  clause changed from "does the published margin of error explain the gap" to
  "can a reader even tell how precise those polls were?", because the largest
  house in the series publishes no margin, no sample size and no publication
  date. Editorial decision: the absence is part of the finding. Non-negotiable
  5 amended to require a visible "no published margin" marker rather than
  allowing a bandless point estimate, and imputing a margin from an assumed n
  is now prohibited outright. Three consequences worth noting. First, the
  project name now reads two ways, the polling gap and the unpublished margin,
  and both are supported by evidence. Second, this is more defensible than the
  original framing: an imputed band would be a fabricated number in the visual
  language of honesty, on a site whose entire premise is not doing that.
  Third, the finding is now partly about the polling industry's disclosure
  practice rather than only about this one party, which is a scope widening
  that has not been separately approved.
- 2026-10-04 — **Framing reversed. The page is no longer about pollsters.** The
  2026-10-03 decision made the absence of a published margin the finding itself,
  which made the page partly a piece about the polling industry's disclosure
  practice. Rejected as a different subject with a different set of people in
  it, and because it invited the obvious rebuttal that plenty of pollsters do
  publish these figures, leaving the page running a weaker version of an
  argument a critic could have run better. Thesis second clause is now "how
  much weight can that comparison carry?", a statement about the evidence rather
  than about any publisher. The missing margin is carried as a stated limit in
  the page's own voice, in Chart 01's caption. Chart 05 (Disclosure, as a
  finding) is withdrawn and retained in `docs/chart-specs.md` under "Charts
  considered and rejected" reasoning so it is not re-litigated. New gotcha in
  `AGENTS.md`: "Do not write about pollsters." The prohibition on imputing a
  margin from an assumed n is unaffected and stands.
- 2026-10-03 — Denominator switch confirmed present in Roy Morgan's own data.
  The monthly PVI table reports One Nation inside a combined "Other Parties
  (ALL)" column with no discrete One Nation column, while the election results
  table on the same page does have one. For the April 27 2025 wave the
  combined figure is 18.5% against One Nation at 7.5%. Reading the combined
  column as the party would overstate it by more than double. Any ingest script
  must select columns by header name and fail loudly on an unmapped column,
  never by fixed offset.
- 2026-10-03 — Preliminary election-result series assembled from Roy Morgan's
  "Recent Election Results" table as a cross-check only, pending AEC
  verification: 1996 0.3%, 2001 4.3%, 2007 0.3%, 2013 0.2%, 2019 3.1%,
  2022 5.0%, 2025 6.4%. The 2007 and 2013 values are far below the 12.3% quota
  and cannot be assumed to represent the same slate as 2025. Not publishable
  until each row is verified against AEC with registered name and fielded
  candidate count recorded.
- 2026-10-03 — Framing decision. The page tests the polling-overstates
  hypothesis rather than asserting it. The thesis is a question the reader can
  answer by checking the series, and the page publishes whichever way the data
  falls, including showing polling was accurate. Reason recorded in
  `_tasks/0001-editorial-thesis.md`: a flat claim can be dismissed by
  producing one contrary poll, which is cheap to do, whereas an open test can
  be re-run by the reader. The credibility of the series is the product, so the
  series has to survive contact with a hostile reader.
- 2026-10-03 — Live AEC archive located: `results.aec.gov.au`, one directory per
  election event with an event id (31496 for 2025, 27966 for 2022, 31633 for the
  Farrer by-election). Note that `aec.gov.au` returns HTTP 200 with a 404 body
  for retired URL patterns, so status codes cannot be used to validate a fetch.
  Validate on page title or body text instead.
- 2026-10-03 — Chart stack researched and proposed (task 0002), not locked.
  Measured real payloads rather than trusting package metadata: Plot 0.6.17
  depends on all of d3 and bundles to 91KB gzip, against 9KB gzip for the
  `d3-scale`/`d3-shape`/`d3-array` subset the page actually needs, and 58KB
  gzip for tree-shaken Chart.js 4. The three-vs-five rule in `TASKS.md`
  resolves to hand-built SVG now that `chart-specs.md` lists four distinct
  bespoke forms. Chart.js is independently disqualified because it renders to
  `<canvas>`, which cannot carry the `role="img"` title and description that
  `DESIGN.md` requires. Observable Plot is not buying the hard part either way:
  the hatch-textured uncertainty band is an SVG `<pattern>` no library ships.
  Recommendation awaits sign-off per `AGENTS.md` editorial control.
- 2026-10-03 — **Superseding the entry above, same day.** Four options were
  costed in full, including two the first pass had dismissed, and the
  recommendation changed to **build-time SVG generation in Python, stdlib
  only**. The original finding about payload was right and stands. The error
  was treating "no client-side JS" as automatically preferable and not weighing
  the Python mandate in `docs/standards.md`: a hand-inlined chart path in
  `index.html` is a transformation done by hand, which that standard forbids,
  and it leaves the page's most load-bearing number as the one artefact with no
  code path from raw data. On the original metric too, Python wins outright at
  0KB client JS against 9KB for the d3 subset. Proof-of-concept: 68 lines of
  stdlib Python emitted a 1,919 byte chart (704 bytes gzipped) carrying
  `role="img"`, `<title>`, `<desc>`, the native hatch `<pattern>` and zero raw
  hex, verified in a real browser rather than asserted.
- 2026-10-03 — **Defect found in the null-margin band logic, before any chart
  ships.** Where a poll with no published margin splits a run, an isolated
  banded poll beside it renders as a zero-width polygon, so **a margin that was
  published becomes invisible**. That is precisely the false claim
  `DESIGN.md`'s "Where there is no band" rule exists to prevent, so it is the
  worst defect class this site has. Fix: a single-poll band segment renders as
  a vertical whisker with a cap, never as a polygon, since a polygon needs two
  distinct x values to have any width. Task 0007 needs an assertion that no
  band element has zero width. Same proof run also hit inverted axes from
  padding unpacked in the wrong order, caught by asserting on rendered
  `getBBox()` rather than by reading the code. Geometry needs tests.
- 2026-10-03 — Performance budget found to be wrong at source. The latin subset
  of the three faces `DESIGN.md` specifies is 177KB, so "sub-200KB critical
  path" was never reachable including a chart runtime. Fonts, not the chart
  library, are the budget. Logged against the BACKLOG performance item rather
  than silently rewriting the target.
- 2026-10-03 — **Task 0002 locked and signed off by Dale.** Chart stack is
  build-time SVG generation in Python, stdlib only: no charting library, no
  client-side JavaScript for charts, no bundler, no framework. Generated SVG is
  **inlined into `index.html` by the build** rather than referenced as a
  separate `.svg` via `<img>`, so `var(--token)` fills inherit from the page
  stylesheet and a token change re-skins every chart without regenerating. The
  accepted cost is that `index.html` becomes a generated artefact, so task 0006
  must establish a hand-written template with `<!-- chart:NN -->` placeholders
  before any chart is written, otherwise the rationale for the decision fails.
  Motion is `IntersectionObserver` plus CSS with no library, 0.4KB against
  animejs at 16KB, and GSAP is excluded on licensing because its npm licence is
  not an OSI open-source grant. Consequence worth restating: fonts are now the
  entire JS-adjacent payload, since chart client JS is zero.
- 2026-10-04 — **Performance budget raised from 200KB to 400KB by decision.**
  The sub-200KB target was never reachable with the three specified faces
  (177KB latin subset, 191KB with Plex Mono 500), so the number was the thing
  that was wrong rather than the typography. Raising it resolves the recorded
  font fork in favour of the design: the Newsreader `opsz` cut becomes
  affordable, and it is the correct file for a broadsheet display face because
  the optical axis is what makes it read as a newspaper. Display face cost
  becomes 271KB (opsz roman + italic) against 119KB (wght). The raise does
  **not** settle LCP: 400KB of fonts on 4G is slow, so task 0006 must ship
  `font-display: swap` with `preload` on the roman faces only. A loading
  strategy protects LCP; a byte cap alone does not.
- 2026-10-04 — **Task 0006 complete: the page shell, built and measured.** The
  template/output separation task 0002 depended on is established and held:
  `src/index.template.html` is hand-written prose, `index.html` is generated,
  and charts inject at `<!-- chart:NN -->`. Build is `tools/build.py` (stdlib,
  with `--check` for CI); it validates the accessibility floor, one-`h1`,
  `lang="en-AU"`, unfilled placeholders and raw hex in chart fills. 21 geometry
  tests pass.
- 2026-10-04 — **Four layout defects found by measuring the rendered page,
  none of which were visible by reading the CSS.** Recording because each would
  have shipped a broken page:
  1. A `<figure>` is sized by its content, and an `<svg>` carrying only a
     `viewBox` with no width attribute is a replaced element falling back to
     the 300x150 default. The figure collapsed to 185px inside a 285px column.
     Fixed with `width: 100%` on the figure.
  2. `margin-block` on `figure` left the browser default 40px inline margins,
     overflowing the page by 20px at a 320px viewport. Fixed with a full
     `margin` reset.
  3. A figure nested inside `.col-prose` is trapped in columns 2 to 8 and can
     never reach the 1120px breakout track. Measured 520px wide at a 1280px
     viewport, labels at 7.4px. Charts are now siblings of the prose section.
  4. The wide viewBox was 1120 while the track actually renders 1072, so 16px
     axis labels came out at 15.3px, under the `DESIGN.md` floor. viewBox is
     now 1072 and labels measure exactly 16px.
- 2026-10-04 — **Mobile chart strategy decided by Dale: a second, narrower
  chart from the same Python generator.** A single 1072px chart scaled into a
  280px phone column renders 16px labels at roughly 4px, which is unreadable.
  Chosen over horizontal scrolling and over leaning on the data table. Each
  generator now emits `chart-NN.svg` and `chart-NN-narrow.svg` (420px
  viewBox, labels measuring 10.7px at 320px viewport). Both ship in the DOM as
  siblings, CSS-switched at 640px, so assistive tech always finds a chart.
  Three corrections were needed to get this right and all three were caught by
  inspecting output rather than assuming: `<picture>` does NOT media-switch two
  inline `<svg>` elements; a wrapper `<svg>` around the narrow variant produced
  invalid nesting with no viewBox on the outer element; and duplicate `id`
  attributes across the two variants meant the narrow chart's
  `aria-labelledby` resolved to the wide chart's title while both claimed the
  same `hatch-mo` pattern id. The build now suffixes narrow IDs and rewrites
  their internal `url(#...)` references.
- 2026-10-04 — **Fonts vendored: five latin files, 356KB, all OFL-1.1,
  registered in `docs/data-sources.md`.** Newsreader `opsz` roman + italic
  (271KB) chosen over the lighter `wght` cut (119KB), affordable only because
  the budget was raised. Verified with fontTools that the opsz cut carries both
  `wght 200-800` and `opsz 6-72`, so it **supersedes** the wght file rather than
  joining it, and only one Newsreader file ships. IBM Plex Mono has no variable
  build, hence two static cuts. Latin subset only, no latin-ext. Confirmed in
  the network panel that all five fetch exactly once, so the preloads are
  matched: `crossorigin` on the preload links is load-bearing, because a woff2
  `@font-face` request is made in CORS-anonymous mode and a preload without it
  would be discarded and the font re-fetched.
- 2026-10-04 — **Known gap recorded, deliberately not papered over:** the build
  enforces the accessibility floor, one-`h1` and the token rule, but it cannot
  yet tell a sourced chart from a placeholder one. `charts/chart_01.py` holds
  unsourced prototype values and passes every check. A sourced-data assertion
  must land before task 0007 ships.
- 2026-10-04 — **TASKS.md reconciled against the code base; six stale claims
  corrected.** Verified by running `tools/build.py --check` (passes) and
  `python3 -m unittest discover -s tests` (21 passing, stdlib `unittest` — there
  is no `pytest` dependency, so the "21 tests passing" note should be read as
  `unittest`, not `pytest`), and by regenerating `index.html` in memory to
  confirm it byte-matches the committed file. What had drifted:
  1. **Print stylesheet is implemented, not absent.** Both the 0008 entry and a
     BACKLOG item said `DESIGN.md` specifies it and nothing implements it. The
     `@media print` block is at `src/margin-of-error.css:375-420` and covers
     white paper, 11pt, `print-color-adjust: exact`, full source URLs in
     `.source-note a[href^="http"]`, `break-inside: avoid` on figures,
     `break-after: avoid` on headings and `@page size: A4 portrait`. Only one
     line of the spec is genuinely missing: `DESIGN.md:212` asks for the **hatch
     density** to be expanded, and the block only preserves the existing density.
     Still unverified on real A4 paper, which is why the item survives, narrowed.
  2. **`forced-colors` was lumped in with reduced motion as "specified, not
     built", which is half wrong.** Reduced motion *is* implemented
     (`src/margin-of-error.css:362`); `forced-colors` appears in **no**
     stylesheet at all, though `DESIGN.md:202` requires it. Split into two items
     so the real gap is visible.
  3. **`index.html` is no longer an orphan.** The 0001 entry still described it
     as a prototype artefact of the rejected direction. It is now generated
     output of the 0006 build; prose was hand-rewritten into
     `src/index.template.html` and nothing of the prototype's figures survived.
     Corrected in place, since it is a status field, not a log entry.
  4. **`.css` and `.js` are still orphans**, untracked and referenced by nothing.
     Logged in BACKLOG for deletion. They are the last trace of the rejected
     feasibility direction and `.css` pulls Fraunces, Inter and JetBrains Mono,
     none of which the page uses.
  5. **`src/margin-of-error.css` was described as "tokens only"** in the 0006
     entry. It is 420 lines carrying tokens, reset, grid, typography, figures,
     focus, motion and print. The 0006 entry's own list of what it contains was
     accurate; the parenthetical was not.
  6. **Font total corrected to 345.9KB** (354,180 bytes across the five woff2
     files), not the 356KB recorded in both the 0006 entry and the Events log.
     The Events entry is append-only and was left as written; the NOW section,
     which is a live status field, carries the corrected figure.
  Also fixed a formatting defect in the Events log: the 0006 entry and the
  performance-budget entry had been concatenated onto one line
  (`...does not.- 2026-10-04 — ...`), so two log entries were silently merged
  into one. Split apart; the text of both is otherwise unchanged.
- 2026-10-04 — **Naming rule clarified in `AGENTS.md`, and the repo root
  tidied.** The house rule read "Kebab-case for files and folders. `snake_case`
  for data files", which left every Python module technically non-compliant and,
  more importantly, invited a rename that would break the test suite. Tested
  rather than assumed: `test-scales.py` still matches the `unittest` discovery
  pattern `test*.py`, but cannot be imported because a hyphen is not a legal
  identifier, so it is silently skipped — `NO TESTS RAN`, **exit 5**, and
  `tests/__init__.py` does not rescue it. Renaming would have switched the
  whole suite off without an exception being raised. The rule now exempts
  Python explicitly and records why the exemption is load-bearing, plus a second
  exemption for third-party asset names (`assets/fonts/` keeps upstream Google
  Fonts naming, which is not ours to normalise).
  The root prototypes `.css` and `.js` were deleted, and a `.gitignore` added for
  `__pycache__`/`*.py[cod]`. The deletion was gated on two checks because
  **neither file was tracked by git**, so there was no recovery: neither name
  appeared in any HTML, CSS or Python file, and the real stylesheet declares
  only Newsreader, IBM Plex Sans and IBM Plex Mono. Worth noting the near-miss
  in that check — a plain grep for "Inter" matched `src/motion.js`, which turned
  out to be a substring of `IntersectionObserver`, not the font. A loose match on
  a font name is exactly the kind of thing that would have justified keeping two
  dead files forever.
- 2026-10-04 — **Rejected feasibility report moved to `docs/archive/` and its
  banner strengthened; an archive convention written.** It lived at
  `docs/reference/political-feasibility-report` with no extension, which read as
  a live reference document rather than dead work. Now
  `docs/archive/2026-10-03-political-feasibility-report.md`, dated by the day it
  was discarded so the archive sorts onto the same timeline as the `## Events`
  entry that explains the rejection.
  The existing banner was **not sufficient**, and the reason is specific: it
  said the report was rejected and unsourced, but it did not say the report's
  seat arithmetic was **wrong**. The document claims 0 lower house seats; the
  AEC-verified figure is 1 (Farrer by-election, 25 May 2026). A reader who saw
  only "ARCHIVED — DO NOT CITE" would plausibly carry the 0 forward as
  historical background. The banner now names the error, gives the correction
  and its source id, and flags the Oxley row as an independent win rather than
  a party seat.
  The body is retained verbatim, errors and all, because it is the evidence for
  the decision. Editing it would destroy the reason the archive exists — which
  makes the annotation itself a hazard: rewriting the original `’` to `'` in
  the title while claiming the body was unedited would have quietly falsified
  it. Caught and reverted before finishing.
  `docs/standards.md` gained a "Discarded work" section, since no convention
  existed and this was the second time the question arose. It requires a
  discard-dated filename, a banner naming why and where the replacement is, the
  wrong claims listed with corrections, a verbatim body, and a flat prohibition
  on citing anything in the directory.
- 2026-10-04 — **Domain `marginoferror.com.au` purchased by Dale.** The highest
  risk open item is closed: an unregistered domain in the site's exact name was
  registrable by anyone, including a hostile party. Kept in `## BLOCKED` with a
  RESOLVED marker rather than deleted, matching how the seat-count contradiction
  was handled, because the record that the risk existed and was closed is itself
  worth keeping. Two follow-ups, neither urgent: confirm auto-renew is on, and
  note that holding the domain does not make the page publishable while the
  right of reply is outstanding.
- 2026-10-04 — **Build guard rails landed: the page can no longer ship an
  unsourced figure, an invisible margin, or placeholder prose.** Five assertions
  in `tools/build.py`, each verified to *fail* on the input it exists to catch,
  because a validation rule that has never been seen to fire is
  indistinguishable from one that does not work. Nine regression tests; suite is
  30, up from 21.
  The one that was not in the plan is the one that mattered. The template was
  still carrying live `PLACEHOLDER` text in the figure caption and source note,
  and every existing check passed, because the checks were all about *charts*.
  `index.html` was serving a reader the words "PLACEHOLDER SOURCE NOTE" in the
  one block where the citation lives. The chart placeholder check, the `h1`
  count and the token rule all looked at generated SVG and none of them could
  see prose. That is the same shape as the 0002 defect — a defect the tooling
  was not pointed at, so it shipped silently — and it was in the page right now.
  Provenance is declared on the `<svg>` root as `data-source-id` or
  `data-unsourced="true"`, chosen over a sidecar manifest because the manifest
  is a second thing to keep in sync with the artefact it describes.
  A chart claiming *both* is refused outright, since that is the shape that
  looks finished while citing nothing.
- 2026-10-04 — **CI added, and two of my own bugs caught by testing the check
  rather than writing it.** `.github/workflows/ci.yml` runs the build, the 30
  tests and an `index.html` drift check on every push and PR. Stdlib only, no
  `pip install`, because the point of locking the stack to Python stdlib was
  that the thing guarding this page's accuracy has no dependency chain to rot.
  Two defects worth recording, both in the guard rather than the page:
  1. **The drift check could never fail.** It ran the build first, which
     overwrites `index.html`, then diffed — so the drift was destroyed before
     it was measured. It reported clean on a file that had been hand-edited.
     Now it copies the committed file to a temp path first and diffs against
     that. Both the hand-edit and stale-template cases are verified to fail it.
  2. **A stray `</content>` tag landed in the workflow file**, caught because
     the YAML was parsed rather than eyeballed. It would have failed every run.
  The pattern across this session is the 0002 defect repeating: the checks were
  pointed at generated SVG, so the placeholder prose shipped; the drift check
  was pointed after the overwrite, so drift looked clean. In both cases the
  assertion existed and had never been seen to fail. Testing that a guard fails
  is now part of adding one.
- 2026-10-04 — **Task 0004 ingest written, and it confirms the blocker rather
  than clearing it.** `tools/ingest_roymorgan.py` produces 138 monthly waves and
  10 election results from the Roy Morgan PVI page, reproducibly from a saved
  copy. The trap AGENTS.md warns about is now enforced in code: `select_column`
  selects by header text, raises `UnmappedColumn` on anything absent, and
  refuses a **discrete** party request that resolves to an **aggregate** column
  while still allowing a deliberate aggregate request by name. `validate()` fails
  outright if `pvi_oned` is ever written on the monthly table. 7 tests, suite is
  37.
  The publisher's own footnote is the decisive evidence and is worth quoting in
  full, because it settles the arithmetic rather than leaving it to inference:
  the April 27 2025 combined cell reads 18.5 and "includes support for One
  Nation (highlighted in the release) of 7.5%". The party is a **subset** of
  that cell. So the monthly table cannot supply a discrete party share at all,
  and chart 01 cannot plot the party's polling trajectory from this house.
  That is now the **open editorial decision on 0007**: find a Tier B source with
  a discrete party column and a published margin, or change the chart's form to
  aggregate-versus-result with the party appearing only at election points.
  Neither is a technical choice and both change what the page claims.
  Four bugs found by running the script rather than reading it, all of the
  silent kind this project keeps hitting:
  1. The aggregate guard fired on a **legitimate** aggregate request on its
     first run, which is a guard that would have been deleted as broken rather
     than fixed. The guard belongs on the mismatch, not on aggregates.
  2. `election_date` collapsed to a bare year: a nested regex group read as the
     date. Output looked plausible and was wrong in every row.
  3. The quota warning tested "below 12.3%", which is true of **all ten**
     elections, so it warned on everything and therefore said nothing. Now
     flags the 2004-2016 block under 2.5%, which is the actual discontinuity.
  4. A local named `start` shadowed a year integer and crashed the run.
  Also: `n`, `margin_of_error` and `pub_date` are null on every row, because
  they do not exist to ingest. Re-verified live by string search for `sample
  size`, `margin of error`, `margin of sampling error`, `interviewed`,
  `confidence interval`, `plus or minus` and `+/-`: zero matches.
- 2026-10-04 — **Print hatch density closed, and it exposed a class of defect
  that no on-screen test can catch.** `DESIGN.md:212` asked for the band texture
  to be "expanded to a visible density" for print, and the only thing the print
  block did was set `print-color-adjust: exact`, which preserves the existing
  density rather than expanding it. A media query cannot change a `<pattern>`'s
  geometry — `width`, `height` and `stroke-width` are SVG attributes, not CSS
  properties — so the generator now emits both densities and the print block
  swaps the fill. Screen is 4px pitch at 1.0 stroke, print is 6px at 1.6, and
  the band edge goes solid rather than dashed because on paper the boundary
  carries the meaning, not the tint.
  The interesting part is the consequence. Swapping a fill means the print
  variant's pattern id is referenced **only from the stylesheet**, so it never
  appears in the markup and no existing check could see it. A typo in that one
  `url(#hatch-mo-print)` drops the uncertainty band to no fill on paper, which
  is exactly the failure the texture exists to prevent: an interval the reader
  cannot distinguish from a plain shape. Nothing on screen would show it,
  because screen uses the other pattern.
  So the build now resolves references from the stylesheet as well as the
  markup, and from the HTML as well as the SVG. Getting that check to actually
  fire took two attempts: a `starts with` allowance for the narrow variant's
  suffixed ids was too permissive and let a **broken wide-chart id pass**, since
  the narrow copy's `-narrow` id still satisfied the prefix test. Exact match
  only, every variant resolved independently. Both are now verified to fail, in
  wide and narrow.
  Five tests added. Suite is 42.
  **Still open and not testable here: a physical A4 print.** No automated check
  can confirm the texture survives a greyscale laser or inkjet, so the item stays
  open until someone prints the page.
- 2026-10-04 — **Right of reply: the AEC was searched and the address is not
  published. The item changes from research to decision.** Task 0003 was
  expected to surface the party's registered address incidentally; it does not.
  Recorded URL by URL in `docs/right-of-reply.md`.
  What was established: the live path is `Parties_and_Representatives`,
  capitalised, and the lowercase `/parties/` paths return **HTTP 200 with a
  "404 - Sauce not found" body** — the exact trap in `AGENTS.md` gotchas, hit
  live, and the reason every fetch was validated on page title. The party
  registration page carries requirements and forms but **no list of registered
  parties**. The transparency register has no One Nation entry. The bulk
  `All-Annual-Data.zip` (2.3MB, 13 files) was downloaded and `Party Returns.csv`
  unpacked: its columns are Financial Year, Name, Party Group, Receipts,
  Payments, Debts and Discretionary Benefits. **No address column.** The annual
  returns carry financial disclosure only.
  So the address sits on a registration statement the AEC holds and does not
  publish. No address is recorded anywhere in this repo, because
  `TASKS.md` `## BLOCKED` and `AGENTS.md` both forbid taking one from a news
  report or a social profile, and inventing the appearance of compliance would
  be worse than the open item.
  **Framing worth stating plainly: the cost here is delay, not the choice of
  channel.** The s 17 clock under the *Broadcasting Services Act 1992* only
  starts when the claim is put to the party, so nothing has been started yet and
  the item has been open since 2026-10-03. Three options are set out in
  `docs/right-of-reply.md` with a recommendation to run two of them together:
  write to the party's own published contact channel now, and ask the AEC's
  party registration team how the public can obtain the registered address,
  which is what closes the gap in non-negotiable 3.
  **Needs Dale's decision. Not actionable by an agent.**
- 2026-10-04 — **Print verification placed ON HOLD by Dale's decision.** The
  hatch-density code is complete and tested; the physical A4 print check is
  deliberately not scheduled. Recorded as code-complete and untested rather than
  done, because the difference between those two words is the whole point of
  this project's corrections policy. Deferred is not the same as verified.
- 2026-10-04 — **Correction: task 0004's blocker is smaller than recorded.** Dale
  asked what the discarded prototype assumed, which prompted a second look at
  the Roy Morgan page. It carries a **second table with a discrete One Nation
  column**, 132 rows spanning 2013 to 2022, which the ingest never read because
  it keys off the election-results table. Measured, per year: 2013 0 of 7 waves,
  2014 0 of 26, 2015 0 of 26, 2016 1 of 12, **2017 absent entirely**, then 2018
  4 of 4, 2019 6 of 6, 2020 8 of 8, 2021 16 of 16, 2022 15 of 15.
  So the true position is **a discrete monthly party series for 2018 to 2022**
  — five years — with nothing usable before 2018 and nothing after 2022, because
  the 2022-2025 monthly table is the combined-column one. The earlier note in
  this entry said the monthly table "cannot supply a discrete party share at
  all", which is true of the table it was looking at and false of the page.
  The distinction matters because it decides what the page can be: five years of
  monthly party polling against two election results is the axis the original
  thesis wanted.
  What is unchanged and still disqualifying: **no margin of error, no sample
  size, no publication date.** The series can carry polling-against-result with
  an honest "no published margin" marker, which is what non-negotiable 5 as
  amended requires, and it cannot carry a band.
  Also recorded from Dale's summary of the prototype: its realistic-ceiling claim
  put the ceiling at "1 to 4 regional **Queensland** lower house seats". The one
  verified win is **Farrer, NSW**, 25 May 2026. Small sample, but it is a
  regional stereotype standing where a verified result belongs, which is exactly
  what the archive convention now exists to catch. Items 2 and 3 of that summary
  (a +4.5%-per-cycle swing assumption, and volunteer numbers under 3,000 with
  sub-15% booth coverage) are **forecasts and unsourced estimates** respectively,
  and neither is publishable under non-negotiables 1 and 2. Items 1 and 4 are
  arithmetic about the electoral system and are a different matter: both are
  measurable from AEC data, and item 1 corresponds to the existing Chart 04
  spec.
- 2026-10-04 — **Prototype feasibility model received, archived, and read for
  what it assumed.** Filed at
  `docs/archive/2026-10-04-phon-feasibility-model.py`, body verbatim, banner
  recording four defects. Three are arithmetic: `TOTAL_HOR_SEATS = 150` against
  a 151-seat House, which contradicts the script's own printed string inside one
  run; `CURRENT_PHON_SEATS = 2` against a verified 1; and a seat-conversion model
  that is a linear ramp on coefficients appearing in no cited source.
  The fourth matters beyond this file. **The summary said booth coverage was
  "below 15%"; the script's own output is 1.33%.** A tenfold overstatement
  introduced between running a model and describing it, with no error raised.
  That is the same class as the 0002 zero-width band and the placeholder prose:
  a defect the tooling was not pointed at, shipping silently. It is recorded
  here because **the approved chart carries the identical exposure** — a
  mean-of-12-waves figure can drift from the waves it was computed from, and
  the only defence is computing it in code from the ingested file at build time
  rather than transcribing it. The spec requires exactly that.
- 2026-10-04 — **Chart 01 design approved and spec written.** The spine is
  polling-against-result for 2018 to 2022. The finding goes both ways: polling
  0.60 points high in 2019 and 1.29 points low in 2022. Recorded as a finding in
  the `## Events` log because it is the first time the dataset has produced an
  answer, and the answer is not the one the page's original framing implied.
  Two errors were caught in the spec's own first draft, both by recomputing from
  the source instead of trusting the number already in my notes:
  1. **The wave count is 48, not 49.** The table yields 49 rows carrying a
     discrete One Nation figure for 2018-2022, but one of them is the row
     labelled `2019 Federal Election - May 18, 2019`, which is a result rather
     than a poll. Counting a result among the polls is the same class of slip as
     a mean that drifts from its inputs, and it is exactly what the tenfold
     booth-coverage overstatement in the archived model looked like: a figure
     that survives because nothing recomputes it.
  2. **The 2019 window is 5 waves, not 12.** Only five polls precede that
     election; twelve precede 2022. The trailing-twelve rule is therefore "up to
     twelve", and a 5-wave mean is a different quantity from a 12-wave mean. Not
     padded, not presented as twelve: each mean is labelled with the wave count it
     used, and build assertion 2 binds that label to the arithmetic.
  Neither error would have been caught by reading the spec. Both were caught by
  running the computation again against the source, which is the habit the spec
  itself mandates for every number on the page.
- 2026-10-04 — **Spec approved with two changes; implementation plan written.**
  Dale: "lets add the seat-efficiency chart alongside", "lets build the chart
  and when I can eyeball it I will decide if it stays or goes", and approval of
  the spec.
  **Chart 02 added** (editorial Chart 04, moved earlier because the data exists
  now): national primary vote against seat share, both measured as a share of
  the 151-seat House so a single axis is honest rather than convenient, gap
  shaded. Provisional and marked as such — it will be judged by eye. It shares
  no data and no code with Chart 01 beyond `charts/stats.py`, so cutting it
  later costs nothing. The Farrer by-election is an **annotation on Chart 02,
  never a point on the series**: different electorate, different field,
  different denominator.
  **The supporting spans moved** from a separate figure to a second panel within
  the spine, so claim and evidence read together under one heading and one
  source note, and the page resolves to two charts rather than three. Recorded as
  a post-approval change rather than made silently.
  **The plan expects CI to be red.** Its Task 6 installs the AEC gate, which
  fails while the 2019 and 2022 results are cross-check-only. That failure is the
  correct state, so the plan says so explicitly and forbids loosening the
  assertion to get a green tick. Ordered last among the code tasks for the same
  reason: a known, explained red build beats a surprise mid-implementation.
- 2026-10-04 — **Implementation plan rewritten to the `writing-plans` skill's
  format.** Dale supplied the skill after the first plan was written by hand.
  The rewrite is not cosmetic; the skill's own self-review found four real
  defects in the first version.
  1. **No required header and no checkbox steps.** The skill mandates both, so
     no task could be tracked or handed to an executor.
  2. **Steps that decided nothing** — "mirroring the monthly ones", "edge cases"
    are precisely the failure the skill names: an implementer cannot write one
    reasonable thing from them. Replaced with named tests and their assertions.
  3. **No `Files:` / `Interfaces:` blocks.** The skill's premise is that an
    implementer sees only their own task, so the plan must state the names and
    types neighbouring tasks use. Every task now carries both, with exact line
    anchors into the files it modifies.
  4. **Proportion.** At 2.08x the spec and 43% code blocks, the plan was writing
    the program instead of the decisions. Now 1.78x and 21%, with test bodies
    reduced to name-plus-assertion tables. **The one exception is the Task 6 gate
    test class, kept in full and labelled as such** — those are the assertions
    standing between a plausible wrong chart and publication, and a summary of
    them is the wrong trade.
  Two new sections the skill requires and the first plan lacked: **Global
  Constraints** (the spec's project-wide rules, verbatim, applying to every task)
  and **Review Focus** (five inputs the spec implies but no test exercised, each
  pinned to the task owning the code). Those five are not hypothetical — four of
  them are edge shapes found in the live Roy Morgan source during this rewrite.

- 2026-10-05 — **Both charts built; the finding is that polling was wrong in
  both directions.** Computed at build time from
  `data/polls_roymorgan_oned.csv`, never typed:
  1. **Polling ran 0.60 points HIGH in 2019.** Five waves averaged 3.70 per
     cent; the party recorded 3.1.
  2. **Polling ran 1.29 points LOW in 2022.** Twelve waves averaged 3.71 per
     cent; the party recorded 5.0.

  Neither figure is smoothed, averaged across, or framed as a direction of
  error. Two elections, opposite signs, small magnitudes. The page's claim is
  that polling missed this party in both directions across two cycles, which
  is an open test of the polling, not a verdict on it.

  Two corrections to figures stated earlier in this log and in the spec, both
  caught by recomputing rather than trusting the earlier number:
  - The usable wave count is **48, not 49.** One row of the 132 on the source
    page is the 2019 election *result*, sitting in the same column as the polls.
  - The 2019 window is **5 waves, not 12.** Only five waves precede that
    election; 2022 has twelve. So the two means are over different numbers of
    observations, which is why every figure is labelled with the count it used.

- 2026-10-05 — **The seat series came from the AEC, not from a cross-check,
  and it changed two things the spec had wrong.**
  1. **The House did not always have 151 seats.** It returned 150 from 2001 to
     2016 and 151 from 2019, verified by summing every party's national total in
     each AEC party representation download. The spec said to divide by 151
     with "the denominator is not a parameter"; that is wrong for six of the
     nine elections, so it is a parameter now, read from each source.
  2. **1996 has no AEC record at all.** The archive begins at 2001, so the
     "1996 to 2025, ten general elections" span in the approved spec is
     unsourceable as written. 2001 is sourced from the AEC's official
     statistics ZIP instead, because the live tally room for that election
     carries a standing disclaimer that its results "are not final".

  All nine general elections now read from AEC primary sources, 0 seats at each.
  The party's only seat was the Farrer by-election in 2026, which is annotated
  on the chart and never plotted, because a by-election is one division on its
  own electorate with no comparable denominator.

- 2026-10-05 — **The publication gate is installed and deliberately red.**
  `tools/build.py --check` exits 1, refusing `chart-01.svg` and its narrow
  variant because their only source is marked `cross_check_only: yes`. This is
  the gate working and it clears when 0003 confirms the results. A test asserts
  the gate is still red, so it cannot be quietly loosened.

  Nine assertions were proven to fire by mutating one input each in a scratch
  copy, which is how three of them were caught **passing on the exact defect
  each was written to catch**: one compared a caption figure against a row count
  derived from the same file, one tagged every row with the value it was about
  to be checked against, and one had nothing in the repository it could fire on.
  A fourth accepted the correct chamber size on the wrong election, because a
  membership test cannot tell the difference between 151 being right and 151
  being right-for-2019.

- 2026-10-06 — **The previous session reported four defects as fixed and
  verified. Three were still on the page.** Found by asking a status question
  rather than by trusting the record: `index.html` as committed still carried the
  wrong `aria-labelledby` on both narrow charts and no `class="band"` on any of
  the eighteen shaded polygons. The sources were right and the artefact was
  wrong, because **the gate refuses to write while it is red, so while the gate
  was red the page could not be regenerated at all.** A gate that blocks
  publication had also frozen the thing under review, and nothing reported it.
  The screenshots from that session were taken from a live build, so they showed
  the fixed page; the committed page was not that page.

  Four defects found this time, all of them the same shape — a guard pointed at
  the wrong object, passing on the thing it exists to catch:

  1. **`--check` never checked drift.** `main()` validated the freshly built
     string and compared it to nothing. The drift comparison lived only in the
     CI workflow, in a step ordered after a step that fails by design, so it
     could never run. The 161 tests were in the same position behind it.
  2. **CI has never executed once.** `.github/workflows/ci.yml` is not on
     `origin/main` and the branch was never pushed. The backlog entry claimed
     the drift check "was verified to fail on both a hand-edited artefact and a
     stale template." A workflow that has never run verified nothing.
  3. **Task 0003 could not clear the gate as specified.** The spec promises the
     fix is a data edit needing "no chart code changes". False on both halves:
     `charts/chart_01.py` reads `primary_vote_oned_pct` and
     `requires_aec_confirmation`, and `data/aec_election_results.csv` has
     `primary_vote_pct` and **no confirmation column**, so pointing it at AEC
     data raises KeyError. And the registry held 2004–2022 only as an
     `aec-hor-<year>-fp-by-party` *family*, which the resolver did not expand —
     the `source_id:` line carried a trailing parenthetical, so the parser's
     `^source_id:\s*(\S+)\s*$` never matched it and the family registered
     nothing. **Seven of nine elections were unciteable.** Chart 02 passed only
     because it happens to cite 2001 and 2025, which were also written up
     individually.
  4. **`data-source-id` was being suffixed as if it were an element id.** The
     narrow-variant pass collects ids with `id="([^"]+)"`, which also matches
     the tail of `data-source-id="roymorgan-pvi"`. The built page therefore
     cited `roymorgan-pvi-narrow`, an id in no registry — and the unknown-id
     gate refused to write, which is the mechanism in defect 1.

  Fixed: families expand against a new `years:` field; the id scan now uses
  `(?<![-\w])id=` so provenance keys are left alone; drift is measured inside
  `validate()`; tests run before `--check` in CI; and `--draft` writes a marked
  artefact (noindex plus a banner stating the gate count) so the page stays
  current with its data while the gate stays red. Publication still requires
  `--check` to pass, which it cannot do until 0003 lands.

  Two new gates, each proven to fire: `artefact_source_id_problems` (the
  existing unknown-id check reads the *source* SVGs, so it cannot see a defect
  the build introduces — which is exactly how defect 4 hid), and
  `duplicate_id_problems`. The latter found a fifth thing: **all four charts
  emit a byte-identical `<pattern id="hatch-mo">`, and only the narrow variant
  is suffixed, so two wide charts in one page both declare it and every
  `url(#hatch-mo)` resolves to Chart 01's.** Harmless while the patterns match,
  silently wrong the moment either density is changed — the change would have no
  effect and nothing would say so. Scoped per chart is the real fix, but it
  breaks the single `.chart-narrow .band` rule that exists to swap the fill, so
  it is a design decision and is recorded rather than taken.

  Suite 144 -> 161. `--check` exits 1 naming chart-01 only, with **zero drift
  problems**, which is the state it should be in.

- 2026-10-18 — **Task 0003 closed. `tools/build.py --check` exits 0 for the
  first time, and the page is no longer a draft.** Chart 01's result axis moved
  from Roy Morgan's cross-check of the count onto the AEC's ingested series.
  `stats.load_results()` reads `data/aec_election_results.csv`, and each row's
  registry `source_id` travels through `Gap.result_source_id` so the chart cites
  exactly the elections it drew. A typed citation list would have drifted the
  moment an election entered or left the window, and the drift is a provenance
  claim pointing at a figure that is not on the page.

  `roymorgan-pvi` **stays** `cross_check_only: yes`. That is the correct reading
  of the marker: it says Roy Morgan is not a source of record for a *result*,
  and it remains a source of record for *polling*. The chart clears the gate by
  citing a confirmed AEC id beside it, not by having the marker removed. A test
  asserts both halves — the real check is green, and a chart citing only the
  cross-check is still refused — because a gate that has only ever been seen
  green is indistinguishable from a gate that was quietly loosened.

  **Figures the reader now sees, against the AEC's record:** polling ran +0.62
  points high in 2019 and −1.25 points low in 2022, where the cross-check read
  +0.60 and −1.29. The direction of the finding is untouched; the shift is the
  cross-check's rounding, and never exceeds 0.04 points at any of the nine
  elections. The design spec is amended rather than rewritten, because a spec is
  a dated artefact. **No `corrections.md` entry**: the spec's own rule was "AEC
  figures differ from Roy Morgan's, AEC wins", this is that case executed, and
  no figure was ever published — the page has been a draft throughout.

  **A sixth defect, found by the gate disagreeing with itself.** The
  source-file provenance check tested `sid not in registry` as a raw substring,
  while the artefact check used the parsed `_registry_entries()`. For a
  `<year>` family the two disagree: `aec-hor-2019-fp-by-party` is registered, by
  expansion, but is not a substring of the file. So the same citation was
  simultaneously accepted and refused, and the symptom looked like an unsourced
  chart. Both now resolve through one parser. A guard that reimplements the
  thing it guards is a second source of truth, and this is what two sources of
  truth cost.

  **Also found: the spec's promise that closing 0003 needed no chart code change
  was false.** `chart_01.py` read `primary_vote_oned_pct` and
  `requires_aec_confirmation`; the AEC file has `primary_vote_pct` and no
  confirmation column, so pointing it at the AEC data raised `KeyError`. Two
  column names that read alike are two different sources, which is why
  `load_results()` now refuses a file without `primary_vote_pct` and names the
  columns it found.

  Suite 161 -> 165. The gate-red test class was inverted, not deleted.
