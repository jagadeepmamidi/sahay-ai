"""
Sahay AI - WhatsApp Message Handler
===================================

Handles incoming WhatsApp messages and routes to appropriate processing.

Author: Jagadeep Mamidi
"""

import logging
from typing import Any, Dict, Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class WhatsAppHandler:
    """
    Handler for WhatsApp messages.

    Processes incoming messages, routes to chat agent,
    and sends responses.
    """

    def __init__(self):
        settings = get_settings()
        self.api_version = settings.whatsapp_graph_api_version
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

        self.greeting_message = {
            "te": "నమస్కారం! 🙏 మీకు భారత ప్రభుత్వ పథకాల గురించి తెలుసుకోవాలనుకుంటున్నారా? వడ్డించండి!",
            "hi": "नमस्ते! 🙏 क्या आप भारत सरकार की योजनाओं के बारे में जानना चाहते हैं? पूछिए!",
            "en": "Namaste! 🙏 How can I help you find government schemes today?",
        }

    def _detect_language(self, text: str) -> str:
        """Detect language from text."""
        try:
            from langdetect import detect

            lang = detect(text)
            if lang in ["te", "hi", "ta", "kn", "ml", "or", "bn"]:
                return lang
            return "en"
        except:
            return "en"

    async def _download_audio(
        self, audio_id: str, access_token: str
    ) -> Optional[bytes]:
        """Download audio file from WhatsApp."""
        url = f"{self.base_url}/{audio_id}"
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.content
        except Exception as e:
            logger.error(f"Failed to download audio: {e}")
            return None

    async def process_message(
        self, message_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Process an incoming WhatsApp message.

        Args:
            message_data: Parsed webhook message data

        Returns:
            Response dict with 'to', 'message', and optional 'audio'
        """
        try:
            entry = message_data.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})

            messages = value.get("messages", [])
            if not messages:
                return None

            message = messages[0]
            from_number = message.get("from")
            msg_id = message.get("id")
            msg_type = message.get("type")

            logger.info(f"Received {msg_type} message from {from_number}")

            if msg_type == "text":
                text = message.get("text", {}).get("body", "")
                language = self._detect_language(text)

                response_text = await self._generate_response(text, language)

                return {
                    "to": from_number,
                    "message": response_text,
                    "language": language,
                }

            elif msg_type == "audio":
                audio_id = message.get("audio", {}).get("id")
                if audio_id:
                    settings = get_settings()
                    audio_bytes = await self._download_audio(
                        audio_id, settings.whatsapp_access_token
                    )

                    if audio_bytes:
                        from app.services.voice import get_voice_service

                        voice_service = get_voice_service()

                        transcription = voice_service.transcribe(audio_bytes)
                        logger.info(f"Transcribed: {transcription}")

                        language = self._detect_language(transcription)
                        response_text = await self._generate_response(
                            transcription, language
                        )

                        return {
                            "to": from_number,
                            "message": response_text,
                            "language": language,
                        }

            return {
                "to": from_number,
                "message": "Sorry, I couldn't process that. Please try again!",
                "language": "en",
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return None

    async def _generate_response(self, query: str, language: str) -> str:
        """Generate response using RAG pipeline."""
        try:
            from app.agents.orchestrator import get_orchestrator

            orchestrator = get_orchestrator()

            result = await orchestrator.process(query=query, language=language)

            return result.get(
                "response", "Sorry, I couldn't find relevant information."
            )

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            fallback = {
                "te": "క్షమించండి, ఏదో లోపం జరిగింది. మళ్ళీ ప్రయత్నించండి.",
                "hi": "क्षमा करें, कुछ गलती हो गई। कृपया पुनः प्रयास करें।",
                "en": "Sorry, something went wrong. Please try again.",
            }
            return fallback.get(language, fallback["en"])

    def get_greeting(self, language: str = "en") -> str:
        """Get greeting message in the specified language."""
        return self.greeting_message.get(language, self.greeting_message["en"])


_whatsapp_handler: Optional[WhatsAppHandler] = None


def get_whatsapp_handler() -> WhatsAppHandler:
    """Get or create singleton WhatsApp handler."""
    global _whatsapp_handler
    if _whatsapp_handler is None:
        _whatsapp_handler = WhatsAppHandler()
    return _whatsapp_handler
