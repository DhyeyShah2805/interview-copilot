"""
Importing this package registers every model class on Base.metadata,
which is what Alembic autogenerate walks.
"""

from app.models.job_description import JobDescription
from app.models.resume import ParseStatus, Resume
from app.models.resume_chunk import ResumeChunk
from app.models.user import User

__all__ = [
    "JobDescription",
    "ParseStatus",
    "Resume",
    "ResumeChunk",
    "User",
]
