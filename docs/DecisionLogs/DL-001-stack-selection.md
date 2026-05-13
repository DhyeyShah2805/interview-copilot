# DL-001: Stack selection

**Date:** 2026-05-13
**Status:** Accepted
**Author:** Dhyey Shah

## Context

Building the v1 of Interview Copilot solo, with a 16-day timeline ending May 28, 2026. Skill level: full-stack tutorials experience but no production deploys. Goal: a portfolio-grade AI product that holds up under recruiter and interviewer scrutiny.

Three forces are in tension:

1. **Speed** — every framework I don't already know costs me a day.
2. **AI ecosystem maturity** — the chosen language must have first-class SDKs for OpenAI and Anthropic, plus libraries for PDF parsing, embeddings, and vector search.
3. **Recruiter legibility** — the stack should match what FAANG and AI-first startups actually use, not something exotic.

## Options considered

### Backend

| Option | For | Against |
|--------|-----|---------|
| FastAPI (chosen) | Best-in-class async Python; mature AI SDK ecosystem; Pydantic-driven type safety; fast to learn from tutorials | Python deploys slightly heavier than Node |
| Node.js + Express/Hono | Same language as frontend; lighter deploys | Anthropic and OpenAI SDKs feel less native than in Python; weaker scientific tooling for future features |
| Go | Fast, strongly typed | AI/ML ecosystem is thin; would slow me down significantly |

### Database + vector store

| Option | For | Against |
|--------|-----|---------|
| Postgres + pgvector (chosen) | Single engine for relational + vector; Railway includes it; zero extra cost; sufficient up to ~1M vectors | Worse than dedicated vector DBs at very large scale |
| Pinecone | Best-in-class vector search; fast | Extra service to manage; cost; overkill for v1 scale; another auth surface |
| Weaviate | Open source; rich schema | More moving parts; slower local dev |

### Frontend

Next.js 14 (App Router) is uncontested for this scope — best DX, native Vercel deploy, streaming support for AI responses out of the box.

### Deployment

| Surface | Choice | Why |
|---------|--------|-----|
| Frontend | Vercel | Native Next.js; global edge; free tier sufficient |
| Backend + DB | Railway | Postgres + pgvector + app in one private network; sub-10ms DB latency |
| Alternative considered | Render | Roughly equivalent; Railway picked for simpler Postgres setup |

## Decision

**FastAPI + Postgres (with pgvector) + Next.js 14, deployed on Railway + Vercel.**

## Consequences

**Positive**

- Single language (Python) for all AI integration code keeps prompts, evaluation, and orchestration in one place.
- pgvector means I never have to context-switch to a separate vector DB UI or worry about syncing user data with embeddings.
- Both deploy targets have generous free tiers that cover the launch period and likely several months after.

**Negative / tradeoffs accepted**

- If user load ever requires sub-50ms vector retrieval over millions of resumes, pgvector will need to be replaced. Acceptable: v1 won't see that scale.
- Python is slightly slower to cold-start than Node. Acceptable: backend is long-running on Railway, not serverless.

**Reversibility**

- High. Swapping pgvector for Pinecone is a one-file change in the retrieval service. Swapping Railway for Render is a redeploy. The architecture doesn't lock me in.

## Follow-ups

- [ ] Set up Railway project and run a hello-world deploy by end of Day 1 (de-risks deployment late in the timeline).
- [ ] Add a DL-002 entry once auth design is finalized.
