"""
Request/response schemas for interview generation and persisted sessions.

The shape of GeneratedQuestion mirrors the OpenAI structured-output schema
defined in app.services.question_generation_service — keep both sides in
sync if you change a field.
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

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


class InterviewSessionCreate(BaseModel):
    resume_id: uuid.UUID
    job_description_id: uuid.UUID
    num_questions: int = Field(default=8, ge=4, le=12)


class InterviewQuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_index: int
    question: str
    type: str
    rationale: str
    difficulty: str
    anchor: str


class InterviewSessionRead(BaseModel):
    # protected_namespaces=() silences Pydantic v2's "model_" reserved-prefix
    # warning for the model_used field.
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: uuid.UUID
    resume_id: uuid.UUID
    job_description_id: uuid.UUID
    status: str
    model_used: str
    num_questions: int
    created_at: datetime
    questions: list[InterviewQuestionRead]


class InterviewSessionListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: uuid.UUID
    resume_id: uuid.UUID
    job_description_id: uuid.UUID
    status: str
    num_questions: int
    created_at: datetime
