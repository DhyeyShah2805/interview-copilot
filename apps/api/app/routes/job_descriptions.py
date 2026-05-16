"""
Job description endpoints: create, list, retrieve.

All routes require a valid access token. Handlers stay thin — persistence
and queries live in app.services.job_description_service.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.job_description import JobDescription
from app.models.user import User
from app.schemas.job_description import (
    JobDescriptionCreate,
    JobDescriptionListItem,
    JobDescriptionRead,
)
from app.services.job_description_service import (
    create_job_description,
    get_job_description,
    list_job_descriptions,
)

router = APIRouter()


@router.post(
    "/",
    response_model=JobDescriptionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_jd(
    payload: JobDescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobDescription:
    return await create_job_description(db, current_user.id, payload)


@router.get("/", response_model=list[JobDescriptionListItem])
async def list_jds(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[JobDescription]:
    return await list_job_descriptions(db, current_user.id)


@router.get("/{jd_id}", response_model=JobDescriptionRead)
async def get_jd(
    jd_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobDescription:
    jd = await get_job_description(db, jd_id, current_user.id)
    if jd is None:
        raise HTTPException(status_code=404, detail="Job description not found")
    return jd
