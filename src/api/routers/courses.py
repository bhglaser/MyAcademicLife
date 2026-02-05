"""CRUD endpoints for courses and teaching records."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.schemas import (
    CourseCreate,
    CourseRead,
    CourseUpdate,
    TeachingRecordCreate,
    TeachingRecordRead,
)
from src.database import get_db
from src.models.academic import Course, TeachingRecord

router = APIRouter(prefix="/courses", tags=["courses"])


# -- Courses -----------------------------------------------------------------

@router.get("/", response_model=list[CourseRead])
def list_courses(
    semester: str | None = None,
    year: int | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Course)
    if semester:
        q = q.filter(Course.semester == semester)
    if year is not None:
        q = q.filter(Course.year == year)
    return q.order_by(Course.year.desc(), Course.code).all()


@router.post("/", response_model=CourseRead, status_code=201)
def create_course(body: CourseCreate, db: Session = Depends(get_db)):
    course = Course(**body.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/{course_id}", response_model=CourseRead)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    return course


@router.patch("/{course_id}", response_model=CourseRead)
def update_course(course_id: int, body: CourseUpdate, db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(course, key, value)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=204)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    db.delete(course)
    db.commit()


# -- Teaching ----------------------------------------------------------------

@router.get("/teaching/", response_model=list[TeachingRecordRead])
def list_teaching(db: Session = Depends(get_db)):
    return db.query(TeachingRecord).order_by(TeachingRecord.year.desc()).all()


@router.post("/teaching/", response_model=TeachingRecordRead, status_code=201)
def create_teaching(body: TeachingRecordCreate, db: Session = Depends(get_db)):
    rec = TeachingRecord(**body.model_dump())
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec
