"""Tests for PYQ exemplar formatting (pure, no DB)."""

import os
import sys
import unittest
from types import SimpleNamespace

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.pyq_retrieval import format_exemplars


def _row(question_type, marks, stem, *, options=None, answer=None, answer_value=None):
    return SimpleNamespace(
        question_type=question_type,
        marks=marks,
        stem=stem,
        options=options,
        answer=answer,
        answer_value=answer_value,
    )


class FormatExemplarsTests(unittest.TestCase):
    def test_empty_returns_empty_string(self):
        self.assertEqual(format_exemplars([]), "")

    def test_mcq_block_has_header_options_and_answer(self):
        out = format_exemplars(
            [_row("MCQ", 2, "What is X?", options=["a", "b", "c", "d"], answer="C")]
        )
        self.assertIn("REFERENCE", out)
        self.assertIn("do NOT copy", out)
        self.assertIn("(MCQ, 2 marks) What is X?", out)
        self.assertIn("A) a", out)
        self.assertIn("D) d", out)
        self.assertIn("Answer: C", out)

    def test_nat_block_uses_value_and_no_options(self):
        out = format_exemplars([_row("NAT", 1, "Compute Y.", answer_value=42)])
        self.assertIn("(NAT, 1 mark) Compute Y.", out)
        self.assertIn("Answer: 42", out)
        self.assertNotIn("A)", out)

    def test_singular_vs_plural_marks(self):
        out = format_exemplars(
            [_row("MCQ", 1, "Q1", options=["1", "2", "3", "4"], answer="A")]
        )
        self.assertIn("(MCQ, 1 mark)", out)
        self.assertNotIn("1 marks", out)

    def test_multiple_rows_numbered(self):
        out = format_exemplars(
            [
                _row("MCQ", 1, "Q1", options=["1", "2", "3", "4"], answer="A"),
                _row("MSQ", 2, "Q2", options=["1", "2", "3", "4"], answer="A,C"),
            ]
        )
        self.assertIn("[1]", out)
        self.assertIn("[2]", out)
        self.assertIn("Answer: A,C", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
