"""
Al-Mudeer - Analysis Service
Handles the business logic for analyzing inbox messages and generating AI responses.
Extracted from chat_routes.py for reuse in background workers.
"""

from typing import Optional, List, Dict
import re
import base64
from logging_config import get_logger
from models import create_outbox_message, approve_outbox_message, update_inbox_status
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
    Core logic to mark message as handled and trigger notifications.
    AI analysis has been removed.
    """
    try:
        from db_helper import get_db, fetch_one
        
        # 1. Fetch message details to ensure it exists and get sender info
        async with get_db() as db:
            message_data = await fetch_one(
                db, 
                "SELECT * FROM inbox_messages WHERE id = ?", 
                [message_id]
            )
        
        if not message_data:
            logger.warning(f"Message {message_id} not found for processing")
            return {"success": False, "error": "not_found"}

        # 2. Update status to 'analyzed' (handled) immediately if not already
        from models import update_inbox_status
        await update_inbox_status(message_id, "analyzed")
        
        # 3. Trigger mobile/desktop notifications
        try:
            notification_data = {
                "sender_name": message_data.get("sender_name", "Unknown"),
                "sender_contact": message_data.get("sender_contact"),
                "body": body or message_data.get("body", ""),
                "intent": "neutral",
                "urgency": "low",
                "sentiment": "neutral",
                "channel": message_data.get("channel", "whatsapp"),
                "attachments": attachments or []
            }
            await process_message_notifications(license_id, notification_data, message_id=message_id)
        except Exception as e:
            logger.warning(f"Notification failed for msg {message_id}: {e}")

        return {"success": True}
            
    except Exception as e:
        logger.error(f"Error in process_inbox_message_logic {message_id}: {e}", exc_info=True)
        raise e

