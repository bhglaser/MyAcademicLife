"""Build a text summary of the user's academic context for the advisor."""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.models.academic import Deadline, DeadlineStatus, ResearchProject, ProjectStatus
from src.models.goals import Goal, GoalStatus
from src.models.journal import JournalEntry
from src.models.tasks import Task, TaskStatus


def gather_context(db: Session) -> str:
    """Return a plain-text summary of the user's current academic state."""
    sections: list[str] = []

    # Upcoming deadlines (next 30 days)
    cutoff = datetime.now() + timedelta(days=30)
    deadlines = (
        db.query(Deadline)
        .filter(Deadline.status == DeadlineStatus.UPCOMING, Deadline.due_date <= cutoff)
        .order_by(Deadline.due_date)
        .all()
    )
    if deadlines:
        lines = ["UPCOMING DEADLINES (next 30 days):"]
        for dl in deadlines:
            days_left = (dl.due_date - datetime.now()).days
            lines.append(f"  - {dl.title} ({dl.kind.value}) — due in {days_left} day(s)")
        sections.append("\n".join(lines))

    # Active research projects
    projects = (
        db.query(ResearchProject)
        .filter(ResearchProject.status == ProjectStatus.ACTIVE)
        .all()
    )
    if projects:
        lines = ["ACTIVE RESEARCH PROJECTS:"]
        for p in projects:
            lines.append(f"  - {p.title}")
        sections.append("\n".join(lines))

    # Open tasks
    open_tasks = (
        db.query(Task)
        .filter(Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS]))
        .order_by(Task.due_date.asc().nullslast())
        .limit(15)
        .all()
    )
    if open_tasks:
        lines = ["OPEN TASKS (top 15):"]
        for t in open_tasks:
            due = f" (due {t.due_date})" if t.due_date else ""
            lines.append(f"  - [{t.priority.value}] {t.title}{due}")
        sections.append("\n".join(lines))

    # Active goals
    goals = db.query(Goal).filter(Goal.status == GoalStatus.ACTIVE).all()
    if goals:
        lines = ["ACTIVE GOALS:"]
        for g in goals:
            lines.append(f"  - [{g.timeframe.value}] {g.title}")
        sections.append("\n".join(lines))

    # Recent journal mood
    recent_entries = (
        db.query(JournalEntry)
        .order_by(JournalEntry.entry_date.desc())
        .limit(5)
        .all()
    )
    if recent_entries:
        lines = ["RECENT JOURNAL MOODS:"]
        for j in recent_entries:
            mood = j.mood or "—"
            lines.append(f"  - {j.entry_date}: {mood}")
        sections.append("\n".join(lines))

    if not sections:
        return "(No data recorded yet — start by adding projects, tasks, or deadlines!)"

    return "\n\n".join(sections)
