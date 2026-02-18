# ProfStack

A personal academic assistant platform built with **FastAPI** and **PostgreSQL**. Track research projects, publications, deadlines, coursework, teaching, goals, and daily reflections — all in one place. Includes an AI-powered assistant and tools to generate your CV and academic website from the same data.

## Features

| Area | What it does |
|---|---|
| **Research Projects** | Track active projects, collaborators, and status |
| **Publications** | Manage papers from idea through submission to publication |
| **Deadlines** | Conference, journal, grant, and coursework deadlines with email reminders |
| **Tasks** | Priority-based to-do list with categories, subtasks, and recurrence |
| **Courses & Teaching** | Record courses taken and teaching/TA roles |
| **Goals & Milestones** | Set weekly-to-multi-year goals and track milestones |
| **Journal** | Daily reflections with mood tracking |
| **CV Generator** | Auto-generate Markdown or LaTeX CV from your data |
| **Website Generator** | Build a static academic homepage from publications and teaching |
| **AI Assistant** | Get personalised suggestions on time management, research focus, and well-being |

## Quick Start

### 1. Start the database

```bash
docker compose up -d db
```

### 2. Install dependencies

```bash
pip install -e ".[dev]"
```

### 3. Run migrations

```bash
alembic upgrade head
```

### 4. Start the API server

```bash
uvicorn src.app:app --reload
```

The API is now running at `http://localhost:8000`. Interactive docs are at `http://localhost:8000/docs`.

### Using Docker Compose (full stack)

```bash
docker compose up --build
```

## Configuration

Copy `.env.example` to `.env` and edit:

```bash
cp .env.example .env
```

Key settings:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `ANTHROPIC_API_KEY` | Enables the AI assistant (optional) |
| `SMTP_*` / `NOTIFICATION_EMAIL` | Email deadline reminders (optional) |

## API Overview

All endpoints live under `/api`. Examples:

```
GET    /api/projects/          List research projects
POST   /api/projects/          Create a project
GET    /api/deadlines/?upcoming_only=true
POST   /api/tasks/             Create a task
PATCH  /api/tasks/{id}         Update (e.g. mark done)
POST   /api/chat/              Ask the assistant
GET    /api/cv/entries          List CV entries
GET    /api/goals/             List goals
POST   /api/journal/           Add a journal entry
```

Full interactive docs: `http://localhost:8000/docs`

## Generating Your CV

```bash
python scripts/generate_cv.py > my_cv.md
```

## Generating Your Academic Website

```bash
python scripts/generate_website.py
# Output in generated_website/index.html
```

## Running Tests

```bash
pytest
```

## Project Structure

```
src/
  app.py                  # FastAPI application
  config.py               # Settings from environment
  database.py             # SQLAlchemy engine/session
  models/                 # ORM models (academic, tasks, cv, journal, goals)
  api/
    schemas.py            # Pydantic request/response schemas
    routers/              # REST endpoint routers
  chatbot/
    assistant.py          # AI assistant (Claude) + rule-based fallback
    context.py            # Gathers DB context for the chatbot
  services/
    deadline_checker.py   # Background deadline reminder emails
    cv_generator.py       # Markdown/LaTeX CV from DB
    website_generator.py  # Static HTML academic homepage
migrations/               # Alembic database migrations
templates/                # Jinja2 templates for CV and website
scripts/                  # CLI utilities
tests/                    # pytest test suite
```

## Tech Stack

- **Python 3.11+**
- **FastAPI** — async web framework
- **SQLAlchemy 2.0** — ORM with mapped columns
- **Alembic** — database migrations
- **PostgreSQL** — production database (SQLite for tests)
- **Pydantic v2** — request/response validation
- **Jinja2** — CV and website templating
- **APScheduler** — background deadline checks
- **Anthropic Claude** — AI assistant (optional)

## License

Private — personal use.
