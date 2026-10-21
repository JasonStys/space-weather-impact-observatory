"""Strict UTC experiment schema and bounded JSON by Jason Stys.

Types: Observation, Health, Forecast, Case. Validation functions describe units/contracts.
Variables/arguments and exact definition lines: docs/CODE_INDEX.md. No executable input.
"""

import json
import math
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

STEP = timedelta(hours=3)
MAX_BYTES = 524288


def instant(value: Any, aligned: bool = False) -> datetime:
    """Parse explicit second-resolution UTC, optionally requiring a three-hour bin boundary."""
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value
    ):
        raise ValueError("Expected explicit UTC timestamp")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not 2000 <= result.year <= 2099 or (
        aligned and (result.hour % 3 or result.minute or result.second)
    ):
        raise ValueError("Timestamp outside supported grid")
    return result


def stamp(value: datetime) -> str:
    """Serialize a UTC grid value without locale-dependent formatting."""
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def number(value: Any, maximum: float, integer: bool = False) -> float:
    """Require finite non-boolean nonnegative quantities, with integer counts where requested."""
    if type(value) not in (int, float) or not 0 <= value <= maximum or not math.isfinite(value):
        raise ValueError("Invalid finite quantity")
    if integer and type(value) is not int:
        raise ValueError("Count must be an integer")
    return float(value)


def fields(value: Any, keys: set[str]) -> dict[str, Any]:
    """Require exact object keys; unknown fields are never silently dropped."""
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError("Unexpected object fields")
    return value


@dataclass(frozen=True)
class Observation:
    """Three-hour Kp bin; missing is null, not a zero or an interpolated value."""

    time: str
    kp: float | None
    quality: str


@dataclass(frozen=True)
class Health:
    """Synthetic or supplied three-hour dropped-frame count; never real spacecraft impact inference."""

    time: str
    drops: int | None


@dataclass(frozen=True)
class Forecast:
    """A target-bin prediction with a separately known UTC issuance instant, or null unknown issuance."""

    target: str
    issued: str | None
    kp: float


@dataclass(frozen=True)
class Case:
    """Bounded grid plus sparse typed records; provenance is assigned outside imported JSON."""

    name: str
    start: str
    bins: int
    observations: tuple[Observation, ...]
    health: tuple[Health, ...]
    forecasts: tuple[Forecast, ...]

    def document(self) -> dict[str, Any]:
        """Return the portable JSON input contract without trusted provenance claims."""
        return {
            "schema": 1,
            "name": self.name,
            "start": self.start,
            "bins": self.bins,
            "observations": [asdict(row) for row in self.observations],
            "health": [asdict(row) for row in self.health],
            "forecasts": [asdict(row) for row in self.forecasts],
        }


def parse_case(value: Any) -> Case:
    """Validate unique keys/time bins and supported ranges before analysis; preserve input omissions."""
    row = fields(value, {"schema", "name", "start", "bins", "observations", "health", "forecasts"})
    if type(row["schema"]) is not int or row["schema"] != 1:
        raise ValueError("Unsupported schema")
    if not isinstance(row["name"], str) or not re.fullmatch(
        r"[a-z0-9][a-z0-9-]{0,47}", row["name"]
    ):
        raise ValueError("Invalid case name")
    start = instant(row["start"], True)
    number(row["bins"], 256, True)
    if not row["bins"]:
        raise ValueError("At least one grid bin required")
    end = start + row["bins"] * STEP
    if end.year > 2099:
        raise ValueError("Grid end outside supported years")
    for key, cap in (("observations", 256), ("health", 256), ("forecasts", 2048)):
        if not isinstance(row[key], list) or len(row[key]) > cap:
            raise ValueError("Invalid record list")
    observations, health, forecasts = [], [], []
    for item in row["observations"]:
        item = fields(item, {"time", "kp", "quality"})
        time = instant(item["time"], True)
        if not start <= time < end or item["quality"] not in ("observed", "estimated", "missing"):
            raise ValueError("Invalid observation")
        if (item["kp"] is None) != (item["quality"] == "missing"):
            raise ValueError("Missing quality/value disagreement")
        kp = None if item["kp"] is None else number(item["kp"], 9)
        observations.append(Observation(item["time"], kp, item["quality"]))
    for item in row["health"]:
        item = fields(item, {"time", "drops"})
        if not start <= instant(item["time"], True) < end:
            raise ValueError("Health bin outside grid")
        drops = None if item["drops"] is None else int(number(item["drops"], 10000, True))
        health.append(Health(item["time"], drops))
    for item in row["forecasts"]:
        item = fields(item, {"target", "issued", "kp"})
        instant(item["target"], True)
        if item["issued"] is not None:
            instant(item["issued"])
        forecasts.append(Forecast(item["target"], item["issued"], number(item["kp"], 9)))
    if len({o.time for o in observations}) != len(observations) or len(
        {h.time for h in health}
    ) != len(health):
        raise ValueError("Duplicate time bin")
    if len({(f.target, f.issued) for f in forecasts}) != len(forecasts):
        raise ValueError("Duplicate forecast revision")
    return Case(
        row["name"],
        row["start"],
        row["bins"],
        tuple(sorted(observations, key=lambda o: o.time)),
        tuple(sorted(health, key=lambda h: h.time)),
        tuple(sorted(forecasts, key=lambda f: (f.target, f.issued or ""))),
    )


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON object keys rather than accepting the last value."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def load_case(path: Path) -> Case:
    """Read at most 512 KiB plus one sentinel byte; reject malformed/recursive JSON safely."""
    with path.open("rb") as source:
        body = source.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise ValueError("Input exceeds 512 KiB")
    try:
        return parse_case(json.loads(body.decode("utf-8"), object_pairs_hook=unique_object))
    except (RecursionError, UnicodeError) as error:
        raise ValueError("Invalid JSON envelope") from error
