"""Shared scale, tick and band geometry for chart modules.

Two rules from task 0002 live here as assertions rather than comments, because
both bugs were silent:

1. Axis padding must be unpacked in a named order. The first draft unpacked
   (left, right, top, bottom) as (x0, x1, y0, y1) and produced an inverted plot
   area. Box is a dataclass so the order is a name, not a position.

2. A band segment covering a single poll has zero width and renders as
   nothing, which hides a margin that WAS published. assert_no_degenerate_bands
   fails the build instead.

It also owns the text-measurement primitives, because two chart modules each
carried their own copy and both were wrong in the same way. See wrap_to_width.
"""

from __future__ import annotations

import math
import textwrap
from dataclasses import dataclass
from typing import Iterable, Sequence


# --- Text measurement -------------------------------------------------------
#
# Wrapping must be done in user units, not characters. `textwrap.wrap` counts
# characters, but the limit that matters is the canvas width in user units.
#
# These are measured, not assumed: at 16px IBM Plex Mono a character advances
# 9.632 units, and at 18px it advances 10.836. Verified in a browser with
# getBBox against a 100-character sample, on both chart modules.
#
# The bug this prevents, hit independently in both charts: wrapping at 76
# characters for a 940-unit column fits, and the same 76 characters in a 340-unit
# narrow column needs 732 units and overruns the canvas by 392. The SVG renders
# perfectly either way and the clipped tail is invisible in the source.
CHAR_UNITS_16 = 9.632
CHAR_UNITS_18 = 10.836


def wrap_to_width(text: str, max_units: float, font_size: int = 16) -> list[str]:
    """Wrap text so no line exceeds `max_units` user units.

    The advance width differs by font size, so the caller states which applies.
    Never wrap by character count against a canvas width: those are different
    quantities and the mismatch is silent.
    """
    per_char = CHAR_UNITS_18 if font_size >= 18 else CHAR_UNITS_16
    return textwrap.wrap(text, width=max(8, int(max_units // per_char))) or [text]


def fits_width(text: str, max_units: float, font_size: int = 16) -> bool:
    """True when a single unwrapped line fits inside `max_units`."""
    per_char = CHAR_UNITS_18 if font_size >= 18 else CHAR_UNITS_16
    return len(text) * per_char <= max_units


@dataclass(frozen=True)
class Box:
    """Plot area in user units. Unpack by attribute name, never by position."""

    left: float
    right: float
    top: float
    bottom: float

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.bottom - self.top

    def __post_init__(self) -> None:
        if self.right <= self.left or self.bottom <= self.top:
            raise ValueError(
                f"inverted plot area: left={self.left} right={self.right} "
                f"top={self.top} bottom={self.bottom}"
            )


def nice_domain(lo: float, hi: float, step: float) -> tuple[float, float]:
    """Snap a domain outward to multiples of step.

    Deliberately not a general "nice number" implementation. Task 0002 found
    that replicating d3-scale's nice() is where the subtlety lives. For four
    chart forms with hand-chosen axes you want floor/ceil against a step you
    chose and can see, asserted in a test, not a general algorithm you trust.
    """
    if step <= 0:
        raise ValueError(f"step must be positive, got {step}")
    return math.floor(lo / step) * step, math.ceil(hi / step) * step


def ticks(lo: float, hi: float, step: float) -> list[float]:
    """Tick values from lo to hi inclusive, at step."""
    if step <= 0:
        raise ValueError(f"step must be positive, got {step}")
    out: list[float] = []
    v = math.ceil(lo / step) * step
    while v <= hi + step / 1000:
        out.append(round(v, 10))
        v += step
    return out


@dataclass(frozen=True)
class Scale:
    """Linear scale mapping a data domain onto a pixel range."""

    d0: float
    d1: float
    r0: float
    r1: float

    def __call__(self, value: float) -> float:
        if self.d1 == self.d0:
            raise ValueError(f"degenerate domain {self.d0}..{self.d1}")
        t = (value - self.d0) / (self.d1 - self.d0)
        return self.r0 + t * (self.r1 - self.r0)


def band_runs(rows: Sequence[dict]) -> list[list[dict]]:
    """Split rows into contiguous runs that all carry a published margin.

    A poll with no published margin (DESIGN.md, "Where there is no band")
    BREAKS the band. Skipping the point instead would draw a straight line
    across the gap and visually assert an interval the source never published.
    """
    runs: list[list[dict]] = []
    current: list[dict] = []
    for row in rows:
        if row.get("lo") is None or row.get("hi") is None:
            if current:
                runs.append(current)
                current = []
        else:
            current.append(row)
    if current:
        runs.append(current)
    return runs


def assert_no_degenerate_bands(runs: Iterable[Sequence[dict]], x_of: Scale, chart: str) -> None:
    """Fail the build if any band segment would render with zero width.

    This is the task 0002 defect. A lone banded poll beside a null produces a
    two-point polygon at the same x, so its uncertainty interval is invisible.
    The fix is to render single-poll runs as a whisker, not a polygon; this
    assertion exists so that if the fix is forgotten, the build stops.
    """
    for run in runs:
        xs = {round(x_of(r["x"]), 3) for r in run}
        if len(xs) < 2:
            raise AssertionError(
                f"{chart}: band segment covers {len(run)} poll(s) at a single x "
                f"({sorted(xs)}), so its interval renders with zero width. Render "
                f"single-poll runs as a vertical whisker with a cap."
            )


def fmt(value: float, dp: int = 1) -> str:
    """Format a figure honestly. False precision undermines the page."""
    return f"{value:.{dp}f}"
