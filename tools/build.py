#!/usr/bin/env python3
"""Build the page: inject generated SVG into the hand-written template.

The separation this enforces is the whole reason the stack was locked. Prose
lives in src/index.template.html and is never generated. Charts are generated
into charts/*.svg by their own modules and injected here. Nothing else moves.

Stdlib only. Usage: python3 tools/build.py [--check]

--check validates without writing, for use in CI.
"""

import argparse
import re
import sys
from pathlib import Path

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
        for sid in source_ids.group(1).split():
            if sid not in registry:
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
    ids = re.findall(r'id="([^"]+)"', tag + rest)
    for original in ids:
        suffixed = f"{original}-narrow"
        rest = rest.replace(f'id="{original}"', f'id="{suffixed}"')
        tag = tag.replace(f'id="{original}"', f'id="{suffixed}"')
        tag = tag.replace(f'aria-labelledby="{original}', f'aria-labelledby="{suffixed}')
        # rewrite any internal url(#id) references in the body
        rest = rest.replace(f"url(#{original})", f"url(#{suffixed})")

    return tag + rest


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
    return out


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true", help="validate only, do not write"
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

    if problems:
        print("build failed validation:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    if args.check:
        print("check passed: template valid, charts present and accessible")
        return 0

    OUTPUT.write_text(html, encoding="utf-8")
    size = OUTPUT.stat().st_size
    print(
        f"wrote {OUTPUT.relative_to(ROOT)} ({size:,} bytes) from "
        f"{TEMPLATE.relative_to(ROOT)} + {len(placeholders)} chart(s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
