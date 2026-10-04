# 0002 — Lock the chart stack

Status: **CONFIRMED 2026-10-03 by Dale.** Editorial sign-off recorded per
`AGENTS.md`. The chart stack is now settled: build-time SVG generation in
Python, stdlib only, no charting library, no client-side JavaScript, no bundler,
no framework, with the generated SVG **inlined into `index.html` by the build**.

Inline rather than `<img>`-referenced, so `var(--token)` fills keep inheriting
from the page stylesheet and a token change re-skins every chart without a
regeneration. The cost is that `index.html` becomes a generated artefact, which
is recorded below as an accepted consequence and as a rule for task 0006.

Supersedes an earlier draft of this file, which recommended hand-built inline
SVG on a d3 subset in the browser. Four options were costed and the
recommendation changed. The original reasoning was not wrong about the
libraries; it was wrong to treat "no client-side JavaScript" as automatically
better, and it did not weigh the Python mandate in `docs/standards.md` properly.

---

## Locked decision, in one place

| Question | Answer |
|---|---|
| Chart generation | Python, stdlib only, run at build time |
| Charting library | None. `requirements.txt` may hold no plotting library at all |
| Client-side JS for charts | Zero. Not d3, not Plot, nothing |
| Chart delivery | SVG inlined into `index.html` by the build |
| Fills in generated SVG | `var(--token)` only, never raw hex |
| Motion | `IntersectionObserver` + CSS, no library |
| Third-party runtime deps | None for charts. Fonts vendored at task 0006 |
| Accessibility layer | Written on the root `<svg>` by our own code, never retrofitted |
| Tests | Assert no band has zero width; assert tick steps; assert viewBox |

This supersedes the `## Recommendation` heading that follows, which is kept as
the reasoning of record for how the decision was reached.

---

## Recommendation (now CONFIRMED, see the locked table above)

**Build-time SVG generation in Python, stdlib only. No charting library, no
client-side JavaScript, no bundler, no framework.**

Generated `.svg` files are committed alongside the Python that produces them and
the raw data that feeds it. The page ships static.

This keeps `docs/standards.md`'s `python3 -m venv .venv` mandate satisfied
rather than fought, and it removes the last place on the page where a number
could be edited by hand.

---

## The four options costed

Measured, not asserted. Sizes are raw / gzip.

| Option | Client JS | Output size | Licence | Verdict |
|---|---|---|---|---|
| **Python, stdlib only** | **none** | **1.9 KB / 0.7 KB** | own code | **Recommended** |
| Python + matplotlib | none | 16 KB / 3.6 KB | PSF-based | Rejected, see below |
| Observable Plot | 91 KB gzip | — | ISC | Rejected |
| vega-lite, build-time compile | none | 9.4 KB / 1.4 KB | ISC | Rejected |
| vega-lite, runtime (vega-embed) | 297 KB gzip | — | ISC | Rejected on payload alone |
| Chart.js 4 | 58 KB gzip | — | MIT | Rejected, canvas |
| hand-built inline SVG in page | 9 KB gzip (d3 subset) | — | ISC (d3) | Superseded |

Reference points measured earlier: Observable Plot 0.6.17 depends on all of d3
and bundles to 270 KB / 91 KB gzip. The `d3-scale` + `d3-shape` + `d3-array`
subset is 24 KB / 9 KB gzip. Tree-shaken Chart.js 4 is 169 KB / 58 KB gzip.

### Verified personally

I wrote the stdlib generator and rendered it in a real browser rather than
trusting the numbers:

- 1,919 bytes of SVG, **704 bytes gzipped**, from 68 lines of Python.
- `role="img"` with `<title>` (67 chars) and `<desc>` (92 chars) present and
  read from the correct element, confirmed via the DOM.
- Hatch `<pattern id="hatch-mo">` with `patternTransform="rotate(45)"`, the
  `DESIGN.md` motif, emitted natively.
- Zero raw hex in the output. Every fill is `var(--token)`, so a token change
  in CSS re-skins all four charts with no regeneration.
- `viewBox="0 0 520 320"`, so the chart scales with the 1120px breakout track
  and the 320px mobile floor without re-rendering.

### Two bugs I hit while proving it

Both are recorded because they will recur in task 0007, and the second is a
correctness issue on the site's central claim.

1. **Axis padding unpacked in the wrong order.** I wrote `PAD = (56, 20, 40,
   64)` and unpacked it as `x0, x1, y0, y1`, giving an inverted plot area and
   degenerate polygons. Caught by asserting on rendered `getBBox()`, not by
   reading the code. Geometry needs assertions, not eyeballing.

2. **A lone banded poll collapses to zero width.** Where a null margin splits
   the series, an isolated banded poll on one side becomes a polygon with
   `width === 0`, so **its uncertainty interval is invisible**. That is the
   worst class of bug this site can have: a poll whose margin was published
   renders as though it had none, which is precisely the false claim
   `DESIGN.md`'s "Where there is no band" section exists to prevent.

   Fix, to carry into 0007: a band segment of one poll renders as a **vertical
   whisker plus cap**, not a polygon. A polygon needs two distinct x values to
   have width at all. Test for it: assert no band element has zero width.

---

## Why stdlib Python, and not matplotlib

matplotlib was costed properly and is the obvious alternative, since it is the
one library that emits a hatch `<pattern>` natively.

**It fails the accessibility floor on arrival.** Grepping its output for
`role=`, `<title` and `<desc>` returns zero matches. Every chart would need a
post-processing pass over the root element to become compliant. On a site
whose first non-negotiable is defensible accuracy, the accessibility floor
should be structurally guaranteed by writing the root `<svg>` yourself, not
retrofitted by string surgery on someone else's output.

**Text is converted to paths by default.** It emits
`<use xlink:href="#DejaVuSans-13"/>` glyph outlines, so axis labels are
invisible to screen readers and the file embeds a slice of DejaVu Sans
regardless of the font you style it with. `svg.fonttype = "none"` fixes that
but then emits a nine-deep hard-coded fallback stack with no IBM Plex Mono.

**Weight.** 13 packages, 133 MB, for the one feature it has that raw SVG does
not, which is about six lines of hand-written markup.

**Its one real win is free elsewhere.** `hatch="////"` produces a real
`<pattern>` def, but the tile is 72 units with ~28 segments rather than the
specified 4px spacing, so the geometry still needs overriding. The thing you
would install 133 MB for is not the thing you get.

Also rejected: **plotly + kaleido** (99 MB, and kaleido 1.4.0 reused a
`chrome-headless-shell` already on the machine, so the export step depends on a
Chrome install that a pinned `requirements.txt` cannot express, breaking the
reproducibility guarantee), **bokeh** (123 MB, built for interactive documents,
not bare SVG), **pygal** (ships its own CSS theme layer, the opposite of
`DESIGN.md`), **svgwrite** (1 package, 25 MB, pleasant dependency footprint but
no raw-XML escape hatch, so anything outside its element set needs private
attributes; it does have `svgwrite.pattern.Pattern` and `svgwrite.text.Text`).

## Why not vega-lite

The build-time compile path is real and does ship zero JS. It loses anyway,
and the reasons are specific:

- **No accessibility layer.** Across the build-time path and Altair: zero
  `role="img"`, zero `<title>`, zero `<desc>`. A `title` set in the spec
  appears nowhere in the output. `aria: true` compiles without effect.
  `vegalite_to_html` does emit them, but that output needs vega-embed at
  runtime, which is the 297 KB option.
- **The hatch can only be referenced, not defined.** `fill="url(#hatch-mo)"`
  passes through verbatim, but the compiler emits no `<defs>`, no `<pattern>`.
  The site's signature motif is the one thing it cannot produce.
- **Custom themes silently no-op.** `theme=` rejects dicts; only 14 fixed
  names exist. `theme="dark"`, `theme="moe"` and no-theme all returned
  byte-identical 9,418 B output. No error, no warning. Silent no-ops are worse
  than a failure on a page whose whole claim is traceability.
- It needs 21 `config` keys plus per-layer colour on all six layers, which is
  the repetition `DESIGN.md` forbids, and its output must then be patched to
  attach the a11y attributes to positional classes like `layer_2_marks` that
  break on reordering.

One genuine finding from that investigation, worth keeping: `var(--token)`
fills **pass through untouched**, so a var-only spec compiles to zero raw hex.
That is a point in favour of vars generally, and it is why the recommendation
emits `var()` fills too.

## Why not client-side at all

My first draft recommended a 9 KB gzip d3 subset over Plot's 91 KB, and that
comparison is still correct on payload. It was wrong on two counts.

**A hand-written SVG path in `index.html` is a transformation done by hand.**
`docs/standards.md` requires every transformation from raw to published to be in
code. Change a number in the raw data and a hand-inlined chart does not move;
you edit path `d` attributes by eye. For a site whose thesis is *do not present
a number you cannot trace*, the chart is the most load-bearing number on the
page, and inlining it makes the one artefact with no code path from source
data. That is an editorial liability dressed as a performance optimisation.

**It does not need to be a tradeoff.** Build-time Python is 0.7 KB gzipped of
client JS, which is zero, against 9 KB for the d3 subset. Python wins on the
metric I originally optimised for, as well as on traceability.

The `viewBox` strategy question raised in the earlier draft (task 0008) largely
dissolves: `viewBox` plus `width:100%; height:auto` scales a generated chart to
any track width with no re-render and no JS. What remains is chart-specific
label density at 320px, which belongs in `chart-specs.md`.

---

## The motion layer

Costed separately, since it was bundled into "the stack" and is a separate
decision. `DESIGN.md` specifies exactly two animations: `fade-in` 240ms on
intersection, and `draw` 600ms for a line path on intersection.

| Option | Raw | Gzip | Licence |
|---|---|---|---|
| **IntersectionObserver + CSS** | **0.7 KB** | **0.4 KB** | own code |
| animejs 4 | 43 KB | 16 KB | MIT |
| motion 14 (Framer Motion vanilla) | 60 KB | 22 KB | MIT |
| GSAP 3.15 + ScrollTrigger | 112 KB | 44 KB | **not OSI open source** |

**GSAP is excluded on licensing, not preference.** Its npm licence is the
"Standard no charge license", a bespoke commercial grant, not an OSI licence, so
it fails `AGENTS.md` outright.

Verified in a real browser, not asserted:

- `getTotalLength()` returns 195.95 for a test path, so the
  `stroke-dasharray` / `stroke-dashoffset` draw technique works.
- Computed transition is `stroke-dashoffset 0.6s`, matching the spec.
- With `prefers-reduced-motion: reduce` emulated, computed transition becomes
  `none 0s`. The reduced-motion path is **pure CSS**, so there is no JS branch
  that can get it wrong and no failure mode where a reader who has asked for
  reduced motion sees an animation anyway.

Two animations is not a reason to take a 16 KB dependency. The honest cost is
about 30 lines of our own code to maintain, which is shorter than the motion
table it implements. **Do not reach for Lenis or smooth-scroll**: `DESIGN.md`
forbids scroll-jacking and parallax outright.

---

## Payload reality check

The `TASKS.md` BACKLOG budget is "sub-200KB critical path", and the fonts
already consume it. Measured, latin subset only, exactly the faces `DESIGN.md`
specifies:

| File | Size |
|---|---|
| Newsreader variable, roman | 56 KB |
| Newsreader variable, italic (pull quotes) | 63 KB |
| IBM Plex Sans variable | 44 KB |
| IBM Plex Mono 400 | 14 KB |
| IBM Plex Mono 500 (only if used) | 14 KB |
| **Total** | **177–191 KB** |

All OFL-1.1, all self-hostable via `@fontsource*`. Chart client JS is 0, which
means **fonts are now 100% of the JS-adjacent payload** and the chart stack no
longer competes for the budget at all.

Sub-200KB for the *whole* critical path is still not reachable with three
faces. That fork is logged in `TASKS.md` and is independent of this decision.

One font question falls out and needs confirming: Newsreader has an optical-size
axis, and the `opsz` cut is **128 KB against 56 KB** for the `wght` cut. For a
broadsheet display face the optical cut is typographically better and the budget
does not have it. Recommend `wght`, revisit only if the budget moves.

---

## Consequences to accept

- **~150 lines of Python per chart form, written once.** Four forms, so roughly
  600 lines of build-time code to maintain. This is the real price and it buys
  traceability plus a 0.7 KB page.
- **`requirements.txt` may contain no plotting library at all**, which is the
  intended outcome. `standards.md`'s venv and pin instructions still bind the
  data pipeline (pandas for parsing AEC files), they just no longer cover the
  charts.
- **Geometry needs assertions, not eyeballing.** Two bugs surfaced in a single
  proof-of-concept, one of which silently hid a published margin. Add tests
  over tick steps and over band-segment width.
- **Chart text lives in the SVG or in the HTML?** The recommendation is that the
  SVG carries `role`, `<title>` and `<desc>`, and the caption stays in HTML
  prose where it can be edited without regenerating. Needs confirming at 0006.
- **Generated SVGs are committed.** So is the Python and the raw data. A
  regeneration that changes output must show up in a diff.
- **`index.html` becomes a generated artefact.** This is the accepted cost of
  inlining rather than `<img>`. The rule that makes it safe: **prose stays
  hand-written in a template, and only the `<svg>` blocks are injected at
  positions marked by a comment placeholder.** Nobody hand-edits a path
  coordinate, and nobody hand-edits prose inside generated markup. If the
  template is not separated from the output, this decision has quietly become
  the "transformation done by hand" problem it was chosen to avoid, and the
  whole rationale collapses. Task 0006 must establish that separation before
  writing any chart.

---

## Files this decision creates or changes

- `_tasks/0002-lock-chart-stack.md` — this file, flips to CONFIRMED on sign-off
- `TASKS.md` — mark 0002 done; 0008 narrows to label density at 320px
- `docs/data-sources.md` — no new dependency rows needed, since there is no
  third-party runtime dependency. Font rows when task 0006 vendors them.
- `docs/standards.md` — add the `var()` fill rule for generated SVG, and the
  whisker-for-isolated-band rule

## Open, and not decided here

**~~Where the charts live and how they are inlined.~~ Resolved 2026-10-03:**
inlined into `index.html` by the build, from a hand-written template with
placeholder comments. Recorded in the locked decision table above and as an
accepted consequence below. The remaining work is the template/output
separation, which belongs to task 0006.

**Re-copycheck of the right-of-reply block.** Unrelated to the stack, noted
because it is still open in `TASKS.md` BLOCKED and is publication-blocking.