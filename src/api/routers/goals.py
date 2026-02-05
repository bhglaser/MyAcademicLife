"""CRUD endpoints for goals and milestones."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.schemas import (
    GoalCreate,
    GoalRead,
    GoalUpdate,
    MilestoneCreate,
    MilestoneRead,
    MilestoneUpdate,
)
from src.database import get_db
from src.models.goals import Goal, Milestone

router = APIRouter(prefix="/goals", tags=["goals"])


# -- Goals -------------------------------------------------------------------

@router.get("/", response_model=list[GoalRead])
def list_goals(
    status: str | None = None,
    timeframe: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Goal)
    if status:
        q = q.filter(Goal.status == status)
    if timeframe:
        q = q.filter(Goal.timeframe == timeframe)
    return q.order_by(Goal.target_date.asc().nullslast()).all()


@router.post("/", response_model=GoalRead, status_code=201)
def create_goal(body: GoalCreate, db: Session = Depends(get_db)):
    goal = Goal(**body.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.get("/{goal_id}", response_model=GoalRead)
def get_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(404, "Goal not found")
    return goal


@router.patch("/{goal_id}", response_model=GoalRead)
def update_goal(goal_id: int, body: GoalUpdate, db: Session = Depends(get_db)):
    goal = db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(404, "Goal not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(goal, key, value)
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=204)
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(404, "Goal not found")
    db.delete(goal)
    db.commit()


# -- Milestones --------------------------------------------------------------

@router.get("/{goal_id}/milestones", response_model=list[MilestoneRead])
def list_milestones(goal_id: int, db: Session = Depends(get_db)):
    goal = db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(404, "Goal not found")
    return (
        db.query(Milestone)
        .filter(Milestone.goal_id == goal_id)
        .order_by(Milestone.target_date.asc().nullslast())
        .all()
    )


@router.post("/{goal_id}/milestones", response_model=MilestoneRead, status_code=201)
def create_milestone(goal_id: int, body: MilestoneCreate, db: Session = Depends(get_db)):
    goal = db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(404, "Goal not found")
    ms = Milestone(**body.model_dump())
    ms.goal_id = goal_id
    db.add(ms)
    db.commit()
    db.refresh(ms)
    return ms


@router.patch("/milestones/{ms_id}", response_model=MilestoneRead)
def update_milestone(ms_id: int, body: MilestoneUpdate, db: Session = Depends(get_db)):
    ms = db.get(Milestone, ms_id)
    if not ms:
        raise HTTPException(404, "Milestone not found")
    updates = body.model_dump(exclude_unset=True)
    if updates.get("is_complete") and not ms.is_complete:
        updates.setdefault("completed_date", date.today())
    for key, value in updates.items():
        setattr(ms, key, value)
    db.commit()
    db.refresh(ms)
    return ms
