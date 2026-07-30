"""
BuildWise AI — FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import structlog
import os

from config import settings
from database import init_db
from routers import (
    auth, buildings, complaints, technicians,
    schedules, equipment, predictions, knowledge,
    analytics, agents, notifications, uploads, cv
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup & shutdown."""
    logger.info("BuildWise AI starting up…", version="1.0.0", env=settings.ENVIRONMENT)
    await init_db()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/images", exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/documents", exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/audio", exist_ok=True)
    yield
    logger.info("BuildWise AI shutting down…")


app = FastAPI(
    title="BuildWise AI API",
    description="Autonomous Multi-Agent Building Maintenance & Facility Management Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static Files ──────────────────────────────────────────────────────────────
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ── Routers ───────────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(auth.router,          prefix=f"{API_PREFIX}/auth",          tags=["Authentication"])
app.include_router(buildings.router,     prefix=f"{API_PREFIX}/buildings",     tags=["Buildings"])
app.include_router(complaints.router,    prefix=f"{API_PREFIX}/complaints",    tags=["Complaints"])
app.include_router(technicians.router,   prefix=f"{API_PREFIX}/technicians",   tags=["Technicians"])
app.include_router(schedules.router,     prefix=f"{API_PREFIX}/schedules",     tags=["Schedules"])
app.include_router(equipment.router,     prefix=f"{API_PREFIX}/equipment",     tags=["Equipment"])
app.include_router(predictions.router,   prefix=f"{API_PREFIX}/predictions",   tags=["Predictions"])
app.include_router(knowledge.router,     prefix=f"{API_PREFIX}/knowledge",     tags=["Knowledge Base"])
app.include_router(analytics.router,     prefix=f"{API_PREFIX}/analytics",     tags=["Analytics"])
app.include_router(agents.router,        prefix=f"{API_PREFIX}/agents",        tags=["AI Agents"])
app.include_router(notifications.router, prefix=f"{API_PREFIX}/notifications", tags=["Notifications"])
app.include_router(uploads.router,       prefix=f"{API_PREFIX}/uploads",       tags=["File Uploads"])
app.include_router(cv.router,            prefix=f"{API_PREFIX}/cv",            tags=["Computer Vision"])


@app.get("/", tags=["Health"])
async def root():
    return {"message": "BuildWise AI API", "version": "1.0.0", "status": "operational"}


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "BuildWise AI",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )
