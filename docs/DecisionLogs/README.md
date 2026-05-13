# Decision Logs

This folder tracks every meaningful engineering decision made during the build of Interview Copilot. Inspired by the [ADR (Architecture Decision Record)](https://adr.github.io/) format used at AWS, Spotify, and many other engineering teams.

## Why this exists

Six months from now, I'll want to remember why I chose Postgres + pgvector instead of Pinecone, or why auth uses JWT instead of sessions. Decision logs capture that reasoning while it's fresh. They also signal engineering maturity to recruiters reading the repo.

## Format

Every entry uses this template:

- **Title:** `DL-NNN-short-slug.md`
- **Sections:** Context → Options considered → Decision → Consequences → Follow-ups
- **Status:** Proposed | Accepted | Superseded by DL-NNN

## Index

| ID | Title | Status |
|----|-------|--------|
| [DL-001](./DL-001-stack-selection.md) | Stack selection | Accepted |
