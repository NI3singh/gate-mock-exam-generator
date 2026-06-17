"""Tests for tex_sanitize helpers."""

from app.services.tex_sanitize import (
    repair_json_escape_corruption,
    sanitize_question_fields,
    sanitize_tex_field,
    unescape_literal_newlines,
)


def test_repair_json_escape_corruption():
    corrupted = "forall x (" + "\t" + "ext{Bird}(x))"
    fixed = repair_json_escape_corruption(corrupted)
    assert "\\text{Bird}" in fixed


def test_unescape_literal_newlines_in_solution():
    sol = "Step 1.\\nStep 2."
    fixed = unescape_literal_newlines(sol)
    assert "\nStep 2." in fixed
    assert "\\neq" in unescape_literal_newlines("$x \\neq 0$")


def test_sanitize_question_fields():
    q = {
        "stem_tex": "Find " + "\t" + "ext{value}?",
        "solution_tex": "Answer.\\nDone.",
        "choices": ["A", "B", "C", "D"],
    }
    cleaned = sanitize_question_fields(q)
    assert "\\text{value}" in cleaned["stem_tex"]
    assert "\nDone." in cleaned["solution_tex"]
    assert cleaned["choices"] == ["A", "B", "C", "D"]


def test_sanitize_tex_field_empty():
    assert sanitize_tex_field(None) == ""
    assert sanitize_tex_field("") == ""
