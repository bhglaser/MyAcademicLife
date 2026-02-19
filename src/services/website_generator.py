"""Generate a simple academic website from the database.

Renders Jinja2 templates in ``templates/website/`` to produce static
HTML pages listing publications, teaching, and a bio pulled from CV data.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from src.models.academic import Publication, PublicationStatus, TeachingRecord
from src.models.cv import CVEntry

TEMPLATE_DIR = Path(__file__).resolve().parent.parent.parent / "templates" / "website"
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "generated_website"


def generate_website(db: Session) -> Path:
    """Generate static HTML pages and return the output directory."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    publications = (
        db.query(Publication)
        .filter(Publication.status.in_([PublicationStatus.ACCEPTED, PublicationStatus.PUBLISHED]))
        .order_by(Publication.published_date.desc().nullslast())
        .all()
    )
    teaching = db.query(TeachingRecord).order_by(TeachingRecord.year.desc()).all()
    bio_entries = db.query(CVEntry).filter(CVEntry.section == "Education").all()

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=True)

    try:
        template = env.get_template("index.html.j2")
    except Exception:
        # Write a minimal page if no template exists
        html = _minimal_html(publications, teaching, bio_entries)
        (OUTPUT_DIR / "index.html").write_text(html)
        return OUTPUT_DIR

    html = template.render(
        publications=publications,
        teaching=teaching,
        bio_entries=bio_entries,
    )
    (OUTPUT_DIR / "index.html").write_text(html)
    return OUTPUT_DIR


def _minimal_html(
    publications: list,
    teaching: list,
    bio_entries: list,
) -> str:
    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        "<title>Homepage</title>",
        "<style>body{font-family:sans-serif;max-width:48rem;margin:2rem auto;padding:0 1rem}</style>",
        "</head><body>",
        "<h1>Homepage</h1>",
    ]

    if bio_entries:
        parts.append("<h2>Education</h2><ul>")
        for e in bio_entries:
            parts.append(f"<li><strong>{e.title}</strong> — {e.organization or ''}</li>")
        parts.append("</ul>")

    if publications:
        parts.append("<h2>Publications</h2><ul>")
        for p in publications:
            parts.append(f"<li>{p.authors}. <em>{p.title}</em>. {p.venue or ''}</li>")
        parts.append("</ul>")

    if teaching:
        parts.append("<h2>Teaching</h2><ul>")
        for t in teaching:
            parts.append(
                f"<li>{t.course_code} {t.course_name} ({t.role}, {t.semester.value} {t.year})</li>"
            )
        parts.append("</ul>")

    parts.append("</body></html>")
    return "\n".join(parts)
