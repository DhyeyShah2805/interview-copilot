"""
InterviewAnswer model.

Stores the candidate's typed answer to a specific InterviewQuestion plus
the AI-graded evaluation. evaluation_json is populated asynchronously after
the grading pipeline completes; until then evaluation_status tracks where
it sits in the queue.
"""

import enum
import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.interview_question import InterviewQuestion
    from app.models.interview_session import InterviewSession


class AnswerEvaluationStatus(str, enum.Enum):
    pending = "pending"
    evaluating = "evaluating"
    completed = "completed"
    failed = "failed"


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_questions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    evaluation_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    evaluation_status: Mapped[AnswerEvaluationStatus] = mapped_column(
        sa.Enum(AnswerEvaluationStatus, name="answer_evaluation_status"),
        default=AnswerEvaluationStatus.pending,
        nullable=False,
    )
    evaluator_model: Mapped[str | None] = mapped_column(String(64), nullable=True)

    session: Mapped["InterviewSession"] = relationship(back_populates="answers")
    question: Mapped["InterviewQuestion"] = relationship(back_populates="answers")

    def __repr__(self) -> str:
        return f"<InterviewAnswer {self.id} status={self.evaluation_status.value}>"
