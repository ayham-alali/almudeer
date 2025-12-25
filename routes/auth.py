"""
Al-Mudeer - Authentication Routes
JWT-based login, registration, and token management
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from services.jwt_auth import (
    create_token_pair,
    refresh_access_token,
    hash_password,
    verify_password,
    get_current_user,
    require_admin,
)
from database import validate_license_key
from db_helper import get_db, execute_sql, fetch_one
from logging_config import get_logger
from security_config import validate_password_strength
from services.login_protection import check_account_lockout, record_failed_login, record_successful_login
from services.security_logger import get_security_logger
from services.token_blacklist import blacklist_token

logger = get_logger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ============ Request/Response Models ============

class LoginRequest(BaseModel):
    """Login with license key or email/password"""
    license_key: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class RegisterRequest(BaseModel):
    """Register a new user account"""
    email: EmailStr
    password: str
    name: str
    license_key: str  # Must have valid license to register


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: Optional[dict] = None


class RefreshRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


# ============ Auth Endpoints ============

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    """
    Login with license key or email/password.
    
    Returns JWT tokens for authenticated access.
    """
    # Option 1: Login with license key (existing flow)
    if data.license_key:
        result = await validate_license_key(data.license_key)
        
        if not result.get("valid"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid license key",
            )
        
        tokens = create_token_pair(
            user_id=data.license_key[:20],
            license_id=result.get("license_id"),
            role="user",
        )
        
        return TokenResponse(
            **tokens,
            user={
                "license_id": result.get("license_id"),
                "company_name": result.get("company_name"),
            }
        )
    
    # Option 2: Login with email/password
    if data.email and data.password:
        security_logger = get_security_logger()
        
        # Check if account is locked
        is_locked, remaining_seconds = check_account_lockout(data.email)
        if is_locked:
            security_logger.log_login_failed(data.email, reason="Account locked")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Account locked. Try again in {remaining_seconds // 60 + 1} minutes.",
            )
        
        # Look up user by email
        async with get_db() as db:
            user = await fetch_one(
                db,
                "SELECT * FROM users WHERE email = ?",
                [data.email]
            )
        
        if not user:
            record_failed_login(data.email)
            security_logger.log_login_failed(data.email, reason="User not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        
        if not verify_password(data.password, user.get("password_hash", "")):
            attempts, is_now_locked = record_failed_login(data.email)
            if is_now_locked:
                security_logger.log_account_locked(data.email, attempts=attempts)
            else:
                security_logger.log_login_failed(data.email, reason="Wrong password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        
        # Successful login - clear failed attempts
        record_successful_login(data.email)
        security_logger.log_login_success(data.email)
        
        tokens = create_token_pair(
            user_id=user.get("email"),
            license_id=user.get("license_key_id"),
            role=user.get("role", "user"),
        )
        
        return TokenResponse(
            **tokens,
            user={
                "email": user.get("email"),
                "name": user.get("name"),
                "role": user.get("role"),
            }
        )
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Provide license_key or email/password",
    )


@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest):
    """
    Register a new user account.
    
    Requires a valid license key to register.
    """
    # SECURITY: Validate password strength first
    is_valid, error_message = validate_password_strength(data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )
    
    # Validate license key
    license_result = await validate_license_key(data.license_key)
    if not license_result.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid license key",
        )
    
    # Check if email already exists
    async with get_db() as db:
        existing = await fetch_one(
            db,
            "SELECT id FROM users WHERE email = ?",
            [data.email]
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        # Create user
        password_hash = hash_password(data.password)
        await execute_sql(
            db,
            """
            INSERT INTO users (email, password_hash, name, license_key_id, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [data.email, password_hash, data.name, license_result.get("license_id"), "user", datetime.utcnow().isoformat()]
        )
    
    # Create tokens
    tokens = create_token_pair(
        user_id=data.email,
        license_id=license_result.get("license_id"),
        role="user",
    )
    
    logger.info(f"New user registered: {data.email}")
    
    return TokenResponse(
        **tokens,
        user={
            "email": data.email,
            "name": data.name,
            "role": "user",
        }
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshRequest):
    """
    Refresh an expired access token.
    
    Use the refresh token to get a new access token.
    """
    result = refresh_access_token(data.refresh_token)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    return TokenResponse(**result)


@router.get("/me")
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "success": True,
        "user": user,
    }


@router.post("/logout")
async def logout(
    request: Request,
    user: dict = Depends(get_current_user)
):
    """
    Logout and invalidate the current token.
    
    The token will be blacklisted and cannot be used again.
    """
    from fastapi import Request
    
    # Get the token from the Authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        
        # Decode to get JTI and expiry
        try:
            from jose import jwt
            from services.jwt_auth import config
            payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
            jti = payload.get("jti")
            exp = payload.get("exp")
            
            if jti and exp:
                from datetime import datetime
                expires_at = datetime.utcfromtimestamp(exp)
                blacklist_token(jti, expires_at)
                
                security_logger = get_security_logger()
                security_logger.log_logout(user.get('user_id'))
                security_logger.log_token_blacklisted(user.get('user_id'), jti)
                
                logger.info(f"User logged out and token blacklisted: {user.get('user_id')}")
        except Exception as e:
            logger.warning(f"Could not blacklist token on logout: {e}")
    
    return {"success": True, "message": "Logged out successfully"}
