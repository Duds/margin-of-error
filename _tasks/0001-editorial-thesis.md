# 0001 — Editorial thesis and the question the page answers

- **Status:** in progress
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

Three candidate theses are live in `TASKS.md`. The working preference is
candidate (a), on the gap between polling and results, because:

- It is the literal meaning of the site's name, so the branding and the
  argument are the same thing.
- The data is public: AEC results and published polling are both obtainable.
- It survives the political situation changing. Whether the party is rising or
  falling, the question of whether polling matches the vote remains answerable.

Candidate (b), seat-level behaviour of a low-single-digit vote, is the stronger
data story but is a *mechanism* explanation rather than a finding, and it needs
vote-conversion data that is harder to source.

## Open questions

- Does the thesis need a comparator party to mean anything? "Polling
  overstates this party" is more legible alongside "polling is accurate for
  the major parties", but that widens the scope considerably.
- Is one election cycle enough, or does the series need to run from the
  party's founding? A founding-to-present series is stronger but the early
  years have different boundaries and party naming.
- How current does the polling series need to be to be worth publishing? A
  six-month-old poll is not a finding.