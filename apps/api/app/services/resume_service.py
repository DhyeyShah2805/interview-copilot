"""
Resume service layer.

Route handlers stay thin — all DB queries, file I/O, and the (placeholder)
parse pipeline live here.
"""

import asyncio
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.resume import ParseStatus, Resume

_CHUNK_SIZE = 8 * 1024  # 8 KB


async def save_uploaded_file(
    file: UploadFile,
    resume_id: uuid.UUID,
    upload_dir: str,
    max_bytes: int,
) -> int:
    """Stream an upload to disk in 8 KB chunks, enforcing a size ceiling.

    Returns the number of bytes written. On overflow the partial file is
    removed before raising.
    """
    Path(upload_dir).mkdir(parents=True, exist_ok=True)
    dest = Path(upload_dir) / f"{resume_id}.pdf"

    total = 0
    try:
        with dest.open("wb") as out:
            while True:
                chunk = await file.read(_CHUNK_SIZE)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File exceeds max size",
                    )
                out.write(chunk)
    except HTTPException:
        dest.unlink(missing_ok=True)
        raise

    return total


async def get_resume_by_id(
    db: AsyncSession, resume_id: uuid.UUID, user_id: uuid.UUID
) -> Resume | None:
    return await db.scalar(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
    )


async def list_resumes_for_user(
    db: AsyncSession, user_id: uuid.UUID
) -> list[Resume]:
    result = await db.scalars(
        select(Resume)
        .where(Resume.user_id == user_id)
        .order_by(Resume.created_at.desc())
    )
    return list(result)


async def placeholder_parse_resume(resume_id: uuid.UUID) -> None:
    """Stand-in for the real parse pipeline (Block 3 replaces this body).

    Runs as a background task, so it opens its own session — the request's
    session is already closed by the time this executes.
    """
    await asyncio.sleep(1)
    async with AsyncSessionLocal() as db:
        resume = await db.get(Resume, resume_id)
        if resume is None:
            return
        resume.parse_status = ParseStatus.processing
        await db.commit()
