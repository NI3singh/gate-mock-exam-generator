<div align="center">

<img src="docs/logo.svg" alt="Mock-Exam AI logo" width="110" />

# Mock-Exam AI

### AI-Powered GATE 2027 Mock Exam Generator

Full-length, AI-generated GATE mock exams for **Computer Science (CS)** and **Data Science & AI (DA)** —
taken in an authentic exam interface, graded instantly, and analyzed down to the topic level.

<p>
  <a href="https://react.dev">
    <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=white" alt="React">
  </a>

  <a href="https://www.typescriptlang.org/">
    <img src="https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript">
  </a>

  <a href="https://fastapi.tiangolo.com/">
    <img src="https://img.shields.io/badge/FastAPI-Async-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  </a>

  <a href="https://www.postgresql.org/">
    <img src="https://img.shields.io/badge/PostgreSQL-14+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  </a>

  <a href="https://tailwindcss.com/">
    <img src="https://img.shields.io/badge/Tailwind_CSS-3-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind CSS">
  </a>

  <a href="https://firebase.google.com/">
    <img src="https://img.shields.io/badge/Firebase-Auth-FFCA28?style=for-the-badge&logo=firebase&logoColor=black" alt="Firebase">
  </a>
</p>

<br>

## 🎬 Watch the Website Tour

<a href="https://youtu.be/NFoiecE-uYs?si=tLaJnazA-xBl4AEt">
  <img src="docs/tour-poster.png" alt="Watch the demo">
</a>

*`docs/website-tour.mp4` — a 40-second walkthrough of the live product, rendered with Remotion from real app screenshots.*

</div>

---

## ✨ What it does

| | Feature | Details |
|---|---|---|
| 🤖 | **AI exam generation** | A full 65-question, 100-mark GATE paper generated on demand by an LLM — full syllabus or hand-picked topics, with MCQ/MSQ/NAT mix and difficulty control |
| 🖥️ | **Authentic exam interface** | Full-screen exam hall UI: server-authoritative 3-hour timer, question palette, mark-for-review, section navigation, autosave every few seconds, resume after disconnect, anti-cheat event logging |
| ✅ | **Instant grading** | Real GATE marking scheme — MCQ with ⅓ negative marking, all-or-nothing MSQ, tolerance-based NAT |
| 📊 | **Deep analytics** | Score trends across attempts, topic-wise accuracy, strongest/weakest topics, improvement tracking |
| 🗂️ | **Question bank browser** | Every generated question, filterable by paper, topic, difficulty and type — with expandable step-by-step solutions |
| 📄 | **Solution PDFs** | LaTeX-rendered solution booklets compiled on demand (KaTeX in-app, XeLaTeX for PDFs) |
| 🔐 | **Firebase auth** | Email/password login, signup, password reset; backend profile sync |
| 🔌 | **Provider-neutral LLM backend** | Swap between Nebius, OpenAI(-compatible), or Anthropic with one `.env` change — no code edits |

## 📸 Screenshots

| Dashboard | Generate Exam |
|---|---|
| ![Dashboard](docs/screens/dashboard-top.png) | ![Generate exam](docs/screens/generate-exam-top.png) |

| Question Bank | Analytics |
|---|---|
| ![Question bank](docs/screens/question-bank-top.png) | ![Analytics](docs/screens/analytics-top.png) |

## 🏗️ Architecture

```mermaid
flowchart LR
    U([Student]) --> FE["React + Vite + Tailwind<br/>frontend · :5173"]
    FE -- "Firebase ID token" --> AUTH[(Firebase Auth)]
    FE -- "REST /api/v1" --> BE["FastAPI backend<br/>async SQLAlchemy · :8000"]
    BE --> DB[("PostgreSQL")]
    BE -- "question generation" --> LLM["LLM provider<br/>Nebius · OpenAI · Anthropic"]
    BE -- "solution booklets" --> TEX["LaTeX.online<br/>XeLaTeX PDF"]
```

**Generation pipeline:** exam config → syllabus-driven batch plan → LLM generates question batches as strict JSON (LaTeX-aware parsing & repair) → per-question validation → question bank storage → 65-question exam assembly respecting the official GATE distribution → live progress polling on the frontend.

## 📝 GATE exam format (enforced by the assembler)

| Section | Questions | Marks |
|---|---|---|
| General Aptitude | 10 &nbsp;(5 × 1M + 5 × 2M) | 15 |
| Subject (CS / DA) | 55 &nbsp;(25 × 1M + 30 × 2M) | 85 |
| **Total** | **65** | **100** |

⏱ 180 minutes · question types **MCQ** (single correct, negative marking), **MSQ** (one or more correct), **NAT** (numerical answer).

## 🚀 Getting started

### Prerequisites

- Python **3.10+**, Node.js **18+**, PostgreSQL **14+**
- A Firebase project with Email/Password auth + its Admin SDK service-account JSON
- An API key for at least one LLM provider (Nebius / OpenAI-compatible / Anthropic)

### 1 · Backend

```powershell
cd backend
python -m venv mock-venv
.\mock-venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/gate_mock_test
FIREBASE_SERVICE_ACCOUNT_PATH=./firebase-service-account.json

# ── Active LLM provider: nebius | openai | anthropic ──
LLM_PROVIDER=nebius

NEBIUS_API_KEY=your_nebius_api_key
NEBIUS_BASE_URL=https://api.studio.nebius.com/v1/
NEBIUS_MODEL=deepseek-ai/DeepSeek-V3.2

OPENAI_API_KEY=
OPENAI_MODEL=
OPENAI_BASE_URL=          # optional — point at any OpenAI-compatible gateway

ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=

LLM_MAX_TOKENS=16000
LLM_TEMPERATURE=0.7
LLM_BATCH_SIZE=5
LLM_MAX_CONCURRENCY=2
LLM_RETRIES=2
LLM_TIMEOUT_SECONDS=120

LATEX_BUILD_URL=https://latex.ytotech.com/builds/sync
LATEX_COMPILER=xelatex
APP_ENV=development
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

Drop your Firebase Admin JSON at `backend/firebase-service-account.json`, then:

```powershell
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

- API base: `http://localhost:8000/api/v1` · health: `http://localhost:8000/health`
- Syllabus data auto-loads on first startup (when the table is empty).

### 2 · Frontend

```powershell
cd frontend
npm install
```

Create `frontend/.env` (match the backend port you chose above):

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

```powershell
npm run dev      # → http://localhost:5173
```

**Run order:** PostgreSQL → backend → frontend → open `http://localhost:5173`.

## 🔌 Switching LLM providers

The frontend never knows which AI is used — it's a backend-only concern:

1. Set `LLM_PROVIDER` to `nebius`, `openai`, or `anthropic` in `backend/.env`
2. Fill in that provider's key/model (and `OPENAI_BASE_URL` for OpenAI-compatible gateways)
3. Restart the backend

Inactive provider settings are ignored. There is no silent fallback — if the active provider fails, generation fails loudly with provider/model context in the logs.

## 📡 API overview

| Endpoint | Purpose |
|---|---|
| `POST /api/v1/exams/generate` | Create exam config & start background generation |
| `GET  /api/v1/exams/{id}/status` | Poll live generation progress |
| `GET  /api/v1/exams/{id}` | Fetch exam questions (answers excluded) |
| `POST /api/v1/exams/{id}/start` | Start / resume a timed attempt |
| `PUT  /api/v1/attempts/{id}/save` | Autosave responses (every few seconds) |
| `POST /api/v1/attempts/{id}/submit` | Submit & grade |
| `GET  /api/v1/attempts/{id}/detail` | Graded attempt with full solutions |
| `GET  /api/v1/analytics/dashboard` | Score trends & topic performance |
| `GET  /api/v1/question-bank` | Browse generated questions with filters |
| `POST /api/v1/admin/load-data` | (Re)load syllabus data |

Interactive docs at `http://localhost:8000/docs` once the backend is running.

## 📁 Project structure

```text
gate-mock-exam-generator/
├─ backend/             FastAPI app
│  ├─ app/
│  │  ├─ api/           routers (auth, exams, attempts, analytics, …)
│  │  ├─ core/          config, database, Firebase auth, GATE constants
│  │  ├─ models/        SQLAlchemy models
│  │  ├─ prompts/       versioned LLM prompt templates (JSON)
│  │  ├─ schemas/       Pydantic request/response models
│  │  └─ services/      generation, validation, assembly, grading, analytics, PDFs
│  ├─ alembic/          database migrations
│  ├─ data/             syllabus source JSON (CS · DA · GA)
│  └─ tests/            hermetic unit tests (no DB / API key needed)
├─ frontend/            React 18 + TypeScript + Vite + Tailwind
│  └─ src/              pages, components, contexts, services
├─ intro-video/         Remotion project — promo & website-tour videos
└─ docs/                README assets (logo, tour video, screenshots)
```

## 🎥 Promo & tour videos (Remotion)

The `intro-video/` folder is a self-contained [Remotion](https://www.remotion.dev) project with two compositions:

- **`Intro`** — a ~24s branded promo (logo reveal → features → stats → CTA)
- **`WebsiteTour`** — the ~40s product walkthrough embedded above, built from **real screenshots** of the running app

```powershell
cd intro-video
npm install
npm run capture        # re-capture live screenshots from localhost:5173 (log in once)
npm run dev            # open Remotion Studio to preview / scrub
npm run render:tour    # render out/website-tour.mp4
npm run render         # render out/intro.mp4
```

## 🛠️ Troubleshooting

| Symptom | Fix |
|---|---|
| Login works but dashboard fails | Backend/PostgreSQL profile was missing — the backend auto-syncs it during auth bootstrap; make sure the backend is running and `VITE_API_BASE_URL` points at it |
| Same account, different data on two machines | They point at different PostgreSQL databases — exam history lives in Postgres, not Firebase |
| Generation fails immediately | Check the active provider's API key/model in `backend/.env`; backend logs include provider + model context |
| PDF download fails | Backend needs outbound access to `latex.ytotech.com`; keep `LATEX_COMPILER=xelatex` (Unicode math) |
| Duplicate `/auth/me` calls in dev | React `StrictMode` double-runs effects in development — harmless, gone in production builds |

## 🔒 Production notes

- Set `APP_ENV=production` and restrict `CORS_ORIGINS` (development allows `*`)
- Use a managed PostgreSQL instance; keep the Firebase service account and API keys in a secret store
- Ensure outbound network access for the LLM provider and (optionally) LaTeX PDF compilation

---

<div align="center">

**Built by GATE aspirants, for GATE aspirants.** 🎓

*65 questions · 100 marks · 180 minutes · unlimited practice*

</div>
