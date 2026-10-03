# TASKS — Margin of Error

Tiered task list. Context notes in the `>` block under each item carry
session-to-session continuity; update them when the state changes.

Each active task has a detailed file in `_tasks/`. TASKS.md is the index.

---

## NOW (Active)

- **0001 — Editorial thesis and the question the page answers** (IN PROGRESS)
  > File: [`_tasks/0001-editorial-thesis.md`](_tasks/0001-editorial-thesis.md)
  > The page needs one question, not six. Candidates so far: (a) has the party
  > ever exceeded a polling high, or has polling always overstated it? (b) how
  > does a 4% vote behave at the seat level? (c) what does the preference flow
  > do to a party polling in the low single digits?
  > Blocking everything downstream. Charts cannot be specified until the
  > thesis is fixed, and the thesis needs the data to be scoped.
  > Next: pick the question, write it as a single sentence, then scope the data.

---

## NEXT (Ready to Start)

- **0002 — Lock the chart stack** — `vanilla-svg` vs `Observable Plot` vs `D3`.
  > Decision hinges on how many custom chart forms are needed. Three bespoke
  > charts argue for hand-built SVG; five or more argue for a library.
  > Depends on: 0001.
- **0003 — Source the AEC data** — build the historical vote series.
  > Blocked on nothing, but doing it early de-risks 0001. AEC publishes
  > results by election, house of reps and senate files per cycle. Historical
  > series must match on AEC party abbreviation per election, not the modern
  > name, or rows drop silently.
  > Next: register every intended source in `docs/data-sources.md` before use.
- **0004 — Establish the polling dataset** — fieldwork dates, house, n, margin.
  > Every row needs `fielded_start`, `fielded_end`, `pub_date`, `house`, `n`,
  > `margin_of_error`. A poll without a fieldwork window is not usable.
  > Depends on: 0001 (which polls matter depends on the question).
- **0005 — Right of reply** — send the draft thesis and named claims.
  > Blocking publication, not blocking development. Send before the copy is
  > final, so a substantive response can shape the framing.
  > Depends on: 0001.
- **0006 — Build the page shell** — typography, grid, source-note component.
  > Depends on: 0002.
- **0007 — Chart one: the band** — whatever the thesis calls for first.
  > Depends on: 0001, 0003, 0004.

---

## BLOCKED

- **Right of reply to the party's registered address** — no contact on file.
  > Need the party's registered address from its most recent AEC party
  > registration statement. The AEC publishes these. Blocked until 0003
  > surfaces it; do not guess an address from a news report.
- **Domain registration** — `marginoferror.com.au` appeared unregistered at
  > 2026-10-03 WHOIS check but is not held. Until it is purchased it is
  > available to anyone, including a hostile party. Treat as highest risk.
  > Status: unpurchased as of 2026-10-03.

---

## BACKLOG

- **Corrections policy page** — `docs/corrections.md` exists as an internal
  register; it needs a public-facing version and a route for readers to report
  an error.
- **Seat boundary handling** — AEC redistributions change seat names and
  boundaries. A helper that resolves a historical seat to its current
  equivalent is needed before any cross-cycle seat comparison chart ships.
- **Small multiples by state** — one small multiple per state beats a
  multi-line spaghetti chart, and Queensland is the story. Prioritise QLD, NSW,
  VIC, WA.
- **Vote efficiency calculator** — the metric that explains how a low-single-digit
  primary vote becomes seats. Needs the seat-level vote conversion data.
- **Print stylesheet** — `DESIGN.md` specifies it, nothing implements it.
- **Reduced-motion and forced-colours audit** — specified, not built.
- **Citation resolver** — a build step that fails the build if any figure on the
  page has no entry in `docs/data-sources.md`.
- **Mobile layout verification** — verify at 320px, 680px, 1100px against the
  > grid spec in `DESIGN.md`.
- **Accessibility audit** — axe or equivalent, plus manual keyboard traversal.
- **Performance budget** — target LCP under 2.0s on a 4G connection. Fonts
  > self-hosted, subset to the Latin subset used. Sub-200KB critical path.

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