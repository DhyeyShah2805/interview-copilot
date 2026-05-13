# Interview Copilot

An AI-powered interview preparation platform that personalizes mock interviews from a user's resume and target job description, then evaluates responses with a structured rubric.

> 🚧 **Status:** Active development. Target v1 launch: May 28, 2026.

---

## What it does

1. User uploads their resume PDF and pastes a target job description.
2. The system extracts skills, identifies gaps, and generates personalized interview questions (behavioral + technical, role-aware).
3. User goes through a streaming mock interview with an AI interviewer.
4. Every answer is scored against a fixed rubric (STAR structure, clarity, technical depth, relevance).
5. Dashboard surfaces weak areas and improvement trends across sessions.

See [`docs/PRD/PRD.md`](./docs/PRD/PRD.md) for the full product spec.
See [`docs/SystemDesign/`](./docs/SystemDesign/) for architecture.

## Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Frontend | Next.js 14 (App Router) + Tailwind + shadcn/ui | Fast iteration, great DX, Vercel-native |
| Backend | FastAPI (async) + Pydantic v2 | Best Python ecosystem for AI integrations |
| Database | Postgres 16 + pgvector | Relational + vector search in one engine |
| AI | OpenAI API (primary) + Claude API (evaluation) | Best-in-class for generation and scoring |
| Auth | JWT + refresh tokens | Simple, stateless, sufficient for v1 |
| Deploy | Vercel (web) + Railway (api + db) | Lowest-friction prod setup |

Full rationale in [`docs/DecisionLogs/`](./docs/DecisionLogs/).

## Repo structure

```
.
├── apps/
│   ├── api/         FastAPI backend
│   └── web/         Next.js frontend
├── docs/            Engineering documentation (PRD, design, decisions)
├── docker-compose.yml
└── README.md
```

## Quick start

Requirements: Docker Desktop, Node 20+, Python 3.11+

```bash
# 1. Clone and enter
git clone https://github.com/<you>/interview-copilot.git
cd interview-copilot

# 2. Copy env files and fill in OPENAI_API_KEY, ANTHROPIC_API_KEY
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local

# 3. Start Postgres + API
docker-compose up -d

# 4. Run migrations (after the API container is up)
docker-compose exec api alembic upgrade head

# 5. Start the frontend
cd apps/web
npm install
npm run dev

# Visit http://localhost:3000
```

Check API health: `curl http://localhost:8000/health`

## Roadmap

- **v1 (May 28, 2026)** — Core flow: resume upload, RAG-grounded questions, text mock interview, evaluation, dashboard
- **v1.1** — Voice mode (STT + TTS), company-specific question packs
- **v1.2** — Live coding sandbox, exportable PDF reports

## License

MIT — see [LICENSE](./LICENSE)
