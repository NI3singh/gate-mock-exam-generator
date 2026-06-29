# Previous-Year Questions (PYQ) — data format & ingestion

This directory holds the **previous-year GATE questions** used to ground exam
generation in authentic GATE difficulty (RAG: retrieve real questions → inject
as exemplars → generate NEW questions at that level, never copying).

## Directory layout

```
data/pyq/
  pdfs/      # raw official PDFs you drop in (question paper + answer key). GITIGNORED.
  json/      # canonical structured PYQ — the LLM-ready files. COMMITTED.
  figures/   # optional archived figure crops. GITIGNORED.
```

## Add flow (4 steps)

1. **Drop PDFs** into `pdfs/`, named **exactly** `{PAPER}_{YEAR}_questions.pdf` and
   `{PAPER}_{YEAR}_answerkey.pdf` (PAPER = `CS` or `DA`). The extractor reads the
   paper and year straight from the filename, so this is how you feed many years
   of CS and DA at once. Example for several combinations:
   ```
   pdfs/
     CS_2022_questions.pdf   CS_2022_answerkey.pdf
     CS_2023_questions.pdf   CS_2023_answerkey.pdf
     CS_2024_questions.pdf   CS_2024_answerkey.pdf
     DA_2023_questions.pdf   DA_2023_answerkey.pdf
     DA_2024_questions.pdf   DA_2024_answerkey.pdf
   ```
2. **Extract** — one paper, or all of them in a single run:
   ```
   # one paper-year:
   python scripts/extract_pyq.py --paper DA --year 2024 --vision-model <vl-model>
   # EVERY {PAPER}_{YEAR}_questions.pdf found in pdfs/ (recommended for 10+ files):
   python scripts/extract_pyq.py --all --vision-model <vl-model>
   ```
   The vision model parses pages → structured JSON, merges the answer key, tags
   topics against the syllabus, and writes `json/{PAPER}_{YEAR}.json` for each.
   (Tip: set `VISION_MODEL` in `.env` to skip `--vision-model`. Pilot one paper
   first with `--max-pages 2` to check quality cheaply before running `--all`.)
3. **Spot-check** each generated `json/{PAPER}_{YEAR}.json` and fix anything wrong.
4. **Load** → `python scripts/load_pyq.py` (loads ALL json files; upserts
   `source_documents` + `pyq_questions` rows and computes embeddings). Idempotent
   per (paper, year) — safe to re-run after adding more papers.

## Canonical JSON format (one file per paper-year)

```jsonc
{
  "paper": "DA",                 // "CS" | "DA"
  "year": 2024,
  "doc_type": "PYQ",             // "PYQ" (real) | "SAMPLE" (synthetic dev data)
  "source": "free-text provenance note",
  "questions": [
    {
      "qno": 5,
      "section_name": "General Aptitude",   // GA lives INSIDE each paper
      "topic": "Quantitative Aptitude",      // nearest syllabus topic
      "question_type": "MCQ",                // "MCQ" | "MSQ" | "NAT"
      "marks": 1,                            // 1 | 2
      "stem": "question text; LaTeX for math; figures folded in as [Figure: ...]",
      "code_snippet": null,                  // code string, or null
      "code_language": null,                 // "c" | "python" | null
      "has_figure": false,                   // true if a figure was described in the stem
      "options": ["40", "45", "48", "50"],   // 4 strings for MCQ/MSQ; null for NAT
      "answer": "C",                         // MCQ: "C"  |  MSQ: "A,C"  |  NAT: null
      "answer_value": null,                  // NAT numeric answer; else null
      "tolerance": null,                     // NAT tolerance; else null
      "solution": null                       // optional worked solution (usually null)
    }
  ]
}
```

### Field rules
- **answer encoding** — MCQ: single option letter (`"A"`..`"D"`). MSQ: comma-joined
  letters (`"A,C"`). NAT: leave `answer` null and set `answer_value` (+ `tolerance`).
- **figures** — convert each figure to a precise text description folded into the
  `stem` as `[Figure: ...]`, and set `has_figure: true`. Option-images are described
  in place inside `options`. Questions whose figure genuinely cannot be captured in
  text are **skipped** (not included in the file).
- **GA** — General Aptitude questions are stored under their real paper
  (`paper: "DA"`, `section_name: "General Aptitude"`). Retrieval pools GA across all
  papers (CS + DA) into one exemplar bank; subject questions are filtered by paper.
- **LaTeX** — write normal single-backslash LaTeX in the *stored* string; in the JSON
  file that means doubling backslashes (`\\frac`, `\\Theta`, `\\mid`).

## Notes
- `SAMPLE_*.json` files are **synthetic dev fixtures**, not real GATE questions
  (`doc_type: "SAMPLE"`). Replace/augment with real `PYQ` files as you collect them.
- Embeddings are 384-dim (`all-MiniLM-L6-v2`) to match the `vector(384)` column —
  computed locally, no API cost.
