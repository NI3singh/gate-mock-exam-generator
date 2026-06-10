"""Unit tests for the PYQ (previous-year-question) reference context.

Hermetic: reuses the fake-module isolation from test_llm_providers so the
question_generator module imports without asyncpg/pgvector being installed.
Covers the pure formatter/attach helpers, the prompt-template contract
({pyq_examples} placeholder present and formattable), and the pass-through of
spec["pyq_examples"] into the LLM user prompt.
"""

import asyncio
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.test_llm_providers import _load_question_generator_isolated

PROMPTS_DIR = (
    Path(__file__).resolve().parent.parent / "app" / "prompts"
)


def _make_pyq(i: int = 1, **overrides) -> dict:
    pyq = {
        "stem": f"What is the time complexity of binary search variant {i}?",
        "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
        "question_type": "MCQ",
        "marks": 1,
        "topic": "Algorithms",
        "year": 2024,
    }
    pyq.update(overrides)
    return pyq


class PyqFormatterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.g = _load_question_generator_isolated()

    def test_empty_bucket_returns_exactly_empty_string(self) -> None:
        # "" exactly — the template slot must degrade to a blank line.
        self.assertEqual(self.g._format_pyq_examples([]), "")

    def test_framing_and_example_markers_present(self) -> None:
        text = self.g._format_pyq_examples([_make_pyq()])
        self.assertIn("REFERENCE — REAL past GATE questions", text)
        self.assertIn("COMPLETELY ORIGINAL", text)
        self.assertIn("[PYQ 1] (GATE 2024, MCQ, 1 marks, topic: Algorithms)", text)
        self.assertIn("Options: (A) O(1)  (B) O(log n)  (C) O(n)  (D) O(n log n)", text)
        self.assertIn("END OF REFERENCE.", text)

    def test_at_most_k_examples_sampled(self) -> None:
        bucket = [_make_pyq(i) for i in range(12)]
        text = self.g._format_pyq_examples(bucket, k=3)
        self.assertEqual(text.count("[PYQ "), 3)

    def test_long_stem_truncated_with_ellipsis(self) -> None:
        long_stem = "a" * (self.g.PYQ_MAX_STEM_CHARS + 100)
        text = self.g._format_pyq_examples([_make_pyq(stem=long_stem)])
        self.assertIn("a" * self.g.PYQ_MAX_STEM_CHARS + "…", text)
        self.assertNotIn("a" * (self.g.PYQ_MAX_STEM_CHARS + 1), text)

    def test_nat_question_renders_without_options_line(self) -> None:
        nat = _make_pyq(options=None, question_type="NAT")
        text = self.g._format_pyq_examples([nat])
        self.assertIn("[PYQ 1]", text)
        self.assertNotIn("Options:", text)

    def test_dict_options_rendered_by_sorted_letter_keys(self) -> None:
        pyq = _make_pyq(options={"B": "two", "A": "one"})
        text = self.g._format_pyq_examples([pyq])
        self.assertIn("Options: (A) one  (B) two", text)


class PyqAttachTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.g = _load_question_generator_isolated()

    def test_keys_specs_to_scope_and_marks_buckets(self) -> None:
        pool = {
            ("GA", 1): [_make_pyq(stem="GA-ONE-MARK-STEM", marks=1)],
            ("Subject", 2): [_make_pyq(stem="SUBJ-TWO-MARK-STEM", marks=2)],
        }
        ga_spec = {"is_ga": True, "marks": 1}
        subj_spec = {"is_ga": False, "marks": 2}
        miss_spec = {"is_ga": False, "marks": 1}  # bucket absent from pool

        self.g._attach_pyq_examples([ga_spec, subj_spec, miss_spec], pool)

        self.assertIn("GA-ONE-MARK-STEM", ga_spec["pyq_examples"])
        self.assertIn("SUBJ-TWO-MARK-STEM", subj_spec["pyq_examples"])
        self.assertEqual(miss_spec["pyq_examples"], "")

    def test_empty_pool_attaches_empty_string_everywhere(self) -> None:
        specs = [{"is_ga": True, "marks": 1}, {"is_ga": False, "marks": 2}]
        self.g._attach_pyq_examples(specs, {})
        for spec in specs:
            self.assertEqual(spec["pyq_examples"], "")


class PromptTemplateTests(unittest.TestCase):
    """Lock the template contract: {pyq_examples} exists, and .format() with the
    exact kwarg sets used by _generate_one_batch resolves every placeholder —
    including when the injected value itself contains literal braces."""

    BRACED_VALUE = (
        "REFERENCE block with set notation $\\{1, 2, 3\\}$ and braces {not a key}"
    )

    @staticmethod
    def _load(filename: str) -> dict:
        with open(PROMPTS_DIR / filename, encoding="utf-8") as f:
            return json.load(f)

    def test_batch_template_has_placeholder_and_formats(self) -> None:
        template = self._load("generate_batch.json")
        self.assertIn("{pyq_examples}", template["user_prompt_template"])
        for value in ("", self.BRACED_VALUE):
            rendered = template["user_prompt_template"].format(
                count=5,
                paper="CS",
                paper_full_name="Computer Science and Information Technology",
                section_name="Algorithms",
                difficulty="medium",
                question_specs="1. MCQ, 1 mark(s)",
                topics_list="- Sorting",
                pyq_examples=value,
            )
            self.assertIn(value, rendered)

    def test_ga_template_has_placeholder_and_formats(self) -> None:
        template = self._load("generate_ga.json")
        self.assertIn("{pyq_examples}", template["user_prompt_template"])
        for value in ("", self.BRACED_VALUE):
            rendered = template["user_prompt_template"].format(
                count=5,
                marks=1,
                difficulty="easy",
                topics_list="- Verbal Aptitude",
                pyq_examples=value,
            )
            self.assertIn(value, rendered)


class GenerateOneBatchPassThroughTests(unittest.TestCase):
    """spec["pyq_examples"] must reach the LLM user prompt; specs built without
    the key (e.g. older tests) must keep working via the .get("", ...) default."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.g = _load_question_generator_isolated()

    def _run_batch(self, spec: dict) -> str:
        captured: dict[str, str] = {}

        async def fake_call_llm(system_prompt: str, user_prompt: str, **kwargs):
            captured["user_prompt"] = user_prompt
            return "[]"

        with patch.object(self.g, "call_llm", fake_call_llm):
            result = asyncio.run(self.g._generate_one_batch(spec))
        self.assertEqual(result, [])
        return captured["user_prompt"]

    def test_pyq_examples_value_appears_in_user_prompt(self) -> None:
        spec = {
            "is_ga": False,
            "paper": "CS",
            "section_name": "Algorithms",
            "marks": 2,
            "count": 1,
            "difficulty": "hard",
            "types": {"MCQ": 1},
            "topics": ["Graph algorithms"],
            "pyq_examples": "MARKER-123",
        }
        self.assertIn("MARKER-123", self._run_batch(spec))

    def test_spec_without_pyq_examples_key_still_works(self) -> None:
        spec = {
            "is_ga": True,
            "section_name": "General Aptitude",
            "marks": 1,
            "count": 1,
            "difficulty": "easy",
            "types": {"MCQ": 1},
            "topics": ["Verbal Aptitude"],
        }
        prompt = self._run_batch(spec)
        self.assertNotIn("MARKER-123", prompt)
        self.assertNotIn("{pyq_examples}", prompt)


if __name__ == "__main__":
    unittest.main()
