"""
Al-Mudeer Backend Tests
Basic tests for core functionality
"""

import pytest
from httpx import AsyncClient, ASGITransport


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_health_check():
    """Test health endpoint returns 200"""
    from main import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.anyio
async def test_health_live():
    """Test liveness probe"""
    from main import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"


@pytest.mark.anyio
async def test_analyze_requires_license():
    """Test that analyze endpoint requires license key"""
    from main import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/analyze",
            json={"message": "Hello world"}
        )
        # Should fail without license key
        assert response.status_code in [401, 403, 422]


@pytest.mark.anyio
async def test_auth_login_invalid():
    """Test login with invalid credentials"""
    from main import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={"license_key": "invalid-key-12345"}
        )
        assert response.status_code == 401


# ============ Unit Tests ============

def test_sanitize_message():
    """Test message sanitization"""
    from security import sanitize_message
    
    # Normal message should pass through
    result = sanitize_message("Hello world")
    assert result == "Hello world"
    
    # XSS should be escaped
    result = sanitize_message("<script>alert('xss')</script>")
    assert "<script>" not in result


def test_password_hashing():
    """Test password hashing and verification"""
    from services.jwt_auth import hash_password, verify_password
    
    password = "test_password_123"
    hashed = hash_password(password)
    
    # Should not be plain text
    assert hashed != password
    
    # Should verify correctly
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_jwt_tokens():
    """Test JWT token creation and verification"""
    from services.jwt_auth import create_token_pair, verify_token, TokenType
    
    tokens = create_token_pair(
        user_id="test@example.com",
        license_id=1,
        role="user"
    )
    
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    
    # Verify access token
    payload = verify_token(tokens["access_token"], TokenType.ACCESS)
    assert payload is not None
    assert payload["sub"] == "test@example.com"
    assert payload["license_id"] == 1


def test_extract_entities():
    """Test entity extraction from messages"""
    from agent import extract_entities
    
    message = "اتصل بي على 0501234567 أو راسلني على test@email.com"
    entities = extract_entities(message)
    
    assert "phones" in entities
    assert "emails" in entities


def test_rule_based_classify():
    """Test rule-based classification fallback"""
    from agent import rule_based_classify
    
    # Inquiry
    result = rule_based_classify("ما هو سعر المنتج؟")
    assert result["intent"] == "استفسار"
    
    # Complaint
    result = rule_based_classify("أريد تقديم شكوى")
    assert result["intent"] == "شكوى"
