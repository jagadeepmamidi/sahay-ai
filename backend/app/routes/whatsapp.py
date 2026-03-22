"""
Sahay AI - WhatsApp Routes
===========================

Webhook endpoints for WhatsApp Cloud API.
Includes the FIXED webhook verification handler.

Author: Jagadeep Mamidi
"""

import logging
from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook/whatsapp", tags=["whatsapp"])


class WhatsAppWebhook(BaseModel):
    """WhatsApp webhook payload."""
    object: str
    entry: list


@router.get("/")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
):
    """
    Verify webhook for WhatsApp Cloud API.
    
    Meta sends a GET request with hub.mode, hub.verify_token, and hub.challenge.
    We verify that hub.verify_token matches our configured token and return hub.challenge.
    
    IMPORTANT: hub.mode, hub.verify_token, hub.challenge must use alias= because
    dots are invalid Python parameter names in FastAPI.
    """
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "change-me")
    
    logger.info(f"Webhook verification - mode: {hub_mode}, token match: {hub_verify_token == verify_token}")
    
    if hub_verify_token == verify_token:
        logger.info("Webhook verified successfully")
        return PlainTextResponse(hub_challenge)
    
    logger.warning("Webhook verification failed - invalid token")
    raise HTTPException(status_code=403, detail="Invalid verify token")


@router.post("/")
async def handle_webhook(
    request: Request,
    webhook_data: Optional[WhatsAppWebhook] = None
):
    """
    Handle incoming WhatsApp messages.
    
    Receives POST requests from Meta with message data.
    Processes the message and sends a text reply, plus a voice reply
    for Indian languages (via Sarvam AI TTS + Meta Media Upload).
    """
    try:
        data = await request.json()
        logger.info(f"Received webhook: {data}")
        
        from app.whatsapp.handler import get_whatsapp_handler
        
        handler = get_whatsapp_handler()
        
        if webhook_data and webhook_data.object == "whatsapp_business_account":
            result = await handler.process_message(data)
            
            if result:
                from app.whatsapp.client import get_wa_client
                wa_client = get_wa_client()
                
                # Always send the text reply first
                await wa_client.send_text_message(
                    to=result["to"],
                    message=result["message"]
                )
                logger.info(f"Sent text response to {result['to']}")
                
                # Send voice reply for Indian languages (best-effort)
                language = result.get("language", "en")
                if language in {"te", "hi", "ta", "kn", "ml", "or", "bn", "mr", "gu", "pa"}:
                    try:
                        from app.services.voice import get_voice_service, SARVAM_LANGUAGE_MAP
                        
                        voice_service = get_voice_service()
                        tts_lang = SARVAM_LANGUAGE_MAP.get(language, f"{language}-IN")
                        audio_bytes = voice_service.text_to_speech(
                            text=result["message"],
                            language_code=tts_lang,
                        )
                        
                        media_id = await wa_client.upload_media(audio_bytes, mime_type="audio/mpeg")
                        await wa_client.send_audio_message(to=result["to"], media_id=media_id)
                        logger.info(f"Sent voice reply to {result['to']} in {language}")
                    except Exception as voice_err:
                        logger.warning(f"Voice reply failed (text was still sent): {voice_err}")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/test")
async def test_webhook(
    to: str,
    message: str
):
    """
    Test endpoint to send a message.
    
    Useful for testing without WhatsApp.
    """
    try:
        from app.whatsapp.client import get_wa_client
        
        wa_client = get_wa_client()
        result = await wa_client.send_text_message(to=to, message=message)
        
        return {"status": "ok", "result": result}
        
    except Exception as e:
        logger.error(f"Test webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
