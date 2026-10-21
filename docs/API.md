# API and input/output contracts

By Jason Stys. Local read-only HTTP only. `GET /api/health` returns status/mode; `/api/catalog` returns finite scenarios, choices and defaults; `/api/run` returns full JSON; `/api/report` returns an attachment in `json`, `csv`, `html` or `input` format. The root and flat hashed `/assets/` files serve the built interface, not arbitrary source files.

`scenario` is one of the six catalog keys. Optional integer `threshold` is 4/5/6; `lag_hours` is 0/3/6; `lead_hours` is 3/12/24. `format` is report-only. Unknown, duplicate, blank/invalid or excessive fields fail with 400. Request targets >1024 characters get 414. Exact Host `127.0.0.1:port`, optional same Origin and non-cross-site Fetch Metadata are required; failures get 403. No CORS is emitted. Unknown/path-escape routes get 404; state-changing methods and HEAD get 405. Local resource failures return generic 500 without paths. There is no remote fetch, upload, account, shell, browser filesystem or HTTP history API.

Example: `/api/run?scenario=forecast-revisions&threshold=5&lag_hours=0&lead_hours=12`. Report download: same options at `/api/report` with `&format=json`. Filenames are fixed `space-weather-evidence.json`, `space-weather-bins.csv`, `space-weather-evidence.html` and `space-weather-input.json`; no user text is reflected in headers.

## CLI import schema 1

Root exact keys: `schema` (integer 1, not true), `name` (1–48 lowercase alphanumeric/hyphen characters, starts alphanumeric), `start` (UTC grid string), `bins` (integer 1..256), and lists `observations`, `health`, `forecasts`. See the complete editable [synthetic example](../examples/synthetic-storm.json).

| List         | Exact row keys and ranges                                                                                              | Maximum |
| ------------ | ---------------------------------------------------------------------------------------------------------------------- | ------- |
| observations | `time`: grid-aligned UTC in window; `kp`: finite 0..9 or null; `quality`: observed/estimated/missing, null iff missing | 256     |
| health       | `time`: grid-aligned UTC in window; `drops`: integer 0..10000 or null                                                  | 256     |
| forecasts    | `target`: grid-aligned UTC; `issued`: explicit UTC or null; `kp`: finite 0..9                                          | 2048    |

Timestamps are exactly `YYYY-MM-DDTHH:MM:SSZ`, years 2000..2099. Issue timestamps need not align to bins. Known late issues are retained and excluded by analysis, not rewritten. No duplicate JSON keys, duplicate time bins or duplicate target/issue revisions. Records normalize to canonical time/revision order. No CSV/PDF/archive deserialization, URL fetch or executable configuration. CLI source is capped at 512 KiB plus one sentinel; malformed UTF-8, excessive nesting and invalid JSON produce controlled errors. `--scenario` selects only bundled inputs; with `--input`, the file is used and its case name is shown, while other numeric settings still apply. The selector field remains in the settings record but grants no provenance authority.

JSON report schema includes `input`, `provenance`, `settings`, `window`, `totals`, `rows`, `forecasts`, `scores`, `association`, `limitations` and full `id`. Output permits null unavailable values, never NaN/infinity. CSV is intentionally the aligned-bin table only; full forecast revisions/provenance/metrics are in JSON/HTML, not lost silently from those formats. CSV timestamps/qualities are validated fixed formats; no imported free-form text is emitted as a formula cell. HTML is a self-contained escaped `<pre>` report without scripts, styles, forms or remote resources. Input JSON contains no trusted source credentials or assertions. History is explicit local CLI-only and not a file synchronization system.
