import { useMemo } from "react";
import "katex/dist/katex.min.css";

import { renderRichText } from "../../utils/mathRender";

type MathTextProps = {
  text: string;
  /** Block layout for stems / solutions (display math + line breaks). */
  block?: boolean;
  /** Step-by-step solution formatting: one paragraph per line. */
  solution?: boolean;
  className?: string;
};

/**
 * Renders prose mixed with LaTeX (delimited or bare) via KaTeX. Falls back to
 * plain, whitespace-preserving text if rendering fails.
 */
export default function MathText({
  text,
  block = false,
  solution = false,
  className = "",
}: MathTextProps) {
  const html = useMemo(
    () => renderRichText(text ?? "", { solutionLayout: solution }),
    [text, solution],
  );

  if (html === null) {
    return <span className="whitespace-pre-wrap leading-relaxed">{text}</span>;
  }

  const classes = [
    "math-text",
    "leading-relaxed",
    solution ? "math-text-solution" : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  if (block) {
    return <div className={classes} dangerouslySetInnerHTML={{ __html: html }} />;
  }
  return <span className={classes} dangerouslySetInnerHTML={{ __html: html }} />;
}
