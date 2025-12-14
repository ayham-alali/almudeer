"""
Run database migrations
Usage: python run_migrations.py
"""

import asyncio
from migrations import migration_manager


async def main():
    """Run all pending migrations"""
    print("🔄 Running database migrations...")
    count = await migration_manager.migrate()
    print(f"✅ Migration complete. Applied {count} migration(s).")


if __name__ == "__main__":
    asyncio.run(main())

