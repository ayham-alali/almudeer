"""
Al-Mudeer - JWT Authentication Service
Production-ready JWT authentication with access/refresh tokens
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from jose import jwt, JWTError
from passlib.context import CryptContext

from constants import TeamRoles
from logging_config import get_logger

logger = get_logger(__name__)


# ============ Configuration ============

def _get_jwt_secret_key() -> str:
    """Get JWT secret key from environment, fail fast in production if not set."""
    key = os.getenv("JWT_SECRET_KEY")
    if key:
        return key
    
    # In production, we MUST have a stable secret key
    if os.getenv("ENVIRONMENT", "development") == "production":
        raise ValueError(
            "JWT_SECRET_KEY must be set in production! "
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    
    # Development only: generate a random key (tokens won't persist across restarts)
    generated_key = secrets.token_hex(32)
    logger.warning(
        "JWT_SECRET_KEY not set - using auto-generated key. "
        "Tokens will be invalidated on restart. Set JWT_SECRET_KEY in production!"
    )
    return generated_key


@dataclass
class JWTConfig:
    """JWT configuration from environment"""
    secret_key: str = None  # Set in __post_init__
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))
    
    def __post_init__(self):
        if self.secret_key is None:
            self.secret_key = _get_jwt_secret_key()


config = JWTConfig()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============ Token Types ============

class TokenType:
    ACCESS = "access"
    REFRESH = "refresh"


# ============ Token Operations ============

def create_access_token(data: Dict[str, Any], expires_delta: timedelta = None) -> Tuple[str, str, datetime]:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data (should include 'sub' for subject/user ID)
        expires_delta: Custom expiration time
    
    Returns:
        Tuple of (encoded_token, jti, expiry_datetime)
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=config.access_token_expire_minutes))
    jti = secrets.token_hex(16)  # Unique token ID for blacklisting
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": TokenType.ACCESS,
        "jti": jti,
    })
    
    return jwt.encode(to_encode, config.secret_key, algorithm=config.algorithm), jti, expire


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token (longer expiration).
    
    Args:
        data: Payload data (should include 'sub' for subject/user ID)
    
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=config.refresh_token_expire_days)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": TokenType.REFRESH,
        "jti": secrets.token_hex(16),  # Unique token ID for revocation
    })
    
    return jwt.encode(to_encode, config.secret_key, algorithm=config.algorithm)


def create_token_pair(user_id: str, license_id: int = None, role: str = TeamRoles.MEMBER) -> Dict[str, Any]:
    """
    Create both access and refresh tokens.
    
    Args:
        user_id: User identifier (email or license key)
        license_id: Associated license ID
        role: User role (admin/user)
    
    Returns:
        Dict with 'access_token', 'refresh_token', 'jti', 'expires_at'
    """
    payload = {
        "sub": user_id,
        "license_id": license_id,
        "role": role,
    }
    
    access_token, jti, expires_at = create_access_token(payload)
    
    return {
        "access_token": access_token,
        "refresh_token": create_refresh_token(payload),
        "token_type": "bearer",
        "expires_in": config.access_token_expire_minutes * 60,  # seconds
        "jti": jti,
        "expires_at": expires_at,
    }


def verify_token(token: str, token_type: str = TokenType.ACCESS) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        token_type: Expected token type (access/refresh)
    
    Returns:
        Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
        
        # Verify token type
        if payload.get("type") != token_type:
            logger.warning(f"Token type mismatch: expected {token_type}, got {payload.get('type')}")
            return None
        
        # Check if token is blacklisted (for access tokens)
        if token_type == TokenType.ACCESS:
            jti = payload.get("jti")
            if jti:
                from services.token_blacklist import is_token_blacklisted
                if is_token_blacklisted(jti):
                    logger.info(f"Token {jti[:8]}... is blacklisted")
                    return None
        
        return payload
        
    except JWTError as e:
        logger.debug(f"JWT verification failed: {e}")
        return None


def refresh_access_token(refresh_token: str) -> Optional[Dict[str, Any]]:
    """
    Use a refresh token to get a new access token.
    
    Args:
        refresh_token: Valid refresh token
    
    Returns:
        New token pair or None if refresh token is invalid
    """
    payload = verify_token(refresh_token, TokenType.REFRESH)
    
    if not payload:
        return None
    
    # Create new access token (not new refresh token for security)
    access_token, jti, expires_at = create_access_token({
        "sub": payload.get("sub"),
        "license_id": payload.get("license_id"),
        "role": payload.get("role", TeamRoles.MEMBER),
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": config.access_token_expire_minutes * 60,
        "jti": jti,
        "expires_at": expires_at,
    }


# ============ Password Operations ============

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ============ FastAPI Dependencies ============

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user.
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"user": user}
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = verify_token(credentials.credentials, TokenType.ACCESS)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "user_id": payload.get("sub"),
        "license_id": payload.get("license_id"),
        "role": payload.get("role", TeamRoles.MEMBER),
    }


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[Dict[str, Any]]:
    """Optional authentication - returns None if not authenticated"""
    if not credentials:
        return None
    
    payload = verify_token(credentials.credentials, TokenType.ACCESS)
    if not payload:
        return None
    
    return {
        "user_id": payload.get("sub"),
        "license_id": payload.get("license_id"),
        "role": payload.get("role", TeamRoles.MEMBER),
    }


def require_role(required_role: str):
    """
    Dependency factory for role-based access control.
    
    Usage:
        @app.get("/admin-only")
        async def admin_route(user: dict = Depends(require_role(TeamRoles.ADMIN))):
            return {"access": "granted"}
    """
    async def role_checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required",
            )
        return user
    return role_checker


# Admin shortcut
require_admin = require_role(TeamRoles.ADMIN)
