# PYQ Runbook — Test Exam Generation with Real Past Questions (Local)

A simple, step-by-step guide to go from a GATE PYQ PDF → questions in your
database → an exam generated with real past-question context.

> **Good to know:** if you skip all of this, nothing breaks. With no PYQs
> loaded, exam generation works exactly like before. PYQs only make the
> generated questions more realistic in style and difficulty.

---

## What you need before starting

- Your usual local setup working: PostgreSQL running, `mock-venv`, frontend.
- A GATE question-paper PDF (e.g. `CS_2024.pdf`). An official answer-key PDF
  is optional but nice to have.
- An Anthropic API key (only for the one-time PDF extraction step).

---

## Step 1 — Extract questions from the PDF (one time per PDF)

Open PowerShell:

```powershell
cd D:\AI-Mock\gate-mock-exam-generator\backend\scripts
pip install -r requirements-ingest.txt
$env:ANTHROPIC_API_KEY = "sk-ant-..."

python ingest_pyq_pdf.py --pdf C:\path\to\CS_2024.pdf --paper CS --year 2024
```

If you also have the official answer key PDF, add:

```powershell
  --answer-key-pdf C:\path\to\CS_2024_key.pdf
```

This sends the PDF pages to a vision model and writes:

```
backend\data\pyqs\CS_2024.json
```

- It takes a few minutes and costs a few dollars of API credit — **once per PDF**.
- If it crashes or you stop it midway, just run the same command again — it
  resumes from where it stopped (checkpoints), you don't pay twice.
- Questions with figures are NOT skipped — the figure becomes a text
  description inside the question, like `[Figure: directed graph with 5 nodes ...]`.

## Step 2 — Quickly review the JSON

Open `backend\data\pyqs\CS_2024.json` and spot-check 4-5 questions against the
PDF:

- Does the stem text look right? Math should be LaTeX like `$O(n \log n)$`.
- Do MCQ/MSQ questions have 4 options?
- The script's final summary in the terminal tells you if any question numbers
  are **missing** or were **dropped** — check those in the PDF if you care.

Found a mistake? Just edit the JSON by hand and save. (Re-loading later
replaces old data, so editing is always safe.)

## Step 3 — Start the backend

```powershell
cd D:\AI-Mock\gate-mock-exam-generator\backend
# activate mock-venv as you usually do, then:
uvicorn app.main:app --reload
```

## Step 4 — Load the PYQs into the database

Call the existing admin endpoint (it now loads syllabus **and** PYQs):

```
POST http://localhost:8000/api/v1/admin/load-data
```

Easiest ways to call it (it needs your normal Firebase login token):

- From the frontend app while logged in (browser devtools → copy the
  `Authorization: Bearer ...` header from any API request), then in PowerShell:

  ```powershell
  curl.exe -X POST http://localhost:8000/api/v1/admin/load-data -H "Authorization: Bearer <your-token>"
  ```

The response should include something like:

```json
"details": { "PYQ CS 2024": { "questions_inserted": 63, "questions_skipped": 2 } }
```

**Safe to repeat:** calling it twice does NOT duplicate anything — each
(paper, year) is wiped and re-inserted. Fixed the JSON? Just call it again.

## Step 5 — Verify the data is in

```
GET http://localhost:8000/api/v1/admin/data-stats
```

Look for the new `pyqs` section:

```json
"pyqs": { "CS": { "total_questions": 63, "years": [2024] }, "DA": { ... } }
```

## Step 6 — Generate an exam (PYQs are used automatically)

Generate a **CS** exam from the frontend like you always do. PYQ reference is
**ON by default** — no toggle needed.

Watch the backend terminal. Right after the "Batch plan" line you should see:

```
PYQ reference pool: {'GA/1m': 5, 'GA/2m': 5, 'Subject/1m': 12, 'Subject/2m': 12}
```

Non-zero numbers = real PYQs are being injected into the generation prompts as
style/difficulty reference.

## Step 7 — Check the result

- The exam should still reach **65/65 questions** as usual.
- Open a few generated questions — they should *feel* more GATE-like, but must
  NOT be copies of the PYQs in your JSON file (the prompt forbids copying).

## Step 8 — (Optional) Test that turning it OFF works

Generate an exam with the API directly, adding one field to the usual body:

```json
{ "paper": "CS", "scope": "full", "difficulty": "auto", "use_pyq_reference": false }
```

The log should then show **no** "PYQ reference pool" line, and generation
still completes normally. Same thing happens automatically for any paper with
no PYQs loaded (e.g. DA right now).

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `PYQ reference pool: {... 0 ...}` everywhere | Step 4 didn't load — re-check the `load-data` response for errors |
| `questions_skipped` is high in Step 4 | Open the JSON; the response's `errors` list says exactly which qno failed and why; fix and re-load |
| Ingestion script dies midway | Re-run the same command — it resumes from checkpoints |
| Want a clean re-extraction | Delete `backend\data\pyqs\.checkpoints\CS_2024\` or pass `--no-resume` |
| Generation behaves weirdly after this change | Generate with `"use_pyq_reference": false` — if the problem disappears, it's PYQ-related; if not, it's unrelated |
