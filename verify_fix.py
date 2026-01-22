import asyncio
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.inbox import get_conversation_messages_cursor

async def verify_json_parsing():
    print("=" * 80)
    print("VERIFYING JSON PARSING IN get_conversation_messages_cursor")
    print("=" * 80)
    
    # We'll use License 5 and Ayham's contact
    result = await get_conversation_messages_cursor(license_id=5, sender_contact='+963968478904', limit=5)
    
    messages = result['messages']
    print(f"\nFetched {len(messages)} messages.")
    
    for m in messages:
        attachments = m.get('attachments')
        print(f"  ID: {m['id']} | Attachments Type: {type(attachments)}")
        if attachments:
            print(f"    Raw Attachments: {attachments}")
            
    print("\nCheck passing:")
    for m in messages:
        if m.get('attachments') and not isinstance(m.get('attachments'), list):
            print(f"  ❌ FAILED: Message {m['id']} has non-list attachments: {type(m['attachments'])}")
        else:
            print(f"  ✅ PASSED: Message {m['id']} attachments are correctly handled.")
            
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(verify_json_parsing())
