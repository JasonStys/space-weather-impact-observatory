# Validation plan and observed evidence

By Jason Stys. Observed locally 2026-10-20 PDT / 2026-10-21 UTC on Windows x64, CPython 3.14.6 and Node 24.18.1. Software correctness tests do not establish a physical impact model, mission safety or real forecast skill.

| Gate                   | Observed local result                                                                                                                               |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Python suite           | 261 passed; 99.66% branch-inclusive Python runtime coverage, minimum 90%                                                                            |
| Finite settings grid   | All 162 cases (six sources × three thresholds × three lags × three leads), deterministic hashes/totals and non-leaking one-per-target selection     |
| Independent arithmetic | Hand-derived synthetic errors/confusion/revision case; 100 property examples compare centered r with independent pairwise-difference identity       |
| Input properties       | 100 order-normalization examples plus timestamp, exact-key, duplicate, numeric, envelope, Unicode/nesting/range rejection cases                     |
| TypeScript suite       | 12 passed: escaping, null metrics, bounded geometry, missing plots, preference coercion/prototype/extra-field rejection and response bounds         |
| Browser acceptance     | 24 passed: eight each Chromium/Firefox/WebKit against real handler/resources/build; explicit substitutions only for failure/hostile-response checks |
| Advisory scans         | npm zero reported vulnerabilities; pip-audit no known vulnerabilities at check time                                                                 |
| Static gates           | Ruff check/format, strict mypy and production TypeScript build passed                                                                               |

Browser checks cover honest NOAA/no-health/no-score state, synthetic analysis, missing-bin filters, exact positive-lag inspector, forecast revisions/lead exclusions, four actual download payloads, opt-in preference persistence/removal, failure/stale-output hiding/retry, hostile text escaping, 390px page width, keyboard chart region and axe WCAG A/AA checks. Automated accessibility checks do not prove compatibility with all assistive technology.

## Traceability and test limits

The native-data contract verifies two frozen NOAA byte hashes and known endpoint values. A tampered raw response stops use. JSON tests reject duplicate keys/records and retain unknown/late issue times as explicit excluded forecasts. Report tests cover actual HTTP/CLI/SQL, fixed headers, no mutation, origin/rebinding, path/symlink confinement, duplicate/excessive fields and generic resource failures. History tests cover hash mismatch, parameterization, idempotence, immutable updates and full-capacity refusal. Exports preserve complete JSON/HTML context; CSV scope is documented.

Runtime timing is descriptive, not a hard-real-time gate. A local 20-run synthetic revision test measured approximately 3.56 ms median and 65,325 bytes peak traced Python allocation, **with tracemalloc overhead**; excludes browser/OS/native allocator memory and is not an RSS benchmark. `python -m tools.benchmark` prints each machine's observation and checks six exact default-case contracts in [reports/benchmark.json](reports/benchmark.json). Timing values are excluded from content hashes. Algorithmic cost/limits are documented in [ARCHITECTURE](ARCHITECTURE.md).

Development findings and fixes: tuples in the initial portable-input representation became explicit JSON lists so serialized input round trips obey the actual schema; SQLite transaction contexts gained an explicit closer to eliminate resource warnings on every return path; a missing-bin test's mistaken index was corrected against the actual timestamps. A pytest collection iterator was materialized without disabling strict warning handling. Snapshot formatting was detected by checksums; raw responses were re-fetched/frozen with reviewed current provenance and excluded from formatting/text conversion before deterministic contracts were established. An exact-label browser test selector was corrected to the actual control identifier; no axe rules or security gates were disabled. Debug/code-review guidance informed reproduce/isolate/fix/regression rather than suppressing failures.

No formal scientific/physical validation, live mission connection, independent real forecast backtest, significance/causality, radiation model, penetration testing/certification, signed app or universal platform guarantee is claimed. Tests are bounded campaigns, not proof every possible defect is absent. CodeQL/advisory conclusions and native packaging are reported only after actual runs.

## Remote evidence and storage

The actual local Windows frozen bundle passed NOAA resource/hash verification, JSON export, production HTML/assets, health and synthetic forecast API smoke. Additional CLI input-export/import/history and two-writer last-slot capacity regressions passed; the final local suite is 261 tests with 99.66% coverage. Export persistence and history are separate files, not a cross-file transaction. Native Linux/macOS execution is still required from CI before publishing downloads.

Publication requires all four OS/Python tests, Linux three-engine acceptance, three frozen-app builds/smokes and both CodeQL analyses on the exact final source. Inspect open alerts separately. Final [release notes](https://github.com/JasonStys/space-weather-impact-observatory/releases) link the exact SHA, completed workflows, downloaded ZIP digests and Windows bundle checks, rather than claiming this document's future commit has already passed.

Actions storage was checked before implementation using current inventory and the live billing meter; account-level usage was reported privately. Existing runs/artifacts/caches are untouched. This repository's workflows upload no Actions artifacts/caches; release assets are distinct.
