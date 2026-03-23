from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, select, func

from app.core.config import settings
from app.core.database import engine,  AsyncSessionLocal
from app.core.firebase_auth import init_firebase
from app.api.router import api_router
from app.models.syllabus import Syllabus
from app.services.data_loader import load_syllabus


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──
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

    yield

    # ── Shutdown ──
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
