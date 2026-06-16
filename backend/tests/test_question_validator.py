"""Tests for aligned batch validation and deficit slot tracking."""

from app.services.question_validator import (
    slot_spec_from_batch,
    validate_batch_aligned,
    validate_question_for_slot,
)

BATCH_SPEC = {
    "section_name": "Programming",
    "paper": "CS",
    "is_ga": False,
    "topics": ["Recursion", "Closures"],
    "marks": 2,
    "count": 3,
    "types": {"MCQ": 2, "MSQ": 1},
    "question_slots": ["MCQ", "MSQ", "MCQ"],
    "difficulty": "medium",
}


def _valid_mcq(index: int = 0) -> dict:
    return {
        "stem_tex": "What is the output of the following Python snippet?",
        "code_snippet": "print(1 + 1)",
        "code_language": "python",
        "choices": ["1", "2", "3", "4"],
        "answer": {"index": index},
        "question_type": "MCQ",
        "marks": 2,
        "difficulty": "medium",
        "difficulty_score": 0.5,
        "section_name": "Programming",
        "topic": "Recursion",
        "estimated_time_seconds": 120,
        "solution_tex": "The expression evaluates to 2, so option B is correct.",
    }


def _valid_msq() -> dict:
    q = _valid_mcq()
    q["question_type"] = "MSQ"
    q["answer"] = {"indices": [0, 2]}
    return q


def test_validate_batch_aligned_accepts_matching_slots():
    valid, failed = validate_batch_aligned(
        [_valid_mcq(1), _valid_msq(), _valid_mcq(0)],
        BATCH_SPEC,
    )
    assert len(valid) == 3
    assert failed == []


def test_validate_batch_aligned_rejects_wrong_type():
    wrong = _valid_mcq()
    wrong["question_type"] = "NAT"
    wrong["choices"] = None
    wrong["answer"] = {"value": 2.0, "tolerance": 0.01}

    valid, failed = validate_batch_aligned([wrong], BATCH_SPEC)
    assert valid == []
    assert len(failed) == 3
    assert failed[0]["question_type"] == "MCQ"


def test_validate_batch_aligned_tracks_missing_output():
    valid, failed = validate_batch_aligned([_valid_mcq()], BATCH_SPEC)
    assert len(valid) == 1
    assert len(failed) == 2
    assert failed[0]["question_type"] == "MSQ"
    assert failed[1]["question_type"] == "MCQ"


def test_validate_question_for_slot_checks_marks():
    q = _valid_mcq()
    q["marks"] = 1
    ok, msg = validate_question_for_slot(q, "MCQ", 2)
    assert not ok
    assert "1 mark" in msg or "Expected 2" in msg


def test_slot_spec_from_batch_preserves_syllabus_context():
    slot = slot_spec_from_batch(BATCH_SPEC, "NAT")
    assert slot["section_name"] == "Programming"
    assert slot["topics"] == ["Recursion", "Closures"]
    assert slot["marks"] == 2
    assert slot["question_type"] == "NAT"
