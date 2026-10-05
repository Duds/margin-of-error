"""Tests for chart geometry.

Written because both bugs found while proving the stack in task 0002 were
silent: inverted axes and a zero-width band that hid a published margin. A
geometry bug in this project does not throw, it publishes a wrong chart.
"""

import csv
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "charts"))

from scales import (  # noqa: E402
    Box,
    Scale,
    assert_no_degenerate_bands,
    band_runs,
    fmt,
    nice_domain,
    ticks,
)


class TestBox(unittest.TestCase):
    def test_named_order_is_not_positional(self):
        """The task 0002 bug: padding unpacked in the wrong order."""
        box = Box(left=56, right=500, top=20, bottom=280)
        self.assertEqual(box.width, 444)
        self.assertEqual(box.height, 260)

    def test_inverted_box_is_rejected(self):
        with self.assertRaises(ValueError):
            Box(left=500, right=56, top=20, bottom=280)
        with self.assertRaises(ValueError):
            Box(left=56, right=500, top=280, bottom=20)

    def test_zero_area_is_rejected(self):
        with self.assertRaises(ValueError):
            Box(left=100, right=100, top=20, bottom=280)


class TestNiceDomain(unittest.TestCase):
    def test_snaps_outward_never_inward(self):
        lo, hi = nice_domain(0.043, 0.061, 0.02)
        self.assertLessEqual(lo, 0.043)
        self.assertGreaterEqual(hi, 0.061)

    def test_exact_values_are_unchanged(self):
        self.assertEqual(nice_domain(0.0, 0.1, 0.02), (0.0, 0.1))

    def test_non_positive_step_rejected(self):
        with self.assertRaises(ValueError):
            nice_domain(0, 1, 0)


class TestTicks(unittest.TestCase):
    def test_inclusive_of_both_bounds(self):
        """An axis from zero must carry the zero tick; that is the zero rule
        DESIGN.md keeps visible."""
        self.assertEqual(ticks(0.0, 0.1, 0.02), [0.0, 0.02, 0.04, 0.06, 0.08, 0.1])

    def test_excludes_bound_below_domain_start(self):
        self.assertEqual(ticks(0.03, 0.09, 0.02), [0.04, 0.06, 0.08])

    def test_no_duplicate_from_float_drift(self):
        vals = ticks(0.0, 1.0, 0.1)
        self.assertEqual(len(vals), len(set(vals)))

    def test_terminates(self):
        """A float drift must not produce an endless loop."""
        self.assertLess(len(ticks(0.0, 1.0, 0.01)), 200)


class TestScale(unittest.TestCase):
    def test_maps_domain_onto_range(self):
        s = Scale(d0=1996, d1=2004, r0=56, r1=500)
        self.assertAlmostEqual(s(1996), 56.0)
        self.assertAlmostEqual(s(2004), 500.0)
        self.assertAlmostEqual(s(2000), 278.0)

    def test_y_axis_is_inverted_but_consistent(self):
        """y grows downward in SVG, so r0 is the bottom."""
        s = Scale(d0=0.0, d1=0.1, r0=280, r1=20)
        self.assertAlmostEqual(s(0.0), 280.0)
        self.assertAlmostEqual(s(0.1), 20.0)
        self.assertLess(s(0.1), s(0.0))

    def test_degenerate_domain_rejected(self):
        with self.assertRaises(ValueError):
            Scale(d0=5, d1=5, r0=0, r1=1)(5)


class TestBandRuns(unittest.TestCase):
    def test_null_margin_breaks_the_band(self):
        rows = [
            {"x": 1, "lo": 0.1, "hi": 0.2},
            {"x": 2, "lo": None, "hi": None},
            {"x": 3, "lo": 0.3, "hi": 0.4},
        ]
        self.assertEqual([len(r) for r in band_runs(rows)], [1, 1])

    def test_contiguous_polls_stay_one_run(self):
        rows = [{"x": i, "lo": 0.1, "hi": 0.2} for i in range(5)]
        self.assertEqual([len(r) for r in band_runs(rows)], [5])

    def test_leading_null_does_not_emit_empty_run(self):
        rows = [{"x": 1, "lo": None, "hi": None}, {"x": 2, "lo": 0.2, "hi": 0.3}]
        self.assertEqual([len(r) for r in band_runs(rows)], [1])

    def test_all_null_yields_no_runs(self):
        rows = [{"x": i, "lo": None, "hi": None} for i in range(3)]
        self.assertEqual(band_runs(rows), [])


class TestDegenerateBandGuard(unittest.TestCase):
    """The defect found in task 0002: a published margin rendered invisible."""

    def setUp(self):
        self.x_of = Scale(d0=1996, d1=2004, r0=56, r1=500)

    def test_single_poll_run_is_rejected(self):
        runs = [[{"x": 1996, "lo": 0.04, "hi": 0.07}]]
        with self.assertRaises(AssertionError) as ctx:
            assert_no_degenerate_bands(runs, self.x_of, "chart-01")
        self.assertIn("zero width", str(ctx.exception))
        self.assertIn("whisker", str(ctx.exception))

    def test_multi_poll_run_passes(self):
        runs = [[{"x": 1996, "lo": 0.04, "hi": 0.07}, {"x": 1998, "lo": 0.05, "hi": 0.08}]]
        assert_no_degenerate_bands(runs, self.x_of, "chart-01")

    def test_null_split_produces_single_poll_runs(self):
        """The exact shape that triggered the defect."""
        rows = [
            {"x": 1996, "lo": 0.04, "hi": 0.07},
            {"x": 1998, "lo": None, "hi": None},
            {"x": 2001, "lo": 0.03, "hi": 0.06},
        ]
        runs = band_runs(rows)
        self.assertEqual([len(r) for r in runs], [1, 1])
        with self.assertRaises(AssertionError):
            assert_no_degenerate_bands(runs, self.x_of, "chart-01")


class TestFmt(unittest.TestCase):
    def test_rounds_honestly(self):
        self.assertEqual(fmt(0.041), "0.0")
        self.assertEqual(fmt(4.14, 1), "4.1")
        self.assertEqual(fmt(4.0, 1), "4.0")


class TestBuildAssertions(unittest.TestCase):
    """The build's guard rails, tested on the strings they are meant to catch.

    A validation rule that has never been seen to fail is indistinguishable from
    one that does not work. These assert the guard fires, not that the current
    content is clean.
    """

    @classmethod
    def setUpClass(cls):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "build", Path(__file__).resolve().parent.parent / "tools" / "build.py"
        )
        cls.build = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.build)

    REGISTRY = "source_id: aec-hor-2025"

    def test_chart_declaring_nothing_is_refused(self):
        """The case that matters: a chart that looks finished and cites nothing."""
        problems = self.build.unsourced_figure_problems(
            "chart-01.svg", '<svg role="img"><title>t</title></svg>', self.REGISTRY
        )
        self.assertEqual(len(problems), 1)
        self.assertIn("neither data-source-id nor", problems[0])

    def test_unknown_source_id_is_refused(self):
        problems = self.build.unsourced_figure_problems(
            "chart-01.svg",
            '<svg data-source-id="made-up-9999"></svg>',
            self.REGISTRY,
        )
        self.assertEqual(len(problems), 1)
        self.assertIn("made-up-9999", problems[0])

    def test_known_source_id_passes(self):
        self.assertEqual(
            self.build.unsourced_figure_problems(
                "chart-01.svg", '<svg data-source-id="aec-hor-2025"></svg>', self.REGISTRY
            ),
            [],
        )

    def test_claiming_both_is_refused(self):
        """A chart is sourced or a placeholder. Never both."""
        problems = self.build.unsourced_figure_problems(
            "chart-01.svg",
            '<svg data-unsourced="true" data-source-id="aec-hor-2025"></svg>',
            self.REGISTRY,
        )
        self.assertEqual(len(problems), 1)
        self.assertIn("never both", problems[0])

    def test_declared_placeholder_must_be_in_the_registry(self):
        """Unauditable unsourced figures are not allowed."""
        problems = self.build.unsourced_figure_problems(
            "chart-99.svg", '<svg data-unsourced="true"></svg>', self.REGISTRY
        )
        self.assertEqual(len(problems), 1)
        self.assertIn("registry does not mention it", problems[0])

    def test_zero_width_band_polygon_is_refused(self):
        """The task 0002 defect, caught at the artefact boundary.

        Two points at one x render a polygon with no width, so a published
        margin becomes invisible. Silent, and exactly what non-negotiable 5
        exists to prevent.
        """
        problems = self.build.degenerate_band_problems(
            "chart-01.svg", '<polygon points="687.0,100.0 687.0,200.0" />'
        )
        self.assertEqual(len(problems), 1)
        self.assertIn("zero width", problems[0])

    def test_proper_band_polygon_passes(self):
        self.assertEqual(
            self.build.degenerate_band_problems(
                "chart-01.svg", '<polygon points="100.0,50.0 200.0,80.0" />'
            ),
            [],
        )

    def test_placeholder_prose_is_flagged_with_a_line_number(self):
        """Prose ships to the reader, so it needs its own guard."""
        found = [m for m in self.build.PROSE_PLACEHOLDERS]
        self.assertIn("PLACEHOLDER", found)
        # The markers are literal and case-sensitive by design: "to do" in a
        # sentence is prose, "TODO" in a caption is a defect.
        self.assertNotIn("to do", found)

    def test_real_charts_pass_every_guard(self):
        """The committed charts must satisfy every rule above."""
        for name in ("chart-01.svg", "chart-01-narrow.svg"):
            svg = (Path(__file__).resolve().parent.parent / "charts" / name).read_text()
            self.assertEqual(
                self.build.unsourced_figure_problems(name, svg, self.build.data_sources()),
                [],
                f"{name} failed the sourcing guard",
            )
            self.assertEqual(
                self.build.degenerate_band_problems(name, svg),
                [],
                f"{name} failed the band guard",
            )


class TestRoyMorganColumnMapping(unittest.TestCase):
    """The trap AGENTS.md gotchas call out by name.

    Roy Morgan's monthly table has no discrete One Nation column. The party is
    folded into a combined "Other Parties (ALL)" cell that reads 18.5 for the
    April 2025 wave against One Nation at 7.5. A positional read overstates the
    party by more than double, and fails silently.

    These tests exist so the mapping cannot be "simplified" back to an offset.
    """

    @classmethod
    def setUpClass(cls):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "ingest",
            Path(__file__).resolve().parent.parent / "tools" / "ingest_roymorgan.py",
        )
        cls.ingest = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.ingest)

    MONTHLY = ["", "ALP", "Liberal Party", "National Party", "Total L-NP",
               "Total Others", "Greens", "Indepen-dents (ALL)",
               "Other Parties (ALL)", "Can't say/ Refused"]

    def test_monthly_table_has_no_one_nation_column(self):
        """States the fact the whole script is built around."""
        with self.assertRaises(self.ingest.UnmappedColumn):
            self.ingest.select_column(self.MONTHLY, "One Nation", "monthly")

    def test_discrete_request_refuses_an_aggregate_column(self):
        header = ["", "ALP", "Greens", "Other Parties (ALL)"]
        with self.assertRaises(self.ingest.UnmappedColumn):
            self.ingest.select_column(header, "One Nation", "monthly")

    def test_aggregate_may_be_requested_by_name(self):
        """Reading the combined cell on purpose is legitimate and allowed.

        The guard is on the mismatch, not on aggregates. Asking for the
        combined column and getting it is the correct behaviour; asking for a
        discrete party and getting it is the bug.
        """
        idx = self.ingest.select_column(
            self.MONTHLY, "Other Parties (ALL)", "monthly"
        )
        self.assertEqual(self.MONTHLY[idx], "Other Parties (ALL)")

    def test_election_table_does_carry_one_nation(self):
        header = ["", "ALP", "L-NP", "The Greens", "One Nation", "Ind./Others"]
        self.assertEqual(
            self.ingest.select_column(header, "One Nation", "results"),
            header.index("One Nation"),
        )

    def test_unknown_column_raises_rather_than_defaulting(self):
        with self.assertRaises(self.ingest.UnmappedColumn):
            self.ingest.select_column(self.MONTHLY, "Some Future Column", "monthly")

    def test_published_absences_stay_null(self):
        """Non-negotiable 5: never impute a margin from an assumed n."""
        rows = list(self.ingest.ingest_monthly(
            [[["", "ALP", "Liberal Party", "National Party", "Total L-NP",
              "Total Others", "Greens", "Indepen-dents (ALL)",
              "Other Parties (ALL)", "Can't say/ Refused"],
             ["2025"],
             ["May 5-31", "37.0", "26.5", "4.5", "31.0", "32.0", "11.5",
              "8.5", "14.5", "6.0"]]],
            [],
        ))
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual(r["n"], "")
        self.assertEqual(r["margin_of_error"], "")
        self.assertEqual(r["pub_date"], "")
        self.assertEqual(r["publishes_n"], "no")

    def test_monthly_ingest_never_writes_a_party_figure(self):
        """The assertion that makes the trap unrepeatable."""
        tables = [[["", "ALP", "Liberal Party", "National Party", "Total L-NP",
                    "Total Others", "Greens", "Indepen-dents (ALL)",
                    "Other Parties (ALL)", "Can't say/ Refused"],
                   ["2025"],
                   ["May 5-31", "37.0", "26.5", "4.5", "31.0", "32.0", "11.5",
                    "8.5", "14.5", "6.0"]]]
        rows = self.ingest.ingest_monthly(tables, [])
        for r in rows:
            self.assertEqual(r["pvi_oned"], "", "monthly table must not carry a party figure")
        self.assertEqual(self.ingest.validate(rows, []), [])



class TestSvgReferences(unittest.TestCase):
    """Internal references must resolve, in the markup AND in the stylesheet.

    The print band is the reason this exists. A band that renders with no fill
    on paper is an uncertainty interval the reader cannot distinguish from a
    plain shape, which is the failure DESIGN.md:212 exists to prevent.
    """

    @classmethod
    def setUpClass(cls):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "build", Path(__file__).resolve().parent.parent / "tools" / "build.py"
        )
        cls.build = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.build)

    def test_committed_charts_resolve_every_reference(self):
        """Any reference the page makes must resolve.

        Chart 01 draws no band, because no wave carries a published margin, so
        it legitimately makes no url(#...) reference. The check therefore runs
        over whatever references exist rather than requiring them, and the
        hatch patterns it still emits are checked separately below.
        """
        html = (Path(__file__).resolve().parent.parent / "index.html").read_text()
        ids = set(__import__("re").findall(r'id="([^"]+)"', html))
        refs = set(__import__("re").findall(r"url\(#([^)]+)\)", html))
        self.assertEqual(refs - ids, set(),
                         f"dangling fill references: {sorted(refs - ids)}")

    def test_both_hatch_densities_are_emitted(self):
        """Screen and print patterns, plus the narrow variant's suffixed ids."""
        html = (Path(__file__).resolve().parent.parent / "index.html").read_text()
        for required in ("hatch-mo", "hatch-mo-narrow",
                         "hatch-mo-print", "hatch-mo-print-narrow"):
            self.assertIn(f'id="{required}"', html,
                          f"missing {required}; print band would render unfilled")

    def test_print_pattern_is_coarser_than_screen(self):
        """Expanded density means a wider pitch and a heavier stroke."""
        for name in ("chart-01.svg", "chart-01-narrow.svg"):
            svg = (Path(__file__).resolve().parent.parent / "charts" / name).read_text()
            screen = svg[svg.index('id="hatch-mo"'):]
            screen = screen[:screen.index("</pattern>")]
            print_ = svg[svg.index('id="hatch-mo-print"'):]
            print_ = print_[:print_.index("</pattern>")]
            sw = float(__import__("re").search(r'stroke-width="([\d.]+)"', screen).group(1))
            pw = float(__import__("re").search(r'stroke-width="([\d.]+)"', print_).group(1))
            self.assertGreater(pw, sw, f"{name}: print hatch is not heavier")
            s_w = int(__import__("re").search(r'width="(\d+)"', screen).group(1))
            p_w = int(__import__("re").search(r'width="(\d+)"', print_).group(1))
            self.assertGreater(p_w, s_w, f"{name}: print hatch pitch not expanded")

    def test_print_block_swaps_the_band_fill(self):
        css = (Path(__file__).resolve().parent.parent
               / "src" / "margin-of-error.css").read_text()
        block = css[css.index("@media print"):]
        self.assertIn("url(#hatch-mo-print)", block,
                      "print block does not swap to the coarse pattern")
        self.assertIn("url(#hatch-mo-print-narrow)", block,
                      "print block does not cover the narrow variant")
        self.assertIn("print-color-adjust: exact", block)

    def test_band_elements_carry_the_class_the_print_rule_targets(self):
        for name in ("chart-01.svg", "chart-01-narrow.svg"):
            svg = (Path(__file__).resolve().parent.parent / "charts" / name).read_text()
            for poly in __import__("re").findall(r"<polygon[^>]*>", svg):
                if "url(#hatch-mo" in poly:
                    self.assertIn('class="band"', poly,
                                  f"{name}: band polygon cannot be targeted on print")



class TestDiscreteOneNationIngest(unittest.TestCase):
    """The second table on the Roy Morgan page, read for Task 1.

    132 rows spanning 2013 to 2022, with a discrete One Nation column. 48 of
    those rows are usable poll waves. The rest are blank for this party, and
    two are election results sitting in the same column as the polls.
    """

    @classmethod
    def setUpClass(cls):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "ingest",
            Path(__file__).resolve().parent.parent / "tools" / "ingest_roymorgan.py",
        )
        cls.ingest = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.ingest)

    DISCRETE_HEADER = ["", "ALP", "L-NP", "The Greens", "One Nation",
                       "NXT/ Centre Alliance", "Ind./Others"]

    def discrete_table(self, rows):
        return [self.DISCRETE_HEADER] + rows

    def test_election_row_is_excluded_from_the_poll_series(self):
        """Results and polls share the first column. Only polls belong here."""
        tables = [self.discrete_table([
            ["2019", "", "", "", "", "", ""],
            ["April 20/21, 2019", "34", "34", "13", "4.5", "n/a", "15"],
            ["2019 Federal Election - May 18, 2019", "33.3", "41.4",
             "10.4", "3.1", "0.3", "11.5"],
        ])]
        rows = self.ingest.ingest_discrete_oned(tables, [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["pvi_oned"], 4.5)

    def test_both_election_rows_are_excluded(self):
        """2016 and 2019 both appear, and the 2019 one sits inside its own
        year group. That is why 2019 yields 5 poll waves and not 6."""
        tables = [self.discrete_table([
            ["2016", "", "", "", "", "", ""],
            ["2016 Federal Election - July 2, 2016", "34.7", "40", "10",
             "1.3", "0", "14"],
            ["2019", "", "", "", "", "", ""],
            ["April 6/7, 2019", "33", "42", "11", "4.0", "0", "12"],
            ["2019 Federal Election - May 18, 2019", "33.3", "41.4",
             "10.4", "3.1", "0.3", "11.5"],
        ])]
        rows = self.ingest.ingest_discrete_oned(tables, [])
        self.assertEqual([r["pvi_oned"] for r in rows], [4.0])

    def test_blank_party_cell_yields_no_row(self):
        """70 of the source rows are 'n/a' for this party."""
        tables = [self.discrete_table([
            ["2016", "", "", "", "", "", ""],
            ["May 21/22 & 28/29, 2016", "30", "40", "12", "n/a", "n/a", "10"],
            ["2019", "", "", "", "", "", ""],
            ["April 6/7, 2019", "33", "42", "11", "4.0", "0", "12"],
        ])]
        rows = self.ingest.ingest_discrete_oned(tables, [])
        self.assertEqual([r["pvi_oned"] for r in rows], [4.0])

    def test_unpublished_fields_are_empty(self):
        tables = [self.discrete_table([
            ["2022", "", "", "", "", "", ""],
            ["April 18-24, 2022", "34", "34", "12", "4.5", "n/a", "14"],
        ])]
        row = self.ingest.ingest_discrete_oned(tables, [])[0]
        for field in ("n", "margin_of_error", "pub_date"):
            self.assertEqual(row[field], "", f"{field} must stay empty")

    def test_year_is_carried_down_from_the_group_header(self):
        tables = [self.discrete_table([
            ["2021", "", "", "", "", "", ""],
            ["January 4-5, 2021", "34", "38", "11", "4.5", "n/a", "12"],
        ])]
        self.assertEqual(self.ingest.ingest_discrete_oned(tables, [])[0]["year"], 2021)

    def test_missing_discrete_table_raises(self):
        monthly_only = [[
            ["", "ALP", "Total Others", "Other Parties (ALL)"],
            ["2025"],
            ["May 5-31", "37.0", "32.0", "14.5"],
        ]]
        with self.assertRaises(self.ingest.SourceShapeChanged):
            self.ingest.ingest_discrete_oned(monthly_only, [])

    def test_years_with_no_usable_wave_are_warned(self):
        """2013 to 2016 carry nothing. Reported, not interpreted."""
        tables = [self.discrete_table([
            ["2015", "", "", "", "", "", ""],
            ["March 3-4, 2015", "32", "45", "9", "n/a", "n/a", "13"],
        ])]
        tables[0].append(["2019", "", "", "", "", "", ""])
        tables[0].append(["April 6/7, 2019", "33", "42", "11", "4.0", "0", "12"])
        warnings = []
        self.ingest.ingest_discrete_oned(tables, warnings)
        self.assertTrue(any("2015" in w for w in warnings),
                        f"no warning named 2015: {warnings}")



class TestStatsWindowMean(unittest.TestCase):
    """Every derived number is computed here and nowhere else.

    Each function returning a figure also returns n_used, so no caller can
    receive a bare float and label it with the wrong wave count.
    """

    @classmethod
    def setUpClass(cls):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "stats", Path(__file__).resolve().parent.parent / "charts" / "stats.py"
        )
        cls.stats = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.stats)

    def polls(self, year, values):
        return [self.stats.Poll(year=year, wave=f"w{i}", value=v,
                                fielded_start=f"{year}-01-{i + 1:02d}",
                                fielded_end=f"{year}-01-{i + 1:02d}")
                for i, v in enumerate(values)]

    def test_mean_carries_the_count_actually_used(self):
        """Five waves exist before 2019. The mean uses five, and says so."""
        m = self.stats.window_mean(self.polls(2019, [3.0, 4.0, 3.5, 3.5, 4.5]),
                                   2019, window=12)
        self.assertEqual(m.n_used, 5)
        self.assertEqual(m.window, 12)
        self.assertAlmostEqual(m.value, 3.7, places=6)

    def test_low_and_high_come_from_the_same_waves_as_the_mean(self):
        m = self.stats.window_mean(self.polls(2022, [3.0, 5.0, 4.0]), 2022, window=12)
        self.assertEqual(m.low, 3.0)
        self.assertEqual(m.high, 5.0)

    def test_no_waves_returns_none_rather_than_a_shorter_window(self):
        self.assertIsNone(self.stats.window_mean([], 2019, window=12))

    def test_window_truncates_to_the_most_recent(self):
        m = self.stats.window_mean(self.polls(2022, [9.0, 9.0, 1.0, 1.0]), 2022, window=2)
        self.assertAlmostEqual(m.value, 1.0)
        self.assertEqual(m.n_used, 2)

    def test_gap_is_poll_minus_result(self):
        gaps = self.stats.gaps(
            [self.stats.Result(year=2022, value=5.0, confirmed=False)],
            self.polls(2022, [3.5, 4.0, 3.5, 3.5]), window=12)
        self.assertAlmostEqual(gaps[0].signed_gap, 3.625 - 5.0)
        self.assertEqual(gaps[0].n_used, 4)

    def test_gap_skips_an_election_with_no_polling(self):
        gaps = self.stats.gaps(
            [self.stats.Result(year=2025, value=6.4, confirmed=False)],
            self.polls(2022, [3.5, 4.0]), window=12)
        self.assertEqual(gaps, [])

    def test_contiguous_years_spans_the_dense_years(self):
        polls = (self.polls(2018, [3.0]) + self.polls(2019, [3.0])
                 + self.polls(2020, [3.0]))
        self.assertEqual(self.stats.contiguous_years(polls), (2018, 2020))

    def test_contiguous_years_ignores_an_isolated_year(self):
        """2022 sits alone, so the run is 2018-2020 and not 2018-2022."""
        polls = (self.polls(2018, [3.0]) + self.polls(2019, [3.0])
                 + self.polls(2020, [3.0]) + self.polls(2022, [4.0]))
        self.assertEqual(self.stats.contiguous_years(polls), (2018, 2020))

    def test_contiguous_years_does_not_bridge_a_gap(self):
        """A 2021 gap must not be silently absorbed into one run."""
        polls = (self.polls(2018, [3.0]) + self.polls(2019, [3.0])
                 + self.polls(2021, [3.0]) + self.polls(2022, [3.0]))
        self.assertEqual(self.stats.contiguous_years(polls), (2018, 2019))

    def test_load_polls_rejects_an_undated_wave(self):
        """Review Focus 1: an undated poll cannot be placed on a time axis."""
        import csv as _csv
        import tempfile as _tf
        with _tf.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
            fh.write("year,wave_label,fielded_start,fielded_end,pvi_oned\n")
            fh.write("2022,April 4,,2022-04-10,4.5\n")
            path = fh.name
        with self.assertRaises(ValueError) as ctx:
            self.stats.load_polls(path)
        self.assertIn("fielded_start", str(ctx.exception))

    def test_load_polls_rejects_an_empty_party_figure(self):
        import csv as _csv
        import tempfile as _tf
        with _tf.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
            fh.write("year,wave_label,fielded_start,fielded_end,pvi_oned\n")
            fh.write("2022,April 4,2022-04-04,2022-04-10,\n")
            path = fh.name
        with self.assertRaises(ValueError):
            self.stats.load_polls(path)

    def test_load_polls_reads_the_real_csv(self):
        """48 waves, 2018 to 2022, as verified in task 1."""
        csv_path = (Path(__file__).resolve().parent.parent
                    / "data" / "polls_roymorgan_oned.csv")
        polls = self.stats.load_polls(csv_path)
        self.assertEqual(len(polls), 48)
        self.assertEqual(min(p.year for p in polls), 2018)
        self.assertEqual(max(p.year for p in polls), 2022)

    def test_real_data_means_match_the_spec_claim(self):
        """The spec states 3.70 from 5 waves and 3.71 from 12. If these drift,
        the published claim has drifted with them."""
        csv_path = (Path(__file__).resolve().parent.parent
                    / "data" / "polls_roymorgan_oned.csv")
        polls = self.stats.load_polls(csv_path)
        m2019 = self.stats.window_mean(polls, 2019, window=12)
        m2022 = self.stats.window_mean(polls, 2022, window=12)
        self.assertEqual(m2019.n_used, 5)
        self.assertEqual(m2022.n_used, 12)
        self.assertAlmostEqual(m2019.value, 3.70, places=2)
        self.assertAlmostEqual(m2022.value, 3.71, places=2)



class TestChart01IsDataDriven(unittest.TestCase):
    """Chart 01 draws figures it computed, not figures someone typed."""

    CHART = Path(__file__).resolve().parent.parent / "charts" / "chart-01.svg"
    SOURCE = Path(__file__).resolve().parent.parent / "charts" / "chart_01.py"

    def test_generator_holds_no_dataset_literal(self):
        """The dataset must not appear as a typed constant.

        A figure transcribed into a generator is a figure that stops agreeing
        with its data, and nothing notices.
        """
        src = self.SOURCE.read_text()
        # Only figures that could only have come from the dataset. Layout
        # numbers like 0.60 or 5.0 are excluded: a substring test cannot tell a
        # panel fraction from a poll result, so this asserts the figures that
        # are unambiguous and the rendering is checked by eye in task 8.
        for value in ("3.70", "3.71", "1.29", "4.5", "4.0"):
            self.assertNotIn(value, src, f"{value} is transcribed, not computed")

    def test_output_declares_its_source_and_not_placeholder(self):
        svg = self.CHART.read_text()
        self.assertIn('data-source-id="roymorgan-pvi"', svg)
        self.assertNotIn('data-unsourced', svg)

    def test_each_panel_labels_the_wave_count_it_used(self):
        """Review Focus 3: the label is bound to the arithmetic."""
        svg = self.CHART.read_text()
        self.assertIn("5 waves", svg)
        self.assertIn("12 waves", svg)

    def test_chart_still_carries_the_accessibility_floor(self):
        svg = self.CHART.read_text()
        self.assertIn('role="img"', svg)
        self.assertIn("<title", svg)
        self.assertIn("<desc", svg)
        self.assertIn('id="hatch-mo-print"', svg)

    def test_chart_states_that_no_wave_carries_a_margin(self):
        """Non-negotiable 5. The absence has to be on the chart."""
        desc = self.CHART.read_text()
        self.assertIn("no margin of error", desc)

    def test_chart_reports_both_directions_of_gap(self):
        """The finding is that polling was high in 2019 and low in 2022."""
        svg = self.CHART.read_text()
        labels = re.findall(r'font-size="19"[^>]*>([^<]*)<', svg)
        self.assertEqual(len(labels), 2, f"expected two gap labels, got {labels}")
        self.assertTrue(labels[0].startswith("+"), f"2019 should be polling high: {labels[0]}")
        self.assertTrue(labels[1].startswith("\u2212"),
                        f"2022 should use a true minus sign: {labels[1]!r}")


class TestSeatShare(unittest.TestCase):
    """The denominator is the number of seats actually in the House.

    The House returned 150 seats at the 2001 to 2016 elections and 151 from
    2019, so "seat share" has two legitimate denominators across the span this
    chart covers. Hard-coding either one is wrong, which is why the chamber size
    is read from the source row rather than assumed.
    """

    @classmethod
    def setUpClass(cls):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "stats", Path(__file__).resolve().parent.parent / "charts" / "stats.py"
        )
        cls.stats = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.stats)

    def test_share_is_over_the_seats_actually_in_the_house(self):
        self.assertAlmostEqual(self.stats.seat_share(1, 151), 1 / 151)
        self.assertAlmostEqual(self.stats.seat_share(151, 151), 1.0)
        self.assertAlmostEqual(self.stats.seat_share(0, 151), 0.0)

    def test_the_150_seat_years_use_150(self):
        """A 1-seat share in a 150-seat House is 0.667%, not 0.662%.

        The difference is 4.4e-5, which assertAlmostEqual(places=4) treats as
        equal. Asserting on the ratio instead, because that is what actually
        distinguishes the two denominators.
        """
        self.assertAlmostEqual(self.stats.seat_share(1, 150), 1 / 150)
        self.assertGreater(
            self.stats.seat_share(1, 150) / self.stats.seat_share(1, 151), 1.005
        )

    def test_a_chamber_size_must_be_a_positive_int(self):
        for bad in (0, -1, 151.0, "151", None):
            with self.assertRaises(ValueError):
                self.stats.seat_share(1, bad)

    def test_more_seats_than_the_house_has_is_refused(self):
        """A row claiming 151 seats in a 150-seat House is corrupt data.

        Refusing is better than plotting it: it would draw a 100% share and
        flatten the axis against every other election.
        """
        with self.assertRaises(ValueError):
            self.stats.seat_share(151, 150)

    def test_seat_count_must_be_a_whole_non_negative_number(self):
        for bad in (-1, 0.5, "0", None):
            with self.assertRaises(ValueError):
                self.stats.seat_share(bad, 151)


class TestChart02SeatShare(unittest.TestCase):
    """Chart 02's two series are percentages of the same elected body."""

    CHART = Path(__file__).resolve().parent.parent / "charts" / "chart-02.svg"
    SOURCE = Path(__file__).resolve().parent.parent / "charts" / "chart_02.py"

    def test_wide_labels_every_election_and_narrow_labels_the_endpoints(self):
        """A membership test against pairs silently dropped every label.

        The labelled set was written `[(0, len(rows) - 1)]`, so `i not in
        labelled` was never true and all eighteen wide labels were skipped. The
        chart still passed every overlap and off-canvas check, because there
        was nothing left to collide with. Counting labels is what caught it.
        """
        root = Path(__file__).resolve().parent.parent / "charts"
        wide = (root / "chart-02.svg").read_text()
        narrow = (root / "chart-02-narrow.svg").read_text()
        rows = list(
            csv.DictReader(
                (
                    Path(__file__).resolve().parent.parent
                    / "data"
                    / "aec_election_results.csv"
                ).open(encoding="utf-8")
            )
        )
        years = [r["election_year"] for r in rows]
        for year in years:
            self.assertIn(f">{year}<", wide, f"{year} unlabelled on wide")
        # Two per election on wide (year and share), so at least two per year.
        self.assertGreaterEqual(wide.count("<text"), len(years) * 2)
        # Narrow cannot fit nine: a 16px year label is wider than a narrow slot.
        self.assertLess(narrow.count("<text"), wide.count("<text"))
        self.assertIn(f">{years[0]}<", narrow)
        self.assertIn(f">{years[-1]}<", narrow)
        for hidden in years[1:-1]:
            self.assertNotIn(f">{hidden}<", narrow, f"{hidden} should be dropped")

    def test_no_wrapped_line_exceeds_its_text_budget(self):
        """Wrapping is in user units, not characters.

        16px IBM Plex Mono advances 9.632 units per character, so a 52-char
        wrap needs 501 units in a 340-unit column. Wrapping by character count
        left every narrow header line overrunning the canvas.
        """
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "chart02", Path(__file__).resolve().parent.parent / "charts" / "chart_02.py"
        )
        chart02 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(chart02)

        # CHAR_UNITS lives in scales.py now: both chart modules had their own
        # copy and both wrapped by character count, which is the same bug twice.
        from scales import CHAR_UNITS_16  # noqa: PLC0415

        bye = {"division": "Farrer", "year": 2026,
               "primary_pct": 39.53, "tcp_pct": 57.55}
        for viewport in ("wide", "narrow"):
            budget = chart02.text_column(viewport)
            blocks = chart02.header_blocks(viewport, bye)
            for key in ("title", "note"):
                for line in blocks[key]:
                    units = len(line) * CHAR_UNITS_16
                    self.assertLessEqual(
                        units, budget,
                        f"{viewport} {key} line {units:.0f}u over {budget:.0f}u: "
                        f"{line!r}",
                    )

    def test_farrer_is_an_annotation_and_never_a_point(self):
        """A by-election has its own electorate and its own denominator."""
        svg = self.CHART.read_text()
        self.assertIn("Farrer", svg)
        for element in re.findall(r"<(circle|rect|path)[^>]*>", svg):
            self.assertNotIn("Farrer", element, "by-election plotted as a mark")

    def test_chart_is_sourced_and_not_a_placeholder(self):
        svg = self.CHART.read_text()
        self.assertIn("data-source-id=", svg)
        self.assertNotIn("data-unsourced", svg)

    def test_every_declared_source_id_resolves_in_the_registry(self):
        """`tools/build.py --check` passed while an id was unregistered.

        The build only validates charts the template references, and Chart 02
        is not in the template until the caption task. So a chart that is built
        but not yet placed gets no source check at all, which is exactly when a
        new id is most likely to be mistyped. This calls the build's own
        validator directly so the gap is closed before the chart ships.
        """
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "build", Path(__file__).resolve().parent.parent / "tools" / "build.py"
        )
        build = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build)

        registry = build.data_sources()
        for name in ("chart-02.svg", "chart-02-narrow.svg"):
            svg = (
                Path(__file__).resolve().parent.parent / "charts" / name
            ).read_text()
            self.assertEqual(
                build.unsourced_figure_problems(name, svg, registry), []
            )

    def test_chart_02_source_ids_are_checked_directly_because_the_build_cannot(self):
        """The build validates only charts the template references.

        Chart 02 is built but not yet in the template, so
        `tools/build.py --check` never reaches it — its source ids,
        role="img" and print hatch are all outside the gate. That was how
        `aec-hor-2025-fp-by-party` sat unregistered while the build reported
        "check passed".

        Rather than assert the gap stays open, this asserts the chart is
        validated directly, so the missing placeholder cannot leave it
        unvalidated. The placeholder arrives with the caption task; this test
        keeps the chart honest until then and afterwards.
        """
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "build", Path(__file__).resolve().parent.parent / "tools" / "build.py"
        )
        build = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build)

        template = (
            Path(__file__).resolve().parent.parent / "src" / "index.template.html"
        ).read_text()
        referenced = {"02"} if "<!-- chart:02 -->" in template else set()

        root = Path(__file__).resolve().parent.parent / "charts"
        registry = build.data_sources()
        for name in ("chart-02.svg", "chart-02-narrow.svg"):
            svg = (root / name).read_text()
            self.assertEqual(
                build.unsourced_figure_problems(name, svg, registry), []
            )
            self.assertIn('role="img"', svg)
            self.assertIn('id="hatch-mo-print"', svg)

        if not referenced:
            # Until the template references it, this direct call is the only
            # thing checking Chart 02. The caption task closed that gap by
            # adding <!-- chart:02 -->, so this branch is now the fallback
            # rather than the only line of defence.
            self.assertTrue(
                (root / "chart-02.svg").exists(),
                "Chart 02 is generated but neither referenced nor validatable.",
            )
        else:
            # Referenced, so the build gate reaches it. Assert the gate would
            # actually notice a regression rather than trusting that it does.
            template = (
                Path(__file__).resolve().parent.parent / "src" / "index.template.html"
            ).read_text()
            self.assertIn("<!-- chart:02 -->", template)
            built = (Path(__file__).resolve().parent.parent / "index.html").read_text()
            self.assertIn('data-chart="02"', built)

    def test_the_2004_to_2016_discontinuity_is_marked(self):
        svg = self.CHART.read_text()
        self.assertIn("2004", svg)
        self.assertIn("2016", svg)

    def test_generator_holds_no_dataset_literal(self):
        """Seat counts and vote shares are read, never typed.

        Matched as whole numbers, not substrings. A substring test cannot tell
        a transcribed 4.3% from a 4.34% quoted in a docstring, which is the same
        trap Task 3 hit with a panel fraction colliding with a poll result. So
        the pattern requires the figure to end at a word boundary.
        """
        src = self.SOURCE.read_text()
        for value in ("6.4", "4.3", "3.1", "0.66", "39.53", "57.55"):
            pattern = re.compile(rf"(?<![\d.]){re.escape(value)}(?![\d])")
            self.assertIsNone(
                pattern.search(src), f"{value} is transcribed, not computed"
            )

    def test_chamber_size_is_stated_because_it_changed(self):
        """150 seats then 151. A reader cannot check the share without it."""
        svg = self.CHART.read_text()
        self.assertIn("150-seat House", svg)
        self.assertIn("151-seat House", svg)

    def test_the_stated_chamber_boundary_matches_the_data(self):
        """The subtitle is a computed sentence, so it can drift.

        It once read "up to 2001", because the year was taken from the
        thin-coverage block's start rather than from the chamber size. Both are
        in the same data, unrelated to each other, and the sentence was wrong
        while every other assertion still passed.
        """
        rows = list(
            csv.DictReader(
                (
                    Path(__file__).resolve().parent.parent
                    / "data"
                    / "aec_election_results.csv"
                ).open(encoding="utf-8")
            )
        )
        small = min(int(r["chamber_size"]) for r in rows)
        large = max(int(r["chamber_size"]) for r in rows)
        last_small = max(
            int(r["election_year"]) for r in rows if int(r["chamber_size"]) == small
        )
        first_large = min(
            int(r["election_year"]) for r in rows if int(r["chamber_size"]) == large
        )
        svg = self.CHART.read_text()
        self.assertIn(
            f"from {rows[0]['election_year']} to {last_small}", svg
        )
        self.assertIn(f"House from {first_large}", svg)

    def test_chart_keeps_the_accessibility_floor(self):
        svg = self.CHART.read_text()
        self.assertIn('role="img"', svg)
        self.assertIn("<title", svg)
        self.assertIn("<desc", svg)
        self.assertIn('id="hatch-mo-print"', svg)


class TestAecSeatIngest(unittest.TestCase):
    """The AEC seat and vote series, and the three traps that shape it.

    Every figure on Chart 02 comes from here. The tests exist because each
    trap produces a plausible wrong number rather than an error.
    """

    @classmethod
    def setUpClass(cls):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "ingest_aec",
            Path(__file__).resolve().parent.parent / "tools" / "ingest_aec_seats.py",
        )
        cls.ingest = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.ingest)

    def test_party_is_found_by_its_abbreviation_not_its_name(self):
        """The AEC renamed the party twice. Matching on the modern name drops
        five of the nine elections."""
        rows = [
            {"PartyAb": "LP", "PartyNm": "Liberal", "TotalPercentage": "30"},
            {"PartyAb": "ON", "PartyNm": "One Nation", "TotalPercentage": "1.29"},
        ]
        self.assertEqual(self.ingest.party_row(2016, rows)["TotalPercentage"], "1.29")

    def test_a_year_whose_abbreviation_is_absent_raises(self):
        """Silently returning nothing makes the series shorter than the caption
        claims, which is the defect this project keeps finding."""
        rows = [{"PartyAb": "ALP", "PartyNm": "Australian Labor Party"}]
        with self.assertRaises(self.ingest.SourceShapeChanged):
            self.ingest.party_row(2016, rows)

    def test_every_election_has_a_recorded_abbreviation(self):
        """A year with no abbreviation cannot be looked up, and must not be
        quietly skipped."""
        self.assertEqual(
            set(self.ingest.ABBREVIATION_BY_YEAR),
            {2001, 2004, 2007, 2010, 2013, 2016, 2019, 2022, 2025},
        )

    def test_2001_reads_the_national_row_not_a_state_row(self):
        """The 2001 statistics repeat the party once per state.

        Queensland reads 7.07 and the national figure is 4.34. A scan for the
        first matching line returns Queensland, which is still a real figure
        from the real file and would put 2001 above every election but 2025.
        """
        self.assertAlmostEqual(
            float(self.ingest.national_row_2001()["vote_pct"]), 4.34
        )

    def test_chamber_size_is_counted_not_asserted(self):
        """150 then 151. Hard-coding either is wrong for part of the series."""
        self.assertEqual(self.ingest.chamber_size_from_members_elected_2001(), 150)

    def test_seat_count_comes_from_the_source_not_from_absence(self):
        """2001 has no by-party representation table for the House at all, so
        the count is made from the elected members carrying the party's code."""
        self.assertEqual(self.ingest.seats_from_members_elected_2001(), 0)

    def test_the_csv_series_carries_nine_elections_and_two_chamber_sizes(self):
        csv_path = (
            Path(__file__).resolve().parent.parent / "data" / "aec_election_results.csv"
        )
        lines = csv_path.read_text().strip().splitlines()[1:]
        self.assertEqual(len(lines), 9)
        sizes = {int(l.split(",")[4]) for l in lines}
        self.assertEqual(sizes, {150, 151})

    def test_every_seat_count_is_zero_across_the_whole_series(self):
        """The claim the chart makes. If this changes, the chart's claim is
        wrong and the caption must change with it."""
        csv_path = (
            Path(__file__).resolve().parent.parent / "data" / "aec_election_results.csv"
        )
        lines = csv_path.read_text().strip().splitlines()[1:]
        self.assertEqual({int(l.split(",")[3]) for l in lines}, {0})


class TestWrapToWidth(unittest.TestCase):
    """Wrapping is in user units, not characters.

    Both chart modules carried their own copy and both wrapped by character
    count, which is the same bug found twice. Chart 01's narrow variant measured
    485 and 755 units inside a 420 canvas, so its two panel titles ran off the
    right edge and were clipped.
    """

    def test_a_line_never_exceeds_the_budget_it_was_given(self):
        from scales import CHAR_UNITS_16, wrap_to_width

        text = (
            "Where polling sat before each election, and what the ballot gave"
        )
        for budget in (340, 400, 940, 1072):
            for line in wrap_to_width(text, budget):
                self.assertLessEqual(
                    len(line) * CHAR_UNITS_16,
                    budget,
                    f"budget {budget}: {line!r} overruns",
                )

    def test_a_character_budget_would_not_have_caught_this(self):
        """The old failure, stated as a test so it cannot come back quietly.

        76 characters is the wide chart's fit. The same 76 characters need 732
        units, and the narrow column is 340.
        """
        from scales import CHAR_UNITS_16

        self.assertGreater(76 * CHAR_UNITS_16, 340)

    def test_the_advance_widths_are_measured_not_assumed(self):
        """9.632 units per character at 16px, 10.836 at 18px.

        Measured in a browser with getBBox over a 100-character sample. If the
        font stack changes these are wrong and every wrapped line is wrong with
        it, so they are asserted as a ratio rather than left implicit.
        """
        from scales import CHAR_UNITS_16, CHAR_UNITS_18

        self.assertAlmostEqual(CHAR_UNITS_16, 9.632, places=3)
        self.assertAlmostEqual(CHAR_UNITS_18, 10.836, places=3)
        # 18px is 1.125x 16px in the same monospace face.
        self.assertAlmostEqual(CHAR_UNITS_18 / CHAR_UNITS_16, 1.125, places=2)

    def test_no_chart_wraps_by_character_count_any_more(self):
        """Neither generator calls textwrap.wrap with a literal width."""
        root = Path(__file__).resolve().parent.parent / "charts"
        for name in ("chart_01.py", "chart_02.py"):
            src = (root / name).read_text()
            self.assertNotIn(
                "textwrap.wrap(", src, f"{name} wraps by character count"
            )
            self.assertIn("wrap_to_width", src, f"{name} does not use the shared helper")


class TestCaptionFiguresAreInjected(unittest.TestCase):
    """Prose states the same numbers the charts draw, from the same source.

    The alternative — typing a figure into the caption — is the drift this
    whole repository is arranged to prevent. The archived feasibility model
    printed 1.33% booth coverage and the prose about it said "below 15%", with
    nothing in between to notice.
    """

    ROOT = Path(__file__).resolve().parent.parent
    TEMPLATE = ROOT / "src" / "index.template.html"
    BUILT = ROOT / "index.html"

    @classmethod
    def setUpClass(cls):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "build", cls.ROOT / "tools" / "build.py"
        )
        cls.build = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.build)

    def test_template_contains_no_dataset_literal(self):
        """The template carries slots, never figures.

        Matched as whole numbers, for the reason TestChart01IsDataDriven sets
        out: a substring test cannot tell a figure from a year or a slot name.
        """
        src = self.TEMPLATE.read_text()
        for value in ("3.70", "3.71", "0.60", "1.29", "48 waves", "39.53", "57.55"):
            self.assertNotIn(
                value, src, f"{value} is typed into the template, not injected"
            )

    def test_template_declares_figure_slots(self):
        src = self.TEMPLATE.read_text()
        for slot in ("{{gap_2019}}", "{{gap_2022}}", "{{waves_total}}"):
            self.assertIn(slot, src, f"{slot} missing from the template")

    def test_every_declared_slot_is_filled(self):
        """An unfilled slot is the prose equivalent of an unfilled chart.

        `{{gap_2019}}` left in the output ships braces and a promise to the
        reader, and reads as finished.
        """
        slots = set(re.findall(r"\{\{(\w+)\}\}", self.TEMPLATE.read_text()))
        self.assertTrue(slots, "the template declares no slots at all")
        filled = self.build.figure_slots()
        missing = sorted(slots - set(filled))
        self.assertEqual(missing, [], f"slots declared but never filled: {missing}")

    def test_built_page_carries_the_computed_figures(self):
        built = self.BUILT.read_text()
        self.assertIn("3.70", built)
        self.assertIn("1.29", built)
        self.assertNotIn("{{", built)

    def test_the_caption_states_the_missing_margins(self):
        """Non-negotiable 5. The absence has to be on the page, not just in
        the chart's desc, because a reader using images off reads the caption.
        """
        built = self.BUILT.read_text()
        self.assertIn("no margin of error", built)
        self.assertIn("sample size", built)

    def test_the_caption_does_not_criticise_any_publisher(self):
        """AGENTS.md: the absence is a property of the evidence, not a finding
        about a publisher, and the page must not present it as one."""
        built = self.BUILT.read_text().lower()
        for phrase in (
            "failed to publish",
            "refused to disclose",
            "secretive",
            "poor practice",
            "should have published",
            "withholds",
        ):
            self.assertNotIn(phrase, built, f"page editorialises a publisher: {phrase}")

    def test_the_chart01_caption_does_not_claim_a_shown_band(self):
        """It used to say the shaded band marks the margin of error.

        No wave in the series carries one, so that sentence described a mark
        the chart does not draw. Corrected when the real caption landed.
        """
        self.assertNotIn(
            "marks the margin of error where the publisher stated one",
            self.BUILT.read_text(),
        )

    def test_the_caption_states_the_chamber_boundary_the_data_carries(self):
        """I typed this wrong twice.

        "Between 2001 and 2016 the House had 150 seats" reads as two
        elections, not a range. It is now computed from the data. The span is
        pinned here so a hand-typed year cannot come back.
        """
        built = " ".join(self.BUILT.read_text().split())
        self.assertIn("The House had 150 seats from 2001 to 2016", built)
        self.assertIn("has had 151 since 2019", built)

    def test_the_caption_states_the_span_the_chart_actually_shades(self):
        """The shaded block is 2004 to 2016, not 2001 to 2016.

        2001 to 2016 is the span the House had 150 seats, which is a different
        fact about a different variable. Conflating them would describe a block
        the chart does not draw.
        """
        built = " ".join(self.BUILT.read_text().split())
        self.assertIn("The shaded block marks 2004 to 2016", built)
        self.assertNotIn("The shaded block marks 2001 to 2016", built)


class TestChartGateAssertions(unittest.TestCase):
    """The gates that refuse to publish an unconfirmed or mismatched figure.

    This is the safety net for the whole plan, so every one of these must be
    seen to fire. An assertion that has never failed has not been tested.

    The first is expected to be RED in the real repository until task 0003
    delivers AEC-confirmed results. That is the gate working, not a bug.
    """

    @classmethod
    def setUpClass(cls):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "build", Path(__file__).resolve().parent.parent / "tools" / "build.py"
        )
        cls.build = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.build)

    REGISTRY = "source_id: roymorgan-pvi\ncross_check_only: yes\n"

    def test_cross_check_only_ids_are_refused(self):
        """The gate. Until AEC confirms, this must fail."""
        svg = '<svg data-source-id="roymorgan-pvi"></svg>'
        problems = self.build.unsourced_result_problems(
            "chart-01.svg", svg, self.REGISTRY
        )
        self.assertTrue(problems)
        self.assertIn("cross-check", problems[0].lower())

    def test_aec_confirmed_id_clears_the_gate(self):
        registry = "source_id: aec-hor-2022\n"
        svg = '<svg data-source-id="aec-hor-2022"></svg>'
        self.assertEqual(
            self.build.unsourced_result_problems("c.svg", svg, registry), []
        )

    def test_one_confirmed_id_among_cross_check_ones_clears_the_gate(self):
        """Chart 02 declares four ids and none is cross-check-only.

        The rule is "fails if EVERY resolved id is cross-check-only", not "fails
        if any is". A chart legitimately drawing on a cross-checked poll series
        and a confirmed election result must pass on the strength of the
        confirmed one.
        """
        registry = (
            "source_id: roymorgan-pvi\ncross_check_only: yes\n"
            "source_id: aec-hor-2025-fp-by-party\n"
        )
        svg = '<svg data-source-id="roymorgan-pvi aec-hor-2025-fp-by-party"></svg>'
        self.assertEqual(
            self.build.unsourced_result_problems("c.svg", svg, registry), []
        )

    def test_populated_margin_is_refused(self):
        problems = self.build.poll_field_problems(
            [{"wave": "w1", "margin_of_error": "2.5",
              "fielded_start": "2022-01-01",
              "publishes_margin_of_error": "no"}]
        )
        self.assertTrue(problems)

    def test_null_margin_with_declared_absence_passes(self):
        problems = self.build.poll_field_problems(
            [{"wave": "w1", "margin_of_error": "",
              "fielded_start": "2022-01-01",
              "publishes_margin_of_error": "no"}]
        )
        self.assertEqual(problems, [])

    def test_missing_field_window_is_refused(self):
        problems = self.build.poll_field_problems(
            [{"wave": "w1", "margin_of_error": "", "fielded_start": "",
              "publishes_margin_of_error": "no"}]
        )
        self.assertTrue(problems)

    def test_by_election_in_the_series_is_refused(self):
        rows = [{"year": 2019, "is_by_election": "no"},
                {"year": 2026, "is_by_election": "yes"}]
        self.assertTrue(self.build.plotted_row_problems(rows))

    def test_general_elections_only_pass(self):
        rows = [{"year": y, "is_by_election": "no"} for y in (2001, 2019, 2025)]
        self.assertEqual(self.build.plotted_row_problems(rows), [])

    def test_label_count_must_match_the_arithmetic(self):
        self.assertTrue(self.build.label_count_problems({2019: (5, 12)}))

    def test_matching_label_counts_pass(self):
        self.assertEqual(self.build.label_count_problems({2019: (5, 5)}), [])

    # -- The remaining five, each proven to fire ------------------------

    def test_a_dataset_literal_in_a_generator_is_refused(self):
        problems = self.build.generator_literal_problems(
            {"charts/chart_01.py": "GAP = 3.70\n"}
        )
        self.assertTrue(problems)

    def test_clean_generator_source_passes(self):
        self.assertEqual(
            self.build.generator_literal_problems({"charts/chart_01.py": "x = 1\n"}),
            [],
        )

    def test_a_wave_outside_the_range_must_declare_why_it_is_blank(self):
        rows = [{"year": 2015, "wave": "w", "blank_reason": ""},
                {"year": 2016, "wave": "w2", "blank_reason": ""}]
        self.assertTrue(self.build.blank_reason_problems(rows, (2016, 2022)))

    def test_a_declared_blank_passes(self):
        rows = [{"year": 2015, "wave": "w", "blank_reason": "no candidates"},
                {"year": 2016, "wave": "w2", "blank_reason": ""}]
        self.assertEqual(self.build.blank_reason_problems(rows, (2016, 2022)), [])

    def test_a_wrong_seat_denominator_is_refused(self):
        """2004 had 150 seats. A row claiming 151 is the right number on the
        wrong election, which a bare membership check would pass."""
        problems = self.build.seat_denominator_problems(
            [{"election_year": "2004", "seats_won": "0", "chamber_size": "151"}],
            expected_small=150,
        )
        self.assertTrue(problems)

    def test_an_impossible_chamber_size_is_refused(self):
        problems = self.build.seat_denominator_problems(
            [{"election_year": "2019", "seats_won": "0", "chamber_size": "300"}],
            expected_small=150,
        )
        self.assertTrue(problems)

    def test_the_real_two_chamber_sizes_pass(self):
        rows = [
            {"election_year": "2004", "seats_won": "0", "chamber_size": "150"},
            {"election_year": "2025", "seats_won": "0", "chamber_size": "151"},
        ]
        self.assertEqual(
            self.build.seat_denominator_problems(rows, expected_small=150), []
        )

    def test_house_and_senate_sharing_an_axis_is_refused(self):
        problems = self.build.chamber_axis_problems(
            '<svg><desc>House of Representatives and Senate results'
            "</desc></svg>"
        )
        self.assertTrue(problems)

    def test_mentioning_one_chamber_alone_passes(self):
        """Neither current chart names a chamber at all.

        Chart 01 is polling against results and Chart 02 says "the House" in
        prose rather than in the figure. So the gate has nothing to fire on in
        the real repository, and a test that adds "Senate" alone proves
        nothing: only one chamber is named, which is allowed. Both chambers must
        be named for the scale to be shared.
        """
        self.assertEqual(
            self.build.chamber_axis_problems("<svg><text>the House</text></svg>"), []
        )
        self.assertEqual(
            self.build.chamber_axis_problems("<svg><text>Senate</text></svg>"), []
        )
        self.assertEqual(
            self.build.chamber_axis_problems("<svg><text>a poll</text></svg>"), []
        )

    def test_caption_wave_count_must_equal_the_rows_used(self):
        self.assertTrue(self.build.caption_count_problems(48, 47))

    def test_matching_caption_count_passes(self):
        self.assertEqual(self.build.caption_count_problems(48, 48), [])


class TestChartGateIsRedUntilAecConfirms(unittest.TestCase):
    """The real repository must fail, and for the stated reason.

    This asserts the gate is closed rather than working around it. If it ever
    goes green before task 0003, something loosened an assertion.
    """

    def test_the_build_check_fails_on_the_unconfirmed_poll_series(self):
        import subprocess

        root = Path(__file__).resolve().parent.parent
        proc = subprocess.run(
            [sys.executable, "tools/build.py", "--check"],
            cwd=root, capture_output=True, text=True,
        )
        self.assertNotEqual(
            proc.returncode, 0,
            "tools/build.py --check passed, but the 2019 and 2022 results are "
            "still Roy Morgan's cross-check rather than the AEC's record. "
            "Either task 0003 has landed and this test should be replaced, or "
            "an assertion was loosened.",
        )
        self.assertIn("cross-check", (proc.stdout + proc.stderr).lower())


if __name__ == "__main__":
    unittest.main()
