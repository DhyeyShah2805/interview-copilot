"""
Request/response schema for answer evaluation.

EvaluationRubric mirrors the OpenAI structured-output schema defined in
app.services.evaluation_service — keep field names in sync if you change
one side.
"""

from pydantic import BaseModel, ConfigDict, Field


class EvaluationRubric(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    clarity: int = Field(ge=0, le=5)
    structure: int = Field(ge=0, le=5)
    depth: int = Field(ge=0, le=5)
    relevance: int = Field(ge=0, le=5)
    overall_score: float = Field(ge=0, le=5)
    strengths: list[str]
    weaknesses: list[str]
    suggested_improvement: str
