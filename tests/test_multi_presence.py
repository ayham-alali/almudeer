import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from services.websocket_manager import ConnectionManager
from contextlib import asynccontextmanager

@pytest.mark.asyncio
async def test_multi_presence_heartbeat():
    """Test that ping with companions refreshes multiple accounts"""
    manager = ConnectionManager()
    manager._pubsub._initialized = True # Mock initialized
    
    primary_license_id = 101
    companion_key = "MUDEER-COMP-ANION-KEY"
    companion_id = 202
    
    # Mock database connection and operations
    mock_conn = MagicMock()
    
    @asynccontextmanager
    async def mock_get_db_ctx():
        yield mock_conn

    # Mock fetch_one to return the companion ID when the key is lookup
    async def mock_fetch_one(db, sql, params):
        if "FROM license_keys" in sql and "key_hash" in sql:
            return {"id": companion_id}
        return None

    # We mock db_helper because websocket_manager imports from it
    with patch('db_helper.get_db', side_effect=mock_get_db_ctx), \
         patch('db_helper.fetch_one', side_effect=mock_fetch_one), \
         patch('db_helper.execute_sql', new_callable=AsyncMock) as mock_execute, \
         patch('db_helper.commit_db', new_callable=AsyncMock) as mock_commit:
        
        # 1. Refresh primary
        await manager.refresh_last_seen(primary_license_id)
        
        # 2. Refresh companion
        await manager.refresh_last_seen_by_key(companion_key)
        
        # Verification
        # Check updates
        update_calls = [args[1] for args, kwargs in mock_execute.call_args_list if "UPDATE license_keys" in args[1]]
        update_params = [args[2] for args, kwargs in mock_execute.call_args_list if "UPDATE license_keys" in args[1]]
        
        print(f"Update calls found: {len(update_calls)}")
        
        assert len(update_calls) == 2
        assert update_params[0][1] == primary_license_id
        assert update_params[1][1] == companion_id
        
        print("SUCCESS: Multi-presence heartbeat backend logic verified.")
        return True

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_multi_presence_heartbeat())
