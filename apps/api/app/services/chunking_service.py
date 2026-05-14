"""
Token-aware text chunking for embedding.

Splits resume text into ~target_tokens chunks with a small overlap so
retrieval doesn't lose context at chunk boundaries. Uses the cl100k_base
tokenizer — the same one text-embedding-3-small uses — so token counts are
exact, not estimated.
"""

import re

import tiktoken

# cl100k_base is the tokenizer for text-embedding-3-small.
_encoder = tiktoken.get_encoding("cl100k_base")

# Heuristic sentence boundary: sentence punctuation followed by whitespace.
_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


def _count_tokens(text: str) -> int:
    return len(_encoder.encode(text))


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_BOUNDARY.split(text) if s.strip()]


def _split_by_token_window(text: str, window: int) -> list[str]:
    """Last-resort split: slice raw tokens into fixed-size windows."""
    tokens = _encoder.encode(text)
    return [
        _encoder.decode(tokens[start : start + window])
        for start in range(0, len(tokens), window)
    ]


def _tail_tokens(text: str, n: int) -> str:
    """Return the trailing n tokens of text, decoded back to a string."""
    if n <= 0:
        return ""
    tokens = _encoder.encode(text)
    if len(tokens) <= n:
        return text
    return _encoder.decode(tokens[-n:])


def _segment(text: str, target_tokens: int) -> list[str]:
    """Break text into segments that each fit within target_tokens.

    paragraph -> (if too big) sentences -> (if still too big) token windows.
    """
    segments: list[str] = []
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    for para in paragraphs:
        if _count_tokens(para) <= target_tokens:
            segments.append(para)
            continue
        for sentence in _split_sentences(para):
            if _count_tokens(sentence) <= target_tokens:
                segments.append(sentence)
            else:
                segments.extend(_split_by_token_window(sentence, target_tokens))
    return segments


def chunk_text(
    text: str,
    target_tokens: int = 500,
    overlap_tokens: int = 50,
) -> list[str]:
    """Chunk text into ~target_tokens pieces with overlap_tokens of overlap.

    Paragraphs are greedily packed into chunks. Oversized paragraphs are split
    by sentence, and oversized sentences by raw token window. Each chunk after
    the first is seeded with the tail of the previous chunk so context carries
    across boundaries.
    """
    segments = _segment(text, target_tokens)
    if not segments:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0
    has_real_segment = False  # current holds >= 1 non-overlap segment

    for seg in segments:
        seg_tokens = _count_tokens(seg)
        if has_real_segment and current_tokens + seg_tokens > target_tokens:
            chunk_str = "\n\n".join(current)
            chunks.append(chunk_str)
            overlap = _tail_tokens(chunk_str, overlap_tokens)
            current = [overlap] if overlap else []
            current_tokens = _count_tokens(overlap) if overlap else 0
            has_real_segment = False
        current.append(seg)
        current_tokens += seg_tokens
        has_real_segment = True

    if has_real_segment:
        chunks.append("\n\n".join(current))

    return chunks
