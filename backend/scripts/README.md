# Backend Scripts

## `ingest_pyq_pdf.py` — PYQ PDF → JSON extractor (offline, one-time per PDF)

Converts an official GATE question-paper PDF into a structured JSON file under
`backend/data/pyqs/`, which the backend then loads into the `pyq_questions`
table. The generator injects these real PYQs into its prompts as **style and
difficulty reference** (they are never shown to students).

It renders each PDF page to an image and sends batches of pages to a
vision-capable Claude model, so it handles GATE's math notation, two-column
layouts, and **figure-based questions** (figures become precise textual
descriptions embedded in the question stem, e.g. `[Figure: directed graph
with 5 nodes ...]`).

### Setup (once)

```bash
cd backend/scripts
pip install -r requirements-ingest.txt
set ANTHROPIC_API_KEY=sk-ant-...        # Windows (PowerShell: $env:ANTHROPIC_API_KEY="...")
```

### Run

```bash
python ingest_pyq_pdf.py --pdf path/to/CS_2024.pdf --paper CS --year 2024
# with a separate official answer-key PDF:
python ingest_pyq_pdf.py --pdf CS_2024.pdf --paper CS --year 2024 --answer-key-pdf CS_2024_key.pdf
```

Useful flags: `--pages-per-call 3` (pages per vision request), `--dpi 170`
(render resolution), `--model claude-opus-4-8`, `--out` (output dir,
defaults to `backend/data/pyqs`), `--no-resume`.

**Resumable:** every vision call is checkpointed under
`<out>/.checkpoints/<PAPER>_<YEAR>/`. If a run dies, re-running skips
completed chunks — you only pay for what's missing. Delete that folder (or
pass `--no-resume`) to force a clean re-extraction.

### After running

1. **Review the JSON by hand** — the script prints a summary (counts by
   type/marks, unanswered questions, dropped/invalid questions, missing
   question numbers). Spot-check stems, figures, and answers against the PDF.
2. Load into the DB: `POST /api/v1/admin/load-data` (reads every
   `backend/data/pyqs/*.json`; idempotent per paper+year — re-loading a fixed
   file replaces the old rows).
3. Verify: `GET /api/v1/admin/data-stats` now shows a `pyqs` section.
4. Generate an exam — PYQ reference is on by default (`use_pyq_reference`).

### Output format

```json
{
  "paper": "CS",
  "year": 2024,
  "source_filename": "CS_2024.pdf",
  "extracted_with": "claude-opus-4-8",
  "questions": [
    {
      "qno": 1, "question_type": "MCQ", "marks": 1,
      "section_name": "General Aptitude", "topic": "Verbal Aptitude",
      "stem": "...", "code_snippet": null,
      "options": ["...", "...", "...", "..."],
      "answer": "B", "answer_value": null, "tolerance": null,
      "solution": null
    }
  ]
}
```

Answer conventions: MCQ `"A"`–`"D"`; MSQ letters joined with `;` (`"A;C"`);
NAT uses `answer_value` + `tolerance` (ranges like `"0.24 to 0.26"` are
converted to midpoint ± half-width automatically).
