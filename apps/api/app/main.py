"""
FastAPI application entry point.

Wires together:
- CORS for the Next.js frontend
- Routers (health, auth, and future feature routes)
- Lifespan hooks for startup/shutdown (DB connection check, etc.)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes import auth, health, job_descriptions, resumes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verify DB connection, warm caches, etc.
    # (We'll add real checks here on Day 2/3.)
    print(f"🚀 Starting {settings.app_name} in {settings.environment} mode")
    yield
    # Shutdown: close pools, flush logs, etc.
    print("👋 Shutting down")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-powered interview preparation platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
app.include_router(
    job_descriptions.router,
    prefix="/job-descriptions",
    tags=["job-descriptions"],
)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
