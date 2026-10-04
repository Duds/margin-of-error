#!/usr/bin/env python3
"""Ingest the party's primary vote and seats won, per federal general election.

Stdlib only. Reads the saved AEC downloads in data/aec/raw/ and writes
data/aec_election_results.csv.

    python3 tools/ingest_aec_seats.py

Why this script exists separately from the Roy Morgan ingest
------------------------------------------------------------
The Roy Morgan page carries a discrete One Nation column, which is why the
project has a working polling ingest at all. It is not the source of record for
either figure on this chart. The AEC publishes both, in one file per election,
with a seat count alongside the vote share, so nothing here is a cross-check.

Both figures come from `HouseFirstPrefsByPartyDownload`, whose header carries
`PartyAb, PartyNm, Elected, TotalPercentage`. The separate party representation
downloads are read too, and the two are cross-checked against each other,
because they are independent tables and a disagreement between them would mean
one of them is being read wrong.

Three traps, each of which produces a plausible wrong number rather than an
error.

**Trap 1: the party is named differently in every era.** The AEC recorded it as
`Pauline Hanson's One Nation` from 2019, `One Nation` from 2007 to 2016, and
`One Nation` with the abbreviation `HAN` in 2004 and 2001. Selecting on the
modern name silently drops five of the nine elections. So the party is located
by its AEC *abbreviation for that election*, recorded per election in
ABBREVIATION_BY_YEAR, and a year whose abbreviation is absent raises rather
than returning a shorter series.

**Trap 2: 2001 is not a CSV, and not one table either.** The AEC publishes no
CSV for 2001 and its live tally room carries a standing disclaimer that the
results "are not final". The official statistics ZIP is used instead. That file
is fixed-width and repeats the party once per state under a section header, so
the national figure must be selected by section. Scanning for the first `HAN`
line returns Queensland's 7.07%, which is over three times the national 4.34%
and still looks entirely reasonable on a chart.

**Trap 3: the House has not always had 151 seats.** It returned 150 from 2001
to 2016 and 151 from 2019. Verified by summing every party's national total in
each party representation download. A share computed against the wrong
denominator is wrong by a fifth in the earlier years, and invisible, because
the seat line is drawn against zero either way.

Usage: python3 tools/ingest_aec_seats.py
"""

import csv
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "aec" / "raw"
OUT = ROOT / "data" / "aec_election_results.csv"

# The AEC abbreviation for the party, per election. This is the primary key for
# finding the row. It is transcribed from the source header, not derived, and
# that is the point: the derivation is what fails silently.
#
# 2004 and 2001 use HAN. 2007 to 2025 use ON. Matching on the modern party name
# instead drops 2004, 2007, 2010, 2013 and 2016.
ABBREVIATION_BY_YEAR = {
    2001: "HAN",
    2004: "HAN",
    2007: "ON",
    2010: "ON",
    2013: "ON",
    2016: "ON",
    2019: "ON",
    2022: "ON",
    2025: "ON",
}

# 2001 has no CSV. Recorded so a reader can see which rows came from where
# without cross-referencing the registry by eye.
CSV_YEARS = (2004, 2007, 2010, 2013, 2016, 2019, 2022, 2025)
FIXED_WIDTH_YEAR = 2001

SECTION_TERMINATOR = "Two Party Preferred"


class SourceShapeChanged(ValueError):
    """A source no longer looks like the source that was assessed.

    Loud by design. `AGENTS.md` gotchas: `aec.gov.au` returns HTTP 200 with a
    404 body for retired URL patterns, and a party that changes its recorded
    name is the same failure at the row level. Both produce an empty or wrong
    series that renders perfectly.
    """


def csv_rows(year: int) -> list[dict]:
    """Read a first-preferences CSV, skipping the AEC's banner line.

    Every one of these files opens with a bracketed metadata line before the
    header, so `csv.DictReader` straight onto the file reads the banner as the
    header and every lookup silently returns None.
    """
    path = RAW / f"house-first-prefs-by-party-{year}.csv"
    if not path.exists():
        raise SourceShapeChanged(f"{path} is missing. Re-fetch and re-verify.")

    lines = path.read_text(encoding="latin-1").splitlines()
    try:
        header_at = next(
            i for i, line in enumerate(lines) if line.startswith("PartyAb,")
        )
    except StopIteration:
        raise SourceShapeChanged(
            f"{path.name}: no PartyAb header found. The AEC may have changed "
            f"the download layout; re-verify against the source."
        ) from None

    return list(csv.DictReader(lines[header_at:]))


def party_row(year: int, rows: list[dict]) -> dict:
    """The party's row, located by the AEC abbreviation for that election.

    Raises if the abbreviation is absent rather than returning nothing. An
    election that quietly contributes no row is a series quietly shorter than
    the caption claims, which is the defect this whole project keeps finding.
    """
    want = ABBREVIATION_BY_YEAR.get(year)
    if want is None:
        raise SourceShapeChanged(
            f"{year}: no AEC abbreviation recorded. Add it to "
            f"ABBREVIATION_BY_YEAR from the source header, having checked the "
            f"party was on the ballot under that abbreviation that year."
        )

    for row in rows:
        if (row.get("PartyAb") or "").strip().upper() == want:
            return row

    present = sorted(
        {(r.get("PartyAb") or "").strip().upper() for r in rows if r.get("PartyAb")}
    )
    raise SourceShapeChanged(
        f"{year}: no party row with abbreviation {want!r}. Present: {present}. "
        f"If the party contested under a different abbreviation that year, fix "
        f"ABBREVIATION_BY_YEAR from the source. Do not match on the party name."
    )


def national_row_2001() -> dict:
    """The party's national first-preference share from the 2001 ZIP.

    `v1_6.txt` lists the party once per state under a section header, national
    first. Selecting the first `HAN` line returns Queensland's 7.07 rather than
    the national 4.34. Both are real figures from the same file, so nothing
    downstream can tell them apart, and 7.07 would put 2001 above every
    election except 2025.

    The section is therefore located explicitly and the row read only from
    within it.
    """
    path = RAW / "2001" / "house-first-prefs-by-party-2001.txt"
    if not path.exists():
        raise SourceShapeChanged(
            f"{path} is missing. The 2001 figures come from the AEC official "
            f"statistics ZIP; see docs/data-sources.md."
        )

    lines = path.read_text(encoding="latin-1").splitlines()

    start = None
    for i, line in enumerate(lines):
        if line.strip().startswith("National Summary"):
            start = i
            break
    if start is None:
        raise SourceShapeChanged(
            f"{path.name}: no National Summary section. The national figure "
            f"must not be guessed from a state section."
        )

    want = ABBREVIATION_BY_YEAR[FIXED_WIDTH_YEAR]
    for line in lines[start + 1 :]:
        if line.strip().startswith(SECTION_TERMINATOR):
            break
        parts = line.split()
        if len(parts) >= 3 and parts[0].upper() == want:
            return {"party_ab": want, "vote_pct": parts[2]}

    raise SourceShapeChanged(
        f"{path.name}: no {want} row inside National Summary. Refusing to fall "
        f"back to a state figure."
    )


def representation_rows(year: int) -> list[dict]:
    """Read the party representation CSV, which lists seats by state."""
    path = RAW / f"house-party-representation-{year}.csv"
    if not path.exists():
        raise SourceShapeChanged(f"{path} is missing. Re-fetch and re-verify.")

    lines = path.read_text(encoding="latin-1").splitlines()
    header_at = next(
        (i for i, line in enumerate(lines) if line.startswith("PartyAb,Party,")), None
    )
    if header_at is None:
        header_at = next(
            (i for i, line in enumerate(lines) if line.startswith("Party,")), None
        )
    if header_at is None:
        raise SourceShapeChanged(
            f"{path.name}: no Party header found; the layout may have changed."
        )

    return list(csv.DictReader(lines[header_at:]))


def chamber_size(year: int, rows: list[dict]) -> int:
    """Seats in the House that election, summed across every party.

    Not a constant. The House returned 150 seats from 2001 to 2016 and 151
    from 2019, and the figure belongs to the source, not to a chart.
    """
    header = [k for k in rows[0].keys() if k]
    column = "Total" if "Total" in header else "National"
    if column not in header:
        raise SourceShapeChanged(
            f"{year}: no Total or National column in party representation; "
            f"present: {header}"
        )

    total = 0
    for row in rows:
        cell = (row.get(column) or "").strip()
        if cell.isdigit():
            total += int(cell)

    if total < 100:
        raise SourceShapeChanged(
            f"{year}: party representation totals sum to {total}, which is not "
            f"a House size. The column was probably read wrong."
        )
    return total


def seats_from_representation(year: int, rows: list[dict]) -> int:
    """Seats won, from the party representation table.

    Read independently of the first-preferences file so the two can be
    cross-checked. They are separate tables on the AEC's site, and agreement
    between them is evidence that neither is being misread.
    """
    want = ABBREVIATION_BY_YEAR[year]
    for row in rows:
        ab = (row.get("PartyAb") or "").strip().upper()
        name = (row.get("Party") or "").strip().lower()
        if ab == want or (not ab and "one nation" in name):
            column = "Total" if "Total" in row else "National"
            cell = (row.get(column) or "").strip()
            if not cell.isdigit():
                raise SourceShapeChanged(
                    f"{year}: representation table has non-numeric {column} "
                    f"for the party: {cell!r}"
                )
            return int(cell)
    raise SourceShapeChanged(
        f"{year}: no representation row for abbreviation {want!r}. Refusing "
        f"rather than assuming zero seats, because absence is not a figure."
    )


def main() -> int:
    rows: list[dict] = []

    for year in sorted(ABBREVIATION_BY_YEAR):
        if year == FIXED_WIDTH_YEAR:
            # 2001 has no CSV for either table. The official statistics ZIP is
            # the source, and it needs different readers for each figure.
            primary = national_row_2001()
            share = float(primary["vote_pct"])
            seats = seats_from_members_elected_2001()
            chamber = chamber_size_from_members_elected_2001()
        else:
            rep_rows = representation_rows(year)
            fp_rows = csv_rows(year)
            row = party_row(year, fp_rows)
            seats = int((row.get("Elected") or "").strip())
            chamber = chamber_size(year, rep_rows)
            share = float((row.get("TotalPercentage") or "").strip())

            # Two independent AEC tables, one figure. A disagreement means one
            # of them is being misread, and that is worth a hard failure.
            from_representation = seats_from_representation(year, rep_rows)
            if from_representation != seats:
                raise SourceShapeChanged(
                    f"{year}: first preferences say {seats} seats, party "
                    f"representation says {from_representation}. Two AEC tables "
                    f"disagree; do not publish either until it is resolved."
                )

        rows.append(
            {
                "election_year": year,
                "party_ab": ABBREVIATION_BY_YEAR[year],
                "primary_vote_pct": f"{share:g}",
                "seats_won": seats,
                "chamber_size": chamber,
                "seat_share_pct": f"{seats / chamber * 100:.4f}",
                "source_id": f"aec-hor-{year}-fp-by-party",
                "retrieved": date.today().isoformat(),
            }
        )

    if len(rows) != len(ABBREVIATION_BY_YEAR):
        raise SystemExit(f"expected {len(ABBREVIATION_BY_YEAR)} rows, got {len(rows)}")

    with OUT.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {OUT.relative_to(ROOT)} ({len(rows)} elections)")
    for r in rows:
        print(
            f"  {r['election_year']}  {r['party_ab']:<4} "
            f"{r['primary_vote_pct']:>5}%  {r['seats_won']} of "
            f"{r['chamber_size']} seats"
        )
    return 0


def chamber_size_from_members_elected_2001() -> int:
    """Seats in the 2001 House, counted from the members elected list.

    Derived, not asserted. The 150 has to be counted here for the same reason
    the seat share is computed rather than typed: it is a property of the
    source, and hard-coding it is how the earlier years would silently end up
    divided by the wrong number.
    """
    rows, _ = _members_elected_2001()
    return len(rows)


def _members_elected_2001() -> tuple[list[tuple[str, str]], int]:
    """Parse the 2001 members elected table into (division, party code) rows.

    Returns the rows and the count of elected members carrying the party's
    AEC code. The party column is the last whitespace-separated field, which
    the table states is the party code, so rows are taken on that shape rather
    than a column index: the table is fixed-width and the column boundaries
    move between eras.
    """
    path = RAW / "2001" / "house-members-elected-2001.txt"
    if not path.exists():
        raise SourceShapeChanged(f"{path} is missing. Re-fetch and re-verify.")

    lines = path.read_text(encoding="latin-1").splitlines()
    start = next(
        (i for i, line in enumerate(lines) if "Division" in line and "Party" in line),
        None,
    )
    if start is None:
        raise SourceShapeChanged(f"{path.name}: no Members Elected header found.")

    want = ABBREVIATION_BY_YEAR[FIXED_WIDTH_YEAR]
    rows: list[tuple[str, str]] = []
    elected = 0
    for line in lines[start + 1 :]:
        parts = line.split()
        if len(parts) >= 4 and re.fullmatch(r"[A-Z]{2,4}", parts[-1]):
            rows.append((parts[0], parts[-1].upper()))
            if parts[-1].upper() == want:
                elected += 1

    if len(rows) < 100:
        raise SourceShapeChanged(
            f"{path.name}: counted {len(rows)} members, which is not a House. "
            f"The column being read is probably not the party code."
        )
    return rows, elected


def seats_from_members_elected_2001() -> int:
    """Count 2001's elected members carrying the party's AEC code.

    The 2001 statistics have no by-party representation table for the House —
    Partyrep.txt lists only LP, NP, CLP, ALP and IND, with no HAN column at
    all — so the count comes from the members elected list instead. Zero is
    read as an absence of the code, which is what that table records; a
    division where the party won would show the code against that member.
    """
    path = RAW / "2001" / "house-members-elected-2001.txt"
    if not path.exists():
        raise SourceShapeChanged(f"{path} is missing. Re-fetch and re-verify.")

    lines = path.read_text(encoding="latin-1").splitlines()
    start = next(
        (i for i, line in enumerate(lines) if "Division" in line and "Party" in line),
        None,
    )
    if start is None:
        raise SourceShapeChanged(f"{path.name}: no Members Elected header found.")

    want = ABBREVIATION_BY_YEAR[FIXED_WIDTH_YEAR]
    elected = 0
    total = 0
    for line in lines[start + 1 :]:
        parts = line.split()
        if len(parts) >= 4 and re.fullmatch(r"[A-Z]{2,4}", parts[-1]):
            total += 1
            if parts[-1].upper() == want:
                elected += 1

    if total < 100:
        raise SourceShapeChanged(
            f"{path.name}: counted {total} members, which is not a House. The "
            f"column being read is probably not the party code."
        )
    return elected


if __name__ == "__main__":
    sys.exit(main())
