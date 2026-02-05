"""Academic advisor chatbot — gathers context from the database and
uses an LLM (Claude) to provide personalised suggestions on time
management, research focus, deadlines, and well-being.

Falls back to a simple rule-based summary when no API key is configured.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.chatbot.context import gather_context
from src.config import settings


def get_advice(user_message: str, db: Session) -> str:
    """Return an advisor response for *user_message*."""
    context = gather_context(db)

    if settings.anthropic_api_key:
        return _llm_advice(user_message, context)

    # Fallback: rule-based summary
    return _rule_based_advice(user_message, context)


# ---------------------------------------------------------------------------
# LLM path (requires `pip install anthropic`)
# ---------------------------------------------------------------------------

def _llm_advice(user_message: str, context: str) -> str:
    try:
        import anthropic  # type: ignore[import-untyped]
    except ImportError:
        return (
            "The anthropic package is not installed.  "
            "Run `pip install 'my-academic-life[chatbot]'` to enable AI advice."
        )

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    system_prompt = (
        "You are a friendly, knowledgeable academic advisor and personal "
        "productivity coach.  You have access to the user's current academic "
        "context (projects, deadlines, tasks, goals, journal entries, etc.) "
        "shown below.  Use this context to give specific, actionable advice.  "
        "Be encouraging but honest.  Keep responses concise.\n\n"
        "--- ACADEMIC CONTEXT ---\n"
        f"{context}\n"
        "--- END CONTEXT ---"
    )

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# Rule-based fallback
# ---------------------------------------------------------------------------

def _rule_based_advice(user_message: str, context: str) -> str:
    """Provide a simple summary-based response without an LLM."""
    lines: list[str] = ["Here's a snapshot of your academic life:\n"]
    lines.append(context)
    lines.append(
        "\n(Tip: configure ANTHROPIC_API_KEY in your .env file to enable "
        "AI-powered personalised advice.)"
    )
    return "\n".join(lines)
