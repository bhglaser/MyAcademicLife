"""Models for core academic activities: research, publications, courses, teaching, deadlines."""

from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class DeadlineKind(str, enum.Enum):
    CONFERENCE = "conference"
    JOURNAL = "journal"
    GRANT = "grant"
    COURSEWORK = "coursework"
    ADMINISTRATIVE = "administrative"
    OTHER = "other"


class DeadlineStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    SUBMITTED = "submitted"
    MISSED = "missed"
    CANCELLED = "cancelled"


class PublicationStatus(str, enum.Enum):
    IDEA = "idea"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    REVISION = "revision"
    ACCEPTED = "accepted"
    PUBLISHED = "published"


class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Semester(str, enum.Enum):
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"


# ---------------------------------------------------------------------------
# Research Projects
# ---------------------------------------------------------------------------

class ResearchProject(Base):
    __tablename__ = "research_projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus), default=ProjectStatus.ACTIVE
    )
    start_date: Mapped[date | None] = mapped_column(Date)
    target_end_date: Mapped[date | None] = mapped_column(Date)
    collaborators: Mapped[str | None] = mapped_column(Text)  # comma-separated or JSON
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    publications: Mapped[list[Publication]] = relationship(back_populates="project")
    deadlines: Mapped[list[Deadline]] = relationship(back_populates="project")
    project_notes: Mapped[list[ProjectNote]] = relationship(back_populates="project")
    journal_entries: Mapped[list[JournalEntry]] = relationship(back_populates="project")


# ---------------------------------------------------------------------------
# Publications
# ---------------------------------------------------------------------------

class Publication(Base):
    __tablename__ = "publications"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    authors: Mapped[str | None] = mapped_column(Text)
    venue: Mapped[str | None] = mapped_column(String(300))
    status: Mapped[PublicationStatus] = mapped_column(
        Enum(PublicationStatus), default=PublicationStatus.IDEA
    )
    abstract: Mapped[str | None] = mapped_column(Text)
    doi: Mapped[str | None] = mapped_column(String(200))
    url: Mapped[str | None] = mapped_column(String(500))
    submitted_date: Mapped[date | None] = mapped_column(Date)
    accepted_date: Mapped[date | None] = mapped_column(Date)
    published_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)

    project_id: Mapped[int | None] = mapped_column(ForeignKey("research_projects.id"))
    project: Mapped[ResearchProject | None] = relationship(back_populates="publications")

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


# ---------------------------------------------------------------------------
# Deadlines
# ---------------------------------------------------------------------------

class Deadline(Base):
    __tablename__ = "deadlines"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    kind: Mapped[DeadlineKind] = mapped_column(Enum(DeadlineKind))
    status: Mapped[DeadlineStatus] = mapped_column(
        Enum(DeadlineStatus), default=DeadlineStatus.UPCOMING
    )
    due_date: Mapped[datetime] = mapped_column(DateTime)
    reminder_days_before: Mapped[int] = mapped_column(default=7)
    url: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)

    project_id: Mapped[int | None] = mapped_column(ForeignKey("research_projects.id"))
    project: Mapped[ResearchProject | None] = relationship(back_populates="deadlines")

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


# ---------------------------------------------------------------------------
# Project Notes
# ---------------------------------------------------------------------------

class ProjectNote(Base):
    __tablename__ = "project_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    project_id: Mapped[int] = mapped_column(ForeignKey("research_projects.id"))
    project: Mapped[ResearchProject] = relationship(back_populates="project_notes")

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


# ---------------------------------------------------------------------------
# Courses (courses you are taking or have taken)
# ---------------------------------------------------------------------------

class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(300))
    semester: Mapped[Semester] = mapped_column(Enum(Semester))
    year: Mapped[int] = mapped_column()
    instructor: Mapped[str | None] = mapped_column(String(200))
    grade: Mapped[str | None] = mapped_column(String(10))
    credits: Mapped[int | None] = mapped_column()
    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


# ---------------------------------------------------------------------------
# Teaching Records (courses / sections you are teaching or TAing)
# ---------------------------------------------------------------------------

class TeachingRecord(Base):
    __tablename__ = "teaching_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_code: Mapped[str] = mapped_column(String(30))
    course_name: Mapped[str] = mapped_column(String(300))
    role: Mapped[str] = mapped_column(String(50))  # e.g. "Instructor", "TA", "Guest Lecturer"
    semester: Mapped[Semester] = mapped_column(Enum(Semester))
    year: Mapped[int] = mapped_column()
    enrollment: Mapped[int | None] = mapped_column()
    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
