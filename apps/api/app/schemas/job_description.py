"""
Request/response schemas for job description endpoints.

Kept separate from the ORM models — keeps the wire format stable and lets
us tighten per-endpoint validation (min/max lengths) here.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobDescriptionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    company: str | None = Field(default=None, max_length=255)
    raw_text: str = Field(min_length=10)


class JobDescriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    company: str | None
    raw_text: str
    parse_status: str
    created_at: datetime


class JobDescriptionListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    company: str | None
    created_at: datetime
