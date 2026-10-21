"""UTC alignment, forecast leakage gates and descriptive association by Jason Stys.

Functions: snapshot, fixture, catalog, analyze, build_run, build_import, correlation.
Settings and all variables: docs/CODE_INDEX.md. No online fetch or causal/operational prediction.
"""

import hashlib
import json
import math
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from weatherlab.model import STEP, Case, Forecast, instant, load_case, parse_case, stamp

RESOURCES = Path(__file__).parent / "resources"
SCENARIOS = {
    "noaa-snapshot": "NOAA frozen snapshot",
    "synthetic-storm": "Synthetic storm and health",
    "missing-bins": "Missing and estimated bins",
    "forecast-revisions": "Forecast revisions and leakage",
    "flat-signal": "Flat signal / undefined correlation",
    "empty-window": "Empty observation window",
}
CHOICES = {"threshold": (4, 5, 6), "lag_hours": (0, 3, 6), "lead_hours": (3, 12, 24)}
LIMITATIONS = [
    "Offline educational evidence, not current conditions, mission guidance or an impact forecast.",
    "Association is descriptive, not causation. Health fixtures are invented, not spacecraft observations.",
    "Kp is a planetary quasi-logarithmic index, not a local dose, damage or radiation measurement.",
    "No interpolation, missing-as-zero substitution, significance test or automatic lag optimization.",
    "Forecast scoring requires a known issue time, positive sufficient lead and a matching nonmissing target bin.",
    "Latest eligible revision per target is selected by issuance time, never by observed error.",
]


@dataclass(frozen=True)
class Settings:
    """Finite sensitivity choices; positive lag pairs weather(t) with health(t+lag)."""

    scenario: str = "noaa-snapshot"
    threshold: int = 5
    lag_hours: int = 0
    lead_hours: int = 3

    def __post_init__(self) -> None:
        """Reject coercions, booleans and unknown settings before accessing any resources."""
        if not isinstance(self.scenario, str) or self.scenario not in SCENARIOS:
            raise ValueError("Unknown experiment")
        for key, choices in CHOICES.items():
            value = getattr(self, key)
            if type(value) is not int or value not in choices:
                raise ValueError("Unsupported setting")


def canonical(value: Any) -> bytes:
    """Stable JSON forbids NaN/infinity and excludes runtime/machine-dependent metadata."""
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False) + "\n"
    ).encode()


def snapshot() -> tuple[Case, dict[str, Any]]:
    """Verify original NOAA response hashes; adapt observed estimates and unknown-issuance predictions."""
    metadata = json.loads((RESOURCES / "snapshot.json").read_bytes())
    bodies = {}
    for key, name in (("observations", "noaa-observed.json"), ("forecasts", "noaa-forecast.json")):
        body = (RESOURCES / name).read_bytes()
        if hashlib.sha256(body).hexdigest() != metadata[key]["sha256"]:
            raise RuntimeError("Bundled NOAA snapshot checksum mismatch")
        bodies[key] = json.loads(body)
    observations: list[dict[str, Any]] = [
        {"time": r["time_tag"] + "Z", "kp": r["Kp"], "quality": "estimated"}
        for r in bodies["observations"]
    ]
    forecasts: list[dict[str, Any]] = [
        {"target": r["time_tag"] + "Z", "issued": None, "kp": r["kp"]}
        for r in bodies["forecasts"]
        if r["observed"] == "predicted"
    ]
    start = observations[0]["time"]
    bins = int((instant(observations[-1]["time"]) - instant(start)) / STEP) + 1
    case = parse_case(
        {
            "schema": 1,
            "name": "noaa-snapshot",
            "start": start,
            "bins": bins,
            "observations": observations,
            "health": [],
            "forecasts": forecasts,
        }
    )
    return case, {
        "weather": "NOAA SWPC estimated planetary Kp snapshot",
        "health": "none supplied",
        "forecasts": "NOAA predicted records; issuance unknown, not scoreable",
        "snapshot": metadata,
    }


def fixture(scenario: str) -> tuple[Case, dict[str, Any]]:
    """Build explicitly invented edge cases, with no claim of physical spacecraft response."""
    if scenario not in SCENARIOS:
        raise ValueError("Unknown fixture")
    if scenario == "noaa-snapshot":
        return snapshot()
    start = instant("2024-05-10T00:00:00Z")
    kp = [1, 2, 2, 3, 5, 7, 8, 9, 7, 6, 4, 3, 2, 1, 2, 2]
    drops = [2, 1, 3, 2, 3, 8, 11, 16, 12, 9, 5, 3, 2, 1, 3, 2]
    observations: list[dict[str, Any]] = [
        {"time": stamp(start + i * STEP), "kp": float(k), "quality": "observed"}
        for i, k in enumerate(kp)
    ]
    health: list[dict[str, Any]] = [
        {"time": stamp(start + i * STEP), "drops": d} for i, d in enumerate(drops)
    ]
    forecasts: list[dict[str, Any]] = [
        {
            "target": r["time"],
            "issued": stamp(instant(r["time"]) - 4 * STEP),
            "kp": max(0.0, r["kp"] - 1.0),
        }
        for r in observations
    ]
    if scenario == "missing-bins":
        observations = [r for i, r in enumerate(observations) if i not in (2, 7)]
        observations[4] = {**observations[4], "kp": None, "quality": "missing"}
        observations[6]["quality"] = "estimated"
        health = [r for i, r in enumerate(health) if i != 10]
        health[3]["drops"] = None
    elif scenario == "forecast-revisions":
        target = observations[6]["time"]
        forecasts.extend(
            [
                {"target": target, "issued": stamp(instant(target) - 2 * STEP), "kp": 6.0},
                {"target": target, "issued": target, "kp": 8.0},
                {"target": observations[7]["time"], "issued": None, "kp": 9.0},
                {"target": stamp(start + 20 * STEP), "issued": stamp(start), "kp": 5.0},
            ]
        )
    elif scenario == "flat-signal":
        for row in observations:
            row["kp"] = 2.0
        for record in health:
            record["drops"] = 3
    elif scenario == "empty-window":
        observations, health, forecasts = [], [], []
    case = parse_case(
        {
            "schema": 1,
            "name": scenario,
            "start": stamp(start),
            "bins": 16,
            "observations": observations,
            "health": health,
            "forecasts": forecasts,
        }
    )
    return case, {
        "weather": "invented Kp fixture, not a historical storm reconstruction",
        "health": "invented dropped-frame counts",
        "forecasts": "invented forecasts with explicit issue times",
    }


def catalog() -> dict[str, Any]:
    """Describe allowlisted experiments/settings for clients; no arbitrary file or URL controls."""
    return {"scenarios": SCENARIOS, "choices": CHOICES, "defaults": asdict(Settings())}


def correlation(pairs: list[tuple[float, int]]) -> tuple[float | None, str]:
    """Centered Pearson descriptive r; null with explicit reason for insufficient/constant pairs."""
    if len(pairs) < 3:
        return None, "insufficient-pairs"
    xmean = math.fsum(x for x, _ in pairs) / len(pairs)
    ymean = math.fsum(y for _, y in pairs) / len(pairs)
    xx = math.fsum((x - xmean) ** 2 for x, _ in pairs)
    yy = math.fsum((y - ymean) ** 2 for _, y in pairs)
    if xx == 0 or yy == 0:
        return None, "constant-series"
    xy = math.fsum((x - xmean) * (y - ymean) for x, y in pairs)
    return max(-1.0, min(1.0, xy / math.sqrt(xx * yy))), "descriptive-only"


def assess_forecasts(case: Case, settings: Settings) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Gate issue/lead/targets first, then select latest eligible revision and calculate errors."""
    observed = {o.time: o for o in case.observations}
    eligible: dict[str, list[Forecast]] = {}
    rows: list[dict[str, Any]] = []
    for forecast in case.forecasts:
        lead = (
            None
            if forecast.issued is None
            else (instant(forecast.target) - instant(forecast.issued)).total_seconds() / 3600
        )
        if lead is None:
            status = "unknown-issuance"
        elif lead <= 0:
            status = "not-before-target"
        elif lead < settings.lead_hours:
            status = "insufficient-lead"
        elif forecast.target not in observed or observed[forecast.target].kp is None:
            status = "missing-observation"
        else:
            status = "eligible"
            eligible.setdefault(forecast.target, []).append(forecast)
        rows.append(
            {
                **asdict(forecast),
                "lead_hours": lead,
                "status": status,
                "actual": None,
                "error": None,
            }
        )
    selected = {
        target: max(revisions, key=lambda f: f.issued or "").issued
        for target, revisions in eligible.items()
    }
    errors = []
    confusion = {"true_positive": 0, "false_positive": 0, "false_negative": 0, "true_negative": 0}
    for row in rows:
        if row["status"] != "eligible":
            continue
        if row["issued"] != selected[row["target"]]:
            row["status"] = "superseded"
            continue
        actual = observed[row["target"]].kp
        assert actual is not None
        error = row["kp"] - actual
        row.update(status="scored", actual=actual, error=round(error, 9))
        errors.append(error)
        positive, event = row["kp"] >= settings.threshold, actual >= settings.threshold
        key = (
            ("true_positive" if event else "false_positive")
            if positive
            else ("false_negative" if event else "true_negative")
        )
        confusion[key] += 1
    count = len(errors)
    metrics = {
        "scored": count,
        "excluded": len(rows) - count,
        "mae": round(math.fsum(abs(e) for e in errors) / count, 9) if count else None,
        "rmse": round(math.sqrt(math.fsum(e * e for e in errors) / count), 9) if count else None,
        "bias": round(math.fsum(errors) / count, 9) if count else None,
        "confusion": confusion,
        "statuses": dict(sorted(Counter(r["status"] for r in rows).items())),
    }
    return rows, metrics


def analyze(case: Case, settings: Settings, provenance: dict[str, Any]) -> dict[str, Any]:
    """Perform exact UTC sparse joins, preserving missingness and displaying selected lag explicitly."""
    obs = {o.time: o for o in case.observations}
    health = {h.time: h for h in case.health}
    rows, pairs = [], []
    high: list[int] = []
    low: list[int] = []
    for index in range(case.bins):
        time = stamp(instant(case.start) + index * STEP)
        shifted = stamp(instant(time) + STEP * (settings.lag_hours // 3))
        o, h = obs.get(time), health.get(shifted)
        kp = None if o is None else o.kp
        drops = None if h is None else h.drops
        quality = "absent" if o is None else o.quality
        paired = kp is not None and drops is not None
        if paired:
            assert kp is not None and drops is not None
            pairs.append((kp, drops))
            (high if kp >= settings.threshold else low).append(drops)
        rows.append(
            {
                "index": index + 1,
                "time": time,
                "kp": kp,
                "quality": quality,
                "health_time": shifted,
                "drops": drops,
                "paired": paired,
                "event": None if kp is None else kp >= settings.threshold,
            }
        )
    r, reason = correlation(pairs)
    forecasts, scores = assess_forecasts(case, settings)
    result: dict[str, Any] = {
        "schema": 1,
        "name": case.name,
        "settings": asdict(settings),
        "input": case.document(),
        "provenance": provenance,
        "limitations": LIMITATIONS,
        "window": {
            "start": case.start,
            "end_exclusive": stamp(instant(case.start) + case.bins * STEP),
            "bin_hours": 3,
        },
        "totals": {
            "bins": case.bins,
            "available": sum(r["kp"] is not None for r in rows),
            "estimated": sum(r["quality"] == "estimated" for r in rows),
            "missing": sum(r["kp"] is None for r in rows),
            "events": sum(r["event"] is True for r in rows),
            "paired": len(pairs),
        },
        "association": {
            "r": None if r is None else round(r, 9),
            "status": reason,
            "lag_hours": settings.lag_hours,
            "high_count": len(high),
            "low_count": len(low),
            "high_mean_drops": round(math.fsum(high) / len(high), 9) if high else None,
            "low_mean_drops": round(math.fsum(low) / len(low), 9) if low else None,
            "warning": "Descriptive only; no causal conclusion, p-value, confidence interval or physical impact model.",
        },
        "rows": rows,
        "forecasts": forecasts,
        "scores": scores,
    }
    result["id"] = run_id(result)
    return result


def run_id(run: dict[str, Any]) -> str:
    """Hash all canonical report content except the identity field itself."""
    return hashlib.sha256(
        canonical({key: value for key, value in run.items() if key != "id"})
    ).hexdigest()


def build_run(settings: Settings | None = None) -> dict[str, Any]:
    """Analyze one finite bundled experiment with its verified or synthetic provenance."""
    settings = settings or Settings()
    case, provenance = fixture(settings.scenario)
    return analyze(case, settings, provenance)


def build_import(path: Path, settings: Settings) -> dict[str, Any]:
    """Analyze explicit local input without promoting its data to authenticated NOAA observations."""
    return analyze(
        load_case(path),
        settings,
        {
            "weather": "unverified local input",
            "health": "unverified local input",
            "forecasts": "unverified local input; issue times are supplied claims",
        },
    )
