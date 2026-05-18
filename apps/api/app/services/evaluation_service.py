"""
AI evaluator for interview answers.

Scores a candidate's typed answer against a 4-dimension rubric (clarity,
structure, depth, relevance) plus a computed overall score and qualitative
feedback, returned as a plain dict ready to drop into
InterviewAnswer.evaluation_json. The service is intentionally ORM-free:
callers pass primitives (question text, type, difficulty, rationale,
anchor, answer text) and receive a dict.
"""

import json
import logging

import openai
from openai import AsyncOpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings

_client = AsyncOpenAI(api_key=settings.openai_api_key)
_MODEL = "gpt-4o-mini"
logger = logging.getLogger(__name__)


_EVALUATION_SCHEMA = {
    "name": "answer_evaluation",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "clarity": {"type": "integer", "minimum": 0, "maximum": 5},
            "structure": {"type": "integer", "minimum": 0, "maximum": 5},
            "depth": {"type": "integer", "minimum": 0, "maximum": 5},
            "relevance": {"type": "integer", "minimum": 0, "maximum": 5},
            "overall_score": {"type": "number", "minimum": 0, "maximum": 5},
            "strengths": {"type": "array", "items": {"type": "string"}},
            "weaknesses": {"type": "array", "items": {"type": "string"}},
            "suggested_improvement": {"type": "string"},
        },
        "required": [
            "clarity",
            "structure",
            "depth",
            "relevance",
            "overall_score",
            "strengths",
            "weaknesses",
            "suggested_improvement",
        ],
        "additionalProperties": False,
    },
}


_SYSTEM_PROMPT = """You are a senior engineering interviewer at a top tech company evaluating a candidate's answer. Provide structured, actionable feedback. Be honest — don't grade-inflate.

Score the answer on four dimensions, each 0-5:

CLARITY (0-5): Is the answer well-structured and easy to follow? Free of rambling, filler, or tangents?
  0 = incoherent or hard to parse
  3 = understandable but could be tighter
  5 = crisp, well-organized, easy to follow

STRUCTURE (0-5): Does the answer use appropriate framing for its type?
  - behavioral: did it follow STAR (Situation, Task, Action, Result)?
  - technical_concept: logical flow (definition → mechanism → tradeoffs)?
  - technical_project: problem → approach → tradeoffs → result?

DEPTH (0-5):
  - behavioral: specificity and concrete details (numbers, names, decisions made)
  - technical_concept: technical accuracy and depth of understanding
  - technical_project: shows real ownership vs surface-level recall

RELEVANCE (0-5): Did the answer actually address what was asked? Not off-topic or just adjacent?

Then compute:
  overall_score = weighted average:
    clarity * 0.20 + structure * 0.25 + depth * 0.30 + relevance * 0.25
  Round to 1 decimal place.

Then provide:
  strengths: 1-3 specific things the answer did well (each one a short sentence)
  weaknesses: 1-3 specific things to improve (each one a short sentence)
  suggested_improvement: 1-2 sentences of concrete, actionable advice

GROUNDING IN THE RESUME ANCHOR
The question is grounded in a verbatim phrase from the candidate's resume (the "anchor"). This means the question is asking about something the candidate actually did — not hypothetically. The answer must demonstrate real ownership of that specific work, not substitute a generic framing that could apply to anyone. If the answer ignores the anchored experience, gives a textbook response without referencing their own work, or contradicts what's stated in the anchor — that's a significant DEPTH and RELEVANCE penalty.

Calibration: most real-interview answers score 2-3. A 4 is a genuinely strong answer. A 5 is exceptional. Reserve high scores accordingly. If the candidate says "I don't know" or gives a non-answer, score low across all dimensions and explain.
"""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((openai.APIError, openai.APIConnectionError)),
)
async def evaluate_answer(
    question_text: str,
    question_type: str,
    difficulty: str,
    rationale: str,
    anchor: str,
    answer_text: str,
) -> dict:
    """Score a candidate's answer against the 4-dimension rubric.

    Returns the raw structured-output dict so callers can persist it
    directly into InterviewAnswer.evaluation_json. Retries only on
    transient OpenAI failures; everything else propagates.
    """
    user_message = f"""QUESTION (type: {question_type}, difficulty: {difficulty})
{question_text}

WHY THIS QUESTION WAS ASKED
Rationale: {rationale}
Anchor (verbatim from candidate's resume): "{anchor}"

CANDIDATE'S ANSWER
{answer_text}

Evaluate this answer per the rubric. Return the structured JSON."""

    response = await _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_schema", "json_schema": _EVALUATION_SCHEMA},
        temperature=0.3,  # lower than question gen — we want consistent scoring
    )

    data = json.loads(response.choices[0].message.content)
    logger.info(
        "Evaluated answer: clarity=%d structure=%d depth=%d relevance=%d overall=%.1f",
        data["clarity"],
        data["structure"],
        data["depth"],
        data["relevance"],
        data["overall_score"],
    )
    return data
