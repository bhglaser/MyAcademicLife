# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ProfStack is a personal academic assistant platform. FastAPI + PostgreSQL backend with a Next.js frontend. Tracks research projects, publications, deadlines, tasks, courses, teaching, goals, journal entries, and CV data. Includes an AI assistant (Claude API, optional) and generators for CVs and academic websites.

## Common Commands

### Backend

```bash
docker compose up -d db                   # Start PostgreSQL
pip install -e ".[dev]"                   # Install with dev dependencies
pip install -e ".[dev,chatbot]"           # Include Anthropic SDK for AI assistant
alembic upgrade head                      # Run database migrations
uvicorn src.app:app --reload              # Dev server on :8000
pytest                                    # Run all tests (uses in-memory SQLite)
pytest tests/api/test_projects.py         # Run a single test file
pytest tests/api/test_projects.py -k test_create  # Run a specific test
ruff check src/                           # Lint
ruff format src/                          # Format
mypy src/                                 # Type check (strict mode)
```

### Frontend

```bash
cd frontend
npm install
npm run dev                               # Dev server on :3000
npm run build                             # Production build
npm run lint                              # ESLint
```

### Full Stack (Docker)

```bash
docker compose up --build                 # Runs both app (:8000) and db
```

## Architecture

### Backend (src/)

Factory pattern: `src/app.py` → `create_app()` creates the FastAPI app, registers CORS (allows localhost:3000), and mounts all routers under `/api`.

**Request flow:** Router → Pydantic schema validation → SQLAlchemy ORM → PostgreSQL

- `models/` — SQLAlchemy 2.0 ORM models split by domain: `academic.py` (projects, publications, deadlines, courses, teaching), `tasks.py`, `goals.py`, `journal.py`, `cv.py`
- `api/schemas.py` — All Pydantic v2 schemas in one file, following Create/Read/Update pattern per resource
- `api/routers/` — One router per domain, all use `Depends(get_db)` for session injection
- `chatbot/assistant.py` — Claude API integration with rule-based fallback when no API key is set
- `chatbot/context.py` — Queries the database to build context string for the AI assistant
- `services/` — CV generation (Markdown/LaTeX via Jinja2), website generation (static HTML), deadline email checker (APScheduler)
- `database.py` — SQLAlchemy engine, session factory, `Base` declarative base, `get_db` dependency

### Frontend (frontend/)

Next.js 14 App Router with client-side rendering (`"use client"` components). Tailwind CSS for styling.

- `lib/api.ts` — Typed API client; all fetch calls to the backend go through here. Hits `http://localhost:8000/api`.
- `app/` — One page per feature (projects, publications, deadlines, tasks, goals, journal, cv, chat). Dashboard at root.
- `components/Sidebar.tsx` — Persistent navigation sidebar in root layout.

### Key Relationships

- Publications and Deadlines can belong to a ResearchProject (FK)
- Tasks can have a TaskCategory (FK) and self-referential subtasks (parent_task_id)
- Goals contain Milestones (one-to-many)

## Testing

Tests use in-memory SQLite via `conftest.py` fixtures. The `client` fixture creates a `TestClient` with DB dependency override. Tables are created/dropped per test (`autouse=True`).

## Code Style

- Python: Ruff (line-length 100, rules: E/F/I/N/W/UP), MyPy strict with Pydantic plugin
- Target: Python 3.11+
- Frontend: TypeScript strict mode, Tailwind CSS

## Environment Variables

See `.env.example`. Key vars: `DATABASE_URL`, `ANTHROPIC_API_KEY` (optional, for chatbot), `SMTP_*`/`NOTIFICATION_EMAIL` (optional, for deadline emails).
