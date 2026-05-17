"""
Interview question generation via OpenAI structured outputs.

Pulls the top-k most relevant resume chunks for the JD (using the existing
RAG retrieval), then prompts gpt-4o-mini with a strict JSON schema so the
caller always gets parseable, well-typed questions back.
"""

import json
import logging
import uuid

import openai
from fastapi import HTTPException, status
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from app.models.resume import ParseStatus
from app.schemas.interview import GeneratedQuestion, InterviewPreviewResponse
from app.services.job_description_service import get_job_description
from app.services.resume_service import get_resume_by_id, search_chunks

_client = AsyncOpenAI(api_key=settings.openai_api_key)
_MODEL = "gpt-4o-mini"
logger = logging.getLogger(__name__)


_QUESTION_SCHEMA = {
    "name": "interview_questions",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "type": {
                            "type": "string",
                            "enum": [
                                "behavioral",
                                "technical_concept",
                                "technical_project",
                            ],
                        },
                        "rationale": {"type": "string"},
                        "difficulty": {
                            "type": "string",
                            "enum": ["easy", "medium", "hard"],
                        },
                        "anchor": {"type": "string"},
                    },
                    "required": [
                        "question",
                        "type",
                        "rationale",
                        "difficulty",
                        "anchor",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["questions"],
        "additionalProperties": False,
    },
}


_SYSTEM_PROMPT = """You are a senior engineering interviewer at a top tech company conducting a real interview.

Generate personalized interview questions based on a candidate's actual resume and the specific job they're applying for. Each question must:

- Reference something specific from the candidate's resume. The anchor MUST be a verbatim substring from the RESUME EXCERPTS section, not from the job description. If you cannot find a resume phrase to anchor a question, do not generate that question — produce one fewer.
- Probe a competency the job description actually cares about
- Be a question a real interviewer would ask, not a generic prompt

Question type distribution: For 8 questions: exactly 3 behavioral, 4 technical_project, 1 technical_concept. For other counts, scale proportionally.

Difficulty: Question 1 must always be an 'easy' difficulty warm-up — typically anchored to education, an early role, or a foundational skill on the resume. The remaining questions follow the normal medium-heavy distribution (most medium, 1-2 hard stretch questions).

NEVER generate:
- "Tell me about yourself" or any opener-style question
- "What's your biggest weakness/strength"
- Generic STAR prompts not grounded in the resume
- Questions about projects/skills not mentioned in the resume excerpts"""


@retry(
    retry=retry_if_exception_type((openai.APIError, openai.APIConnectionError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
async def generate_questions(
    db: AsyncSession,
    resume_id: uuid.UUID,
    job_description_id: uuid.UUID,
    user_id: uuid.UUID,
    num_questions: int = 8,
) -> InterviewPreviewResponse:
    """Generate personalized interview questions for a (resume, JD) pair.

    Verifies ownership of both records, ensures the resume has been parsed,
    pulls the top-6 most-relevant resume chunks via RAG, and asks gpt-4o-mini
    to produce a structured set of questions. Retries only on transient
    OpenAI failures — HTTPException (404/409) propagates immediately.
    """
    resume = await get_resume_by_id(db, resume_id, user_id)
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )

    jd = await get_job_description(db, job_description_id, user_id)
    if jd is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found"
        )

    if resume.parse_status != ParseStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Resume not ready (status: {resume.parse_status})",
        )

    chunks = await search_chunks(
        db, resume_id, user_id, query_text=jd.raw_text, top_k=6
    )
    if not chunks:
        raise HTTPException(
            status_code=500,
            detail="No chunks found for a completed resume — possible data inconsistency",
        )

    chunks_text = "\n\n".join(
        f"--- Excerpt {i + 1} ---\n{c['content']}" for i, c in enumerate(chunks)
    )
    user_message = f"""JOB DESCRIPTION
Title: {jd.title}
Company: {jd.company or 'Not specified'}

{jd.raw_text}

CANDIDATE'S RESUME — RELEVANT EXCERPTS
{chunks_text}

Generate exactly {num_questions} interview questions following all the rules in the system prompt."""

    response = await _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_schema", "json_schema": _QUESTION_SCHEMA},
        temperature=0.7,
    )

    data = json.loads(response.choices[0].message.content)
    logger.info(
        "Generated %d questions for resume=%s jd=%s model=%s",
        len(data["questions"]),
        resume_id,
        job_description_id,
        _MODEL,
    )

    return InterviewPreviewResponse(
        resume_id=resume_id,
        job_description_id=job_description_id,
        questions=[GeneratedQuestion(**q) for q in data["questions"]],
        num_resume_chunks_used=len(chunks),
        model=_MODEL,
    )
