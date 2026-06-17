"""Tests for exam question reference resolution."""

from types import SimpleNamespace

from app.services.exam_question_refs import lookup_response, resolve_exam_question_refs


def _exam(**kwargs):
    return SimpleNamespace(
        id="exam-1",
        question_order=kwargs.get("question_order", []),
        question_ids=kwargs.get("question_ids", []),
    )


def test_merge_empty_question_id_from_question_ids_by_index():
    exam = _exam(
        question_order=[
            {"qno": 1, "question_id": "aaa", "section": "GA"},
            {"qno": 2, "question_id": "", "section": "GA"},
            {"qno": 3, "question_id": "ccc", "section": "Subject"},
        ],
        question_ids=["aaa", "bbb", "ccc"],
    )
    refs = resolve_exam_question_refs(exam)
    assert [r["question_id"] for r in refs] == ["aaa", "bbb", "ccc"]
    assert refs[1]["section"] == "GA"


def test_fallback_to_question_ids_when_order_empty():
    exam = _exam(question_order=[], question_ids=["x1", "x2"])
    refs = resolve_exam_question_refs(exam)
    assert len(refs) == 2
    assert refs[0]["question_id"] == "x1"


def test_lookup_response_case_insensitive():
    responses = {"550E8400-E29B-41D4-A716-446655440000": {"index": 1}}
    assert lookup_response(responses, "550e8400-e29b-41d4-a716-446655440000") == {"index": 1}
