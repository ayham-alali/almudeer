"""
Al-Mudeer - Presence and Real-time Indicators Routes
API endpoints for broadcasting typing, recording, and presence status
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Body, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

from db_helper import get_db, fetch_one
from dependencies import get_license_from_header
from services.websocket_manager import broadcast_typing_indicator, broadcast_recording_indicator

router = APIRouter(prefix="/api/presence", tags=["Chat Features"])


class IndicatorRequest(BaseModel):
    sender_contact: str
    is_active: bool
    channel: str = "whatsapp" # default to whatsapp if missing, or maybe generic


@router.post("/typing")
async def send_typing_indicator(
    data: IndicatorRequest,
    license: dict = Depends(get_license_from_header)
):
    """
    Broadcast that an agent is typing in a conversation.
    This informs other connected clients/UIs.
    """
    license_id = license.get("license_id")
    
    # NOTE: We do NOT broadcast to internal WebSocket here.
    # This endpoint is for OUTGOING indicators (Agent -> External Platform).
    # The app already knows the agent is typing; no need to echo it back.
    # Internal WebSocket broadcasts are only for INCOMING indicators from TelegramListenerService.
    
    # Send to external platform
    try:
        if data.channel == "telegram":
            # 1. Try Telegram Bot first (preferred/more stable)
            try:
                from services.telegram_service import TelegramBotManager
                from models.telegram_config import get_telegram_bot_token
                
                bot_token = await get_telegram_bot_token(license_id)
                if bot_token:
                    bot = TelegramBotManager.get_bot(license_id, bot_token)
                    await bot.send_typing_action(data.sender_contact)
                    return {"success": True}
            except Exception:
                pass

            # 2. Fallback to Telegram Phone API (User Account)
            try:
                import models
                from services.telegram_phone_service import TelegramPhoneService
                
                session = await models.get_telegram_phone_session(license_id, data.sender_contact)
                if session and session.session_string:
                    service = TelegramPhoneService()
                    await service.set_typing(
                        session.session_string,
                        data.sender_contact,
                        action="typing" if data.is_active else "cancel"
                    )
            except Exception:
                pass
                
        elif data.channel == "whatsapp":
            from services.whatsapp_service import WhatsAppService, get_whatsapp_config
            
            if data.is_active: # Only send "ON", WhatsApp handles timeout automatically
                config = await get_whatsapp_config(license_id)
                if config and config.get("is_active"):
                    service = WhatsAppService(
                        phone_number_id=config["phone_number_id"],
                        access_token=config["access_token"]
                    )
                    await service.send_typing_indicator(data.sender_contact)

    except Exception as e:
        # Don't fail the request if external indicator fails
        print(f"Failed to send external typing indicator: {e}")

    return {"success": True}


@router.post("/recording")
async def send_recording_indicator(
    data: IndicatorRequest,
    license: dict = Depends(get_license_from_header)
):
    """
    Broadcast that an agent is recording audio in a conversation.
    """
    license_id = license.get("license_id")
    
    # NOTE: No internal broadcast - see /typing endpoint comment.
    
    # Send to external platform
    try:
        if data.channel == "telegram":
            import models
            from services.telegram_phone_service import TelegramPhoneService
            
            session = await models.get_telegram_phone_session(license_id, data.sender_contact)
            if session and session.session_string:
                service = TelegramPhoneService()
                await service.set_typing(
                    session.session_string,
                    data.sender_contact,
                    action="recording" if data.is_active else "cancel"
                )
        # WhatsApp doesn't support "recording" distinct from "typing" well in Cloud API stub
        # We can map it to typing if we want, or ignore.
        
    except Exception as e:
        print(f"Failed to send external recording indicator: {e}")

    return {"success": True}


@router.get("/{sender_contact:path}")
async def get_contact_presence(
    sender_contact: str,
    license: dict = Depends(get_license_from_header)
):
    """
    Get presence status for a contact (customer).
    Inferred from their last message timestamp.
    """
    license_id = license.get("license_id")
    
    # Decoding URI component handled by FastAPI automatically for path params? 
    # Actually for "path" params with slashes it might be tricky but @ symbol is usually fine.
    # sender_contact might be like "@Yamen_Etaki"
    
    async with get_db() as db:
        # Find the latest message from this contact
        query = """
            SELECT created_at 
            FROM inbox_messages 
            WHERE license_key_id = ? AND sender_contact = ?
            ORDER BY created_at DESC 
            LIMIT 1
        """
        row = await fetch_one(db, query, [license_id, sender_contact])
        
        if not row:
            return {
                "is_online": False, 
                "last_seen": None,
                "status_text": "غير متصل"
            }
            
        last_seen_str = row.get("created_at")
        
        # Parse timestamp
        last_seen = None
        if isinstance(last_seen_str, str):
            try:
                last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
            except:
                pass
        elif isinstance(last_seen_str, datetime):
            last_seen = last_seen_str
            
        if not last_seen:
             return {
                "is_online": False, 
                "last_seen": None,
                "status_text": "غير متصل"
            }

        # Ensure UTC
        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)
            
        now = datetime.now(timezone.utc)
        diff = now - last_seen
        
        # Logic: Online if message within last 5 minutes
        is_online = diff < timedelta(minutes=5)
        
        # Format status text (Arabic)
        status_text = "غير متصل"
        if is_online:
            status_text = "متصل الآن"
        else:
            # Simple formatting
            if diff < timedelta(hours=1):
                mins = int(diff.total_seconds() / 60)
                status_text = f"آخر ظهور منذ {mins} دقيقة"
            elif diff < timedelta(days=1):
                hours = int(diff.total_seconds() / 3600)
                status_text = f"آخر ظهور منذ {hours} ساعة"
            elif diff < timedelta(days=7):
                days = diff.days
                status_text = f"آخر ظهور منذ {days} يوم"
            else:
                status_text = f"آخر ظهور {last_seen.strftime('%Y-%m-%d')}"

        return {
            "is_online": is_online,
            "last_seen": last_seen.isoformat(),
            "status_text": status_text
        }

