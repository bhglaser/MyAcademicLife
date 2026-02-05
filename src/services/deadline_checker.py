"""Background service that checks for approaching deadlines and
sends email reminders.

Designed to run as a scheduled job via APScheduler.
"""

from __future__ import annotations

import logging
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage

from sqlalchemy.orm import Session

from src.config import settings
from src.database import SessionLocal
from src.models.academic import Deadline, DeadlineStatus

logger = logging.getLogger(__name__)


def check_deadlines() -> None:
    """Scan for deadlines due within their reminder window and send alerts."""
    db: Session = SessionLocal()
    try:
        upcoming = (
            db.query(Deadline)
            .filter(Deadline.status == DeadlineStatus.UPCOMING)
            .all()
        )
        now = datetime.now()
        for dl in upcoming:
            reminder_threshold = dl.due_date - timedelta(days=dl.reminder_days_before)
            if now >= reminder_threshold:
                days_left = (dl.due_date - now).days
                _send_reminder(dl, days_left)
    finally:
        db.close()


def _send_reminder(deadline: Deadline, days_left: int) -> None:
    """Send an email reminder for a single deadline."""
    if not settings.smtp_host or not settings.notification_email:
        logger.info(
            "Deadline reminder (email not configured): %s — %d day(s) left",
            deadline.title,
            days_left,
        )
        return

    msg = EmailMessage()
    msg["Subject"] = f"[Academic Reminder] {deadline.title} — {days_left} day(s) left"
    msg["From"] = settings.smtp_user
    msg["To"] = settings.notification_email
    msg.set_content(
        f"Deadline: {deadline.title}\n"
        f"Type: {deadline.kind.value}\n"
        f"Due: {deadline.due_date:%Y-%m-%d %H:%M}\n"
        f"Days remaining: {days_left}\n\n"
        f"Notes: {deadline.notes or '—'}\n"
    )

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            smtp.starttls()
            smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)
        logger.info("Sent reminder for deadline: %s", deadline.title)
    except Exception:
        logger.exception("Failed to send reminder for deadline: %s", deadline.title)
