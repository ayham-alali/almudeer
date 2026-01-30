import asyncio
import httpx
import re
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import json

# Import the service (mocking dependencies if needed)
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.gmail_api_service import GmailAPIService

async def test_gmail_rate_limit_handling():
    print("Starting Gmail Rate Limit Verification Test...")
    
    # Initialize service
    service = GmailAPIService(access_token="test-token")
    
    # 1. Test Case: Success on first try
    with patch("httpx.AsyncClient.request") as mock_request:
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.content = b'{"status": "ok"}'
        mock_response.json.return_value = {"status": "ok"}
        mock_request.return_value = mock_response
        
        result = await service._request("GET", "test-endpoint")
        assert result == {"status": "ok"}
        assert mock_request.call_count == 1
        print("✓ Success on first try passed.")

    # 2. Test Case: Rate limit with "Retry after" timestamp
    with patch("httpx.AsyncClient.request") as mock_request:
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            # 1st call: 429 with retry timestamp
            # Use a time 5 seconds in the future
            future_ts = "2026-01-30T20:00:05.123Z" 
            # Note: The code uses datetime.now(timezone.utc), so we should mock that too for consistency
            
            error_msg = f"User-rate limit exceeded.  Retry after {future_ts}"
            
            resp429 = MagicMock(spec=httpx.Response)
            resp429.status_code = 429
            resp429.content = json.dumps({"error": {"message": error_msg}}).encode()
            resp429.json.return_value = {"error": {"message": error_msg}}
            resp429.text = error_msg
            
            resp200 = MagicMock(spec=httpx.Response)
            resp200.status_code = 200
            resp200.content = b'{"status": "recovered"}'
            resp200.json.return_value = {"status": "recovered"}
            
            # Use fixed time for comparison
            mock_now = datetime(2026, 1, 30, 20, 0, 0, tzinfo=timezone.utc)
            
            mock_request.side_effect = [resp429, resp200]
            
            with patch("services.gmail_api_service.datetime") as mock_dt_module:
                mock_dt_module.now.return_value = mock_now
                mock_dt_module.fromisoformat.side_effect = datetime.fromisoformat
                
                result = await service._request("GET", "test-endpoint")
                
            assert result == {"status": "recovered"}
            assert mock_request.call_count == 2
            
            # Verify sleep was called with approx 5.123 seconds
            # In code: wait_time = (retry_at - now).total_seconds()
            # 20:00:05.123 - 20:00:00 = 5.123
            sleep_call_args = mock_sleep.call_args[0][0]
            assert 5.0 < sleep_call_args < 5.2
            print(f"✓ Rate limit with timestamp parsing passed (Sleep: {sleep_call_args:.3f}s)")

    # 3. Test Case: Rate limit with exponential backoff (no timestamp)
    with patch("httpx.AsyncClient.request") as mock_request:
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            resp429 = MagicMock(spec=httpx.Response)
            resp429.status_code = 429
            resp429.content = b'{"error": {"message": "Rate limit exceeded"}}'
            resp429.json.return_value = {"error": {"message": "Rate limit exceeded"}}
            resp429.text = "Rate limit exceeded"
            
            resp200 = MagicMock(spec=httpx.Response)
            resp200.status_code = 200
            resp200.content = b'{"status": "backoff_works"}'
            resp200.json.return_value = {"status": "backoff_works"}
            
            mock_request.side_effect = [resp429, resp200]
            
            result = await service._request("GET", "test-endpoint")
            
            assert result == {"status": "backoff_works"}
            assert mock_request.call_count == 2
            # First retry after 429 (no ts) uses 5 * (2 ** 0) = 5s
            assert mock_sleep.call_args[0][0] == 5
            print("✓ Exponential backoff (no timestamp) passed.")

    print("\nAll Gmail Rate Limit Verification Tests Passed Successfully!")

if __name__ == "__main__":
    asyncio.run(test_gmail_rate_limit_handling())
