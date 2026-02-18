"""Chat / academic assistant endpoint with persistent history."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.schemas import ChatMessageRead, ChatRequest, ChatResponse
from src.chatbot.assistant import get_advice
from src.database import get_db
from src.models.chat import ChatMessage

router = APIRouter(prefix="/chat", tags=["chatbot"])


@router.get("/history", response_model=list[ChatMessageRead])
def get_history(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Return the most recent chat messages, oldest first."""
    messages = (
        db.query(ChatMessage)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )
    messages.reverse()
    result = []
    for msg in messages:
        result.append(
            ChatMessageRead(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                tool_actions=json.loads(msg.tool_actions) if msg.tool_actions else None,
                created_at=msg.created_at,
            )
        )
    return result


@router.post("/", response_model=ChatResponse)
def chat(body: ChatRequest, db: Session = Depends(get_db)):
    """Send a message and get an AI assistant response.

    Persists both the user message and the assistant response.
    Sends full conversation history to Claude for multi-turn context.
    """
    # 1. Persist the user message
    user_msg = ChatMessage(role="user", content=body.message)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # 2. Load recent conversation history for multi-turn context
    #    Only send the last 20 messages to the LLM to control token costs.
    #    (All messages are still persisted in the DB for the UI.)
    recent = (
        db.query(ChatMessage)
        .order_by(ChatMessage.created_at.desc())
        .limit(20)
        .all()
    )
    recent.reverse()
    messages_for_llm = [
        {"role": msg.role, "content": msg.content}
        for msg in recent
    ]

    # 3. Get assistant response (with recent history and tool support)
    reply, tool_actions = get_advice(messages_for_llm, db)

    # 4. Persist the assistant response
    assistant_msg = ChatMessage(
        role="assistant",
        content=reply,
        tool_actions=json.dumps(tool_actions) if tool_actions else None,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return ChatResponse(
        reply=reply,
        tool_actions=tool_actions,
        user_message_id=user_msg.id,
        assistant_message_id=assistant_msg.id,
    )


@router.delete("/history", status_code=204)
def clear_history(db: Session = Depends(get_db)):
    """Delete all chat messages to start a fresh conversation."""
    db.query(ChatMessage).delete()
    db.commit()
