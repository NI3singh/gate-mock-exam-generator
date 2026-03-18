from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.core.firebase_auth import init_firebase
from app.api.router import api_router


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