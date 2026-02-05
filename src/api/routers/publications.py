"""CRUD endpoints for publications."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.schemas import PublicationCreate, PublicationRead, PublicationUpdate
from src.database import get_db
from src.models.academic import Publication

router = APIRouter(prefix="/publications", tags=["publications"])


@router.get("/", response_model=list[PublicationRead])
def list_publications(
    status: str | None = None,
    project_id: int | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Publication)
    if status:
        q = q.filter(Publication.status == status)
    if project_id is not None:
        q = q.filter(Publication.project_id == project_id)
    return q.order_by(Publication.updated_at.desc()).all()


@router.post("/", response_model=PublicationRead, status_code=201)
def create_publication(body: PublicationCreate, db: Session = Depends(get_db)):
    pub = Publication(**body.model_dump())
    db.add(pub)
    db.commit()
    db.refresh(pub)
    return pub


@router.get("/{pub_id}", response_model=PublicationRead)
def get_publication(pub_id: int, db: Session = Depends(get_db)):
    pub = db.get(Publication, pub_id)
    if not pub:
        raise HTTPException(404, "Publication not found")
    return pub


@router.patch("/{pub_id}", response_model=PublicationRead)
def update_publication(pub_id: int, body: PublicationUpdate, db: Session = Depends(get_db)):
    pub = db.get(Publication, pub_id)
    if not pub:
        raise HTTPException(404, "Publication not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(pub, key, value)
    db.commit()
    db.refresh(pub)
    return pub


@router.delete("/{pub_id}", status_code=204)
def delete_publication(pub_id: int, db: Session = Depends(get_db)):
    pub = db.get(Publication, pub_id)
    if not pub:
        raise HTTPException(404, "Publication not found")
    db.delete(pub)
    db.commit()
