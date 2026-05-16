# EcosystemGraph AI

AI-native ecosystem relationship intelligence for mentors, companies, participants, programs, skills, and reusable graph relationships.

This MVP treats relationships as first-class programmable entities:

- Company-to-mentor matching for startup growth guidance
- Company-to-program matching so companies can find programs that grow participant skills
- Program-to-company matching so programs can find relevant companies
- Participant-to-program matching for professional skill growth
- Participant-to-company linkage
- Skill graph creation
- Strict Gemini extraction for explicit professional skills
- Neo4j graph memory for ecosystem linkages

## Stack

- Frontend: Vite, React, TypeScript, TailwindCSS
- Backend: FastAPI, Python 3.12, async SQLAlchemy
- AI: Google Gemini API
- Data: PostgreSQL, Neo4j, Redis
- Infra: Docker Compose

## Quick Start

1. Copy the environment file:

```bash
cp .env.example .env
```

2. Add `GEMINI_API_KEY` in `.env` for live Gemini extraction. Without it, the backend uses a conservative local extractor that only tags exact explicit terms found in the bio.

3. Start the stack:

```bash
docker compose up --build
```

If you previously ran the older mentor-company-only schema locally, recreate the Postgres volume before starting again so the generalized `matches` table is created cleanly.

The local database also loads demo companies, mentors, participants, programs, skills, relationships, and starter matches from `infra/demo_seed.sql` on first initialization. If you already have a Postgres volume, run `docker compose down -v` before `docker compose up --build` to reload the demo data.

4. Open:

- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs
- Neo4j browser: http://localhost:7474

For frontend-only development, run `npm install` once inside `frontend/`, then `npm run dev`. Vite reads the API base URL from `VITE_API_URL`.

Default local auth is disabled with `DISABLE_AUTH=true`. For production-like auth, set `DISABLE_AUTH=false`, change `JWT_SECRET`, `ADMIN_USERNAME`, and `ADMIN_PASSWORD`, then request a token from `/api/auth/token`.

## Core Flow

1. Admin creates a mentor, company, participant, or program.
2. Backend sends the profile bio through Gemini using strict extraction prompts.
3. AI returns a short bio and explicit professional skill tags only.
4. PostgreSQL stores the profile, skills, embeddings, and matches.
5. Neo4j stores graph nodes and relationships.
6. Matching engine recomputes ecosystem recommendations across company-mentor, company-program, program-company, and participant-program paths.

## Matching Formula

The story behind the matching engine is simple: startup companies need mentors who can guide them toward business growth, companies need programs that help their participants build practical skills, programs need the right companies to serve, and participants need programs that fit their current professional profile.

Every match is scored from 0 to 1:

- 45% exact normalized skill overlap
- 40% embedding similarity over short bio plus skills
- 15% relationship/program bonus

Skill overlap compares explicit extracted skills such as `AI`, `Fintech`, or `Product Management`. Embedding similarity compares the enriched short bio plus skills to catch softer alignment. The relationship/program bonus is awarded when a company is already linked to a program, which increases confidence for company-program and program-company recommendations.

The MVP includes deterministic hash embeddings so it can run without a paid vector service. The `EmbeddingService` is isolated so it can be swapped for Gemini embeddings or pgvector later.

## Project Structure

```text
backend/app/
  api/             FastAPI routes and dependencies
  ai/              Gemini prompts and strict JSON handling
  core/            config, JWT, rate limiting
  db/              async database sessions
  graph/           Neo4j relationship memory
  models/          SQLAlchemy models
  repositories/    persistence layer
  schemas/         Pydantic contracts
  services/        profile enrichment, embeddings, matching

frontend/
  src/             Vite application entry and SPA router
  components/      dashboard, entity forms, graph, matches
  lib/             API client and types

infra/
  postgres_schema.sql
  demo_seed.sql
```

## Production Notes

- Keep `temperature=0` for extraction.
- Keep AI outputs post-filtered against source bios.
- Move rate limiting to Redis for multi-instance deployment.
- Replace hash embeddings with Gemini embeddings plus `pgvector` when ready.
- Add role-based authorization before opening multi-tenant admin access.
