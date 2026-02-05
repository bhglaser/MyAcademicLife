"""Chat / academic advisor endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.schemas import ChatRequest, ChatResponse
from src.chatbot.advisor import get_advice
from src.database import get_db

router = APIRouter(prefix="/chat", tags=["chatbot"])


@router.post("/", response_model=ChatResponse)
def chat(body: ChatRequest, db: Session = Depends(get_db)):
    reply = get_advice(body.message, db)
    return ChatResponse(reply=reply)
