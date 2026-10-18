#!/usr/bin/env python3
"""Build the page: inject generated SVG into the hand-written template.

The separation this enforces is the whole reason the stack was locked. Prose
lives in src/index.template.html and is never generated. Charts are generated
into charts/*.svg by their own modules and injected here. Nothing else moves.

Stdlib only. Usage: python3 tools/build.py [--check]

--check validates without writing, for use in CI.
"""

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "src" / "index.template.html"
OUTPUT = ROOT / "index.html"
CHART_DIR = ROOT / "charts"
DATA_SOURCES = ROOT / "docs" / "data-sources.md"
CSS = ROOT / "src" / "margin-of-error.css"

PLACEHOLDER = re.compile(
    r"^\s*(?P<indent>[ \t]*)<!--\s*chart:(?P<id>\d+)\s*-->\s*$", re.MULTILINE
)

# Literal markers that must never reach a reader. The chart placeholder check
# covers `<!-- chart:NN -->`; this covers prose the author left unfinished.
# Both ship. A missing chart is obvious; an unfinished caption is not.
PROSE_PLACEHOLDERS = ("PLACEHOLDER", "TBD", "TODO", "XXX", "Lorem ipsum")

# A chart declares its own status, so the build can tell a sourced chart from a
# placeholder one. Until 0003 and 0004 exist, every chart must declare
# `data-unsourced="true"` AND that declaration must be recorded in
# docs/data-sources.md. A chart that claims to be sourced but cites nothing is
# the dangerous case, so that is what fails.
UNSOURCED_ATTR = re.compile(r'data-unsourced="(true|false)"')
SOURCE_ID_ATTR = re.compile(r'data-source-id="([^"]+)"')

# An unfilled slot in the prose. Refused rather than shipped: `{{gap_2019}}`
# reaching the reader is a promise unkept, and it looks finished.
SLOT = re.compile(r"\{\{(\w+)\}\}")


def figure_slots() -> dict[str, str]:
    """Every figure the prose states, computed once from the ingested data.

    The template carries `{{gap_2019}}`, never `+0.60`. A figure typed into a
    caption is a figure that stops agreeing with the chart beside it, and the
    drift is silent: the page keeps rendering and the sentence stops being
    true. The archived feasibility model printed 1.33% booth coverage while the
    prose describing it said "below 15%", with nothing in between to notice.

    So this calls charts/stats.py, the single derivation site, rather than
    recomputing anything. sys.path is adjusted here because the module lives
    under charts/ and this script lives under tools/.
    """
    sys.path.insert(0, str(ROOT / "charts"))
    from stats import gaps, load_polls, load_results, window_mean  # noqa: E402

    polls = load_polls(ROOT / "data" / "polls_roymorgan_oned.csv")
    # The same call the generator makes, against the same file. Caption and
    # figure are both computed from the AEC's record now that task 0003's
    # series is the result axis; if these two ever read different files the
    # page states one number while the chart beside it draws another.
    results = load_results(ROOT / "data" / "aec_election_results.csv")

    gaps_ = gaps(results, polls, WINDOW)
    if not gaps_:
        raise SystemExit(
            "no election has preceding waves, so no caption figure can be "
            "computed. Check the ingest before writing prose."
        )

    def signed(value: float) -> str:
        """A signed figure with a true minus sign, not a hyphen.

        U+2212. The chart emits the same character, so the caption and the
        figure agree glyph for glyph.
        """
        return f"\u2212{abs(value):.2f}" if value < 0 else f"+{value:.2f}"

    slots: dict[str, str] = {"waves_total": str(len(polls))}
    for g in gaps_:
        m = window_mean(polls, g.year, WINDOW)
        slots[f"gap_{g.year}"] = signed(g.signed_gap)
        slots[f"mean_{g.year}"] = f"{g.mean:.2f}"
        slots[f"waves_{g.year}"] = str(g.n_used)
        slots[f"result_{g.year}"] = f"{g.result:g}"
        slots[f"polled_low_{g.year}"] = f"{m.low:g}" if m else ""
        slots[f"polled_high_{g.year}"] = f"{m.high:g}" if m else ""

    # Chart 02's figures, from the AEC series. Same rule: read, never typed.
    with (ROOT / "data" / "aec_election_results.csv").open(
        encoding="utf-8", newline=""
    ) as fh:
        aec = list(csv.DictReader(fh))
    if aec:
        seats = sum(int(r["seats_won"]) for r in aec)
        slots["aec_elections"] = str(len(aec))
        slots["aec_first_year"] = aec[0]["election_year"]
        slots["aec_last_year"] = aec[-1]["election_year"]
        slots["aec_total_seats"] = str(seats)
        slots["aec_best_vote"] = f"{max(float(r['primary_vote_pct']) for r in aec):g}"
        slots["aec_best_vote_year"] = max(
            aec, key=lambda r: float(r["primary_vote_pct"])
        )["election_year"]
        large = max(int(r["chamber_size"]) for r in aec)
        small = min(int(r["chamber_size"]) for r in aec)
        slots["aec_chamber_small"] = str(small)
        slots["aec_chamber_large"] = str(large)
        slots["aec_chamber_large_from"] = min(
            r["election_year"] for r in aec if int(r["chamber_size"]) == large
        )

        slots["aec_chamber_small_to"] = max(
            r["election_year"] for r in aec if int(r["chamber_size"]) == small
        )

    # The low-coverage block Chart 02 shades. Read from the chart module's own
    # constants rather than typed here, so the caption cannot describe a
    # different span than the chart draws. This was wrong twice by hand: first
    # it said "2004 to 2016", then "2001 to 2016", which is the span the House
    # had 150 seats and is a different thing entirely.
    thin = _thin_coverage_span()
    if thin:
        slots["aec_thin_from"], slots["aec_thin_to"] = thin

    return slots


def _thin_coverage_span() -> tuple[str, str] | None:
    """The years Chart 02 marks as thinner slate coverage, or None."""
    sys.path.insert(0, str(ROOT / "charts"))
    try:
        import chart_02
    except Exception:
        return None
    return str(chart_02.THIN_COVERAGE_FROM), str(chart_02.THIN_COVERAGE_TO)


WINDOW = 12


def data_sources() -> str:
    """The registry text, read once per validation pass."""
    return DATA_SOURCES.read_text(encoding="utf-8")


def unsourced_figure_problems(name: str, svg: str, registry: str) -> list[str]:
    """Refuse a chart that is neither sourced nor declared a placeholder.

    This is the check task 0006 recorded as missing and task 0007 needs. A
    chart carries its provenance on the root `<svg>`, so it is greppable:

      data-source-id="aec-hor-2025 roymorgan-pvi"  sourced; each id must
                                                       resolve in the registry
      data-unsourced="true"                        a placeholder, and the
                                                       registry must say so

    A chart with neither attribute is refused outright. That is the case that
    matters: it looks finished, passes every accessibility rule, and nothing
    stops it being published with figures that resolve to no document at all.
    """
    problems: list[str] = []

    unsourced = UNSOURCED_ATTR.search(svg)
    source_ids = SOURCE_ID_ATTR.search(svg)

    if unsourced and source_ids:
        return [
            f"{name}: declares both data-unsourced=\"true\" and a source id. "
            f"A chart is sourced or it is a placeholder, never both."
        ]

    if source_ids:
        # Resolved against the parsed entries, not a substring of the raw text.
        # The two disagree for a `<year>` family: the registry holds
        # `aec-hor-<year>-fp-by-party` plus a `years:` list, so
        # `aec-hor-2019-fp-by-party` is a registered id but is not a substring
        # of the file. A substring test here refused a citation the artefact
        # gate accepted, so the two provenance checks disagreed about the same
        # id — and the disagreement looked like an unsourced chart.
        entries = _registry_entries(registry)
        for sid in source_ids.group(1).split():
            if sid not in entries:
                problems.append(
                    f'{name}: source id "{sid}" has no entry in '
                    f"docs/data-sources.md (non-negotiable 2)"
                )
        return problems

    if unsourced and unsourced.group(1) == "true":
        # Declared a placeholder. The registry must record that fact, so the
        # unsourced figures are visible to a reader auditing the repo rather
        # than being a private note in a Python file.
        stem = Path(name).stem
        if stem not in registry:
            problems.append(
                f"{name}: chart is declared data-unsourced=\"true\" but the "
                f"registry does not mention it. Record it in "
                f"docs/data-sources.md so the unsourced figures are auditable."
            )
        return problems

    problems.append(
        f"{name}: chart declares neither data-source-id nor "
        f'data-unsourced="true", so the build cannot tell whether its figures '
        f"are sourced. A sourced chart cites its source ids; a placeholder "
        f"declares itself. See task 0007 and docs/data-sources.md."
    )
    return problems


def find_placeholders(template: str) -> list[tuple[str, str]]:
    """Return (id, indent) for every chart placeholder in the template."""
    return [(m.group("id"), m.group("indent")) for m in PLACEHOLDER.finditer(template)]


def load_chart(chart_id: str) -> tuple[str, str | None]:
    """Return (wide svg, narrow svg or None) for a chart id.

    A narrow variant is optional per chart. A chart whose form has no mobile
    problem (a single ranked bar, say) legitimately ships one variant only, and
    forcing a second file on it would be noise.
    """
    stem = f"chart-{chart_id.zfill(2)}"
    path = CHART_DIR / f"{stem}.svg"
    if not path.exists():
        raise FileNotFoundError(
            f"placeholder <!-- chart:{chart_id} --> has no generated chart at "
            f"{path.relative_to(ROOT)}. Generate it first, or remove the "
            f"placeholder. The build does not ship an empty figure."
        )
    svg = path.read_text(encoding="utf-8").strip()
    if not svg.startswith("<svg"):
        raise ValueError(f"{path.name} does not start with <svg")

    narrow_path = CHART_DIR / f"{stem}-narrow.svg"
    narrow = None
    if narrow_path.exists():
        narrow = narrow_path.read_text(encoding="utf-8").strip()
        if not narrow.startswith("<svg"):
            raise ValueError(f"{narrow_path.name} does not start with <svg")
    return svg, narrow


def reindent(svg: str, pad: str) -> str:
    return "\n".join((pad + ln) if ln.strip() else ln for ln in svg.split("\n"))


def add_narrow_attrs(svg: str) -> str:
    """Mark a generated SVG as the narrow variant, by rewriting its root tag.

    Adds the marker class the stylesheet keys on, and hides it from assistive
    technology at wide widths where the wide variant is the one being read.
    """
    # Match the opening tag properly. A naive partition on the first ">"
    # truncates the tag, because viewBox carries ">" inside its quotes only
    # in malformed input; more importantly the class attribute must be merged
    # into an existing class list rather than appended as a second attribute.
    match = re.match(r"<svg\b[^>]*>", svg)
    assert match, f"narrow chart has no root <svg> tag: {svg[:60]}"
    tag = match.group(0)
    if "chart-narrow" in tag:
        return svg

    existing = re.search(r'class="([^"]*)"', tag)
    if existing:
        new_class = existing.group(1) + " chart-narrow"
        tag = tag[: existing.start()] + f'class="{new_class}"' + tag[existing.end() :]
    else:
        tag = tag[:4] + ' class="chart chart-narrow"' + tag[4:]

    rest = svg[match.end() :]

    # IDs must be unique across the document. Both variants ship in the same
    # page, so the narrow copy's ids are suffixed, and its internal references
    # (aria-labelledby, url(#hatch-mo)) are rewritten to match. Without this,
    # aria-labelledby on the narrow chart resolves to the WIDE chart's title
    # and desc, and both charts claim the same pattern id.
    # Only the `id` ATTRIBUTE, never `data-source-id`. The lookbehind is doing
    # real work: `data-source-id="roymorgan-pvi"` ends in `id="`, so a bare
    # `id="([^"]+)"` scan collects the provenance key as though it were an
    # element id, and the pass below appends `-narrow` to it. The page then
    # cites `roymorgan-pvi-narrow`, an id that exists in no registry, and the
    # unknown-id gate refuses it — so the build cannot write, which is how the
    # committed artefact went stale without anyone being told.
    ids = re.findall(r'(?<![-\w])id="([^"]+)"', tag + rest)
    for original in ids:
        suffixed = f"{original}-narrow"
        rest = rest.replace(f'id="{original}"', f'id="{suffixed}"')
        tag = tag.replace(f'id="{original}"', f'id="{suffixed}"')
        # rewrite internal url(#id) references in the body
        rest = rest.replace(f"url(#{original})", f"url(#{suffixed})")

    # aria-labelledby is rewritten last, as a whole attribute, and by token
    # rather than by prefix.
    #
    # The previous version did `tag.replace(f'aria-labelledby="{original}', ...)`
    # inside the loop above, which only matches when the id is the FIRST token
    # of the attribute. `aria-labelledby="chart-01-title chart-01-desc"` has
    # two ids, so the title was suffixed and the desc was not: the narrow chart
    # pointed at the WIDE chart's desc while its own desc went unreferenced.
    #
    # That is invisible in the SVG, passes every id-resolves check because the
    # referenced id does exist, and is read aloud by a screen reader as the
    # wrong chart's description. Found by measuring aria-labelledby against the
    # ids each SVG actually contains.
    own_ids = set(ids)

    def _suffix_labelledby(match: re.Match) -> str:
        tokens = match.group(1).split()
        rewritten = [f"{t}-narrow" if t in own_ids else t for t in tokens]
        return f'aria-labelledby="{" ".join(rewritten)}"'

    tag = re.sub(r'aria-labelledby="([^"]+)"', _suffix_labelledby, tag)

    return tag + rest


DRAFT_MARKER = "data-draft"
ROBOTS_NOINDEX = '<meta name="robots" content="noindex" />'


def draft_banner(problems: Sequence[str]) -> str:
    """The visible notice on a page built while a publication gate is red.

    A draft artefact must not be mistakable for a publishable one, by a human
    opening the file or by a search engine finding it. So it carries a
    `noindex`, and a banner. The banner counts the outstanding gates rather
    than quoting them: the gate text names files and columns, which belongs in
    a build log and not on a page a reader might screenshot.

    Uses no raw hex and no prose placeholder, so it survives `validate()`
    rather than tripping the rules it sits inside.
    """
    n = len(problems)
    detail = f"{n} outstanding publication {'gate' if n == 1 else 'gates'}" if n else (
        "no outstanding gates"
    )
    return (
        f'<div class="draft-banner" {DRAFT_MARKER}="true">'
        "<p><strong>Not for publication.</strong></p>"
        f"<p>This page was built from data with {detail}. The figures are "
        "current with the data in the repository, and the sourcing has not "
        "been confirmed.</p></div>"
    )


def mark_draft(html: str, problems: Sequence[str]) -> str:
    """Add the noindex and the banner to an otherwise correct page."""
    if DRAFT_MARKER in html:
        return html
    out = html.replace("<head>", f"<head>\n    {ROBOTS_NOINDEX}", 1)
    if ROBOTS_NOINDEX not in out:
        raise SystemExit(
            "could not add the draft noindex: the template has no <head> to "
            "mark. A draft page that can be indexed is not a draft."
        )
    out = out.replace("<body>", f"<body>\n    {draft_banner(problems)}", 1)
    if DRAFT_MARKER not in out:
        raise SystemExit(
            "could not add the draft banner: the template has no <body> to "
            "mark. A draft page that looks publishable is not a draft."
        )
    return out


def build(template: str) -> str:
    out = template
    for chart_id, indent in find_placeholders(template):
        wide, narrow = load_chart(chart_id)
        pad = " " * (len(indent.expandtabs(2)) + 2)

        if narrow:
            # Both variants ship as SIBLINGS in the DOM so the accessibility
            # tree carries the chart at every width, rather than only whichever
            # one the browser picked. CSS media queries decide which is laid
            # out; see the .chart-narrow rules in the stylesheet.
            #
            # <picture> is deliberately NOT used: its source switching applies
            # to raster and <img>, and does not media-switch two inline <svg>
            # elements. Verified in a browser.
            #
            # The narrow SVG is a sibling, never a child. Wrapping one <svg> in
            # another produced invalid nesting with no viewBox on the outer
            # element, which is what the first attempt did.
            narrow_svg = add_narrow_attrs(narrow)
            body = reindent(wide, pad) + f"\n{pad}" + reindent(narrow_svg, pad)
        else:
            body = reindent(wide, pad)

        out = out.replace(
            f"{indent}<!-- chart:{chart_id} -->",
            f'<figure class="col-full" data-chart="{chart_id}">\n{body}'
            f"\n{' ' * len(indent.expandtabs(2))}</figure>",
        )

    # Prose figures, substituted after the charts so a caption can state a
    # number the chart beside it draws.
    slots = figure_slots()
    out = SLOT.sub(lambda m: slots.get(m.group(1), m.group(0)), out)

    unfilled = sorted(set(SLOT.findall(out)))
    if unfilled:
        raise SystemExit(
            f"unfilled figure slots in the built page: {', '.join(unfilled)}. "
            f"Declared in the template but absent from figure_slots(). An "
            f"unfilled slot ships braces and a promise to the reader."
        )
    return out


# --- Publication gates ------------------------------------------------------
#
# Each of these refuses a specific, named way for a wrong figure to reach a
# reader. They are separate functions rather than one validator because each
# has to be provable on its own: a test that mutates one input and expects one
# named failure. An assertion bundled with others cannot be shown to fire.
#
# The first of these is expected to fail until task 0003 delivers AEC-confirmed
# results. That is the gate working. Do not loosen it to make the build green.

CROSS_CHECK_FIELD = re.compile(
    r"^source_id:\s*(?P<sid>\S+)\s*$", re.MULTILINE
)
YEARS_FIELD = re.compile(r"^years:[ \t]*(?P<years>[0-9, \t]+)$", re.MULTILINE)


def _registry_entries(registry: str) -> dict[str, bool]:
    """Map each source id to whether it is marked cross-check-only.

    Parsed by scanning for `source_id:` lines and reading the
    `cross_check_only: yes` that follows each, so an id is cross-check-only
    only if its own block says so. Matching the id and the flag independently
    would let one entry's flag mark a different entry's id.

    An id containing `<year>` is a FAMILY, and a family registers nothing on
    its own: `aec-hor-<year>-fp-by-party` is not an id any chart can cite. It is
    expanded against the block's own `years:` list, so citing
    `aec-hor-2019-fp-by-party` resolves. Without this, seven of the nine AEC
    elections in `data/aec_election_results.csv` are unciteable, and the only
    reason Chart 02 passed is that it happens to cite the two years (2001 and
    2025) that were also written up individually.

    A family block with no `years:` list is a defect, not an empty set, so it
    registers nothing and every citation against it is refused.
    """
    entries: dict[str, bool] = {}
    current: str | None = None
    for line in registry.splitlines():
        stripped = line.strip()
        m = CROSS_CHECK_FIELD.match(stripped)
        if m:
            current = m.group("sid")
            for sid in _expand_family(current, registry):
                entries.setdefault(sid, False)
            continue
        if current and re.match(r"^\s*cross_check_only:\s*yes\s*$", line):
            for sid in _expand_family(current, registry):
                entries[sid] = True
    return entries


def _expand_family(sid: str, registry: str) -> list[str]:
    """Concrete ids for a `source_id`, expanding any `<year>` family.

    The year list is read from the same block, between this `source_id:` line
    and the next, so a family cannot borrow another block's years.
    """
    if "<year>" not in sid:
        return [sid]

    block = _family_block(sid, registry)
    if block is None:
        return []
    m = YEARS_FIELD.search(block)
    if not m:
        return []
    years = [y.strip() for y in m.group("years").split(",") if y.strip()]
    return [sid.replace("<year>", y) for y in years]


def _family_block(sid: str, registry: str) -> str | None:
    """The registry lines belonging to one `source_id`, up to the next one."""
    escaped = re.escape(sid)
    start = re.search(rf"^source_id:[ \t]*{escaped}[ \t]*$", registry, re.MULTILINE)
    if not start:
        return None
    rest = registry[start.end() :]
    nxt = re.search(r"^source_id:", rest, re.MULTILINE)
    return rest[: nxt.start()] if nxt else rest


def unsourced_result_problems(name: str, svg: str, registry: str) -> list[str]:
    """Refuse a chart whose every source is a cross-check, not a source of record.

    Roy Morgan is a cross-check for the 2019 and 2022 results, not the AEC's
    record. AGENTS.md non-negotiable 2 requires every number to resolve to a
    primary source, so a chart resting only on cross-checks must not ship.

    The rule is "fails if EVERY resolved id is cross-check-only", not "fails if
    any is". Chart 02 draws on a cross-checked poll series and confirmed AEC
    results, and it ships. And an id absent from the registry is not treated as
    cross-check-only here — `unsourced_figure_problems` refuses unknown ids
    separately and more precisely.
    """
    ids = SOURCE_ID_ATTR.search(svg)
    if not ids:
        return []  # a chart declaring nothing is unsourced_figure_problems' job

    entries = _registry_entries(registry)
    resolved = [s for s in ids.group(1).split() if s in entries]
    if not resolved:
        return []  # nothing resolvable; the unknown-id check reports it

    cross_checked = [s for s in resolved if entries[s]]
    if cross_checked and len(cross_checked) == len(resolved):
        return [
            f"{name}: every source it cites is a cross-check rather than a "
            f"source of record ({', '.join(cross_checked)}). Non-negotiable 2 "
            f"requires a primary source. This clears when task 0003 confirms "
            f"the AEC results; it must not be worked around."
        ]
    return []


def poll_field_problems(rows: Sequence[dict]) -> list[str]:
    """Refuse an imputed margin or an undated wave, naming the wave.

    `margin_of_error` must be empty. A populated value is either a genuine
    change of source or a figure computed from an assumed sample size, and the
    second is prohibited by non-negotiable 5. The two are not told apart
    because the safe response is the same: go and check the source.

    `fielded_start` must be present. An undated poll cannot be ordered against
    an election or placed on a time axis.
    """
    problems: list[str] = []
    for row in rows:
        wave = row.get("wave") or row.get("wave_label") or "<unnamed wave>"
        margin = (row.get("margin_of_error") or "").strip()
        if margin:
            problems.append(
                f"wave {wave!r} carries margin_of_error={margin!r}. Either the "
                f"source now publishes one and the registry must record that, "
                f"or the value was computed from an assumed sample size, which "
                f"non-negotiable 5 prohibits. Never impute."
            )
        if not (row.get("fielded_start") or "").strip():
            problems.append(
                f"wave {wave!r} has no field window. An undated poll cannot be "
                f"ordered against an election or placed on a time axis."
            )
    return problems


def plotted_row_problems(
    rows: Sequence[dict], bye_years: set[str] | None = None
) -> list[str]:
    """Refuse a by-election inside a general-election series.

    A by-election is one division on its own electorate. Plotted on a national
    series drawn against 150 or 151 seats it asserts comparability that does not
    exist, and it is the mistake most likely to be made silently because the
    row looks exactly like any other.

    Two ways in, both checked. A row may flag itself with is_by_election=yes,
    or the by-election may be in the separate by-election file and then appear
    in the plotted series too. The overlap check is the one that matters: a row
    that says nothing about what it is has to be caught by the other file.
    """
    problems = [
        f"election {row.get('year')} is flagged is_by_election=yes and cannot "
        f"be plotted on the general-election series. A by-election is one "
        f"division on its own electorate, with its own denominator. Annotate "
        f"it instead."
        for row in rows
        if (row.get("is_by_election") or "").strip().lower() == "yes"
    ]
    for row in bye_years or set():
        if any(str(r.get("election_year")) == row for r in rows):
            problems.append(
                f"election {row} is a by-election and appears in the "
                f"general-election series. It may only be annotated."
            )
    return problems


def label_count_problems(pairs: dict[int, tuple[int, int]]) -> list[str]:
    """Refuse a stated wave count that disagrees with the arithmetic.

    Takes {year: (stated, used)}. This is the check that would have caught the
    49-versus-48 slip: a caption saying "twelve waves" beside a mean actually
    taken over five is a true-looking sentence about the wrong quantity.
    """
    return [
        f"{year}: the page states {stated} wave(s) but {used} were used. A "
        f"figure labelled with the wrong count is a true-looking sentence "
        f"about the wrong quantity."
        for year, (stated, used) in sorted(pairs.items())
        if stated != used
    ]


# Figures only a dataset could produce. Layout numbers like 0.60 or 5.0 are
# excluded on purpose: a substring test cannot distinguish a panel fraction
# from a poll result, so this lists the figures that are unambiguous.
DATASET_LITERALS = ("3.70", "3.71", "1.29", "4.34", "39.53", "57.55")


def generator_literal_problems(sources: dict[str, str]) -> list[str]:
    """Refuse a dataset figure typed into a generator instead of computed.

    Matched as whole numbers, not substrings: "4.34" in a docstring is not a
    transcribed 4.3%, and a test that cannot tell the two apart trains people to
    ignore it.
    """
    problems: list[str] = []
    for name, src in sources.items():
        for value in DATASET_LITERALS:
            pattern = re.compile(rf"(?<![\d.]){re.escape(value)}(?![\d])")
            if pattern.search(src):
                problems.append(
                    f"{name}: {value} appears as a literal. Chart figures are "
                    f"computed from the ingested data; a transcribed figure is "
                    f"a figure that stops agreeing with its source."
                )
    return problems


def blank_reason_problems(rows: Sequence[dict], span: tuple[int, int]) -> list[str]:
    """Refuse a wave outside the charted range without a stated reason.

    A wave the chart does not show, carrying no explanation, is a hole in the
    series that a reader cannot see and a maintainer cannot account for.
    """
    lo, hi = span
    return [
        f"wave {row.get('wave') or '<unnamed>'} ({row.get('year')}) falls "
        f"outside the charted range {lo} to {hi} and declares no blank_reason."
        for row in rows
        if not lo <= int(row.get("year") or 0) <= hi
        and not (row.get("blank_reason") or "").strip()
    ]


def seat_denominator_problems(rows: Sequence[dict], expected_small: int) -> list[str]:
    """Refuse a seat share computed against anything but the real chamber size.

    The House returned 150 seats to 2016 and 151 from 2019, so a fixed
    denominator is wrong for part of the series and the error is invisible,
    because the seat line is drawn against zero either way.
    """
    allowed = {expected_small, expected_small + 1}
    problems: list[str] = []
    for row in rows:
        size = int(row.get("chamber_size") or 0)
        year = int(row.get("election_year") or 0)
        if size not in allowed:
            problems.append(
                f"election {row.get('election_year')}: chamber_size={size}. "
                f"Expected {expected_small} or {expected_small + 1}; the House "
                f"changed size in 2019 and each share must be taken against "
                f"the chamber as it was."
            )
        elif year < 2019 and size != expected_small:
            # The subtler defect: a real number attached to the wrong election.
            problems.append(
                f"election {year}: chamber_size={size}, but the House had "
                f"{expected_small} seats until 2019. The right number on the "
                f"wrong election is still wrong."
            )
        seats = int(row.get("seats_won") or 0)
        if size and seats > size:
            problems.append(
                f"election {row.get('election_year')}: {seats} seats in a "
                f"{size}-seat House is corrupt data and would draw a 100% line."
            )
    return problems


def chamber_axis_problems(svg: str) -> list[str]:
    """Refuse House and Senate figures sharing one axis.

    The two chambers have different sizes and different quotas, so a shared
    scale compares two different denominators and the visual gap means nothing.
    AGENTS.md gotchas names this trap.
    """
    has_house = "house of representatives" in svg.lower()
    has_senate = bool(re.search(r"\bsenate\b", svg, re.IGNORECASE))
    if has_house and has_senate:
        return [
            "the chart names both the House of Representatives and the Senate. "
            "They have different sizes and different quotas; one axis cannot "
            "compare both."
        ]
    return []


def caption_count_problems(stated: int, used: int) -> list[str]:
    """Refuse a caption wave count that disagrees with the rows behind it."""
    if stated == used:
        return []
    return [
        f"the caption states {stated} wave(s) but {used} rows were used to "
        f"compute the figures beside it."
    ]


def _read_csv(path: Path) -> list[dict]:
    """Read a CSV into dicts, or return empty if it is missing.

    Missing data is not itself a gate failure: the gates report what they can
    check, and a missing file makes every gate on it pass vacuously. A missing
    chart is still caught outright by load_chart.
    """
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _stated_wave_counts() -> dict[str, int]:
    """Wave counts the means were computed from, recomputed from the data.

    Recomputed here rather than read back from figure_slots() on purpose: the
    gate compares what the page *says* against what the arithmetic *did*. Both
    read from one dict would compare a value with itself and pass on any drift.
    """
    sys.path.insert(0, str(ROOT / "charts"))
    from stats import gaps, load_polls, load_results, window_mean  # noqa: E402

    polls = load_polls(ROOT / "data" / "polls_roymorgan_oned.csv")
    # Independent recomputation from the AEC series, which is what the chart
    # draws. Recomputed here rather than read back from figure_slots() on
    # purpose: the gate compares what the page *says* against what the
    # arithmetic *did*. Both reading from one dict would compare a value with
    # itself and pass on any drift.
    results = load_results(ROOT / "data" / "aec_election_results.csv")
    out: dict[str, int] = {}
    for g in gaps(results, polls, WINDOW):
        m = window_mean(polls, g.year, WINDOW)
        if m:
            out[str(g.year)] = m.n_used
    return out


WAVE_TOTAL_IN_PAGE = re.compile(
    r"(\d+)\s+waves?\s+in\s+this\s+series", re.IGNORECASE
)


def _stated_wave_total_in_html(html: str) -> int | None:
    """The wave total as the built page states it, or None if it does not.

    Read out of the rendered prose rather than out of figure_slots(), because
    a gate that reads the slot and compares it against the figure it was built
    from is comparing a value with itself and cannot fail.
    """
    m = WAVE_TOTAL_IN_PAGE.search(html)
    return int(m.group(1)) if m else None


def contiguous_years_from(rows: Sequence[dict]) -> tuple[int, int] | None:
    """The longest run of consecutive years carrying at least one wave."""
    years = sorted({int(r["year"]) for r in rows if r.get("year")})
    if not years:
        return None
    best = (years[0], years[0])
    start = end = years[0]
    for y in years[1:]:
        if y == end + 1:
            end = y
        else:
            start = end = y
        if (end - start) > (best[1] - best[0]):
            best = (start, end)
    return best


def validate(html: str, template: str) -> list[str]:
    """Fail the build on the defects that matter most. Not a full HTML lint."""
    problems: list[str] = []

    if 'lang="en-AU"' not in html:
        problems.append("missing lang=en-AU (AGENTS.md requires en-AU)")

    if html.count("<h1") != 1:
        problems.append(f"expected exactly one h1, found {html.count('<h1')}")

    if html.count("<main") != 1:
        problems.append(f"expected exactly one main landmark, found {html.count('<main')}")

    # A placeholder that survived means a chart is missing from the page.
    leftovers = PLACEHOLDER.findall(html)
    if leftovers:
        ids = ", ".join(i for i, _ in leftovers)
        problems.append(f"unfilled chart placeholders remain: {ids}")

    # Placeholder PROSE ships just as visibly as a missing chart. The chart
    # check above cannot see it: the caption and source note are hand-written
    # in the template, so a chart can pass every accessibility rule while the
    # reader is still served "PLACEHOLDER SOURCE NOTE" in the figure block.
    # That is the whole caption, which is where the citation lives, so it is
    # the one string on the page a hostile reader most wants to quote.
    for lineno, line in enumerate(template.split("\n"), 1):
        for marker in PROSE_PLACEHOLDERS:
            if marker in line:
                problems.append(
                    f"src/index.template.html:{lineno}: placeholder prose "
                    f'"{marker}" ships to the reader; replace it with the real '
                    f"caption and citation or remove the figure"
                )

    # Every generated SVG must carry its accessible name. A chart that cannot
    # be read with images off does not ship (DESIGN.md accessibility floor).
    for chart_id, _ in find_placeholders(template):
        stem = f"chart-{chart_id.zfill(2)}"
        for name in (f"{stem}.svg", f"{stem}-narrow.svg"):
            chart = CHART_DIR / name
            if not chart.exists():
                continue
            svg = chart.read_text(encoding="utf-8")
            if 'role="img"' not in svg:
                problems.append(f"{name}: missing role=\"img\"")
            if "<title" not in svg:
                problems.append(f"{name}: missing <title>")
            if "<desc" not in svg:
                problems.append(f"{name}: missing <desc>")
            problems.extend(unsourced_figure_problems(name, svg, data_sources()))
            problems.extend(unsourced_result_problems(name, svg, data_sources()))
            problems.extend(chamber_axis_problems(svg))
            problems.extend(generator_literal_problems(
                {
                    f"charts/chart_{chart_id}.py": (
                        CHART_DIR / f"chart_{chart_id}.py"
                    ).read_text(encoding="utf-8")
                    if (CHART_DIR / f"chart_{chart_id}.py").exists()
                    else ""
                }
            ))

    # ---- The data-side gates -------------------------------------------
    #
    # These read the ingested files rather than the page, because the defect
    # they catch is in the data the page was built from. Each one is given the
    # figures it needs so it can be tested on its own.

    polls = _read_csv(ROOT / "data" / "polls_roymorgan_oned.csv")
    problems.extend(poll_field_problems(polls))

    # The caption states how many waves the series holds. That number is
    # derived from the same file, so comparing the slot against len(rows)
    # compares a value with itself and can never fire — the first version of
    # this gate did exactly that and passed on a row deleted from the data.
    #
    # The check that means something compares the *rendered page* against the
    # data. If the number a reader sees disagrees with the number of rows behind
    # it, the page misstates its own series, and that is falsifiable: edit the
    # built HTML and the gate fires.
    stated_waves = _stated_wave_total_in_html(html)
    if stated_waves is None:
        problems.append(
            "the built page states no wave total, so the caption cannot be "
            "checked against the data. Either the slot is missing or the "
            "sentence was reworded past recognition."
        )
    else:
        problems.extend(caption_count_problems(stated_waves, len(polls)))

    aec = _read_csv(ROOT / "data" / "aec_election_results.csv")
    problems.extend(seat_denominator_problems(aec, expected_small=150))
    # A by-election must never reach the general-election series. The by-election
    # lives in its own file precisely so it cannot drift in here, so the check
    # is that the two do not overlap: a by-election year appearing in the
    # general-election series means a row was copied across, and the gate has
    # to be able to say so.
    #
    # The first version tagged every plotted row is_by_election="no" before
    # checking it, which made the assertion unfalsifiable — it compared each
    # row against a value it had just been given. It passed on a by-election
    # added to the file.
    byes = _read_csv(ROOT / "data" / "aec_by_election.csv")
    bye_years = {str(r.get("election_year")) for r in byes if r.get("election_year")}
    problems.extend(plotted_row_problems(aec, bye_years=bye_years))
    for row in byes:
        if (row.get("plottable_on_general_election_series") or "").strip() != "no":
            problems.append(
                f"the by-election row for {row.get('division')} is marked "
                f"plottable on the general-election series. A by-election is "
                f"one division on its own electorate; it may only ever be "
                f"annotated."
            )

    # The caption's wave count against the rows behind it, and each election's
    # stated wave count against the mean actually taken over that many waves.
    try:
        slots = figure_slots()
        stated_waves = int(slots["waves_total"])
        problems.extend(caption_count_problems(stated_waves, len(polls)))

        # Each election's stated wave count against the count actually used.
        used = _stated_wave_counts()
        stated: dict[int, tuple[int, int]] = {}
        for year, n_used in used.items():
            key = f"waves_{year}"
            if key not in slots:
                continue
            stated[int(year)] = (int(slots[key]), n_used)
        problems.extend(label_count_problems(stated))
    except (KeyError, SystemExit, ValueError) as exc:
        problems.append(f"could not check the caption figures: {exc}")

    span = contiguous_years_from(polls)
    if span:
        problems.extend(blank_reason_problems(polls, span))

    # Every internal reference must resolve, including the ones only the print
    # stylesheet reaches. A dangling url(#hatch-mo-print) drops the uncertainty
    # band to no fill, which on paper is precisely what DESIGN.md:212 exists to
    # prevent: an interval that reads as a plain shape, indistinguishable from
    # a series line.
    ids = set(re.findall(r'id="([^"]+)"', html))

    # References the stylesheet makes into the SVG, which never appear in the
    # markup at all. The print block swaps the band fill to a coarser pattern,
    # so a typo there is invisible in the HTML and silently drops the hatch on
    # paper. Check the stylesheet's url(#...) targets too.
    css = CSS.read_text(encoding="utf-8") if CSS.exists() else ""
    # Exact match only, plus the one suffix the build itself appends to the
    # narrow variant's ids. A looser "starts with" test was tried and masks the
    # wide chart: a broken wide id still matched the narrow "-narrow" copy, so
    # the defect passed. Every reference must resolve for the variant that
    # actually uses it.
    for ref in sorted(set(re.findall(r"url\(#([^)]+)\)", css))):
        if ref not in ids:
            problems.append(
                f"stylesheet references url(#{ref}) but no element carries that "
                f"id; the print band will render with no fill"
            )

    for ref in sorted(set(re.findall(r"url\(#([^)]+)\)", html))):
        if ref not in ids:
            problems.append(
                f"fill references url(#{ref}) but no element carries that id; "
                f"the band will render with no fill"
            )
    for labelledby in re.findall(r'aria-labelledby="([^"]+)"', html):
        for token in labelledby.split():
            if token not in ids:
                problems.append(
                    f'aria-labelledby="{labelledby}" points at missing id '
                    f'"{token}"; the chart has no accessible name'
                )

    problems.extend(duplicate_id_problems(html))
    problems.extend(artefact_source_id_problems(html, data_sources()))

    # Raw hex is banned outside :root by the generative UI rules. The template
    # and stylesheet carry no hex at all, so any here came from a chart.
    for match in re.finditer(r'fill="(#[0-9a-fA-F]{3,8})"', html):
        problems.append(f"chart uses raw hex fill {match.group(1)}; use var(--token)")

    for chart_id, _ in find_placeholders(template):
        stem = f"chart-{chart_id.zfill(2)}"
        for name in (f"{stem}.svg", f"{stem}-narrow.svg"):
            chart = CHART_DIR / name
            if not chart.exists():
                continue
            problems.extend(degenerate_band_problems(name, chart.read_text("utf-8")))

    return problems


# A band polygon needs two distinct x values to have any width. This is the
# task 0002 defect: a lone banded poll beside a null-margin run collapsed to a
# zero-width shape, so a margin that WAS published rendered invisibly. The
# generator guards it with charts/scales.assert_no_degenerate_bands, but that
# only runs if someone remembers to run the generator. This asserts on the
# committed SVG, which is what actually ships.
ZERO_WIDTH_BAND = re.compile(
    r'<polygon\b[^>]*\bpoints="(?P<pts>[^"]+)"', re.IGNORECASE
)


def degenerate_band_problems(name: str, svg: str) -> list[str]:
    """Refuse a band polygon whose points all share one x.

    Catches the invisible-margin defect at the artefact boundary rather than
    trusting the generator to have been run.
    """
    problems: list[str] = []

    for i, match in enumerate(ZERO_WIDTH_BAND.finditer(svg), 1):
        xs: set[str] = set()
        for pair in match.group("pts").split():
            x, _, _y = pair.partition(",")
            try:
                xs.add(f"{float(x):.2f}")
            except ValueError:
                problems.append(f"{name}: band polygon {i} has unreadable point '{pair}'")
        if len(xs) < 2:
            problems.append(
                f"{name}: band polygon {i} covers {len(xs)} distinct x value(s) "
                f"({sorted(xs)}), so its interval renders with zero width and a "
                f"published margin becomes invisible. Render single-poll runs as "
                f"a vertical whisker with a cap (charts/scales.py)."
            )

    # A whisker is the correct rendering for a lone banded point, but a line
    # element is ambiguous on its own (the zero rule is also a <line>), so the
    # polygon check above is the real gate. Nothing further to assert here.

    return problems


def drift_problems(expected: str) -> list[str]:
    """Compare the committed artefact with what the sources build.

    `index.html` is committed, so it can be hand-edited or simply left behind
    when a source changes. Both are the same defect: the page readers get is
    not the page the pipeline produces.

    This must be given the marked page when a gate is red, not the unmarked
    one, because the artefact under a red gate IS the draft. Comparing against
    the unmarked build would report drift on every commit made while the gate
    is closed, which is the state this repository is in by design.

    The old version of this check lived only in the CI workflow, in a step
    ordered after a step that fails by design, so it never ran. It also ran
    `build.py` with no arguments, which overwrote the file it was about to
    compare.
    """
    if not OUTPUT.exists():
        return [
            f"{OUTPUT.relative_to(ROOT)} is missing; the committed artefact is "
            "part of the repository, so generate it"
        ]
    committed = OUTPUT.read_text(encoding="utf-8")
    if committed == expected:
        return []
    return [
        f"{OUTPUT.relative_to(ROOT)} does not match its sources "
        f"({len(committed.splitlines())} committed lines vs "
        f"{len(expected.splitlines())} built). Run `python3 tools/build.py"
        f"{' --draft' if DRAFT_MARKER in expected else ''}` and commit the result."
    ]


def artefact_source_id_problems(html: str, registry: str) -> list[str]:
    """Refuse a built page citing a source id the registry does not hold.

    The existing unknown-id check runs over the SOURCE files, where the
    provenance is written correctly. It cannot see a defect the build itself
    introduces, and the build rewrites ids on the narrow variant. So a page
    could cite `roymorgan-pvi-narrow` — an id in no registry — while every
    source file passed, and the gate would report nothing.

    That is exactly how the suffixing bug hid: the transformation was wrong,
    and the only code that looked at the wrong output was a check pointed at
    the right input.
    """
    problems: list[str] = []
    entries = _registry_entries(registry)
    for match in SOURCE_ID_ATTR.finditer(html):
        for sid in match.group(1).split():
            if sid not in entries:
                problems.append(
                    f"built page cites source id \"{sid}\", which has no entry "
                    f"in docs/data-sources.md. The source SVG is checked "
                    f"separately; this is the artefact, so the build itself "
                    f"produced an unresolvable provenance key."
                )
    return sorted(set(problems))


def duplicate_id_problems(html: str) -> list[str]:
    """Refuse a page where an id appears twice with different content.

    Every chart emits its own `<pattern id="hatch-mo">`, and the build suffixes
    only the narrow variant, so two wide charts in one page both declare
    `hatch-mo`. A `url(#hatch-mo)` reference resolves to whichever comes first
    in the document, so Chart 02's bands are currently painted by Chart 01's
    pattern.

    That is harmless while the patterns are identical, which they are, and
    silently wrong the moment one generator's density is changed — the change
    would have no effect on the page and nothing would say so. This is the same
    shape as the narrow variant referencing the wide chart's pattern id, one
    level up.

    So the rule is: a duplicate id is refused unless every element carrying it
    is byte-identical. Identical duplicates are inert; divergent ones are the
    defect. Fixing the root cause properly means scoping pattern ids per chart,
    which breaks the single `.chart-narrow .band` stylesheet rule that exists to
    swap the fill, so that is a design decision rather than a side effect.
    """
    problems: list[str] = []
    seen: dict[str, list[str]] = {}
    for match in re.finditer(
        r'<(?P<tag>pattern|linearGradient|radialGradient|clipPath|marker|filter)\b[^>]*\bid="(?P<sid>[^"]+)"',
        html,
    ):
        name = match.group("sid")
        end = html.find(f"</{match.group('tag')}>", match.start())
        if end == -1:
            continue
        seen.setdefault(name, []).append(html[match.start() : end])

    for sid, blocks in sorted(seen.items()):
        if len(blocks) < 2:
            continue
        distinct = set(blocks)
        if len(distinct) > 1:
            problems.append(
                f'duplicate id="{sid}" with DIFFERENT content in the page: '
                f"{len(blocks)} elements claim it and {len(distinct)} differ. "
                "Every url(#" + sid + ") resolves to the first, so the others "
                "are dead. Scope the id per chart."
            )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the page and the committed artefact, do not write",
    )
    parser.add_argument(
        "--draft",
        action="store_true",
        help="write the artefact even while a publication gate is red, "
        "marked noindex and with a banner",
    )
    args = parser.parse_args()

    if not TEMPLATE.exists():
        print(f"error: template missing at {TEMPLATE}", file=sys.stderr)
        return 1

    template = TEMPLATE.read_text(encoding="utf-8")

    placeholders = find_placeholders(template)
    if not placeholders:
        print("note: no chart placeholders in the template, page has no figures yet")

    try:
        html = build(template)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    problems = validate(html, template)

    # The artefact a fresh build SHOULD produce, given the data state. When a
    # gate is red the page is still built correctly and then marked, rather
    # than not built at all.
    #
    # Refusing to write was the original behaviour and it is the reason the
    # committed index.html went stale: while the gate was red the page could
    # not be regenerated, so three fixes to the sources never reached the
    # artefact, and nothing said so. A gate that blocks publication should not
    # also freeze the thing under review.
    expected = mark_draft(html, problems) if problems else html

    # Re-validate the marked page. The banner must not itself trip a rule; if
    # it did, the draft artefact would carry a defect the check never saw.
    if problems:
        after = validate(expected, template)
        if len(after) != len(problems):
            print(
                "error: the draft banner changed the validation result "
                f"({len(problems)} -> {len(after)} problems), so the marked "
                "page is not the page the gate judged.",
                file=sys.stderr,
            )
            for p in after:
                print(f"  - {p}", file=sys.stderr)
            return 1

    if args.check:
        # Drift is checked here rather than only in the workflow, because the
        # gate is red by design and a CI step ordered after a failing step
        # never runs. The drift check was written, and could not fire.
        drift = drift_problems(expected)
        for p in problems:
            print(f"  - gate: {p}", file=sys.stderr)
        for p in drift:
            print(f"  - drift: {p}", file=sys.stderr)
        if problems or drift:
            print(
                f"check failed: {len(problems)} gate(s), {len(drift)} drift "
                f"problem(s)",
                file=sys.stderr,
            )
            return 1
        print("check passed: gates clear, artefact current")
        return 0

    if problems and not args.draft:
        print("publication gates are red:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print(
            "\nnothing written. Re-run with --draft to build the page anyway, "
            "marked noindex and bannered, for review.",
            file=sys.stderr,
        )
        return 1

    OUTPUT.write_text(expected, encoding="utf-8")
    size = OUTPUT.stat().st_size
    state = "DRAFT" if problems else "final"
    print(
        f"wrote {state} {OUTPUT.relative_to(ROOT)} ({size:,} bytes) from "
        f"{TEMPLATE.relative_to(ROOT)} + {len(placeholders)} chart(s)"
    )
    if problems:
        print(
            f"NOT FOR PUBLICATION: {len(problems)} publication gate(s) still "
            "red. See tools/build.py --check.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
