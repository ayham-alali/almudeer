"""
Al-Mudeer - Purchases Table Migration
Creates the purchases table for tracking customer transactions
"""

from logging_config import get_logger

logger = get_logger(__name__)


async def create_purchases_table():
    """
    Create the purchases table for tracking customer transactions.
    Also adds analytics columns to the customers table.
    """
    from db_helper import get_db, execute_sql, commit_db, DB_TYPE
    
    logger.info("Creating purchases table...")
    
    async with get_db() as db:
        # Create purchases table
        if DB_TYPE == "postgresql":
            await execute_sql(db, """
                CREATE TABLE IF NOT EXISTS purchases (
                    id SERIAL PRIMARY KEY,
                    license_key_id INTEGER NOT NULL,
                    customer_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    currency TEXT DEFAULT 'SYP',
                    status TEXT DEFAULT 'completed',
                    notes TEXT,
                    purchase_date TIMESTAMP DEFAULT NOW(),
                    created_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (license_key_id) REFERENCES license_keys(id),
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
                )
            """)
        else:
            await execute_sql(db, """
                CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_key_id INTEGER NOT NULL,
                    customer_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'SYP',
                    status TEXT DEFAULT 'completed',
                    notes TEXT,
                    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (license_key_id) REFERENCES license_keys(id),
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
                )
            """)
        
        # Create index for faster lookups
        await execute_sql(db, """
            CREATE INDEX IF NOT EXISTS idx_purchases_customer
            ON purchases(customer_id)
        """)
        
        await execute_sql(db, """
            CREATE INDEX IF NOT EXISTS idx_purchases_license
            ON purchases(license_key_id)
        """)
        
        # Add analytics columns to customers table if they don't exist
        try:
            await execute_sql(db, "ALTER TABLE customers ADD COLUMN sentiment_avg REAL DEFAULT 0")
        except Exception:
            pass  # Column already exists
        
        try:
            await execute_sql(db, "ALTER TABLE customers ADD COLUMN lifetime_value REAL DEFAULT 0")
        except Exception:
            pass  # Column already exists
        
        try:
            await execute_sql(db, "ALTER TABLE customers ADD COLUMN avg_response_time_seconds INTEGER")
        except Exception:
            pass  # Column already exists
        
        await commit_db(db)
        logger.info("✅ Purchases table and analytics columns created!")
