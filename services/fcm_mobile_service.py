"""
Al-Mudeer - FCM Mobile Push Service
Handles Firebase Cloud Messaging for mobile app push notifications
"""

import os
import json
import httpx
from typing import Optional, List
from logging_config import get_logger

logger = get_logger(__name__)

# FCM Server Key from environment (for HTTP v1 API, we use service account)
FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY")


async def ensure_fcm_tokens_table():
    """Ensure fcm_tokens table exists."""
    from db_helper import get_db, execute_sql, commit_db, DB_TYPE
    
    id_type = "SERIAL PRIMARY KEY" if DB_TYPE == "postgresql" else "INTEGER PRIMARY KEY AUTOINCREMENT"
    ts_default = "TIMESTAMP DEFAULT NOW()" if DB_TYPE == "postgresql" else "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    
    async with get_db() as db:
        try:
            await execute_sql(db, f"""
                CREATE TABLE IF NOT EXISTS fcm_tokens (
                    id {id_type},
                    license_key_id INTEGER NOT NULL,
                    token TEXT NOT NULL UNIQUE,
                    platform TEXT DEFAULT 'android',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at {ts_default},
                    updated_at TIMESTAMP,
                    FOREIGN KEY (license_key_id) REFERENCES license_keys(id)
                )
            """)
            
            await execute_sql(db, """
                CREATE INDEX IF NOT EXISTS idx_fcm_token
                ON fcm_tokens(token)
            """)
            
            await execute_sql(db, """
                CREATE INDEX IF NOT EXISTS idx_fcm_license
                ON fcm_tokens(license_key_id) 
            """)
            
            await commit_db(db)
            logger.info("FCM: fcm_tokens table verified")
        except Exception as e:
            logger.error(f"FCM: Verify table failed: {e}")


async def save_fcm_token(
    license_id: int,
    token: str,
    platform: str = "android"
) -> int:
    """Save a new FCM token for a license."""
    from db_helper import get_db, fetch_one, execute_sql, commit_db
    
    async with get_db() as db:
        # Check if token already exists
        existing = await fetch_one(
            db,
            "SELECT id FROM fcm_tokens WHERE token = ?",
            [token]
        )
        
        if existing:
            # Update existing token
            await execute_sql(
                db,
                """
                UPDATE fcm_tokens 
                SET license_key_id = ?, platform = ?, is_active = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE token = ?
                """,
                [license_id, platform, token]
            )
            await commit_db(db)
            logger.info(f"FCM: Token updated for license {license_id}")
            return existing["id"]
        
        # Create new token
        await execute_sql(
            db,
            """
            INSERT INTO fcm_tokens (license_key_id, token, platform)
            VALUES (?, ?, ?)
            """,
            [license_id, token, platform]
        )
        
        row = await fetch_one(
            db,
            "SELECT id FROM fcm_tokens WHERE token = ?",
            [token]
        )
        await commit_db(db)
        logger.info(f"FCM: Token registered for license {license_id}")
        return row["id"] if row else 0


async def remove_fcm_token(token: str) -> bool:
    """Remove an FCM token."""
    from db_helper import get_db, execute_sql, commit_db
    
    async with get_db() as db:
        await execute_sql(
            db,
            "DELETE FROM fcm_tokens WHERE token = ?",
            [token]
        )
        await commit_db(db)
        logger.info(f"FCM: Token removed")
        return True


async def send_fcm_notification(
    token: str,
    title: str,
    body: str,
    data: Optional[dict] = None,
    link: Optional[str] = None
) -> bool:
    """
    Send push notification to a single FCM token using legacy HTTP API.
    
    For production, consider migrating to HTTP v1 API with service account.
    """
    if not FCM_SERVER_KEY:
        logger.warning("FCM: Server key not configured")
        return False
    
    try:
        payload = {
            "to": token,
            "notification": {
                "title": title,
                "body": body,
                "sound": "default",
                "click_action": "FLUTTER_NOTIFICATION_CLICK"
            },
            "data": data or {},
            "priority": "high"
        }
        
        if link:
            payload["data"]["link"] = link
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://fcm.googleapis.com/fcm/send",
                json=payload,
                headers={
                    "Authorization": f"key={FCM_SERVER_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success", 0) > 0:
                    logger.info(f"FCM: Notification sent: {title[:30]}...")
                    return True
                else:
                    logger.warning(f"FCM: Notification failed: {result}")
                    return False
            else:
                logger.error(f"FCM: HTTP error {response.status_code}: {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"FCM: Error sending notification: {e}")
        return False


async def send_fcm_to_license(
    license_id: int,
    title: str,
    body: str,
    data: Optional[dict] = None,
    link: Optional[str] = None
) -> int:
    """
    Send push notification to all mobile devices for a license.
    
    Returns the number of successful sends.
    """
    from db_helper import get_db, fetch_all, execute_sql, commit_db
    
    sent_count = 0
    expired_ids = []
    
    async with get_db() as db:
        rows = await fetch_all(
            db,
            """
            SELECT id, token FROM fcm_tokens
            WHERE license_key_id = ? AND is_active = TRUE
            """,
            [license_id]
        )
        
        if not rows:
            return 0
        
        for row in rows:
            success = await send_fcm_notification(
                token=row["token"],
                title=title,
                body=body,
                data=data,
                link=link
            )
            
            if success:
                sent_count += 1
            else:
                expired_ids.append(row["id"])
        
        # Mark failed tokens as inactive
        if expired_ids:
            placeholders = ",".join("?" for _ in expired_ids)
            await execute_sql(
                db,
                f"UPDATE fcm_tokens SET is_active = FALSE WHERE id IN ({placeholders})",
                expired_ids
            )
            await commit_db(db)
            logger.info(f"FCM: Marked {len(expired_ids)} tokens as inactive")
    
    return sent_count
