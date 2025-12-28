"""
Al-Mudeer - User Presence Model
Tracks online/offline status and last seen timestamps
"""

from typing import Optional, Dict
from datetime import datetime, timezone, timedelta

from db_helper import get_db, execute_sql, fetch_one, commit_db, DB_TYPE
from logging_config import get_logger

logger = get_logger(__name__)

# Consider user offline after this many seconds of inactivity
OFFLINE_THRESHOLD_SECONDS = 60


async def update_presence(license_id: int, is_online: bool = True) -> bool:
    """
    Update user's presence status.
    Call this on WebSocket connect/disconnect and periodically on activity.
    
    Returns: True if successful
    """
    async with get_db() as db:
        try:
            now = datetime.now(timezone.utc)
            
            if DB_TYPE == "postgresql":
                await execute_sql(db, """
                    INSERT INTO user_presence (license_id, is_online, last_seen, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT (license_id) DO UPDATE SET
                        is_online = EXCLUDED.is_online,
                        last_seen = EXCLUDED.last_seen,
                        updated_at = EXCLUDED.updated_at
                """, (license_id, is_online, now, now))
            else:
                # SQLite upsert
                await execute_sql(db, """
                    INSERT INTO user_presence (license_id, is_online, last_seen, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(license_id) DO UPDATE SET
                        is_online = excluded.is_online,
                        last_seen = excluded.last_seen,
                        updated_at = excluded.updated_at
                """, (license_id, 1 if is_online else 0, now.isoformat(), now.isoformat()))
            
            await commit_db(db)
            return True
            
        except Exception as e:
            logger.error(f"Failed to update presence for license {license_id}: {e}")
            return False


async def get_presence(license_id: int) -> Dict:
    """
    Get user's current presence status.
    
    Returns:
        {
            "is_online": bool,
            "last_seen": str (ISO format) or None,
            "status_text": str  # "متصل الآن" or "آخر ظهور منذ 5 دقائق"
        }
    """
    async with get_db() as db:
        try:
            if DB_TYPE == "postgresql":
                result = await execute_sql(db, """
                    SELECT is_online, last_seen, updated_at
                    FROM user_presence
                    WHERE license_id = ?
                """, (license_id,))
            else:
                result = await execute_sql(db, """
                    SELECT is_online, last_seen, updated_at
                    FROM user_presence
                    WHERE license_id = ?
                """, (license_id,))
            
            row = await fetch_one(result)
            
            if not row:
                return {
                    "is_online": False,
                    "last_seen": None,
                    "status_text": "غير متصل"
                }
            
            is_online_raw = row[0]
            last_seen_raw = row[1]
            updated_at_raw = row[2]
            
            # Parse is_online (SQLite stores as 0/1)
            is_online = bool(is_online_raw)
            
            # Parse last_seen
            if isinstance(last_seen_raw, str):
                last_seen = datetime.fromisoformat(last_seen_raw.replace('Z', '+00:00'))
            elif isinstance(last_seen_raw, datetime):
                last_seen = last_seen_raw
            else:
                last_seen = None
            
            # Check if user is truly online (within threshold)
            if is_online and last_seen:
                now = datetime.now(timezone.utc)
                if last_seen.tzinfo is None:
                    last_seen = last_seen.replace(tzinfo=timezone.utc)
                
                seconds_ago = (now - last_seen).total_seconds()
                
                if seconds_ago > OFFLINE_THRESHOLD_SECONDS:
                    is_online = False
            
            # Generate status text
            if is_online:
                status_text = "متصل الآن"
            elif last_seen:
                status_text = _format_last_seen(last_seen)
            else:
                status_text = "غير متصل"
            
            return {
                "is_online": is_online,
                "last_seen": last_seen.isoformat() if last_seen else None,
                "status_text": status_text
            }
            
        except Exception as e:
            logger.error(f"Failed to get presence for license {license_id}: {e}")
            return {
                "is_online": False,
                "last_seen": None,
                "status_text": "غير متصل"
            }


def _format_last_seen(last_seen: datetime) -> str:
    """Format last seen time in Arabic."""
    now = datetime.now(timezone.utc)
    
    if last_seen.tzinfo is None:
        last_seen = last_seen.replace(tzinfo=timezone.utc)
    
    diff = now - last_seen
    
    if diff < timedelta(minutes=1):
        return "آخر ظهور منذ لحظات"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        if minutes == 1:
            return "آخر ظهور منذ دقيقة"
        elif minutes == 2:
            return "آخر ظهور منذ دقيقتين"
        elif minutes <= 10:
            return f"آخر ظهور منذ {minutes} دقائق"
        else:
            return f"آخر ظهور منذ {minutes} دقيقة"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        if hours == 1:
            return "آخر ظهور منذ ساعة"
        elif hours == 2:
            return "آخر ظهور منذ ساعتين"
        elif hours <= 10:
            return f"آخر ظهور منذ {hours} ساعات"
        else:
            return f"آخر ظهور منذ {hours} ساعة"
    elif diff < timedelta(days=7):
        days = diff.days
        if days == 1:
            return "آخر ظهور أمس"
        elif days == 2:
            return "آخر ظهور منذ يومين"
        else:
            return f"آخر ظهور منذ {days} أيام"
    else:
        # Format as date
        return f"آخر ظهور {last_seen.strftime('%d/%m/%Y')}"


async def set_offline(license_id: int) -> bool:
    """Mark user as offline (call on WebSocket disconnect)."""
    return await update_presence(license_id, is_online=False)


async def set_online(license_id: int) -> bool:
    """Mark user as online (call on WebSocket connect)."""
    return await update_presence(license_id, is_online=True)


async def heartbeat(license_id: int) -> bool:
    """
    Update last_seen without changing online status.
    Call this periodically while user is active.
    """
    async with get_db() as db:
        try:
            now = datetime.now(timezone.utc)
            
            if DB_TYPE == "postgresql":
                await execute_sql(db, """
                    UPDATE user_presence
                    SET last_seen = ?, updated_at = ?
                    WHERE license_id = ?
                """, (now, now, license_id))
            else:
                await execute_sql(db, """
                    UPDATE user_presence
                    SET last_seen = ?, updated_at = ?
                    WHERE license_id = ?
                """, (now.isoformat(), now.isoformat(), license_id))
            
            await commit_db(db)
            return True
            
        except Exception as e:
            logger.error(f"Failed to heartbeat for license {license_id}: {e}")
            return False
