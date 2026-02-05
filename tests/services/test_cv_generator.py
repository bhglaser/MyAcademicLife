"""Tests for the CV generator."""

from src.models.cv import CVEntry, CVSection
from src.services.cv_generator import generate_cv_markdown


def test_generate_empty_cv(db):
    result = generate_cv_markdown(db)
    assert "Curriculum Vitae" in result


def test_generate_cv_with_entries(db):
    db.add(CVSection(name="Education", display_order=0))
    db.add(
        CVEntry(
            section="Education",
            title="PhD Computer Science",
            organization="MIT",
            display_order=0,
        )
    )
    db.commit()

    result = generate_cv_markdown(db)
    assert "Education" in result
    assert "PhD Computer Science" in result
    assert "MIT" in result
