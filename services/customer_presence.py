"""
Al-Mudeer - Customer Presence Service
Tracks real customer last seen from WhatsApp and Telegram.
Syncs presence data in real-time to the Almudeer dashboard.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from logging_config import get_logger

logger = get_logger(__name__)


async def update_customer_presence(
    license_id: int,
    sender_contact: str,
    channel: str,
    is_online: bool = False,
    last_activity: Optional[datetime] = None
) -> bool:
    """
    Update customer presence based on their activity.
    Called when we receive a message from them.
    
    Args:
        license_id: The workspace license ID
        sender_contact: Customer's contact identifier (phone, username, etc.)
        channel: whatsapp, telegram, telegram_bot, email
        is_online: Whether customer is currently online (if known)
        last_activity: Last activity timestamp (defaults to now)
    """
    from db_helper import get_db, execute_sql, commit_db, DB_TYPE
    
    if last_activity is None:
        last_activity = datetime.utcnow()
    
    try:
        async with get_db() as db:
            if DB_TYPE == "postgresql":
                await execute_sql(
                    db,
                    """
                    INSERT INTO customer_presence 
                        (license_id, sender_contact, channel, is_online, last_seen, last_activity, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, NOW())
                    ON CONFLICT (license_id, sender_contact) 
                    DO UPDATE SET 
                        is_online = EXCLUDED.is_online,
                        last_seen = CASE 
                            WHEN NOT EXCLUDED.is_online THEN EXCLUDED.last_seen 
                            ELSE customer_presence.last_seen 
                        END,
                        last_activity = EXCLUDED.last_activity,
                        channel = EXCLUDED.channel,
                        updated_at = NOW()
                    """,
                    [license_id, sender_contact, channel, is_online, last_activity, last_activity]
                )
            else:
                await execute_sql(
                    db,
                    """
                    INSERT OR REPLACE INTO customer_presence 
                        (license_id, sender_contact, channel, is_online, last_seen, last_activity, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                    """,
                    [license_id, sender_contact, channel, is_online, 
                     last_activity.isoformat() if not is_online else None,
                     last_activity.isoformat()]
                )
            await commit_db(db)
        
        logger.debug(f"Updated presence for {sender_contact}: online={is_online}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update customer presence: {e}")
        return False


async def get_customer_presence(
    license_id: int,
    sender_contact: str
) -> Dict[str, Any]:
    """
    Get customer's presence status.
    
    Returns:
        {
            "is_online": bool,
            "last_seen": datetime or None,
            "last_activity": datetime,
            "status_text": Arabic formatted string
        }
    """
    from db_helper import get_db, fetch_one
    
    try:
        async with get_db() as db:
            row = await fetch_one(
                db,
                """
                SELECT is_online, last_seen, last_activity, channel, updated_at
                FROM customer_presence
                WHERE license_id = ? AND sender_contact = ?
                """,
                [license_id, sender_contact]
            )
        
        if not row:
            return {
                "is_online": False,
                "last_seen": None,
                "last_activity": None,
                "status_text": "غير متصل"
            }
        
        is_online = row.get("is_online", False)
        last_activity = row.get("last_activity")
        last_seen = row.get("last_seen")
        
        # Parse datetime if string
        if isinstance(last_activity, str):
            try:
                last_activity = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
            except:
                last_activity = None
        
        if isinstance(last_seen, str):
            try:
                last_seen = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
            except:
                last_seen = None
        
        # Check if "online" status is stale (no activity for 5+ minutes)
        if is_online and last_activity:
            if datetime.utcnow() - last_activity > timedelta(minutes=5):
                is_online = False
                last_seen = last_activity
        
        # Format status text in Arabic
        status_text = format_customer_last_seen(is_online, last_activity or last_seen)
        
        return {
            "is_online": is_online,
            "last_seen": last_seen.isoformat() if last_seen else None,
            "last_activity": last_activity.isoformat() if last_activity else None,
            "status_text": status_text,
            "channel": row.get("channel")
        }
        
    except Exception as e:
        logger.error(f"Failed to get customer presence: {e}")
        return {
            "is_online": False,
            "last_seen": None,
            "last_activity": None,
            "status_text": "غير متوفر"
        }


def format_customer_last_seen(is_online: bool, last_time: Optional[datetime]) -> str:
    """
    Format customer last seen in Arabic, matching WhatsApp/Telegram style.
    """
    if is_online:
        return "متصل الآن"
    
    if not last_time:
        return "غير متصل"
    
    now = datetime.utcnow()
    diff = now - last_time
    
    if diff.total_seconds() < 60:
        return "كان متصل الآن"
    elif diff.total_seconds() < 120:
        return "آخر ظهور منذ دقيقة"
    elif diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() / 60)
        return f"آخر ظهور منذ {minutes} دقيقة"
    elif diff.total_seconds() < 7200:
        return "آخر ظهور منذ ساعة"
    elif diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f"آخر ظهور منذ {hours} ساعات"
    elif diff.days == 1:
        return "آخر ظهور أمس"
    elif diff.days < 7:
        return f"آخر ظهور منذ {diff.days} أيام"
    else:
        # Format date
        return f"آخر ظهور {last_time.strftime('%d/%m/%Y')}"


async def mark_customer_online(
    license_id: int,
    sender_contact: str,
    channel: str
):
    """Mark customer as online when they send a message."""
    await update_customer_presence(
        license_id=license_id,
        sender_contact=sender_contact,
        channel=channel,
        is_online=True,
        last_activity=datetime.utcnow()
    )


async def mark_customer_offline(
    license_id: int,
    sender_contact: str
):
    """Mark customer as offline (e.g., from webhook status update)."""
    await update_customer_presence(
        license_id=license_id,
        sender_contact=sender_contact,
        channel="",
        is_online=False,
        last_activity=datetime.utcnow()
    )
