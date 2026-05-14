"""
Resume endpoints: upload, list, retrieve.

All routes require a valid access token. Handlers stay thin — file I/O and
queries live in app.services.resume_service.
"""

import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.resume import ParseStatus, Resume
from app.models.user import User
from app.schemas.resume import ResumeListItem, ResumeRead
from app.services.resume_service import (
    get_resume_by_id,
    list_resumes_for_user,
    placeholder_parse_resume,
    save_uploaded_file,
)

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

    await save_uploaded_file(
        file,
        resume.id,
        settings.upload_dir,
        settings.max_upload_size_mb * 1024 * 1024,
    )

    await db.commit()
    await db.refresh(resume)

    background_tasks.add_task(placeholder_parse_resume, resume.id)
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
