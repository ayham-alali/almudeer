import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_helper import get_db
from models.inbox import get_full_chat_history

async def test_full_history():
    print("=" * 80)
    print("SIMULATING get_full_chat_history(license_id=5, contact='+963968478904')")
    print("=" * 80)
    
    messages = await get_full_chat_history(license_id=5, sender_contact='+963968478904', limit=100)
    
    print(f"\nReturned {len(messages)} messages total.")
    
    # Print first 5 and last 5
    print("\nFIRST 5 (OLDEST):")
    for m in messages[:5]:
        print(f"  ID: {m['id']} | {m['direction']} | {m['timestamp']} | Status: {m['status']}")
        print(f"    Body: {(m['body'] or '')[:50]}")
        
    print("\nLAST 5 (NEWEST):")
    for m in messages[-5:]:
        print(f"  ID: {m['id']} | {m['direction']} | {m['timestamp']} | Status: {m['status']}")
        print(f"    Body: {(m['body'] or '')[:50]}")
    
    # Check for certain IDs
    target_ids = [1305, 1371, 1372]
    all_ids = [m['id'] for m in messages]
    print("\nPresence Check:")
    for tid in target_ids:
        present = "YES" if tid in all_ids else "NO"
        print(f"  ID {tid} present: {present}")
        
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(test_full_history())
