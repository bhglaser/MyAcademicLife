"""Pydantic schemas for request / response validation."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from src.models.academic import (
    DeadlineKind,
    DeadlineStatus,
    ProjectStatus,
    PublicationStatus,
    Semester,
)
from src.models.goals import GoalStatus, GoalTimeframe
from src.models.tasks import TaskPriority, TaskStatus


# ---------------------------------------------------------------------------
# Mixins
# ---------------------------------------------------------------------------

class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Research Projects
# ---------------------------------------------------------------------------

class ResearchProjectCreate(BaseModel):
    title: str
    description: str | None = None
    status: ProjectStatus = ProjectStatus.ACTIVE
    start_date: date | None = None
    target_end_date: date | None = None
    collaborators: str | None = None
    notes: str | None = None


class ResearchProjectRead(ResearchProjectCreate, TimestampMixin):
    id: int


class ResearchProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None
    start_date: date | None = None
    target_end_date: date | None = None
    collaborators: str | None = None
    notes: str | None = None


# ---------------------------------------------------------------------------
# Publications
# ---------------------------------------------------------------------------

class PublicationCreate(BaseModel):
    title: str
    authors: str | None = None
    venue: str | None = None
    status: PublicationStatus = PublicationStatus.IDEA
    abstract: str | None = None
    doi: str | None = None
    url: str | None = None
    submitted_date: date | None = None
    accepted_date: date | None = None
    published_date: date | None = None
    notes: str | None = None
    project_id: int | None = None


class PublicationRead(PublicationCreate, TimestampMixin):
    id: int


class PublicationUpdate(BaseModel):
    title: str | None = None
    authors: str | None = None
    venue: str | None = None
    status: PublicationStatus | None = None
    abstract: str | None = None
    doi: str | None = None
    url: str | None = None
    submitted_date: date | None = None
    accepted_date: date | None = None
    published_date: date | None = None
    notes: str | None = None
    project_id: int | None = None


# ---------------------------------------------------------------------------
# Deadlines
# ---------------------------------------------------------------------------

class DeadlineCreate(BaseModel):
    title: str
    description: str | None = None
    kind: DeadlineKind
    status: DeadlineStatus = DeadlineStatus.UPCOMING
    due_date: datetime
    reminder_days_before: int = 7
    url: str | None = None
    notes: str | None = None
    project_id: int | None = None


class DeadlineRead(DeadlineCreate, TimestampMixin):
    id: int


class DeadlineUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    kind: DeadlineKind | None = None
    status: DeadlineStatus | None = None
    due_date: datetime | None = None
    reminder_days_before: int | None = None
    url: str | None = None
    notes: str | None = None
    project_id: int | None = None


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    due_date: date | None = None
    estimated_hours: float | None = None
    is_recurring: bool = False
    recurrence_rule: str | None = None
    category_id: int | None = None
    parent_id: int | None = None


class TaskRead(TaskCreate, TimestampMixin):
    id: int
    actual_hours: float | None = None
    completed_at: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    due_date: date | None = None
    estimated_hours: float | None = None
    actual_hours: float | None = None
    is_recurring: bool | None = None
    recurrence_rule: str | None = None
    category_id: int | None = None
    parent_id: int | None = None


class TaskCategoryCreate(BaseModel):
    name: str
    color: str | None = None
    description: str | None = None


class TaskCategoryRead(TaskCategoryCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Courses
# ---------------------------------------------------------------------------

class CourseCreate(BaseModel):
    code: str
    name: str
    semester: Semester
    year: int
    instructor: str | None = None
    grade: str | None = None
    credits: int | None = None
    notes: str | None = None


class CourseRead(CourseCreate, TimestampMixin):
    id: int


class CourseUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    semester: Semester | None = None
    year: int | None = None
    instructor: str | None = None
    grade: str | None = None
    credits: int | None = None
    notes: str | None = None


# ---------------------------------------------------------------------------
# Teaching
# ---------------------------------------------------------------------------

class TeachingRecordCreate(BaseModel):
    course_code: str
    course_name: str
    role: str
    semester: Semester
    year: int
    enrollment: int | None = None
    notes: str | None = None


class TeachingRecordRead(TeachingRecordCreate, TimestampMixin):
    id: int


# ---------------------------------------------------------------------------
# CV
# ---------------------------------------------------------------------------

class CVSectionCreate(BaseModel):
    name: str
    display_order: int = 0


class CVSectionRead(CVSectionCreate, TimestampMixin):
    id: int


class CVEntryCreate(BaseModel):
    section: str
    title: str
    organization: str | None = None
    location: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None
    display_order: int = 0


class CVEntryRead(CVEntryCreate, TimestampMixin):
    id: int


class CVEntryUpdate(BaseModel):
    section: str | None = None
    title: str | None = None
    organization: str | None = None
    location: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None
    display_order: int | None = None


# ---------------------------------------------------------------------------
# Journal
# ---------------------------------------------------------------------------

class JournalEntryCreate(BaseModel):
    entry_date: date | None = None
    title: str | None = None
    body: str
    mood: str | None = None
    tags: str | None = None


class JournalEntryRead(JournalEntryCreate, TimestampMixin):
    id: int


class JournalEntryUpdate(BaseModel):
    title: str | None = None
    body: str | None = None
    mood: str | None = None
    tags: str | None = None


# ---------------------------------------------------------------------------
# Goals
# ---------------------------------------------------------------------------

class GoalCreate(BaseModel):
    title: str
    description: str | None = None
    timeframe: GoalTimeframe
    status: GoalStatus = GoalStatus.ACTIVE
    target_date: date | None = None
    notes: str | None = None


class GoalRead(GoalCreate, TimestampMixin):
    id: int


class GoalUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    timeframe: GoalTimeframe | None = None
    status: GoalStatus | None = None
    target_date: date | None = None
    notes: str | None = None


class MilestoneCreate(BaseModel):
    title: str
    description: str | None = None
    target_date: date | None = None
    goal_id: int


class MilestoneRead(MilestoneCreate, TimestampMixin):
    id: int
    is_complete: bool
    completed_date: date | None = None


class MilestoneUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_complete: bool | None = None
    target_date: date | None = None
    completed_date: date | None = None


# ---------------------------------------------------------------------------
# Chatbot
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
