#!/usr/bin/env python3
"""Ingest Roy Morgan federal primary voting intention (task 0004).

Stdlib only, no dependencies. Reads the saved page HTML and writes
data/polls_roymorgan.csv plus data/roymorgan_election_results.csv.

    python3 tools/ingest_roymorgan.py --html /tmp/rm.html
    python3 tools/ingest_roymorgan.py --fetch      # network, slower

Why this script is careful
--------------------------
Two traps, both verified against the live page on 2026-10-04, and both of the
kind that produce a plausible wrong number rather than an error.

**Trap 1: the monthly table has no One Nation column.** The long-term table
splits Independents and Other Parties apart; the monthly table collapses them
into a single "Other Parties (ALL)" column. A positional read of the monthly
table would silently substitute that combined figure for the party.

For the April 27 2025 wave that cell reads 18.5, against One Nation at 7.5.
The publisher's own footnote says so: "a combined figure of 18.5% for
Independents & Other Parties. This includes support for One Nation
(highlighted in the release) of 7.5%." One Nation is a SUBSET of that cell,
so the monthly table cannot supply a discrete party figure at all.

**Trap 2: "Other Parties (ALL)" includes One Nation.** Even where a
discrete figure is recoverable it must never be read from a combined column.

So the policy is enforced in code, not in a comment:
  - columns are selected by header text, never by index
  - a requested column that is absent raises UnmappedColumn
  - a column whose name marks it combined ("(ALL)", "Ind./Others") can never
    satisfy a request for a discrete party
  - the election-results table, which DOES carry a discrete One Nation
    column, is the only source of a party primary vote
  - the monthly table contributes field windows only, with share left null

**What this source cannot supply.** Roy Morgan publishes no sample size, no
margin of error, no publication date and no methodology page. Verified by
string search over the full page for "sample size", "margin of error",
"margin of sampling error", "interviewed", "confidence interval", "plus or
minus" and "+/-": zero matches. Those fields are written as null and must
stay null. Imputing a margin from an assumed n is prohibited by AGENTS.md
non-negotiable 5 and would be fabricated precision.

Validation runs on write, on both files: every numeric field is range-checked,
every wave must carry a field window whose days and span agree with its own
label, and a discrete party figure may never exceed the combined column that
contains it. The window check was added 2026-10-18 after nine waves were found
to have been written with a month applied to the wrong days.
"""

import argparse
import csv
import html
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data"
URL = "https://www.roymorgan.com/morgan-poll/primary-voting-intention/"

# Headers that mark a column as an aggregate rather than a single party. A
# request for a discrete party figure must never be satisfied by one of these.
COMBINED_MARKERS = ("(all)", "ind./others", "ind./ others", "can't say", "total others")


class UnmappedColumn(KeyError):
    """A required column is absent. Loud by design.

    AGENTS.md gotchas: "select columns by header, never by offset". A fixed
    offset read overstates the party by more than double on the April 2025
    wave, and it fails silently, which is worse than crashing.
    """


class SourceShapeChanged(ValueError):
    """The page no longer looks like the page that was assessed."""


def clean(html_fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", html_fragment)).strip()


def parse_tables(raw: str) -> list[list[list[str]]]:
    """Return every <table> as a list of rows of cell text."""
    out = []
    for table in re.findall(r"<table.*?</table>", raw, re.S | re.I):
        rows = []
        for row in re.findall(r"<tr.*?</tr>", table, re.S | re.I):
            cells = [
                clean(c) for c in re.findall(r"<t[hd].*?</t[hd]>", row, re.S | re.I)
            ]
            if cells:
                rows.append(cells)
        if rows:
            out.append(rows)
    return out


def is_aggregate(name: str) -> bool:
    """True when a column name marks an aggregate rather than a single party."""
    n = name.strip().lower()
    return any(m in n for m in COMBINED_MARKERS)


def select_column(header: list[str], want: str, table: str) -> int:
    """Return the index of a column by header text. Never by position.

    An aggregate column is refused when the caller asked for a DISCRETE party,
    because that substitution is the specific error this whole script exists to
    prevent. Asking for an aggregate by name is legitimate and allowed: the
    monthly table's "Other Parties (ALL)" is read on purpose, and labelled as
    such, precisely so it is never mistaken for the party.

    So the guard is on the mismatch, not on aggregates themselves. It fires
    when the request is discrete and the resolved column is not, which is the
    shape of the bug. Asking for "Other Parties (ALL)" and getting it is not
    the bug; asking for "One Nation" and getting it is.
    """
    normalised = [h.strip().lower() for h in header]
    target = want.strip().lower()
    want_is_aggregate = is_aggregate(target)

    for i, name in enumerate(normalised):
        if name == target:
            if not want_is_aggregate and is_aggregate(name):
                raise UnmappedColumn(
                    f"{table}: requested discrete column {want!r} matched "
                    f"aggregate column {name!r}. A combined column includes One "
                    f"Nation and other parties, so reading it as a discrete "
                    f"party figure would overstate the party. Refusing rather "
                    f"than substituting."
                )
            return i

    # Tolerate spacing and punctuation differences before giving up, but only
    # for genuinely equivalent spellings, never to bridge to a different column.
    squashed = {re.sub(r"[^a-z]", "", n): i for i, n in enumerate(normalised)}
    squashed_target = re.sub(r"[^a-z]", "", target)
    if squashed_target in squashed:
        i = squashed[squashed_target]
        if not want_is_aggregate and is_aggregate(normalised[i]):
            raise UnmappedColumn(
                f"{table}: requested discrete column {want!r} matched aggregate "
                f"column {normalised[i]!r} after normalisation. Refusing."
            )
        return i

    # Last resort: a discrete party name appearing inside an aggregate header.
    # This is where a careless mapping would quietly succeed, so it is refused.
    for i, name in enumerate(normalised):
        if not want_is_aggregate and target and target in name and is_aggregate(name):
            raise UnmappedColumn(
                f"{table}: requested discrete column {want!r} only appears inside "
                f"aggregate column {name!r}. Refusing rather than reading a "
                f"combined figure as a party share."
            )

    raise UnmappedColumn(
        f"{table}: no column headed {want!r}. Present: {header!r}. "
        f"The page schema may have changed; re-verify against the source "
        f"before changing anything."
    )


def parse_number(cell: str) -> float | None:
    """Return a float, or None for an empty, 'n/a' or 'Change' cell."""
    c = cell.strip().replace("−", "-")
    if not c or c.lower() in {"n/a", "na", "-", "change", "*"}:
        return None
    m = re.match(r"^(-?\d+(?:\.\d+)?)", c)
    return float(m.group(1)) if m else None


def resolve_year(label: str, current: int | None) -> int | None:
    """Table rows are grouped under bare year headers; carry the year down."""
    if re.fullmatch(r"\d{4}", label.strip()):
        return int(label.strip())
    return current


MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5,
    "june": 6, "july": 7, "august": 8, "september": 9, "october": 10,
    "november": 11, "december": 12,
}


def parse_field_window(label: str, year_hint: int | None = None) -> tuple[str, str]:
    """Turn 'May 5-31' or 'March 15/16 & 22/23, 2014' into an ISO date range.

    The publisher puts the year on some wave labels and only on the year
    header row for others, so `year_hint` carries the grouping year down.
    Returns (start, end) as ISO dates, or ("", "") when no day is given.

    Each day number belongs to the month named *before* it, not to the first
    month on the label. The previous version took the leading month and applied
    it to every day it found, which silently corrupted the eight cross-month
    waves: 'April 25 - May 1, 2022' came out as 2022-04-01 to 2022-04-25, a
    24-day window starting three weeks early, and 'July 24/25 & 31/ August 1,
    2021' became 2021-07-01 to 2021-07-31. The fieldwork window is one of the
    four fields `docs/standards.md` requires a polling citation to carry, so a
    wrong one is a wrong citation on the page, and nothing in the chart drawing
    would have shown it: the windows are not rendered.
    """
    year_match = re.search(r"(\d{4})", label)
    year = int(year_match.group(1)) if year_match else year_hint
    if not year:
        return "", ""

    # Walk the label left to right, tracking the month most recently named.
    # A bare day inherits it. This is what makes 'February 28/March 1 & 7/8'
    # resolve to 18 February through 8 March rather than 1 February through 28.
    pairs: list[tuple[int, int]] = []
    month: int | None = None
    for token in re.finditer(r"([A-Za-z]+)|\b(\d{1,2})\b", label):
        word, day = token.group(1), token.group(2)
        if word:
            candidate = MONTHS.get(word.lower())
            if candidate:
                month = candidate
            continue
        if month is not None:
            d = int(day)
            if 1 <= d <= 31:
                pairs.append((month, d))

    if not pairs:
        return "", ""

    # Months in the order they are named, which is the order of the window.
    # Taking min and max of the month *numbers* would invert
    # 'December 30 - January 6', because 1 < 12.
    month_seq: list[int] = []
    for m, _ in pairs:
        if m not in month_seq:
            month_seq.append(m)

    start_month, end_month = month_seq[0], month_seq[-1]
    # Days within the opening and closing months: earliest first, latest last.
    start_day = min(d for m, d in pairs if m == start_month)
    end_day = max(d for m, d in pairs if m == end_month)

    # An earlier-numbered month named second crosses a year boundary:
    # 'December 30 - January 6, 2021' ends in the year the label states and its
    # December belongs to the year before.
    start_year = year - 1 if end_month < start_month else year
    return (
        f"{start_year:04d}-{start_month:02d}-{start_day:02d}",
        f"{year:04d}-{end_month:02d}-{end_day:02d}",
    )


def ingest_monthly(tables: list[list[list[str]]], warnings: list[str]) -> list[dict]:
    """Field windows and combined shares from the long-term monthly table.

    One Nation is deliberately absent from the output. The column does not
    exist, and the nearest equivalent is an aggregate containing several
    parties. Recording the aggregate under the party's name is the error this
    script refuses to make.
    """
    monthly = max(tables, key=lambda t: len(t))
    header = monthly[0]

    idx_total_others = select_column(header, "Total Others", "monthly table")
    idx_other_all = select_column(header, "Other Parties (ALL)", "monthly table")
    idx_indep = select_column(header, "Indepen-dents (ALL)", "monthly table")
    idx_alp = select_column(header, "ALP", "monthly table")
    idx_cant = select_column(header, "Can't say/ Refused", "monthly table")

    rows: list[dict] = []
    year: int | None = None

    for cells in monthly[1:]:
        label = cells[0].strip()
        if not label:
            continue
        if re.fullmatch(r"\d{4}", label):
            year = int(label)
            continue
        if label.lower() == "change":
            continue

        alp = parse_number(cells[idx_alp]) if idx_alp < len(cells) else None
        other_all = parse_number(cells[idx_other_all]) if idx_other_all < len(cells) else None
        indep = parse_number(cells[idx_indep]) if idx_indep < len(cells) else None
        cant = parse_number(cells[idx_cant]) if idx_cant < len(cells) else None
        total_others = (
            parse_number(cells[idx_total_others]) if idx_total_others < len(cells) else None
        )

        if other_all is None and total_others is None:
            continue

        # An asterisk marks a wave the publisher footnoted, which is exactly
        # the wave where the combined column is not the party.
        footnote = "*" in label or any("*" in c for c in cells[1:])

        win_start, win_end = parse_field_window(label, year)
        rows.append(
            {
                "house": "Roy Morgan",
                "wave_label": label,
                "year": year or "",
                "fielded_start": win_start,
                "fielded_end": win_end,
                # Not published by this house. Left null deliberately.
                "n": "",
                "margin_of_error": "",
                "pub_date": "",
                "pvi_alp": alp if alp is not None else "",
                # AGGREGATE ONLY. Includes One Nation plus every other party.
                "other_parties_all": other_all if other_all is not None else "",
                "independents_all": indep if indep is not None else "",
                "total_others": total_others if total_others is not None else "",
                "cant_say": cant if cant is not None else "",
                # Never populated from the columns above. See module docstring.
                "pvi_oned": "",
                "publishes_n": "no",
                "publishes_margin_of_error": "no",
                "publishes_pub_date": "no",
                "footnoted_wave": "yes" if footnote else "no",
                "source_id": "roymorgan-pvi",
                "retrieved": date.today().isoformat(),
            }
        )

    if not rows:
        raise SourceShapeChanged(
            "monthly table parsed to zero rows; the page layout has probably "
            "changed. Re-verify against the source before trusting any output."
        )

    footnoted = [r["wave_label"] for r in rows if r["footnoted_wave"] == "yes"]
    if footnoted:
        warnings.append(
            f"{len(footnoted)} wave(s) carry a publisher footnote, which is where "
            f"the combined column is least safe to read: {footnoted}"
        )
    return rows


def ingest_election_results(
    tables: list[list[list[str]]], warnings: list[str]
) -> list[dict]:
    """Discrete One Nation primary vote by election, from the results table.

    This is the only table with a real One Nation column. Every figure still
    requires confirmation against AEC before publication (AGENTS.md
    non-negotiable 2); Roy Morgan is a cross-check, not the source of record.
    """
    # Identified by HAVING a discrete One Nation column, not by guessing from
    # the header text. The header's first cell is empty on this page and the
    # word "election" lives in the body rows, so a header-text test finds
    # nothing; what actually distinguishes the results table is the one column
    # the monthly table lacks. Keying on that is both simpler and safer: it
    # selects for the property the caller needs.
    candidates = []
    for t in tables:
        if "one nation" in [h.strip().lower() for h in t[0]]:
            candidates.append(t)

    if not candidates:
        raise SourceShapeChanged(
            "no table with a discrete One Nation column found; the page layout "
            "has probably changed. Roy Morgan's monthly table is not a usable "
            "substitute: it has no such column."
        )

    # Two tables carry the column (a recent-results table and a 2013-2022
    # long-run one). The smaller is the recent election results.
    table = min(candidates, key=len)
    header = table[0]
    idx_oned = select_column(header, "One Nation", "election results table")
    idx_alp = select_column(header, "ALP", "election results table")

    out: list[dict] = []
    for cells in table[1:]:
        label = cells[0].strip()
        # 'Election May 3, 2025'. Group 1 is the whole date; group 2 is the year
        # nested inside it. Reading group(2) as the date collapses every row to
        # a bare year, which is what the first run of this script did.
        m = re.match(r"Election\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})", label)
        if not m:
            continue
        election_date = m.group(1).strip()
        election_year = int(re.search(r"(\d{4})", election_date).group(1))
        oned = parse_number(cells[idx_oned]) if idx_oned < len(cells) else None
        if oned is None:
            continue
        out.append(
            {
                "election_date": election_date,
                "election_year": election_year,
                "house": "Roy Morgan",
                "primary_vote_oned_pct": oned,
                "primary_vote_alp_pct": (
                    parse_number(cells[idx_alp]) if idx_alp < len(cells) else None
                ),
                "cross_check_only": "yes",
                "requires_aec_confirmation": "yes",
                "source_id": "roymorgan-pvi",
                "retrieved": date.today().isoformat(),
            }
        )

    if not out:
        raise SourceShapeChanged("election-results table yielded no rows")

    # The 12.3% Senate-registration quota is a threshold this party has never
    # cleared at any federal election, so testing "is it below quota" flags all
    # ten rows and therefore says nothing. The meaningful signal is the sharp
    # discontinuity in 2004-2013, where the party polled around 1-2% against
    # 5-6% before and after. Those cycles are a different measure of the same
    # name: below quota, and with far fewer candidates on the ballot.
    lownoise = [r for r in out if r["primary_vote_oned_pct"] < 2.5]
    if lownoise:
        warnings.append(
            f"{len(lownoise)} election(s) return under 2.5% "
            f"({', '.join(str(r['election_year']) for r in lownoise)}). Below "
            f"the 12.3% Senate quota a party can still contest, but coverage is "
            f"thinner and the figure is not the same measure as the 5-6% cycles. "
            f"Plot as one continuous series only with that break marked."
        )
    return out



ELECTION_ROW = re.compile(r"\bElection\b", re.IGNORECASE)


def ingest_discrete_oned(
    tables: list[list[list[str]]], warnings: list[str]
) -> list[dict]:
    """Discrete One Nation polling by wave. Election results are excluded.

    The page carries a second table with its own One Nation column, separate from
    the long-term monthly one. The monthly table has no such column, so this is
    the only place on the page a discrete party polling figure exists.

    Results are interleaved with polls in the same first column and must be
    dropped. Two appear in range, the 2016 and 2019 federal elections, and the
    2019 one sits *inside* the 2019 year group, so counting rather than matching
    is how you get a window of 6 where the data holds 5. A result counted as a
    poll is the same class of error as the 49-versus-48 slip: it survives
    because nothing recomputes it.

    Coverage on the live source, measured 2026-10-04: 2018 to 2022 complete, 2013
    to 2016 almost entirely blank, 2017 absent from the table altogether.
    """
    candidates = [t for t in tables if "one nation" in [h.strip().lower() for h in t[0]]]

    if not candidates:
        raise SourceShapeChanged(
            "no table with a discrete One Nation column found; the page layout "
            "has probably changed. Roy Morgan's monthly table is not a usable "
            "substitute: it has no such column."
        )

    # The live page carries two such tables: the recent election results
    # (12 rows) and this long-run one (132). Taking the larger is the correct
    # choice, but picking between them silently is how a series quietly becomes
    # the wrong series, so an unexpected count is reported rather than absorbed.
    if len(candidates) > 2:
        warnings.append(
            f"{len(candidates)} tables carry a discrete One Nation column, not the "
            f"2 this script was written against (the recent election results and "
            f"the long-run polling table). Taking the largest. Re-verify the "
            f"page structure if the row count looks wrong."
        )

    table = max(candidates, key=len)
    header = table[0]
    idx_oned = select_column(header, "One Nation", "discrete polling table")

    rows: list[dict] = []
    years_seen: dict[int, int] = {}
    results_dropped: list[str] = []

    for cells in table[1:]:
        label = cells[0].strip()
        if not label:
            continue
        if re.fullmatch(r"\d{4}", label):
            continue  # bare year group header, carries no data
        if ELECTION_ROW.search(label):
            results_dropped.append(label)
            continue

        years = re.findall(r"\b(20\d\d)\b", label)
        if not years:
            continue  # a commentary row, not a wave
        year = int(years[0])

        if idx_oned >= len(cells):
            continue
        value = parse_number(cells[idx_oned])
        if value is None:
            years_seen.setdefault(year, 0)
            continue  # no discrete figure for the party on this wave

        window_start, window_end = parse_field_window(label, year)
        years_seen[year] = years_seen.get(year, 0) + 1
        rows.append(
            {
                "house": "Roy Morgan",
                "wave_label": label,
                "year": year,
                "fielded_start": window_start,
                "fielded_end": window_end,
                # Not published by this house. Left null deliberately.
                "n": "",
                "margin_of_error": "",
                "pub_date": "",
                "pvi_oned": value,
                "publishes_n": "no",
                "publishes_margin_of_error": "no",
                "publishes_pub_date": "no",
                "source_id": "roymorgan-pvi",
                "retrieved": date.today().isoformat(),
            }
        )

    if not rows:
        raise SourceShapeChanged(
            "discrete polling table yielded no usable rows; the page layout has "
            "probably changed."
        )

    if results_dropped:
        warnings.append(
            f"excluded {len(results_dropped)} election result row(s) from the poll "
            f"series: {results_dropped}. They share the poll table's first column "
            f"and are results, not polls."
        )

    empty = sorted(y for y, n in years_seen.items() if n == 0)
    if empty:
        warnings.append(
            f"{len(empty)} year(s) in the table carry no discrete figure for this "
            f"party: {', '.join(str(y) for y in empty)}. Recorded as a property "
            f"of the source, not interpreted."
        )

    return rows


def window_problems(rows: list[dict], max_days: int) -> list[str]:
    """Refuse a fieldwork window that contradicts its own label.

    `docs/standards.md` requires a polling citation to carry the fieldwork
    window, so a wrong window is a wrong citation on the page. It is also
    invisible in the chart: the windows are never rendered, and the figures are
    grouped by year, so a corrupt window changes nothing you can see.

    This exists because `parse_field_window()` took the leading month name and
    applied it to every day number on the label, which silently corrupted the
    nine cross-month waves. 'April 25 - May 1, 2022' became 2022-04-01 to
    2022-04-25 — a 25-day window starting three weeks early — and nothing
    failed, because the only file validated was the monthly one.

    `max_days` is passed in rather than assumed, because the two series are
    genuinely different cadences: the discrete One Nation table is fortnightly,
    and the monthly table's waves really do span up to 31 days. One shared cap
    would either reject real monthly waves or miss corrupted fortnightly ones.
    The day-level test below is the part that does not depend on cadence.
    """
    problems: list[str] = []
    for r in rows:
        label = r.get("wave_label", "")
        start, end = r.get("fielded_start", ""), r.get("fielded_end", "")
        if not start or not end:
            continue
        try:
            d0 = date.fromisoformat(start)
            d1 = date.fromisoformat(end)
        except ValueError:
            problems.append(f"{label}: window {start!r}..{end!r} is not ISO")
            continue

        span = (d1 - d0).days + 1
        if span < 1:
            problems.append(
                f"{label}: window runs backwards, {start} to {end}"
            )
        elif span > max_days:
            problems.append(
                f"{label}: fieldwork window spans {span} days ({start} to "
                f"{end}), more than the {max_days}-day cap for this series. A "
                f"month has probably been applied to a day it does not belong "
                f"to."
            )

        # Every day in the window must be a day named on the label. This is the
        # check that catches a month misapplied rather than merely a long span.
        days_on_label = {int(d) for d in re.findall(r"\b(\d{1,2})\b", label)}
        for d in (d0.day, d1.day):
            if d not in days_on_label:
                problems.append(
                    f"{label}: window edge day {d} is not a day named in the "
                    f"label. A month has been applied to a day it does not "
                    f"belong to."
                )
    return problems


def validate(rows: list[dict], warnings: list[str]) -> list[str]:
    """Fail loudly rather than writing a plausible wrong file."""
    problems: list[str] = []

    if not rows:
        problems.append("no monthly rows produced")

    for r in rows:
        label = r["wave_label"]
        if not r["year"]:
            problems.append(f"{label}: no year resolved")
        for key in ("alp", "other_parties_all", "total_others"):
            v = r[f"pvi_{key}"] if key == "alp" else r[key]
            if v != "" and not (0 <= float(v) <= 100):
                problems.append(f"{label}: pvi_{key}={v} outside 0-100")
        # The aggregate must never be smaller than a party inside it. This
        # cannot be checked without a party figure, which is the point: the
        # monthly table has none, so the check is structural, below.
        if r["pvi_oned"] != "":
            problems.append(
                f"{label}: pvi_oned is populated on the monthly table, which has "
                f"no One Nation column. This script must never write that field."
            )

    if problems:
        return problems
    return []


def write_csv(path: Path, rows: list[dict]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise SystemExit(f"refusing to write an empty file: {path}")
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path.relative_to(ROOT)} ({len(rows)} rows)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--html", type=Path, help="saved page HTML")
    ap.add_argument("--fetch", action="store_true", help="download the page")
    args = ap.parse_args()

    if args.fetch:
        import urllib.request

        req = urllib.request.Request(URL, headers={"User-Agent": "margin-of-error/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    elif args.html:
        raw = args.html.read_text(encoding="utf-8", errors="replace")
    else:
        ap.error("pass --html or --fetch")

    # AGENTS.md gotchas: aec.gov.au returns HTTP 200 with a 404 body, so a
    # fetch is validated on content, never on status code alone. Same habit.
    if "voting intention" not in raw.lower():
        print("error: page does not contain the expected content; refusing", file=sys.stderr)
        return 1

    tables = parse_tables(raw)
    if len(tables) < 2:
        print(f"error: expected at least 2 tables, found {len(tables)}", file=sys.stderr)
        return 1

    warnings: list[str] = []
    try:
        monthly = ingest_monthly(tables, warnings)
        results = ingest_election_results(tables, warnings)
        oned = ingest_discrete_oned(tables, warnings)
    except (UnmappedColumn, SourceShapeChanged) as exc:
        print(f"error: {exc}", file=sys.stderr)
        print(
            "Refusing to guess. Re-verify the source and update the column "
            "mapping deliberately.",
            file=sys.stderr,
        )
        return 1

    # The discrete series is what every chart figure is computed from, so it is
    # validated too. It used to be that only the monthly file was checked, which
    # meant the file that ships had no guard at all: the nine corrupted field
    # windows were written straight through, and the monthly check had nothing to
    # say about them because those labels are single-month.
    problems = validate(monthly, warnings)
    # Both files, not just the monthly one. The discrete series is what every
    # chart figure is computed from and it had no guard at all, which is how the
    # nine corrupted windows were written straight through.
    #
    # Caps are measured from each file rather than assumed: the discrete waves
    # span 2 to 14 days and the monthly waves 1 to 27, so one shared cap would
    # either reject real monthly waves or miss corrupted fortnightly ones.
    problems += window_problems(oned, max_days=16)
    problems += window_problems(monthly, max_days=31)
    if problems:
        print("error: validation failed", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    write_csv(OUT_DIR / "polls_roymorgan.csv", monthly)
    write_csv(OUT_DIR / "roymorgan_election_results.csv", results)
    write_csv(OUT_DIR / "polls_roymorgan_oned.csv", oned)

    print()
    for w in warnings:
        print(f"warning: {w}")
    print()
    print(
        "One Nation is NOT written to the monthly file: that table has no "
        "discrete One Nation column. The election-results table is a cross-check "
        "only and needs AEC confirmation before publication."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
