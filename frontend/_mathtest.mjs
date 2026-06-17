/**
 * Quick manual regression checks for math rendering.
 * Run:  node _mathtest.mjs
 *   or: npm run test:math   (if script added)
 */
import assert from "node:assert/strict";
import {
  prepareMathText,
  repairJsonEscapeCorruption,
  renderRichText,
  unescapeLiteralNewlines,
} from "./src/utils/mathRender.ts";

const birdStem =
  "Consider the following knowledge base in first-order logic: \\forall x\\; (\\text{Bird}(x) \\rightarrow \\text{Flies}(x)) \\;\\;\\;\\;\\; (1)\\qquad \\text{Bird(Tweety)} \\;\\;\\;\\;\\; (2)\\qquad \\text{Bird(Chilly)} \\;\\;\\;\\;\\; (3)\\qquad \\neg\\text{Flies(Chilly)} \\;\\;\\;\\;\\; (4). Using resolution, which of the following clauses is derived when attempting to prove \\text{Flies(Tweety)}?";

const statsSol =
  "Let total students = 60.\\nGiven ratio of boys to girls who play cricket is 3:2.\\nLet C be set of cricket players, H be set of hockey players.\\nBy inclusion-exclusion: |C \\cup H| = |C| + |H| - |C \\cap H|.";

// ── Tab-corrupted \\text ──
{
  const tab = "prove " + "\t" + "ext{Flies(Tweety)}?";
  const fixed = repairJsonEscapeCorruption(tab);
  assert.ok(fixed.includes("\\text{Flies(Tweety)}"), `tab fix failed: ${fixed}`);
}

// ── Bare textFlies without backslash ──
{
  const bare = "prove textFlies(Tweety)?";
  const fixed = prepareMathText(bare);
  assert.ok(fixed.includes("\\text{Flies(Tweety)}"), `bare text fix failed: ${fixed}`);
}

// ── Bird KB stem ──
{
  const html = renderRichText(birdStem);
  assert.ok(html?.includes("katex"), "bird stem should render KaTeX");
  assert.ok(!html?.includes("math-error"), "bird stem should not error");
  assert.ok(!html?.includes("textFlies"), "should not show bare textFlies");
}

// ── Stats solution with \\n and set notation ──
{
  const html = renderRichText(statsSol, { solutionLayout: true });
  assert.ok(html?.includes("math-paragraph"), "solution should use paragraphs");
  assert.ok((html?.match(/math-paragraph/g) ?? []).length >= 3, "solution should split lines");
  assert.ok(html?.includes("katex"), "solution should render cup/cap");
  assert.ok(!html?.includes("\\nGiven"), "literal \\n should be gone");
}

// ── Literal newlines preserved for \\neq ──
{
  assert.equal(unescapeLiteralNewlines("$x \\neq 0$"), "$x \\neq 0$");
}

console.log("All _mathtest.mjs checks passed.");
