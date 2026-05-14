"""
ResumeChunk — a slice of resume text plus its 1536-d embedding for RAG.
"""

import uuid
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.resume import Resume


class ResumeChunk(Base):
    __tablename__ = "resume_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)

    resume: Mapped["Resume"] = relationship(back_populates="chunks")

    def __repr__(self) -> str:
        return f"<ResumeChunk resume={self.resume_id} idx={self.chunk_index}>"
