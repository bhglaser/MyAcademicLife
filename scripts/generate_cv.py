#!/usr/bin/env python3
"""Generate a CV in Markdown from the database and print to stdout."""

from src.database import SessionLocal
from src.services.cv_generator import generate_cv_markdown

if __name__ == "__main__":
    db = SessionLocal()
    try:
        print(generate_cv_markdown(db))
    finally:
        db.close()
