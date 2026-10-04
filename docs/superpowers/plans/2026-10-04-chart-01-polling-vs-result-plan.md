# Charts 01 and 02 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the placeholder chart with two real charts — polling against
result for 2018 to 2022, and national vote against seat share — built entirely
from ingested data with every displayed figure computed at build time.

**Architecture:** One ingest script writes two CSVs. A new `charts/stats.py` is
the only place a derived number is computed; chart generators and the HTML
prose both call it, so a figure cannot drift between what is drawn and what is
written. `tools/build.py` validates both charts and holds a deliberate gate that
fails until AEC confirms the election results.

**Tech Stack:** Python 3.13 standard library only. No `pytest`, no third-party
packages. Tests run via `python3 -m unittest discover -s tests`. Charts are
generated SVG, inlined into `index.html` by `tools/build.py`.

**Spec:** `docs/superpowers/specs/2026-10-04-chart-01-polling-vs-result-design.md`

## Global Constraints

- Stdlib only. Do not add a dependency. `AGENTS.md` stack section.
- Python files are `snake_case`, tests included. A hyphenated `test-*.py` is
  silently skipped by `unittest` discovery — verified, exits 5. `AGENTS.md` house
  rules.
- No figure is transcribed. Anything displayed is computed from a CSV at build
  time. Never type a dataset value into a chart constant or into prose.
- `margin_of_error`, `n` and `pub_date` are **empty** in every poll row. Roy
  Morgan publishes none of them. Never populate them, never impute
  (`AGENTS.md` non-negotiable 5).
- Every new build assertion gets a test proving it **fails** on bad input. A
  guard never seen to fire is indistinguishable from one that does not work.
- Raw hex is banned in chart output. Fills use `var(--token)`.
- Every chart SVG carries `role="img"`, `<title>`, `<desc>`, and both hatch
  densities (`hatch-mo`, `hatch-mo-print`) for the print block.
- Commit per task, imperative subject under 72 characters.

## Review Focus

The spec implies these inputs; no task's tests currently exercise them. Each has
a test pinned to the owning task below.

1. **A poll row with no field window.** It cannot be placed on a time axis or
   ordered against an election. Expect: build fails with the wave named.
2. **An election row inside the poll table.** The source interleaves results
   with polls and labels both in the same first column. Expect: excluded from
   the poll series, never plotted as a poll, counted separately.
3. **Fewer waves before an election than the window.** The 2019 election has 5,
   the window is 12. Expect: the mean uses the 5, the chart labels it "5 waves",
   and the label is bound to the arithmetic.
4. **A wave carrying a populated `margin_of_error`.** Expect: build refuses. Only
   a source change or a prohibited imputation could produce one.
5. **A by-election entering the general-election series.** Farrer 2026 is a
   different electorate, field and denominator. Expect: build refuses; it is an
   annotation only.

---

## File Structure

| File | Responsibility |
|---|---|
| `tools/ingest_roymorgan.py` | Roy Morgan page → CSVs. Owns column selection and the aggregate-column refusal. |
| `data/polls_roymorgan_oned.csv` | **Create.** 48 discrete poll waves, 2018–2022. |
| `charts/stats.py` | **Create.** The only place a derived number is computed. No rendering. |
| `charts/scales.py` | Existing geometry. Unchanged. |
| `charts/chart_01.py` | Rewrite. Polling against result: gap bars plus evidence spans. |
| `charts/chart_02.py` | **Create.** National vote share against seat share. |
| `tools/build.py` | Injection and validation. Grows nine assertions. |
| `src/index.template.html` | Hand-written prose. Second chart placeholder. |
| `index.html` | Generated. Never hand-edited. |
| `tests/test_scales.py` | Existing 42 tests. Grows with each task. |

`stats.py` is separate from `scales.py` on purpose: `scales.py` is pure
geometry, `stats.py` reads data and derives meaning. Merged, the derived numbers
would be untestable without a renderer.

---

### Task 1: Ingest the discrete One Nation polling table

**Files:**
- Modify: `tools/ingest_roymorgan.py` (add `ingest_discrete_oned`, call from `main` at line 421)
- Create: `data/polls_roymorgan_oned.csv` (generated)
- Test: `tests/test_scales.py` (add class `TestDiscreteOneNationIngest`)

**Interfaces:**
- Consumes: `parse_tables(raw) -> list[list[list[str]]]` (line 85), `select_column(header, want, table) -> int` (line 107), `parse_number(cell) -> float | None` (line 167), `parse_field_window(label, year_hint) -> tuple[str, str]` (line 183), `SourceShapeChanged` (line 77), `write_csv(path, rows)` (line 410)
- Produces: `ingest_discrete_oned(tables: list[list[list[str]]], warnings: list[str]) -> list[dict]` and the CSV at `data/polls_roymorgan_oned.csv`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_scales.py`, class `TestDiscreteOneNationIngest`, loading the
ingest module with the same `importlib.util.spec_from_file_location` pattern the
existing `TestRoyMorganColumnMapping` class uses (line 261).

Table header under test:
`['', 'ALP', 'L-NP', 'The Greens', 'One Nation', 'NXT/ Centre Alliance', 'Ind./Others']`

| Test name | Asserts |
|---|---|
| `test_election_row_is_excluded_from_the_poll_series` | Given rows `['April 20/21, 2019', ..., '4.5']` and `['2019 Federal Election - May 18, 2019', ..., '3.1']` under year `2019`: exactly 1 row returned, `pvi_oned == "4.5"` |
| `test_blank_party_cell_yields_no_row` | Row with `'n/a'` in the One Nation column returns `[]` |
| `test_unpublished_fields_are_empty` | `n`, `margin_of_error`, `pub_date` all `""` on the returned row |
| `test_missing_discrete_table_raises` | A table with no discrete One Nation column raises `SourceShapeChanged` |

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest discover -s tests 2>&1 | tail -5`
Expected: ERROR — `AttributeError: module 'ingest' has no attribute 'ingest_discrete_oned'`

- [ ] **Step 3: Implement `ingest_discrete_oned` in `tools/ingest_roymorgan.py`**

Select the table by **having a discrete One Nation column**, not by header text.
Two tables qualify on the live page — the election-results table (12 rows) and
this one (132) — so take the larger and assert exactly two candidates so a page
restructure fails loudly rather than silently picking wrong.

Exclusion rule, exact: skip a row when its label matches `r"\bElection\b"`
(case-insensitive). Two such rows exist in range — the 2016 and 2019 federal
elections — and the 2019 one sits inside the 2019 year group, which is why 2019
yields 5 poll waves and not 6.

Emit a warning naming any year with zero usable waves. On the live source those
are 2013, 2014, 2015, 2016 and 2017; 2017 is absent from the table entirely, and
that absence is a property of the source to record, not to interpret.

Signature: `def ingest_discrete_oned(tables, warnings) -> list[dict]`. Docstring must
record why results are excluded — the source interleaves them with polls in the
same column, and a result counted as a poll is the same class of error as the
spec's 49-versus-48 slip.

Row dict keys, in this order: `house`, `wave_label`, `year`, `fielded_start`,
`fielded_end`, `n`, `margin_of_error`, `pub_date`, `pvi_oned`,
`publishes_n`, `publishes_margin_of_error`, `publishes_pub_date`,
`source_id`, `retrieved`. The three unpublished fields are `""`.

In `main`, after the existing `ingest_monthly` call, write the result to
`OUT_DIR / "polls_roymorgan_oned.csv"` via `write_csv`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests 2>&1 | tail -4`
Expected: OK, 46 tests

- [ ] **Step 5: Run the ingest and check the row count**

```bash
python3 tools/ingest_roymorgan.py --html <path-to-saved-page.html>
```

Expected: `wrote data/polls_roymorgan_oned.csv (48 rows)`

Then confirm the shape directly:

```bash
python3 - <<'EOF'
import csv
rows = list(csv.DictReader(open("data/polls_roymorgan_oned.csv")))
assert len(rows) == 48, f"expected 48, got {len(rows)}"
assert all(r["pvi_oned"] for r in rows)
assert all(r["n"] == "" and r["margin_of_error"] == "" for r in rows)
assert {r["year"] for r in rows} == {"2018", "2019", "2020", "2021", "2022"}
print("48 waves, party populated, three fields empty, 2018-2022 only")
EOF
```

If the count is 49, the election-row exclusion is not matching. If 47 or fewer,
a poll row is being dropped — check the `n/a` path before anything else.

- [ ] **Step 6: Commit**

```bash
git add tools/ingest_roymorgan.py tests/test_scales.py data/polls_roymorgan_oned.csv
git commit -m "Ingest discrete One Nation polling, 2018 to 2022"
```

---

### Task 2: `charts/stats.py`, the only place a derived number is computed

**Files:**
- Create: `charts/stats.py`
- Test: `tests/test_scales.py` (add class `TestStatsWindowMean`)

**Interfaces:**
- Consumes: the CSV at `data/polls_roymorgan_oned.csv` from Task 1
- Produces: `load_polls(path) -> list[Poll]`, `contiguous_years(polls) -> tuple[int, int]`, `waves_before(polls, year, window) -> list[Poll]`, `window_mean(polls, year, window) -> Mean | None`, `gaps(results, polls, window) -> list[Gap]`. Types `Poll`, `Mean`, `Gap` are dataclasses in `charts/stats.py`.

Every function returning a number returns `n_used` alongside it, so no caller
can receive a bare float and label it with the wrong wave count. That is the
structural answer to the archived model's booth-coverage drift, where a prose
figure came to differ from the model that produced it.

- [ ] **Step 1: Write the failing test**

Add `TestStatsWindowMean`, loading `charts/stats.py` the same way. Helper
`self.polls(year, values)` builds `Poll` objects with sequential wave names and
field windows.

| Test name | Asserts |
|---|---|
| `test_mean_carries_the_count_actually_used` | 5 polls in 2019, window 12 → `m.n_used == 5`, `m.window == 12`, `m.value == 3.7` |
| `test_low_and_high_come_from_the_same_waves_as_the_mean` | values `[3.0, 5.0, 4.0]` → `m.low == 3.0`, `m.high == 5.0` |
| `test_no_waves_returns_none_rather_than_a_shorter_window` | `window_mean([], 2019, 12)` is `None` |
| `test_window_truncates_to_the_most_recent` | values `[9.0, 9.0, 1.0, 1.0]`, window 2 → `m.value == 1.0`, `m.n_used == 2` |
| `test_gap_is_poll_minus_result` | 4 polls averaging 3.625 against result 5.0 → `signed_gap == -1.375`, `n_used == 4` |
| `test_contiguous_years_spans_the_dense_years` | one poll each in 2018/2019/2020 → `(2018, 2020)` |

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest discover -s tests 2>&1 | tail -5`
Expected: ERROR — `FileNotFoundError` for `charts/stats.py`

- [ ] **Step 3: Create `charts/stats.py`**

```python
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
    signed_gap: float      # poll minus result; negative means polling was low
```

Signatures:

```python
def load_polls(path: Path) -> list[Poll]
def contiguous_years(polls: Sequence[Poll]) -> tuple[int, int]
def waves_before(polls: Sequence[Poll], year: int, window: int) -> list[Poll]
def window_mean(polls: Sequence[Poll], year: int, window: int) -> Mean | None
def gaps(results: Sequence[Result], polls: Sequence[Poll], window: int) -> list[Gap]
```

`load_polls` reads only `year`, `wave_label`, `pvi_oned`, `fielded_start`,
`fielded_end`. It raises `ValueError` naming the wave if `pvi_oned` is empty or
`fielded_start` is empty — Review Focus lines 1 and 4.

`waves_before` returns the trailing `window` waves whose `year` equals `year`,
newest last. It does **not** exclude any row: election rows were already removed
at ingest (Review Focus line 2).

`window_mean` returns `None` when `waves_before` is empty. It never substitutes a
longer or shorter window to avoid a `None`.

`contiguous_years` returns the longest run of consecutive years with at least one
wave, derived from data. Never hard-coded.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests 2>&1 | tail -4`
Expected: OK, 52 tests

- [ ] **Step 5: Check the real data through the module**

```bash
python3 - <<'EOF'
import sys; sys.path.insert(0, "charts")
from pathlib import Path
from stats import load_polls, window_mean
polls = load_polls(Path("data/polls_roymorgan_oned.csv"))
print("waves:", len(polls), "range:", min(p.year for p in polls), max(p.year for p in polls))
for y in (2019, 2022):
    m = window_mean(polls, y, window=12)
    print(f"  {y}: mean {m.value:.2f} from {m.n_used} waves, span {m.low}-{m.high}")
EOF
```

Expected: 48 waves, 2018-2022, `2019: mean 3.70 from 5 waves, span 3.0-4.5`,
`2022: mean 3.71 from 12 waves, span 3.0-5.0`. These match the spec's claim
section; if they do not, stop and reconcile with the spec before continuing.

- [ ] **Step 6: Commit**

```bash
git add charts/stats.py tests/test_scales.py
git commit -m "Add stats module for computed polling figures"
```

---

### Task 3: Chart 01 generator

**Files:**
- Modify: `charts/chart_01.py` (delete `SERIES` at line 51 and `X0, X1`/`Y0, Y1` at 58-59; rewrite `render` at line 119)
- Test: `tests/test_scales.py` (add class `TestChart01IsDataDriven`)

**Interfaces:**
- Consumes: `load_polls`, `window_mean`, `gaps` from Task 2; `data/roymorgan_election_results.csv`
- Produces: `charts/chart-01.svg` and `charts/chart-01-narrow.svg`, each declaring `data-source-id="roymorgan-pvi"` and **no** `data-unsourced` attribute

- [ ] **Step 1: Write the failing test**

Add `TestChart01IsDataDriven`:

| Test name | Asserts |
|---|---|
| `test_generator_holds_no_dataset_literal` | `charts/chart_01.py` source contains none of `"3.70"`, `"3.71"`, `"0.60"`, `"1.29"`, `"4.5"`, `"3.1"`, `"5.0"` |
| `test_output_declares_its_source_and_not_placeholder` | `chart-01.svg` has `data-source-id="roymorgan-pvi"`, no `data-unsourced` |
| `test_each_panel_labels_the_wave_count_it_used` | `chart-01.svg` contains `"5 waves"` and `"12 waves"` |

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest discover -s tests 2>&1 | tail -5`
Expected: FAIL — `4.5` found in source (the placeholder `SERIES` block), and
`data-source-id` absent from the SVG.

- [ ] **Step 3: Rewrite `charts/chart_01.py`**

Keep `VIEWPORTS` (line 45) unchanged so the label floor and the 640px switch are
untouched. Keep both hatch patterns. Delete `SERIES` and the axis constants.

Load both CSVs at module scope through `stats.py`. Compute every displayed value
from `window_mean` and `gaps`.

**Panel 1, the gap.** Two bars from a zero rule, poll-minus-result in
percentage points. `signed_gap` is negative when polling was low, so 2022 draws
below the rule. The axis spans the zero rule by construction, so no truncation
caveat is needed and none may be written.

**Panel 2, the evidence.** Per election, a vertical line from `low` to `high`
with the result marked by a distinct glyph. For 2022 the span tops out at the
result, which is the strongest fact in the dataset and must be visible without
annotation.

Label each panel `f"{year}  ·  {m.n_used} waves"`.

`desc_text` states the finding with its direction per election, the wave count,
and that no wave carries a published margin — all interpolated from computed
values.

- [ ] **Step 4: Regenerate and verify**

```bash
python3 charts/chart_01.py && python3 tools/build.py --check
```

Expected: build check passes at this task; Task 6 is what introduces the failing
AEC gate.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests 2>&1 | tail -4`
Expected: OK, 55 tests

- [ ] **Step 6: Commit**

```bash
git add charts/chart_01.py charts/chart-01.svg charts/chart-01-narrow.svg tests/test_scales.py
git commit -m "Build Chart 01 from ingested polling data"
```

---

### Task 4: Chart 02 generator

**Files:**
- Create: `charts/chart_02.py`
- Modify: `charts/stats.py` (add `seat_share`)
- Test: `tests/test_scales.py` (add class `TestChart02SeatShare`)

**Interfaces:**
- Consumes: `data/roymorgan_election_results.csv` (national primary, ten elections); seats won from the AEC party record registered as `aec-hor-2025-party-rep`
- Produces: `seat_share(seats: int, chamber: str = "house") -> float` in `charts/stats.py`; `charts/chart-02.svg` and `charts/chart-02-narrow.svg`

- [ ] **Step 1: Write the failing test for `seat_share`**

Add `TestSeatShare`:

| Test name | Asserts |
|---|---|
| `test_seat_share_is_over_151_and_only_151` | `seat_share(1) == 1/151`, `seat_share(0) == 0.0`, `seat_share(151) == 1.0` |
| `test_seat_share_rejects_a_senate_denominator` | `seat_share(1, chamber="senate")` raises `ValueError` |

- [ ] **Step 2: Run test to verify it fails**

Expected: `AttributeError: module 'stats' has no attribute 'seat_share'`

- [ ] **Step 3: Implement `seat_share` in `charts/stats.py`**

```python
def seat_share(seats: int, chamber: str = "house") -> float:
    """Share of the 151-seat House. The denominator is not a parameter."""
    if chamber != "house":
        raise ValueError(f"seat share is only defined for the House, not {chamber!r}")
    return seats / 151
```

- [ ] **Step 4: Write the failing test for the chart**

Add `TestChart02SeatShare`:

| Test name | Asserts |
|---|---|
| `test_by_election_is_an_annotation_not_a_point` | `chart-02.svg` contains `"Farrer"`, and no line beginning `<circle` contains it |
| `test_chart_02_is_sourced_not_placeholder` | `chart-02.svg` has `data-source-id=`, no `data-unsourced` |
| `test_2004_to_2016_discontinuity_is_marked` | `chart-02.svg` contains `"2004"` |

- [ ] **Step 5: Run test to verify it fails**

Expected: FAIL — `charts/chart-02.svg` does not exist.

- [ ] **Step 6: Create `charts/chart_02.py`**

Mirror `chart_01.py`'s structure: same `VIEWPORTS` shape, both hatch patterns,
`role="img"`/`<title>`/`<desc>`, wide and narrow from one pass.

Two lines on one axis, both percentages of the 151-seat House: national primary
vote, and seat share from `seat_share()`. Shade the gap between them.

**Farrer 2026 is an annotation.** Draw it as labelled text near the 2022 segment,
never as a point on either line. Its figures — 39.53% primary, 57.55% two-party
preferred, margin 15,302 — come from `aec-by-farrer-2026`.

Mark the 2004 to 2016 block. Those elections sit at 0.2 to 1.3% against 3.1 to
6.4% either side; thinner slate coverage means it is not the same measure, and
the chart must say so. This is the break already recorded in
`docs/data-sources.md`.

Declare `data-source-id="roymorgan-pvi aec-hor-2025-party-rep aec-by-farrer-2026"`
and no `data-unsourced`.

- [ ] **Step 7: Generate, register, verify**

```bash
python3 charts/chart_02.py
python3 -m unittest discover -s tests 2>&1 | tail -4
```

Expected: OK. Then register the chart in the placeholder-figures section of
`docs/data-sources.md` as **sourced**, so the existing build assertion passes
rather than being worked around.

- [ ] **Step 8: Commit**

```bash
git add charts/chart_02.py charts/chart-02.svg charts/chart-02-narrow.svg \
        charts/stats.py docs/data-sources.md tests/test_scales.py
git commit -m "Build Chart 02, seat share against vote share"
```

---

### Task 5: Template prose with injected figures

**Files:**
- Modify: `src/index.template.html` (replace the placeholder caption, add `<!-- chart:02 -->`)
- Modify: `tools/build.py` (add substitution in `build`, line 184)
- Test: `tests/test_scales.py` (add class `TestCaptionFiguresAreInjected`)

**Interfaces:**
- Consumes: `gaps` from Task 2, called by `tools/build.py`
- Produces: `FIGURE_SLOTS: dict[str, str]` in `tools/build.py`, substituted into the template

- [ ] **Step 1: Write the failing test**

Add `TestCaptionFiguresAreInjected`:

| Test name | Asserts |
|---|---|
| `test_template_contains_no_dataset_literal` | `src/index.template.html` contains none of `"3.70"`, `"3.71"`, `"0.60"`, `"1.29"`, `"48 waves"` |
| `test_template_declares_figure_slots` | template contains `{{gap_2019}}`, `{{gap_2022}}`, `{{waves_total}}` |
| `test_built_page_carries_the_computed_figures` | `index.html` contains `"3.70"` and `"1.29"`, and no `"{{"` |

- [ ] **Step 2: Run test to verify they fail**

Expected: FAIL — `{{gap_2019}}` not in template.

- [ ] **Step 3: Add substitution to `tools/build.py`**

In `build(template: str) -> str` (line 184), after chart injection, build a
`FIGURE_SLOTS` dict from `charts/stats.py` and replace every `{{key}}`:

```python
FIGURE_SLOTS: dict[str, str] = {}
```

Keys: `gap_2019`, `gap_2022` (signed, 2dp, with a leading `+` or `−`),
`mean_2019`, `mean_2022`, `waves_2019`, `waves_2022`, `waves_total`,
`result_2019`, `result_2022`.

Any `{{` remaining in the output after substitution is a build failure — an
unfilled slot is the prose equivalent of the unfilled chart placeholder the
build already refuses.

In the template, replace the placeholder caption with prose carrying those
slots, and state: the wave count and window per election; "N of M waves publish no
margin of error, no sample size or publication date"; the finding in one sentence
with its direction; and that this is not a claim about any publisher's
competence.

- [ ] **Step 4: Rebuild and verify**

```bash
python3 tools/build.py && python3 -m unittest discover -s tests 2>&1 | tail -4
```

Expected: OK. Confirm `index.html` contains no `{{`.

- [ ] **Step 5: Commit**

```bash
git add src/index.template.html tools/build.py index.html tests/test_scales.py
git commit -m "Write chart captions from computed values"
```

---

### Task 6: The nine build assertions

**Files:**
- Modify: `tools/build.py` (extend `validate` at line 216)
- Test: `tests/test_scales.py` (add class `TestChartGateAssertions`)

**Interfaces:**
- Consumes: `FIGURE_SLOTS` and the generated SVGs from Tasks 3–5
- Produces: `unsourced_result_problems`, `poll_field_problems`, `plotted_row_problems`, `label_count_problems` in `tools/build.py`

**Expect `--check` to FAIL after this task and stay failing until task 0003
delivers AEC figures. That failure is the gate working. Do not loosen any
assertion to make it green.**

- [ ] **Step 1: Write the failing tests**

This one test class is the safety net for the whole plan, so it is given in
full rather than as a table — every one of these must be seen to fire.

```python
class TestChartGateAssertions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "build", Path(__file__).resolve().parent.parent / "tools" / "build.py")
        cls.build = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.build)

    REGISTRY = "source_id: roymorgan-pvi\ncross_check_only: yes\n"

    def test_cross_check_only_ids_are_refused(self):
        """The gate. Until AEC confirms, this must fail."""
        svg = '<svg data-source-id="roymorgan-pvi"></svg>'
        problems = self.build.unsourced_result_problems("chart-01.svg", svg, self.REGISTRY)
        self.assertTrue(problems)
        self.assertIn("cross-check", problems[0].lower())

    def test_aec_confirmed_id_clears_the_gate(self):
        registry = "source_id: aec-hor-2022\n"
        svg = '<svg data-source-id="aec-hor-2022"></svg>'
        self.assertEqual(self.build.unsourced_result_problems("c.svg", svg, registry), [])

    def test_populated_margin_is_refused(self):
        problems = self.build.poll_field_problems(
            [{"wave": "w1", "margin_of_error": "2.5",
              "fielded_start": "2022-01-01",
              "publishes_margin_of_error": "no"}])
        self.assertTrue(problems)

    def test_null_margin_with_declared_absence_passes(self):
        problems = self.build.poll_field_problems(
            [{"wave": "w1", "margin_of_error": "",
              "fielded_start": "2022-01-01",
              "publishes_margin_of_error": "no"}])
        self.assertEqual(problems, [])

    def test_missing_field_window_is_refused(self):
        problems = self.build.poll_field_problems(
            [{"wave": "w1", "margin_of_error": "", "fielded_start": "",
              "publishes_margin_of_error": "no"}])
        self.assertTrue(problems)

    def test_by_election_in_the_series_is_refused(self):
        rows = [{"year": 2019, "is_by_election": "no"},
                {"year": 2026, "is_by_election": "yes"}]
        self.assertTrue(self.build.plotted_row_problems(rows))

    def test_label_count_must_match_the_arithmetic(self):
        self.assertTrue(self.build.label_count_problems({2019: (5, 12)}))

    def test_matching_label_counts_pass(self):
        self.assertEqual(self.build.label_count_problems({2019: (5, 5)}), [])
```

- [ ] **Step 2: Run tests to verify they fail**

Expected: `AttributeError` on each of the four new functions.

- [ ] **Step 3: Implement the four functions in `tools/build.py`**

```python
def unsourced_result_problems(name: str, svg: str, registry: str) -> list[str]
def poll_field_problems(rows: Sequence[dict]) -> list[str]
def plotted_row_problems(rows: Sequence[dict]) -> list[str]
def label_count_problems(pairs: dict[int, tuple[int, int]]) -> list[str]
```

`unsourced_result_problems` resolves each `data-source-id` token against the
registry and fails if every resolved id is marked `cross_check_only: yes`.

`poll_field_problems` fails when `margin_of_error` is non-empty (Review Focus 4)
or `fielded_start` is empty (Review Focus 1), naming the wave.

`plotted_row_problems` fails on any row with `is_by_election == "yes"` (Review
Focus 5).

`label_count_problems` takes `{year: (stated, used)}` and fails where they
differ (Review Focus 3).

- [ ] **Step 4: Wire all nine into `validate`**

The remaining five: no dataset literal in chart source; caption wave count equals
CSV rows used; no wave outside the contiguous range without `blank_reason`; seat
share denominator is 151 only; House and Senate never share an axis.

- [ ] **Step 5: Verify each assertion fires**

Copy the repo to a scratch directory, break one input per assertion, and confirm
`--check` exits 1 each time. **An assertion that has never failed has not been
tested.** Restore between cases.

```bash
rm -rf /tmp/gatetest && cp -r . /tmp/gatetest && cd /tmp/gatetest && rm -rf .git
# per-assertion: mutate one input, run python3 tools/build.py --check, expect exit 1
```

- [ ] **Step 6: Confirm the real repo is red for the right reason**

```bash
python3 tools/build.py --check; echo "exit=$?"
```

Expected: exit 1, with the cross-check message naming `roymorgan-pvi`. **Any
other failure means a bug, not the gate.** Then `cd - && rm -rf /tmp/gatetest`.

- [ ] **Step 7: Commit**

```bash
git add tools/build.py tests/test_scales.py
git commit -m "Refuse unconfirmed results and unsourced figures"
```

State in the message that CI is red pending task 0003 and that the assertion is
deliberate.

---

### Task 7: Registry, chart specs, TASKS

**Files:**
- Modify: `docs/data-sources.md`, `docs/chart-specs.md`, `TASKS.md`

- [ ] **Step 1: Register the dataset**

Add to the ingested-datasets section: `data/polls_roymorgan_oned.csv`, 48 rows,
2018–2022 contiguous, and the three null fields with the reason each is null.
Note that 2013 to 2016 are unusable and 2017 absent, as a property of the source.

- [ ] **Step 2: Mark Chart 01 built in `docs/chart-specs.md`**

Replace the placeholder entry with a pointer to the spec, and record that
Chart 04 is now Chart 02 and still awaiting a keep-or-cut decision.

- [ ] **Step 3: Update `TASKS.md`**

0007 status, and an Events entry recording the finding: 0.60pp high in 2019,
1.29pp low in 2022, computed at build time. Record that the gate is red pending
0003.

- [ ] **Step 4: Commit**

```bash
git add docs/data-sources.md docs/chart-specs.md TASKS.md
git commit -m "Register the polling dataset and update task records"
```

---

### Task 8: Browser verification

Not automatable. Measure; do not assume.

- [ ] **Step 1: Serve the page and check three widths**

```bash
python3 -m http.server 8000
```

At 320px, 640px and 1280px confirm: both charts render; wide and narrow variants
switch at 640px; labels measure 16px wide and 10.7px at 320px viewport. If the
floor is breached, fix the viewBox rather than accepting the measurement — the
task 0006 note records why.

- [ ] **Step 2: Check reduced motion and images-off**

`prefers-reduced-motion` honoured. With images off, every chart still reads via
`<title>` and `<desc>`.

- [ ] **Step 3: Confirm the by-election annotation reads as an annotation**

It must be visibly outside the plotted series, not a point on it.

- [ ] **Step 4: Screenshot each width and commit**

```bash
git add screenshots/
git commit -m "Verify both charts in a browser at three widths"
```

---

## Deliberately not in this plan

- **Task 0003**, AEC confirmation. The gate waits on it. Nothing here substitutes
  for it and no step pretends otherwise.
- **The print check.** On hold by Dale's decision, 2026-10-04.
- **Per-division seat efficiency.** Needs the archived model's eight 2022
  primaries verified against AEC. In `TASKS.md` BACKLOG.
- **A national polling aggregate across houses.** Only Roy Morgan has a discrete
  column for this party.

## Order

1, 2, 3, 4 (either order after 2), 5, 6, 7, 8.

Tasks 1 and 2 are the foundation. Task 6 is last among the code tasks because
its gate deliberately fails until task 0003 lands, and a known, explained red
build beats a surprise mid-implementation.