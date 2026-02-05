"""CRUD endpoints for journal entries."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.schemas import JournalEntryCreate, JournalEntryRead, JournalEntryUpdate
from src.database import get_db
from src.models.journal import JournalEntry

router = APIRouter(prefix="/journal", tags=["journal"])


@router.get("/", response_model=list[JournalEntryRead])
def list_entries(
    mood: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    q = db.query(JournalEntry)
    if mood:
        q = q.filter(JournalEntry.mood == mood)
    return q.order_by(JournalEntry.entry_date.desc()).limit(limit).all()


@router.post("/", response_model=JournalEntryRead, status_code=201)
def create_entry(body: JournalEntryCreate, db: Session = Depends(get_db)):
    entry = JournalEntry(**body.model_dump(exclude_unset=True))
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/{entry_id}", response_model=JournalEntryRead)
def get_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.get(JournalEntry, entry_id)
    if not entry:
        raise HTTPException(404, "Journal entry not found")
    return entry


@router.patch("/{entry_id}", response_model=JournalEntryRead)
def update_entry(entry_id: int, body: JournalEntryUpdate, db: Session = Depends(get_db)):
    entry = db.get(JournalEntry, entry_id)
    if not entry:
        raise HTTPException(404, "Journal entry not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=204)
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.get(JournalEntry, entry_id)
    if not entry:
        raise HTTPException(404, "Journal entry not found")
    db.delete(entry)
    db.commit()
