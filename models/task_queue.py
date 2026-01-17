"""
Al-Mudeer - Persistent Task Queue
Handles background jobs (AI analysis, etc.) robustly with database persistence.
"""

import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from db_helper import get_db, execute_sql, fetch_one, fetch_all, commit_db, DB_TYPE

async def enqueue_task(
    task_type: str,
    payload: Dict[str, Any],
    priority: int = 0
) -> int:
    """
    Queue a background task.
    priority: Higher runs first (default 0)
    """
    async with get_db() as db:
        now = datetime.utcnow()
        ts_value = now if DB_TYPE == "postgresql" else now.isoformat()
        payload_json = json.dumps(payload)
        
        if DB_TYPE == "postgresql":
            sql = """
                INSERT INTO task_queue (task_type, payload, priority, status, created_at, updated_at)
                VALUES ($1, $2, $3, 'pending', $4, $4)
                RETURNING id
            """
            row = await fetch_one(db, sql, [task_type, payload_json, priority, ts_value])
            await commit_db(db)
            return row["id"]
        else:
            # SQLite
            sql = """
                INSERT INTO task_queue (task_type, payload, priority, status, created_at, updated_at)
                VALUES (?, ?, ?, 'pending', ?, ?)
            """
            await execute_sql(db, sql, [task_type, payload_json, priority, ts_value, ts_value])
            
            # Get ID
            row = await fetch_one(db, "SELECT last_insert_rowid() as id")
            task_id = row["id"]
            await commit_db(db)
            return task_id

async def fetch_next_task(worker_id: str = "worker-1") -> Optional[Dict]:
    """
    Fetch and lock the next pending task.
    Returns task dict or None.
    """
    now = datetime.utcnow()
    ts_value = now if DB_TYPE == "postgresql" else now.isoformat()
    
    async with get_db() as db:
        # Atomic fetch-and-update (skip locked)
        if DB_TYPE == "postgresql":
            # PostgreSQL FOR UPDATE SKIP LOCKED
            sql = """
                UPDATE task_queue
                SET status = 'processing', worker_id = $1, processed_at = $2, updated_at = $2
                WHERE id = (
                    SELECT id FROM task_queue
                    WHERE status = 'pending'
                    ORDER BY priority DESC, created_at ASC
                    LIMIT 1
                    FOR UPDATE SKIP LOCKED
                )
                RETURNING id, task_type, payload
            """
            row = await fetch_one(db, sql, [worker_id, ts_value])
            if row:
                await commit_db(db)
                return {
                    "id": row["id"],
                    "task_type": row["task_type"],
                    "payload": json.loads(row["payload"])
                }
            return None
            
        else:
            # SQLite (Simulated atomic lock)
            # 1. Find candidate
            find_sql = """
                SELECT id, task_type, payload FROM task_queue
                WHERE status = 'pending'
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
            """
            row = await fetch_one(db, find_sql)
            if not row:
                return None
                
            task_id = row["id"]
            
            # 2. Try to lock
            update_sql = """
                UPDATE task_queue
                SET status = 'processing', worker_id = ?, processed_at = ?, updated_at = ?
                WHERE id = ? AND status = 'pending'
            """
            try:
                await execute_sql(db, update_sql, [worker_id, ts_value, ts_value, task_id])
                await commit_db(db)
                # Success
                return {
                    "id": task_id,
                    "task_type": row["task_type"],
                    "payload": json.loads(row["payload"])
                }
            except:
                 # Race condition failed
                return None

async def complete_task(task_id: int):
    """Mark task as completed."""
    now = datetime.utcnow()
    ts_value = now if DB_TYPE == "postgresql" else now.isoformat()
    
    async with get_db() as db:
        await execute_sql(
            db, 
            "UPDATE task_queue SET status = 'completed', completed_at = ?, updated_at = ? WHERE id = ?",
            [ts_value, ts_value, task_id]
        )
        await commit_db(db)

async def fail_task(task_id: int, error_msg: str):
    """Mark task as failed."""
    now = datetime.utcnow()
    ts_value = now if DB_TYPE == "postgresql" else now.isoformat()
    
    async with get_db() as db:
        await execute_sql(
            db, 
            "UPDATE task_queue SET status = 'failed', error_message = ?, updated_at = ? WHERE id = ?",
            [str(error_msg), ts_value, task_id]
        )
        await commit_db(db)

async def retry_stuck_tasks(timeout_minutes: int = 15):
    """Reset tasks stuck in 'processing' state for too long."""
    # Logic to be implemented if needed for robustness
    pass
