/** Re-captures /analytics, waiting out the auth-check splash screen. */
import { chromium } from "playwright";
import { fileURLToPath } from "node:url";
import path from "node:path";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(HERE, "..", "public", "shots");
const PROFILE = path.join(HERE, ".profile");

const context = await chromium.launchPersistentContext(PROFILE, {
  headless: false,
  viewport: { width: 1600, height: 1000 },
  deviceScaleFactor: 2,
  args: ["--hide-scrollbars"],
});
const page = context.pages()[0] ?? (await context.newPage());

const splashGone = () =>
  page.waitForFunction(
    () => !document.body.innerText.toUpperCase().includes("CHECKING ACCESS"),
    undefined,
    { timeout: 90_000 }
  );

try {
  // Warm up the session on the dashboard first (auth restore can be slow on
  // a fresh launch), then navigate client-side to analytics.
  await page.goto("http://localhost:5173/dashboard", { waitUntil: "domcontentloaded" });
  await splashGone();
  if (!page.url().includes("/dashboard")) {
    throw new Error(`Not authenticated (landed on ${page.url()}) — re-run capture.mjs and log in.`);
  }
  console.log("Session restored; opening analytics ...");
  await page.goto("http://localhost:5173/analytics", { waitUntil: "domcontentloaded" });
  await splashGone();
  await page.waitForLoadState("networkidle").catch(() => {});
  await page.evaluate(() => document.fonts.ready).catch(() => {});
  await page.waitForTimeout(4500); // charts + entrance animations
  await page.screenshot({ path: path.join(OUT, "analytics.png"), fullPage: true });
  await page.screenshot({ path: path.join(OUT, "analytics-top.png") });
  console.log("analytics re-captured");
} finally {
  await context.close();
}
