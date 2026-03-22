"""
Sahay AI - Voice Service
========================

Speech-to-text and text-to-speech services.
- Sarvam AI for Indian languages (Telugu, Hindi, etc.)
- Groq Whisper as fallback for English

Author: Jagadeep Mamidi
"""

import base64
import io
import logging
from typing import Optional

import httpx
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
from tenacity.retry import retry_if_exception_type

from app.core.config import get_settings

logger = logging.getLogger(__name__)

INDIAN_LANGUAGES = {"te", "hi", "ta", "kn", "ml", "or", "bn", "mr", "gu", "pa"}

SARVAM_LANGUAGE_MAP = {
    "te": "te-IN",
    "hi": "hi-IN",
    "ta": "ta-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "or": "od-IN",
    "bn": "bn-IN",
    "mr": "mr-IN",
    "gu": "gu-IN",
    "pa": "pa-IN",
    "en": "en-IN",
}


class VoiceService:
    """
    Voice service for STT, TTS, and translation.

    Uses Sarvam AI for Indian languages (check dashboard for free tier limits)
    Falls back to Groq Whisper for English.

    Sarvam Docs: https://docs.sarvam.ai/
    Sarvam Dashboard: https://dashboard.sarvam.ai/
    """

    def __init__(self):
        settings = get_settings()
        self.sarvam_api_key = settings.sarvam_api_key
        self.sarvam_stt_model = settings.sarvam_stt_model
        self.sarvam_tts_model = settings.sarvam_tts_model
        self.sarvam_translate_model = settings.sarvam_translate_model

        self.groq_client = Groq(api_key=settings.groq_api_key)
        self.groq_whisper_model = settings.groq_whisper_model

        self._init_sarvam()

    def _init_sarvam(self):
        """Initialize Sarvam client if API key is available."""
        self.sarvam_client = None
        if self.sarvam_api_key:
            try:
                from sarvamai import SarvamAI

                self.sarvam_client = SarvamAI(api_subscription_key=self.sarvam_api_key)
                logger.info("Sarvam AI client initialized")
            except ImportError:
                logger.warning("sarvamai package not installed. Using HTTP fallback.")
            except Exception as e:
                logger.warning(f"Failed to initialize Sarvam client: {e}")

    def _map_language(self, lang_code: Optional[str]) -> str:
        """Map language code to Sarvam format."""
        if lang_code is None:
            return "unknown"
        return SARVAM_LANGUAGE_MAP.get(lang_code.lower(), lang_code)

    def _is_indian_language(self, lang_code: Optional[str]) -> bool:
        """Check if language is an Indian language supported by Sarvam AI.

        English (plain 'en' or any 'en-*' locale) is always routed to Groq Whisper,
        not Sarvam, per the implementation plan.
        """
        if lang_code is None:
            return True  # Default to Sarvam for unknown/undetected languages
        lang = lang_code.lower()
        # English in any form (en, en-US, en-IN, en-GB …) → Groq Whisper
        if lang == "en" or lang.startswith("en-"):
            return False
        return lang in INDIAN_LANGUAGES

    def transcribe_sarvam(
        self, audio_bytes: bytes, language_code: str = "unknown"
    ) -> str:
        """
        Transcribe audio using Sarvam AI saarika.

        Supports: Hindi, Bengali, Tamil, Telugu, Gujarati, Kannada,
                  Malayalam, Marathi, Punjabi, Odia
        """
        if self.sarvam_client is None:
            raise RuntimeError("Sarvam client not initialized")

        audio_io = io.BytesIO(audio_bytes)
        audio_io.name = "audio.webm"

        response = self.sarvam_client.speech_to_text.transcribe(
            file=audio_io, model=self.sarvam_stt_model, language_code=language_code
        )

        if hasattr(response, "transcript"):
            return response.transcript
        return str(response)

    def transcribe_sarvam_http(
        self, audio_bytes: bytes, language_code: str = "unknown"
    ) -> str:
        """
        Transcribe audio using Sarvam AI HTTP API (fallback if SDK fails).
        """

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
        )
        def _call():
            with httpx.Client(timeout=30.0) as client:
                files = {"file": ("audio.webm", audio_bytes, "audio/webm")}
                data = {"model": self.sarvam_stt_model, "language_code": language_code}
                headers = {"api-subscription-key": self.sarvam_api_key}

                response = client.post(
                    "https://api.sarvam.ai/speech-to-text",
                    files=files,
                    data=data,
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()

        result = _call()
        return result.get("transcript", "")

    def transcribe_groq(
        self, audio_bytes: bytes, language: Optional[str] = None
    ) -> str:
        """
        Transcribe audio using Groq Whisper.

        Faster but less accurate for Indian languages.
        Best for English.
        """
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.webm"

        result = self.groq_client.audio.transcriptions.create(
            file=audio_file,
            model=self.groq_whisper_model,
            language=language if language and language != "unknown" else None,
            response_format="text",
        )
        return result.text

    def transcribe(
        self, audio_bytes: bytes, language_code: Optional[str] = None
    ) -> str:
        """
        Transcribe audio to text.

        Automatically routes to Sarvam for Indian languages,
        Groq Whisper for English.

        Args:
            audio_bytes: Audio file content (WebM/WAV/MP3)
            language_code: Language code (e.g., 'te', 'hi', 'en')

        Returns:
            Transcribed text
        """
        lang = self._map_language(language_code)

        if self._is_indian_language(language_code):
            try:
                if self.sarvam_client:
                    return self.transcribe_sarvam(audio_bytes, lang)
                return self.transcribe_sarvam_http(audio_bytes, lang)
            except Exception as e:
                logger.warning(f"Sarvam STT failed: {e}, falling back to Groq")
                return self.transcribe_groq(audio_bytes, language_code)
        else:
            return self.transcribe_groq(audio_bytes, language_code)

    def text_to_speech(
        self,
        text: str,
        language_code: str = "te-IN",
        voice_style: str = "conversational",
    ) -> bytes:
        """
        Convert text to speech using Sarvam AI.

        Args:
            text: Text to convert
            language_code: Target language (e.g., 'te-IN', 'hi-IN')
            voice_style: 'formal', 'conversational', or 'storytelling'

        Returns:
            Audio bytes (MP3 format)
        """
        if self.sarvam_client is None:
            raise RuntimeError("Sarvam client not initialized")

        response = self.sarvam_client.text_to_speech.convert(
            text=text,
            language_code=language_code,
            model=self.sarvam_tts_model,
            voice_style=voice_style,
        )

        if hasattr(response, "audio"):
            return base64.b64decode(response.audio)

        audio_b64 = str(response)
        return base64.b64decode(audio_b64)

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        """
        Translate text between languages.

        Args:
            text: Text to translate
            source_language: Source language code (e.g., 'te')
            target_language: Target language code (e.g., 'en')

        Returns:
            Translated text
        """
        if self.sarvam_client is None:
            raise RuntimeError("Sarvam client not initialized")

        source = self._map_language(source_language)
        target = self._map_language(target_language)

        response = self.sarvam_client.text.translate(
            input=text, source_language=source, target_language=target
        )

        if hasattr(response, "translated_text"):
            return response.translated_text
        return str(response)


_voice_service: Optional[VoiceService] = None


def get_voice_service() -> VoiceService:
    """Get or create singleton voice service."""
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceService()
    return _voice_service
