# AI / Prompt Engineering

> Track every prompt, every prompt version, and every evaluation. The differentiator vs. "I made a chatbot."

## Pipelines

### 1. Question generation

**Purpose:** Given a resume + JD + interview type, produce N relevant questions.

**Input shape:**
```json
{
  "resume_chunks": ["...", "..."],
  "jd_chunks": ["...", "..."],
  "interview_type": "behavioral" | "technical" | "system_design",
  "n_questions": 8
}
```

**Output shape:** Structured JSON array of questions (enforced via response_format).

**Prompts:** see [`prompts/question_gen/`](./prompts/) (will be populated Day 5).

### 2. Answer evaluation

**Purpose:** Score a user answer against a fixed rubric.

**Rubric dimensions (v1):**

- **Clarity** (0–5) — Was the answer well-structured and easy to follow?
- **STAR adherence** (0–5) — For behavioral questions, did it follow Situation/Task/Action/Result?
- **Technical depth** (0–5) — For technical questions, did it demonstrate real understanding vs. memorized terms?
- **Relevance** (0–5) — Did the answer actually address the question asked?

**Output shape:** Strict JSON conforming to the rubric schema.

**Prompts:** see [`prompts/evaluation/`](./prompts/) (Day 7).

## Prompt versioning

Every prompt change gets a new file:

```
prompts/
  question_gen/
    v1.txt
    v2.txt   <- changelog at top: what changed, why
```

## Evaluation data

`evals/` will hold:

- A fixed test set of 20–30 (resume, JD, expected question characteristics) triples.
- Scripts to run each prompt version against the test set.
- Results comparing versions on relevance, hallucination rate, and JSON validity.

## Open questions

- Should evaluation include a "confidence" score from the user, or only from the model?
- Calibration: do scores drift across sessions? Need to spot-check 20 evaluations manually each week.
