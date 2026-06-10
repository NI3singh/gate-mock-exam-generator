/**
 * Captures real screenshots of the running website (localhost:5173) for the
 * WebsiteTour Remotion composition.
 *
 * Auth flow: opens a VISIBLE browser using a persistent profile. If not
 * logged in yet, it waits (up to 5 minutes) for YOU to log in manually, then
 * captures everything automatically. Re-runs reuse the saved session.
 *
 * Output: intro-video/public/shots/*.png  (2x DPR for crisp pans/zooms)
 *
 * Run:  node capture/capture.mjs
 */

import { chromium } from "playwright";
import { fileURLToPath } from "node:url";
import path from "node:path";
import fs from "node:fs";

const BASE = "http://localhost:5173";
const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(HERE, "..", "public", "shots");
const PROFILE = path.join(HERE, ".profile");

fs.mkdirSync(OUT, { recursive: true });

const VIEWPORT = { width: 1600, height: 1000 };

/** Wait for fonts + network + entrance animations (one-shot CSS) to settle. */
async function settle(page, extraMs = 2600) {
  await page.waitForLoadState("networkidle").catch(() => {});
  await page.evaluate(() => document.fonts.ready).catch(() => {});
  await page.waitForTimeout(extraMs);
}

async function shoot(page, url, name, { fullPage = true, viewportToo = false } = {}) {
  console.log(`-> ${url}`);
  await page.goto(`${BASE}${url}`, { waitUntil: "domcontentloaded" });
  await settle(page);
  if (fullPage) {
    await page.screenshot({ path: path.join(OUT, `${name}.png`), fullPage: true });
    console.log(`   saved shots/${name}.png (full page)`);
  }
  if (viewportToo || !fullPage) {
    await page.screenshot({ path: path.join(OUT, `${name}-top.png`) });
    console.log(`   saved shots/${name}-top.png (viewport)`);
  }
}

const context = await chromium.launchPersistentContext(PROFILE, {
  headless: false,
  viewport: VIEWPORT,
  deviceScaleFactor: 2,
  args: ["--hide-scrollbars"],
});
const page = context.pages()[0] ?? (await context.newPage());

try {
  // ── 1. Public pages (logged out or in — content is the same) ──
  await shoot(page, "/", "landing", { viewportToo: true });
  await shoot(page, "/login", "login", { fullPage: false });

  // ── 2. Ensure an authenticated session ──
  await page.goto(`${BASE}/dashboard`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(3000);
  if (!page.url().includes("/dashboard")) {
    console.log("\n================================================================");
    console.log("  PLEASE LOG IN in the browser window that just opened.");
    console.log("  Waiting up to 5 minutes for the dashboard to appear...");
    console.log("================================================================\n");
    await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
    await page.waitForURL("**/dashboard", { timeout: 5 * 60 * 1000 });
    console.log("Logged in — continuing capture.");
  } else {
    console.log("Already logged in (saved session) — continuing capture.");
  }

  // ── 3. Authenticated, read-only pages ──
  await shoot(page, "/dashboard", "dashboard", { viewportToo: true });
  await shoot(page, "/generate-exam", "generate-exam", { viewportToo: true });
  await shoot(page, "/question-bank", "question-bank", { viewportToo: true });
  await shoot(page, "/analytics", "analytics", { viewportToo: true });

  console.log("\nAll screenshots captured into intro-video/public/shots/");
} finally {
  await context.close();
}
