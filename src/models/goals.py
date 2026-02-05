"""Goals and milestones — longer-horizon planning."""

from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class GoalTimeframe(str, enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEMESTER = "semester"
    YEARLY = "yearly"
    MULTI_YEAR = "multi_year"


class GoalStatus(str, enum.Enum):
    ACTIVE = "active"
    ACHIEVED = "achieved"
    DEFERRED = "deferred"
    DROPPED = "dropped"


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    timeframe: Mapped[GoalTimeframe] = mapped_column(Enum(GoalTimeframe))
    status: Mapped[GoalStatus] = mapped_column(Enum(GoalStatus), default=GoalStatus.ACTIVE)
    target_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)

    milestones: Mapped[list[Milestone]] = relationship(back_populates="goal")

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class Milestone(Base):
    __tablename__ = "milestones"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    is_complete: Mapped[bool] = mapped_column(default=False)
    target_date: Mapped[date | None] = mapped_column(Date)
    completed_date: Mapped[date | None] = mapped_column(Date)

    goal_id: Mapped[int] = mapped_column(ForeignKey("goals.id"))
    goal: Mapped[Goal] = relationship(back_populates="milestones")

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
