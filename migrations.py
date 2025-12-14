"""
Database migration utilities
Prepares for SQLite → PostgreSQL migration
"""

import os
import aiosqlite
from typing import List, Dict


class MigrationManager:
    """Manages database schema migrations"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv("DATABASE_PATH", "almudeer.db")
        self.migrations: List[Dict] = []
    
    def register_migration(self, version: int, name: str, up_sql: str, down_sql: str = None):
        """Register a migration"""
        self.migrations.append({
            "version": version,
            "name": name,
            "up": up_sql,
            "down": down_sql
        })
        self.migrations.sort(key=lambda x: x["version"])
    
    async def create_migrations_table(self):
        """Create migrations tracking table"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
    
    async def get_applied_migrations(self) -> List[int]:
        """Get list of applied migration versions"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT version FROM schema_migrations ORDER BY version")
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
    
    async def apply_migration(self, migration: Dict):
        """Apply a single migration"""
        async with aiosqlite.connect(self.db_path) as db:
            # Check if already applied
            cursor = await db.execute(
                "SELECT version FROM schema_migrations WHERE version = ?",
                (migration["version"],)
            )
            if await cursor.fetchone():
                return False
            
            # Special handling for version 2 (add license_key_encrypted column)
            if migration["version"] == 2:
                # Check if column already exists
                cursor = await db.execute("PRAGMA table_info(license_keys)")
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                if "license_key_encrypted" not in column_names:
                    await db.execute("ALTER TABLE license_keys ADD COLUMN license_key_encrypted TEXT")
                    await db.commit()
            else:
                # Apply migration normally
                await db.executescript(migration["up"])
            
            # Record migration
            await db.execute(
                "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
                (migration["version"], migration["name"])
            )
            await db.commit()
            return True
    
    async def migrate(self):
        """Apply all pending migrations"""
        await self.create_migrations_table()
        applied = await self.get_applied_migrations()
        
        applied_count = 0
        for migration in self.migrations:
            if migration["version"] not in applied:
                if await self.apply_migration(migration):
                    applied_count += 1
                    print(f"✅ Applied migration {migration['version']}: {migration['name']}")
        
        if applied_count == 0:
            print("✅ No pending migrations")
        
        return applied_count


# Initialize migration manager
migration_manager = MigrationManager()

# Register initial migrations
migration_manager.register_migration(
    version=1,
    name="add_database_indexes",
    up_sql="""
        CREATE INDEX IF NOT EXISTS idx_license_key_hash ON license_keys(key_hash);
        CREATE INDEX IF NOT EXISTS idx_crm_license_id ON crm_entries(license_key_id);
        CREATE INDEX IF NOT EXISTS idx_crm_created_at ON crm_entries(created_at);
        CREATE INDEX IF NOT EXISTS idx_usage_logs_license_id ON usage_logs(license_key_id);
        CREATE INDEX IF NOT EXISTS idx_license_expires_at ON license_keys(expires_at);
    """
)

# Migration to add license_key_encrypted column
migration_manager.register_migration(
    version=2,
    name="add_license_key_encrypted_column",
    up_sql="""
        -- Add license_key_encrypted column if it doesn't exist
        -- SQLite doesn't support IF NOT EXISTS for ALTER TABLE ADD COLUMN
        -- So we'll use a try-catch approach in the migration manager
        -- For PostgreSQL, we'll handle it separately
    """
)

