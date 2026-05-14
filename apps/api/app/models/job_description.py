"""
JobDescription model.

The target role a user is preparing for. Drives question generation and
resume-job matching.
"""

import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.resume import ParseStatus

if TYPE_CHECKING:
    from app.models.user import User


class JobDescription(Base):
    __tablename__ = "job_descriptions"

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
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    # The Postgres ENUM type "parse_status" is owned by resumes.parse_status;
    # create_type=False prevents Alembic from emitting a duplicate CREATE TYPE.
    parse_status: Mapped[ParseStatus] = mapped_column(
        sa.Enum(ParseStatus, name="parse_status", create_type=False),
        default=ParseStatus.pending,
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="job_descriptions")

    def __repr__(self) -> str:
        return f"<JobDescription {self.title}>"
