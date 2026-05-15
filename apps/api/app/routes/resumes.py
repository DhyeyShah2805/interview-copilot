"""
Resume endpoints: upload, list, retrieve.

All routes require a valid access token. Handlers stay thin — file I/O and
queries live in app.services.resume_service.
"""

import logging
import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.resume import ParseStatus, Resume
from app.models.user import User
from app.schemas.resume import ResumeChunkMatch, ResumeListItem, ResumeRead
from app.services.resume_service import (
    get_resume_by_id,
    list_resumes_for_user,
    parse_resume,
    save_uploaded_file,
    search_chunks,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ResumeRead, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Resume:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF uploads supported")

    resume = Resume(
        user_id=current_user.id,
        filename=file.filename,
        parse_status=ParseStatus.pending,
        raw_text=None,
    )
    db.add(resume)
    await db.flush()  # populate resume.id

    size, file_path = await save_uploaded_file(
        file,
        resume.id,
        settings.upload_dir,
        settings.max_upload_size_mb * 1024 * 1024,
    )

    await db.commit()
    await db.refresh(resume)

    logger.info("Saved resume %s (%d bytes) to %s", resume.id, size, file_path)
    background_tasks.add_task(parse_resume, resume.id, file_path)
    return resume


@router.get("/", response_model=list[ResumeListItem])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Resume]:
    return await list_resumes_for_user(db, current_user.id)


@router.get("/{resume_id}", response_model=ResumeRead)
async def get_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Resume:
    resume = await get_resume_by_id(db, resume_id, current_user.id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.get("/{resume_id}/search", response_model=list[ResumeChunkMatch])
async def search_resume(
    resume_id: uuid.UUID,
    q: str = Query(..., min_length=1, max_length=500),
    top_k: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    resume = await get_resume_by_id(db, resume_id, current_user.id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.parse_status != ParseStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Resume is not yet processed (status: {resume.parse_status.value})",
        )
    return await search_chunks(db, resume_id, current_user.id, q, top_k)
