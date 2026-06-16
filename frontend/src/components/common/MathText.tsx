import { useMemo } from "react";
import "katex/dist/katex.min.css";

import { renderRichText } from "../../utils/mathRender";

type MathTextProps = {
  text: string;
  /** Render as a block (<div>) so display math and line breaks lay out nicely.
   *  Use for question stems and solutions. Leave false for inline contexts
   *  like answer choices. */
  block?: boolean;
  className?: string;
};

/**
 * Renders prose mixed with LaTeX (delimited or bare) via KaTeX. Falls back to
 * plain, whitespace-preserving text if rendering fails.
 */
export default function MathText({ text, block = false, className = "" }: MathTextProps) {
  const html = useMemo(() => renderRichText(text ?? ""), [text]);

  if (html === null) {
    return <span className="whitespace-pre-wrap leading-relaxed">{text}</span>;
  }

  const classes = `math-text leading-relaxed ${className}`.trim();

  if (block) {
    return <div className={classes} dangerouslySetInnerHTML={{ __html: html }} />;
  }
  return <span className={classes} dangerouslySetInnerHTML={{ __html: html }} />;
}
