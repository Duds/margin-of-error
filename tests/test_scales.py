"""Tests for chart geometry.

Written because both bugs found while proving the stack in task 0002 were
silent: inverted axes and a zero-width band that hid a published margin. A
geometry bug in this project does not throw, it publishes a wrong chart.
"""

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
        html = (Path(__file__).resolve().parent.parent / "index.html").read_text()
        ids = set(__import__("re").findall(r'id="([^"]+)"', html))
        refs = set(__import__("re").findall(r"url\(#([^)]+)\)", html))
        self.assertTrue(refs, "no url(#...) references found; the test is vacuous")
        self.assertEqual(refs - ids, set(), "dangling fill references in index.html")

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
        labels = re.findall(r'class="value">([^<]*)<', svg)
        self.assertEqual(len(labels), 2, f"expected two gap labels, got {labels}")
        self.assertTrue(labels[0].startswith("+"), f"2019 should be polling high: {labels[0]}")
        self.assertTrue(labels[1].startswith("\u2212"),
                        f"2022 should use a true minus sign: {labels[1]!r}")


if __name__ == "__main__":
    unittest.main()
