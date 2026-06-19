"""
Model A/B comparison tool for GATE question generation (DEV / EVAL ONLY).

Generates a small sample of questions with two different models using the SAME
(current) generation prompts, so you can eyeball which model produces more
authentic, GATE-level questions before committing to one.

This is a standalone manual tool. It is NOT imported by the running app and has
no effect on production behaviour. It DOES call the LLM provider APIs, which
consumes credits on your account — run it yourself when ready.

Usage (from the backend/ directory):

    # Compare the current active model against an Anthropic model:
    python scripts/compare_models.py --b-provider anthropic --b-model claude-opus-4-8

    # Compare against another Nebius-hosted model:
    python scripts/compare_models.py --b-provider nebius --b-model Qwen/Qwen2.5-72B-Instruct

Options:
    --count N        questions per (section x model)   [default: 3]
    --paper CS|DA    subject paper                      [default: CS]
    --section NAME   subject section name               [default: first in syllabus]
    --out PATH       output markdown file               [default: scripts/model_comparison.md]

The challenger model must be reachable with the API key already configured in
your .env for that provider (NEBIUS_API_KEY / OPENAI_API_KEY / ANTHROPIC_API_KEY).
Model A is always the current active provider (settings.LLM_PROVIDER).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Make the app package importable when run directly as a script.
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings
from app.services.llm.providers import AnthropicProvider, OpenAICompatibleProvider
from app.services.llm.registry import get_active_provider
from app.services.llm.types import LLMProvider, LLMRequest
from app.services.llm_service import extract_json_array

PROMPTS_DIR = BACKEND_ROOT / "app" / "prompts"
SYLLABUS_DIR = BACKEND_ROOT / "data" / "syllabus"

PAPER_NAMES = {
    "CS": "Computer Science and Information Technology",
    "DA": "Data Science and Artificial Intelligence",
}

# Used only if a syllabus JSON file cannot be found on disk.
FALLBACK_SUBJECT = {
    "CS": ("Algorithms", ["Asymptotic complexity", "Greedy algorithms",
                          "Dynamic programming", "Graph traversal", "Divide and conquer"]),
    "DA": ("Machine Learning", ["Linear regression", "Logistic regression",
                               "Decision trees", "Bias-variance tradeoff", "k-NN"]),
}
FALLBACK_GA = ["Quantitative aptitude", "Data interpretation",
               "Logical reasoning", "Verbal aptitude", "Analytical reasoning"]


def _load_prompt(name: str) -> dict:
    with open(PROMPTS_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def _find_syllabus_file(paper: str) -> Path | None:
    """Case-insensitive lookup so CS_Syllabus.json / CS_syllabus.json both work."""
    if not SYLLABUS_DIR.exists():
        return None
    target = f"{paper}_syllabus.json".lower()
    for p in SYLLABUS_DIR.iterdir():
        if p.is_file() and p.name.lower() == target:
            return p
    return None


def _read_sections(paper: str) -> list[dict]:
    path = _find_syllabus_file(paper)
    if path is None:
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("sections", []) or []
    except (json.JSONDecodeError, OSError):
        return []


def _subject_section_topics(paper: str, section: str | None) -> tuple[str, list[str]]:
    sections = _read_sections(paper)
    chosen = None
    if section:
        for s in sections:
            if s.get("section_name", "").lower() == section.lower():
                chosen = s
                break
    if chosen is None and sections:
        chosen = sections[0]
    if chosen:
        return chosen.get("section_name", "Subject"), list(chosen.get("topics", []))
    return FALLBACK_SUBJECT.get(paper, FALLBACK_SUBJECT["CS"])


def _ga_topics() -> list[str]:
    topics: list[str] = []
    for s in _read_sections("GA"):
        topics.extend(s.get("topics", []))
    return topics or FALLBACK_GA


def _build_ga_user_prompt(tmpl: dict, count: int, topics: list[str]) -> str:
    topics_list = "\n".join(f"- {t}" for t in topics)
    return tmpl["user_prompt_template"].format(
        count=count, marks=2, difficulty="hard", topics_list=topics_list,
    )


def _build_subject_user_prompt(
    tmpl: dict, count: int, paper: str, section: str, topics: list[str]
) -> str:
    specs = "\n".join(f"{i}. MCQ, 2 mark(s)" for i in range(1, count + 1))
    topics_list = "\n".join(f"- {t}" for t in topics)
    return tmpl["user_prompt_template"].format(
        count=count, paper=paper, paper_full_name=PAPER_NAMES.get(paper, paper),
        section_name=section, difficulty="hard",
        question_specs=specs, topics_list=topics_list,
    )


def _build_challenger(provider: str, model: str) -> LLMProvider:
    provider = provider.lower()
    if provider == "nebius":
        return OpenAICompatibleProvider(
            name="nebius", api_key=settings.NEBIUS_API_KEY,
            base_url=settings.NEBIUS_BASE_URL, model=model,
        )
    if provider == "openai":
        return OpenAICompatibleProvider(
            name="openai", api_key=settings.OPENAI_API_KEY, model=model,
        )
    if provider == "anthropic":
        return AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY, model=model)
    raise SystemExit(f"Unknown provider '{provider}'. Use nebius, openai, or anthropic.")


async def _generate(provider: LLMProvider, system_prompt: str, user_prompt: str):
    request = LLMRequest(
        system_prompt=system_prompt, user_prompt=user_prompt,
        temperature=settings.LLM_TEMPERATURE, max_tokens=settings.LLM_MAX_TOKENS,
    )
    try:
        resp = await provider.generate(request)
    except Exception as exc:  # noqa: BLE001
        return [], f"GENERATION FAILED: {exc.__class__.__name__}: {exc}", None
    try:
        questions = extract_json_array(resp.text)
    except Exception as exc:  # noqa: BLE001
        return [], f"PARSE FAILED: {exc}", resp.usage
    return questions, None, resp.usage


def _format_question_md(q: dict) -> str:
    lines = [
        f"- **Topic:** {q.get('topic', '?')}  |  "
        f"**Difficulty:** {q.get('difficulty', '?')} ({q.get('difficulty_score', '?')})  |  "
        f"**Est. time:** {q.get('estimated_time_seconds', '?')}s",
        f"  **Q:** {(q.get('stem_tex') or '').strip()}",
    ]
    choices = q.get("choices")
    if isinstance(choices, list):
        for idx, c in enumerate(choices):
            lines.append(f"    {chr(65 + idx)}. {c}")
    lines.append(f"  **Answer:** {json.dumps(q.get('answer'))}")
    lines.append(f"  **Solution:** {(q.get('solution_tex') or '').strip()}")
    return "\n".join(lines)


def _section_md(title: str, questions: list[dict], err: str | None, usage) -> str:
    out = [f"### {title}"]
    if usage:
        out.append(f"_tokens: in={usage.get('prompt_tokens')} "
                   f"out={usage.get('completion_tokens')}_")
    if err:
        out.append(f"\n> {err}\n")
    if not questions and not err:
        out.append("\n_(no questions parsed)_\n")
    for q in questions:
        out.append(_format_question_md(q))
        out.append("")
    return "\n".join(out)


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="A/B compare two LLM models for GATE question generation."
    )
    parser.add_argument("--b-provider", required=True,
                        choices=["nebius", "openai", "anthropic"],
                        help="Provider for the challenger model (Model B).")
    parser.add_argument("--b-model", required=True,
                        help="Model id for the challenger (Model B).")
    parser.add_argument("--count", type=int, default=3,
                        help="Questions per section per model (default 3).")
    parser.add_argument("--paper", default="CS", choices=["CS", "DA"])
    parser.add_argument("--section", default=None,
                        help="Subject section name (default: first in syllabus).")
    parser.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parent / "model_comparison.md"),
    )
    args = parser.parse_args()

    ga_prompt = _load_prompt("generate_ga.json")
    batch_prompt = _load_prompt("generate_batch.json")

    provider_a = get_active_provider()
    provider_b = _build_challenger(args.b_provider, args.b_model)

    section_name, topics = _subject_section_topics(args.paper, args.section)
    ga_topics = _ga_topics()

    ga_user = _build_ga_user_prompt(ga_prompt, args.count, ga_topics)
    subj_user = _build_subject_user_prompt(
        batch_prompt, args.count, args.paper, section_name, topics
    )

    print(f"Model A (current):    {provider_a.name} / {provider_a.model}")
    print(f"Model B (challenger): {provider_b.name} / {provider_b.model}")
    print(f"Sample: {args.count} GA + {args.count} {args.paper}/{section_name} "
          f"(2-mark, hard) per model. Calling APIs...")

    a_ga, a_subj, b_ga, b_subj = await asyncio.gather(
        _generate(provider_a, ga_prompt["system_prompt"], ga_user),
        _generate(provider_a, batch_prompt["system_prompt"], subj_user),
        _generate(provider_b, ga_prompt["system_prompt"], ga_user),
        _generate(provider_b, batch_prompt["system_prompt"], subj_user),
    )

    md = [
        "# Model comparison — GATE question generation\n",
        f"- **Model A (current):** `{provider_a.name} / {provider_a.model}`",
        f"- **Model B (challenger):** `{provider_b.name} / {provider_b.model}`",
        f"- **Sample:** {args.count} GA + {args.count} {args.paper}/{section_name}, "
        f"2-mark, difficulty=hard, improved prompts\n",
        "## General Aptitude",
        _section_md(f"Model A — {provider_a.model}", *a_ga),
        _section_md(f"Model B — {provider_b.model}", *b_ga),
        f"## {args.paper} / {section_name}",
        _section_md(f"Model A — {provider_a.model}", *a_subj),
        _section_md(f"Model B — {provider_b.model}", *b_subj),
    ]

    out_path = Path(args.out)
    out_path.write_text("\n".join(md), encoding="utf-8")
    print(f"\nWrote comparison to: {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
