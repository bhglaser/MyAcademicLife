#!/usr/bin/env python3
"""Manually trigger a deadline check (useful for cron or testing)."""

from src.services.deadline_checker import check_deadlines

if __name__ == "__main__":
    check_deadlines()
    print("Deadline check complete.")
