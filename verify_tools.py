
import asyncio
import sys
import os
from unittest.mock import patch, MagicMock

# Add the backend to path
sys.path.append(r"c:\roya\products\almudeer\backend")

# Define mock tool response logic
class MockGeminiResponse:
    def __init__(self, tool_calls=None, content=None):
        self.tool_calls = tool_calls
        self.content = content
        self.tool_calls_raw = tool_calls # for debugging

async def setup_test_db():
    """Setup test data in SQLite for verification"""
    import aiosqlite
    DB_PATH = "almudeer.db" # Should match database.py default or env
    
    # Ensure tables exist (database.py init_database)
    from database import init_database
    await init_database()
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Seed Customer
        await db.execute("DELETE FROM customers WHERE contact = '0555999888'")
        await db.execute("""
            INSERT INTO customers (name, contact, type, total_spend, notes)
            VALUES ('Real DB Customer', '0555999888', 'VIP', 999.0, 'Seeded for test')
        """)
        
        # Seed Order
        await db.execute("DELETE FROM orders WHERE order_ref = 'ORD-REAL-123'")
        await db.execute("""
            INSERT INTO orders (order_ref, status, total_amount, items, created_at)
            VALUES ('ORD-REAL-123', 'Delivered', 150.0, 'Test Item X', CURRENT_TIMESTAMP)
        """)
        await db.commit()
    print("✅ Test DB seeded.")

async def test_tool_use():
    print("\n--- Testing Active Tool Use (Real DB) ---")
    
    # Scenario: User asks for order status -> Agent calls tool -> Agent gets result -> Agent answers
    
    # Use AsyncMock for proper async behavior of the LLM part
    from unittest.mock import AsyncMock

    # Patch KB to avoid ChromaDB startup lag/hangs
    with patch("agent.call_llm", new_callable=AsyncMock) as mock_call_llm, \
         patch("services.knowledge_base.get_knowledge_base") as mock_kb:
        
        # Configure KB mock
        mock_kb_instance = MagicMock()
        mock_kb_instance.search.return_value = []
        mock_kb.return_value = mock_kb_instance

        import agent
        from tools import definitions
        
        # Setup DB
        await setup_test_db()
        
        # Turn 1: LLM decides to check order
        mock_response_1 = MockGeminiResponse(
            tool_calls=[{"name": "check_order_status", "args": {"order_id": "ORD-REAL-123"}}]
        )
        
        # Turn 2: Final answer
        mock_response_2 = '{"intent": "info", "draft_response": "Order is delivered."}'
        
        mock_call_llm.side_effect = [mock_response_1, mock_response_2]
        
        # Verify Status Callback
        status_updates = []
        async def mock_status_callback(msg):
            print(f"[Callback] Status received: {msg}")
            status_updates.append(msg)

        # Run agent with callback
        print("User: Check order ORD-REAL-123")
        await agent.process_message("Check order ORD-REAL-123", status_callback=mock_status_callback)
        
        if any("Check Order Status" in m for m in status_updates):
             print("✅ Status callback fired correctly.")
        else:
             print("❌ Status callback NOT fired.")

async def test_lead_notifications():
    print("\n--- Testing Lead Notifications ---")
    from unittest.mock import AsyncMock
    with patch("agent.call_llm", new_callable=AsyncMock) as mock_call_llm, \
         patch("services.knowledge_base.get_knowledge_base") as mock_kb, \
         patch("services.notification_service.send_tool_action_alert", new_callable=AsyncMock) as mock_alert:
         
        mock_kb.return_value.search.return_value = []
        import agent
        
        # Turn 1: Create Lead
        mock_response_1 = MockGeminiResponse(
            tool_calls=[{"name": "create_lead", "args": {"name": "TestUser", "contact": "0000", "interest": "X"}}]
        )
        
        mock_response_2 = '{"intent": "info", "draft_response": "Done."}'
        mock_call_llm.side_effect = [mock_response_1, mock_response_2]
        
        # Pass dummy preference with license_id to allow alert triggering
        prefs = {"license_key_id": 999}
        
        await agent.process_message("Create lead", preferences=prefs)
        
        # Check if alert was called (it's fire-and-forget in definitions.py, so we sleep briefly)
        await asyncio.sleep(0.1)
        if mock_alert.called:
            print("✅ Safety Alert triggered.")
        else:
            print("❌ Safety Alert NOT triggered (check license_id passing).")

if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(test_tool_use())
        asyncio.run(test_lead_notifications())
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
