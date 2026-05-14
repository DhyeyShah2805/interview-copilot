"""
Resume model.

A resume belongs to a user and is split into chunks for embedding-based
retrieval. parse_status tracks the async parse/chunk/embed pipeline.
"""

import enum
import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.resume_chunk import ResumeChunk
    from app.models.user import User


class ParseStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Resume(Base):
    __tablename__ = "resumes"

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
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parse_status: Mapped[ParseStatus] = mapped_column(
        sa.Enum(ParseStatus, name="parse_status"),
        default=ParseStatus.pending,
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="resumes")
    chunks: Mapped[list["ResumeChunk"]] = relationship(
        back_populates="resume",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Resume {self.filename}>"
