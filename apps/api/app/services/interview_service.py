"""
Interview session persistence layer.

Wraps the generate_questions pipeline (LLM call + RAG retrieval) with the
DB writes that persist the session and its questions.
"""

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.interview_question import InterviewQuestion
from app.models.interview_session import (
    InterviewSession,
    InterviewSessionStatus,
    QuestionDifficulty,
    QuestionType,
)
from app.schemas.interview import InterviewSessionCreate
from app.services.question_generation_service import generate_questions


async def create_session(
    db: AsyncSession,
    user_id: uuid.UUID,
    payload: InterviewSessionCreate,
) -> InterviewSession:
    """Generate questions via the LLM pipeline, then persist as a session.

    Ownership / readiness errors (404, 409, 500-empty-chunks) raised by
    generate_questions propagate unchanged — we never reach the DB writes if
    that call fails.
    """
    preview = await generate_questions(
        db=db,
        resume_id=payload.resume_id,
        job_description_id=payload.job_description_id,
        user_id=user_id,
        num_questions=payload.num_questions,
    )

    session = InterviewSession(
        user_id=user_id,
        resume_id=payload.resume_id,
        job_description_id=payload.job_description_id,
        status=InterviewSessionStatus.not_started,
        model_used=preview.model,
        num_questions=len(preview.questions),
    )
    db.add(session)
    await db.flush()  # populate session.id for the FK below

    for i, q in enumerate(preview.questions):
        db.add(
            InterviewQuestion(
                session_id=session.id,
                order_index=i,
                question=q.question,
                type=QuestionType(q.type),
                rationale=q.rationale,
                difficulty=QuestionDifficulty(q.difficulty),
                anchor=q.anchor,
            )
        )

    await db.commit()

    refreshed = await get_session_by_id(db, session.id, user_id)
    if refreshed is None:
        # Defensive: we just committed this row with this user_id, so this
        # branch shouldn't be reachable. get_session_by_id is Optional by
        # contract, so we make the impossible case explicit.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to re-fetch newly created session",
        )
    return refreshed


async def list_sessions(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> list[InterviewSession]:
    result = await db.scalars(
        select(InterviewSession)
        .where(InterviewSession.user_id == user_id)
        .order_by(InterviewSession.created_at.desc())
    )
    return list(result)


async def get_session_by_id(
    db: AsyncSession,
    session_id: uuid.UUID,
    user_id: uuid.UUID,
) -> InterviewSession | None:
    return await db.scalar(
        select(InterviewSession)
        .where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id,
        )
        .options(selectinload(InterviewSession.questions))
    )
