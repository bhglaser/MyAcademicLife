"""CRUD endpoints for tasks."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from src.api.schemas import (
    TaskCategoryCreate,
    TaskCategoryRead,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from src.database import get_db
from src.models.tasks import Task, TaskCategory, TaskStatus

router = APIRouter(prefix="/tasks", tags=["tasks"])


# -- Categories --------------------------------------------------------------

@router.get("/categories", response_model=list[TaskCategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return db.query(TaskCategory).order_by(TaskCategory.name).all()


@router.post("/categories", response_model=TaskCategoryRead, status_code=201)
def create_category(body: TaskCategoryCreate, db: Session = Depends(get_db)):
    cat = TaskCategory(**body.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


# -- Tasks -------------------------------------------------------------------

@router.get("/", response_model=list[TaskRead])
def list_tasks(
    status: str | None = None,
    priority: str | None = None,
    category_id: int | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Task).options(
        selectinload(Task.subtasks)
    ).filter(Task.parent_id.is_(None))  # top-level only; subtasks nested inside
    if status:
        q = q.filter(Task.status == status)
    if priority:
        q = q.filter(Task.priority == priority)
    if category_id is not None:
        q = q.filter(Task.category_id == category_id)
    return q.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc()).all()


@router.post("/", response_model=TaskRead, status_code=201)
def create_task(body: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**body.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, body: TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    updates = body.model_dump(exclude_unset=True)
    # Auto-set completed_at when transitioning to done
    if updates.get("status") == TaskStatus.DONE and task.status != TaskStatus.DONE:
        updates["completed_at"] = datetime.now()
    for key, value in updates.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    db.delete(task)
    db.commit()
