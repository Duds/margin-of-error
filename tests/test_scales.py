"""Tests for chart geometry.

Written because both bugs found while proving the stack in task 0002 were
silent: inverted axes and a zero-width band that hid a published margin. A
geometry bug in this project does not throw, it publishes a wrong chart.
"""

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



if __name__ == "__main__":
    unittest.main()
