#!/usr/bin/env python3
"""The only place a derived figure is computed.

Charts render numbers. Prose states them. If those were computed separately they
would drift, and the drift is silent: the page keeps rendering, the sentence
stops being true. The archived feasibility model is the worked example. Its own
output was 1.33% booth coverage and the prose describing it said "below 15%",
with nothing in between to notice.

So this module exists to be the single derivation site, and it is deliberately
small and deliberately has no rendering in it. `charts/scales.py` maps numbers
to pixels; this reads data and derives meaning. Merged, the derived numbers
would be untestable without a renderer.

Every function that returns a figure also returns `n_used`. That is not
decoration. The 2019 election has five preceding waves and 2022 has twelve, so a
window of twelve is two different quantities depending on the year, and a caller
holding a bare float has no way to know which one it has. Returning the count
alongside the number makes the wrong caption unreachable rather than merely
unlikely.

`n`, `margin_of_error` and `pub_date` are not modelled here. Roy Morgan
publishes none of them, and `AGENTS.md` non-negotiable 5 prohibits imputing a
margin from an assumed sample size. Their absence is the finding, so there is
no field to hold a fabricated value.
"""

import csv
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class Poll:
    year: int
    wave: str
    value: float
    fielded_start: str
    fielded_end: str


@dataclass(frozen=True)
class Result:
    year: int
    value: float
    confirmed: bool


@dataclass(frozen=True)
class Mean:
    value: float
    n_used: int
    window: int
    low: float
    high: float


@dataclass(frozen=True)
class Gap:
    year: int
    result: float
    mean: float
    n_used: int
    signed_gap: float  # poll minus result; negative means polling was low


def load_polls(path: str | Path) -> list[Poll]:
    """Read the discrete polling CSV.

    Raises ValueError naming the wave if a row has no party figure or no field
    window. An undated poll cannot be placed on a time axis or ordered against
    an election, and a blank figure is the aggregate-column trap the ingest
    exists to prevent reaching this far. Both are refused rather than skipped,
    because a silently dropped row is a series quietly shorter than it claims.
    """
    path = Path(path)
    polls: list[Poll] = []
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            wave = (row.get("wave_label") or "").strip()
            if not wave:
                continue

            raw_value = (row.get("pvi_oned") or "").strip()
            if not raw_value:
                raise ValueError(
                    f"{path.name}: wave {wave!r} has no discrete One Nation "
                    f"figure. The monthly table has no such column; this file "
                    f"should only ever contain waves that do."
                )

            start = (row.get("fielded_start") or "").strip()
            end = (row.get("fielded_end") or "").strip()
            if not start or not end:
                raise ValueError(
                    f"{path.name}: wave {wave!r} has no field window "
                    f"(fielded_start={start!r} fielded_end={end!r}). An undated "
                    f"poll cannot be ordered against an election."
                )

            polls.append(
                Poll(
                    year=int(row["year"]),
                    wave=wave,
                    value=float(raw_value),
                    fielded_start=start,
                    fielded_end=end,
                )
            )
    return polls


def waves_before(polls: Sequence[Poll], year: int, window: int) -> list[Poll]:
    """The trailing `window` waves fielded in `year`, oldest first.

    Election results were already removed at ingest, so nothing here needs to
    exclude them. A wave is not excluded merely for falling in the same year as
    an election: waves fielded in April belong in April's window whether or not
    an election followed in May.
    """
    same_year = [p for p in polls if p.year == year]
    return same_year[-window:] if window > 0 else []


def window_mean(
    polls: Sequence[Poll], year: int, window: int
) -> Mean | None:
    """Mean of the waves preceding `year`, with the count actually used.

    Returns None when no waves precede the year. It never widens or narrows the
    window to manufacture a figure: a five-wave mean and a twelve-wave mean are
    different quantities, and quietly padding one to look like the other is the
    failure this whole module is arranged to prevent.
    """
    used = waves_before(polls, year, window)
    if not used:
        return None

    values = [p.value for p in used]
    return Mean(
        value=statistics.mean(values),
        n_used=len(used),
        window=window,
        low=min(values),
        high=max(values),
    )


def gaps(
    results: Sequence[Result], polls: Sequence[Poll], window: int
) -> list[Gap]:
    """Polling minus result, per election.

    An election with no preceding waves is omitted rather than drawn as zero or
    guessed at. `confirmed` travels through so the build can refuse a chart that
    rests on an unconfirmed result.
    """
    out: list[Gap] = []
    for r in sorted(results, key=lambda x: x.year):
        m = window_mean(polls, r.year, window)
        if m is None:
            continue
        out.append(
            Gap(
                year=r.year,
                result=r.value,
                mean=m.value,
                n_used=m.n_used,
                signed_gap=m.value - r.value,
            )
        )
    return out


def contiguous_years(polls: Sequence[Poll]) -> tuple[int, int]:
    """The longest run of consecutive years carrying at least one wave.

    Derived from the data, never hard-coded. The series this produces starts
    where the source starts, which is a property of the source and not a choice
    made in a chart.
    """
    years = sorted({p.year for p in polls})
    if not years:
        raise ValueError("no polls to take a contiguous range from")

    best_start = best_end = run_start = run_end = years[0]
    for y in years[1:]:
        if y == run_end + 1:
            run_end = y
        else:
            run_start = run_end = y
        # Compare on how many years the run spans, not on its endpoints: a run
        # of 2018-2020 spans 2 and 2018-2019 spans 1, so the longer run wins on
        # length even though its start is earlier. Comparing endpoints instead
        # silently absorbed a trailing isolated year.
        if (run_end - run_start) > (best_end - best_start):
            best_start, best_end = run_start, run_end
    return best_start, best_end


def seat_share(seats: int, chamber: int) -> float:
    """Seats as a fraction of the seats actually in the chamber that election.

    The denominator is a parameter, and deliberately so. The House returned
    150 seats at the 2001, 2004, 2007, 2010, 2013 and 2016 elections and 151
    from 2019, verified by summing every party's national total in each AEC
    party representation download. A single hard-coded 151 — which is what the
    spec originally said — understates a 1-seat share by a fifth in the earlier
    years, and the error is invisible because the gap it feeds is already
    drawn against zero.

    Both arguments are validated rather than coerced. A share of 151 seats in a
    150-seat chamber is corrupt data, and plotting it would draw a 100% line
    that flattens every other election against the axis.
    """
    if isinstance(chamber, bool) or not isinstance(chamber, int) or chamber <= 0:
        raise ValueError(f"chamber size must be a positive integer, got {chamber!r}")
    if isinstance(seats, bool) or not isinstance(seats, int) or seats < 0:
        raise ValueError(f"seat count must be a non-negative integer, got {seats!r}")
    if seats > chamber:
        raise ValueError(
            f"{seats} seats cannot be a share of a {chamber}-seat chamber. "
            f"This is corrupt data, and plotting it would draw a 100% line."
        )
    return seats / chamber
