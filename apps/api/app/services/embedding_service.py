"""
Embedding generation via OpenAI.

text-embedding-3-small -> 1536-dim vectors, matching ResumeChunk.embedding.
Retries on transient API failures (tenacity, exponential backoff).
"""

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

_client = AsyncOpenAI(api_key=settings.openai_api_key)

_MODEL = "text-embedding-3-small"
_MAX_BATCH = 100


# TODO(v1.1): per-batch retry instead of whole-function retry once we
# regularly process documents with > 100 chunks.
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts, returning one 1536-float vector per input.

    Inputs longer than 100 items are split into batches of 100; results are
    concatenated in input order.
    """
    if not texts:
        return []

    embeddings: list[list[float]] = []
    for start in range(0, len(texts), _MAX_BATCH):
        batch = texts[start : start + _MAX_BATCH]
        response = await _client.embeddings.create(model=_MODEL, input=batch)
        # Sort by index defensively — the API returns results in input order,
        # but we don't want to rely on that silently.
        ordered = sorted(response.data, key=lambda item: item.index)
        embeddings.extend(item.embedding for item in ordered)

    return embeddings
