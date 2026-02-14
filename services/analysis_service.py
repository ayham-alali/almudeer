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
        if message_data:
            # Basic validation
            pass



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

        # Legacy Analysis Structure (Placeholder)
        data = {
            "intent": "neutral",
            "urgency": "low",
            "sentiment": "neutral",
            "language": "ar",
            "dialect": None,
            "summary": None,
            "draft_response": None
        }
        
        # Update inbox with analysis results
        await update_inbox_analysis(
            message_id=message_id,
            intent=data["intent"],
            urgency=data["urgency"],
            sentiment=data["sentiment"],
            language=data.get("language"),
            dialect=data.get("dialect"),
            summary=data["summary"],
            draft_response=data["draft_response"]
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

