"""Independent arithmetic, finite-grid and property verification by Jason Stys.

Functions: test_* contracts. Variables: settings product, manual errors, random paired series.
Exact definitions/arguments: docs/CODE_INDEX.md. Assertions are not production-model fallbacks.
"""

import hashlib
import itertools
import json
import math
from dataclasses import replace

import pytest
from hypothesis import given
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st

from weatherlab.engine import (
    CHOICES,
    RESOURCES,
    SCENARIOS,
    Settings,
    analyze,
    build_run,
    canonical,
    correlation,
    fixture,
    snapshot,
)
from weatherlab.model import STEP, Forecast, instant, stamp


@pytest.mark.parametrize(
    "scenario,threshold,lag,lead", list(itertools.product(SCENARIOS, *CHOICES.values()))
)
def test_grid(scenario, threshold, lag, lead):
    """All 162 finite configurations preserve totals, report identity and non-leaking target selection."""
    config = Settings(scenario, threshold, lag, lead)
    run = build_run(config)
    assert canonical(run) == canonical(build_run(config))
    content = dict(run)
    identity = content.pop("id")
    assert hashlib.sha256(canonical(content)).hexdigest() == identity
    assert run["totals"]["available"] + run["totals"]["missing"] == run["totals"]["bins"]
    scored = [f for f in run["forecasts"] if f["status"] == "scored"]
    assert len(scored) == len({f["target"] for f in scored}) == run["scores"]["scored"]
    for row in scored:
        assert row["lead_hours"] >= lead and instant(row["issued"]) < instant(row["target"])
    assert sum(run["scores"]["statuses"].values()) == len(run["forecasts"])


def test_noaa_snapshot():
    """Original public-data hashes and manual endpoint values match; no invented health or issuance."""
    run = build_run()
    assert run["totals"] == {
        "bins": 56,
        "available": 56,
        "estimated": 56,
        "missing": 0,
        "events": 0,
        "paired": 0,
    }
    assert run["rows"][0]["time"] == "2026-10-14T00:00:00Z"
    assert run["rows"][0]["kp"] == 2.33 and run["rows"][-1]["kp"] == 3.0
    assert run["scores"]["statuses"] == {"unknown-issuance": 17}
    assert run["scores"]["mae"] is None and run["association"]["r"] is None
    metadata = json.loads((RESOURCES / "snapshot.json").read_bytes())
    for key, name in (("observations", "noaa-observed.json"), ("forecasts", "noaa-forecast.json")):
        assert (
            hashlib.sha256((RESOURCES / name).read_bytes()).hexdigest() == metadata[key]["sha256"]
        )


def test_snapshot_tamper(monkeypatch, tmp_path):
    """A modified original response stops snapshot use instead of silently changing provenance."""
    metadata = (RESOURCES / "snapshot.json").read_bytes()
    (tmp_path / "snapshot.json").write_bytes(metadata)
    (tmp_path / "noaa-observed.json").write_bytes(b"[]")
    monkeypatch.setattr("weatherlab.engine.RESOURCES", tmp_path)
    with pytest.raises(RuntimeError, match="checksum"):
        snapshot()


def test_manual_score_and_revision():
    """Hand-derived baseline errors and later worse revision prove no best-error cherry-picking."""
    run = build_run(Settings("synthetic-storm"))
    assert (run["scores"]["mae"], run["scores"]["rmse"], run["scores"]["bias"]) == (1.0, 1.0, -1.0)
    assert run["scores"]["confusion"] == {
        "true_positive": 5,
        "false_positive": 0,
        "false_negative": 1,
        "true_negative": 10,
    }
    revised = build_run(Settings("forecast-revisions"))
    scored = [
        f
        for f in revised["forecasts"]
        if f["status"] == "scored" and f["target"] == "2024-05-10T18:00:00Z"
    ]
    assert len(scored) == 1 and scored[0]["kp"] == 6.0 and scored[0]["error"] == -2.0
    assert revised["scores"]["mae"] == 17 / 16
    assert revised["scores"]["rmse"] == pytest.approx(math.sqrt(19 / 16))
    assert revised["scores"]["statuses"]["not-before-target"] == 1
    long = build_run(Settings("forecast-revisions", lead_hours=12))
    assert long["scores"]["mae"] == 1.0 and long["scores"]["statuses"]["insufficient-lead"] == 1


def test_positive_lag_and_missingness():
    """Positive lag shifts the health time forward; out-of-window tails are not filled with zeros."""
    run = build_run(Settings("synthetic-storm", lag_hours=6))
    assert run["rows"][0]["health_time"] == "2024-05-10T06:00:00Z"
    assert run["rows"][0]["drops"] == 3
    assert run["totals"]["paired"] == 14
    assert all(row["drops"] is None for row in run["rows"][-2:])
    missing = build_run(Settings("missing-bins"))
    assert missing["totals"]["missing"] == 3 and missing["totals"]["paired"] == 11
    assert missing["rows"][2]["quality"] == "absent" and missing["rows"][5]["quality"] == "missing"


@pytest.mark.parametrize(
    "scenario,reason", [("flat-signal", "constant-series"), ("empty-window", "insufficient-pairs")]
)
def test_undefined_correlation(scenario, reason):
    """Undefined statistics remain null with reasons, not misleading zeros or NaN JSON."""
    association = build_run(Settings(scenario))["association"]
    assert association["r"] is None and association["status"] == reason


@pytest.mark.parametrize(
    "key,value",
    [
        ("scenario", "bad"),
        ("scenario", []),
        ("threshold", True),
        ("threshold", 5.0),
        ("lag_hours", -3),
        ("lead_hours", 0),
    ],
)
def test_settings(key, value):
    """Finite settings reject bool/float coercion and unsupported values."""
    with pytest.raises(ValueError):
        Settings(**{key: value})


def test_unknown_fixture_and_future_issue():
    """Unknown cases fail, and forecasts issued after target never enter skill scores."""
    with pytest.raises(ValueError):
        fixture("unknown")
    case, _ = fixture("synthetic-storm")
    forecast = Forecast(case.start, stamp(instant(case.start) + STEP), 9.0)
    run = analyze(replace(case, forecasts=(forecast,)), Settings(), {})
    assert run["scores"]["scored"] == 0 and run["forecasts"][0]["status"] == "not-before-target"


@hypothesis_settings(max_examples=100, derandomize=True, deadline=None)
@given(st.lists(st.tuples(st.integers(0, 9), st.integers(0, 100)), min_size=3, max_size=100))
def test_independent_pearson(samples):
    """Compare centered production r to independent pairwise-difference identity over 100 examples."""
    pairs = [(float(x), y) for x, y in samples]
    result, status = correlation(pairs)
    xx = sum((a[0] - b[0]) ** 2 for a, b in itertools.combinations(samples, 2))
    yy = sum((a[1] - b[1]) ** 2 for a, b in itertools.combinations(samples, 2))
    xy = sum((a[0] - b[0]) * (a[1] - b[1]) for a, b in itertools.combinations(samples, 2))
    if not xx or not yy:
        assert result is None and status == "constant-series"
    else:
        assert result == pytest.approx(xy / math.sqrt(xx * yy), abs=1e-12)
