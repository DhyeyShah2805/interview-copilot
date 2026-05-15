"""
Request/response schemas for resume endpoints.

Kept separate from the ORM models — the wire format exposes only what the
frontend needs, never raw_text or embeddings.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    parse_status: str
    created_at: datetime


class ResumeListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    parse_status: str
    created_at: datetime


class ResumeChunkMatch(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    chunk_index: int
    content: str
    similarity: float  # cosine similarity, higher is better (0.0–1.0)
