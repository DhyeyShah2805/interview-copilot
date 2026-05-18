"""
Interview generation endpoints.

POST /interviews/preview          — generate questions only (no persistence).
POST /interviews                  — generate AND persist as an InterviewSession.
GET  /interviews                  — list saved sessions for the current user.
GET  /interviews/{id}             — fetch one saved session with all its questions.
POST /interviews/{id}/answers     — submit an answer, evaluate synchronously.
GET  /interviews/{id}/answers     — list answers for a session.

All routes require auth via get_current_user.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.interview_answer import InterviewAnswer
from app.models.interview_session import InterviewSession
from app.models.user import User
from app.schemas.interview import (
    InterviewAnswerCreate,
    InterviewAnswerRead,
    InterviewPreviewRequest,
    InterviewPreviewResponse,
    InterviewSessionCreate,
    InterviewSessionListItem,
    InterviewSessionRead,
)
from app.services.interview_service import (
    create_session,
    get_session_by_id,
    list_answers,
    list_sessions,
    submit_answer,
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


@router.post(
    "/",
    response_model=InterviewSessionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_interview(
    payload: InterviewSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewSession:
    return await create_session(db, current_user.id, payload)


@router.get("/", response_model=list[InterviewSessionListItem])
async def list_interviews(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[InterviewSession]:
    return await list_sessions(db, current_user.id)


@router.get("/{session_id}", response_model=InterviewSessionRead)
async def get_interview(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewSession:
    session = await get_session_by_id(db, session_id, current_user.id)
    if session is None:
        raise HTTPException(status_code=404, detail="Interview session not found")
    return session


@router.post(
    "/{session_id}/answers",
    response_model=InterviewAnswerRead,
    status_code=status.HTTP_201_CREATED,
)
async def submit_interview_answer(
    session_id: uuid.UUID,
    payload: InterviewAnswerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewAnswer:
    return await submit_answer(db, current_user.id, session_id, payload)


@router.get(
    "/{session_id}/answers",
    response_model=list[InterviewAnswerRead],
)
async def list_interview_answers(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[InterviewAnswer]:
    return await list_answers(db, current_user.id, session_id)
