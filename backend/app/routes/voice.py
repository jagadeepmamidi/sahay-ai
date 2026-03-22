"""
Sahay AI - Voice Routes
========================

API endpoints for speech-to-text and text-to-speech.

Author: Jagadeep Mamidi
"""

import logging
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["voice"])


class TranscriptionRequest(BaseModel):
    """Request for transcription."""

    language: Optional[str] = None


class TranslationRequest(BaseModel):
    """Request for translation."""

    text: str
    source_language: str
    target_language: str


class TranscriptionResponse(BaseModel):
    """Response from transcription."""

    text: str
    language: str


class TranslationResponse(BaseModel):
    """Response from translation."""

    translated_text: str
    source_language: str
    target_language: str


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...), language: Optional[str] = Form(None)
):
    """
    Transcribe audio to text.

    - For Indian languages (Telugu, Hindi, etc.): Uses Sarvam AI
    - For English: Uses Groq Whisper

    Args:
        file: Audio file (WebM, WAV, MP3, OGG)
        language: Optional language code (te, hi, en, etc.)

    Returns:
        Transcription text
    """
    try:
        audio_bytes = await file.read()

        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")

        from app.services.voice import get_voice_service

        voice_service = get_voice_service()

        text = voice_service.transcribe(audio_bytes, language)

        detected_lang = language or "unknown"

        return TranscriptionResponse(text=text, language=detected_lang)

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate text between languages.

    Uses Sarvam AI for Indian language pairs.

    Args:
        request: Translation request with text and language pair

    Returns:
        Translated text
    """
    try:
        from app.services.voice import get_voice_service

        voice_service = get_voice_service()

        translated = voice_service.translate(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
        )

        return TranslationResponse(
            translated_text=translated,
            source_language=request.source_language,
            target_language=request.target_language,
        )

    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/speak")
async def text_to_speech(text: str = Form(...), language: str = Form("te")):
    """
    Convert text to speech.

    Uses Sarvam AI bulbul-v2 for Indian languages.

    Args:
        text: Text to convert to speech
        language: Language code (te-IN, hi-IN, etc.)

    Returns:
        Audio file (MP3)
    """
    try:
        from app.services.voice import get_voice_service

        voice_service = get_voice_service()

        lang_map = {
            "te": "te-IN",
            "hi": "hi-IN",
            "ta": "ta-IN",
            "kn": "kn-IN",
            "ml": "ml-IN",
            "en": "en-IN",
        }

        lang_code = lang_map.get(language, language)

        audio_bytes = voice_service.text_to_speech(text=text, language_code=lang_code)

        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=response.mp3"},
        )

    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported languages for voice.

    Returns:
        Dict of supported languages
    """
    return {
        "stt": {
            "sarvam": [
                "te-IN",
                "hi-IN",
                "ta-IN",
                "kn-IN",
                "ml-IN",
                "mr-IN",
                "bn-IN",
                "gu-IN",
                "pa-IN",
                "od-IN",
            ],
            "groq": ["en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko", "ru"],
        },
        "tts": {
            "sarvam": [
                "te-IN",
                "hi-IN",
                "ta-IN",
                "kn-IN",
                "ml-IN",
                "mr-IN",
                "bn-IN",
                "gu-IN",
                "pa-IN",
                "od-IN",
            ]
        },
        "translate": {
            "available_pairs": [
                {"source": "te", "target": "en"},
                {"source": "hi", "target": "en"},
                {"source": "en", "target": "te"},
                {"source": "en", "target": "hi"},
            ]
        },
    }
