# PYQ setup & run guide (fresh machine)

How to get the app running **with previous-year-question (PYQ) grounding** on a new
computer — from installing prerequisites, to adding PDFs, to seeing generated
questions grounded on real GATE papers.

You already know how to run the app *without* PYQ. This guide calls out the
**new/extra** steps (marked 🆕) and keeps the parts you already know short.

---

## TL;DR — the command order

```bash
# from backend/ , with your virtualenv active
pip install -r requirements.txt          # 🆕 now includes sentence-transformers + pymupdf
# ... fill in .env (see section 3) ...
# DB: point DATABASE_URL at your existing Neon DB (already has schema + data) -> nothing
#     else to do.  (A brand-new EMPTY database instead? run:  alembic upgrade head)

# 🆕 PYQ pipeline
#   1. put PDFs in data/pyq/pdfs/  named CS_2024_questions.pdf / CS_2024_answerkey.pdf ...
python scripts/extract_pyq.py --all --vision-model <your-vision-model>   # PDFs -> json/
#   2. review the json/ files
python scripts/load_pyq.py               # json -> DB rows + embeddings

uvicorn app.main:app --reload            # run the app; new exams now auto-ground on PYQs
```

---

## 1. What PYQ adds (why these extra steps exist)

Without PYQ, the LLM invented questions from scratch (too easy). With PYQ, at
generation time the app **retrieves real previous-year questions** similar to the
topic and injects them as exemplars ("match this difficulty, generate NEW"). That
needs three things that the base app didn't: a couple of Python packages, the PYQ
tables in the DB (already created by migration `002`), and your PYQ data loaded.

**Safety net:** if PYQs aren't loaded or the embedding model isn't installed, the
app silently falls back to normal generation — it will not crash. So the only way
to "lose" grounding is to skip the data steps, never to break the app.

---

## 2. Prerequisites (delta from the base app)

The base app needs: Python 3.11+, Node (for the frontend), and a Postgres database.
For PYQ, three things matter:

- 🆕 **Database — use Neon (recommended).** The database now lives on **Neon** (cloud)
  and already has pgvector, the full schema, and your data (migrated from the old local
  Postgres via `scripts/migrate_to_neon.py`). On a new machine you do **not** need a
  local Postgres install, `createdb`, migrations, or a data re-load — just set
  `DATABASE_URL` to your Neon URL (section 3) and run.
  - App (asyncpg) form: `postgresql+asyncpg://<user>:<pass>@<ep-...>.neon.tech/neondb?ssl=require`
    — note **`?ssl=require`** (NOT `sslmode=`), and use the **direct** endpoint
    (hostname has no `-pooler`).
  - _Alternative — local Postgres:_ you must have the **pgvector** extension available
    (easiest: `docker run -d --name gate-pg -e POSTGRES_PASSWORD=postgres -p 5432:5432 pgvector/pgvector:pg16`),
    then create the DB and run `alembic upgrade head` (section 3, Option B).
- 🆕 **First embedding run downloads a model (~90 MB).** The first time embeddings
  are computed, `sentence-transformers` downloads `all-MiniLM-L6-v2`. Needs internet
  once; it's then cached. (Offline machine? See Troubleshooting.)
- 🆕 **A vision-capable LLM** is required only for the PDF→JSON extractor, e.g. a
  Qwen-VL model on Nebius. Confirm the exact model id in your provider dashboard.

---

## 3. One-time machine setup

```bash
git clone <repo-url>
cd gate-mock-exam-generator
git checkout pyq_addition        # the branch with PYQ support

cd backend
python -m venv venv
#   Windows:        venv\Scripts\activate
#   macOS / Linux:  source venv/bin/activate
pip install -r requirements.txt  # 🆕 pulls sentence-transformers + pymupdf too
```

Create `backend/.env` (same vars as before, **plus** the 🆕 PYQ ones):

```dotenv
# --- database: Neon (recommended) — copy from the Neon dashboard; asyncpg form + ?ssl=require ---
DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<ep-xxxx>.<region>.aws.neon.tech/neondb?ssl=require
# (local alternative) DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/gate_mock_test
FIREBASE_SERVICE_ACCOUNT_PATH=./firebase-service-account.json
LLM_PROVIDER=nebius
NEBIUS_API_KEY=...
NEBIUS_BASE_URL=https://api.studio.nebius.com/v1/
NEBIUS_MODEL=...                  # your text model for generation

# --- 🆕 PYQ grounding ---
PYQ_GROUNDING_ENABLED=true        # master switch (default true)
PYQ_RETRIEVAL_TOP_K=3             # how many exemplars per batch
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2   # 384-dim, free, local
VISION_MODEL=                     # set to a vision model id for the extractor

# --- 🆕 optional: difficulty/correctness gate (off by default) ---
# LLM_VERIFY_ENABLED=false
# LLM_VERIFY_CHECK_DIFFICULTY=true
```

**Database — pick one:**

- **Option A — Neon (recommended):** nothing to do. Your Neon DB already has every
  table, index, pgvector, and all data (it was migrated). Just confirm `DATABASE_URL`
  points to it (above) and **skip `createdb` / `alembic`**.
- **Option B — a fresh/empty DB** (new local Postgres, or a brand-new empty Neon DB):
  create it, then build the schema:
  ```bash
  # local example:  docker exec -it gate-pg createdb -U postgres gate_mock_test
  alembic upgrade head    # creates ALL tables incl. pyq_questions + pgvector HNSW indexes
  ```

> Syllabus data **auto-loads** on first server start *if its table is empty* (so a fresh
> Option-B DB self-populates syllabus; your existing Neon DB already has it). PYQ data
> **never** auto-loads — you load it explicitly in section 4.

---

## 4. 🆕 The PYQ data pipeline (the main new part)

### Step 1 — add the PDFs
Put official GATE PDFs into `backend/data/pyq/pdfs/`, named **exactly**:

```
{PAPER}_{YEAR}_questions.pdf      e.g.  CS_2024_questions.pdf
{PAPER}_{YEAR}_answerkey.pdf      e.g.  CS_2024_answerkey.pdf
```

`PAPER` is `CS` or `DA`; the year comes from the filename. CS and DA go in the
**same folder** — the prefix keeps them apart. Drop in as many years as you have:

```
data/pyq/pdfs/
  CS_2022_questions.pdf   CS_2022_answerkey.pdf
  CS_2023_questions.pdf   CS_2023_answerkey.pdf
  DA_2023_questions.pdf   DA_2023_answerkey.pdf
  DA_2024_questions.pdf   DA_2024_answerkey.pdf
  ...
```

(This folder is gitignored, so your PDFs stay local.)

### Step 2 — set the vision model
Put a vision-capable model id in `.env` as `VISION_MODEL=...` (or pass
`--vision-model` on the command line each time).

### Step 3 — extract PDFs → JSON
**Pilot one paper first** (cheap — only 2 pages) to check quality before spending
credits on everything:

```bash
python scripts/extract_pyq.py --paper CS --year 2024 --max-pages 2
```

Open `data/pyq/json/CS_2024.json` and sanity-check it. Happy? Run them all:

```bash
python scripts/extract_pyq.py --all
```

This finds every `*_questions.pdf`, pairs it with its answer key, and writes one
`json/{PAPER}_{YEAR}.json` per paper. It calls the vision model, so it uses credits.

### Step 4 — review the JSON
Skim each `data/pyq/json/*.json`. Fix any wrong topic tags, garbled stems, or
answers. This is your quality gate — the better the PYQs, the better the grounding.

> The repo ships two `SAMPLE_*.json` dev fixtures. For a real run you can delete
> them so only your genuine PYQs are loaded:
> `rm data/pyq/json/SAMPLE_*.json` (Windows: `del data\pyq\json\SAMPLE_*.json`).

### Step 5 — load into the database
```bash
python scripts/load_pyq.py
```

Expected output (the important bits):

```
PYQ load result
  embeddings available: True          <-- must be True for retrieval to work
  CS_2024.json: 65 questions (paper=CS, year=2024, embedded=True)
  ...
  total questions loaded: N
```

If `embeddings available: False`, retrieval won't work — install
`sentence-transformers` (it's in requirements) and re-run this command.

It's **idempotent per (paper, year)** — safe to re-run after adding more papers or
editing JSON; it replaces that paper-year's rows. (With Neon, this loads into the
cloud DB, so every machine pointing at Neon immediately sees the PYQs.)

---

## 5. Run the app & confirm grounding works

```bash
uvicorn app.main:app --reload         # backend on http://localhost:8000
# (frontend: same as before — cd frontend && npm install && npm run dev)
```

Generate an exam from the UI as usual. In the **backend logs** you should see:

```
PYQ grounding is ON for this generation
Attached 3 PYQ exemplar(s) to batch (CS / Algorithms)
...
```

That confirms real PYQs are being injected into generation. If you don't see those
lines, check the troubleshooting list below.

---

## 6. Environment toggles (quick reference)

| Variable | Default | Meaning |
|---|---|---|
| `PYQ_GROUNDING_ENABLED` | `true` | Master switch for PYQ grounding. |
| `PYQ_RETRIEVAL_TOP_K` | `3` | Exemplars retrieved per batch. |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Local embedding model (must be 384-dim). |
| `VISION_MODEL` | _(empty)_ | Vision model for the PDF extractor. |
| `LLM_VERIFY_ENABLED` | `false` | Re-solve + difficulty-gate each generated question (adds ~1 LLM call/question). |
| `LLM_VERIFY_CHECK_DIFFICULTY` | `true` | When verify is on, also reject too-easy questions. |

Per-exam, grounding also respects the exam's `use_pyq_reference` flag (set from
`PYQ_GROUNDING_ENABLED` at creation time).

---

## 7. Troubleshooting

- **App can't connect to Neon / SSL error** → make sure `DATABASE_URL` is the
  **asyncpg** form with **`?ssl=require`** (not `sslmode=`), pointing at the **direct**
  endpoint (no `-pooler` in the host). Re-verify the data with
  `python scripts/migrate_to_neon.py --verify-only`.
- **No `PYQ grounding is ON` in logs** → `PYQ_GROUNDING_ENABLED` is false, or the
  exam was created before you enabled it. Set it true, restart, make a NEW exam.
- **`Attached 0 exemplars` / no exemplar lines** → no PYQs loaded, or embeddings
  missing. Run `python scripts/load_pyq.py` and confirm `embeddings available: True`.
- **`embeddings available: False`** → `pip install sentence-transformers`, then
  re-run the loader (rows loaded without embeddings won't be retrievable).
- **`CREATE EXTENSION vector` fails (local DB only)** → pgvector isn't installed in
  that Postgres. Use the `pgvector/pgvector:pg16` Docker image (or add pgvector to your
  install), then `alembic upgrade head` again. (Neon already has pgvector.)
- **Extractor: `No vision model set`** → set `VISION_MODEL` in `.env` or pass
  `--vision-model`.
- **Extractor produces messy JSON** → tune with `--max-pages` on one paper; fix the
  prompt in `scripts/extract_pyq.py` (the `_EXTRACT_SYSTEM` string) and re-pilot.
- **Offline machine (no model download)** → on an online machine, download the
  model once and copy the cache (`~/.cache/huggingface`), or set `EMBEDDING_MODEL`
  to a local folder path.

---

## 8. Adding more papers later

1. Drop the new `{PAPER}_{YEAR}_questions.pdf` + `_answerkey.pdf` into `pdfs/`.
   (To avoid re-paying to extract papers you already did, keep only the NEW PDFs in
   the folder, or extract them individually with `--paper/--year`.)
2. `python scripts/extract_pyq.py --all`  → review the new `json/` files.
3. `python scripts/load_pyq.py`  → loads/refreshes everything (idempotent).

No app restart is needed for new PYQs to be used — retrieval reads the DB live on
the next generation.
