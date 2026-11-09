"""Manual lead/window arithmetic contracts by Jason Stys.

Functions: case and test_*; variables: independently chosen revisions, target boundaries and errors.
Exact lines: docs/CODE_INDEX.md. No best-error or best-window selection is used.
"""

import math

from weatherlab.engine import Settings, build_run, forecast_comparison
from weatherlab.model import Case, Forecast, Observation


def case() -> Case:
    """Four bins with missing truth, unknown issuance and a deliberately worse recent forecast."""
    return Case(
        "manual",
        "2026-01-02T00:00:00Z",
        4,
        (
            Observation("2026-01-02T00:00:00Z", 2, "observed"),
            Observation("2026-01-02T03:00:00Z", 4, "observed"),
            Observation("2026-01-02T06:00:00Z", 6, "observed"),
            Observation("2026-01-02T09:00:00Z", None, "missing"),
        ),
        (),
        (
            Forecast("2026-01-02T00:00:00Z", None, 9),
            Forecast("2026-01-02T03:00:00Z", "2026-01-01T03:00:00Z", 5),
            Forecast("2026-01-02T06:00:00Z", "2026-01-01T18:00:00Z", 5),
            Forecast("2026-01-02T06:00:00Z", "2026-01-02T03:00:00Z", 3),
            Forecast("2026-01-02T09:00:00Z", "2026-01-01T09:00:00Z", 6),
        ),
    )


def test_manual_revision_scores_and_coverage():
    """Three-hour errors [1,-3], twelve-hour [1,-1], twenty-four-hour [1] have known scores."""
    rows = forecast_comparison(case(), Settings())
    three, twelve, day = rows[:3]
    assert (three["scores"]["mae"], three["scores"]["bias"]) == (2, -1)
    assert three["scores"]["rmse"] == round(math.sqrt(5), 9)
    assert twelve["scores"]["mae"] == twelve["scores"]["rmse"] == 1
    assert twelve["scores"]["bias"] == 0
    assert day["scores"]["scored"] == 1
    assert three["selected"][1]["issued"] == "2026-01-02T03:00:00Z"
    assert twelve["selected"][1]["issued"] == "2026-01-01T18:00:00Z"
    assert three["available_observations"] == 3
    assert three["issuance_eligible_targets"] == 3
    assert three["scored_bin_coverage"] == 0.5
    assert three["scored_observation_coverage"] == round(2 / 3, 9)


def test_half_open_windows_partition_targets_without_pooling_revisions():
    """The 06:00 boundary belongs to later; each scored target occurs once per cutoff/window."""
    rows = forecast_comparison(case(), Settings())
    for offset in range(3):
        whole, early, late = rows[offset], rows[3 + offset], rows[6 + offset]
        assert early["end_exclusive"] == late["start"] == "2026-01-02T06:00:00Z"
        assert whole["scores"]["scored"] == early["scores"]["scored"] + late["scores"]["scored"]
        assert not (
            {r["target"] for r in early["selected"]} & {r["target"] for r in late["selected"]}
        )
    assert rows[6]["scores"]["mae"] == 3
    assert rows[7]["scores"]["mae"] == 1


def test_empty_half_and_unknown_issuance_do_not_inflate_skill():
    """No truth produces null errors; zero-length halves have undefined coverage, never perfect."""
    single = Case("one", "2026-01-02T00:00:00Z", 1, (), (), ())
    rows = forecast_comparison(single, Settings())
    assert rows[3]["bins"] == 0 and rows[3]["observation_coverage"] is None
    assert rows[0]["scores"]["mae"] is None and rows[0]["scored_observation_coverage"] is None
    assert rows[6]["bins"] == 1 and rows[6]["missing_observations"] == 1
    report = build_run()
    assert all(
        r["scores"]["scored"] == 0 and r["scores"]["mae"] is None
        for r in report["forecast_comparison"]
    )
