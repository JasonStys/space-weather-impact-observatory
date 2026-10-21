# Model, metrics and scientific limits

By Jason Stys. This is an evidence-analysis tool, not a space-weather impact prediction model.

## Bins and missingness

The analysis grid starts at explicit `Z` UTC and has 1–256 consecutive three-hour bins. Start and observation/health timestamps must be three-hour aligned, seconds/minutes zero, years 2000–2099. End is exclusive. No naive/offset timestamp or leap-second import is silently reinterpreted. Observation/health rows must fall in the grid; forecast targets may lie outside it and are then unscoreable without a matching observed row. Duplicate observation/health timestamps and duplicate (target, issued) revisions are rejected. Omitted observation, explicit missing observation and missing health remain visible; neither interpolation nor zero substitution occurs.

Kp values are finite 0..9. Fractional inputs are allowed; the validator does not claim definitive Kp quantization or convert Kp to a physical linear energy scale. Counted health values are integers 0..10000. Source quality is `observed`, `estimated` or `missing`; the last requires null Kp. Both available observed and estimated targets can be scored; quality/provenance stays in the report. NOAA's rapid product is labeled estimated rather than definitive GFZ Kp even where the forecast feed calls rows observed. [NOAA product description](https://www.swpc.noaa.gov/products/planetary-k-index).

Event threshold 4/5/6 is an analytical sensitivity choice, **not** a NOAA G-scale classification, radiation threshold or damage criterion. At threshold c, an available observation is an event iff Kp >= c. Missing bins have null event status and do not count as non-events. No storm duration, physical dose or local exposure is inferred.

## Forecast verification

Each forecast has target-bin UTC, separately supplied issue UTC or null, and predicted Kp. Exclusion precedence:

1. Null issue: `unknown-issuance`.
2. Issue at/after target: `not-before-target`.
3. Positive lead smaller than 3/12/24 hours: `insufficient-lead`.
4. No matching nonmissing target observation: `missing-observation`.
5. Among remaining revisions per target, latest issue wins; earlier eligible revisions are `superseded`.
6. Exactly one revision per scoreable target is `scored`.

The rule prevents choosing a forecast retrospectively because it happened to be closest. It does not authenticate supplied issue timestamps, reconstruct data publication latency, or validate a real forecasting service. Original NOAA feed rows have no issue field; retrieval time is never substituted. All 17 retained predicted records in the frozen feed therefore remain excluded. Observed/estimated entries in that mixed feed are not forecast candidates. A snapshot of the latest feed cannot provide historical forecast skill by itself.

For selected errors e = forecast − target Kp: MAE = mean(abs(e)), RMSE = sqrt(mean(e²)), bias = mean(e). All are in Kp **index units**, not physical units. Metrics are null with zero scored targets. Threshold confusion counts TP/FP/FN/TN use the same selected targets and chosen analytical threshold. Excluded records are never counted as correct negatives. No persistence skill score, calibrated probability or forecast-accuracy claim is computed. Display rounding is separate from selection; error/summary JSON is rounded to nine decimals for portable deterministic contracts.

## Health association

A selected nonnegative lag of 0/3/6 hours pairs weather(t) with health(t+lag). Only pairs with both values contribute; positive-lag tail health outside the grid is missing. Pearson r uses centered sums, with null + `insufficient-pairs` for <3 pairs or null + `constant-series` for zero variance. Non-null r is bounded against floating-point overshoot and labeled descriptive only. An independent pairwise-difference identity validates the arithmetic in property tests, rather than repeating the centered production algorithm.

High/low threshold group means are descriptive means and counts of paired health values, null for an empty group. They are not inferred treatment effects. Temporal dependence, confounding, multiple lag/threshold exploration, quasi-logarithmic Kp, small samples and selection/missingness can invalidate naive interpretation. The application offers no p-value, confidence interval, causal model, statistical significance, population generalization or automatic best-lag selection. Synthetic correlation was deliberately invented; it is not a discovered spacecraft relationship. Real research would require authorized independently sourced mission data, sensor definitions/exposure, publication timing, a preregistered analysis, suitable controls and domain review.

## Evidence versus assurance

All reports include full inputs, provenance, settings, exclusions and warnings. The canonical SHA-256 omits only its own id and excludes wallclock/runtime/path metadata. It identifies bytes/content under this contract; anyone able to modify data can compute another SHA. It is not a signature, authenticity proof, physical validation or flight qualification. NOAA data checksums detect accidental file drift, not a malicious party able to replace the metadata too. [Validation evidence](VALIDATION.md).
