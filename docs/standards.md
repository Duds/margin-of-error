# Editorial standards

The bar a figure has to clear before it goes on the page. Companion to
`data-sources.md`, which records *what* the sources are; this records *how* they
are cited and what a correction is.

---

## Citation format

Every figure in a chart caption or body copy cites inline:

> Primary vote, 2025 federal election. Source: Australian Electoral Commission,
> House of Representatives results, retrieved 2026-10-03.

For polling, the citation must carry the four fields that make it checkable:

> Two-party primary, fieldwork 12–15 September 2025, n=1,424. Source: pollster
> name, published 17 September 2025, margin of error ±2.4.

If any of those four fields is unavailable for a poll, the poll does not go on
the page. No fieldwork window means no margin of error, which means the number
cannot be distinguished from noise — which is precisely the question this site
is about.

---

## Sourcing tiers

Defined in `data-sources.md`. Two rules that go beyond the table:

**One hop to primary.** If a figure reaches you via a news article, that is not
a citation, it is a lead. Trace it to the AEC document or the pollster's own
published table. If it cannot be traced, it does not run.

**Interested parties cite at their own interest.** Party financial returns are
useful and go in Tier A, because they are filed documents and the AEC publishes
them unchanged. But a self-reported figure presented as neutral fact is not the
same as a filed figure, and the caption should say which it is.

---

## Neutral register

The test: would this sentence be equally at home in a report written by a
supporter and by an opponent?

- ✅ "Lost Griffith by 630 votes, a margin of 0.8 points."
- ❌ "Collapsed in Griffith." "Nowhere near a threshold." "The polling was
  nothing but a lie."

Descriptive, specific, and sourced beats evaluative and vague. Precision is
itself a form of impartiality — "lost by 630 votes" tells a reader more than
any adjective, and it cannot be argued with.

Where a party or a person has made a claim worth reporting, report the claim
attributed to its maker: "the party said the result showed X" — never as a
statement of fact.

---

## Defamation

Pauline Hanson is a living person. Under the *Broadcasting Services Act 1992*
ss 17–23, truth is an absolute defence, so accuracy is necessary but not
sufficient — the accuracy must be demonstrable from the record.

Practical consequences:

- Every allegation of fact carries a citation to the document it rests on.
- Opinion is avoided. If a judgement is unavoidable, it is attributed and the
  attribution is accurate.
- Quotes are exact, not trimmed to change meaning, and are attributed verbatim.
- Right of reply is a hard precondition for publication, tracked in
  `right-of-reply.md`.
- Photographs and images carry a source and a licence. Do not reproduce the
  party's logo, wordmark, "Vote 1" branding, or campaign material — these are
  trade-marked and reproducing them in editorial context is a separate legal
  question from fair dealing for reporting.

---

## Uncertainty

Not optional, and not a footnote.

- No bandless point estimate for a poll-derived figure, anywhere.
- Every chart rendering an estimate carries its interval, visually and numerically.
- A caption that says "rising" when the change is inside the margin of error is
  wrong. This is the site's own subject matter, so it applies with full force.
- State the measure. "Primary vote" and "two-party primary" and "primary
  including preferences" are three different numbers and are not
  interchangeable.
- Round honestly: 4.1% not 4.07%. False precision undermines the whole site.

---

## Corrections

`corrections.md` is append-only and public. Policy:

- A correction is appended, never an edit to a previous entry.
- State what was wrong, what is right, and when it was fixed.
- If the error changed a reader's conclusion, say so explicitly.
- Silence is not a fix. An unannounced number swap is worse than an error.

---

## Language

- `en-AU`. Dates `D MMM YYYY`. No `MM/DD/YYYY`.
- Plain English, and assume the reader has not voted since 1996.
- Define a term on first use: first preference, two-party swing, vote
  efficiency, margin. Assume none of them are known.
- No jargon as shorthand for a conclusion. "Preferred" and "quota" are fine.
- Avoid the subject's name in the page title and in headings where the
  subject's party name would do. This is about the party's electoral record, not
  about a person.

---

## Accessibility

The floor, not the goal. A reader using a screen reader, printing in greyscale,
or navigating by keyboard is a first-class reader of this site.

- 4.5:1 contrast for body text, 3:1 for large text and chart strokes.
- Every chart has a caption stating its finding in words, and links to the data
  table. If a chart cannot be read with images off, it does not ship.
- Uncertainty bands are textures, not colours, so they survive greyscale and
  forced-colours mode.
- No information carried by colour alone; every distinction has a second
  channel.
- Keyboard reachable, visibly focused at 2px.
- One `h1`. No skipped heading levels.

---

## Reproducibility

- Raw data is committed alongside the derived data. Never overwrite raw.
- Every transformation from raw to published is in code, not done by hand.
- `python3 -m venv .venv` then install from a pinned `requirements.txt`;
  record the retrieval date in the dataset, not the filename.
- Each dataset carries a `method.md` note: what was dropped, what was joined,
  what assumptions were made, what a reader would need to reproduce the result.