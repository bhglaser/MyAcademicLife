"""Academic assistant chatbot — gathers context from the database and
uses an LLM (Claude) to provide personalised suggestions on time
management, research focus, deadlines, and well-being.

Supports tool use (e.g. creating tasks) via the Anthropic tool-use API.
Falls back to a simple rule-based summary when no API key is configured.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from src.chatbot.context import gather_context
from src.config import settings


# ---------------------------------------------------------------------------
# Tool definitions for the Anthropic API
# ---------------------------------------------------------------------------

TOOLS: list[dict[str, Any]] = [
    {
        "name": "create_task",
        "description": (
            "Create a new task in the user's task list. Use this when the user "
            "asks you to add, create, or schedule a task, to-do item, or action item. "
            "When the conversation is about a specific project, always set project_id "
            "to associate the task with that project. When creating subtasks, set "
            "parent_id to the ID of the parent task."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Short title for the task (max 500 chars)",
                },
                "description": {
                    "type": "string",
                    "description": "Optional longer description of the task",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "urgent"],
                    "description": "Task priority. Default: medium",
                },
                "due_date": {
                    "type": "string",
                    "description": "Optional due date in YYYY-MM-DD format",
                },
                "project_id": {
                    "type": "integer",
                    "description": (
                        "ID of the research project to associate this task with. "
                        "Look up the project ID from the academic context."
                    ),
                },
                "parent_id": {
                    "type": "integer",
                    "description": (
                        "ID of the parent task, when creating a subtask. "
                        "Use the task ID returned from a previous create_task call."
                    ),
                },
            },
            "required": ["title"],
        },
    },
]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def get_advice(
    messages: list[dict[str, str]], db: Session
) -> tuple[str, list[dict[str, Any]] | None]:
    """Return an assistant response for the conversation so far.

    Args:
        messages: List of {"role": "user"|"assistant", "content": "..."}
                  representing the full conversation history.
        db: SQLAlchemy session for context gathering and tool execution.

    Returns:
        (reply_text, tool_actions) — tool_actions is a list of dicts
        describing any tools that were executed, or None.
    """
    context = gather_context(db)

    if settings.anthropic_api_key:
        return _llm_advice(messages, context, db)

    # Fallback: rule-based summary (uses only the last user message)
    last_user_msg = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            last_user_msg = msg["content"]
            break
    return _rule_based_advice(last_user_msg, context), None


# ---------------------------------------------------------------------------
# LLM path (requires `pip install anthropic`)
# ---------------------------------------------------------------------------

def _llm_advice(
    messages: list[dict[str, str]],
    context: str,
    db: Session,
) -> tuple[str, list[dict[str, Any]] | None]:
    try:
        import anthropic  # type: ignore[import-untyped]
    except ImportError:
        return (
            "The anthropic package is not installed.  "
            "Run `pip install 'faculty-run[chatbot]'` to enable AI advice.",
            None,
        )

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # Use cache_control on the system prompt so it gets cached across turns.
    # The academic context changes per request, but the instructions are stable.
    system = [
        {
            "type": "text",
            "text": (
                "You are a friendly, knowledgeable academic assistant and personal "
                "productivity coach.  You have access to the user's current academic "
                "context — projects with their notes and journal reflections, deadlines, "
                "tasks, goals, and recent journal entries — shown below.  Use this "
                "context to give specific, actionable advice.  When the user seems "
                "overwhelmed, help them prioritize by suggesting the top 3 things to "
                "focus on today and what can safely be deferred.  Be encouraging but "
                "honest.  Keep responses concise.\n\n"
                "You can create tasks for the user using the create_task tool "
                "when they ask you to add something to their task list.  Always "
                "associate tasks with the relevant project by setting project_id.  "
                "When creating subtasks, set parent_id to the parent task's ID.\n\n"
                f"Today's date is {date.today().isoformat()}.\n\n"
                "--- ACADEMIC CONTEXT ---\n"
                f"{context}\n"
                "--- END CONTEXT ---"
            ),
            "cache_control": {"type": "ephemeral"},
        }
    ]

    api_messages = _prepare_messages(messages)
    tool_actions: list[dict[str, Any]] = []

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1536,
        system=system,
        messages=api_messages,
        tools=TOOLS,
    )

    # Tool-use loop: keep calling until we get a final text response
    while response.stop_reason == "tool_use":
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
        tool_results = []

        for tool_block in tool_use_blocks:
            result = _execute_tool(tool_block.name, tool_block.input, db)
            tool_actions.append({
                "tool": tool_block.name,
                "input": tool_block.input,
                "result": result,
            })
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_block.id,
                "content": str(result),
            })

        api_messages.append({"role": "assistant", "content": response.content})
        api_messages.append({"role": "user", "content": tool_results})

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1536,
            system=system,
            messages=api_messages,
            tools=TOOLS,
        )

    # Extract final text
    reply_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            reply_text += block.text

    return reply_text, tool_actions if tool_actions else None


def _prepare_messages(
    messages: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Ensure messages alternate user/assistant and start with user.

    The Anthropic API requires messages to alternate between user and
    assistant roles, starting with user.  We strip leading assistant
    messages and merge consecutive same-role messages.
    """
    cleaned: list[dict[str, str]] = []
    started = False
    for msg in messages:
        if not started and msg["role"] == "assistant":
            continue
        started = True
        cleaned.append(msg)

    if not cleaned:
        return []

    merged: list[dict[str, str]] = [cleaned[0]]
    for msg in cleaned[1:]:
        if msg["role"] == merged[-1]["role"]:
            merged[-1] = {
                "role": msg["role"],
                "content": merged[-1]["content"] + "\n\n" + msg["content"],
            }
        else:
            merged.append(msg)

    return merged


# ---------------------------------------------------------------------------
# Tool execution
# ---------------------------------------------------------------------------

def _execute_tool(
    tool_name: str, tool_input: dict[str, Any], db: Session
) -> dict[str, Any]:
    """Execute a tool call and return the result."""
    if tool_name == "create_task":
        return _tool_create_task(tool_input, db)
    return {"error": f"Unknown tool: {tool_name}"}


def _tool_create_task(
    params: dict[str, Any], db: Session
) -> dict[str, Any]:
    """Create a task in the database."""
    from src.models.tasks import Task, TaskPriority

    priority_str = params.get("priority", "medium").lower()
    priority_map = {
        "low": TaskPriority.LOW,
        "medium": TaskPriority.MEDIUM,
        "high": TaskPriority.HIGH,
        "urgent": TaskPriority.URGENT,
    }
    priority = priority_map.get(priority_str, TaskPriority.MEDIUM)

    due_date = None
    if params.get("due_date"):
        try:
            due_date = date.fromisoformat(params["due_date"])
        except ValueError:
            pass

    task = Task(
        title=params["title"][:500],
        description=params.get("description"),
        priority=priority,
        due_date=due_date,
        project_id=params.get("project_id"),
        parent_id=params.get("parent_id"),
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "success": True,
        "task_id": task.id,
        "title": task.title,
        "priority": task.priority.value,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "project_id": task.project_id,
        "parent_id": task.parent_id,
    }


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
