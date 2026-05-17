"""
Interview generation endpoints.

POST /interviews/preview — generate questions for a (resume, JD) pair.
Requires auth.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.interview import (
    InterviewPreviewRequest,
    InterviewPreviewResponse,
)
from app.services.question_generation_service import generate_questions

router = APIRouter()


@router.post(
    "/preview",
    response_model=InterviewPreviewResponse,
    status_code=status.HTTP_200_OK,
)
async def preview_interview(
    payload: InterviewPreviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewPreviewResponse:
    return await generate_questions(
        db=db,
        resume_id=payload.resume_id,
        job_description_id=payload.job_description_id,
        user_id=current_user.id,
        num_questions=payload.num_questions,
    )
