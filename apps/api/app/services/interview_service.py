"""
Interview session persistence layer.

Wraps the generate_questions pipeline (LLM call + RAG retrieval) with the
DB writes that persist the session and its questions. Also handles answer
submission, which runs the evaluator synchronously and persists either
the evaluation result or a 'failed' marker.
"""

import logging
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.interview_answer import AnswerEvaluationStatus, InterviewAnswer
from app.models.interview_question import InterviewQuestion
from app.models.interview_session import (
    InterviewSession,
    InterviewSessionStatus,
    QuestionDifficulty,
    QuestionType,
)
from app.schemas.interview import InterviewAnswerCreate, InterviewSessionCreate
from app.services.evaluation_service import evaluate_answer
from app.services.question_generation_service import generate_questions

logger = logging.getLogger(__name__)


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


async def submit_answer(
    db: AsyncSession,
    user_id: uuid.UUID,
    session_id: uuid.UUID,
    payload: InterviewAnswerCreate,
) -> InterviewAnswer:
    """Persist an answer, then run the evaluator synchronously.

    The answer row is committed before the evaluator runs so a failure mid-
    eval still leaves the user's answer on disk. If the evaluator raises,
    we mark the row 'failed' (not 'completed') so the client can retry.
    """
    session = await get_session_by_id(db, session_id, user_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found",
        )

    question = await db.scalar(
        select(InterviewQuestion).where(
            InterviewQuestion.id == payload.question_id,
            InterviewQuestion.session_id == session_id,
        )
    )
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found in this session",
        )

    if session.status == InterviewSessionStatus.not_started:
        session.status = InterviewSessionStatus.in_progress

    answer = InterviewAnswer(
        session_id=session_id,
        question_id=payload.question_id,
        answer_text=payload.answer_text,
        evaluation_status=AnswerEvaluationStatus.evaluating,
    )
    db.add(answer)
    await db.flush()  # populate answer.id
    await db.commit()  # persist before the slow evaluator call

    try:
        eval_data = await evaluate_answer(
            question_text=question.question,
            question_type=question.type.value,
            difficulty=question.difficulty.value,
            rationale=question.rationale,
            anchor=question.anchor,
            answer_text=payload.answer_text,
        )
        answer.evaluation_json = eval_data
        answer.evaluation_status = AnswerEvaluationStatus.completed
        answer.evaluator_model = "gpt-4o-mini"  # match _MODEL in evaluation_service
    except Exception as exc:
        logger.exception("Evaluation failed for answer %s: %s", answer.id, exc)
        answer.evaluation_status = AnswerEvaluationStatus.failed

    await db.commit()
    await db.refresh(answer)
    return answer


async def list_answers(
    db: AsyncSession,
    user_id: uuid.UUID,
    session_id: uuid.UUID,
) -> list[InterviewAnswer]:
    """List all answers for a session, oldest first.

    Verifies session ownership; 404 if the session doesn't exist or isn't
    owned by user_id.
    """
    session = await get_session_by_id(db, session_id, user_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found",
        )

    result = await db.scalars(
        select(InterviewAnswer)
        .where(InterviewAnswer.session_id == session_id)
        .order_by(InterviewAnswer.created_at.asc())
    )
    return list(result)
