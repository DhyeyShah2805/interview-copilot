"""
InterviewSession model.

A session captures one generated set of questions for a specific (resume, JD)
pair. The questions themselves live in InterviewQuestion rows.
"""

import enum
import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.interview_answer import InterviewAnswer
    from app.models.interview_question import InterviewQuestion
    from app.models.job_description import JobDescription
    from app.models.resume import Resume
    from app.models.user import User


class InterviewSessionStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    abandoned = "abandoned"


class QuestionType(str, enum.Enum):
    behavioral = "behavioral"
    technical_concept = "technical_concept"
    technical_project = "technical_project"


class QuestionDifficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    job_description_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_descriptions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[InterviewSessionStatus] = mapped_column(
        sa.Enum(InterviewSessionStatus, name="interview_session_status"),
        default=InterviewSessionStatus.not_started,
        nullable=False,
    )
    model_used: Mapped[str] = mapped_column(String(64), nullable=False)
    num_questions: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship(back_populates="interview_sessions")
    resume: Mapped["Resume"] = relationship(back_populates="interview_sessions")
    job_description: Mapped["JobDescription"] = relationship(
        back_populates="interview_sessions"
    )
    questions: Mapped[list["InterviewQuestion"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="InterviewQuestion.order_index",
    )
    answers: Mapped[list["InterviewAnswer"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<InterviewSession {self.id} status={self.status.value}>"
