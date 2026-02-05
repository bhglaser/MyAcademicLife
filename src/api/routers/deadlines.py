"""CRUD endpoints for deadlines."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.schemas import DeadlineCreate, DeadlineRead, DeadlineUpdate
from src.database import get_db
from src.models.academic import Deadline, DeadlineStatus

router = APIRouter(prefix="/deadlines", tags=["deadlines"])


@router.get("/", response_model=list[DeadlineRead])
def list_deadlines(
    status: str | None = None,
    kind: str | None = None,
    upcoming_only: bool = False,
    db: Session = Depends(get_db),
):
    q = db.query(Deadline)
    if status:
        q = q.filter(Deadline.status == status)
    if kind:
        q = q.filter(Deadline.kind == kind)
    if upcoming_only:
        q = q.filter(
            Deadline.status == DeadlineStatus.UPCOMING,
            Deadline.due_date >= datetime.now(),
        )
    return q.order_by(Deadline.due_date.asc()).all()


@router.post("/", response_model=DeadlineRead, status_code=201)
def create_deadline(body: DeadlineCreate, db: Session = Depends(get_db)):
    dl = Deadline(**body.model_dump())
    db.add(dl)
    db.commit()
    db.refresh(dl)
    return dl


@router.get("/{deadline_id}", response_model=DeadlineRead)
def get_deadline(deadline_id: int, db: Session = Depends(get_db)):
    dl = db.get(Deadline, deadline_id)
    if not dl:
        raise HTTPException(404, "Deadline not found")
    return dl


@router.patch("/{deadline_id}", response_model=DeadlineRead)
def update_deadline(deadline_id: int, body: DeadlineUpdate, db: Session = Depends(get_db)):
    dl = db.get(Deadline, deadline_id)
    if not dl:
        raise HTTPException(404, "Deadline not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(dl, key, value)
    db.commit()
    db.refresh(dl)
    return dl


@router.delete("/{deadline_id}", status_code=204)
def delete_deadline(deadline_id: int, db: Session = Depends(get_db)):
    dl = db.get(Deadline, deadline_id)
    if not dl:
        raise HTTPException(404, "Deadline not found")
    db.delete(dl)
    db.commit()
