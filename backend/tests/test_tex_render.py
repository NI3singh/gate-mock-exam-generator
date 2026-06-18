"""Tests for the compile-safe LaTeX renderer used by the solution-key PDF."""

import os
import re
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.tex_render import render_mixed_latex


def _inline_dollar_count(s: str) -> int:
    """Count real inline-math '$' (ignoring escaped '\\$')."""
    return len(re.findall(r"(?<!\\)\$", s))


def _display_open(s: str) -> int:
    return len(re.findall(r"(?<!\\)\\\[", s))


def _display_close(s: str) -> int:
    return len(re.findall(r"(?<!\\)\\\]", s))


class BareLatexWrappingTests(unittest.TestCase):
    def test_bare_commands_get_wrapped_not_escaped(self):
        raw = (
            r"\forall x (\text{Bird}(x) \rightarrow \text{Flies}(x))"
            "\n"
            r"\text{Bird}(\text{Tweety})"
            "\n"
            "Therefore Tweety flies."
        )
        out = render_mixed_latex(raw, solution_layout=True)
        # Commands must survive as real LaTeX, never as literal backslash text.
        self.assertIn(r"\forall", out)
        self.assertIn(r"\rightarrow", out)
        self.assertNotIn(r"\textbackslash{}forall", out)
        self.assertNotIn(r"\textbackslash{}", out)
        # Plain prose is preserved.
        self.assertIn("Therefore Tweety flies.", out)
        # Inline math delimiters are balanced.
        self.assertEqual(_inline_dollar_count(out) % 2, 0)

    def test_plain_prose_is_never_mathified(self):
        raw = "A class has 60 students with a 3:2 ratio of boys to girls."
        out = render_mixed_latex(raw)
        self.assertNotIn("$", out)
        self.assertIn("60 students", out)
        self.assertIn("3:2", out)

    def test_delimiters_are_normalized(self):
        raw = r"Given \(x = 5\) we compute \[ y = x^2 \] for the area."
        out = render_mixed_latex(raw)
        # \( \) -> inline $, \[ \] -> display \[ \]
        self.assertNotIn(r"\(", out)
        self.assertNotIn(r"\)", out)
        self.assertEqual(_display_open(out), _display_close(out))
        self.assertGreaterEqual(_display_open(out), 1)


class SolutionLayoutTests(unittest.TestCase):
    def test_steps_become_paragraphs_without_linebreak_macros(self):
        raw = (
            "Step 1: Total students = 50.\n"
            r"$|C \cup H| = |C| + |H| - |C \cap H|$"
            "\n"
            "Step 2: Substitute the known values.\n"
            r"$$ |C \cup H| = 30 + 25 - 10 = 45 $$"
            "\n"
            "So 45 students play at least one sport."
        )
        out = render_mixed_latex(raw, solution_layout=True)
        # No fragile/illegal '\\' line breaks anywhere in step-by-step layout.
        self.assertNotIn(r"\\", out)
        # Steps are separated into paragraphs (blank line between them).
        self.assertIn("\n\n", out)
        # Display math is wrapped legally and balanced.
        self.assertEqual(_display_open(out), _display_close(out))
        self.assertEqual(_inline_dollar_count(out) % 2, 0)
        self.assertIn("So 45 students play at least one sport.", out)

    def test_no_leading_or_trailing_linebreak(self):
        raw = "\n\nFirst line.\n\n\nSecond line.\n\n"
        out = render_mixed_latex(raw, solution_layout=True)
        self.assertFalse(out.startswith("\\"))
        self.assertFalse(out.endswith("\\"))
        self.assertNotIn(r"\\", out)


class DisplayMathSafetyTests(unittest.TestCase):
    def test_display_with_linebreaks_is_wrapped_in_aligned(self):
        raw = r"$$ a = b \\ c = d $$"
        out = render_mixed_latex(raw)
        self.assertIn(r"\begin{aligned}", out)
        self.assertIn(r"\end{aligned}", out)
        self.assertEqual(_display_open(out), _display_close(out))

    def test_align_environment_is_converted_to_nestable_aligned(self):
        raw = r"$$\begin{align} x &= 1 \\ y &= 2 \end{align}$$"
        out = render_mixed_latex(raw)
        # Display-only 'align' becomes nestable 'aligned', wrapped in \[ \].
        self.assertNotIn(r"\begin{align}", out)
        self.assertEqual(out.count(r"\begin{aligned}"), 1)
        self.assertEqual(out.count(r"\end{aligned}"), 1)
        self.assertEqual(_display_open(out), _display_close(out))
        self.assertEqual(_display_open(out), 1)

    def test_nested_display_env_is_made_nestable(self):
        # align* nested inside aligned is illegal LaTeX -> must be converted.
        raw = r"$$\begin{aligned} a &= 1 \\ \begin{align*} b &= 2 \end{align*} \end{aligned}$$"
        out = render_mixed_latex(raw)
        self.assertNotIn(r"align*", out)
        self.assertEqual(out.count(r"\begin{aligned}"), out.count(r"\end{aligned}"))

    def test_unclosed_environment_is_closed(self):
        raw = r"$$\begin{pmatrix} 1 & 2 \\ 3 & 4$$"
        out = render_mixed_latex(raw)
        self.assertEqual(out.count(r"\begin{pmatrix}"), out.count(r"\end{pmatrix}"))
        self.assertGreaterEqual(out.count(r"\end{pmatrix}"), 1)


    def test_aligned_subenvironment_is_wrapped_in_display_once(self):
        raw = r"$$\begin{aligned} x &= 1 \\ y &= 2 \end{aligned}$$"
        out = render_mixed_latex(raw)
        self.assertEqual(out.count(r"\begin{aligned}"), 1)
        self.assertEqual(_display_open(out), 1)
        self.assertEqual(_display_close(out), 1)

    def test_unbalanced_dollar_does_not_run_away(self):
        raw = "The price is $5 for each unit only."
        out = render_mixed_latex(raw)
        # The lone '$' must be escaped to a literal, leaving no open math.
        self.assertEqual(_inline_dollar_count(out), 0)
        self.assertIn(r"\$5", out)


class TextCommandAndTableTests(unittest.TestCase):
    def test_raw_underscore_in_text_command_is_escaped(self):
        # $\texttt{emp_id}$ : raw _ inside \texttt is fatal in math; must escape.
        out = render_mixed_latex(r"key $\texttt{emp_id}$ end")
        self.assertIn(r"\texttt{emp\_id}", out)
        self.assertNotIn("emp_id", out)

    def test_mangled_table_is_flattened_to_text(self):
        raw = (
            r"$$\begin{tabular}{|c|c|}\hline Year & Sales $$ \\ "
            r"$\hline 2020$ & 120 \\ \hline 2021 & 140 \\ \hline \end{tabular}$$"
        )
        out = render_mixed_latex(raw, solution_layout=True)
        self.assertNotIn(r"\begin{tabular}", out)
        self.assertNotIn(r"\hline", out)
        # The data survives as readable text.
        self.assertIn("2020", out)
        self.assertIn("140", out)
        self.assertEqual(_inline_dollar_count(out) % 2, 0)


class MathHardeningTests(unittest.TestCase):
    def test_unicode_symbols_are_mapped(self):
        raw = "For all values ∀ x we have x ≤ 5 and α + β ≥ 0."
        out = render_mixed_latex(raw)
        self.assertIn(r"\forall", out)
        self.assertIn(r"\leq", out)
        self.assertIn(r"\alpha", out)
        self.assertIn(r"\geq", out)
        # No stray raw unicode operators left behind.
        for ch in "∀≤≥α":
            self.assertNotIn(ch, out)

    def test_percent_and_hash_inside_math_are_protected(self):
        raw = r"$x \% y$ and $a \# b$ plus a raw $p % q$ case"
        out = render_mixed_latex(raw)
        # No unescaped % or # remains to comment-out / crash the line.
        self.assertEqual(len(re.findall(r"(?<!\\)%", out)), 0)
        self.assertEqual(len(re.findall(r"(?<!\\)#", out)), 0)

    def test_over_escaped_commands_are_normalized_in_math(self):
        raw = r"$\\forall x \\rightarrow y$"
        out = render_mixed_latex(raw)
        self.assertIn(r"\forall", out)
        self.assertNotIn(r"\\forall", out)


class RobustnessTests(unittest.TestCase):
    def test_empty_and_none(self):
        self.assertEqual(render_mixed_latex(None), "")
        self.assertEqual(render_mixed_latex(""), "")
        self.assertEqual(render_mixed_latex("   \n  "), "")

    def test_returns_string_for_varied_inputs(self):
        samples = [
            r"Compute $\frac{1}{2} + \frac{1}{3}$.",
            "Plain text only.",
            r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}",
            "Mixed ∑ and $x^2$ and \\(y\\) end.",
            r"$$\int_0^1 x\,dx = \frac{1}{2}$$",
        ]
        for s in samples:
            out = render_mixed_latex(s, solution_layout=True)
            self.assertIsInstance(out, str)
            self.assertEqual(_display_open(out), _display_close(out))
            self.assertEqual(_inline_dollar_count(out) % 2, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
