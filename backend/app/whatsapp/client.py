"""
Sahay AI - WhatsApp Client
===========================

Meta WhatsApp Business API client wrapper.

Author: Jagadeep Mamidi
"""

import logging
import httpx
from typing import Optional, Dict, Any
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """
    Client for WhatsApp Cloud API.
    
    Handles sending messages, media, and templates.
    """
    
    def __init__(self):
        settings = get_settings()
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.access_token = settings.whatsapp_access_token
        self.api_version = settings.whatsapp_graph_api_version
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def send_text_message(self, to: str, message: str) -> Dict[str, Any]:
        """
        Send a text message.
        
        Args:
            to: Recipient phone number (with country code)
            message: Message text
            
        Returns:
            API response
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    async def upload_media(
        self, media_bytes: bytes, mime_type: str = "audio/mpeg"
    ) -> str:
        """
        Upload media to Meta's Media API.

        Args:
            media_bytes: Raw file bytes
            mime_type:   MIME type (e.g. "audio/mpeg", "audio/ogg")

        Returns:
            media_id from Meta
        """
        url = f"{self.base_url}/{self.phone_number_id}/media"

        # Media upload uses multipart/form-data, not JSON
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {self.access_token}"},
                data={"messaging_product": "whatsapp", "type": mime_type},
                files={"file": ("audio.mp3", media_bytes, mime_type)},
            )
            response.raise_for_status()
            media_id = response.json().get("id")
            logger.info(f"Uploaded media, id={media_id}")
            return media_id

    async def send_audio_message(
        self,
        to: str,
        audio_url: Optional[str] = None,
        media_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send an audio message via URL or uploaded media_id.

        Provide exactly one of audio_url or media_id.

        Args:
            to:        Recipient phone number
            audio_url: Public URL to audio file
            media_id:  Media ID from upload_media()

        Returns:
            API response
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"

        if media_id:
            audio_payload = {"id": media_id}
        elif audio_url:
            audio_payload = {"link": audio_url}
        else:
            raise ValueError("Provide either audio_url or media_id")

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "audio",
            "audio": audio_payload,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()
    
    async def send_interactive_buttons(
        self,
        to: str,
        header: str,
        body: str,
        buttons: list
    ) -> Dict[str, Any]:
        """
        Send interactive buttons message.
        
        Args:
            to: Recipient phone number
            header: Header text
            body: Body text
            buttons: List of button dicts with 'id' and 'title'
            
        Returns:
            API response
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {
                    "type": "text",
                    "text": header
                },
                "body": {
                    "text": body
                },
                "footer": {
                    "text": "Sahay AI - Government Scheme Assistant"
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    async def send_reaction(self, to: str, message_id: str, emoji: str = "👍") -> Dict[str, Any]:
        """
        Send a reaction to a message.
        
        Args:
            to: Recipient phone number
            message_id: ID of message to react to
            emoji: Reaction emoji
            
        Returns:
            API response
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "reaction",
            "reaction": {
                "message_id": message_id,
                "emoji": emoji
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Mark a message as read.
        
        Args:
            message_id: ID of message to mark as read
            
        Returns:
            API response
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()


_wa_client: Optional[WhatsAppClient] = None


def get_wa_client() -> WhatsAppClient:
    """Get or create singleton WhatsApp client."""
    global _wa_client
    if _wa_client is None:
        _wa_client = WhatsAppClient()
    return _wa_client
