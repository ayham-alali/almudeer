import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_helper import get_db
from models.inbox import get_conversation_messages

async def test_query():
    print("=" * 80)
    print("TESTING get_conversation_messages(license_id=5, contact='+963968478904')")
    print("=" * 80)
    
    messages = await get_conversation_messages(license_id=5, sender_contact='+963968478904', limit=20)
    
    print(f"\nFound {len(messages)} messages:")
    for m in messages:
        print(f"  ID: {m['id']} | At: {m['created_at']} | Status: {m['status']}")
        print(f"    Body: {(m['body'] or '')[:100]}")
    
    # Check if 1371 is in the list
    ids = [m['id'] for m in messages]
    if 1371 in ids:
        print("\n✅ Message 1371 IS in the result set!")
    else:
        print("\n❌ Message 1371 IS NOT in the result set!")
        
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(test_query())
