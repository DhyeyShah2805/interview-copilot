# System Design

> Living document — updated whenever the architecture changes.

## Overview

Interview Copilot is a three-tier web app:

1. **Next.js frontend** on Vercel — handles all UI, talks to the backend over HTTP/SSE.
2. **FastAPI backend** on Railway — handles auth, business logic, AI orchestration, and persistence.
3. **Postgres with pgvector** on Railway — single store for relational data (users, sessions, messages) and embeddings (resume chunks, JD chunks).

External dependencies: OpenAI API (question generation, embeddings) and Anthropic Claude API (evaluation).

## Architecture diagram

_(Insert the SVG architecture diagram here. Export from the Claude conversation or recreate in Excalidraw.)_

## Data flow — resume upload through interview

1. User uploads a PDF in the browser.
2. Next.js sends a `POST /resumes` with the file.
3. FastAPI saves the upload, kicks off a `BackgroundTask` to parse and chunk it.
4. The background task uses `pypdf` to extract text, splits it into 500-token chunks, embeds each chunk via OpenAI `text-embedding-3-small`, and stores them in Postgres with `pgvector`.
5. When the user starts an interview, the backend retrieves the top-k relevant chunks for each question type (technical, behavioral, role-specific) and includes them in the prompt to the LLM.
6. The LLM streams its question back through FastAPI to the frontend over Server-Sent Events.
7. After the user submits an answer, a separate evaluator prompt scores it against a fixed rubric and returns structured JSON.

## Scalability considerations (v1)

- Async I/O end-to-end means a single FastAPI worker handles hundreds of concurrent users without blocking.
- pgvector with HNSW index keeps retrieval under 50ms up to ~1M chunks.
- Streaming responses keep perceived latency under 1.5s even when total generation takes 6–8s.

## Failure handling

- **PDF parse fails** — return a clear error to the user, log the failure, keep the upload for debugging.
- **LLM API rate limit** — exponential backoff with jitter; surface a "retrying" state to the user after 2s.
- **DB connection lost** — `pool_pre_ping` reconnects automatically; `/ready` endpoint will report `degraded` so Railway can restart if needed.

## Future work

See [`docs/PRD/PRD.md`](../PRD/PRD.md) §12 for v1.1+ scope.
