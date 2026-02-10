import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from dependencies import get_license_from_header

client = TestClient(app)

@pytest.fixture(autouse=True)
def auth_override():
    """Override license verification for all tests"""
    app.dependency_overrides[get_license_from_header] = lambda: {
        "license_id": 1, 
        "valid": True, 
        "username": "sender_user", 
        "company_name": "Sender Co"
    }
    yield
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_get_call_token():
    """Test Agora token generation endpoint"""
    with patch("services.agora_service.AgoraService.generate_token") as mock_gen:
        mock_gen.return_value = "mocked_token"
        with patch("services.agora_service.AgoraService.get_app_id") as mock_appid:
            mock_appid.return_value = "test_app_id"
            
            response = client.get("/voice/call/token?channel_name=test_channel")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["token"] == "mocked_token"
            assert data["app_id"] == "test_app_id"

@pytest.mark.asyncio
async def test_call_invite_success():
    """Test call invitation signaling"""
    with patch("services.websocket_manager.ConnectionManager.send_to_license") as mock_send:
        mock_send.return_value = None
        
        # Mock DB for recipient lookup
        with patch("db_helper.fetch_one") as mock_fetch:
            mock_fetch.return_value = {"id": 2, "username": "recipient_user"}
            
            response = client.post("/voice/call/invite", json={
                "recipient_username": "recipient_user"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "channel_name" in data
            
            # Verify signaling via WebSocket
            assert mock_send.called
            call_args = mock_send.call_args
            assert call_args[0][0] == 2 # recipient license_id
            ws_msg = call_args[0][1]
            assert ws_msg.event == "call_invite"
            assert ws_msg.data["sender_username"] == "sender_user"

