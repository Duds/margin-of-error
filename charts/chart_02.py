#!/usr/bin/env python3
"""Chart 02 — at what primary vote does this party convert into seats?

Two lines on one axis, both measured against the same elected body: the
national primary vote, and seat share as seats over the number of seats the
House actually had that election. The gap between them is shaded.

Why one axis is honest here and would not be elsewhere. Both series are
percentages of one body, so a single scale compares like with like. A chart
that put vote share on one axis and a seat count on the other would be
comparing two different quantities and the visual gap would mean nothing.

Every figure is computed from data/aec_election_results.csv by charts/stats.py.
The generator holds no dataset constant, which a test enforces.

Three things this chart must not do, each of which is a live failure mode:

**Farrer 2026 is an annotation, never a point.** The party's only seat came
there, and it is tempting to draw it. It was a single division on its own
electorate, converting a high primary vote into a two-party preferred majority
there. Plotted on a national general-election series it would assert
comparability that does not exist, because a by-election has no
previous-election comparison and a denominator of one division rather than 150
or 151 seats. Its figures are read from data/aec_by_election.csv, and that file
carries `plottable_on_general_election_series = no` so the chart has to check
the flag rather than rely on remembering the rule.

**The 2004 to 2016 block is not the same measure as the years around it.** The
party polled at its lowest levels of the whole series across those five
elections, against 4.34% in 2001 and 3.08% in 2019. That is slate coverage, not
a collapse and recovery. Joining the block into a single line asserts a
continuity the data does not support, so it is drawn as a marked span with its
own note.

**The House has not always had 151 seats.** It returned 150 from 2001 to 2016
and 151 from 2019, and the share is computed against each election's own chamber
size. A single 151 would understate every earlier share by a twentieth.

Usage: python3 charts/chart_02.py
"""

import csv
import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from scales import Box, Scale, nice_domain, ticks  # noqa: E402
from stats import seat_share  # noqa: E402

DATA_CSV = ROOT / "data" / "aec_election_results.csv"
BYELECTION_CSV = ROOT / "data" / "aec_by_election.csv"

# The header above the plot carries the title, the chamber-size sentence and
# the by-election annotation, each of which wraps to a different number of
# lines at each width. The plot top is therefore not a constant either: it is
# derived from the header height for the viewport being rendered, so wrapping a
# sentence to an extra line can never push header text into the plot area.
#
# The bottom is fixed, and the canvas height is then the sum, so growing the
# header grows the figure rather than compressing the plot.
# The canvas is wider than the plot: the left gutter carries the y-axis tick
# labels, and the right gutter carries the direct labels. Measured against the
# canvas, not the plot, so a tick label is never clipped by the viewBox.
CANVAS_WIDTH = {"wide": 1072, "narrow": 420}
PLOT_LEFT_RIGHT = {"wide": (104, 1044), "narrow": (64, 404)}
PLOT_BOTTOM = {"wide": 440, "narrow": 516}
# Space below the plot for the year and percentage rows, then the footer.
# The gap is measured from the bottom of the percentage label's bounding box to
# the top of the footer's, not from baseline to baseline. At 22 units of pitch
# between the last percentage line and the first footer line the boxes still
# overlapped by 4.6 units, which only getBBox sees.
LABEL_BAND = 74
# Below the last footer line, measured from the baseline to the bottom of its
# bounding box rather than to the baseline itself. At 16px a line's box is
# about 20.5 units tall, so a tail of 18 clipped the last line by 2.5 units in
# both variants — and clipping is invisible in the SVG, only measurable.
FOOTER_TAIL = 24


def footer_lines(viewport: str, election_count: int) -> list[str]:
    """The source note, wrapped to this viewport's text column."""
    return wrap_to_width(
        f"{election_count} general elections, and no seat at any of them. "
        f"Source: AEC first preferences by party, each election's own file.",
        text_column(viewport),
        TICK,
    )


def geometry(viewport: str, blocks: dict, footer: list[str]) -> tuple[int, int, Box]:
    """Canvas size and plot box, sized from the header and footer it holds."""
    left, right = PLOT_LEFT_RIGHT[viewport]
    top = header_height(blocks)
    bottom = PLOT_BOTTOM[viewport]
    height = bottom + LABEL_BAND + (len(footer) - 1) * 22 + FOOTER_TAIL
    return (
        CANVAS_WIDTH[viewport],
        height,
        Box(left=left, right=right, top=top, bottom=bottom),
    )
# Room kept clear on the right of the text column, so a wrapped line that
# exactly fills its budget still sits inside the canvas.
TEXT_MARGIN_RIGHT = {"wide": 28, "narrow": 16}

# --- Text measurement -------------------------------------------------------
#
# Wrapping is done in user units, not characters. `textwrap.wrap` counts
# characters, but the limit that matters is the canvas width in user units, and
# at 16px IBM Plex Mono one character is 9.632 units across — measured in a
# browser with getBBox, not assumed. So a 52-character wrap needs 501 units in
# a narrow plot 356 units wide, and the line runs 145 units off the right edge.
#
# The first pass wrapped by character count and every line still overflowed,
# because a character count and a unit budget are different quantities.
CHAR_UNITS_16 = 9.632
CHAR_UNITS_18 = 10.836


def wrap_to_width(text: str, max_units: float, font_size: int) -> list[str]:
    """Wrap text so no line exceeds `max_units` user units.

    The advance width is a measured constant rather than a guess, and it
    differs by font size, so the caller states which applies.
    """
    per_char = CHAR_UNITS_18 if font_size >= 18 else CHAR_UNITS_16
    return textwrap.wrap(text, width=max(8, int(max_units // per_char))) or [text]


TITLE_TEXT = "What share of the vote, and what share of the House"


def text_column(viewport: str) -> float:
    """Width available to header and footer text, in user units."""
    left, right = PLOT_LEFT_RIGHT[viewport]
    return CANVAS_WIDTH[viewport] - left - TEXT_MARGIN_RIGHT[viewport]


def header_blocks(viewport: str, byelection: dict) -> dict:
    """Every header string, wrapped to the width available at this viewport.

    Returned rather than drawn inline so the plot box can be sized from the
    same numbers the text is drawn with. Two copies of a line count is how a
    header and a plot box disagree about where the plot starts.
    """
    budget = text_column(viewport)
    return {
        "title": wrap_to_width(TITLE_TEXT, budget, TITLE),
        "note": wrap_to_width(
            f"{byelection['division']} by-election, {byelection['year']}: one "
            f"division, {byelection['primary_pct']:g}% primary converting to "
            f"{byelection['tcp_pct']:g}% two-party preferred. Annotated, not "
            f"plotted — a by-election has its own electorate and its own "
            f"denominator.",
            budget,
            TICK,
        ),
    }


def header_height(blocks: dict) -> int:
    """Vertical space the header needs, in user units.

    Same arithmetic as the layout code, so the plot box is positioned from the
    text rather than from a remembered number.
    """
    return (
        TITLE_BLOCK_TOP
        + len(blocks["title"]) * 26
        + 4
        + 21  # the chamber sentence, drawn inline
        + 12
        + len(blocks["note"]) * 21
        + 30  # clearance between the last header line and the plot
    )


def geometry(viewport: str, blocks: dict, footer: list[str]) -> tuple[int, int, Box]:
    """Canvas size and plot box, sized from the header and footer it holds."""
    left, right = PLOT_LEFT_RIGHT[viewport]
    top = header_height(blocks)
    bottom = PLOT_BOTTOM[viewport]
    height = bottom + LABEL_BAND + (len(footer) - 1) * 22 + FOOTER_TAIL
    return (
        CANVAS_WIDTH[viewport],
        height,
        Box(left=left, right=right, top=top, bottom=bottom),
    )


# The low-coverage block. Years are inclusive, and the values are stated so a
# test can assert the annotation and the shaded span agree.
THIN_COVERAGE_FROM = 2004
THIN_COVERAGE_TO = 2016

TICK = 16
STRONG = 17
VALUE = 19
TITLE = 18

# Where the header block starts, measured down from the top of the canvas. The
# header is laid out top-down from here and the plot sits below whatever it
# ends up needing, so wrapping a sentence to a second line cannot push text
# into the plot area.
TITLE_BLOCK_TOP = 34


def load() -> list[dict]:
    """Every election, with seat share recomputed from its own chamber size."""
    rows: list[dict] = []
    with DATA_CSV.open(encoding="utf-8", newline="") as fh:
        for raw in csv.DictReader(fh):
            seats = int(raw["seats_won"])
            chamber = int(raw["chamber_size"])
            rows.append(
                {
                    "year": int(raw["election_year"]),
                    "primary_pct": float(raw["primary_vote_pct"]),
                    "seats": seats,
                    "chamber": chamber,
                    "seat_pct": seat_share(seats, chamber) * 100,
                }
            )
    if not rows:
        raise SystemExit(
            "no elections in the ingested CSV; the chart would draw an empty "
            "axis. Run python3 tools/ingest_aec_seats.py first."
        )
    rows.sort(key=lambda r: r["year"])
    return rows


def load_byelection() -> dict:
    """The one by-election, read from its own file.

    Kept out of the general-election CSV on purpose. It is a different kind of
    event on a different denominator, and a shared file would invite exactly
    the comparison this chart must not make. The row carries
    `plottable_on_general_election_series = no`, and the chart reads the flag
    rather than trusting itself to remember.
    """
    with BYELECTION_CSV.open(encoding="utf-8", newline="") as fh:
        row = next(csv.DictReader(fh))

    if (row.get("event_type") or "").strip() != "by_election":
        raise SystemExit(
            f"{BYELECTION_CSV.name}: expected a by_election row, found "
            f"{row.get('event_type')!r}. Refusing to plot it as a "
            f"general election."
        )
    if (row.get("plottable_on_general_election_series") or "").strip() != "no":
        raise SystemExit(
            f"{BYELECTION_CSV.name}: a by-election may not be marked plottable "
            f"on the general-election series."
        )
    return {
        "year": int(row["election_year"]),
        "division": (row["division"] or "").strip(),
        "primary_pct": float(row["primary_vote_pct"]),
        "tcp_pct": float(row["two_party_preferred_pct"]),
    }


def step_for_height(span: float, height: float, label_px: float = TICK) -> float:
    """The coarsest tick step whose labels still fit the space available.

    Picking the step from the data range alone puts nine ticks in 76px. The
    count of intervals is capped by panel height, then the first "nice" value
    at or above what that cap requires is used.
    """
    if span <= 0:
        return 1.0
    max_intervals = max(1, int(height // (label_px * 1.6)))
    needed = span / max_intervals
    for candidate in (0.5, 1, 2, 2.5, 5, 10):
        if candidate >= needed:
            return candidate
    return 50.0


def render(viewport: str, panels: dict) -> str:
    blocks = header_blocks(viewport, panels["byelection"])
    footer = footer_lines(viewport, len(panels["elections"]))
    w, h, plot = geometry(viewport, blocks, footer)
    narrow = viewport == "narrow"
    rows = panels["elections"]

    # Every source this figure rests on, declared on the figure. The build
    # resolves each id against the registry, so a chart that quietly drops a
    # source stops passing. 2001 is listed separately because it comes from the
    # official statistics ZIP rather than a per-election CSV, and the
    # by-election because its figures are annotated on the figure.
    source_ids = (
        ["aec-hor-2025-fp-by-party", "aec-hor-2001-fp-by-party",
         "aec-hor-2025-party-rep", "aec-by-farrer-2026"]
    )

    top_vote = max(r["primary_pct"] for r in rows)
    step = step_for_height(top_vote * 1.12, plot.height)
    v_lo, v_hi = nice_domain(0, top_vote * 1.12, step)
    y = Scale(d0=v_lo, d1=v_hi, r0=plot.bottom, r1=plot.top)
    tick_values = [v for v in ticks(v_lo, v_hi, step) if v_lo <= v <= v_hi]

    n = len(rows)
    slot = plot.width / n

    def x_of(i: int) -> float:
        return plot.left + slot * (i + 0.5)

    thin_idx = [
        i for i, r in enumerate(rows)
        if THIN_COVERAGE_FROM <= r["year"] <= THIN_COVERAGE_TO
    ]
    thin_span = (
        (x_of(thin_idx[0]) - slot / 2, x_of(thin_idx[-1]) + slot / 2)
        if thin_idx
        else None
    )

    out: list[str] = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'class="chart" role="img" '
        f'aria-labelledby="chart-02-title chart-02-desc" '
        f'data-source-id="{" ".join(source_ids)}" '
        f'font-family="IBM Plex Mono, ui-monospace, monospace" '
        f'style="aspect-ratio: {w} / {h}; font-variant-numeric: tabular-nums">'
    )
    out.append(
        '<title id="chart-02-title">National primary vote and share of the '
        'House held, federal elections 2001 to 2025</title>'
    )
    out.append(f'<desc id="chart-02-desc">{desc_text(rows)}</desc>')
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
        "</defs>"
    )

    # Header, laid out top-down from TITLE_BLOCK_TOP. The wrapped strings come
    # from header_blocks(), which also sized the plot box, so the header cannot
    # grow into the plot. A label's bounding box is about 1.28x its font size,
    # so baselines need roughly 26 units of pitch at 16px and 30 at 18px;
    # anything tighter overlaps once measured rather than assumed.
    small_chamber = min(r["chamber"] for r in rows)
    large_chamber = max(r["chamber"] for r in rows)
    first_large = next(r["year"] for r in rows if r["chamber"] == large_chamber)
    last_small = max(r["year"] for r in rows if r["chamber"] == small_chamber)
    subtitle_lines = wrap_to_width(
        f"Seat share is over the {small_chamber}-seat House from "
        f"{rows[0]['year']} to {last_small}, and the {large_chamber}-seat House "
        f"from {first_large}.",
        text_column(viewport),
        TICK,
    )

    y_cursor = TITLE_BLOCK_TOP
    for line in blocks["title"]:
        out.append(
            f'<text x="{plot.left}" y="{y_cursor}" font-size="{TITLE}" '
            f'fill="var(--color-ink)">{line}</text>'
        )
        y_cursor += 26
    y_cursor += 4
    for line in subtitle_lines:
        out.append(
            f'<text x="{plot.left}" y="{y_cursor}" font-size="{TICK}" '
            f'fill="var(--color-ink-muted)">{line}</text>'
        )
        y_cursor += 21
    y_cursor += 12
    note_top = y_cursor

    # Thin-coverage block, drawn behind everything. A band of coverage, not a
    # band of uncertainty: it marks where the slate was thinner, so the dip is
    # not read as the party losing and regaining ground.
    if thin_span:
        lo_x, hi_x = thin_span
        out.append(
            f'<rect x="{lo_x:.1f}" y="{plot.top:.1f}" '
            f'width="{hi_x - lo_x:.1f}" height="{plot.height:.1f}" '
            f'fill="var(--color-rule)" opacity="0.10" />'
        )

    for tv in tick_values:
        ty = y(tv)
        is_zero = abs(tv) < 1e-9
        out.append(
            f'<line x1="{plot.left}" y1="{ty:.1f}" x2="{plot.right}" '
            f'y2="{ty:.1f}" stroke="var(--color-rule)" '
            f'stroke-width="{2 if is_zero else 1}" '
            f'stroke-dasharray="{"none" if is_zero else "2 4"}" />'
        )
        out.append(
            f'<text x="{plot.left - 10}" y="{ty + 4:.1f}" font-size="{TICK}" '
            f'text-anchor="end" fill="var(--color-ink-muted)">{tv:g}%</text>'
        )

    # The gap between the two series. The seat line is flat at zero across the
    # whole span, so this shades the area between the vote line and the axis.
    for i, r in enumerate(rows):
        cx = x_of(i)
        half = slot / 2
        vote_y = y(r["primary_pct"])
        seat_y = y(r["seat_pct"])
        out.append(
            f'<polygon points="{cx - half:.1f},{seat_y:.1f} '
            f'{cx + half:.1f},{seat_y:.1f} '
            f'{cx + half:.1f},{vote_y:.1f} '
            f'{cx - half:.1f},{vote_y:.1f}" '
            f'fill="var(--band-hatch)" stroke="none" />'
        )

    seat_points = " ".join(
        f"{x_of(i):.1f},{y(r['seat_pct']):.1f}" for i, r in enumerate(rows)
    )
    vote_points = " ".join(
        f"{x_of(i):.1f},{y(r['primary_pct']):.1f}" for i, r in enumerate(rows)
    )
    out.append(
        f'<polyline points="{seat_points}" fill="none" '
        f'stroke="var(--color-ink)" stroke-width="2.5" />'
    )
    out.append(
        f'<polyline points="{vote_points}" fill="none" '
        f'stroke="var(--color-ink)" stroke-width="2.5" />'
    )

    # Per-point labels. Wide has room for all nine; narrow has room for the
    # endpoints only, because a 16px year label is wider than a narrow slot.
    #
    # This was a set of indices, not a set of pairs. Written as `[(0, n-1)]`
    # the membership test `i not in labelled` is never true, so every label was
    # silently skipped and the wide chart lost all eighteen of them while still
    # passing every overlap check — there was nothing left to overlap.
    labelled = {0, len(rows) - 1} if narrow else set(range(len(rows)))
    for i, r in enumerate(rows):
        cx = x_of(i)
        out.append(
            f'<circle cx="{cx:.1f}" cy="{y(r["primary_pct"]):.1f}" r="5" '
            f'fill="var(--color-ink)" />'
        )
        out.append(
            f'<circle cx="{cx:.1f}" cy="{y(r["seat_pct"]):.1f}" r="5" '
            f'fill="var(--color-ink)" />'
        )
        if i not in labelled:
            continue
        anchor = "middle"
        tx = cx
        if narrow and i == 0:
            anchor, tx = "start", plot.left - 4
        elif narrow and i == len(rows) - 1:
            anchor, tx = "end", plot.right + 4
        out.append(
            f'<text x="{tx:.1f}" y="{plot.bottom + 26}" font-size="{TICK}" '
            f'text-anchor="{anchor}" fill="var(--color-ink-muted)">'
            f'{r["year"]}</text>'
        )
        out.append(
            f'<text x="{tx:.1f}" y="{plot.bottom + 48}" font-size="{TICK}" '
            f'text-anchor="{anchor}" fill="var(--color-ink-muted)">'
            f'{r["primary_pct"]:g}%</text>'
        )

    # Direct labels instead of a legend, per DESIGN.md.
    #
    # Measured, not eyeballed. Three attempts on the wide variant, each caught
    # by getBBox:
    #   1. Above the final point — collided with the by-election note.
    #   2. In the left gutter, text-anchor="end" — ran to x=-28.8, off the
    #      canvas, because "primary vote" is wider than the 94-unit gutter.
    #   3. Same gutter, anchor="start" — sat on top of the y-axis tick labels.
    #
    # What works on wide is inside the plot, left-aligned just right of the
    # axis, in a band above the highest data point: the axis ceiling carries
    # headroom over the peak, so there is genuine empty space there.
    #
    # Narrow is a different problem and gets a different answer. Nine elections
    # across the narrow plot is 37.8 units per slot, and a "2001" label at 16px
    # monospace is about 38 units wide, so per-point labels cannot fit at any
    # size the label floor allows. Rather than rotate them or drop below the
    # floor, the narrow variant labels the endpoints only and drops the
    # per-point percentages; every figure is in the desc and in the page's
    # data, which is what the accessibility tree reads anyway.
    label_x = plot.left + 12
    if narrow:
        out.append(
            f'<text x="{plot.left + 4:.1f}" y="{y(rows[0]["primary_pct"]) - 18:.1f}" '
            f'font-size="{STRONG}" text-anchor="start" '
            f'fill="var(--color-ink)">primary vote</text>'
        )
        out.append(
            f'<text x="{plot.left + 4:.1f}" y="{y(0) - 14:.1f}" '
            f'font-size="{STRONG}" text-anchor="start" '
            f'fill="var(--color-ink)">seats won</text>'
        )
    else:
        out.append(
            f'<text x="{label_x:.1f}" y="{plot.top + 26:.1f}" '
            f'font-size="{STRONG}" text-anchor="start" '
            f'fill="var(--color-ink)">primary vote</text>'
        )
        out.append(
            f'<text x="{label_x:.1f}" y="{y(0) - 14:.1f}" '
            f'font-size="{STRONG}" text-anchor="start" '
            f'fill="var(--color-ink)">seats won</text>'
        )

    # The by-election. Labelled text, never a marker on either series: it was a
    # single division on its own electorate, so it has no place on a national
    # series drawn against 150 or 151 seats. Every figure is read from
    # data/aec_by_election.csv, not typed.
    #
    # Placed in the header band above the plot rather than inside it. The first
    # pass set it at plot.top+18, which put the 2025 point's label at the same
    # height: the note has three lines and the vote line peaks on the right,
    # so wherever the note sits inside the plot something on the line collides
    # with it. Above the plot there is nothing to collide with.
    #
    # It starts below the title's bounding box, not below its baseline. At 18px
    # the title box is about 23px tall, so title_y - 14 lands inside it.
    for i, line in enumerate(blocks["note"]):
        out.append(
            f'<text x="{plot.left}" y="{note_top + i * 21:.1f}" '
            f'font-size="{TICK}" fill="var(--color-ink-muted)">{line}</text>'
        )

    if thin_span and not narrow:
        # Not on narrow: the shaded block is still drawn, but the caption
        # collided with the "seats won" label there, and the block is explained
        # in the desc either way.
        out.append(
            f'<text x="{(thin_span[0] + thin_span[1]) / 2:.1f}" '
            f'y="{plot.bottom - 14:.1f}" font-size="{TICK}" '
            f'text-anchor="middle" fill="var(--color-ink-muted)">'
            f'thinner slate</text>'
        )

    # Positioned from the label band below the plot, not from the canvas
    # height. Anchoring to h - 16 assumed a fixed tail, which held only while
    # the header was one line shorter; when the narrow header grew, the footer
    # rose into the endpoint labels and getBBox found five overlaps. The band
    # below the plot is the thing that has to stay clear.
    footer_y = plot.bottom + LABEL_BAND
    for i, line in enumerate(footer):
        out.append(
            f'<text x="{plot.left}" y="{footer_y + i * 22}" font-size="{TICK}" '
            f'fill="var(--color-ink-muted)">{line}</text>'
        )

    out.append("</svg>")
    return "\n".join(out)


def desc_text(rows: list[dict]) -> str:
    small = min(r["chamber"] for r in rows)
    large = max(r["chamber"] for r in rows)
    first_large = next(r["year"] for r in rows if r["chamber"] == large)
    parts = [
        f"In {r['year']} the party recorded {r['primary_pct']:g} per cent of "
        f"the primary vote and won {r['seats']} of {r['chamber']} seats."
        for r in rows
    ]
    return (
        f"A line chart over {len(rows)} Australian federal general elections "
        f"from {rows[0]['year']} to {rows[-1]['year']}. The upper line is the "
        f"party's national primary vote share. The lower line is its share of "
        f"the House, which is zero at every one of these elections, so the "
        f"hatched band between the two lines is the entire distance between "
        f"vote share and seat share. " + " ".join(parts) + f" The House "
        f"returned {small} seats to {first_large - 3} and {large} from "
        f"{first_large}, and each share is computed against the chamber size for "
        f"its own election rather than a single figure. The shaded block marks "
        f"{THIN_COVERAGE_FROM} to {THIN_COVERAGE_TO}, where the party contested "
        f"far fewer divisions and the figures are not the same measure as the "
        f"years either side. The party's only seat came at the Farrer "
        f"by-election in 2026, which is not plotted: a by-election covers one "
        f"division on its own electorate rather than the whole House."
    )


def build_panels() -> dict:
    """Every number the chart will draw, computed once."""
    return {"elections": load(), "byelection": load_byelection()}


def main() -> int:
    panels = build_panels()
    for viewport in ("wide", "narrow"):
        svg = render(viewport, panels)
        name = f"chart-02{'-narrow' if viewport == 'narrow' else ''}.svg"
        (HERE / name).write_text(svg, encoding="utf-8")
        print(f"wrote {name} ({len(svg.encode('utf-8')):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
