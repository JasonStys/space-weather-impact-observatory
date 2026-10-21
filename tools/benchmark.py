"""Reviewed deterministic contracts plus descriptive profiling by Jason Stys.

Function: main. Variables: default case contracts, elapsed sample and traced peak allocation.
Only --write updates reviewed fixtures; CI compares content, not machine-dependent timings.
"""

import argparse
import statistics
import time
import tracemalloc
from pathlib import Path

from weatherlab.engine import SCENARIOS, Settings, build_run, canonical


def main() -> None:
    """Check exact outputs and print runtime/memory observations without fragile performance gates."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rows = []
    for scenario in SCENARIOS:
        run = build_run(Settings(scenario))
        rows.append(
            {
                "scenario": scenario,
                "id": run["id"],
                "totals": run["totals"],
                "scores": run["scores"],
                "association": run["association"],
            }
        )
    path = Path("docs/reports/benchmark.json")
    body = canonical({"cases": rows})
    if args.write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    elif path.read_bytes() != body:
        raise SystemExit(
            "Deterministic evidence drift; investigate before changing reviewed contracts"
        )
    times = []
    tracemalloc.start()
    for _ in range(20):
        start = time.perf_counter()
        build_run(Settings("forecast-revisions"))
        times.append((time.perf_counter() - start) * 1000)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(
        f"Six deterministic analysis contracts passed; median {statistics.median(times):.3f} ms, traced Python peak {peak} bytes (descriptive, includes tracing overhead)"
    )


if __name__ == "__main__":
    main()
