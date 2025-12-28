"""
Al-Mudeer - Message Reactions Model
Handles emoji reactions on messages (visible to both parties)
"""

from typing import List, Dict, Optional
from datetime import datetime

from db_helper import get_db, execute_sql, fetch_all, fetch_one, commit_db, DB_TYPE
from logging_config import get_logger

logger = get_logger(__name__)


async def add_reaction(
    message_id: int,
    license_id: int,
    emoji: str,
    user_type: str = "agent"  # "agent" or "customer"
) -> Dict:
    """
    Add a reaction to a message.
    If reaction already exists, it's a no-op (UNIQUE constraint).
    
    Args:
        message_id: ID of the inbox message
        license_id: License ID of the user adding reaction
        emoji: The emoji reaction (e.g., "❤️", "👍")
        user_type: "agent" for business owner, "customer" for message sender
        
    Returns:
        {"success": bool, "reaction_id": int or None, "error": str or None}
    """
    async with get_db() as db:
        try:
            if DB_TYPE == "postgresql":
                sql = """
                    INSERT INTO message_reactions (message_id, license_id, user_type, emoji)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT (message_id, license_id, user_type, emoji) DO NOTHING
                    RETURNING id
                """
                row = await fetch_one(db, sql, (message_id, license_id, user_type, emoji))
                reaction_id = row["id"] if row else None
            else:
                sql = """
                    INSERT OR IGNORE INTO message_reactions (message_id, license_id, user_type, emoji)
                    VALUES (?, ?, ?, ?)
                """
                await execute_sql(db, sql, (message_id, license_id, user_type, emoji))
                
                # Get the ID
                select_sql = """
                    SELECT id FROM message_reactions 
                    WHERE message_id = ? AND license_id = ? AND user_type = ? AND emoji = ?
                """
                row = await fetch_one(db, select_sql, (message_id, license_id, user_type, emoji))
                reaction_id = row["id"] if row else None
            
            await commit_db(db)
            
            logger.info(f"Added reaction {emoji} to message {message_id} by {user_type}")
            
            return {
                "success": True,
                "reaction_id": reaction_id
            }
            
        except Exception as e:
            logger.error(f"Failed to add reaction: {e}")
            return {
                "success": False,
                "reaction_id": None,
                "error": str(e)
            }


async def remove_reaction(
    message_id: int,
    license_id: int,
    emoji: str,
    user_type: str = "agent"
) -> Dict:
    """
    Remove a reaction from a message.
    
    Returns:
        {"success": bool, "removed": bool, "error": str or None}
    """
    async with get_db() as db:
        try:
            sql = """
                DELETE FROM message_reactions 
                WHERE message_id = ? AND license_id = ? AND user_type = ? AND emoji = ?
            """
            await execute_sql(db, sql, (message_id, license_id, user_type, emoji))
            await commit_db(db)
            
            logger.info(f"Removed reaction {emoji} from message {message_id}")
            
            return {
                "success": True,
                "removed": True
            }
            
        except Exception as e:
            logger.error(f"Failed to remove reaction: {e}")
            return {
                "success": False,
                "removed": False,
                "error": str(e)
            }


async def get_message_reactions(message_id: int) -> List[Dict]:
    """
    Get all reactions for a message, grouped by emoji.
    
    Returns:
        [{"emoji": "❤️", "count": 3, "user_types": ["agent", "customer"]}]
    """
    async with get_db() as db:
        try:
            if DB_TYPE == "postgresql":
                sql = """
                    SELECT emoji, COUNT(*) as count, 
                           array_agg(DISTINCT user_type) as user_types
                    FROM message_reactions
                    WHERE message_id = ?
                    GROUP BY emoji
                    ORDER BY count DESC
                """
            else:
                # SQLite doesn't have array_agg, so we'll do it differently
                sql = """
                    SELECT emoji, COUNT(*) as count, 
                           GROUP_CONCAT(DISTINCT user_type) as user_types
                    FROM message_reactions
                    WHERE message_id = ?
                    GROUP BY emoji
                    ORDER BY count DESC
                """
            
            rows = await fetch_all(db, sql, (message_id,))
            
            reactions = []
            for row in rows:
                emoji = row.get("emoji") or row[0] if isinstance(row, tuple) else row["emoji"]
                count = row.get("count") or row[1] if isinstance(row, tuple) else row["count"]
                user_types_raw = row.get("user_types", []) or row[2] if isinstance(row, tuple) else row.get("user_types", [])
                
                # Parse user_types
                if isinstance(user_types_raw, list):
                    user_types = user_types_raw
                elif isinstance(user_types_raw, str):
                    user_types = user_types_raw.split(",")
                else:
                    user_types = []
                
                reactions.append({
                    "emoji": emoji,
                    "count": count,
                    "user_types": user_types
                })
            
            return reactions
            
        except Exception as e:
            logger.error(f"Failed to get reactions: {e}")
            return []


async def get_reactions_for_messages(message_ids: List[int]) -> Dict[int, List[Dict]]:
    """
    Batch get reactions for multiple messages (efficient for conversation view).
    
    Returns:
        {message_id: [{"emoji": "❤️", "count": 1}]}
    """
    if not message_ids:
        return {}
    
    async with get_db() as db:
        try:
            placeholders = ",".join(["?"] * len(message_ids))
            
            sql = f"""
                SELECT message_id, emoji, COUNT(*) as count
                FROM message_reactions
                WHERE message_id IN ({placeholders})
                GROUP BY message_id, emoji
                ORDER BY message_id, count DESC
            """
            
            rows = await fetch_all(db, sql, tuple(message_ids))
            
            # Group by message_id
            reactions_map = {}
            for row in rows:
                msg_id = row.get("message_id") or row[0]
                emoji = row.get("emoji") or row[1]
                count = row.get("count") or row[2]
                
                if msg_id not in reactions_map:
                    reactions_map[msg_id] = []
                
                reactions_map[msg_id].append({
                    "emoji": emoji,
                    "count": count
                })
            
            return reactions_map
            
        except Exception as e:
            logger.error(f"Failed to batch get reactions: {e}")
            return {}


async def has_user_reacted(
    message_id: int,
    license_id: int,
    emoji: str,
    user_type: str = "agent"
) -> bool:
    """Check if a specific user has reacted with a specific emoji."""
    async with get_db() as db:
        try:
            sql = """
                SELECT 1 FROM message_reactions
                WHERE message_id = ? AND license_id = ? AND user_type = ? AND emoji = ?
                LIMIT 1
            """
            row = await fetch_one(db, sql, (message_id, license_id, user_type, emoji))
            return row is not None
            
        except Exception as e:
            logger.error(f"Failed to check reaction: {e}")
            return False
