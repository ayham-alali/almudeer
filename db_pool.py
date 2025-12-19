"""
Database connection pool manager
Supports both SQLite (current) and PostgreSQL (future migration)
"""

import os
from typing import Optional, Any
import aiosqlite

# Try to import asyncpg for PostgreSQL (optional)
try:
    import asyncpg
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    asyncpg = None


class DatabasePool:
    """Unified database connection pool manager"""
    
    def __init__(self):
        self.db_type = os.getenv("DB_TYPE", "sqlite").lower()
        self.pool: Optional[Any] = None
        self.sqlite_path = os.getenv("DATABASE_PATH", "almudeer.db")
        
        # PostgreSQL connection string
        self.postgres_url = os.getenv("DATABASE_URL")
    
    async def initialize(self):
        """Initialize the appropriate database connection pool"""
        if self.db_type == "postgresql" and POSTGRES_AVAILABLE and self.postgres_url:
            await self._init_postgres()
        else:
            # Use SQLite (current default)
            self._init_sqlite()
    
    def _init_sqlite(self):
        """Initialize SQLite (no pooling, but prepared for future)"""
        # SQLite doesn't need explicit pooling, but we prepare the interface
        self.pool = None
        self.db_type = "sqlite"
    
    async def _init_postgres(self):
        """Initialize PostgreSQL connection pool"""
        if not POSTGRES_AVAILABLE:
            raise ImportError("asyncpg is required for PostgreSQL. Install with: pip install asyncpg")
        
        if not self.postgres_url:
            raise ValueError("DATABASE_URL environment variable required for PostgreSQL")
        
        # Create connection pool with optimized settings for scalability
        query_timeout = int(os.getenv("DB_QUERY_TIMEOUT", "30"))  # Configurable timeout
        self.pool = await asyncpg.create_pool(
            self.postgres_url,
            min_size=5,  # Keep 5 connections warm (was 2)
            max_size=20,  # Allow up to 20 concurrent (was 10)
            command_timeout=query_timeout,  # Configurable query timeout
            statement_cache_size=100,  # Cache prepared statements
        )
        self.db_type = "postgresql"
    
    async def acquire(self):
        """Acquire a database connection"""
        if self.db_type == "postgresql" and self.pool:
            return await self.pool.acquire()
        elif self.db_type == "sqlite":
            # Return SQLite connection (no pooling)
            return await aiosqlite.connect(self.sqlite_path)
        else:
            raise RuntimeError("Database not initialized")
    
    async def release(self, conn):
        """Release a database connection"""
        if self.db_type == "postgresql" and self.pool:
            await self.pool.release(conn)
        elif self.db_type == "sqlite":
            await conn.close()
    
    async def execute(self, query: str, params: tuple = None):
        """Execute a query (convenience method)"""
        conn = await self.acquire()
        try:
            if self.db_type == "postgresql":
                if params:
                    result = await conn.execute(query, *params)
                else:
                    result = await conn.execute(query)
            else:
                cursor = await conn.execute(query, params or ())
                await conn.commit()
                result = cursor
            return result
        finally:
            await self.release(conn)
    
    async def fetch(self, query: str, params: tuple = None):
        """Fetch rows from database"""
        conn = await self.acquire()
        try:
            if self.db_type == "postgresql":
                if params:
                    rows = await conn.fetch(query, *params)
                else:
                    rows = await conn.fetch(query)
                return [dict(row) for row in rows]
            else:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.execute(query, params or ())
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        finally:
            await self.release(conn)
    
    async def fetchone(self, query: str, params: tuple = None):
        """Fetch a single row"""
        conn = await self.acquire()
        try:
            if self.db_type == "postgresql":
                if params:
                    row = await conn.fetchrow(query, *params)
                else:
                    row = await conn.fetchrow(query)
                return dict(row) if row else None
            else:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.execute(query, params or ())
                row = await cursor.fetchone()
                return dict(row) if row else None
        finally:
            await self.release(conn)
    
    async def close(self):
        """Close the connection pool"""
        if self.db_type == "postgresql" and self.pool:
            await self.pool.close()


# Global database pool instance
db_pool = DatabasePool()

