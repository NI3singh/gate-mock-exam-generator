# GATE MockTest

AI-powered GATE 2026 mock-test platform with:

- Firebase authentication
- FastAPI + PostgreSQL backend
- React + Vite frontend
- AI-generated exams, solutions, analytics, exam history, and question bank browsing
- Solution PDF generation through LaTeX.online

## Tech Stack

- Frontend: React, TypeScript, Vite, Tailwind CSS, Firebase Auth, Recharts, KaTeX
- Backend: FastAPI, SQLAlchemy Async, PostgreSQL, Alembic, Firebase Admin, Jinja2, httpx
- PDF: LaTeX template rendered server-side and compiled through `https://latex.ytotech.com/builds/sync`

## Project Structure

```text
gate-mock-exam-generator/
├─ backend/
│  ├─ app/
│  ├─ alembic/
│  ├─ data/
│  ├─ generated_pdfs/
│  └─ requirements.txt
└─ frontend/
   ├─ src/
   └─ package.json
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- A Firebase project with Email/Password auth enabled
- A valid Firebase service account JSON file
- API key for the active backend LLM provider used for question generation

## Backend Setup

### 1. Create a virtual environment

```powershell
cd backend
python -m venv mock-venv
.\mock-venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Create `backend/.env`

Use this as a starting point:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/gate_mock_test
FIREBASE_SERVICE_ACCOUNT_PATH=./firebase-service-account.json

LLM_PROVIDER=nebius

NEBIUS_API_KEY=your_nebius_api_key
NEBIUS_BASE_URL=https://api.studio.nebius.com/v1/
NEBIUS_MODEL=deepseek-ai/DeepSeek-V3.2

OPENAI_API_KEY=
OPENAI_MODEL=

ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=

LLM_MAX_TOKENS=16000
LLM_TEMPERATURE=0.7
LLM_TEMPERATURE_VERIFY=0.1
LLM_BATCH_SIZE=5
LLM_MAX_CONCURRENCY=2
LLM_RETRIES=2
LLM_TIMEOUT_SECONDS=120
LATEX_BUILD_URL=https://latex.ytotech.com/builds/sync
LATEX_COMPILER=xelatex
APP_ENV=development
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

Notes:

- `LLM_PROVIDER` is backend-only and can be `nebius`, `openai`, or `anthropic`.
- To switch providers, set `LLM_PROVIDER`, fill that provider's API key/model values, and restart the backend.
- The frontend does not choose the AI provider. Inactive provider settings are ignored.
- There is no automatic provider fallback; if the active provider fails or hits limits, generation fails with provider/model context in backend logs.
- `LATEX_COMPILER=xelatex` is important because generated questions/solutions can contain Unicode math symbols.
- In development, the backend currently allows all CORS origins.

### 4. Place your Firebase service account file

Put the Firebase Admin SDK JSON at:

```text
backend/firebase-service-account.json
```

Or change `FIREBASE_SERVICE_ACCOUNT_PATH` in `backend/.env`.

### 5. Run database migrations

```powershell
alembic upgrade head
```

### 6. Start the backend

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

API base URL:

```text
http://localhost:8001/api/v1
```

Health check:

```text
http://localhost:8001/health
```

### 7. Syllabus loading

The backend auto-loads syllabus data on startup if the syllabus table is empty.

## Frontend Setup

### 1. Install dependencies

```powershell
cd frontend
npm install
```

### 2. Create `frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8001/api/v1
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

### 3. Start the frontend

```powershell
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

## Typical Local Run Order

1. Start PostgreSQL.
2. Start backend from `backend/`.
3. Start frontend from `frontend/`.
4. Open `http://localhost:5173`.

## Features Implemented

- Firebase login, signup, logout, reset password
- Backend profile sync for authenticated users
- Exam generation flow with progress tracking
- Full-screen exam interface with timer, autosave, resume, and anti-cheat logging
- Result screen with topic analysis and downloadable solution PDF
- Read-only solutions review page
- Analytics dashboard with score trends and topic performance
- Exam history with resume/result/delete actions
- Question bank browser with filters and expandable solutions
- Global API error toasts, loading states, 404 page, and standardized backend error responses

## PDF Generation Notes

- Solution PDFs are generated on demand by the backend.
- PDFs are saved under:

```text
backend/generated_pdfs/
```

- The backend must be able to reach:

```text
https://latex.ytotech.com/builds/sync
```

- If PDF generation fails, check backend logs first.

## Common Troubleshooting

### Login succeeds but dashboard fails

This usually means Firebase auth is working but the local backend/PostgreSQL user profile was missing. The backend now auto-syncs that profile during auth bootstrap.

### Same account works on one machine but not another

If both machines point to different PostgreSQL databases, authentication may work on both, but exam history, dashboard data, and analytics will differ.

### Duplicate `/auth/me` calls in development

React `StrictMode` can run effects twice in development. This is normal and does not happen in the production build.

### PDF download fails

Check:

- `jinja2` is installed in the backend virtual environment
- backend has internet access to LaTeX.online
- `LATEX_COMPILER=xelatex` is set or left as default

## Useful Commands

### Frontend type check / build

```powershell
cd frontend
npm run build
```

### Backend syntax sanity check

```powershell
cd backend
python -m py_compile app/main.py
```

## Production Notes

- Set `APP_ENV=production`
- Restrict `CORS_ORIGINS`
- Use a production PostgreSQL instance
- Host Firebase config and service-account secrets securely
- Ensure outbound access for PDF compilation if solution PDFs are enabled
