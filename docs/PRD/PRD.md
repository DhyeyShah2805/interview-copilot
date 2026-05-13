# AI Interview Copilot — Product Requirements Doc

**Author:** [Your name]
**Status:** Draft v1
**Target launch:** May 28, 2026
**Last updated:** May 12, 2026

---

## 1. Problem

Students and junior engineers preparing for technical interviews face three concrete problems:

1. **Generic prep.** Sites like LeetCode and Glassdoor give questions, not personalized prep tailored to *their* resume and *their* target role.
2. **No realistic practice loop.** Reading questions ≠ answering them under pressure. Most prep is passive.
3. **No feedback.** Even when users practice, they don't know if their answers are good, structured, or missing the mark.

The result: candidates walk into interviews under-prepared in ways they couldn't have predicted from their study materials.

## 2. Goal

Build an AI-powered interview preparation platform that:

- Generates **personalized** interview questions from a user's resume and a target job description.
- Simulates **realistic** mock interviews via a streaming chat experience.
- Returns **structured, actionable feedback** on every answer (clarity, STAR structure, technical depth, relevance).
- Tracks improvement over sessions so users can see weak areas trend.

## 3. Target users

Primary: CS students and junior SWEs (0–3 years) preparing for FAANG / AI-startup interviews.

Secondary: Career switchers preparing for first technical roles.

Out of scope (v1): senior engineers, non-technical roles, leadership interviews.

## 4. Core user journey

1. User signs up.
2. Uploads resume PDF + pastes target job description.
3. System parses resume, extracts skills/experience, matches against JD requirements, identifies gaps.
4. System generates a personalized question set (behavioral + technical, role-aware).
5. User starts a mock interview — streaming chat with an AI interviewer.
6. AI asks one question at a time, evaluates each response, asks follow-ups.
7. After the session, user sees a scorecard: per-question scores, weak areas, suggested focus.
8. Dashboard shows trends across sessions over time.

## 5. Core features (v1 — MUST ship by May 28)

| # | Feature | Why it matters |
|---|---------|---------------|
| F1 | Email/password auth (JWT) | Multi-session tracking requires accounts |
| F2 | Resume PDF upload + parsing | Foundation for personalization |
| F3 | Job description input + skill-gap extraction | Drives question relevance |
| F4 | RAG-grounded question generation | The core "personalized" value prop |
| F5 | Streaming chat mock interview (text) | Realistic practice loop |
| F6 | Structured evaluation per answer (rubric-based JSON) | Feedback that's actually useful |
| F7 | Session history + weak-area heatmap dashboard | Improvement tracking |

## 6. Stretch features (only if Days 14–15 have buffer)

- **S1** — Voice mode (STT in, TTS out) using Deepgram + ElevenLabs.
- **S2** — Company-specific question packs (Meta-style behavioral, Google-style system design).
- **S3** — Exportable PDF report after each session.

If S1 doesn't ship, list it in the README under "Roadmap" — this is a feature, not a failure.

## 7. Explicit non-goals

These are listed not to be coy — listing non-goals is *itself* a signal of engineering maturity to reviewers.

- ❌ Live coding interview simulation (whiteboard, code execution sandbox)
- ❌ Multi-user / collaborative interviews
- ❌ Mobile native app (web responsive only)
- ❌ Custom model training or fine-tuning
- ❌ Real-time video / facial analysis
- ❌ Payment / subscription system
- ❌ Microservices, Kubernetes, multi-region deploys
- ❌ Advanced auth (OAuth, MFA, SSO) — JWT only

## 8. Success metrics

**Engineering metrics (measurable in code/logs):**

- p50 question-generation latency < 3s, p95 < 6s
- Streaming first-token latency < 1.5s
- Evaluation JSON conforms to schema 100% of the time (structured output enforcement)
- Resume parsing succeeds on ≥95% of well-formed PDFs

**Product metrics (measurable post-launch):**

- ≥50% of users who upload a resume complete at least one mock interview
- Average session length ≥ 8 minutes (signal: it's engaging enough to stick with)

**Personal metrics (the real point of this project):**

- Polished GitHub repo with clean commit history
- Live deployed URL
- LinkedIn launch post with demo video
- 5 documentation artifacts (this PRD + 4 others)
- Resume bullet that survives recruiter scrutiny

## 9. Tech stack & rationale

(Full rationale lives in Decision Log — this is the summary.)

- **Frontend:** Next.js 14 (App Router) + Tailwind + shadcn/ui — Vercel deploy
- **Backend:** FastAPI (async) + Pydantic — Railway or Render deploy
- **DB:** Postgres + pgvector extension — bundled with backend host
- **AI:** OpenAI API for generation + embeddings; Claude API as fallback / for evaluation
- **Auth:** JWT with refresh tokens
- **Background work:** FastAPI `BackgroundTasks` (no Celery/Redis in v1)
- **PDF parsing:** `pypdf` for text extraction
- **Observability:** Structured logging + a simple `/health` endpoint. No Datadog/Grafana in v1.

## 10. Risk register

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| RAG returns irrelevant chunks → low-quality questions | High | Spend Day 4 evaluating retrieval quality with 5–10 test resumes before moving on |
| Evaluation prompts hallucinate scores | High | Use structured outputs (JSON schema enforcement) + a fixed rubric |
| Latency makes the chat feel sluggish | Medium | Stream responses; cache embeddings; pre-generate question pools |
| Vercel/Railway deploy fails late in the timeline | Medium | Deploy a "hello world" version on Day 1, not Day 11 |
| Scope creep (especially voice) | High | This doc is the anchor — re-read at the start of every day |
| Burnout in days 10–14 | Medium | Days 10 and 13 are buffer days; don't add features into them |

## 11. Open questions

(Update this section throughout the build — open questions are normal and showing them is good.)

- Should the evaluation rubric be visible to users mid-interview, or only at the end?
- How do we handle a user who uploads a resume in a language other than English? (v1: English only, document the limitation.)
- What's the right number of questions per session? (Start with 8, measure, adjust.)

## 12. Out-of-scope follow-ups for v1.1+

- Voice mode
- Company-specific question packs
- Live coding sandbox
- Peer review (other users evaluate your answers)
- Mobile app
- Recruiter-facing dashboard

---

*This PRD is a living document. Update it whenever scope changes — and log those changes in the Decision Log.*
