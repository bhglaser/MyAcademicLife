"""CRUD endpoints for CV sections and entries."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.schemas import (
    CVEntryCreate,
    CVEntryRead,
    CVEntryUpdate,
    CVSectionCreate,
    CVSectionRead,
)
from src.database import get_db
from src.models.cv import CVEntry, CVSection

router = APIRouter(prefix="/cv", tags=["cv"])


# -- Sections ----------------------------------------------------------------

@router.get("/sections", response_model=list[CVSectionRead])
def list_sections(db: Session = Depends(get_db)):
    return db.query(CVSection).order_by(CVSection.display_order).all()


@router.post("/sections", response_model=CVSectionRead, status_code=201)
def create_section(body: CVSectionCreate, db: Session = Depends(get_db)):
    sec = CVSection(**body.model_dump())
    db.add(sec)
    db.commit()
    db.refresh(sec)
    return sec


# -- Entries -----------------------------------------------------------------

@router.get("/entries", response_model=list[CVEntryRead])
def list_entries(section: str | None = None, db: Session = Depends(get_db)):
    q = db.query(CVEntry)
    if section:
        q = q.filter(CVEntry.section == section)
    return q.order_by(CVEntry.section, CVEntry.display_order).all()


@router.post("/entries", response_model=CVEntryRead, status_code=201)
def create_entry(body: CVEntryCreate, db: Session = Depends(get_db)):
    entry = CVEntry(**body.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/entries/{entry_id}", response_model=CVEntryRead)
def get_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.get(CVEntry, entry_id)
    if not entry:
        raise HTTPException(404, "CV entry not found")
    return entry


@router.patch("/entries/{entry_id}", response_model=CVEntryRead)
def update_entry(entry_id: int, body: CVEntryUpdate, db: Session = Depends(get_db)):
    entry = db.get(CVEntry, entry_id)
    if not entry:
        raise HTTPException(404, "CV entry not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/entries/{entry_id}", status_code=204)
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.get(CVEntry, entry_id)
    if not entry:
        raise HTTPException(404, "CV entry not found")
    db.delete(entry)
    db.commit()
