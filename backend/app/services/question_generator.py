"""
Main orchestrator for exam question generation.

Flow:
  1. Load exam config from DB
  2. Load syllabus topics
  3. Calculate question distribution → list of batch specs
  4. For each batch: call LLM → parse → validate → collect
  5. Store valid questions in question_bank
  6. Assemble 65-question exam
  7. Update exam row with question_ids, question_order, status
"""

import asyncio
import json
import logging
import math
import random
import time
import uuid
from pathlib import Path

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.core.llm_config import (
    GA_1MARK,
    GA_2MARK,
    SUBJECT_1MARK,
    SUBJECT_2MARK,
    GATE_TOTAL_QUESTIONS,
)
from app.models.exam import Exam
from app.models.syllabus import Syllabus
from app.models.question_bank import QuestionBank
from app.models.pyq_question import PYQuestion
from app.services.llm_service import (
    call_llm,
    extract_json_array,
    get_active_llm_metadata,
)
from app.services.question_validator import validate_batch
from app.services.exam_assembler import assemble_exam, compute_marks_summary

logger = logging.getLogger(__name__)

# ── Load prompt templates ──
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

def _load_prompt(filename: str) -> dict:
    filepath = PROMPTS_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

_BATCH_PROMPT = _load_prompt("generate_batch.json")
_GA_PROMPT = _load_prompt("generate_ga.json")

PAPER_NAMES = {
    "CS": "Computer Science and Information Technology",
    "DA": "Data Science and Artificial Intelligence",
}

# Aggregate selection targets the assembler enforces. assemble_exam picks
# questions purely by (GA-vs-Subject, marks) — ignoring type/section for the
# counts — so the top-up loop only needs to satisfy these four buckets.
TARGETS: dict[tuple[str, int], int] = {
    ("GA", 1): GA_1MARK,
    ("GA", 2): GA_2MARK,
    ("Subject", 1): SUBJECT_1MARK,
    ("Subject", 2): SUBJECT_2MARK,
}


# ──────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────

async def run_generation(exam_id: uuid.UUID) -> None:
    """
    Background task: generates all questions for an exam.
    Uses its own DB session (not the request session).

    Wrapped in a hard timeout so a hung provider can never leave the exam pinned
    in 'generating' forever; on timeout or any error the exam is marked failed.
    """
    async with AsyncSessionLocal() as db:
        try:
            await asyncio.wait_for(
                _do_generation(db, exam_id),
                timeout=settings.LLM_GEN_MAX_SECONDS,
            )
        except asyncio.TimeoutError:
            logger.error(
                "Exam generation timed out for %s after %ss",
                exam_id,
                settings.LLM_GEN_MAX_SECONDS,
            )
            await _set_error(
                db,
                exam_id,
                f"Generation timed out after {settings.LLM_GEN_MAX_SECONDS}s. "
                "Please try again.",
            )
        except Exception as exc:
            logger.exception(f"Exam generation failed for {exam_id}: {exc}")
            await _set_error(db, exam_id, str(exc))


async def _do_generation(db: AsyncSession, exam_id: uuid.UUID) -> None:
    # ── 1. Load exam config ──
    exam = await db.get(Exam, exam_id)
    if exam is None:
        raise ValueError(f"Exam {exam_id} not found")

    logger.info(f"Starting generation for exam {exam_id} (paper={exam.paper})")

    # ── 2. Load syllabus topics ──
    subject_sections = await _load_syllabus_grouped(db, exam.paper)
    ga_sections = await _load_syllabus_grouped(db, "GA")

    if not subject_sections:
        raise ValueError(f"No syllabus data for paper {exam.paper}")
    if not ga_sections:
        raise ValueError("No syllabus data for GA")

    # Filter subject sections if scope is 'topic'
    if exam.scope == "topic" and exam.selected_topics:
        selected = set(exam.selected_topics)
        filtered = {}
        for sec_name, topics in subject_sections.items():
            matching = [t for t in topics if t in selected]
            if matching:
                filtered[sec_name] = matching
        if not filtered:
            raise ValueError("No matching sections for selected topics")
        subject_sections = filtered

    # ── 3. Build batch plan ──
    types_ratio = exam.types_ratio or {"MCQ": 0.6, "MSQ": 0.2, "NAT": 0.2}
    difficulty = exam.difficulty

    batches = _build_batch_plan(
        subject_sections=subject_sections,
        ga_sections=ga_sections,
        types_ratio=types_ratio,
        difficulty=difficulty,
        paper=exam.paper,
    )

    total_expected = sum(b["count"] for b in batches)
    logger.info(f"Batch plan: {len(batches)} batches, {total_expected} questions expected")

    # PYQ reference context: ONE serial prefetch on this session BEFORE the
    # concurrent fan-out (the session is not concurrency-safe). The pool is
    # reused by every top-up round — zero DB calls inside the loop. An empty
    # pool (no PYQs loaded / flag off) attaches "" and prompts are unchanged.
    pyq_pool: dict[tuple[str, int], list[dict]] = {}
    if exam.use_pyq_reference:
        pyq_pool = await _load_pyq_pool(db, exam.paper)
        logger.info(
            "PYQ reference pool: %s",
            {f"{scope}/{marks}m": len(rows) for (scope, marks), rows in pyq_pool.items()},
        )
    _attach_pyq_examples(batches, pyq_pool)

    # ── 4. Generate questions — concurrent first pass + self-healing top-up ──
    # Topic pools the top-up phase draws from to refill deficient buckets.
    all_ga_topics: list[str] = []
    for _topics in ga_sections.values():
        all_ga_topics.extend(_topics)
    subject_items = list(subject_sections.items())

    all_questions: list[dict] = []

    # Phase 0: fire every planned batch concurrently. Real concurrency is bounded
    # by the semaphore inside llm_service.call_llm (LLM_MAX_CONCURRENCY); the
    # consumer drains results one-at-a-time so the single DB session is only ever
    # touched by one coroutine.
    phase0_tasks = [asyncio.create_task(_wrap(spec)) for spec in batches]
    new_valid = await _consume_and_collect(
        db, exam, phase0_tasks, len(phase0_tasks), "round 1", 0
    )
    all_questions.extend(_dedup_against(all_questions, new_valid))

    # Top-up: refill ONLY the (scope, marks) buckets that fell short, until every
    # bucket is satisfied, OR a round adds nothing new (stuck model), OR the round
    # / time budget is exhausted. run_generation's wait_for is the hard backstop.
    deadline = time.monotonic() + settings.LLM_TOPUP_TIME_BUDGET_SECONDS
    rr = [0]  # mutable round-robin cursor across subject sections
    for round_no in range(2, 2 + settings.LLM_TOPUP_MAX_ROUNDS):
        deficits = _deficits(all_questions)
        if sum(deficits.values()) == 0:
            break  # first pass already covered every bucket — zero extra calls
        if time.monotonic() >= deadline:
            logger.warning("Top-up time budget exhausted; deficits=%s", deficits)
            break

        specs: list[dict] = []
        for (scope, marks), deficit in deficits.items():
            if deficit <= 0:
                continue
            if scope == "Subject" and not subject_items:
                continue  # topic-scope removed all subjects; can't refill these
            specs.extend(
                _topup_specs(
                    scope, marks, deficit, types_ratio, difficulty,
                    exam.paper, all_ga_topics, subject_items, rr,
                )
            )
        if not specs:
            break
        _attach_pyq_examples(specs, pyq_pool)

        before = len(all_questions)
        topup_tasks = [asyncio.create_task(_wrap(spec)) for spec in specs]
        new_valid = await _consume_and_collect(
            db, exam, topup_tasks, len(topup_tasks),
            f"round {round_no}", len(all_questions),
        )
        all_questions.extend(_dedup_against(all_questions, new_valid))

        if len(all_questions) == before:
            logger.warning(
                "Top-up round %s produced 0 new questions; stopping early.",
                round_no,
            )
            break

    logger.info(
        "Generation done: %s valid questions (deficits=%s)",
        len(all_questions),
        _deficits(all_questions),
    )

    if len(all_questions) < 20:
        raise ValueError(
            f"Only generated {len(all_questions)} valid questions — "
            "not enough to assemble an exam. Check LLM configuration."
        )

    # ── 5. Store questions in question_bank ──
    stored_ids = await _store_questions(db, all_questions, exam)

    # Tag each question dict with its stored UUID BEFORE assembly.
    # stored_ids[i] corresponds to all_questions[i] by position (see
    # _store_questions). assemble_exam reads this "_stored_id" off each
    # selected dict, so every question_order entry comes out with the correct
    # question_id — no positional post-fix required.
    for i, q in enumerate(all_questions):
        q["_stored_id"] = str(stored_ids[i])

    # ── 6. Assemble exam ──
    question_order, _selected = assemble_exam(all_questions, exam.paper)

    summary = compute_marks_summary(question_order)
    logger.info(f"Exam assembled: {summary}")

    # ── 7. Update exam row ──
    # question_ids = ordered list of UUID strings matching question_order
    exam.question_ids = [entry["question_id"] for entry in question_order]
    exam.question_order = question_order
    # Reconcile the headline totals with what was actually assembled. If
    # generation fell short of the standard 65 questions / 100 marks, scoring
    # and percentages must use the real totals, not the optimistic defaults.
    exam.total_questions = summary["total_questions"]
    exam.total_marks = summary["total_marks"]
    exam.status = "generated"
    # Fresh dict on success: no stale 'batch'/'error' keys leak through (the
    # frontend flips to FAILED on any truthy 'error'), and 'failed' carries only
    # a REAL shortfall so the "fewer questions" note shows only when warranted.
    assembled = len(question_order)
    exam.generation_progress = {
        "total": GATE_TOTAL_QUESTIONS,
        "completed": assembled,
        "failed": max(0, GATE_TOTAL_QUESTIONS - assembled),
    }
    await db.commit()

    logger.info(f"Exam {exam_id} generation complete — status: generated")


# ──────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────

async def _load_syllabus_grouped(
    db: AsyncSession, paper: str
) -> dict[str, list[str]]:
    """Load syllabus topics grouped by section_name."""
    result = await db.execute(
        select(Syllabus.section_name, Syllabus.topic)
        .where(Syllabus.paper == paper)
        .order_by(Syllabus.section_name, Syllabus.id)
    )
    rows = result.fetchall()

    grouped: dict[str, list[str]] = {}
    for section_name, topic in rows:
        grouped.setdefault(section_name, []).append(topic)
    return grouped


def _build_batch_plan(
    subject_sections: dict[str, list[str]],
    ga_sections: dict[str, list[str]],
    types_ratio: dict[str, float],
    difficulty: str,
    paper: str,
) -> list[dict]:
    """
    Create a list of batch specifications.
    Each batch = one LLM call producing up to 5 questions.
    """
    batches: list[dict] = []

    # ── GA batches ──
    all_ga_topics = []
    for topics in ga_sections.values():
        all_ga_topics.extend(topics)

    batches.append({
        "section_name": "General Aptitude",
        "paper": paper,
        "is_ga": True,
        "topics": all_ga_topics,
        "marks": 1,
        "count": GA_1MARK,
        "types": {"MCQ": GA_1MARK},
        "difficulty": difficulty if difficulty != "auto" else "easy",
    })
    batches.append({
        "section_name": "General Aptitude",
        "paper": paper,
        "is_ga": True,
        "topics": all_ga_topics,
        "marks": 2,
        "count": GA_2MARK,
        "types": {"MCQ": GA_2MARK},
        "difficulty": difficulty if difficulty != "auto" else "medium",
    })

    # ── Subject batches ──
    num_sections = len(subject_sections)
    if num_sections == 0:
        return batches

    # Distribute 55 questions across sections
    base = SUBJECT_1MARK + SUBJECT_2MARK  # 55
    per_section = base // num_sections
    remainder = base % num_sections

    section_list = list(subject_sections.items())

    # Distribute 1-mark and 2-mark across sections
    remaining_1m = SUBJECT_1MARK  # 25
    remaining_2m = SUBJECT_2MARK  # 30

    for i, (sec_name, topics) in enumerate(section_list):
        total_for_section = per_section + (1 if i < remainder else 0)

        # Split into 1-mark and 2-mark proportionally
        sec_1m = round(total_for_section * SUBJECT_1MARK / base)
        sec_2m = total_for_section - sec_1m

        # Clamp to remaining
        sec_1m = min(sec_1m, remaining_1m)
        sec_2m = min(sec_2m, remaining_2m)

        # If we under-allocated, adjust
        if sec_1m + sec_2m < total_for_section:
            diff = total_for_section - sec_1m - sec_2m
            if remaining_1m - sec_1m >= diff:
                sec_1m += diff
            else:
                sec_2m += diff

        remaining_1m -= sec_1m
        remaining_2m -= sec_2m

        # Determine types for this section's questions
        for marks_val, count in [(1, sec_1m), (2, sec_2m)]:
            if count == 0:
                continue

            types_dist = _distribute_types(count, types_ratio)
            diff_level = _pick_difficulty(difficulty, marks_val)

            # Split into batches of max 5
            specs_for_batch = _build_question_specs(types_dist, marks_val)

            for chunk_start in range(0, len(specs_for_batch), 5):
                chunk = specs_for_batch[chunk_start : chunk_start + 5]
                type_counts: dict[str, int] = {}
                for s in chunk:
                    type_counts[s] = type_counts.get(s, 0) + 1

                batches.append({
                    "section_name": sec_name,
                    "paper": paper,
                    "is_ga": False,
                    "topics": topics,
                    "marks": marks_val,
                    "count": len(chunk),
                    "types": type_counts,
                    "difficulty": diff_level,
                })

    return batches


def _distribute_types(count: int, ratio: dict[str, float]) -> dict[str, int]:
    """Distribute `count` questions across MCQ/MSQ/NAT based on ratio."""
    mcq = round(count * ratio.get("MCQ", 0.6))
    msq = round(count * ratio.get("MSQ", 0.2))
    nat = count - mcq - msq  # remainder goes to NAT

    # Ensure no negatives
    if nat < 0:
        nat = 0
        msq = count - mcq

    return {"MCQ": mcq, "MSQ": msq, "NAT": nat}


def _build_question_specs(types_dist: dict[str, int], marks: int) -> list[str]:
    """Build a flat list of type strings, e.g., ['MCQ', 'MCQ', 'MSQ', 'NAT']."""
    specs: list[str] = []
    for qtype, count in types_dist.items():
        specs.extend([qtype] * count)
    return specs


def _pick_difficulty(difficulty: str, marks: int) -> str:
    """Pick difficulty for a batch."""
    if difficulty != "auto":
        return difficulty
    # Auto: 1-mark tends easier, 2-mark tends harder
    return "medium" if marks == 1 else "hard"


async def _generate_one_batch(batch_spec: dict) -> list[dict]:
    """Generate one batch of questions via LLM."""
    is_ga = batch_spec["is_ga"]
    prompt_template = _GA_PROMPT if is_ga else _BATCH_PROMPT

    # Build the question specs text
    specs_lines = []
    idx = 1
    for qtype, count in batch_spec["types"].items():
        for _ in range(count):
            specs_lines.append(f"{idx}. {qtype}, {batch_spec['marks']} mark(s)")
            idx += 1

    question_specs = "\n".join(specs_lines)

    # Build topics list
    topics_list = "\n".join(f"- {t}" for t in batch_spec["topics"])

    # Format user prompt
    if is_ga:
        user_prompt = prompt_template["user_prompt_template"].format(
            count=batch_spec["count"],
            marks=batch_spec["marks"],
            difficulty=batch_spec["difficulty"],
            topics_list=topics_list,
            pyq_examples=batch_spec.get("pyq_examples", ""),
        )
    else:
        user_prompt = prompt_template["user_prompt_template"].format(
            count=batch_spec["count"],
            paper=batch_spec["paper"],
            paper_full_name=PAPER_NAMES.get(batch_spec["paper"], batch_spec["paper"]),
            section_name=batch_spec["section_name"],
            difficulty=batch_spec["difficulty"],
            question_specs=question_specs,
            topics_list=topics_list,
            pyq_examples=batch_spec.get("pyq_examples", ""),
        )

    system_prompt = prompt_template["system_prompt"]

    # Call LLM
    raw_response = await call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=settings.LLM_TEMPERATURE,
    )

    # Parse JSON
    questions = extract_json_array(raw_response)

    # Ensure section_name is set correctly
    for q in questions:
        if is_ga:
            q["section_name"] = "General Aptitude"
        elif not q.get("section_name"):
            q["section_name"] = batch_spec["section_name"]

    return questions


async def _wrap(
    spec: dict,
) -> tuple[dict, list[dict] | None, Exception | None]:
    """Run one batch, returning (spec, raw, exc) and NEVER raising.

    This keeps a failed future from aborting the as_completed consumer and
    preserves which spec failed (as_completed loses that association).
    """
    try:
        return spec, await _generate_one_batch(spec), None
    except Exception as exc:  # noqa: BLE001 — captured to report, not swallowed
        return spec, None, exc


async def _consume_and_collect(
    db: AsyncSession,
    exam: Exam,
    tasks: list,
    total: int,
    label: str,
    completed_so_far: int,
) -> list[dict]:
    """Drain in-flight batch tasks (created via _wrap) one-at-a-time, validating
    and tagging each result and committing interim progress after each.

    Single-consumer by design: the gathered tasks touch no DB session and this
    loop awaits commits serially, so the one AsyncSession is never used
    concurrently. Returns the validated (not-yet-deduped) questions.
    """
    collected: list[dict] = []
    done = 0
    for fut in asyncio.as_completed(tasks):
        done += 1
        spec, raw, exc = await fut
        if exc is not None or raw is None:
            logger.error("Batch failed in %s: %s", label, exc)
        else:
            valid = validate_batch(raw, expected_section=spec["section_name"])
            for q in valid:
                q["_paper"] = exam.paper if spec["is_ga"] is False else "GA"
            collected.extend(valid)

        running = completed_so_far + len(collected)
        exam.generation_progress = {
            "total": GATE_TOTAL_QUESTIONS,
            "completed": min(running, GATE_TOTAL_QUESTIONS),
            "failed": 0,  # interim only; the real shortfall is set once at the end
            "batch": f"{label} {done}/{total}",
        }
        await db.commit()
    return collected


def _bucket_counts(pool: list[dict]) -> dict[tuple[str, int], int]:
    """Count questions per (scope, marks) bucket, mirroring assemble_exam."""
    counts: dict[tuple[str, int], int] = {key: 0 for key in TARGETS}
    for q in pool:
        scope = "GA" if q.get("section_name") == "General Aptitude" else "Subject"
        key = (scope, q.get("marks"))
        if key in counts:
            counts[key] += 1
    return counts


def _deficits(pool: list[dict]) -> dict[tuple[str, int], int]:
    """How many more questions each bucket needs to reach its target."""
    counts = _bucket_counts(pool)
    return {key: max(0, TARGETS[key] - counts[key]) for key in TARGETS}


def _normalize_stem(stem: str) -> str:
    """Whitespace/case-normalized stem text, for duplicate detection."""
    return " ".join((stem or "").split()).lower()


def _dedup_against(existing: list[dict], new: list[dict]) -> list[dict]:
    """Return items of `new` whose normalized stem is not already present in
    `existing` nor earlier within `new` (dedups across AND within rounds)."""
    seen = {_normalize_stem(q.get("stem_tex", "")) for q in existing}
    fresh: list[dict] = []
    for q in new:
        key = _normalize_stem(q.get("stem_tex", ""))
        if not key or key in seen:
            continue
        seen.add(key)
        fresh.append(q)
    return fresh


# ── PYQ reference context ──
# Real previous-year questions are injected into generation prompts as style /
# difficulty calibration only (never shown to students, never copied). Pool is
# keyed by the same (scope, marks) buckets as TARGETS.

PYQ_POOL_PER_BUCKET = 12    # rows fetched per bucket in the one-shot prefetch
PYQ_EXAMPLES_PER_BATCH = 3  # examples injected per LLM call
PYQ_MAX_STEM_CHARS = 600    # stems are truncated to bound prompt size


async def _load_pyq_pool(
    db: AsyncSession, paper: str
) -> dict[tuple[str, int], list[dict]]:
    """Prefetch a random sample of PYQs per (scope, marks) bucket.

    Called ONCE, serially, before the concurrent fan-out (the shared session is
    not concurrency-safe); rows are projected to plain dicts so later sampling
    never touches the session. GA questions appear inside every paper's PDF, so
    the GA buckets match on section_name across papers.
    """
    pool: dict[tuple[str, int], list[dict]] = {}
    for scope, marks in TARGETS:
        stmt = select(PYQuestion).where(PYQuestion.marks == marks)
        if scope == "GA":
            stmt = stmt.where(PYQuestion.section_name == "General Aptitude")
        else:
            stmt = stmt.where(
                PYQuestion.paper == paper,
                or_(
                    PYQuestion.section_name.is_(None),
                    PYQuestion.section_name != "General Aptitude",
                ),
            )
        stmt = stmt.order_by(func.random()).limit(PYQ_POOL_PER_BUCKET)
        result = await db.execute(stmt)
        pool[(scope, marks)] = [
            {
                "stem": row.stem,
                "options": row.options,
                "question_type": row.question_type,
                "marks": row.marks,
                "topic": row.topic,
                "year": row.year,
            }
            for row in result.scalars().all()
        ]
    return pool


def _format_pyq_options(options) -> str:
    """Render PYQ options (stored as list or letter-keyed dict) on one line."""
    if not options:
        return ""
    letters = "ABCDEFGH"
    if isinstance(options, dict):
        pairs = [f"({key}) {value}" for key, value in sorted(options.items())]
    elif isinstance(options, list):
        pairs = [
            f"({letters[i]}) {opt}" for i, opt in enumerate(options[: len(letters)])
        ]
    else:
        return ""
    return "Options: " + "  ".join(pairs)


def _format_pyq_examples(
    bucket: list[dict], k: int = PYQ_EXAMPLES_PER_BATCH
) -> str:
    """Render up to k sampled PYQs as a reference block for the user prompt.

    Returns "" for an empty bucket so the template's {pyq_examples} slot
    degrades to a blank line. The framing header lives here (in the formatted
    VALUE) rather than in the JSON template: str.format would choke on literal
    braces in template text, while braces inside a formatted value are safe.
    """
    if not bucket:
        return ""
    sample = random.sample(bucket, min(k, len(bucket)))
    lines = [
        "REFERENCE — REAL past GATE questions "
        "(STYLE AND DIFFICULTY CALIBRATION ONLY):",
        "Study the phrasing style, rigor, and difficulty of these examples. "
        "Your questions must be COMPLETELY ORIGINAL — do NOT copy, paraphrase, "
        "or reuse their scenarios or numbers.",
    ]
    for i, q in enumerate(sample, start=1):
        stem = " ".join((q.get("stem") or "").split())
        if len(stem) > PYQ_MAX_STEM_CHARS:
            stem = stem[:PYQ_MAX_STEM_CHARS].rstrip() + "…"
        lines.append("")
        lines.append(
            f"[PYQ {i}] (GATE {q.get('year')}, {q.get('question_type')}, "
            f"{q.get('marks')} marks, topic: {q.get('topic')})"
        )
        lines.append(stem)
        options_line = _format_pyq_options(q.get("options"))
        if options_line:
            lines.append(options_line)
    lines.append("")
    lines.append("END OF REFERENCE.")
    return "\n".join(lines)


def _attach_pyq_examples(
    specs: list[dict], pool: dict[tuple[str, int], list[dict]]
) -> None:
    """Set spec["pyq_examples"] on every batch spec (mutates in place).

    Re-samples from the bucket per spec, so different batches (and top-up
    rounds) see varied examples. An empty/missing bucket yields "".
    """
    for spec in specs:
        key = ("GA" if spec.get("is_ga") else "Subject", spec.get("marks"))
        spec["pyq_examples"] = _format_pyq_examples(pool.get(key, []))


def _topup_specs(
    scope: str,
    marks: int,
    deficit: int,
    types_ratio: dict[str, float],
    difficulty: str,
    paper: str,
    ga_topics: list[str],
    subject_items: list[tuple[str, list[str]]],
    rr: list[int],
) -> list[dict]:
    """Build batch specs to refill `deficit` questions for one (scope, marks)
    bucket, chunked to <=5 like _build_batch_plan. Subject deficits are spread
    round-robin across sections via the mutable cursor `rr`."""
    types_dist = _distribute_types(deficit, types_ratio)
    flat = _build_question_specs(types_dist, marks)
    diff_level = _pick_difficulty(difficulty, marks)

    specs: list[dict] = []
    for start in range(0, len(flat), 5):
        chunk = flat[start:start + 5]
        type_counts: dict[str, int] = {}
        for qtype in chunk:
            type_counts[qtype] = type_counts.get(qtype, 0) + 1

        if scope == "GA":
            sec_name, topics, is_ga = "General Aptitude", ga_topics, True
        else:
            sec_name, topics = subject_items[rr[0] % len(subject_items)]
            rr[0] += 1
            is_ga = False

        specs.append({
            "section_name": sec_name,
            "paper": paper,
            "is_ga": is_ga,
            "topics": topics,
            "marks": marks,
            "count": len(chunk),
            "types": type_counts,
            "difficulty": diff_level,
        })
    return specs


async def _store_questions(
    db: AsyncSession,
    questions: list[dict],
    exam: Exam,
) -> list[uuid.UUID]:
    """Store generated questions in the question_bank table."""
    stored_ids: list[uuid.UUID] = []
    llm_metadata = get_active_llm_metadata()

    for q in questions:
        qb = QuestionBank(
            id=uuid.uuid4(),
            paper=exam.paper if q.get("section_name") != "General Aptitude" else "GA",
            question_type=q["question_type"],
            marks=q["marks"],
            difficulty=q.get("difficulty", "medium"),
            difficulty_score=q.get("difficulty_score", 0.5),
            section_name=q["section_name"],
            topic=q.get("topic", "General"),
            stem_tex=q["stem_tex"],
            code_snippet=q.get("code_snippet"),
            code_language=q.get("code_language"),
            choices=q.get("choices"),
            answer=q["answer"],
            solution_tex=q["solution_tex"],
            estimated_time_seconds=q.get("estimated_time_seconds"),
            llm_provider=llm_metadata["provider"],
            llm_model=llm_metadata["model"],
            llm_prompt_version="1.0",
            validated=True,
        )
        db.add(qb)
        stored_ids.append(qb.id)

    await db.flush()
    return stored_ids


async def _set_error(db: AsyncSession, exam_id: uuid.UUID, error_msg: str) -> None:
    """Mark an exam generation as failed.

    Resilient to a poisoned/aborted session (e.g. a wait_for cancellation that
    landed on a DB await): roll back first, and if the write still fails, retry
    once on a fresh session so the exam can never be left stuck in 'generating'.
    """
    try:
        await db.rollback()
    except Exception:
        pass

    try:
        exam = await db.get(Exam, exam_id)
        if exam:
            exam.status = "failed"
            exam.generation_progress = {
                **(exam.generation_progress or {}),
                "error": error_msg,
            }
            await db.commit()
        return
    except Exception:
        logger.exception(
            "Primary _set_error write failed; retrying on a fresh session"
        )

    try:
        async with AsyncSessionLocal() as db2:
            exam = await db2.get(Exam, exam_id)
            if exam:
                exam.status = "failed"
                exam.generation_progress = {
                    **(exam.generation_progress or {}),
                    "error": error_msg,
                }
                await db2.commit()
    except Exception:
        logger.exception("Fallback _set_error also failed for %s", exam_id)
