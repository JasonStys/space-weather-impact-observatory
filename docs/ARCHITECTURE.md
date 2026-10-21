# Architecture and decisions

By Jason Stys. Design/testing guidance shaped explicit trust boundaries and independent arithmetic checks.

```text
hash-verified original NOAA snapshots ─┐
invented finite case fixtures ─────────┼─ strict immutable Case ─ UTC joins / issue gates
bounded CLI-only JSON input ──────────┘                         │
                  deterministic full-context report + SHA ─────┤
                         │                    │                │
                 read-only loopback      explicit exports   optional SQLite
                         │                                  CLI history only
                TypeScript / SVG / HTML
```

Python's standard library is sufficient for this bounded statistics/validation workload. Additional native/ML dependencies would increase distribution and validation cost without a measured need. TypeScript provides finite UI contracts and numeric-only SVG geometry; SQL enforces local immutable evidence. There are no cloud accounts, workers, data brokers, external fonts, analytics or remote AI calls.

Imports are max 512 KiB plus one sentinel byte, max 256 bins and 2048 revisions. Validation normalizes order and rejects ambiguity before computation. NOAA snapshots are dedicated packaged resources with byte checksums; their retrieval date is not issuance. App startup never refreshes them. Missing files/checksum disagreement stops that experiment rather than falling back to invented observations.

For B bins, O observations, H health records and F forecasts: parsing/canonical order normalization is O(O log O + H log H + F log F); alignment/metrics and revision eligibility are O(B+O+H+F) after normalization. Dictionaries prevent repeated full scans. Output hashing/serialization is O(output bytes), and memory is O(B+O+H+F+output bytes). No covariance matrices, optimization loop or ML training is involved. Datetime parsing has bounded constant-size inputs. ASCII identifier and timestamp contracts prevent arbitrary CSV cells.

Per-target latest eligible forecast selection is independent of truth/error. Null statistics and all exclusion rows are retained. Kp and health charts have separate scales/units, avoiding a visually arbitrary dual-axis overlay. Positive lag and exact health timestamp are printed in both UI and exports. Filtering changes display only, not the evidence hash or full-window counts.

History uses content-hash verification, SQL parameters, `BEGIN IMMEDIATE` for serialized capacity/idempotence decisions, and no-update/no-delete triggers. An explicit connection closer releases resources on success, early return and exceptions. Export and database are separate files, not a cross-file atomic transaction: a later export I/O failure can leave a valid history record. History is not encrypted/authenticated backup, and local modification by an OS user is outside the integrity guarantee.

The server binds only IPv4 loopback, validates exact Host and same-origin headers, confines static paths/symlinks and accepts finite options. Browser imports/accounts/history are absent by design. This stdlib threaded server is not a publicly exposed production service: no public TLS/authentication, fair-use rate quota or distributed scheduling claim is made. Revisit process limits, data licensing, publication latency and authenticated deployment before expanding scope; do not just bind to 0.0.0.0.

The shallow layout separates schema, analysis, export and transport. Shared input/output contracts are versioned at schema 1; no database migration or automatic updater is installed. Release changes require fresh exact-source CI, downloaded-asset checksum review and native executable smoke. [Release procedure](RELEASE.md).
