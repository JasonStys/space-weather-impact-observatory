/** Offline evidence interface by Jason Stys.
 * Functions: controls, load, render, bind, inspect; variables: settings, report, request, selected.
 * Dynamic content is escaped and geometry is numeric-only. Exact lines: docs/CODE_INDEX.md.
 */
import {
  choices,
  defaults,
  display,
  escape,
  isReport,
  parsePreferences,
  scenarios,
  seriesSvg,
  type Report,
  type Settings,
} from "./contracts";
import "./style.css";
const app = document.querySelector<HTMLDivElement>("#app")!;
const storageKey = "space-weather-preferences-v1";
let settings = { ...defaults };
let remember = false;
try {
  const saved = parsePreferences(localStorage.getItem(storageKey));
  if (saved) {
    settings = saved;
    remember = true;
  }
} catch {
  /* Storage is optional; analysis never depends on it. */
}
let report: Report | null = null;
let selected = 0;
let request: AbortController | null = null;
let filter = "all";
app.innerHTML = `<header class="top"><a class="brand" href="#workspace"><span class="sun" aria-hidden="true">✳</span> FIELDNOTES <span>/ SPACE WEATHER</span></a><nav aria-label="Project"><a href="#guide">How it works</a><a href="https://github.com/JasonStys/space-weather-impact-observatory" rel="noreferrer">Source ↗</a><a href="https://github.com/JasonStys" rel="noreferrer">Jason Stys ↗</a></nav></header><main id="workspace"><section class="hero"><div><p class="eyebrow">01 / SPACE ENVIRONMENT · OFFLINE ANALYSIS</p><h1>Signals. Evidence.<br><em>Context.</em></h1><p class="intro">Explore planetary Kp, inspect forecast eligibility, and ask better questions of mission-health data.</p></div><aside class="scope"><span class="tag">RESEARCH WORKBENCH</span><h2>Association ≠ causation.</h2><p>No live conditions. No operational decisions. NOAA estimates and invented health records are labeled separately.</p><p class="mono">UTC ONLY / 3-HOUR BINS</p></aside></section><section class="control-panel" aria-label="Experiment settings"><div id="controls"></div><label class="remember"><input id="remember" type="checkbox">Remember these settings on this device</label></section><p id="status" role="status" aria-live="polite">Loading evidence…</p><section id="evidence" hidden></section><section id="guide" class="guide"><p class="eyebrow">METHOD / READ BEFORE INTERPRETING</p><h2>The boundary is part of the result.</h2><div class="guide-grid"><div><h3>01 · Observations</h3><p>The frozen NOAA feed contains estimated planetary Kp—not definitive local exposure. Missing data stays missing. The snapshot is not live or automatically refreshed.</p></div><div><h3>02 · Forecasts</h3><p>Issue time must precede the target by the selected minimum lead. Only the latest eligible revision per target is scored. Unknown issuance is excluded, never inferred from download time.</p></div><div><h3>03 · Health association</h3><p>Positive lag pairs weather at t with health at t + lag. Synthetic health illustrates analysis, not real effects. Pearson r requires three pairs and varying series; no causal claim or significance test is made.</p></div></div><p><a href="https://github.com/JasonStys/space-weather-impact-observatory/blob/main/docs/USER_GUIDE.md" rel="noreferrer">User guide & limitations ↗</a> · <a href="https://github.com/JasonStys/space-weather-impact-observatory/issues" rel="noreferrer">Help / report an issue ↗</a></p></section></main><footer>Designed and engineered by <a href="https://github.com/JasonStys" rel="noreferrer">Jason Stys</a><span>EDUCATIONAL · INDEPENDENT · NO AGENCY ENDORSEMENT</span></footer>`;

/** Build finite controls from reviewed client constants, not remote HTML. */
function controls(): void {
  document.querySelector("#controls")!.innerHTML =
    `<label>Experiment<select id="scenario">${Object.entries(scenarios)
      .map(
        ([key, label]) =>
          `<option value="${key}" ${key === settings.scenario ? "selected" : ""}>${label}</option>`,
      )
      .join(
        "",
      )}</select></label>${(["threshold", "lag_hours", "lead_hours"] as const).map((key) => `<label>${{ threshold: "Kp event threshold", lag_hours: "Health lag / hours", lead_hours: "Minimum forecast lead / hours" }[key]}<select id="${key}">${choices[key].map((value) => `<option value="${value}" ${value === settings[key] ? "selected" : ""}>${value}</option>`).join("")}</select></label>`).join("")}<button id="refresh" class="primary">Recompute evidence ↗</button>`;
  for (const key of ["scenario", "threshold", "lag_hours", "lead_hours"] as const) {
    document.querySelector<HTMLSelectElement>(`#${key}`)!.addEventListener("change", (event) => {
      const value = (event.target as HTMLSelectElement).value;
      settings = { ...settings, [key]: key === "scenario" ? value : Number(value) };
      void load();
    });
  }
  document.querySelector("#refresh")!.addEventListener("click", () => void load());
}

/** Cancel superseded requests, hide stale exports, persist finite preferences only when opted in. */
async function load(): Promise<void> {
  request?.abort();
  const current = new AbortController();
  request = current;
  const status = document.querySelector<HTMLElement>("#status")!;
  const evidence = document.querySelector<HTMLElement>("#evidence")!;
  evidence.hidden = true;
  status.textContent = "Loading evidence…";
  try {
    if (remember)
      try {
        localStorage.setItem(storageKey, JSON.stringify(settings));
      } catch {
        /* Optional preference storage only. */
      }
    const query = new URLSearchParams(Object.entries(settings).map(([k, v]) => [k, String(v)]));
    const response = await fetch(`/api/run?${query}`, {
      signal: current.signal,
      cache: "no-store",
    });
    if (!response.ok) throw new Error("Local service unavailable");
    const value: unknown = await response.json();
    if (!isReport(value)) throw new Error("Invalid evidence response");
    if (request !== current) return;
    report = value;
    selected = 0;
    filter = "all";
    render();
    evidence.hidden = false;
    status.textContent =
      "Evidence ready. Inspect provenance and exclusions before interpreting results.";
  } catch (error) {
    if (current.signal.aborted || request !== current) return;
    report = null;
    status.innerHTML = `Could not load evidence. <button id="retry">Try again</button>`;
    document.querySelector("#retry")!.addEventListener("click", () => void load());
  }
}

/** Render complete evidence summaries, independent chart scales and inspectable source rows. */
function render(): void {
  if (!report) return;
  const r = report;
  const query = new URLSearchParams(Object.entries(settings).map(([k, v]) => [k, String(v)]));
  const metrics = [
    ["AVAILABLE BINS", `${r.totals.available} / ${r.totals.bins}`],
    ["MISSING BINS", r.totals.missing],
    ["EVENT BINS", r.totals.events],
    ["SCORED TARGETS", r.scores.scored],
  ];
  document.querySelector("#evidence")!.innerHTML =
    `<div class="metrics">${metrics.map(([label, value]) => `<article><p>${label}</p><strong>${escape(value)}</strong></article>`).join("")}</div><section class="panel"><div class="section-head"><div><p class="eyebrow">02 / ALIGNED OBSERVATIONS</p><h2>See the signal. Keep the gaps.</h2></div><span class="tag">${escape(r.window.bin_hours)}H · UTC</span></div><p class="provenance"><b>Weather:</b> ${escape(r.provenance.weather)}<br><b>Health:</b> ${escape(r.provenance.health)}</p><div class="legend"><span class="legend-solid">Observed fixture</span><span class="legend-outline">Estimated NOAA / fixture</span><span>× Missing</span></div><div class="chart-region" tabindex="0" role="region" aria-label="Kp chart; full numeric values in bin ledger">${seriesSvg(r.rows, "kp", settings.threshold)}</div><p class="chart-caption">Kp index (0–9) · ${escape(r.window.start)} → ${escape(r.window.end_exclusive)} exclusive</p><h3>Health alignment <span class="subtle">/ dropped-frame count · lag +${escape(settings.lag_hours)}h</span></h3><div class="chart-region" tabindex="0" role="region" aria-label="Health chart; full numeric values in bin ledger">${seriesSvg(r.rows, "drops", settings.threshold)}</div><div class="association"><div><span class="eyebrow">DESCRIPTIVE PEARSON R</span><strong>${display(r.association.r, 3)}</strong><span>${escape(r.association.status)} · ${escape(r.totals.paired)} pairs</span></div><p>${escape(r.association.warning)}<br>Threshold groups: ${escape(r.association.high_count)} high / ${escape(r.association.low_count)} low. Mean drops: ${display(r.association.high_mean_drops)} / ${display(r.association.low_mean_drops)}.</p></div></section><section class="panel"><div class="section-head"><div><p class="eyebrow">03 / FORECAST VERIFICATION</p><h2>Know what can be scored.</h2></div><span class="tag">ISSUANCE GATE ON</span></div><p>${escape(r.provenance.forecasts)}</p><div class="score-grid"><div><span>MAE / Kp index units</span><strong>${display(r.scores.mae, 3)}</strong></div><div><span>RMSE / Kp index units</span><strong>${display(r.scores.rmse, 3)}</strong></div><div><span>Bias / predicted − observed</span><strong>${display(r.scores.bias, 3)}</strong></div><div><span>Excluded records</span><strong>${escape(r.scores.excluded)}</strong></div></div><p>${
      Object.entries(r.scores.statuses)
        .map(([key, value]) => `<span class="status-chip">${escape(key)} · ${escape(value)}</span>`)
        .join(" ") || "No forecast records supplied."
    }</p><details><summary>Inspect forecast revisions and exclusion reasons</summary><div tabindex="0" role="region" aria-label="Forecast ledger" class="table-scroll"><table><thead><tr><th>Target UTC</th><th>Issued UTC</th><th>Kp</th><th>Lead h</th><th>Status</th><th>Error</th></tr></thead><tbody>${r.forecasts.map((f) => `<tr><td>${escape(f.target)}</td><td>${f.issued === null ? "Unknown" : escape(f.issued)}</td><td>${display(f.kp)}</td><td>${display(f.lead_hours)}</td><td>${escape(f.status)}</td><td>${display(f.error)}</td></tr>`).join("")}</tbody></table></div></details></section><section class="panel"><div class="section-head"><div><p class="eyebrow">04 / BIN LEDGER</p><h2>Every bin has a story.</h2></div><label>Show bins<select id="filter"><option value="all">All bins</option><option value="missing">Missing weather</option><option value="events">Threshold events</option><option value="paired">Paired health</option></select></label></div><p>Filtering does not change full-window metrics or downloads.</p><div id="ledger"></div><div id="inspector" class="inspector" aria-live="polite"></div></section><section class="panel"><div class="section-head"><div><p class="eyebrow">05 / REPRODUCIBLE EVIDENCE</p><h2>Take the context with you.</h2></div></div><div class="downloads">${["json", "csv", "html", "input"].map((format) => `<a href="/api/report?${query}&format=${format}" download>${format === "input" ? "Input JSON" : format.toUpperCase() + " report"} ↓</a>`).join("")}</div><p class="digest">CONTENT SHA-256<br>${escape(r.id)}</p><details><summary>Provenance, source snapshot and limitations</summary><pre>${escape(JSON.stringify(r.provenance, null, 2))}</pre><ul>${r.limitations.map((text) => `<li>${escape(text)}</li>`).join("")}</ul></details></section>`;
  document.querySelector("#filter")!.addEventListener("change", (event) => {
    filter = (event.target as HTMLSelectElement).value;
    bind();
  });
  bind();
}

/** Filter only the displayed ledger, preserving all data and selection context. */
function bind(): void {
  if (!report) return;
  const rows = report.rows.filter((row) =>
    filter === "missing"
      ? row.kp === null
      : filter === "events"
        ? row.event === true
        : filter === "paired"
          ? row.paired
          : true,
  );
  document.querySelector("#ledger")!.innerHTML =
    `<div class="table-scroll" tabindex="0" role="region" aria-label="Aligned bin ledger"><table><thead><tr><th>Inspect</th><th>Weather UTC</th><th>Kp</th><th>Quality</th><th>Health UTC</th><th>Drops</th><th>Paired</th></tr></thead><tbody>${rows.map((row) => `<tr><td><button class="inspect-bin" data-bin="${escape(row.index - 1)}" aria-label="Inspect bin ${escape(row.index)}">${escape(row.index)} ↗</button></td><td>${escape(row.time)}</td><td>${display(row.kp)}</td><td>${escape(row.quality)}</td><td>${escape(row.health_time)}</td><td>${display(row.drops, 0)}</td><td>${row.paired ? "Yes" : "No"}</td></tr>`).join("")}</tbody></table>${rows.length ? "" : "<p>No bins match this filter.</p>"}</div>`;
  for (const button of document.querySelectorAll<HTMLButtonElement>(".inspect-bin"))
    button.addEventListener("click", () => {
      selected = Number(button.dataset.bin);
      inspect();
    });
  inspect();
}

/** Show exact selected weather/health times so positive-lag semantics cannot be hidden by a plot. */
function inspect(): void {
  const row = report?.rows[selected];
  if (!row) return;
  document.querySelector("#inspector")!.innerHTML =
    `<p class="eyebrow">BIN ${escape(row.index)} / CONTEXT</p><h3>${escape(row.time)}</h3><div class="inspect-grid"><p>Weather Kp<strong>${display(row.kp)}</strong></p><p>Observation quality<strong>${escape(row.quality)}</strong></p><p>Aligned health UTC<strong>${escape(row.health_time)}</strong></p><p>Dropped frames<strong>${display(row.drops, 0)}</strong></p></div><p>${row.paired ? "Included in descriptive paired analysis." : "Not paired: a weather or aligned health value is unavailable."} No physical effect or causal attribution is inferred.</p>`;
}

controls();
document.querySelector<HTMLInputElement>("#remember")!.checked = remember;
document.querySelector("#remember")!.addEventListener("change", (event) => {
  remember = (event.target as HTMLInputElement).checked;
  try {
    if (remember) localStorage.setItem(storageKey, JSON.stringify(settings));
    else localStorage.removeItem(storageKey);
  } catch {
    /* No data is sent elsewhere when storage is unavailable. */
  }
});
void load();
