"""Tests for the chatbot context builder."""

from datetime import datetime, timedelta

from src.chatbot.context import gather_context
from src.models.academic import Deadline, DeadlineKind, DeadlineStatus, ResearchProject
from src.models.tasks import Task


def test_empty_context(db):
    result = gather_context(db)
    assert "No data recorded yet" in result


def test_context_with_data(db):
    db.add(ResearchProject(title="Project Alpha"))
    db.add(
        Deadline(
            title="Submit paper",
            kind=DeadlineKind.CONFERENCE,
            status=DeadlineStatus.UPCOMING,
            due_date=datetime.now() + timedelta(days=10),
        )
    )
    db.add(Task(title="Review literature"))
    db.commit()

    result = gather_context(db)
    assert "Project Alpha" in result
    assert "Submit paper" in result
    assert "Review literature" in result
