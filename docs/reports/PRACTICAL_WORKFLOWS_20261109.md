# Lead/window comparison validation — 2026-11-09

Local Windows / Python3.14.6 verification passed: 264 Python tests, 99.66% combined statement/branch coverage and 100% for the engine. Hand-authored revisions prove a newer eligible forecast can have worse error and still be selected. Manual errors [1,-3], [1,-1] and [1] independently establish MAE/RMSE/bias at the three lead cutoffs. Tests verify exact lead equality, missing truth, unknown issuance, half-open target boundaries, disjoint half-window counts and a one-bin case's empty earlier half with undefined denominators.

Twelve TypeScript unit tests, strict production build and all 27 Chromium/Firefox/WebKit browser tests passed. A real service-backed journey checks nine comparison rows, observed/scored coverage, NOAA unknown-issuance exclusions and empty-window results. Existing accessibility, failed requests, safe text rendering, provenance and actual downloads remain covered. Ruff lint/format, mypy, generated source indexes and dependency audits pass, with no known Python vulnerabilities and zero npm vulnerabilities.

All six old totals, selected-lead forecast scores and association golden summaries are independently compared unchanged before refreshing content hashes for the new comparison evidence. Deterministic benchmark contracts pass. No NOAA resource bytes or frozen provenance were changed.

Cutoffs overlap and are not independent samples. Differences between fixed halves are descriptive, not a significance test or generalized forecast-skill claim. Unknown issuance never creates historical skill; the app has no current conditions, causal impact predictions or mission guidance. The parent handles review, publishing, remote Actions and cross-platform portable builds; this child triggered no remote workflows.
