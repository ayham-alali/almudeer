import asyncio
import asyncpg

async def cross_license_check():
    conn = await asyncpg.connect('')
    
    contact = '+963968478904'
    print(f"\nCROSS-LICENSE CHECK for contact='{contact}':")
    
    rows = await conn.fetch("""
        SELECT license_key_id, COUNT(*) as msg_count, MIN(created_at) as first, MAX(created_at) as last
        FROM inbox_messages
        WHERE sender_contact = $1 OR sender_id = '639679230'
        GROUP BY license_key_id
    """, contact)
    
    for r in rows:
        print(f"  License {r['license_key_id']} | Count: {r['msg_count']} | First: {r['first']} | Last: {r['last']}")
        
    print("\nRecent messages (last 5) for ANY license:")
    rows = await conn.fetch("""
        SELECT id, license_key_id, sender_name, body, created_at, deleted_at
        FROM inbox_messages
        WHERE sender_contact = $1 OR sender_id = '639679230'
        ORDER BY created_at DESC
        LIMIT 5
    """, contact)
    for r in rows:
        deleted = "[D]" if r['deleted_at'] else "[A]"
        print(f"  ID: {r['id']} | L: {r['license_key_id']} | {r['sender_name']} | {deleted} | {r['created_at']} | {r['body'][:30]}")

    await conn.close()

asyncio.run(cross_license_check())
