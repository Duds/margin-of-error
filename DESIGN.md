---
updated: 2026-10-03 (band spec revised, see "Where there is no band")
---

# DESIGN.md — Margin of Error

Single source of truth for visual decisions. Read by agents when writing any
markup or CSS, and when generating any chart.

---

## Aesthetic

**Broadsheet data desk.** Warm paper, hard rules, restrained ink, one colour.
The reference points are the financial pages of a quality newspaper and an
economics desk: dense with figures, unhurried, no decoration that does not
carry data. The page should feel like it was set by an editor who trusts the
reader.

Deliberately **not**: a dashboard, a dark-mode analytics product, a campaign
microsite, a neon data-art piece. The subject is partisan, so the design's
job is to be the most boring, most careful thing in the room.

Do NOT generate: border-radius on data containers, drop shadows on flat
surfaces, gradients as decoration, icon fonts, carousels, animated counters,
framework CSS utility classes, or any chart with a 3D effect.

---

## Colour Palette

One accent, one diverging pair, one uncertainty texture. Colour carries meaning
here, so the palette is deliberately small.

| Token | Hex | Usage |
|---|---|---|
| `--color-paper` | `#FBFAF7` | Page background. Warm off-white, not `#fff` |
| `--color-paper-raised` | `#F2EFE9` | Source notes, figure captions, table stripes |
| `--color-ink` | `#14110F` | Body text, rules, the subject series |
| `--color-ink-muted` | `#6B6259` | Captions, axis labels, secondary metadata |
| `--color-rule` | `#D8D2C8` | Hairlines, table borders, gridlines |
| `--color-accent` | `#2B4C7E` | Links, the page's structural accent, focus rings |
| `--color-gain` | `#0F7B6C` | Positive margin: seat won, share increased |
| `--color-loss` | `#C1443A` | Negative margin: seat lost, share decreased |

### Rules on colour

- The diverging pair is teal and red, not green and red. Teal/red survives
  deuteranopia and protanopia; green/red does not.
- **Never encode by colour alone.** Every distinction carries a second channel:
  a label, a sign, a pattern fill, or a position. A diverging bar chart is also
  signed, a line chart is also direct-labelled.
- Orange is the party's brand colour. **Do not use it.** Using the subject's
  brand colour would import their identity into the design. The subject is
  rendered in `--color-ink`; every other party is rendered in `--color-rule` or
  `--color-ink-muted`. This is the "one story, one colour" pattern, and it
  sidesteps the branding question entirely.
- Saturation is the only thing separating the subject from context. Do not
  introduce a fourth hue.

### Uncertainty texture

The signature motif, and the reason the site is named what it is.

| Token | Value | Usage |
|---|---|---|
| `--band-fill` | `rgba(20, 17, 15, 0.07)` | Confidence interval wash |
| `--band-hatch` | `url(#hatch-mo)` | 45-degree hatch, 4px spacing, 1px stroke |
| `--band-edge` | `--color-ink-muted` | Band boundary, 1px dashed |

The band is a texture, not a colour. That keeps it legible in greyscale print,
in forced-colours mode, and for readers who cannot distinguish the series hue.
Where a band is too narrow to read as a texture, widen it or show the interval
as a numeric label instead. Never omit the band to make a chart tidier.

### Where there is no band

Revised 2026-10-03. Roy Morgan, the most complete Tier B polling source
available, publishes no sample size and no margin of error for its primary
voting intention poll. It also links no methodology page and offers no data
download. So for much of the series there is nothing to draw.

**The absence gets its own marker.** A poll point with no published margin
carries a small open circle in `--color-ink-muted`, distinct from a banded
point, plus a count in the caption. Do not render it as a clean point on a line,
because a clean point on a line asserts a precision nobody stated.

**Never impute.** Do not compute a margin from a default maximum sample size, do
not carry forward the last known margin, do not substitute an industry rule of
thumb. A fabricated band is a fabricated number in the visual language of
honesty, which is the one thing this site does not do.

This makes the motif more honest than the original brief assumed. The band is
not decoration for the numbers; it is the record of how precise the source said
it was. Where the source said nothing, the chart shows nothing, and says so.

**This is a statement about the evidence, not about the source.** The marker
marks the limit of what the page's comparison can support. It is never captioned
as a criticism of any publisher, and the page does not generalise from one
publisher to pollsters as a class. See the Gotchas entry "Do not write about
pollsters" in `AGENTS.md`.

---

## Typography

Open-licensed, self-hostable, no CDN dependency at runtime.

| Role | Face | Fallback | Notes |
|---|---|---|---|
| Display | **Newsreader** (SIL OFL) | `Georgia, serif` | Headline, section titles, pull quotes. Has real italics |
| Body | **IBM Plex Sans** (SIL OFL) | `system-ui, sans-serif` | Prose at 18px minimum |
| Figures | **IBM Plex Mono** (SIL OFL) | `ui-monospace, monospace` | All tabular figures, axis ticks, data tables |

- Body text is **18px / 1.6**. Never smaller than 16px for any axis label.
- Figures always use `font-variant-numeric: tabular-nums`. Columns of numbers
  must align on the decimal.
- Prose measure: **66ch maximum**. Charts may break out to 1120px.
- No more than two type sizes in the same view. No text in all caps for
  anything a reader needs to read; all caps is for kickers and axis units only.

---

## Spacing

4px base unit.

| Token | Value |
|---|---|
| `--space-1` | 4px |
| `--space-2` | 8px |
| `--space-3` | 12px |
| `--space-4` | 16px |
| `--space-5` | 20px |
| `--space-6` | 24px |
| `--space-8` | 32px |
| `--space-10` | 40px |
| `--space-12` | 48px |
| `--space-16` | 64px |

Section rhythm is `--space-12` at mobile, `--space-16` desktop. Nothing uses a
literal pixel value that is not in this table.

---

## Layout

- **Mobile-first**, single column, content max 720px centred.
- Charts break out of the prose column to a 1120px `full` grid track.
- A 12-column grid at >= 960px, 6-column at 640px to 959px, 1-column below.
- Source note sits directly beneath every figure, never collected into a
  footer. A reader must never have to search for what a number came from.
- Hairline rules, not boxes. Use `--color-rule` at 1px. No cards.

---

## Charts

Read `docs/chart-specs.md` for the required data and the claims each chart may
and may not make. The rules below are general.

| Rule | Detail |
|---|---|
| Output | Inline SVG, `role="img"`, with a `<title>` and `<desc>` |
| Axis | Direct-label the series; drop the x-axis gridlines except a zero rule |
| Colour | Subject in `--color-ink`, context in `--color-ink-muted` |
| Uncertainty | Every poll-derived point carries a band **where one is published**, and a visible "no published margin" marker where one is not. The marker states a limit on the evidence, never a criticism of a publisher. Never impute a margin from an assumed sample size |
| Annotation | One annotation per chart, in `--color-ink`, with a leader line |
| Data labels | Prefer them to a legend. Under 8 series, label directly |
| Tooltips | Hover tooltips are an enhancement, never the only route to a value |
| Small multiples | One small multiple per state beats a 6-line spaghetti chart |

The band motif must appear at least once in the first viewport, so the reader
meets the thesis before meeting the data.

---

## Motion

| Name | Duration | Usage |
|---|---|---|
| `fade-in` | 240ms | Section entry, once, on intersection |
| `draw` | 600ms | Line chart path draw, once, on intersection |

Everything respects `prefers-reduced-motion: reduce`, which disables both and
resolves to the final state. No motion conveys meaning. No scroll-jacking, no
parallax, no counting animations.

---

## Accessibility floor

This is the minimum, not a goal. See `docs/standards.md`.

- Contrast: 4.5:1 for body text, 3:1 for large text and chart strokes.
- Every chart has a text equivalent: a caption stating the finding, and a
  linked data table. A chart that cannot be read with images off does not ship.
- Keyboard: all interactive elements reachable and visibly focused at 2px
  `--color-accent` offset.
- Landmarks: `header`, `main`, `figure`, `footer`. One `h1`. No heading level
  skipped.
- `forced-colors` mode: the hatch texture and `--color-rule` both survive.
- Language set to `en-AU`. Dates as `D MMM YYYY`, never `MM/DD/YYYY`.

---

## Print

A reader will print this. Ship a print stylesheet.

- Force `--color-paper` to white and remove the paper tint.
- Expand the hatch pattern to a visible density; print at `-webkit-print-color-adjust: exact`.
- Show source URLs in full in the print footer of each figure, not just the source name.
- Break before a figure whose caption would be orphaned from it.
- Target A4 portrait. Assume no colour printer.

---

## Generative UI rules

When generating any markup or CSS for this project:

1. Use only the semantic tokens above. Never a raw hex value.
2. Prose in Newsreader, UI in IBM Plex Sans, figures in IBM Plex Mono.
3. 1px solid `--color-rule` borders, no `border-radius`, no `box-shadow`.
4. Emit plain HTML and CSS. No Tailwind, no CSS-in-JS, no component framework.
5. Subject data is `--color-ink`. Context data is `--color-ink-muted`. Nothing
   else gets a hue.
6. Any chart rendering a poll figure ships its band where one is published, and
   its "no published margin" marker where one is not. It ships neither only if
   the figure is not poll-derived.
7. Source notes are part of the figure, not an afterthought.
8. Null is a value. Render it as a visible marker with a count, never as an
   absence and never as a guessed number.