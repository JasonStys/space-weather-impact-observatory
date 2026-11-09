# Compare forecast lead and coverage

The comparison panel evaluates **minimum lead cutoffs** of 3, 12 and 24 hours over the whole target window and its earlier/later halves. The target UTC midpoint is half-open: the boundary belongs to later, and an odd final bin belongs to later. These fixed windows are declared before examining errors; the application does not search for a favorable window or lag.

For each cutoff, only the latest issuance at or before target-minus-cutoff is scored. Exactly one forecast per target can contribute, regardless of revisions. Rows across cutoffs overlap and must not be pooled as independent forecasts. A higher-lead cutoff can select an older revision with a different error; the system never selects by whichever forecast looks best against truth.

The panel shows available observations/all bins, issuance-eligible targets, scored targets/observations and scored targets/all bins. The JSON report includes both coverage ratios, missing observation count, forecast-target count, full error/confusion summaries, status counts and exact selected target/issue/error records. Unknown issuance and missing observations remain explicit exclusions. Zero denominators and absent errors are null, never perfect scores or healthy zeros. A one-bin case has an empty earlier half.

The existing selected-lead forecast ledger and bin filter retain their original meanings. Full JSON/HTML, strict CLI imports and local immutable history include all nine comparison rows in the content hash. Observation quality/provenance remains visible; the frozen NOAA snapshot has unknown forecast issuance and establishes no historical forecast skill. These are descriptive dataset comparisons, not statistical significance, causal impact, current conditions or mission guidance.
