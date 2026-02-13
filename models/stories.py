"""
Al-Mudeer - Stories Models
DB table creation and CRUD for stories and views
"""

import os
from datetime import datetime
from typing import List, Optional, Dict, Any

from db_helper import get_db, execute_sql, fetch_all, fetch_one, commit_db, DB_TYPE

# Story expiration (default 24 hours, but we keep them in DB and can filter by date)
STORY_EXPIRATION_HOURS = int(os.getenv("STORY_EXPIRATION_HOURS", 24))

async def init_stories_tables():
    """Create stories and story_views tables if they don't exist."""
    
    # helper for cross-DB compatibility
    ID_PK = "SERIAL PRIMARY KEY" if DB_TYPE == "postgresql" else "INTEGER PRIMARY KEY AUTOINCREMENT"
    TIMESTAMP_NOW = "TIMESTAMP DEFAULT NOW()" if DB_TYPE == "postgresql" else "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    TEXT_TYPE = "TEXT"
    INT_TYPE = "INTEGER"

    async with get_db() as db:
        # 1. Stories Table
        await execute_sql(
            db,
            f"""
            CREATE TABLE IF NOT EXISTS stories (
                id {ID_PK},
                license_key_id INTEGER NOT NULL,
                user_id TEXT,
                type TEXT NOT NULL, -- text, image, video, voice, audio, file
                title TEXT,
                content TEXT,
                media_path TEXT,
                thumbnail_path TEXT,
                duration_ms INTEGER DEFAULT 0,
                created_at {TIMESTAMP_NOW},
                deleted_at TIMESTAMP,
                FOREIGN KEY (license_key_id) REFERENCES license_keys(id)
            )
            """
        )
        
        # 2. Story Views Table (tracking who viewed what)
        await execute_sql(
            db,
            f"""
            CREATE TABLE IF NOT EXISTS story_views (
                id {ID_PK},
                story_id INTEGER NOT NULL,
                viewer_contact TEXT NOT NULL, -- phone number or contact unique ID
                viewer_name TEXT,
                viewed_at {TIMESTAMP_NOW},
                UNIQUE(story_id, viewer_contact),
                FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE
            )
            """
        )
        
        # 3. Create Indexes
        if DB_TYPE == "postgresql":
            await execute_sql(db, "CREATE INDEX IF NOT EXISTS idx_stories_license ON stories(license_key_id)")
            await execute_sql(db, "CREATE INDEX IF NOT EXISTS idx_stories_created ON stories(created_at)")
            await execute_sql(db, "CREATE INDEX IF NOT EXISTS idx_story_views_contact ON story_views(viewer_contact)")
        else:
            await execute_sql(db, "CREATE INDEX IF NOT EXISTS idx_stories_license ON stories(license_key_id)")
            await execute_sql(db, "CREATE INDEX IF NOT EXISTS idx_stories_created ON stories(created_at)")
        
        await commit_db(db)

async def add_story(
    license_id: int,
    story_type: str,
    user_id: Optional[str] = None,
    title: Optional[str] = None,
    content: Optional[str] = None,
    media_path: Optional[str] = None,
    thumbnail_path: Optional[str] = None,
    duration_ms: int = 0
) -> dict:
    """Publish a new story and return the created object atomically."""
    now = datetime.utcnow()
    ts_value = now if DB_TYPE == "postgresql" else now.isoformat()
    
    async with get_db() as db:
        if DB_TYPE == "postgresql":
            # Atomic return in PostgreSQL
            query = """
                INSERT INTO stories 
                (license_key_id, user_id, type, title, content, media_path, thumbnail_path, duration_ms, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING *
            """
            row = await fetch_one(db, query, [license_id, user_id, story_type, title, content, media_path, thumbnail_path, duration_ms, ts_value])
            await commit_db(db)
            return dict(row) if row else {}
        else:
            # SQLite insertion
            await execute_sql(
                db,
                """
                INSERT INTO stories 
                (license_key_id, user_id, type, title, content, media_path, thumbnail_path, duration_ms, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [license_id, user_id, story_type, title, content, media_path, thumbnail_path, duration_ms, ts_value]
            )
            # Use last_insert_rowid() inside the same connection context
            row = await fetch_one(db, "SELECT * FROM stories WHERE id = last_insert_rowid()")
            await commit_db(db)
            return dict(row) if row else {}

async def get_active_stories(license_id: int, viewer_contact: Optional[str] = None) -> List[dict]:
    """
    Get active stories (last 24h) for a license.
    If viewer_contact is provided, includes 'is_viewed' join status.
    """
    if DB_TYPE == "postgresql":
        time_filter = "created_at > NOW() - INTERVAL '24 hours'"
    else:
        time_filter = "created_at > datetime('now', '-24 hours')"

    query = f"""
        SELECT s.*, 
               (CASE WHEN sv.id IS NOT NULL THEN 1 ELSE 0 END) as is_viewed
        FROM stories s
        LEFT JOIN story_views sv ON s.id = sv.story_id AND sv.viewer_contact = ?
        WHERE s.license_key_id = ? AND s.deleted_at IS NULL AND {time_filter}
        ORDER BY s.created_at DESC
    """
    
    async with get_db() as db:
        rows = await fetch_all(db, query, [viewer_contact, license_id])
        return [dict(row) for row in rows]

async def mark_story_viewed(story_id: int, viewer_contact: str, viewer_name: Optional[str] = None) -> bool:
    """Record that a contact viewed a story."""
    now = datetime.utcnow()
    ts_value = now if DB_TYPE == "postgresql" else now.isoformat()
    
    # Use INSERT OR IGNORE / ON CONFLICT depending on DB
    if DB_TYPE == "postgresql":
        query = """
            INSERT INTO story_views (story_id, viewer_contact, viewer_name, viewed_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (story_id, viewer_contact) DO NOTHING
        """
        # Note: execute_sql handles params differently for PG in some wrappers, but we follow the helper pattern
    else:
        query = """
            INSERT OR IGNORE INTO story_views (story_id, viewer_contact, viewer_name, viewed_at)
            VALUES (?, ?, ?, ?)
        """

    async with get_db() as db:
        try:
            await execute_sql(db, query, [story_id, viewer_contact, viewer_name, ts_value])
            await commit_db(db)
            return True
        except Exception:
            return False

async def get_story_viewers(story_id: int, license_id: int) -> List[dict]:
    """List details of who viewed a specific story."""
    query = """
        SELECT sv.viewer_contact, sv.viewer_name, sv.viewed_at, s.license_key_id
        FROM story_views sv
        JOIN stories s ON sv.story_id = s.id
        WHERE sv.story_id = ? AND s.license_key_id = ?
        ORDER BY sv.viewed_at DESC
    """
    async with get_db() as db:
        rows = await fetch_all(db, query, [story_id, license_id])
        return [dict(row) for row in rows]

async def delete_story(story_id: int, license_id: int, user_id: Optional[str] = None) -> bool:
    """Soft delete a story. If user_id is provided, only deletes if owner matches."""
    now = datetime.utcnow()
    ts_value = now if DB_TYPE == "postgresql" else now.isoformat()
    
    query = "UPDATE stories SET deleted_at = ? WHERE id = ? AND license_key_id = ?"
    params = [ts_value, story_id, license_id]
    
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)
    
    async with get_db() as db:
        await execute_sql(db, query, params)
        await commit_db(db)
        return True

async def cleanup_expired_stories():
    """Permanent deletion of stories older than expiry hours or soft-deleted items."""
    if DB_TYPE == "postgresql":
        query = f"DELETE FROM stories WHERE created_at < NOW() - INTERVAL '{STORY_EXPIRATION_HOURS} hours' OR deleted_at IS NOT NULL"
    else:
        query = f"DELETE FROM stories WHERE created_at < datetime('now', '-{STORY_EXPIRATION_HOURS} hours') OR deleted_at IS NOT NULL"
    
    async with get_db() as db:
        await execute_sql(db, query)
        await commit_db(db)
