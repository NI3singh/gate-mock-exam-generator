"""Tests for the optional LLM verification gate (question_verifier)."""

import asyncio
import json
import os
import sys
import unittest
from unittest.mock import AsyncMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services import question_verifier
from app.services.llm_service import extract_json_object


def _verdict(is_correct=True, meets_bar=True, difficulty="hard") -> str:
    return json.dumps({
        "is_correct": is_correct,
        "computed_answer": "42",
        "assessed_difficulty": difficulty,
        "meets_bar": meets_bar,
        "reason": "test",
    })


def _q(qtype="MCQ") -> dict:
    return {
        "stem_tex": "What is the value of the expression?",
        "question_type": qtype,
        "marks": 2,
        "choices": ["40", "42", "44", "48"] if qtype != "NAT" else None,
        "answer": {"index": 1} if qtype != "NAT" else {"value": 42, "tolerance": 0.1},
        "solution_tex": "Step by step, the result is 42.",
        "code_snippet": None,
        "code_language": None,
    }


class ExtractJsonObjectTests(unittest.TestCase):
    def test_plain_object(self):
        obj = extract_json_object('{"is_correct": true, "x": 1}')
        self.assertEqual(obj["x"], 1)

    def test_object_with_fences_and_prose(self):
        obj = extract_json_object("Sure, here it is:\n```json\n{\"a\": 2}\n```\nDone.")
        self.assertEqual(obj["a"], 2)

    def test_object_with_latex_backslashes(self):
        # Unescaped LaTeX backslashes must be repaired, not crash the parse.
        obj = extract_json_object('{"computed_answer": "$\\frac{1}{2}$"}')
        self.assertIn("frac", obj["computed_answer"])

    def test_non_object_raises(self):
        with self.assertRaises(ValueError):
            extract_json_object("[1, 2, 3]")


class VerifyQuestionsTests(unittest.TestCase):
    def setUp(self):
        self._diff = question_verifier.settings.LLM_VERIFY_CHECK_DIFFICULTY
        question_verifier.settings.LLM_VERIFY_CHECK_DIFFICULTY = True

    def tearDown(self):
        question_verifier.settings.LLM_VERIFY_CHECK_DIFFICULTY = self._diff

    def _run(self, questions, llm_side_effect):
        with patch.object(
            question_verifier, "call_llm",
            new=AsyncMock(side_effect=llm_side_effect),
        ):
            return asyncio.run(
                question_verifier.verify_questions(questions, "hard")
            )

    def test_keeps_correct_and_hard(self):
        kept, rejected = self._run([_q()], [_verdict(True, True)])
        self.assertEqual(len(kept), 1)
        self.assertEqual(len(rejected), 0)

    def test_rejects_incorrect(self):
        kept, rejected = self._run([_q()], [_verdict(False, True)])
        self.assertEqual(len(kept), 0)
        self.assertEqual(len(rejected), 1)

    def test_rejects_too_easy_when_difficulty_check_on(self):
        kept, rejected = self._run([_q()], [_verdict(True, False)])
        self.assertEqual(len(kept), 0)
        self.assertEqual(len(rejected), 1)

    def test_keeps_too_easy_when_difficulty_check_off(self):
        question_verifier.settings.LLM_VERIFY_CHECK_DIFFICULTY = False
        kept, rejected = self._run([_q()], [_verdict(True, False)])
        self.assertEqual(len(kept), 1)
        self.assertEqual(len(rejected), 0)

    def test_fail_open_on_verifier_error(self):
        kept, rejected = self._run([_q()], RuntimeError("boom"))
        self.assertEqual(len(kept), 1)
        self.assertEqual(len(rejected), 0)

    def test_mixed_batch(self):
        kept, rejected = self._run(
            [_q(), _q(), _q("NAT")],
            [_verdict(True, True), _verdict(False, True), _verdict(True, False)],
        )
        self.assertEqual(len(kept), 1)
        self.assertEqual(len(rejected), 2)

    def test_empty_input_makes_no_calls(self):
        with patch.object(question_verifier, "call_llm", new=AsyncMock()) as m:
            kept, rejected = asyncio.run(
                question_verifier.verify_questions([], "hard")
            )
        self.assertEqual(kept, [])
        self.assertEqual(rejected, [])
        m.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
