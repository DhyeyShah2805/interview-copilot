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