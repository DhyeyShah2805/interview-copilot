"""
Importing this package registers every model class on Base.metadata,
which is what Alembic autogenerate walks.
"""

from app.models.interview_question import InterviewQuestion
from app.models.interview_session import (
    InterviewSession,
    InterviewSessionStatus,
    QuestionDifficulty,
    QuestionType,
)
from app.models.job_description import JobDescription
from app.models.resume import ParseStatus, Resume
from app.models.resume_chunk import ResumeChunk
from app.models.user import User

__all__ = [
    "InterviewQuestion",
    "InterviewSession",
    "InterviewSessionStatus",
    "JobDescription",
    "ParseStatus",
    "QuestionDifficulty",
    "QuestionType",
    "Resume",
    "ResumeChunk",
    "User",
]
