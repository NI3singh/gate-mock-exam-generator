import assert from "node:assert/strict";

import {
  prepareMathText,
  repairJsonEscapeCorruption,
  renderRichText,
  unescapeLiteralNewlines,
} from "./mathRender";

// ── JSON escape corruption ────────────────────────────────────────────────────
{
  const corrupted = "Consider: \forall x\; (\text{Bird}(x) \rightarrow \text{Flies}(x))";
  // Simulate \t and \f eaten as control chars
  const withTab = "Consider: " + "\u0009ext{Bird}(x) \u000Dightarrow \u0009ext{Flies}(x)";
  const fixed = repairJsonEscapeCorruption(withTab);
  assert.ok(fixed.includes("\\text{Bird}"), `expected \\text{Bird}, got: ${fixed}`);
  assert.ok(fixed.includes("\\rightarrow"), `expected \\rightarrow, got: ${fixed}`);
}

{
  const withForall = "\u000Corall x";
  const fixed = repairJsonEscapeCorruption(withForall);
  assert.ok(fixed.includes("\\forall"), `expected \\forall, got: ${fixed}`);
}

// ── Literal \n in solutions ───────────────────────────────────────────────────
{
  const sol = "Let total = 60.\\nGiven ratio is 3:2.\\nWe have B + G = 60.";
  const fixed = unescapeLiteralNewlines(sol);
  assert.ok(fixed.includes("\nGiven"), `expected newline before Given, got: ${JSON.stringify(fixed)}`);
  assert.ok(!fixed.includes("\\neq"), "should not touch \\neq if present");
  const neq = "$x \\neq 0$";
  assert.equal(unescapeLiteralNewlines(neq), neq);
}

// ── Bird KB stem (properly escaped LaTeX) ───────────────────────────────────
{
  const stem =
    "Consider the following knowledge base in first-order logic: \\forall x\\; (\\text{Bird}(x) \\rightarrow \\text{Flies}(x)) \\;\\;\\;\\;\\; (1)\\qquad \\text{Bird(Tweety)} \\;\\;\\;\\;\\; (2)\\qquad \\text{Bird(Chilly)} \\;\\;\\;\\;\\; (3)\\qquad \\neg\\text{Flies(Chilly)} \\;\\;\\;\\;\\; (4). Using resolution, which of the following clauses is derived when attempting to prove \\text{Flies(Tweety)}?";
  const html = renderRichText(stem);
  assert.ok(html, "should render");
  assert.ok(html!.includes("katex"), "should contain KaTeX output");
  assert.ok(html!.includes("Bird"), "should render Bird in formula");
  assert.ok(!html!.includes("math-error"), "should not have math errors");
}

// ── Solution with literal newlines and set notation ───────────────────────────
{
  const sol =
    "Let total students = 60.\\nGiven ratio of boys to girls who play cricket is 3:2.\\nLet C be set of cricket players, H be set of hockey players.\\nBy inclusion-exclusion: |C \\cup H| = |C| + |H| - |C \\cap H|.";
  const html = renderRichText(sol, { solutionLayout: true });
  assert.ok(html, "should render solution");
  assert.ok(html!.includes("math-paragraph"), "should use paragraphs");
  assert.ok((html!.match(/math-paragraph/g) ?? []).length >= 3, "should split on each line");
  assert.ok(html!.includes("katex"), "should render \\cup and \\cap");
  assert.ok(!html!.includes("\\nGiven"), "literal \\n should be gone");
}

// ── Bare textFlies corruption ─────────────────────────────────────────────────
{
  const fixed = prepareMathText("prove textFlies(Tweety)?");
  assert.ok(fixed.includes("\\text{Flies(Tweety)}"), "should repair textFlies");
}

// ── Over-escaped backslashes ──────────────────────────────────────────────────
{
  const over = "Find $\\\\frac{1}{2}$ when $x = 1$.";
  const prepared = prepareMathText(over);
  assert.ok(prepared.includes("\\frac"), "should normalize frac");
}

console.log("mathRender tests passed");
