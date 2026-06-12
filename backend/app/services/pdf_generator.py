"""
PDF generator for GATE 2027 result sheets.

Requires: pip install weasyprint
  (or pip install fpdf2 as a fallback)

If weasyprint is not available, raises ValueError with installation instructions.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.attempt import Attempt
from app.models.exam import Exam
from app.models.question_bank import QuestionBank

# Try weasyprint first, fall back to nothing (raises ImportError)
try:
    from weasyprint import HTML as WeasyHTML  # type: ignore
    _PDF_ENGINE = "weasyprint"
except ImportError:
    _PDF_ENGINE = None


def _build_html(result: dict) -> str:
    """
    Build a self-contained HTML string from the attempt result dict.
    """
    score = result.get("score", 0)
    max_score = result.get("max_score", 100)
    percentage = round((score / max_score) * 100, 1) if max_score else 0

    section_scores = result.get("section_scores", {})
    topic_analysis = result.get("topic_analysis", [])
    violations = result.get("violations", [])
    solutions = result.get("solutions", [])

    # Section breakdown rows
    section_rows = ""
    for section, data in section_scores.items():
        pct = round((data.get("score", 0) / data.get("max_score", 1)) * 100, 1) if data.get("max_score") else 0
        section_rows += f"""
        <tr>
            <td>{'General Aptitude' if section == 'GA' else 'Subject'}</td>
            <td>{data.get('correct', 0)}</td>
            <td>{data.get('wrong', 0)}</td>
            <td>{data.get('unanswered', 0)}</td>
            <td>{data.get('score', 0):.2f} / {data.get('max_score', 0)}</td>
            <td>{pct}%</td>
        </tr>"""

    # Violation rows
    violation_rows = ""
    if violations:
        for v in violations:
            violation_rows += f"<tr><td>{v['event_type']}</td><td>{v['count']}</td></tr>"
    else:
        violation_rows = "<tr><td colspan='2' style='color:green'>No violations</td></tr>"

    # Topic analysis rows
    topic_rows = ""
    for item in topic_analysis:
        accuracy = round((item.get("correct", 0) / item.get("total", 1)) * 100, 1) if item.get("total") else 0
        topic_rows += f"""
        <tr>
            <td>{item.get('topic', '')}</td>
            <td>{item.get('section_name', '')}</td>
            <td>{item.get('total', 0)}</td>
            <td>{item.get('correct', 0)}</td>
            <td>{item.get('wrong', 0)}</td>
            <td>{item.get('unanswered', 0)}</td>
            <td>{accuracy}%</td>
            <td>{item.get('score', 0):.2f} / {item.get('max_score', 0)}</td>
        </tr>"""

    # Solutions (first 10 as preview)
    solution_rows = ""
    for sol in solutions[:10]:
        status_icon = "✓" if sol["is_correct"] else ("—" if sol["user_answer"] is None else "✗")
        status_color = "#22c55e" if sol["is_correct"] else ("#9ca3af" if sol["user_answer"] is None else "#ef4444")
        solution_rows += f"""
        <tr>
            <td>Q{sol['qno']}</td>
            <td>{sol['question_type']}</td>
            <td>{sol['marks']}M</td>
            <td style="color:{status_color};font-weight:bold">{status_icon}</td>
            <td>{sol['score']:.2f}</td>
            <td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{sol.get('stem_tex', '')[:80]}</td>
        </tr>"""
    if len(solutions) > 10:
        solution_rows += f"<tr><td colspan='6' style='color:#9ca3af;text-align:center'>...and {len(solutions) - 10} more questions</td></tr>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>GATE 2027 — Result Sheet</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #1a1a2e; background: #f8fafc; }}
  .container {{ max-width: 900px; margin: 20px auto; background: white; border-radius: 12px; padding: 32px; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }}
  h1 {{ font-size: 22px; font-weight: 900; color: #1e3a8a; text-align: center; margin-bottom: 4px; }}
  .subtitle {{ text-align: center; color: #64748b; font-size: 12px; margin-bottom: 28px; letter-spacing: 0.5px; text-transform: uppercase; }}
  .score-hero {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; border-radius: 12px; padding: 28px; text-align: center; margin-bottom: 28px; }}
  .score-hero .big {{ font-size: 56px; font-weight: 900; line-height: 1; }}
  .score-hero .max {{ font-size: 24px; opacity: 0.7; font-weight: 300; }}
  .score-hero .pct {{ font-size: 20px; opacity: 0.9; margin-top: 6px; }}
  .badges {{ display: flex; gap: 12px; justify-content: center; margin-top: 12px; flex-wrap: wrap; }}
  .badge {{ background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; font-size: 12px; }}
  .score-badges {{ display: flex; gap: 16px; justify-content: center; margin-top: 14px; }}
  .score-badge {{ background: white; color: #1e3a8a; padding: 6px 16px; border-radius: 8px; font-weight: 700; font-size: 13px; }}
  .negative {{ color: #ef4444; font-size: 13px; margin-top: 8px; text-align: center; }}
  .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }}
  h2 {{ font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #64748b; margin-bottom: 12px; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  th {{ background: #f1f5f9; text-align: left; padding: 7px 10px; font-weight: 600; color: #475569; border-bottom: 2px solid #e2e8f0; }}
  td {{ padding: 7px 10px; border-bottom: 1px solid #f1f5f9; }}
  tr:hover {{ background: #fafafa; }}
  .full-width {{ margin-bottom: 24px; }}
  .footer {{ text-align: center; color: #94a3b8; font-size: 11px; margin-top: 28px; }}
  @media print {{ body {{ background: white; }} .container {{ box-shadow: none; border: 1px solid #e2e8f0; }} }}
</style>
</head>
<body>
<div class="container">
  <h1>GATE 2027 — Mock Test Result</h1>
  <p class="subtitle">{result.get('paper', '')} &nbsp;·&nbsp; {result.get('difficulty', '').capitalize()} &nbsp;·&nbsp; {result.get('total_questions', 0)} Questions &nbsp;·&nbsp; {result.get('total_marks', 0)} Marks</p>

  <!-- Score Hero -->
  <div class="score-hero">
    <div class="big">{score:.2f}<span class="max">/{max_score}</span></div>
    <div class="pct">{percentage}%</div>
    <div class="score-badges">
      <div class="score-badge">✓ {result.get('total_correct', 0)} Correct</div>
      <div class="score-badge">✗ {result.get('total_wrong', 0)} Wrong</div>
      <div class="score-badge">— {result.get('total_unanswered', 0)} Unanswered</div>
    </div>
    {f"<div class='negative'>−{result.get('negative_marks', 0):.2f} marks deducted (negative marking)</div>" if result.get('negative_marks', 0) > 0 else ""}
  </div>

  <!-- Section & Violations -->
  <div class="two-col">
    <div>
      <h2>Section Breakdown</h2>
      <table>
        <thead><tr><th>Section</th><th>✓</th><th>✗</th><th>—</th><th>Score</th><th>%</th></tr></thead>
        <tbody>{section_rows}</tbody>
      </table>
    </div>
    <div>
      <h2>Anti-Cheat Violations</h2>
      <table>
        <thead><tr><th>Event Type</th><th>Count</th></tr></thead>
        <tbody>{violation_rows}</tbody>
      </table>
    </div>
  </div>

  <!-- Topic Analysis -->
  <div class="full-width">
    <h2>Topic Analysis</h2>
    <table>
      <thead><tr><th>Topic</th><th>Section</th><th>Total</th><th>✓</th><th>✗</th><th>—</th><th>Accuracy</th><th>Score</th></tr></thead>
      <tbody>{topic_rows}</tbody>
    </table>
  </div>

  <!-- Solutions Preview -->
  <div class="full-width">
    <h2>Solutions Preview (First 10 Questions)</h2>
    <table>
      <thead><tr><th>#</th><th>Type</th><th>Marks</th><th>Status</th><th>Score</th><th>Question Snippet</th></tr></thead>
      <tbody>{solution_rows}</tbody>
    </table>
  </div>

  <p class="footer">Generated by GATE 2027 Mock Test Platform · {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>
</body>
</html>"""


async def generate_result_pdf(
    db: AsyncSession, attempt_id: str, user_id: UUID
) -> bytes:
    """
    Fetches attempt data and returns a PDF bytes object.
    Raises ValueError if the attempt is not found or not owned by user.
    """
    if _PDF_ENGINE is None:
        raise ValueError(
            "weasyprint is not installed. Run: pip install weasyprint "
            "(Note: on Windows you may also need: pip install weasyprint[windows])"
        )

    # Fetch attempt
    result = await db.execute(
        select(Attempt).where(
            Attempt.id == attempt_id,
            Attempt.user_id == user_id,
        )
    )
    attempt: Attempt | None = result.scalar_one_or_none()
    if attempt is None:
        raise ValueError("Attempt not found.")

    # Fetch exam
    exam_result = await db.execute(select(Exam).where(Exam.id == attempt.exam_id))
    exam: Exam | None = exam_result.scalar_one_or_none()
    if exam is None:
        raise ValueError("Exam not found.")

    # Build result dict (reuse AttemptDetailResponse data)
    section_scores = attempt.score_breakdown.get("section", {}) if attempt.score_breakdown else {}
    topic_analysis = attempt.topic_analysis or []

    # Group violations
    events_log: list[dict] = list(attempt.events_log or [])
    violation_map: dict[str, int] = {}
    for evt in events_log:
        evt_type = evt.get("event_type", "unknown")
        violation_map[evt_type] = violation_map.get(evt_type, 0) + 1
    violations = [{"event_type": k, "count": v} for k, v in sorted(violation_map.items())]

    # Compute negative marks
    negative_marks = 0.0
    if attempt.responses:
        # question_order is stored as list[dict]; extract the UUID strings.
        question_ids: list[str] = [
            entry["question_id"]
            for entry in (exam.question_order or [])
            if isinstance(entry, dict) and entry.get("question_id")
        ]
        q_result = await db.execute(
            select(QuestionBank).where(QuestionBank.id.in_(question_ids))
        )
        questions: list[QuestionBank] = q_result.scalars().all()
        question_map: dict[str, QuestionBank] = {str(q.id): q for q in questions}
        responses: dict = attempt.responses or {}

        for q_id in question_ids:
            q = question_map.get(q_id)
            if q is None or q.question_type != "MCQ":
                continue
            user_answer = responses.get(q_id)
            if user_answer and user_answer.get("index") != q.answer.get("index"):
                negative_marks += round(q.marks / 3, 6)

    result_dict = {
        "paper": exam.paper,
        "difficulty": exam.difficulty,
        "total_questions": exam.total_questions,
        "total_marks": exam.total_marks,
        "score": round(attempt.score or 0.0, 2),
        "max_score": attempt.max_score,
        "total_correct": attempt.total_correct or 0,
        "total_wrong": attempt.total_wrong or 0,
        "total_unanswered": attempt.total_unanswered or 0,
        "negative_marks": round(negative_marks, 2),
        "section_scores": section_scores,
        "topic_analysis": topic_analysis,
        "violations": violations,
        "solutions": [],  # Not included in PDF for brevity
    }

    html_string = _build_html(result_dict)

    if _PDF_ENGINE == "weasyprint":
        pdf_bytes = WeasyHTML(string=html_string).write_pdf()
        return pdf_bytes

    # Should not reach here
    raise ValueError("No PDF engine available.")