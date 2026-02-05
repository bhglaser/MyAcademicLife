#!/usr/bin/env python3
"""Generate the static academic website from the database."""

from src.database import SessionLocal
from src.services.website_generator import generate_website

if __name__ == "__main__":
    db = SessionLocal()
    try:
        out = generate_website(db)
        print(f"Website generated in {out}")
    finally:
        db.close()
