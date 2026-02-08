"""
Al-Mudeer - Analysis Service
Handles the business logic for analyzing inbox messages and generating AI responses.
Extracted from chat_routes.py for reuse in background workers.
"""

from typing import Optional, List, Dict
import re
import base64
from logging_config import get_logger
from models import update_inbox_analysis, create_outbox_message, approve_outbox_message, update_inbox_status
from agent import process_message
from services.notification_service import process_message_notifications

logger = get_logger(__name__)

async def process_inbox_message_logic(
    message_id: int,
    body: str,
    license_id: int,
    telegram_chat_id: str = None,
    attachments: Optional[List[dict]] = None
):
    """
    Core logic to analyze message with AI and optionally auto-reply.
    Now designed to be called from a robust background task queue.
    """
    try:
        from models.inbox import get_inbox_message_by_id, get_chat_history_for_llm
        message_data = await get_inbox_message_by_id(message_id, license_id)
        chat_history = ""
        
        if message_data:
            sender = message_data.get("sender_contact") or message_data.get("sender_id")
            if sender:
                try: chat_history = await get_chat_history_for_llm(license_id, sender, limit=10)
                except: pass

        # --- Voice Note Transcription (NEW) ---
        # Decode and transcribe audio attachments so the AI can understand them
        if attachments:
            for att in attachments:
                # Check for audio types
                if att.get("type", "").startswith(("audio", "voice", "audio/ogg", "audio/mpeg", "audio/wav")):
                    if att.get("base64"):
                        try:
                            logger.info(f"Transcribing voice note for message {message_id}...")
                            audio_bytes = base64.b64decode(att["base64"])
                            
                            # Import here to avoid circular dependencies if any
                            from services.voice_service import transcribe_voice_message
                            
                            # Transcribe
                            trans_result = await transcribe_voice_message(audio_bytes)
                            
                            if trans_result["success"]:
                                transcribed_text = trans_result["text"]
                                logger.info(f"Transcription success for msg {message_id}: {transcribed_text[:50]}...")
                                
                                # Append to body
                                if body:
                                    body += f"\n\n[Voice Message Transcription]: {transcribed_text}"
                                else:
                                    body = f"[Voice Message Transcription]: {transcribed_text}"
                            else:
                                logger.warning(f"Transcription failed for msg {message_id}: {trans_result.get('error')}")
                                
                        except Exception as e:
                            logger.error(f"Error processing voice attachment for msg {message_id}: {e}")

        # Detect media-only and skip full AI if just simple media
        is_media_only = False
        if attachments and (not body or len(body.strip()) < 3):
            has_img = any(a.get("type", "").startswith("image") for a in attachments)
            has_aud = any(a.get("type", "").startswith(("audio", "voice")) for a in attachments)
            if has_img and not has_aud: is_media_only = True
        
        if is_media_only:
            await update_inbox_analysis(message_id, "media", "low", "neutral", None, None, "📷 صورة بدون نص", "")
            return {
                "success": True, 
                "action": "media_only", 
                "message_id": message_id
            }

        # Call AI Agent - DISABLED by user request
        # Result is now hardcoded to bypass LLM analysis
        # result = await process_message(message=body, attachments=attachments, history=chat_history)
        
        # Hardcoded result to skip AI
        data = {
            "intent": "neutral",
            "urgency": "medium",
            "sentiment": "neutral",
            "language": "ar", # Default to Arabic
            "dialect": None,
            "summary": None,
            "draft_response": None # CRITICAL: No draft response
        }
        
        # Check for transcription to append to body if needed (already done above)
        
        # We process the result as if it came from AI, but it's just defaults
        # The update_inbox_analysis will save these neutral values
        await update_inbox_analysis(
            message_id=message_id,
            intent=data["intent"], urgency=data["urgency"], sentiment=data["sentiment"],
            language=data.get("language"), dialect=data.get("dialect"),
            summary=data["summary"], draft_response=data["draft_response"]
        )
        
        # Notifications
        try:
            await process_message_notifications(license_id, {
                    "sender_name": message_data.get("sender_name", "Unknown") if message_data else "Unknown",
                    "sender_contact": message_data.get("sender_contact") if message_data else None,
                    "body": body, "intent": data.get("intent"), "urgency": data.get("urgency"), "sentiment": data.get("sentiment"),
                    "channel": message_data.get("channel", "whatsapp") if message_data else "whatsapp",
                    "attachments": attachments
                }, message_id=message_id)
        except Exception as e:
            logger.warning(f"Notification failed for msg {message_id}: {e}")

        return {"success": True, "analysis": data}
            
    except Exception as e:
        logger.error(f"Error in process_inbox_message_logic {message_id}: {e}", exc_info=True)
        raise e # Rethrow so task queue marks it as failed

