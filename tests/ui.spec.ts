/** Actual browser/service acceptance by Jason Stys. Functions/tests and fixtures: docs/CODE_INDEX.md.
 * All normal paths use the real handler and packaged resources. Network substitutions isolate explicit failure/security paths.
 */
import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("NOAA provenance and synthetic comparison are honest", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#evidence")).toBeVisible();
  await expect(page.locator(".provenance")).toContainText("NOAA SWPC estimated");
  await expect(page.locator(".score-grid")).toContainText("Not available");
  await expect(page.locator(".status-chip")).toContainText("unknown-issuance · 17");
  await page.locator("#scenario").selectOption("synthetic-storm");
  await expect(page.locator(".provenance")).toContainText("invented Kp");
  await expect(page.locator(".score-grid")).toContainText("1.000");
  await expect(page.locator(".metrics article").first()).toContainText("16 / 16");
});

test("positive lag and missing filter preserve context", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#evidence")).toBeVisible();
  await page.locator("#scenario").selectOption("synthetic-storm");
  await expect(page.locator(".provenance")).toContainText("invented Kp");
  await page.locator("#lag_hours").selectOption("6");
  await expect(page.locator("#inspector")).toContainText("2024-05-10T06:00:00Z");
  await page.locator("#scenario").selectOption("missing-bins");
  await expect(page.locator("#status")).toContainText("Evidence ready");
  await page.locator("#filter").selectOption("missing");
  await expect(page.locator(".inspect-bin")).toHaveCount(3);
  await page.getByRole("button", { name: "Inspect bin 6", exact: true }).click();
  await expect(page.locator("#inspector")).toContainText("Observation qualitymissing");
  await expect(page.locator(".metrics article").first()).toContainText("13 / 16");
});

test("forecast revision and lead gates update actual scores", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#evidence")).toBeVisible();
  await page.locator("#scenario").selectOption("forecast-revisions");
  await expect(page.locator(".status-chip").filter({ hasText: "superseded" })).toHaveText(
    "superseded · 1",
  );
  await page.getByText("Inspect forecast revisions and exclusion reasons", { exact: true }).click();
  await expect(page.getByRole("region", { name: "Forecast ledger" })).toContainText(
    "not-before-target",
  );
  await page.locator("#lead_hours").selectOption("24");
  await expect(page.locator(".metrics article").last()).toContainText("0");
  await expect(page.locator(".score-grid")).toContainText("Not available");
});

test("all downloads point at actual evidence and preserve input", async ({ page, request }) => {
  await page.goto("/");
  await expect(page.locator("#evidence")).toBeVisible();
  for (const label of ["JSON report ↓", "CSV report ↓", "HTML report ↓", "Input JSON ↓"]) {
    const link = page.getByRole("link", { name: label, exact: true });
    const href = await link.getAttribute("href");
    const response = await request.get(href!);
    expect(response.status()).toBe(200);
    expect(response.headers()["content-disposition"]).toContain("attachment");
    if (label.startsWith("JSON")) {
      const body = await response.json();
      expect(body.totals.estimated).toBe(56);
      expect(body.scores.scored).toBe(0);
    }
    if (label.startsWith("Input")) {
      const body = await response.json();
      expect(body.observations).toHaveLength(56);
    }
    if (label.startsWith("HTML")) expect(await response.text()).not.toContain("<script");
  }
});

test("settings persistence is explicit and finite", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#evidence")).toBeVisible();
  expect(
    await page.evaluate(() => localStorage.getItem("space-weather-preferences-v1")),
  ).toBeNull();
  await page.locator("#scenario").selectOption("flat-signal");
  await expect(page.locator(".association")).toContainText("constant-series");
  await page.getByLabel("Remember these settings on this device").check();
  await page.reload();
  await expect(page.locator("#scenario")).toHaveValue("flat-signal");
  await expect(page.locator("#evidence")).toBeVisible();
  await page.getByLabel("Remember these settings on this device").uncheck();
  expect(
    await page.evaluate(() => localStorage.getItem("space-weather-preferences-v1")),
  ).toBeNull();
});

test("failure hides stale evidence and allows explicit retry", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#evidence")).toBeVisible();
  await page.route("**/api/run?**", (route) => route.fulfill({ status: 503, body: "unavailable" }));
  await page.getByRole("button", { name: "Recompute evidence ↗" }).click();
  await expect(page.getByRole("button", { name: "Try again" })).toBeVisible();
  await expect(page.locator("#evidence")).toBeHidden();
  await page.unroute("**/api/run?**");
  await page.getByRole("button", { name: "Try again" }).click();
  await expect(page.locator("#evidence")).toBeVisible();
});

test("hostile response text cannot create injected elements", async ({ page }) => {
  await page.route("**/api/run?**", async (route) => {
    const response = await route.fetch();
    const body = await response.json();
    body.provenance.weather = '<img src=x onerror="alert(1)">';
    body.rows[0].quality = "<script>alert(1)</script>";
    await route.fulfill({ response, json: body });
  });
  await page.goto("/");
  await expect(page.locator("#evidence")).toBeVisible();
  await expect(page.locator(".provenance")).toContainText("<img src=x");
  await expect(page.locator("#evidence img, #evidence script")).toHaveCount(0);
});

test("mobile layout, keyboard chart regions and accessibility", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(page.locator("#evidence")).toBeVisible();
  const dimensions = await page.evaluate(() => ({
    width: innerWidth,
    scroll: document.documentElement.scrollWidth,
  }));
  expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.width + 1);
  const chart = page.getByRole("region", { name: "Kp chart; full numeric values in bin ledger" });
  await chart.focus();
  await expect(chart).toBeFocused();
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();
  expect(results.violations).toEqual([]);
});
