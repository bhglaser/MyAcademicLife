"""Generate CV / résumé documents from the database.

Renders Jinja2 templates in ``templates/cv/`` to produce LaTeX or
Markdown output that you can compile or convert as needed.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from src.models.cv import CVEntry, CVSection

TEMPLATE_DIR = Path(__file__).resolve().parent.parent.parent / "templates" / "cv"


def generate_cv_markdown(db: Session) -> str:
    """Return a Markdown-formatted CV built from the database."""
    sections = db.query(CVSection).order_by(CVSection.display_order).all()
    entries = db.query(CVEntry).order_by(CVEntry.section, CVEntry.display_order).all()

    entries_by_section: dict[str, list[CVEntry]] = {}
    for entry in entries:
        entries_by_section.setdefault(entry.section, []).append(entry)

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)

    try:
        template = env.get_template("cv.md.j2")
    except Exception:
        # Fallback: generate inline if template missing
        return _inline_markdown(sections, entries_by_section)

    return template.render(sections=sections, entries_by_section=entries_by_section)


def generate_cv_latex(db: Session) -> str:
    """Return a LaTeX-formatted CV built from the database."""
    sections = db.query(CVSection).order_by(CVSection.display_order).all()
    entries = db.query(CVEntry).order_by(CVEntry.section, CVEntry.display_order).all()

    entries_by_section: dict[str, list[CVEntry]] = {}
    for entry in entries:
        entries_by_section.setdefault(entry.section, []).append(entry)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=False,
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="<<",
        variable_end_string=">>",
        comment_start_string="<#",
        comment_end_string="#>",
    )

    try:
        template = env.get_template("cv.tex.j2")
    except Exception:
        return "% LaTeX template not found.  Add templates/cv/cv.tex.j2"

    return template.render(sections=sections, entries_by_section=entries_by_section)


def _inline_markdown(
    sections: list[CVSection],
    entries_by_section: dict[str, list[CVEntry]],
) -> str:
    lines: list[str] = ["# Curriculum Vitae\n"]
    for sec in sections:
        items = entries_by_section.get(sec.name, [])
        lines.append(f"## {sec.name}\n")
        for e in items:
            period = ""
            if e.start_date:
                end = e.end_date.strftime("%Y") if e.end_date else "Present"
                period = f" ({e.start_date.strftime('%Y')}–{end})"
            org = f" — {e.organization}" if e.organization else ""
            lines.append(f"**{e.title}**{org}{period}  ")
            if e.description:
                lines.append(f"{e.description}\n")
            lines.append("")
    return "\n".join(lines)
