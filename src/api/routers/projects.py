"""CRUD endpoints for research projects."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.schemas import ResearchProjectCreate, ResearchProjectRead, ResearchProjectUpdate
from src.database import get_db
from src.models.academic import ResearchProject

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
