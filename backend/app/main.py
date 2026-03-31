from contextlib import asynccontextmanager
import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text, select, func

from app.core.config import settings
from app.core.database import engine,  AsyncSessionLocal
from app.core.firebase_auth import init_firebase
from app.api.router import api_router
from app.models.syllabus import Syllabus
from app.services.data_loader import load_syllabus

logger = logging.getLogger(__name__)


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


def build_error_response(
    status_code: int,
    detail: str,
    *,
    code: str,
    errors: list[dict[str, Any]] | None = None,
):
    payload: dict[str, Any] = {
        "detail": detail,
        "error": {
            "code": code,
            "status_code": status_code,
        },
    }

    if errors:
        payload["error"]["fields"] = errors

    return JSONResponse(status_code=status_code, content=payload)


def extract_error_message(detail: Any, fallback: str) -> str:
    if isinstance(detail, str) and detail.strip():
        return detail.strip()

    if isinstance(detail, dict):
        message = detail.get("detail") or detail.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()

    if isinstance(detail, list) and detail:
        joined = "; ".join(str(item) for item in detail[:3])
        if joined.strip():
            return joined.strip()

    return fallback


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    detail = exc.detail
    code = f"http_{exc.status_code}"
    errors: list[dict[str, Any]] | None = None

    if isinstance(detail, dict):
        nested_error = detail.get("error")
        if isinstance(nested_error, dict):
            nested_code = nested_error.get("code")
            if isinstance(nested_code, str) and nested_code.strip():
                code = nested_code.strip()

            nested_fields = nested_error.get("fields")
            if isinstance(nested_fields, list):
                errors = nested_fields

        top_level_code = detail.get("code")
        if isinstance(top_level_code, str) and top_level_code.strip():
            code = top_level_code.strip()

        top_level_errors = detail.get("errors")
        if isinstance(top_level_errors, list):
            errors = top_level_errors

    return build_error_response(
        exc.status_code,
        extract_error_message(detail, "Request failed."),
        code=code,
        errors=errors,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    fields: list[dict[str, Any]] = []
    messages: list[str] = []

    for error in exc.errors():
        loc = ".".join(str(item) for item in error.get("loc", []))
        message = error.get("msg", "Invalid value.")
        fields.append(
            {
                "field": loc or "request",
                "message": message,
                "type": error.get("type"),
            }
        )
        messages.append(f"{loc or 'request'}: {message}")

    summary = "; ".join(messages[:3]) if messages else "Validation failed."
    return build_error_response(
        422,
        summary,
        code="validation_error",
        errors=fields,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled exception during %s %s",
        request.method,
        request.url.path,
    )
    if settings.APP_ENV == "development":
        detail = str(exc).strip() or "Internal server error."
    else:
        detail = "Internal server error."

    return build_error_response(
        500,
        detail,
        code="internal_server_error",
    )


# ── Health check (no auth needed) ──
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
