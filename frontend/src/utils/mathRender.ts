/**
 * Rich text + math renderer shared by the exam screen, solutions review, and
 * question bank.
 */

import katex from "katex";

function isLetter(c: string): boolean {
  return (c >= "A" && c <= "Z") || (c >= "a" && c <= "z");
}

const MATH_SYMBOL = /[+\-*/=<>^_|().,:;!'~[\]?]/;
const DIGIT = /[0-9]/;

/** Detect over-escaped LaTeX inside math delimiters (`\\forall` etc.). */
const OVER_ESCAPED_CMD_HINT =
  /\\\\(?:forall|text|frac|cup|cap|neg|rightarrow|leftarrow|times|qquad|leq|geq)/;

const LATEX_N_PREFIX =
  /^(?:eq|eg(?:medspace|thickspace|thinspace)?|ot|u|abla|ewline|ewcommand|othing|mid|leftrightarrow|leftarrow|rightarrow|sim|subseteq|supseteq|subset|supset|times|cong|dash|atural|parallel|prec|preceq|succeq|geq|leq|gtr|exists|in|i|e|approx|uances|umber)/;

export function repairJsonEscapeCorruption(text: string): string {
  return (
    text
      .replace(/\u0009exttt\{/g, "\\texttt{")
      .replace(/\u0009extbf\{/g, "\\textbf{")
      .replace(/\u0009extit\{/g, "\\textit{")
      .replace(/\u0009extsc\{/g, "\\textsc{")
      .replace(/\u0009extrm\{/g, "\\textrm{")
      .replace(/\u0009ext\{/g, "\\text{")
      .replace(/\u0009imes\b/g, "\\times")
      .replace(/\u0009heta\b/g, "\\theta")
      .replace(/\u0009au\b/g, "\\tau")
      .replace(/\u0009riangle\b/g, "\\triangle")
      .replace(/\u000Dightarrow\b/g, "\\rightarrow")
      .replace(/\u000Dangle\b/g, "\\rangle")
      .replace(/\u000Dceil\b/g, "\\rceil")
      .replace(/\u000Dfloor\b/g, "\\rfloor")
      .replace(/\u000Crac\{/g, "\\frac{")
      .replace(/\u000Corall\b/g, "\\forall")
      .replace(/\u0008eta\b/g, "\\beta")
      .replace(/\u0008inom\{/g, "\\binom{")
      .replace(/\u0008ig\b/g, "\\big")
      .replace(/\u0008igg\b/g, "\\bigg")
      .replace(/(?<![\\a-zA-Z{])ext\{/g, "\\text{")
      .replace(/(?<![\\a-zA-Z])text\{/g, "\\text{")
      .replace(/(?<![\\a-zA-Z])text([A-Z][A-Za-z]*)\(([^)]+)\)/g, "\\text{$1($2)}")
      .replace(/(?<![\\a-zA-Z])imes(?=\b|[({])/g, "\\times")
      .replace(/(?<![\\a-zA-Z])ightarrow\b/g, "\\rightarrow")
      .replace(/(?<![\\a-zA-Z])orall\b/g, "\\forall")
      .replace(/(?<![\\a-zA-Z])rac\{/g, "\\frac{")
      .replace(/(?<![\\a-zA-Z])neg(?=\\text)/g, "\\neg")
  );
}

function outsideMath(text: string, fn: (chunk: string) => string): string {
  let out = "";
  let i = 0;
  const n = text.length;
  while (i < n) {
    if (text[i] === "$") {
      if (text[i + 1] === "$") {
        const end = text.indexOf("$$", i + 2);
        if (end === -1) {
          out += text.slice(i);
          break;
        }
        out += text.slice(i, end + 2);
        i = end + 2;
        continue;
      }
      const end = text.indexOf("$", i + 1);
      if (end === -1) {
        out += text.slice(i);
        break;
      }
      out += text.slice(i, end + 1);
      i = end + 1;
      continue;
    }
    const next = text.indexOf("$", i);
    const chunk = next === -1 ? text.slice(i) : text.slice(i, next);
    out += fn(chunk);
    i = next === -1 ? n : next;
  }
  return out;
}

export function unescapeLiteralNewlines(text: string): string {
  return outsideMath(text, (chunk) =>
    chunk.replace(/\\n/g, (match, offset, whole) => {
      const after = whole.slice(offset + 2);
      const word = after.match(/^[a-zA-Z]+/)?.[0] ?? "";
      if (word && LATEX_N_PREFIX.test(word)) return match;
      return "\n";
    }),
  );
}

export function normalizeOverEscapedBackslashes(text: string): string {
  if (!/\\\\/.test(text)) return text;
  return outsideMath(text, (chunk) => {
    if (!/\\\\/.test(chunk)) return chunk;
    // Collapse \\cmd → \cmd when we see known over-escaped LaTeX commands.
    if (!/\\\\(?:forall|text|frac|cup|cap|neg|rightarrow|leftarrow|times|qquad|leq|geq)/.test(chunk)) {
      return chunk;
    }
    return chunk.replace(/\\\\(?=[a-zA-Z{([\]|;])/g, "\\");
  });
}

function skipBalanced(text: string, pos: number, open: string, close: string): number {
  const n = text.length;
  let depth = 0;
  while (pos < n) {
    const c = text[pos];
    if (c === "\\") {
      pos += 2;
      continue;
    }
    if (c === open) depth++;
    else if (c === close) {
      depth--;
      if (depth === 0) return pos + 1;
    }
    pos++;
  }
  return n;
}

function findRunEnd(text: string, start: number): number {
  const n = text.length;
  let pos = start;
  let lastSolid = start;
  while (pos < n) {
    const c = text[pos];
    if (c === "$" || c === "\n") break;

    if (c === "\\") {
      if (pos + 1 < n) {
        const nx = text[pos + 1];
        if (isLetter(nx)) {
          pos += 1;
          while (pos < n && isLetter(text[pos])) pos++;
          if (pos < n && text[pos] === "*") pos++;
          while (pos < n) {
            let look = pos;
            while (look < n && text[look] === " ") look++;
            if (look < n && (text[look] === "{" || text[look] === "[")) {
              const open = text[look];
              const close = open === "{" ? "}" : "]";
              pos = skipBalanced(text, look, open, close);
            } else break;
          }
          lastSolid = pos;
          continue;
        }
        pos += 2;
        lastSolid = pos;
        continue;
      }
      pos++;
      lastSolid = pos;
      continue;
    }

    if (c === "{") {
      pos = skipBalanced(text, pos, "{", "}");
      lastSolid = pos;
      continue;
    }

    if (c === " " || c === "\t") {
      let look = pos;
      while (look < n && (text[look] === " " || text[look] === "\t")) look++;
      if (look >= n) break;
      const after = text[look];
      if (after === "\n") break;
      if (after === "\\" || after === "{" || MATH_SYMBOL.test(after) || DIGIT.test(after)) {
        pos = look;
        continue;
      }
      if (isLetter(after) && (look + 1 >= n || !isLetter(text[look + 1]))) {
        pos = look;
        continue;
      }
      break;
    }

    if (MATH_SYMBOL.test(c) || DIGIT.test(c)) {
      pos++;
      lastSolid = pos;
      continue;
    }

    if (isLetter(c)) {
      let w = pos;
      while (w < n && isLetter(text[w])) w++;
      if (w - pos === 1) {
        pos = w;
        lastSolid = pos;
        continue;
      }
      break;
    }

    break;
  }
  return lastSolid;
}

function mergeAdjacentRuns(text: string, runs: Array<[number, number]>): Array<[number, number]> {
  if (runs.length === 0) return runs;
  const merged: Array<[number, number]> = [runs[0]];
  for (let r = 1; r < runs.length; r++) {
    const [s, e] = runs[r];
    const prev = merged[merged.length - 1];
    const gap = text.slice(prev[1], s);
    if (/^[\s;]*(?:\(\d+\)[\s;]*)*$/.test(gap) && gap.length < 40) {
      prev[1] = e;
    } else {
      merged.push([s, e]);
    }
  }
  return merged;
}

function collectBareLatexRuns(text: string): Array<[number, number]> {
  const n = text.length;
  const runs: Array<[number, number]> = [];
  let i = 0;
  while (i < n) {
    if (text[i] === "$") {
      if (text[i + 1] === "$") {
        const end = text.indexOf("$$", i + 2);
        i = end === -1 ? n : end + 2;
      } else {
        const end = text.indexOf("$", i + 1);
        i = end === -1 ? n : end + 1;
      }
      continue;
    }
    if (text[i] === "\\" && i + 1 < n && isLetter(text[i + 1])) {
      runs.push([i, findRunEnd(text, i)]);
      i = runs[runs.length - 1][1];
      continue;
    }
    i++;
  }
  return mergeAdjacentRuns(text, runs);
}

function wrapBareLatexRuns(text: string): string {
  const runs = collectBareLatexRuns(text);
  if (runs.length === 0) return text;
  let out = "";
  let cursor = 0;
  for (const [start, end] of runs) {
    out += text.slice(cursor, start);

    let absStart = start;
    let absEnd = end;

    // Include a single variable/operator immediately before the run (e.g. C in C \cup H).
    const before = out.match(/([A-Za-z0-9+\-*/=<>|])(\s*)$/);
    if (before) {
      const leadIdx = out.length - before[0].length;
      const prev = leadIdx > 0 ? out[leadIdx - 1] : "";
      if (!/[A-Za-z0-9]/.test(prev)) {
        out = out.slice(0, leadIdx);
        absStart = start - before[1].length - 1;
      }
    }

    // Include | … | set/cardinality delimiters when wrapping e.g. |C \cup H|.
    while (absStart > 0 && /\s/.test(text[absStart - 1])) absStart--;
    if (absStart > 0 && text[absStart - 1] === "|") absStart--;
    while (absEnd < text.length && /\s/.test(text[absEnd])) absEnd++;
    if (absEnd < text.length && text[absEnd] === "|") absEnd++;

    if (absStart < start) {
      out = out.slice(0, out.length - (start - absStart));
    }

    const slice = text.slice(absStart, absEnd);
    const useDisplay = slice.length > 80 || /\\qquad|\\begin\{/.test(slice);
    out += (useDisplay ? "$$" : "$") + slice + (useDisplay ? "$$" : "$");
    cursor = absEnd;
  }
  out += text.slice(cursor);
  return out;
}

function normalizeDelimiters(text: string): string {
  return text
    .replace(/(?<!\\)\\\[/g, "$$$$")
    .replace(/(?<!\\)\\\]/g, "$$$$")
    .replace(/(?<!\\)\\\(/g, "$")
    .replace(/(?<!\\)\\\)/g, "$");
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function renderMath(content: string, displayMode: boolean): string {
  try {
    let cleaned = content.trim();
    if (OVER_ESCAPED_CMD_HINT.test(cleaned)) {
      cleaned = cleaned.replace(/\\\\(?=[a-zA-Z{([\]|;])/g, "\\");
    }
    return katex.renderToString(cleaned, {
      displayMode,
      throwOnError: false,
      trust: false,
      strict: false,
    });
  } catch {
    return `<span class="math-error">[Math Error]</span>`;
  }
}

type Segment = { type: "text" | "inline" | "display"; content: string };

function splitSegments(text: string): Segment[] {
  const segments: Segment[] = [];
  const displaySplit = text.split(/(\$\$[\s\S]*?\$\$)/g);
  for (const chunk of displaySplit) {
    if (chunk.startsWith("$$") && chunk.endsWith("$$") && chunk.length > 4) {
      segments.push({ type: "display", content: chunk.slice(2, -2) });
      continue;
    }
    const inlineSplit = chunk.split(/(\$[^$\n]+?\$)/g);
    for (const piece of inlineSplit) {
      if (piece.startsWith("$") && piece.endsWith("$") && piece.length > 2) {
        segments.push({ type: "inline", content: piece.slice(1, -1) });
      } else if (piece.length > 0) {
        segments.push({ type: "text", content: piece });
      }
    }
  }
  return segments;
}

function formatTextBlock(text: string, solutionLayout: boolean): string {
  const trimmed = text.replace(/\r\n/g, "\n");
  const paragraphs = solutionLayout
    ? trimmed.split(/\n+/).map((p) => p.trim()).filter(Boolean)
    : trimmed.split(/\n{2,}/).map((p) => p.trim()).filter(Boolean);

  if (paragraphs.length === 0 && trimmed.length > 0) {
    paragraphs.push(trimmed);
  }

  return paragraphs
    .map((para) => {
      const lines = para.split("\n");
      const inner = lines
        .map((line) => {
          const t = line.trimEnd();
          if (/^\d+[\.\)]\s/.test(t)) {
            return `<div class="solution-step">${escapeHtml(t)}</div>`;
          }
          return escapeHtml(t);
        })
        .join("<br/>");
      return `<p class="math-paragraph">${inner}</p>`;
    })
    .join("");
}

function expandLongParagraphBreaks(text: string): string {
  if (text.includes("\n") || text.length < 350) return text;
  return text.replace(/\.\s+(?=[A-Z])/g, ".\n\n");
}

export type RenderOptions = {
  /** One paragraph per line — best for step-by-step solutions. */
  solutionLayout?: boolean;
};

export function prepareMathText(raw: string): string {
  let text = raw ?? "";
  text = repairJsonEscapeCorruption(text);
  text = normalizeOverEscapedBackslashes(text);
  text = unescapeLiteralNewlines(text);
  text = expandLongParagraphBreaks(text);
  text = normalizeDelimiters(text);
  text = wrapBareLatexRuns(text);
  return text;
}

export function renderRichText(raw: string, options: RenderOptions = {}): string | null {
  try {
    if (!raw) return "";
    const prepared = prepareMathText(raw);
    const segments = splitSegments(prepared);
    const solutionLayout = options.solutionLayout ?? false;
    return segments
      .map((seg) => {
        if (seg.type === "display") {
          return `<div class="math-display">${renderMath(seg.content, true)}</div>`;
        }
        if (seg.type === "inline") {
          return `<span class="math-inline">${renderMath(seg.content, false)}</span>`;
        }
        return formatTextBlock(seg.content, solutionLayout);
      })
      .join("");
  } catch {
    return null;
  }
}
