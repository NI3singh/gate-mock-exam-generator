import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, select, func, update

from app.core.config import settings
from app.core.database import engine, AsyncSessionLocal
from app.core.firebase_auth import init_firebase
from app.api.router import api_router
from app.models.syllabus import Syllabus
from app.models.exam import Exam
from app.services.data_loader import load_syllabus
from app.services.llm_queue import run_worker, shutdown_queue, GenerationJob
from app.services.question_generator import generate_exam_questions
from app.services.exam_assembler import assemble_exam

# Module-level worker task handle
worker_task: asyncio.Task | None = None


async def process_generation_job(job: GenerationJob) -> None:
    """
    Top-level handler that wires together generation + assembly for a single exam.
    Run by the LLM queue worker.
    """
    async with AsyncSessionLocal() as db:
        try:
            questions, _ = await generate_exam_questions(
                db=db,
                exam_id=str(job.exam_id),
                paper=job.paper,
                scope=job.scope,
                selected_topics=job.selected_topics,
                difficulty=job.difficulty,
                types_ratio=job.types_ratio,
            )
            await assemble_exam(
                db=db,
                exam_id=str(job.exam_id),
                all_questions=questions,
                types_ratio=job.types_ratio,
            )
            print(f"[generation] Exam {job.exam_id} completed successfully")
        except Exception as exc:
            print(f"[generation] Exam {job.exam_id} failed: {exc}")
            await db.execute(
                update(Exam)
                .where(Exam.id == job.exam_id)
                .values(status="failed")
            )
            await db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──
    global worker_task

    # 1. Test database connection
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅  Database connection successful")
    except Exception as e:
        print(f"❌  Database connection failed: {e}")
        raise

    # 2. Initialize Firebase Admin SDK
    init_firebase()
    print("✅  Firebase Admin SDK initialized")

    # 3. Auto-load syllabus data if the table is empty
    async with AsyncSessionLocal() as db:
        count_result = await db.execute(
            select(func.count(Syllabus.id))
        )
        total = count_result.scalar() or 0
        if total == 0:
            print("📦  Syllabus table is empty — auto-loading data…")
            load_result = await load_syllabus(db)
            if load_result.errors:
                for err in load_result.errors:
                    print(f"⚠️  {err}")
            else:
                print(
                    f"✅  Syllabus auto-loaded: "
                    f"{load_result.total_rows_inserted} rows "
                    f"for {', '.join(load_result.papers_loaded)}"
                )
        else:
            print(f"✅  Syllabus table already has {total} rows — skipping auto-load")

    # 4. Start LLM queue worker
    worker_task = asyncio.create_task(run_worker(process_generation_job))
    print("✅  LLM queue worker started")

    yield

    # ── Shutdown ──
    await shutdown_queue()
    if worker_task:
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass
    await engine.dispose()
    print("🛑  Application shut down")


app = FastAPI(
    title="GATE Mock-Test API",
    description="Backend API for the GATE 2026 mock-test system",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──
app.include_router(api_router, prefix="/api/v1")


# ── Health check (no auth needed) ──
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}