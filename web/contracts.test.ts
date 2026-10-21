/** Presentation/geometry/preference contract tests by Jason Stys. Definitions: docs/CODE_INDEX.md. */
import { describe, expect, test } from "vitest";
import {
  defaults,
  display,
  escape,
  isReport,
  parsePreferences,
  plotNumber,
  seriesSvg,
  type Bin,
} from "./contracts";
describe("inert text and numeric geometry", () => {
  test("escapes all markup delimiters", () =>
    expect(escape("<img x=\"1\" onerror='x'>&")).toBe(
      "&lt;img x=&quot;1&quot; onerror=&#39;x&#39;&gt;&amp;",
    ));
  test("does not coerce unavailable metrics to zero", () => {
    expect(display(null)).toBe("Not available");
    expect(display("3")).toBe("Not available");
    expect(display(1, 3)).toBe("1.000");
  });
  test("bounds geometry without string coercion", () => {
    for (const value of [null, "4", -1, 10, Infinity, NaN]) expect(plotNumber(value, 9)).toBeNull();
    expect(plotNumber(0, 9)).toBe(0);
  });
  test("labels missing Kp instead of drawing a zero-valued observation", () => {
    const rows = [{ kp: null, drops: null, quality: "absent" }] as Bin[];
    const svg = seriesSvg(rows, "kp", 5);
    expect(svg).toContain("missing-mark");
    expect(svg).not.toContain('class="observed-bar"');
    expect(svg).toContain("Full values in the bin ledger");
  });
  test("health has a separate bounded unit scale", () => {
    const svg = seriesSvg([{ kp: 9, drops: 20, quality: "observed" }] as Bin[], "drops", 5);
    expect(svg).toContain(">20</text>");
    expect(svg).not.toContain("threshold-line");
  });
  test("empty chart remains finite", () =>
    expect(seriesSvg([], "kp", 5)).not.toMatch(/NaN|Infinity/));
});
describe("finite opt-in preferences", () => {
  test("valid settings survive round trip", () =>
    expect(parsePreferences(JSON.stringify(defaults))).toEqual(defaults));
  test("unknown and inherited scenarios fail", () => {
    for (const scenario of ["constructor", "__proto__", "unknown"])
      expect(parsePreferences(JSON.stringify({ ...defaults, scenario }))).toBeNull();
  });
  test("coercions extras malformed and arrays fail", () => {
    for (const raw of [
      null,
      "{",
      "[]",
      JSON.stringify({ ...defaults, threshold: "5" }),
      JSON.stringify({ ...defaults, lead_hours: true }),
      JSON.stringify({ ...defaults, extra: 1 }),
    ])
      expect(parsePreferences(raw)).toBeNull();
  });
  test("unsupported numeric options fail", () =>
    expect(parsePreferences(JSON.stringify({ ...defaults, lag_hours: 4 }))).toBeNull());
});
describe("response envelope", () => {
  test("invalid top-level envelopes fail", () => {
    for (const value of [null, [], {}, { schema: 1, id: "bad" }])
      expect(isReport(value)).toBe(false);
  });
  test("bounded primitive constraints enforced", () => {
    const sample = {
      schema: 1,
      id: "a".repeat(64),
      rows: [],
      forecasts: [],
      totals: {},
      scores: {},
      association: {},
      window: {},
      provenance: {},
      settings: {},
      limitations: [],
    };
    expect(isReport(sample)).toBe(true);
    expect(isReport({ ...sample, rows: [null] })).toBe(false);
    expect(isReport({ ...sample, forecasts: Array(2049).fill({}) })).toBe(false);
  });
});
