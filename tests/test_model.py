"""Schema, duplicate, range, UTC and import-boundary tests by Jason Stys.

Functions: document, test_* contracts. Variables: hostile values and exact JSON input structures.
Exact lines: docs/CODE_INDEX.md. No executable payloads are run.
"""

import json

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from weatherlab.engine import Settings, build_import, fixture
from weatherlab.model import MAX_BYTES, instant, load_case, number, parse_case


def document():
    """Fresh JSON lists rather than dataclass tuple containers emulate an actual JSON import."""
    return json.loads(json.dumps(fixture("synthetic-storm")[0].document()))


@pytest.mark.parametrize("value", [None, True, -1, 10, float("nan"), float("inf"), "5", 10**300])
def test_numeric_values(value):
    """Kp validates finite 0..9 without booleans, strings, huge-int overflow or coercion."""
    with pytest.raises(ValueError):
        number(value, 9)


@pytest.mark.parametrize(
    "value",
    [
        "2024-05-10T00:00:00",
        "2024-05-10T00:00:00+00:00",
        "2024-05-10T00:00:60Z",
        "1999-01-01T00:00:00Z",
        "2024-05-10T01:00:00Z",
        "2024-02-30T00:00:00Z",
        0,
    ],
)
def test_utc_alignment(value):
    """Reject naive/offset/non-grid/leap-second/out-of-range timestamps explicitly."""
    with pytest.raises(ValueError):
        instant(value, True)


@pytest.mark.parametrize(
    "key,value",
    [
        ("schema", True),
        ("schema", 2),
        ("name", "<script>"),
        ("name", "a" * 49),
        ("bins", 0),
        ("bins", 257),
        ("bins", 1.0),
        ("start", "2099-12-31T21:00:00Z"),
        ("observations", {}),
        ("health", [{}]),
        ("forecasts", [{}]),
    ],
)
def test_root_contract(key, value):
    """Root schema requires exact types, bounded grid and structured lists."""
    case = document()
    case[key] = value
    with pytest.raises(ValueError):
        parse_case(case)


@pytest.mark.parametrize("kind", ["observations", "health", "forecasts"])
def test_duplicate_records(kind):
    """Duplicate bins/revisions are not silently last-write-wins, independent of order."""
    case = document()
    case[kind].append(case[kind][0])
    with pytest.raises(ValueError, match="Duplicate"):
        parse_case(case)


@pytest.mark.parametrize(
    "path,key,value",
    [
        ("observations", "quality", "bad"),
        ("observations", "quality", []),
        ("observations", "kp", None),
        ("observations", "time", "2024-06-01T00:00:00Z"),
        ("health", "drops", 1.0),
        ("health", "time", "2024-06-01T00:00:00Z"),
        ("forecasts", "issued", "bad"),
        ("forecasts", "kp", 10),
        ("observations", "extra", 1),
    ],
)
def test_record_contract(path, key, value):
    """Unknown record fields, out-of-window bins and invalid/missing quantities fail closed."""
    case = document()
    case[path][0][key] = value
    with pytest.raises(ValueError):
        parse_case(case)


def test_envelope_and_local_provenance(tmp_path):
    """Imports are bounded, reject duplicate keys, and never become trusted NOAA records by name."""
    path = tmp_path / "input.json"
    body = document()
    body["name"] = "noaa-snapshot"
    path.write_text(json.dumps(body), encoding="utf-8")
    run = build_import(path, Settings())
    assert run["provenance"]["weather"] == "unverified local input"
    for payload in (
        b"{}",
        b'{"schema":1,"schema":1}',
        b"\xff",
        b"[" * 1100 + b"]" * 1100,
        b" " * (MAX_BYTES + 1),
    ):
        path.write_bytes(payload)
        with pytest.raises(ValueError):
            load_case(path)


@settings(max_examples=100, derandomize=True, deadline=None)
@given(st.lists(st.integers(0, 9), min_size=1, max_size=16))
def test_order_invariant(values):
    """Strict imports normalize record order, preserving byte-identical portable input for 100 examples."""
    case = document()
    case["observations"] = case["observations"][: len(values)]
    for row, value in zip(case["observations"], values, strict=True):
        row["kp"] = value
    expected = parse_case(case)
    case["observations"].reverse()
    case["health"].reverse()
    case["forecasts"].reverse()
    assert parse_case(case) == expected
