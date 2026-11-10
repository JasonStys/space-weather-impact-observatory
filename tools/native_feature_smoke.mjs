/**
 * Frozen forecast lead/window acceptance by Jason Stys.
 * Function: runNativeJourney callback; variables: selected errors and disjoint half-window counts.
 * Fixed synthetic/public snapshots only; no current weather or mission advice.
 * Symbol locations: docs/CODE_INDEX.md.
 */
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { expect } from "@playwright/test";
import { runNativeJourney } from "./native_browser.mjs";

await runNativeJourney(async ({ page, request }) => {
  await page.goto("/");
  await expect(page.locator("#forecast-comparison tbody tr")).toHaveCount(9);
  await expect(page.locator("#forecast-comparison")).toContainText("overlapping cutoffs");
  await page.locator("#scenario").selectOption("synthetic-storm");
  await expect(page.locator("#forecast-comparison tbody tr").first()).toContainText("1.000");
  const response = await request.get("/api/run?scenario=synthetic-storm");
  assert.equal(response.status(), 200);
  const report = await response.json();
  assert.equal(report.forecast_comparison.length, 9);
  for (let index = 0; index < 3; index += 1) {
    assert.equal(
      report.forecast_comparison[index].scores.scored,
      report.forecast_comparison[index + 3].scores.scored +
        report.forecast_comparison[index + 6].scores.scored,
    );
  }
  for (const row of report.forecast_comparison) {
    assert.equal(row.available_observations + row.missing_observations, row.bins);
    assert.equal(row.selected.length, row.scores.scored);
    if (row.selected.length) {
      const mae =
        row.selected.reduce((sum, item) => sum + Math.abs(item.error), 0) / row.selected.length;
      assert.ok(Math.abs(mae - row.scores.mae) < 1e-8);
    } else assert.equal(row.scores.mae, null);
  }
  const pending = page.waitForEvent("download");
  await page.getByRole("link", { name: "JSON report ↓", exact: true }).click();
  const downloaded = await pending;
  assert.deepEqual(
    JSON.parse(await readFile(await downloaded.path(), "utf8")).forecast_comparison,
    report.forecast_comparison,
  );
  await page.locator("#scenario").selectOption("empty-window");
  await expect(page.locator("#forecast-comparison tbody tr").first()).toContainText("0 / 16");
});
