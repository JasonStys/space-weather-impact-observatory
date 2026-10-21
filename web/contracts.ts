/** Browser evidence contracts and safe presentation by Jason Stys.
 * Functions: escape, display, plotNumber, isReport, parsePreferences, seriesSvg.
 * Variables/types/fields and exact lines: docs/CODE_INDEX.md. Missing values are never plotted as zero.
 */
export type Settings = {
  scenario: string;
  threshold: number;
  lag_hours: number;
  lead_hours: number;
};
export interface Bin {
  index: number;
  time: string;
  kp: number | null;
  quality: string;
  health_time: string;
  drops: number | null;
  paired: boolean;
  event: boolean | null;
}
export interface Forecast {
  target: string;
  issued: string | null;
  kp: number;
  lead_hours: number | null;
  status: string;
  actual: number | null;
  error: number | null;
}
export interface Report {
  schema: number;
  name: string;
  id: string;
  settings: Settings;
  provenance: Record<string, unknown>;
  window: { start: string; end_exclusive: string; bin_hours: number };
  totals: {
    bins: number;
    available: number;
    estimated: number;
    missing: number;
    events: number;
    paired: number;
  };
  association: {
    r: number | null;
    status: string;
    high_count: number;
    low_count: number;
    high_mean_drops: number | null;
    low_mean_drops: number | null;
    warning: string;
  };
  scores: {
    scored: number;
    excluded: number;
    mae: number | null;
    rmse: number | null;
    bias: number | null;
    statuses: Record<string, number>;
    confusion: Record<string, number>;
  };
  rows: Bin[];
  forecasts: Forecast[];
  limitations: string[];
}
export const scenarios: Record<string, string> = {
  "noaa-snapshot": "NOAA frozen snapshot",
  "synthetic-storm": "Synthetic storm and health",
  "missing-bins": "Missing and estimated bins",
  "forecast-revisions": "Forecast revisions and leakage",
  "flat-signal": "Flat signal / undefined correlation",
  "empty-window": "Empty observation window",
};
export const defaults: Settings = {
  scenario: "noaa-snapshot",
  threshold: 5,
  lag_hours: 0,
  lead_hours: 3,
};
export const choices = { threshold: [4, 5, 6], lag_hours: [0, 3, 6], lead_hours: [3, 12, 24] };

/** Escape every dynamic text/attribute fragment, including unexpected JSON primitive types. */
export function escape(value: unknown): string {
  return String(value).replace(
    /[&<>"']/g,
    (character) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character]!,
  );
}
/** Display only finite numeric values; null, malformed and unavailable metrics remain explicit. */
export function display(value: unknown, digits = 2): string {
  return typeof value === "number" && Number.isFinite(value)
    ? value.toFixed(digits)
    : "Not available";
}
/** Permit bounded numeric geometry only; never put a server string into an SVG coordinate. */
export function plotNumber(value: unknown, maximum: number): number | null {
  return typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= maximum
    ? value
    : null;
}
/** Reject unusable top-level evidence; rendering still escapes every dynamic field. */
export function isReport(value: unknown): value is Report {
  if (!value || typeof value !== "object") return false;
  const row = value as Record<string, unknown>;
  return (
    row.schema === 1 &&
    typeof row.id === "string" &&
    /^[a-f0-9]{64}$/.test(row.id) &&
    Array.isArray(row.rows) &&
    row.rows.length <= 256 &&
    row.rows.every((x) => !!x && typeof x === "object") &&
    Array.isArray(row.forecasts) &&
    row.forecasts.length <= 2048 &&
    row.forecasts.every((x) => !!x && typeof x === "object") &&
    ["totals", "scores", "association", "window", "provenance", "settings"].every(
      (key) => !!row[key] && typeof row[key] === "object",
    ) &&
    Array.isArray(row.limitations) &&
    row.limitations.every((x) => typeof x === "string")
  );
}
/** Finite preferences only; inherited names, booleans, extra fields and coercions are rejected. */
export function parsePreferences(raw: string | null): Settings | null {
  try {
    const value: unknown = JSON.parse(raw ?? "null");
    if (!value || typeof value !== "object" || Array.isArray(value)) return null;
    const row = value as Record<string, unknown>;
    if (Object.keys(row).sort().join(",") !== Object.keys(defaults).sort().join(",")) return null;
    if (typeof row.scenario !== "string" || !Object.hasOwn(scenarios, row.scenario)) return null;
    for (const key of ["threshold", "lag_hours", "lead_hours"] as const)
      if (typeof row[key] !== "number" || !choices[key].includes(row[key])) return null;
    return row as Settings;
  } catch {
    return null;
  }
}
/** Accessible bar geometry with independent unit scale; missing bins get crosses, not zero bars. */
export function seriesSvg(rows: Bin[], field: "kp" | "drops", threshold: number): string {
  const maximum =
    field === "kp" ? 9 : Math.max(1, ...rows.map((row) => plotNumber(row.drops, 10000) ?? 0));
  const width = 760,
    height = 158,
    left = 34,
    base = 125,
    plot = 680,
    step = plot / Math.max(1, rows.length);
  const bars = rows
    .map((row, index) => {
      const value = plotNumber(row[field], field === "kp" ? 9 : 10000);
      const x = left + index * step + 2;
      if (value === null) return `<path class="missing-mark" d="M ${x} 118 l 5 5 m -5 0 l 5 -5"/>`;
      const size = (value / maximum) * 100;
      return `<rect class="${field === "kp" ? (row.quality === "estimated" ? "estimated-bar" : "observed-bar") : "health-bar"}" x="${x}" y="${base - size}" width="${Math.max(1, step - 4)}" height="${Math.max(0.8, size)}"/>`;
    })
    .join("");
  const line =
    field === "kp"
      ? `<path class="threshold-line" d="M ${left} ${base - (threshold / 9) * 100} H 724"/><text x="728" y="${base - (threshold / 9) * 100 + 4}">cut ${threshold}</text>`
      : "";
  return `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${field === "kp" ? "Kp three-hour bins" : "Aligned synthetic or supplied dropped-frame counts"}. Missing values shown as crosses. Full values in the bin ledger."><text x="4" y="29">${maximum}</text><text x="14" y="129">0</text><path class="axis" d="M 32 20 V 126 H 724"/>${bars}${line}<text x="34" y="150">START / UTC</text><text x="670" y="150">END</text></svg>`;
}
