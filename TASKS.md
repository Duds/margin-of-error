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
- **0003 — Source the AEC data** — build the historical vote series.
  > Blocked on nothing. AEC publishes results by election, house of reps and
  > senate files per cycle. Historical series must match on AEC party
  > abbreviation per election, not the modern name, or rows drop silently.
  > **Progress 2026-10-03:** results.aec.gov.au is the live archive. The
  > general-election index is `results.aec.gov.au/<eventId>/Website/`, one
  > event id per cycle. Seat count verified (see BLOCKED). The historical vote
  > series across cycles is the remaining work.
  > Next: register every intended source in `docs/data-sources.md` before use.
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
- **0007 — Chart one: the band** — whatever the thesis calls for first.
  > Depends on: 0001, 0003, 0004.
  > **The build blocker is cleared.** It was previously "blocked on a build
  > assertion, not on data": `charts/chart_01.py` held unsourced placeholder
  > values and passed every check, so nothing stopped an unsourced chart from
  > shipping. Both halves are now implemented and tested — the sourced-data
  > assertion and the zero-width band assertion (BACKLOG: citation resolver).
  > **0007 is now blocked on data only:** tasks 0003 and 0004 must supply the
  > polling series and the AEC results.
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
  > - **Both variants ship in the DOM as siblings**, CSS-switched at 640px, so
  >   a screen reader always finds a chart. Not `<picture>`: verified that it
  >   does not media-switch two inline `<svg>` elements. Narrow IDs are
  >   suffixed and its `url(#hatch-mo)` rewritten, or both charts would claim
  >   the same `id` and the narrow `aria-labelledby` would resolve to the wide
  >   chart's title.
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
  without a manifest to drift out of sync. 9 regression tests cover these;
  suite is 30.
- **Mobile layout verification** — verify at 320px, 680px, 1100px against the
  grid spec in `DESIGN.md`. Partially done by 0006 (320px and 1280px
  measured, reduced-motion checked); 680px and 1100px are unverified, and
  680px is the breakpoint the 640px chart switch sits just inside.
- **Accessibility audit** — axe or equivalent, plus manual keyboard traversal.
  The build enforces the floor mechanically (`lang="en-AU"`, one `h1`, one
  `main`, `role="img"`/`<title>`/`<desc>` on every chart, no unfilled
  placeholder, no raw hex), but no third-party audit and no keyboard pass has
  been run.
- **CI** — **DONE 2026-10-04.** `.github/workflows/ci.yml` runs on push and
  pull request: `build.py --check`, the 30 geometry and guard-rail tests, and a
  drift check confirming `index.html` matches its sources. No `pip install`, so
  the guard on the page's accuracy has no supply chain to go stale. Python
  pinned to 3.13 (the generators use PEP 604 unions, so 3.10 is the floor).
  Verified by simulating each step locally, and the drift check was verified to
  fail on both a hand-edited artefact and a stale template.
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
