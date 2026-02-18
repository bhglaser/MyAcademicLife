"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import chat, courses, cv, deadlines, goals, journal, projects, publications, tasks


def create_app() -> FastAPI:
    app = FastAPI(
        title="ProfStack",
        description=(
            "A personal academic assistant — track research, publications, deadlines, "
            "teaching, coursework, goals, and more.  Includes an AI-powered assistant."
        ),
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(projects.router, prefix="/api")
    app.include_router(publications.router, prefix="/api")
    app.include_router(deadlines.router, prefix="/api")
    app.include_router(tasks.router, prefix="/api")
    app.include_router(courses.router, prefix="/api")
    app.include_router(cv.router, prefix="/api")
    app.include_router(journal.router, prefix="/api")
    app.include_router(goals.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
