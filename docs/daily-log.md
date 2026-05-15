# Daily Log

## Day 1 — May 13, 2026

### Completed
- Verified scaffold boots cleanly: Docker, FastAPI API, Next.js frontend, all green
- Upgraded Next.js 14.2.15 → 16.2.6 and React 18 → 19 to patch May 2026 CVEs
- Fixed Turbopack monorepo workspace root inference
- Removed deprecated `baseUrl` from tsconfig
- Replaced author placeholders across LICENSE, PRD, DL-001
- Initialized Alembic with async template, wired env.py to read from `app.core.config`
- Wrote first migration to enable pgvector extension
- Generated and applied `users` table migration
- Hit and resolved bcrypt 4.1+ vs passlib 1.7.4 incompatibility (pinned bcrypt==4.0.1)
- Tested register + login end-to-end via Swagger UI — auth flow live
- Added Resume, JobDescription, ResumeChunk SQLAlchemy models with cascading FKs and shared `parse_status` enum
- Generated and applied second migration; all 5 tables verified in DB
- Added decision logs DL-002 (Next 16 upgrade), DL-003 (audit findings triage), DL-004 (bcrypt pin)

### Notes / what surprised me
- Day 1 was 60% engineering, 40% supply-chain triage (npm audit warnings, Turbopack quirks, framework upgrades). Realized "the deps don't fight you" is something you build *toward*, not something that comes free.
- Found out the hard way that passlib hasn't been updated since 2020. Replacing it is on the v1.1 list.
- Reading auto-generated migration files closely caught a missing pgvector import — would have blown up the migration. The 30 seconds of review saved an hour of debugging.

### Tomorrow (Day 2)
- Build POST /resumes endpoint accepting PDF upload via FastAPI's UploadFile
- Implement async PDF parsing + token-aware chunking pipeline (pypdf + tiktoken)
- Generate embeddings via OpenAI `text-embedding-3-small` and store in pgvector
- Verify end-to-end with a real resume PDF — upload, parse, chunk, embed, retrieve top-k by similarity

## Day 2 — May 14, 2026

### Completed
- Added uploads volume and HNSW index migration (HNSW deferred — not needed at current scale)
- Built POST /resumes with HTTPBearer auth, file size + content-type validation, BackgroundTasks for async processing
- Built end-to-end parsing pipeline: pypdf extraction → tiktoken chunking → OpenAI text-embedding-3-small → pgvector storage
- Added structured error handling with rollback on failure; ParseStatus enum transitions atomic
- Added GET /resumes/{id}/search returning top-k chunks ranked by cosine similarity
- Tested end-to-end with own resume: parse → 3 chunks @ 1536 dims → semantic search returns relevant chunks

### Notes / what surprised me
- Spent ~2 hours debugging an "APIConnectionError" that was actually "API key was empty in container." Docker compose substitutes ${VAR} from project-root .env, not apps/api/.env. Two .env files, two different consumers.
- bcrypt 4.1+ vs passlib 1.7.4 → bcrypt 4.0.1 pin (caught on Day 1 too)
- Cosine similarity scores for text-embedding-3-small cluster in 0.2-0.5 for relevant matches. Relative ordering is what matters for RAG, not absolute scores.

### Tomorrow (Day 3)
- Build POST /job-descriptions with same parsing pipeline
- Add resume + JD skill-gap extraction service (LLM-driven JSON output)
- Update GET /resumes/{id} response to include chunk count and processing duration