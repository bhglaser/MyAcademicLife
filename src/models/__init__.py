"""Database models for the academic life platform."""

from src.models.academic import (
    Course,
    Deadline,
    ProjectNote,
    Publication,
    ResearchProject,
    TeachingRecord,
)
from src.models.chat import ChatMessage
from src.models.cv import CVEntry, CVSection
from src.models.tasks import Task, TaskCategory
from src.models.journal import JournalEntry
from src.models.goals import Goal, Milestone

__all__ = [
    "ChatMessage",
    "Course",
    "CVEntry",
    "CVSection",
    "Deadline",
    "Goal",
    "JournalEntry",
    "Milestone",
    "ProjectNote",
    "Publication",
    "ResearchProject",
    "Task",
    "TaskCategory",
    "TeachingRecord",
]
