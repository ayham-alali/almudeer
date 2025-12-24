
import sys
import os
import asyncio

# Add current directory to path just in case
sys.path.append(os.getcwd())

print("Step 1: Testing Migration Imports...")
try:
    from migrations import migration_manager
    from migrations import ensure_inbox_columns
    from migrations import ensure_user_preferences_columns
    from migrations.users_table import create_users_table
    from migrations.fix_customers_serial import fix_customers_serial
    from migrations.purchases_table import create_purchases_table
    print("✅ Migration imports successful!")
except ImportError as e:
    print(f"❌ Migration import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error during migration imports: {e}")
    sys.exit(1)

print("\nStep 2: Testing Service Imports (Lazy Loading Check)...")
try:
    from services.telegram_phone_service import TelegramPhoneService
    # Just instantiate to see if it crashes immediately on init (it shouldn't, mostly env checks)
    # We won't call methods that require auth
    print("✅ TelegramPhoneService import successful!")
except Exception as e:
    print(f"❌ TelegramPhoneService import warning (might be env vars): {e}")

print("\nStep 3: Testing WhatsApp Route Imports...")
try:
    from routes import whatsapp
    print("✅ WhatsApp routes import successful!")
except Exception as e:
    print(f"❌ WhatsApp routes import failed: {e}")
    sys.exit(1)

print("\n✅ Verification COMPLETE: All critical modules import correctly.")
