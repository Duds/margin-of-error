#!/usr/bin/env python3
"""Chart 01 placeholder generator, written to prove the shell, not to publish.

IMPORTANT: the figures below are PLACEHOLDER values carried over from the
discarded prototype. They are NOT sourced. docs/data-sources.md has no entry
for them and they must never be published. Task 0007 replaces this file once
the AEC series (0003) and the polling dataset (0004) exist.

What this file is for: exercising the build, the template injection, the
whisker fix for single-poll bands, and the narrow-viewport variant. It is the
smallest thing that proves the pipeline end to end.

Emits two charts from one pass of the data:
  chart-01.svg       1120px breakout track
  chart-01-narrow.svg  420px mobile, where labels must stay at 16px

Usage: python3 charts/chart_01.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scales import (  # noqa: E402
    Box,
    Scale,
    assert_no_degenerate_bands,
    band_runs,
    nice_domain,
    ticks,
)

# Two viewports from one generator. A 1120px chart scaled into a 265px column
# renders 16px axis labels at about 3.8px, which is unreadable. DESIGN.md sets a
# 1120px breakout track and a 16px label floor, and those two rules collide at
# mobile widths. Rather than break either, the narrow variant uses fewer user
# units, so 16px in a 420px viewBox stays legible at a 265px render.
# The wide viewBox is 1072 user units, not 1120. 1120 is the DESIGN.md track,
# and the track carries 24px of inline padding each side, so the chart's own
# box is 1072. Sizing the viewBox to the render width means 16px in the SVG is
# 16px on screen, so the DESIGN.md axis-label floor is met exactly rather than
# approximately. Measured: a 1120 viewBox in a 1072 box rendered labels at
# 15.3px, under the floor.
VIEWPORTS = {
    "wide": {"w": 1072, "h": 520, "plot": Box(left=92, right=1044, top=32, bottom=440)},
    "narrow": {"w": 420, "h": 460, "plot": Box(left=52, right=404, top=28, bottom=392)},
}

# PLACEHOLDER. Not sourced. See module docstring.
SERIES = [
    {"x": 1996, "est": 0.060, "lo": 0.045, "hi": 0.075},
    {"x": 1998, "est": 0.090, "lo": None, "hi": None},
    {"x": 2001, "est": 0.045, "lo": 0.030, "hi": 0.060},
    {"x": 2004, "est": 0.065, "lo": 0.050, "hi": 0.080},
]

X0, X1 = 1996, 2004
Y0, Y1, STEP = 0.0, 0.10, 0.02


def scales_for(viewport: str) -> tuple[Scale, Scale, list[float]]:
    cfg = VIEWPORTS[viewport]
    plot = cfg["plot"]
    x_of = Scale(d0=X0, d1=X1, r0=plot.left, r1=plot.right)
    y_of = Scale(d0=Y0, d1=Y1, r0=plot.bottom, r1=plot.top)
    return x_of, y_of, ticks(*nice_domain(Y0, Y1, STEP), STEP)


def band_polygon(run: list[dict], x_of: Scale, y_of: Scale) -> str:
    top = " ".join("{:.1f},{:.1f}".format(x_of(r["x"]), y_of(r["hi"])) for r in run)
    bottom = " ".join(
        "{:.1f},{:.1f}".format(x_of(r["x"]), y_of(r["lo"])) for r in reversed(run)
    )
    return (
        f'<polygon points="{top} {bottom}" fill="url(#hatch-mo)" '
        f'color="var(--color-ink-muted)" stroke="var(--band-edge)" '
        f'stroke-width="1" stroke-dasharray="4 3" />'
    )


def whisker(row: dict, x_of: Scale, y_of: Scale) -> str:
    """A single poll's interval, drawn as a vertical line with caps.

    A polygon needs two distinct x values to have any width. With one poll it
    collapses to a zero-width shape and the published margin becomes invisible,
    which is the defect task 0002 found. The whisker is the fix.
    """
    x, lo, hi = x_of(row["x"]), y_of(row["lo"]), y_of(row["hi"])
    cap = 6
    return (
        f'<line x1="{x:.1f}" y1="{lo:.1f}" x2="{x:.1f}" y2="{hi:.1f}" '
        f'stroke="var(--band-edge)" stroke-width="1" />'
        f'<line x1="{x - cap:.1f}" y1="{lo:.1f}" x2="{x + cap:.1f}" y2="{lo:.1f}" '
        f'stroke="var(--band-edge)" stroke-width="1" />'
        f'<line x1="{x - cap:.1f}" y1="{hi:.1f}" x2="{x + cap:.1f}" y2="{hi:.1f}" '
        f'stroke="var(--band-edge)" stroke-width="1" />'
    )


def desc_text(n_banded: int, n_null: int, narrow: bool) -> str:
    band_note = (
        "drawn as a capped vertical whisker where a single bounded poll stands alone"
        if narrow
        else "drawn as a hatched band where two or more are adjacent, and as a "
        "capped vertical whisker where a single bounded poll stands alone"
    )
    return (
        f"A time series of poll estimates from {X0} to {X1} plotted against election "
        f"year. {n_banded} of {len(SERIES)} polls carry a published margin of error, "
        f"{band_note}. {n_null} poll published no margin of error and is drawn as an "
        f"open circle, with no interval imputed. The y axis runs from 0 to 10 per cent "
        f"and is not truncated. Fills use the page semantic tokens. These are "
        f"placeholder figures and are not published."
    )


def render(viewport: str) -> str:
    cfg = VIEWPORTS[viewport]
    w, h, plot = cfg["w"], cfg["h"], cfg["plot"]
    narrow = viewport == "narrow"

    x_of, y_of, y_ticks = scales_for(viewport)
    runs = band_runs(SERIES)
    n_null = sum(1 for r in SERIES if r["lo"] is None)
    n_banded = len(SERIES) - n_null

    # At 420px there is no room for a y-axis unit label on every tick.
    y_label_every = 2 if narrow else 1

    out: list[str] = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'class="chart" role="img" aria-labelledby="chart-01-title chart-01-desc" '
        # Declares its own provenance. tools/build.py refuses any chart that
        # declares neither a source id nor this flag, so a placeholder cannot be
        # mistaken for a finished chart. Drop this attribute only when SERIES
        # carries a real data-source-id from docs/data-sources.md.
        f'data-unsourced="true" '
        f'font-family="IBM Plex Mono, ui-monospace, monospace" '
        f'style="aspect-ratio: {w} / {h}; font-variant-numeric: tabular-nums">'
    )
    out.append(
        '<title id="chart-01-title">One Nation primary vote intention, polls by '
        "year, with published margins of error. Placeholder figures, not "
        "published.</title>"
    )
    out.append(f'<desc id="chart-01-desc">{desc_text(n_banded, n_null, narrow)}</desc>')
    out.append(
        '<defs><pattern id="hatch-mo" width="4" height="4" '
        'patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        '<line x1="0" y1="0" x2="0" y2="4" stroke="currentColor" '
        'stroke-width="1" /></pattern></defs>'
    )

    # Zero rule only. No other gridlines (DESIGN.md).
    out.append(
        f'<line x1="{plot.left}" y1="{y_of(0):.1f}" x2="{plot.right}" '
        f'y2="{y_of(0):.1f}" stroke="var(--color-rule)" stroke-width="1" />'
    )

    for i, v in enumerate(y_ticks):
        if i % y_label_every:
            continue
        out.append(
            f'<text x="{plot.left - 10}" y="{y_of(v) + 4:.1f}" text-anchor="end" '
            f'font-size="16" fill="var(--color-ink-muted)">{v * 100:.0f}%</text>'
        )

    for run in runs:
        # The guard protects the polygon path. Single-poll runs are whiskers by
        # design, so they are excluded from the check deliberately.
        if len({round(x_of(r["x"]), 3) for r in run}) >= 2:
            assert_no_degenerate_bands([run], x_of, f"chart-01 ({viewport})")
            out.append(band_polygon(run, x_of, y_of))
        else:
            out.append(whisker(run[0], x_of, y_of))

    line_points = " ".join(
        "{:.1f},{:.1f}".format(x_of(r["x"]), y_of(r["est"])) for r in SERIES
    )
    out.append(
        f'<polyline points="{line_points}" fill="none" stroke="var(--color-ink)" '
        f'stroke-width="2" data-draw-path />'
    )

    for r in SERIES:
        cx, cy = x_of(r["x"]), y_of(r["est"])
        if r["lo"] is None:
            # No published margin: open circle in muted ink. Never a clean
            # filled point, which would assert a precision nobody stated.
            out.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="none" '
                f'stroke="var(--color-ink-muted)" stroke-width="1.5" />'
            )
        else:
            out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="var(--color-ink)" />')

    x_label_every = 2 if narrow else 1
    for i, r in enumerate(SERIES):
        if i % x_label_every and not narrow:
            continue
        if narrow and i % x_label_every:
            continue
        out.append(
            f'<text x="{x_of(r["x"]):.1f}" y="{plot.bottom + 30}" text-anchor="middle" '
            f'font-size="16" fill="var(--color-ink-muted)">{r["x"]}</text>'
        )

    if not narrow:
        out.append(
            f'<text x="{plot.left - 10}" y="{plot.top - 12}" text-anchor="end" '
            f'font-size="14" fill="var(--color-ink-muted)">Primary vote, per cent</text>'
        )

    out.append("</svg>")
    return "\n".join(out)


def main() -> int:
    here = Path(__file__).resolve().parent
    for viewport, filename in (("wide", "chart-01.svg"), ("narrow", "chart-01-narrow.svg")):
        svg = render(viewport)
        (here / filename).write_text(svg + "\n", encoding="utf-8")
        print(f"wrote {filename} ({len(svg):,} bytes) PLACEHOLDER, not for publication")
    return 0


if __name__ == "__main__":
    sys.exit(main())
