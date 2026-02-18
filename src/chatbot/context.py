"""Build a text summary of the user's academic context for the assistant."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from src.models.academic import (
    Deadline,
    DeadlineStatus,
    ProjectNote,
    ProjectStatus,
    ResearchProject,
)
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

    # Active research projects with recent notes and tagged journal entries
    active_projects = (
        db.query(ResearchProject)
        .filter(ResearchProject.status == ProjectStatus.ACTIVE)
        .all()
    )
    if active_projects:
        lines = ["ACTIVE RESEARCH PROJECTS:"]
        for p in active_projects:
            lines.append(f"\n  PROJECT: {p.title}")
            if p.description:
                lines.append(f"    Description: {p.description[:200]}")
            if p.target_end_date:
                days_to_end = (p.target_end_date - date.today()).days
                lines.append(f"    Target end: {p.target_end_date} ({days_to_end} days away)")

            # Recent project notes (last 3)
            recent_notes = (
                db.query(ProjectNote)
                .filter(ProjectNote.project_id == p.id)
                .order_by(ProjectNote.created_at.desc())
                .limit(3)
                .all()
            )
            if recent_notes:
                lines.append("    Recent notes:")
                for note in recent_notes:
                    truncated = note.content[:150].replace("\n", " ")
                    lines.append(
                        f"      - [{note.created_at.strftime('%m/%d')}] {truncated}"
                    )

            # Tagged journal entries (last 3)
            tagged_journals = (
                db.query(JournalEntry)
                .filter(JournalEntry.project_id == p.id)
                .order_by(JournalEntry.entry_date.desc())
                .limit(3)
                .all()
            )
            if tagged_journals:
                lines.append("    Recent journal entries about this project:")
                for j in tagged_journals:
                    mood_str = f" (mood: {j.mood})" if j.mood else ""
                    body_preview = j.body[:100].replace("\n", " ")
                    lines.append(f"      - [{j.entry_date}]{mood_str} {body_preview}")

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

    # Recent journal entries (with body preview and project tags)
    recent_entries = (
        db.query(JournalEntry)
        .order_by(JournalEntry.entry_date.desc())
        .limit(5)
        .all()
    )
    if recent_entries:
        lines = ["RECENT JOURNAL ENTRIES:"]
        for j in recent_entries:
            mood = f" | mood: {j.mood}" if j.mood else ""
            project_tag = ""
            if j.project_id and j.project:
                project_tag = f" | project: {j.project.title}"
            body_preview = j.body[:150].replace("\n", " ")
            lines.append(f"  - [{j.entry_date}{mood}{project_tag}] {body_preview}")
        sections.append("\n".join(lines))

    # Overwhelm signals
    total_open = (
        db.query(Task)
        .filter(Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS]))
        .count()
    )
    overwhelm_signals: list[str] = []
    if total_open >= 10:
        overwhelm_signals.append(f"{total_open} open tasks")
    if deadlines:
        urgent = [dl for dl in deadlines if (dl.due_date - datetime.now()).days <= 3]
        if urgent:
            overwhelm_signals.append(f"{len(urgent)} deadline(s) within 3 days")
    if recent_entries:
        stressed = [j for j in recent_entries if j.mood in ("stressed", "anxious", "tired")]
        if stressed:
            overwhelm_signals.append(
                f"recent mood: {', '.join(j.mood for j in stressed if j.mood)}"
            )
    if overwhelm_signals:
        sections.append(
            "OVERWHELM SIGNALS: "
            + "; ".join(overwhelm_signals)
            + "\n(If the user seems overwhelmed, suggest the top 3 priorities for today "
            "and what can safely be deferred.)"
        )

    if not sections:
        return "(No data recorded yet — start by adding projects, tasks, or deadlines!)"

    return "\n\n".join(sections)
