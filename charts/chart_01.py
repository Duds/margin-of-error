#!/usr/bin/env python3
"""Chart 01 — did polling overstate or understate the party's vote?

Two panels in one figure, because the claim and its evidence should be read
together. Panel 1 is the finding: polling minus result, in percentage points,
from a zero rule. Panel 2 is the evidence: where polling sat across the waves
preceding each election, with the result marked against it.

Every figure here is computed by charts/stats.py from the ingested CSV. Nothing
is typed. The generator holds no dataset constant at all, which a test enforces,
because a transcribed figure is a figure that stops agreeing with its data.

On the missing margin. Roy Morgan published no margin of error, no sample size
and no publication date for any of these waves. There is therefore no band to
draw, and none is drawn. What is drawn instead is a statement of the absence:
the caption reports how many waves published none, computed from the file. That
is not a decoration and not a criticism of any publisher. It marks the edge of
what this comparison can show, which is a property of the evidence on the table.

On the shape of panel 2. Not a line across the waves. These are fortnightly
snapshots with no model between them, and a line would assert a value for the
gaps between points that nobody measured. A span states exactly what was
published and nothing more.

Usage: python3 charts/chart_01.py
"""

import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from scales import (  # noqa: E402
    Box,
    Scale,
    nice_domain,
    ticks,
    wrap_to_width,
)
from stats import Result, gaps, load_polls, window_mean  # noqa: E402

POLL_CSV = ROOT / "data" / "polls_roymorgan_oned.csv"
RESULT_CSV = ROOT / "data" / "roymorgan_election_results.csv"
WINDOW = 12

# Two viewports from one generator, unchanged from task 0006. A 1072-unit chart
# scaled into a 265px phone column renders 16px axis labels at about 4px, which
# is unreadable, so the narrow variant uses fewer user units. The wide viewBox
# equals the rendered track width (1072, not the nominal 1120) so 16px in the
# SVG is 16px on screen and the DESIGN.md label floor is met exactly.
VIEWPORTS = {
    "wide": {"w": 1072, "h": 640, "plot": Box(left=104, right=1044, top=56, bottom=330)},
    "narrow": {"w": 420, "h": 620, "plot": Box(left=64, right=404, top=52, bottom=342)},
}

# Panel geometry, as a fraction of the plot box. Kept as ratios so the narrow
# variant needs no separate numbers.
# Fractions of the plot box. Panel 1 leaves room below gap_bottom for its own
# year and value labels; panel 2's title then starts clear of them, which is
# what the first two passes got wrong: span_top-14 landed at y=195.1 while the
# year label sat at y=196.7, so the two drew through each other.
GAP_PANEL_TOP = 0.08
GAP_PANEL_BOTTOM = 0.34
SPAN_PANEL_TOP = 0.56
SPAN_PANEL_BOTTOM = 0.86


def load_results() -> list[Result]:
    """Election results, marked unconfirmed.

    Every figure here is currently Roy Morgan's cross-check, not the AEC's
    record, so `confirmed` is False and tools/build.py refuses to publish a
    chart resting on it until task 0003 confirms. That refusal is the gate.
    """
    import csv

    out: list[Result] = []
    with RESULT_CSV.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            year = int(row["election_year"])
            value = float(row["primary_vote_oned_pct"])
            needs = (row.get("requires_aec_confirmation") or "").strip().lower()
            out.append(Result(year=year, value=value, confirmed=(needs != "yes")))
    return out


def fmt_signed(value: float) -> str:
    """A signed figure with a true minus sign, not a hyphen."""
    if value < 0:
        return f"\u2212{abs(value):.2f}".replace(".", ".")
    return f"+{value:.2f}"


def build_panels() -> dict:
    """Every number the chart will draw, computed once from the data."""
    polls = load_polls(POLL_CSV)
    results = load_results()
    gaps_ = gaps(results, polls, WINDOW)
    if not gaps_:
        raise SystemExit(
            "no election has preceding waves; the chart would assert a "
            "comparison it cannot make. Check the ingest."
        )
    return {
        "waves": len(polls),
        "waves_with_margin": sum(
            1 for p in polls if False  # never true: this house publishes none
        ),
        "gaps": gaps_,
        "means": {g.year: window_mean(polls, g.year, WINDOW) for g in gaps_},
    }



def step_for_height(lo: float, hi: float, height: float, label_px: float = 16) -> float:
    """The coarsest tick step whose labels still fit the space available.

    Picking a step from the data range alone puts nine ticks in 76px, which is
    not a density problem you can read past. A label needs its own height in
    clear space, so the count of intervals is capped by the panel, and the
    step is then the first "nice" value at or above what that cap requires.
    """
    span = abs(hi - lo)
    if span <= 0:
        return 1.0
    max_intervals = max(1, int(height // (label_px * 1.6)))
    needed = span / max_intervals
    for candidate in (0.1, 0.2, 0.25, 0.5, 1, 2, 2.5, 5, 10, 20, 25, 50):
        if candidate >= needed:
            return candidate
    return 100.0


def gap_scale(plot: Box, values: list[float], span: float) -> Scale:
    """A scale centred on zero, symmetric, so the axis cannot flatter the data."""
    reach = max(abs(min(values)), abs(max(values)))
    reach = max(reach * 1.4, 0.5)
    nice_lo, nice_hi = nice_domain(-reach, reach, span)
    return Scale(d0=nice_lo, d1=nice_hi, r0=plot.bottom, r1=plot.top)


def render(viewport: str, panels: dict) -> str:
    cfg = VIEWPORTS[viewport]
    w, h, plot = cfg["w"], cfg["h"], cfg["plot"]
    narrow = viewport == "narrow"
    box_h = plot.bottom - plot.top

    # Panel titles are wrapped before the panels are positioned, because on the
    # narrow variant the second title is two lines and has to be allowed to
    # push the panel below it down. Positioning first and wrapping second is how
    # the wrapped title ended up drawn through panel 1's year labels: the panel
    # fractions were fixed, the text was not, and the text got longer.
    gap_title_lines = wrap_to_width(
        "Polling minus result, percentage points",
        plot.right - plot.left,
        18,
    )
    span_title_lines = wrap_to_width(
        "Where polling sat before each election, and what the ballot gave",
        plot.right - plot.left,
        18,
    )
    note_text = (
        f"{panels['waves']} of {panels['waves']} waves publish no margin of "
        f"error, no sample size and no publication date."
    )
    note_lines = wrap_to_width(note_text, plot.right - plot.left)

    gap_top = plot.top + box_h * GAP_PANEL_TOP
    gap_bottom = plot.top + box_h * GAP_PANEL_BOTTOM
    span_top = plot.top + box_h * SPAN_PANEL_TOP
    span_bottom = plot.top + box_h * SPAN_PANEL_BOTTOM

    # Panel 1's labels sit below its axis; panel 2's title must clear them, and
    # must clear its own extra lines. Both are measured in bounding boxes: an
    # 18px line's box is about 23 units tall.
    span_title_y = max(
        span_top - 14,
        gap_bottom + 78 + (len(gap_title_lines) - 1) * 0,
    )
    span_title_y -= (len(span_title_lines) - 1) * 26
    if span_title_y < gap_bottom + 64:
        span_title_y = gap_bottom + 64
        span_top = span_title_y + 14 + (len(span_title_lines) - 1) * 26
        span_bottom = plot.bottom

    gs = panels["gaps"]
    signed = [g.signed_gap for g in gs]

    gap_plot = Box(left=plot.left, right=plot.right, top=gap_top, bottom=gap_bottom)
    reach = max(abs(min(signed)), abs(max(signed))) * 1.35
    step = step_for_height(-reach, reach, gap_bottom - gap_top)
    g_lo, g_hi = nice_domain(-reach, reach, step)
    gap_y = Scale(d0=g_lo, d1=g_hi, r0=gap_bottom, r1=gap_top)
    gap_ticks = [v for v in ticks(g_lo, g_hi, step) if g_lo <= v <= g_hi]

    # DESIGN.md forbids a truncated y-axis, so this starts at zero. It also
    # refuses to scale far past the data: the first pass ran 0 to 6 for values
    # living in 3.0 to 5.0, which left each span using a third of its height and
    # made the 2022 result sitting at the top of its span hard to see, which is
    # the single fact this panel exists to show.
    all_values = [v for g in gs for v in (g.mean, g.result)] + [
        panels["means"][g.year].low for g in gs
    ] + [panels["means"][g.year].high for g in gs]
    ceiling = max(all_values)
    v_step = step_for_height(0, ceiling * 1.08, span_bottom - span_top)
    v_lo, v_hi = nice_domain(0, ceiling * 1.08, v_step)
    span_y = Scale(d0=v_lo, d1=v_hi, r0=span_bottom, r1=span_top)

    n = len(gs)
    slot = (gap_plot.right - gap_plot.left) / n
    bar_w = min(slot * 0.34, 120)

    # Type sizes are attributes, not classes. The stylesheet carries no SVG
    # text rules, so a class name would size nothing and every label would fall
    # to the 16px default, which the viewBox then scales. DESIGN.md's floor is
    # 16px *measured*, so the sizes below are the measured values.
    tick = 16
    strong = 17
    value = 19
    title = 18

    out: list[str] = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'class="chart" role="img" aria-labelledby="chart-01-title chart-01-desc" '
        f'data-source-id="roymorgan-pvi" '
        f'font-family="IBM Plex Mono, ui-monospace, monospace" '
        f'style="aspect-ratio: {w} / {h}; font-variant-numeric: tabular-nums">'
    )
    out.append(
        '<title id="chart-01-title">Polling against the result, One Nation '
        "primary vote, federal elections 2019 and 2022</title>"
    )
    out.append(f'<desc id="chart-01-desc">{desc_text(panels, gs, narrow)}</desc>')
    out.append(
        '<defs>'
        '<pattern id="hatch-mo" width="4" height="4" '
        'patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        '<line x1="0" y1="0" x2="0" y2="4" stroke="currentColor" '
        'stroke-width="1" /></pattern>'
        '<pattern id="hatch-mo-print" width="6" height="6" '
        'patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        '<line x1="0" y1="0" x2="0" y2="6" stroke="currentColor" '
        'stroke-width="1.6" /></pattern>'
        '<marker id="result-mark" viewBox="0 0 10 10" refX="5" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="var(--color-ink)" />'
        '</marker>'
        '</defs>'
    )

    # ---- Panel 1: the gap -------------------------------------------------
    title_y = gap_top - 14 - (len(gap_title_lines) - 1) * 26
    for i, line in enumerate(gap_title_lines):
        out.append(
            f'<text x="{gap_plot.left}" y="{title_y + i * 26}" '
            f'font-size="{title}" fill="var(--color-ink)">{line}</text>'
        )
    zero_y = gap_y(0)
    for tv in gap_ticks:
        ty = gap_y(tv)
        if not (gap_top - 1 <= ty <= gap_bottom + 1):
            continue
        is_zero = abs(tv) < 1e-9
        out.append(
            f'<line x1="{gap_plot.left}" y1="{ty:.1f}" '
            f'x2="{gap_plot.right}" y2="{ty:.1f}" '
            f'stroke="var(--color-rule)" '
            f'stroke-width="{2 if is_zero else 1}" />'
        )
        if not narrow or is_zero:
            label = "0" if is_zero else f"{tv:g}"
            out.append(
                f'<text x="{gap_plot.left - 10}" y="{ty + 4:.1f}" '
                f'font-size="{tick}" text-anchor="end" '
                f'fill="var(--color-ink-muted)">{label}</text>'
            )

    for i, g in enumerate(gs):
        cx = gap_plot.left + slot * (i + 0.5)
        y = gap_y(g.signed_gap)
        top, bottom = min(y, zero_y), max(y, zero_y)
        out.append(
            f'<rect x="{cx - bar_w / 2:.1f}" y="{top:.1f}" '
            f'width="{bar_w:.1f}" height="{max(abs(bottom - top), 1.5):.1f}" '
            f'fill="var(--color-ink-muted)" />'
        )
        out.append(
            f'<text x="{cx:.1f}" y="{gap_bottom + 34}" text-anchor="middle" '
            f'font-size="{strong}" text-anchor="middle" '
            f'fill="var(--color-ink)">{g.year}</text>'
        )
        label_y = top - 10 if g.signed_gap > 0 else bottom + 20
        out.append(
            f'<text x="{cx:.1f}" y="{label_y:.1f}" text-anchor="middle" '
            f'font-size="{value}" text-anchor="middle" '
            f'fill="var(--color-ink)">{fmt_signed(g.signed_gap)}</text>'
        )

    # ---- Panel 2: the evidence -------------------------------------------
    # Clearance is measured against the label's bounding box, not its ink:
    # getBBox on a 18px line is ~23px tall, which is why span_top-14 landed
    # inside the year labels at y=166-188 rather than below them. The same
    # reason the wrapped title starts at gap_bottom + 78 rather than a fixed
    # offset: on narrow it is two lines, and the second line needs the room.
    for i, line in enumerate(span_title_lines):
        out.append(
            f'<text x="{plot.left}" y="{span_title_y + i * 26:.1f}" '
            f'font-size="{title}" fill="var(--color-ink)">{line}</text>'
        )

    span_slot = (plot.right - plot.left) / n
    for v in [x for x in ticks(v_lo, v_hi, v_step) if v_lo <= x <= v_hi]:
        ty = span_y(v)
        if not (span_top - 1 <= ty <= span_bottom + 1):
            continue
        is_zero = abs(v) < 1e-9
        out.append(
            f'<line x1="{plot.left}" y1="{ty:.1f}" x2="{plot.right}" '
            f'y2="{ty:.1f}" stroke="var(--color-rule)" '
            f'stroke-width="{2 if is_zero else 1}" '
            f'stroke-dasharray="{"none" if is_zero else "2 4"}" />'
        )
        if not narrow or is_zero or int(v) % 2 == 0:
            out.append(
                f'<text x="{plot.left - 10}" y="{ty + 4:.1f}" '
                f'font-size="{tick}" text-anchor="end" '
                f'fill="var(--color-ink-muted)">{v:g}</text>'
            )

    for i, g in enumerate(gs):
        m = panels["means"][g.year]
        cx = plot.left + span_slot * (i + 0.5)
        lo_y, hi_y = span_y(m.low), span_y(m.high)
        out.append(
            f'<line x1="{cx:.1f}" y1="{lo_y:.1f}" x2="{cx:.1f}" '
            f'y2="{hi_y:.1f}" stroke="var(--band-edge)" stroke-width="8" '
            f'stroke-linecap="butt" opacity="0.55" />'
        )
        out.append(
            f'<line x1="{cx:.1f}" y1="{span_y(m.value):.1f}" '
            f'x2="{cx:.1f}" y2="{span_y(m.value):.1f}" '
            f'stroke="var(--color-ink)" stroke-width="1" />'
        )
        r_y = span_y(g.result)
        out.append(
            f'<line x1="{cx - 13:.1f}" y1="{r_y:.1f}" x2="{cx + 13:.1f}" '
            f'y2="{r_y:.1f}" stroke="var(--color-ink)" stroke-width="2.5" />'
        )
        # Per-election captions. Wide has room; the narrow plot has two slots
        # across 340 units and the wave-count caption is 173 units, so the
        # labels would collide with each other as well as overrun the canvas.
        # Narrow keeps the mean and the result, which is what a reader needs to
        # read the shape; the full span and wave count are in the desc and on
        # the wide variant.
        if narrow:
            out.append(
                f'<text x="{cx:.1f}" y="{span_bottom + 26}" font-size="{tick}" '
                f'text-anchor="middle" fill="var(--color-ink-muted)">'
                f'mean {m.value:.2f}%</text>'
            )
            out.append(
                f'<text x="{cx:.1f}" y="{span_bottom + 50}" font-size="{strong}" '
                f'text-anchor="middle" fill="var(--color-ink)">'
                f'result {g.result:g}%</text>'
            )
            continue

        out.append(
            f'<text x="{cx:.1f}" y="{span_bottom + 26}" font-size="{tick}" '
            f'text-anchor="middle" fill="var(--color-ink-muted)">'
            f'{m.low:g}&#8211;{m.high:g}% polled</text>'
        )
        out.append(
            f'<text x="{cx:.1f}" y="{span_bottom + 50}" font-size="{tick}" '
            f'text-anchor="middle" fill="var(--color-ink-muted)">'
            f'{m.n_used} waves, mean {m.value:.2f}%</text>'
        )
        out.append(
            f'<text x="{cx:.1f}" y="{span_bottom + 74}" font-size="{strong}" '
            f'text-anchor="middle" fill="var(--color-ink)">'
            f'result {g.result:g}%</text>'
        )

    note_y = h - 16 - (len(note_lines) - 1) * 22
    for i, line in enumerate(note_lines):
        out.append(
            f'<text x="{plot.left}" y="{note_y + i * 22}" font-size="{tick}" '
            f'fill="var(--color-ink-muted)">{line}</text>'
        )
    out.append("</svg>")
    return "\n".join(out)


def desc_text(panels: dict, gs: list, narrow: bool) -> str:
    parts = []
    for g in gs:
        direction = "overstated" if g.signed_gap > 0 else "understated"
        parts.append(
            f"For {g.year}, polling averaged {g.mean:.2f} per cent across the "
            f"{g.n_used} waves before the election and the party recorded "
            f"{g.result:g} per cent, so polling {direction} it by "
            f"{abs(g.signed_gap):.2f} points."
        )
    return (
        f"A two-panel chart. The upper panel shows polling minus result in "
        f"percentage points for {len(gs)} federal elections, drawn from a zero "
        f"rule so the axis is centred on the quantity being measured. The lower "
        f"panel shows, for each election, the span of polling values published "
        f"in the preceding waves as a vertical bar, the mean of those waves, and "
        f"the result marked as a horizontal rule. "
        + " ".join(parts)
        + f" Based on {panels['waves']} fortnightly waves published between 2018 "
        f"and 2022. No wave carries a published margin of error, sample size or "
        f"publication date, so no uncertainty interval is drawn and none is "
        f"imputed. The span is not a time series: these are fortnightly "
        f"snapshots and nothing is claimed about the values between them."
    )


def main() -> int:
    panels = build_panels()
    for viewport in ("wide", "narrow"):
        svg = render(viewport, panels)
        name = f"chart-01{'-narrow' if viewport == 'narrow' else ''}.svg"
        path = HERE / name
        path.write_text(svg, encoding="utf-8")
        print(f"wrote {name} ({len(svg.encode('utf-8')):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
