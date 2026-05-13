"""
Health and readiness endpoints.

GET /health — liveness (the process is up)
GET /ready  — readiness (the DB is reachable)

Railway, Render, and Kubernetes all use these. Don't skip them.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/ready")
async def ready(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "reachable"}
    except Exception as exc:
        return {"status": "degraded", "db": "unreachable", "error": str(exc)}
