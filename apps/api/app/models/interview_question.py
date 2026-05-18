"""
InterviewQuestion — one question inside an InterviewSession.
"""

import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.interview_session import QuestionDifficulty, QuestionType

if TYPE_CHECKING:
    from app.models.interview_answer import InterviewAnswer
    from app.models.interview_session import InterviewSession


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

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
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[QuestionType] = mapped_column(
        sa.Enum(QuestionType, name="question_type"),
        nullable=False,
    )
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[QuestionDifficulty] = mapped_column(
        sa.Enum(QuestionDifficulty, name="question_difficulty"),
        nullable=False,
    )
    anchor: Mapped[str] = mapped_column(String(500), nullable=False)

    session: Mapped["InterviewSession"] = relationship(back_populates="questions")
    answers: Mapped[list["InterviewAnswer"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<InterviewQuestion {self.session_id}#{self.order_index}>"
