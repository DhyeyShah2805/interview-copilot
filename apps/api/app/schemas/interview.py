"""
Request/response schemas for interview generation.

The shape of GeneratedQuestion mirrors the OpenAI structured-output schema
defined in app.services.question_generation_service — keep both sides in
sync if you change a field.
"""

import uuid
from typing import Literal

from pydantic import BaseModel, Field

QuestionType = Literal["behavioral", "technical_concept", "technical_project"]
QuestionDifficulty = Literal["easy", "medium", "hard"]


class GeneratedQuestion(BaseModel):
    question: str
    type: QuestionType
    rationale: str  # 1-2 sentences explaining why this question
    difficulty: QuestionDifficulty
    anchor: str  # short verbatim phrase from resume this targets


class InterviewPreviewRequest(BaseModel):
    resume_id: uuid.UUID
    job_description_id: uuid.UUID
    num_questions: int = Field(default=8, ge=4, le=12)


class InterviewPreviewResponse(BaseModel):
    resume_id: uuid.UUID
    job_description_id: uuid.UUID
    questions: list[GeneratedQuestion]
    num_resume_chunks_used: int
    model: str
