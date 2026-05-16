"""
Job description service layer.

JDs don't need a parse pipeline — they're stored as the user submits them.
This module just wraps the persistence + lookup so route handlers stay thin.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_description import JobDescription
from app.models.resume import ParseStatus
from app.schemas.job_description import JobDescriptionCreate


async def create_job_description(
    db: AsyncSession,
    user_id: uuid.UUID,
    payload: JobDescriptionCreate,
) -> JobDescription:
    """Persist a JD owned by user_id.

    JDs are 'completed' on save — there is no async processing pipeline.
    """
    jd = JobDescription(
        user_id=user_id,
        title=payload.title,
        company=payload.company,
        raw_text=payload.raw_text,
        parse_status=ParseStatus.completed,
    )
    db.add(jd)
    await db.commit()
    await db.refresh(jd)
    return jd


async def get_job_description(
    db: AsyncSession,
    jd_id: uuid.UUID,
    user_id: uuid.UUID,
) -> JobDescription | None:
    return await db.scalar(
        select(JobDescription).where(
            JobDescription.id == jd_id,
            JobDescription.user_id == user_id,
        )
    )


async def list_job_descriptions(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> list[JobDescription]:
    result = await db.scalars(
        select(JobDescription)
        .where(JobDescription.user_id == user_id)
        .order_by(JobDescription.created_at.desc())
    )
    return list(result)
