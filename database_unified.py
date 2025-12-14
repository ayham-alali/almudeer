"""
Al-Mudeer - Unified Database Interface
Supports both SQLite (development) and PostgreSQL (production)
Automatically switches based on DB_TYPE environment variable
"""

import os
from typing import Optional, Any
from contextlib import asynccontextmanager

# Database configuration
DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
DATABASE_PATH = os.getenv("DATABASE_PATH", "almudeer.db")
DATABASE_URL = os.getenv("DATABASE_URL")

# Database connection pool (for PostgreSQL)
_db_pool = None

# Import appropriate database driver
if DB_TYPE == "postgresql":
    try:
        import asyncpg
        POSTGRES_AVAILABLE = True
        
        async def get_db_pool():
            """Get or create PostgreSQL connection pool"""
            global _db_pool
            if _db_pool is None and DATABASE_URL:
                _db_pool = await asyncpg.create_pool(
                    DATABASE_URL,
                    min_size=1,
                    max_size=10,
                    command_timeout=60
                )
            return _db_pool
        
        async def close_db_pool():
            """Close PostgreSQL connection pool"""
            global _db_pool
            if _db_pool:
                await _db_pool.close()
                _db_pool = None
        
    except ImportError:
        raise ImportError(
            "PostgreSQL selected but asyncpg not installed. "
            "Install with: pip install asyncpg"
        )
else:
    import aiosqlite
    POSTGRES_AVAILABLE = False


@asynccontextmanager
async def get_db_connection():
    """
    Unified database connection context manager.
    Works with both SQLite and PostgreSQL.
    """
    if DB_TYPE == "postgresql" and POSTGRES_AVAILABLE:
        pool = await get_db_pool()
        if not pool:
            raise ConnectionError("PostgreSQL connection pool not available. Check DATABASE_URL.")
        async with pool.acquire() as conn:
            yield conn
    else:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            yield db


async def execute_query(query: str, params: tuple = None):
    """
    Execute a query and return results.
    Handles differences between SQLite and PostgreSQL.
    """
    async with get_db_connection() as db:
        if DB_TYPE == "postgresql":
            if params:
                rows = await db.fetch(query, *params)
                return [dict(row) for row in rows]
            else:
                rows = await db.fetch(query)
                return [dict(row) for row in rows]
        else:
            # SQLite
            if params:
                cursor = await db.execute(query, params)
            else:
                cursor = await db.execute(query)
            await db.commit()
            rows = await cursor.fetchall()
            if hasattr(cursor, 'row_factory') and cursor.row_factory:
                return [dict(row) for row in rows]
            else:
                # Convert to dict format
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                return [dict(zip(columns, row)) for row in rows]


async def execute_update(query: str, params: tuple = None) -> int:
    """
    Execute an update/insert query and return affected rows or lastrowid.
    """
    async with get_db_connection() as db:
        if DB_TYPE == "postgresql":
            if params:
                result = await db.execute(query, *params)
            else:
                result = await db.execute(query)
            return int(result.split()[-1]) if result else 0
        else:
            # SQLite
            if params:
                cursor = await db.execute(query, params)
            else:
                cursor = await db.execute(query)
            await db.commit()
            return cursor.lastrowid or cursor.rowcount


def adapt_sql_for_db(query: str) -> str:
    """
    Adapt SQL query syntax for the current database type.
    Converts SQLite syntax to PostgreSQL if needed.
    """
    if DB_TYPE == "postgresql":
        # Convert SQLite syntax to PostgreSQL
        query = query.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
        query = query.replace("AUTOINCREMENT", "")
        query = query.replace("BOOLEAN", "BOOLEAN")
        query = query.replace("TEXT", "VARCHAR")
        query = query.replace("TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "TIMESTAMP DEFAULT NOW()")
        query = query.replace("DATE", "DATE")
        # PostgreSQL uses $1, $2 for parameters instead of ?
        # This is handled by asyncpg automatically
    return query
