"""
Chat Routes
===========

API endpoints for conversational AI interactions.
Supports multilingual queries and context-aware responses.
Uses Groq Llama 3.3 for fast inference.
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.orchestrator import get_orchestrator
from app.core.config import SUPPORTED_LANGUAGES, get_settings

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()


def _translate_text(lang_agent, text: str, target_lang: str) -> str:
    """Translate helper that leaves empty/English text untouched on failure."""
    if not text or target_lang == "en":
        return text
    try:
        return lang_agent.translate_from_english(text, target_lang)
    except Exception:
        return text


# ==================== Request/Response Models ====================


class ChatMessage(BaseModel):
    """A single chat message."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = None
    language: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat request from the user."""

    message: str = Field(
        ..., min_length=1, max_length=2000, description="User's message"
    )
    session_id: Optional[str] = Field(
        None, description="Session ID for conversation context"
    )
    language: Optional[str] = Field(
        "auto", description="Language code (auto for detection)"
    )
    user_profile: Optional[dict] = Field(
        None, description="User profile for personalization"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What schemes can I apply for as a farmer in Maharashtra?",
                "language": "en",
                "user_profile": {
                    "occupation": "farmer",
                    "state": "Maharashtra",
                    "income": "below_poverty_line",
                },
            }
        }


class SchemeCard(BaseModel):
    """Scheme information card embedded in responses."""

    id: str
    name: str
    category: str
    benefit_summary: str
    eligibility_summary: str
    apply_url: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response from the AI."""

    success: bool = True
    message: str = Field(..., description="AI response message")
    session_id: str = Field(..., description="Session ID for context")
    detected_language: str = Field(..., description="Detected input language")
    response_language: str = Field(..., description="Language of response")
    intent: Optional[str] = Field(None, description="Detected user intent")
    confidence: Optional[float] = Field(None, description="Intent confidence score")
    schemes: Optional[List[SchemeCard]] = Field(None, description="Related schemes")
    suggested_questions: Optional[List[str]] = Field(
        None, description="Follow-up suggestions"
    )
    timestamp: str = Field(..., description="Response timestamp")


class ConversationHistory(BaseModel):
    """Conversation history response."""

    session_id: str
    messages: List[ChatMessage]
    created_at: str
    last_activity: str


class FeedbackRequest(BaseModel):
    """User feedback on a response."""

    session_id: str
    message_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    feedback_text: Optional[str] = None
    helpful: Optional[bool] = None


# ==================== Endpoints ====================


@router.post("", response_model=ChatResponse)
@router.post("/", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message to Sahay AI and get a response.

    Supports multilingual queries - the AI will detect the language
    and respond in the same language using Groq Llama 3.3.
    """
    try:
        session_id = request.session_id or str(uuid4())
        orchestrator = get_orchestrator()

        detected_lang = request.language
        if request.language == "auto":
            from app.agents.language_agent import LanguageAgent

            lang_agent = LanguageAgent()
            detected_lang = lang_agent.detect_language(request.message)

        if detected_lang not in SUPPORTED_LANGUAGES:
            detected_lang = "en"

        result = await orchestrator.process(
            query=request.message,
            language=detected_lang,
            session_id=session_id,
            user_profile=request.user_profile,
        )

        lang_agent = None
        if detected_lang != "en":
            from app.agents.language_agent import LanguageAgent

            lang_agent = LanguageAgent()

        scheme_cards = None
        if result.get("schemes"):
            scheme_cards = [
                SchemeCard(
                    id=s.get("id", ""),
                    name=_translate_text(lang_agent, s.get("name", ""), detected_lang),
                    category=_translate_text(
                        lang_agent, s.get("category", ""), detected_lang
                    ),
                    benefit_summary=_translate_text(
                        lang_agent, s.get("benefit_summary", ""), detected_lang
                    ),
                    eligibility_summary=_translate_text(
                        lang_agent, s.get("eligibility_summary", ""), detected_lang
                    ),
                    apply_url=s.get("apply_url"),
                )
                for s in result["schemes"][:5]
            ]

        suggested_questions = result.get(
            "suggested_questions",
            [
                "What documents do I need?",
                "How do I apply online?",
                "What is the benefit amount?",
            ],
        )
        if detected_lang != "en":
            suggested_questions = [
                _translate_text(lang_agent, question, detected_lang)
                for question in suggested_questions
            ]

        return ChatResponse(
            success=True,
            message=result.get(
                "response", "I apologize, I couldn't process your request."
            ),
            session_id=result.get("session_id", session_id),
            detected_language=detected_lang,
            response_language=detected_lang,
            intent=result.get("intent"),
            confidence=result.get("confidence"),
            schemes=scheme_cards,
            suggested_questions=suggested_questions,
            timestamp=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}", response_model=ConversationHistory)
async def get_chat_history(session_id: str):
    """
    Get conversation history for a session.
    """
    try:
        orchestrator = get_orchestrator()
        history = orchestrator.get_conversation_history(session_id)

        if not history:
            raise HTTPException(status_code=404, detail="Session not found")

        return ConversationHistory(
            session_id=session_id,
            messages=[
                ChatMessage(
                    role=msg["role"],
                    content=msg["content"],
                    timestamp=msg.get("timestamp"),
                    language=msg.get("language"),
                )
                for msg in history.get("messages", [])
            ],
            created_at=history.get("created_at", ""),
            last_activity=history.get("last_activity", ""),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"History error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback on a chat response.
    Used to improve the AI over time.
    """
    try:
        try:
            from app.db.supabase_client import get_supabase

            client = get_supabase()
            client.table("feedback").insert(
                {
                    "session_id": request.session_id,
                    "message_index": 0,
                    "rating": request.rating,
                    "feedback_text": request.feedback_text or "",
                }
            ).execute()
            logger.info(
                f"Feedback stored: session={request.session_id}, rating={request.rating}"
            )
        except Exception as db_err:
            logger.warning(f"Could not store feedback in DB: {db_err}")
            logger.info(
                f"Feedback received: session={request.session_id}, rating={request.rating}"
            )

        return {"success": True, "message": "Thank you for your feedback!"}

    except Exception as e:
        logger.error(f"Feedback error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported languages for chat.
    """
    return {"languages": SUPPORTED_LANGUAGES, "default": settings.default_language}
