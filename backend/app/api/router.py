from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.admin import router as admin_router
from app.api.syllabus import router as syllabus_router
from app.api.exams import router as exams_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(syllabus_router, prefix="/syllabus", tags=["syllabus"])
api_router.include_router(exams_router, prefix="/exams", tags=["exams"])
