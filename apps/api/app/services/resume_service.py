"""
Resume service layer.

Route handlers stay thin — all DB queries, file I/O, and the resume parse
pipeline (extract -> chunk -> embed -> store) live here.
"""

import asyncio
import logging
import uuid
from pathlib import Path

import sqlalchemy as sa
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.resume import ParseStatus, Resume
from app.models.resume_chunk import ResumeChunk
from app.services.chunking_service import chunk_text
from app.services.embedding_service import embed_texts
from app.services.pdf_service import extract_text_from_pdf

logger = logging.getLogger(__name__)

_CHUNK_SIZE = 8 * 1024  # 8 KB


async def save_uploaded_file(
    file: UploadFile,
    resume_id: uuid.UUID,
    upload_dir: str,
    max_bytes: int,
) -> tuple[int, str]:
    """Stream an upload to disk in 8 KB chunks, enforcing a size ceiling.

    Returns (bytes_written, file_path). On overflow the partial file is
    removed before raising.
    """
    Path(upload_dir).mkdir(parents=True, exist_ok=True)
    dest = Path(upload_dir) / f"{resume_id}.pdf"

    total = 0
    try:
        with dest.open("wb") as out:
            while True:
                chunk = await file.read(_CHUNK_SIZE)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File exceeds max size",
                    )
                out.write(chunk)
    except HTTPException:
        dest.unlink(missing_ok=True)
        raise

    return total, str(dest)


async def get_resume_by_id(
    db: AsyncSession, resume_id: uuid.UUID, user_id: uuid.UUID
) -> Resume | None:
    return await db.scalar(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
    )


async def list_resumes_for_user(
    db: AsyncSession, user_id: uuid.UUID
) -> list[Resume]:
    result = await db.scalars(
        select(Resume)
        .where(Resume.user_id == user_id)
        .order_by(Resume.created_at.desc())
    )
    return list(result)


async def parse_resume(resume_id: uuid.UUID, file_path: str) -> None:
    """Full resume processing pipeline, run as a background task.

    extract text -> chunk -> embed -> store chunks. Atomic: any failure marks
    the resume 'failed' and rolls back first, so no partial chunks are ever
    committed. Opens its own session — the request's session is long closed
    by the time this runs.
    """
    async with AsyncSessionLocal() as db:
        try:
            resume = await db.get(Resume, resume_id)
            if resume is None:
                logger.error("Resume %s not found; aborting parse", resume_id)
                return

            resume.parse_status = ParseStatus.processing
            await db.commit()

            # pypdf is synchronous — run it off the event loop.
            text = await asyncio.to_thread(extract_text_from_pdf, file_path)
            resume.raw_text = text
            await db.commit()

            chunks = chunk_text(text)
            if not chunks:
                raise ValueError("Chunking produced zero chunks")
            embeddings = await embed_texts(chunks)
            assert len(embeddings) == len(chunks), (
                f"Embedding count {len(embeddings)} != chunk count {len(chunks)}"
            )

            for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                db.add(
                    ResumeChunk(
                        resume_id=resume_id,
                        content=chunk,
                        chunk_index=i,
                        embedding=emb,
                    )
                )

            resume.parse_status = ParseStatus.completed
            await db.commit()
        except Exception as exc:
            logger.exception("Resume %s parse failed: %s", resume_id, exc)
            # Discard any pending ResumeChunk inserts so the 'failed' update
            # commits cleanly and we don't persist a half-processed resume.
            await db.rollback()
            try:
                resume = await db.get(Resume, resume_id)
                if resume:
                    resume.parse_status = ParseStatus.failed
                    await db.commit()
            except Exception:
                await db.rollback()


async def search_chunks(
    db: AsyncSession,
    resume_id: uuid.UUID,
    user_id: uuid.UUID,
    query_text: str,
    top_k: int = 5,
) -> list[dict]:
    """Return the top-k most similar chunks for a query, scoped to one resume.

    Ownership is re-verified here so the function is safe to call standalone.
    Similarity is cosine similarity in [0, 1] — higher is a better match.
    """
    resume = await get_resume_by_id(db, resume_id, user_id)
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )

    query_embedding = (await embed_texts([query_text]))[0]
    # pgvector accepts a bracketed literal; cast it to `vector` in-query so we
    # don't depend on a type adapter being registered on the raw connection.
    query_vec = "[" + ",".join(str(x) for x in query_embedding) + "]"

    sql = sa.text(
        """
        SELECT chunk_index,
               content,
               1 - (embedding <=> CAST(:query_vec AS vector)) AS similarity
        FROM resume_chunks
        WHERE resume_id = :resume_id
        ORDER BY embedding <=> CAST(:query_vec AS vector)
        LIMIT :top_k
        """
    )
    result = await db.execute(
        sql,
        {"query_vec": query_vec, "resume_id": resume_id, "top_k": top_k},
    )
    return [
        {
            "chunk_index": row.chunk_index,
            "content": row.content,
            "similarity": row.similarity,
        }
        for row in result
    ]
