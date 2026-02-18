"""CRUD endpoints for research projects."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.schemas import (
    ProjectDetailRead,
    ProjectNoteCreate,
    ProjectNoteRead,
    ProjectNoteUpdate,
    ResearchProjectCreate,
    ResearchProjectRead,
    ResearchProjectUpdate,
)
from src.database import get_db
from src.models.academic import Deadline, ProjectNote, Publication, ResearchProject
from src.models.journal import JournalEntry

router = APIRouter(prefix="/projects", tags=["research-projects"])


@router.get("/", response_model=list[ResearchProjectRead])
def list_projects(
    status: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(ResearchProject)
    if status:
        q = q.filter(ResearchProject.status == status)
    return q.order_by(ResearchProject.updated_at.desc()).all()


@router.post("/", response_model=ResearchProjectRead, status_code=201)
def create_project(body: ResearchProjectCreate, db: Session = Depends(get_db)):
    project = ResearchProject(**body.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ResearchProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(ResearchProject, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project


@router.patch("/{project_id}", response_model=ResearchProjectRead)
def update_project(
    project_id: int, body: ResearchProjectUpdate, db: Session = Depends(get_db)
):
    project = db.get(ResearchProject, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(ResearchProject, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    db.delete(project)
    db.commit()


# -- Project Detail ----------------------------------------------------------

@router.get("/{project_id}/detail", response_model=ProjectDetailRead)
def get_project_detail(project_id: int, db: Session = Depends(get_db)):
    project = db.get(ResearchProject, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    notes = (
        db.query(ProjectNote)
        .filter(ProjectNote.project_id == project_id)
        .order_by(ProjectNote.created_at.desc())
        .all()
    )
    journal_entries = (
        db.query(JournalEntry)
        .filter(JournalEntry.project_id == project_id)
        .order_by(JournalEntry.entry_date.desc())
        .all()
    )
    publications = (
        db.query(Publication)
        .filter(Publication.project_id == project_id)
        .order_by(Publication.updated_at.desc())
        .all()
    )
    deadlines = (
        db.query(Deadline)
        .filter(Deadline.project_id == project_id)
        .order_by(Deadline.due_date.asc())
        .all()
    )
    return ProjectDetailRead(
        **{c.key: getattr(project, c.key) for c in ResearchProject.__table__.columns},
        project_notes=notes,
        journal_entries=journal_entries,
        publications=publications,
        deadlines=deadlines,
    )


# -- Project Notes -----------------------------------------------------------

@router.get("/{project_id}/notes", response_model=list[ProjectNoteRead])
def list_project_notes(project_id: int, db: Session = Depends(get_db)):
    project = db.get(ResearchProject, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return (
        db.query(ProjectNote)
        .filter(ProjectNote.project_id == project_id)
        .order_by(ProjectNote.created_at.desc())
        .all()
    )


@router.post("/{project_id}/notes", response_model=ProjectNoteRead, status_code=201)
def create_project_note(
    project_id: int, body: ProjectNoteCreate, db: Session = Depends(get_db)
):
    project = db.get(ResearchProject, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    note = ProjectNote(**body.model_dump())
    note.project_id = project_id
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.patch("/notes/{note_id}", response_model=ProjectNoteRead)
def update_project_note(
    note_id: int, body: ProjectNoteUpdate, db: Session = Depends(get_db)
):
    note = db.get(ProjectNote, note_id)
    if not note:
        raise HTTPException(404, "Note not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(note, key, value)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/notes/{note_id}", status_code=204)
def delete_project_note(note_id: int, db: Session = Depends(get_db)):
    note = db.get(ProjectNote, note_id)
    if not note:
        raise HTTPException(404, "Note not found")
    db.delete(note)
    db.commit()
