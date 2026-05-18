### v2 results

**Wins:**
- Anchor leakage eliminated (0/8 vs 1/8 in v1). All anchors verbatim from resume.
- Easy warm-up question now produced (Q1: CI/CD).
- Hard distribution rule held for technical_concept (1/1).

**Partial wins:**
- "Easy" warm-up was CI/CD — better than v1, but not a true conversational opener.

**Still broken:**
- Behavioral count still 2/3. Type distribution skew unchanged (5 technical_project vs target 4).
- New issue: Q8 was *labeled* behavioral but is functionally a technical_project question. 
  The model now satisfies the count by misclassifying rather than by truly producing more 
  behavioral questions.

**Root cause analysis:**
The behavioral undershoot is partly a resume issue, not a prompt issue. The resume has 
strong technical content and a single explicit behavioral line ("cross-functional teams"). 
The hard anchor rule forces behavioral questions to ground in resume phrases, but there's 
limited behavioral content to anchor to. The model resolves this by either (a) producing 
fewer behavioral questions or (b) mislabeling a technical question.

### Open issues for v3

- Relax the anchor requirement for behavioral questions: allow general situational prompts 
  (conflict, learning, deadline pressure) without requiring a verbatim resume substring.
- Add a type-validation pass: after generation, verify each question's content actually 
  matches its declared type. Reject and regenerate if labels lie.


### v3 results

**Bad answer test** ("I don't remember the details..."):
- All four dimensions: 0/0/0/0
- Overall: 0
- Strengths: 3 minimal but genuine ("Acknowledged uncertainty honestly", 
  "Kept response brief rather than padding with filler", "Stated libraries 
  were used")
- Weaknesses: 3 sharp callouts about missing specifics
- Suggested improvement: concrete and references the question's domain 
  (LangGraph, external APIs)

Calibration now works in both directions: strong answers score 4 with 
real critique, bad answers score 0-1 with minimal-but-real strengths 
and sharp weaknesses. The rubric is shippable.

### Open issues for v4 (not planned)

- The "minimal positive" pattern for bad answers could be exploited by 
  candidates (e.g., always starting answers with "I'll be honest..." to 
  guarantee an "intellectual honesty" strength). Not worth fixing for v1.
- Difficulty level still isn't used in scoring — could affect calibration 
  for easy warm-up questions vs hard stretch questions.