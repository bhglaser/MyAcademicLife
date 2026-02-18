"""Daily / weekly journal and reflection entries."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    entry_date: Mapped[date] = mapped_column(Date, default=date.today)
    title: Mapped[str | None] = mapped_column(String(300))
    body: Mapped[str] = mapped_column(Text)
    mood: Mapped[str | None] = mapped_column(String(50))  # e.g. "great", "stressed", "focused"
    tags: Mapped[str | None] = mapped_column(String(500))  # comma-separated

    project_id: Mapped[int | None] = mapped_column(ForeignKey("research_projects.id"))
    project: Mapped[ResearchProject | None] = relationship(back_populates="journal_entries")

    @property
    def project_title(self) -> str | None:
        return self.project.title if self.project else None

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
