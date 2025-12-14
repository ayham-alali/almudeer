"""
Al-Mudeer - Subscription Key Management Routes
Easy subscription key generation and management for clients
"""

import os
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
from dotenv import load_dotenv

from database import generate_license_key, validate_license_key
from security_enhanced import validate_license_key_format

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/api/admin/subscription", tags=["Subscription Management"])

# Admin authentication
ADMIN_KEY = os.getenv("ADMIN_KEY")
if not ADMIN_KEY:
    raise ValueError("ADMIN_KEY environment variable is required")


async def verify_admin(x_admin_key: str = Header(None, alias="X-Admin-Key")):
    """Verify admin key"""
    if not x_admin_key or x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="غير مصرح - Admin key required")


# ============ Schemas ============

class SubscriptionCreate(BaseModel):
    """Request to create a new subscription"""
    company_name: str = Field(..., description="اسم الشركة", min_length=2, max_length=200)
    contact_email: Optional[EmailStr] = Field(None, description="البريد الإلكتروني للتواصل")
    contact_phone: Optional[str] = Field(None, description="رقم الهاتف")
    days_valid: int = Field(365, description="مدة الصلاحية بالأيام", ge=1, le=3650)
    max_requests_per_day: int = Field(1000, description="الحد الأقصى للطلبات اليومية", ge=10, le=100000)
    notes: Optional[str] = Field(None, description="ملاحظات إضافية", max_length=500)


class SubscriptionResponse(BaseModel):
    """Response with subscription details"""
    success: bool
    subscription_key: str
    company_name: str
    expires_at: str
    max_requests_per_day: int
    message: str


class SubscriptionListResponse(BaseModel):
    """Response for subscription list"""
    subscriptions: List[dict]
    total: int


class SubscriptionUpdate(BaseModel):
    """Request to update subscription"""
    is_active: Optional[bool] = None
    max_requests_per_day: Optional[int] = Field(None, ge=10, le=100000)
    days_valid_extension: Optional[int] = Field(None, description="إضافة أيام للصلاحية", ge=0, le=3650)
    notes: Optional[str] = Field(None, max_length=500)


# ============ Routes ============

@router.post("/create", response_model=SubscriptionResponse)
async def create_subscription(
    subscription: SubscriptionCreate,
    _: None = Depends(verify_admin)
):
    """
    Create a new subscription key for a client.
    
    This endpoint allows easy generation of subscription keys with customizable
    validity period and request limits.
    """
    import os
    from logging_config import get_logger
    
    logger = get_logger(__name__)
    
    try:
        # Generate the subscription key
        key = await generate_license_key(
            company_name=subscription.company_name,
            contact_email=subscription.contact_email,
            days_valid=subscription.days_valid,
            max_requests=subscription.max_requests_per_day
        )
        
        # Calculate expiration date
        expires_at = datetime.now() + timedelta(days=subscription.days_valid)
        
        # Save additional metadata if needed (contact_phone, notes)
        # This could be stored in a separate table or as JSON in license_keys
        
        logger.info(f"Created subscription for {subscription.company_name}: {key[:20]}...")
        
        return SubscriptionResponse(
            success=True,
            subscription_key=key,
            company_name=subscription.company_name,
            expires_at=expires_at.isoformat(),
            max_requests_per_day=subscription.max_requests_per_day,
            message=f"تم إنشاء اشتراك بنجاح لـ {subscription.company_name}"
        )
    
    except Exception as e:
        logger.error(f"Error creating subscription: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"حدث خطأ أثناء إنشاء الاشتراك: {str(e)}"
        )


@router.get("/list", response_model=SubscriptionListResponse)
async def list_subscriptions(
    active_only: bool = False,
    limit: int = 100,
    _: None = Depends(verify_admin)
):
    """
    List all subscriptions with filtering options.
    """
    import os
    from database import DB_TYPE, DATABASE_PATH, DATABASE_URL, POSTGRES_AVAILABLE
    
    try:
        subscriptions = []
        
        if DB_TYPE == "postgresql" and POSTGRES_AVAILABLE:
            import asyncpg
            if not DATABASE_URL:
                raise ValueError("DATABASE_URL is required for PostgreSQL")
            conn = await asyncpg.connect(DATABASE_URL)
            try:
                query = "SELECT id, company_name, contact_email, is_active, created_at, expires_at, max_requests_per_day, requests_today, last_request_date FROM license_keys"
                params = []
                
                if active_only:
                    query += " WHERE is_active = TRUE"
                
                query += " ORDER BY created_at DESC LIMIT $1"
                params.append(limit)
                
                rows = await conn.fetch(query, *params)
                
                for row in rows:
                    row_dict = dict(row)
                    # Calculate days remaining
                    if row_dict.get("expires_at"):
                        if isinstance(row_dict["expires_at"], str):
                            expires = datetime.fromisoformat(row_dict["expires_at"])
                        else:
                            expires = row_dict["expires_at"]
                        days_remaining = (expires - datetime.now()).days
                        row_dict["days_remaining"] = max(0, days_remaining)
                    else:
                        row_dict["days_remaining"] = None
                    
                    subscriptions.append(row_dict)
            finally:
                await conn.close()
        else:
            import aiosqlite
            async with aiosqlite.connect(DATABASE_PATH) as db:
                db.row_factory = aiosqlite.Row
                
                query = "SELECT id, company_name, contact_email, is_active, created_at, expires_at, max_requests_per_day, requests_today, last_request_date FROM license_keys"
                params = []
                
                if active_only:
                    query += " WHERE is_active = 1"
                
                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    
                    for row in rows:
                        row_dict = dict(row)
                        # Calculate days remaining
                        if row_dict.get("expires_at"):
                            expires = datetime.fromisoformat(row_dict["expires_at"])
                            days_remaining = (expires - datetime.now()).days
                            row_dict["days_remaining"] = max(0, days_remaining)
                        else:
                            row_dict["days_remaining"] = None
                        
                        subscriptions.append(row_dict)
        
        return SubscriptionListResponse(
            subscriptions=subscriptions,
            total=len(subscriptions)
        )
    
    except Exception as e:
        from logging_config import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error listing subscriptions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="حدث خطأ أثناء جلب الاشتراكات")


@router.get("/{license_id}")
async def get_subscription(
    license_id: int,
    _: None = Depends(verify_admin)
):
    """Get details of a specific subscription"""
    import aiosqlite
    from database import DATABASE_PATH
    
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM license_keys WHERE id = ?
            """, (license_id,)) as cursor:
                row = await cursor.fetchone()
                
                if not row:
                    raise HTTPException(status_code=404, detail="الاشتراك غير موجود")
                
                subscription = dict(row)
                
                # Calculate days remaining
                if subscription.get("expires_at"):
                    expires = datetime.fromisoformat(subscription["expires_at"])
                    days_remaining = (expires - datetime.now()).days
                    subscription["days_remaining"] = max(0, days_remaining)
                else:
                    subscription["days_remaining"] = None
                
                # Calculate usage statistics
                today = datetime.now().date().isoformat()
                if subscription.get("last_request_date") == today:
                    subscription["requests_today"] = subscription.get("requests_today", 0)
                else:
                    subscription["requests_today"] = 0
                
                return {"subscription": subscription}
    
    except HTTPException:
        raise
    except Exception as e:
        from logging_config import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error getting subscription: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="حدث خطأ أثناء جلب الاشتراك")


@router.patch("/{license_id}")
async def update_subscription(
    license_id: int,
    update: SubscriptionUpdate,
    _: None = Depends(verify_admin)
):
    """Update subscription settings"""
    import aiosqlite
    from database import DATABASE_PATH
    from logging_config import get_logger
    
    logger = get_logger(__name__)
    
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Get current subscription
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM license_keys WHERE id = ?", (license_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="الاشتراك غير موجود")
                
                current = dict(row)
            
            # Build update query
            updates = []
            params = []
            
            if update.is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if update.is_active else 0)
            
            if update.max_requests_per_day is not None:
                updates.append("max_requests_per_day = ?")
                params.append(update.max_requests_per_day)
            
            if update.days_valid_extension is not None and update.days_valid_extension > 0:
                # Extend expiration date
                current_expires = datetime.fromisoformat(current["expires_at"]) if current.get("expires_at") else datetime.now()
                new_expires = current_expires + timedelta(days=update.days_valid_extension)
                updates.append("expires_at = ?")
                params.append(new_expires.isoformat())
            
            if not updates:
                raise HTTPException(status_code=400, detail="لا توجد تحديثات لتطبيقها")
            
            # Execute update
            params.append(license_id)
            query = f"UPDATE license_keys SET {', '.join(updates)} WHERE id = ?"
            await db.execute(query, params)
            await db.commit()
            
            logger.info(f"Updated subscription {license_id}")
            
            return {
                "success": True,
                "message": "تم تحديث الاشتراك بنجاح"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating subscription: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="حدث خطأ أثناء تحديث الاشتراك")


class ValidateKeyRequest(BaseModel):
    """Request to validate a subscription key"""
    key: str = Field(..., description="Subscription key to validate")


@router.post("/validate-key")
async def validate_subscription_key(
    request: ValidateKeyRequest
):
    """
    Validate a subscription key (public endpoint, no admin required).
    Useful for clients to check their key status.
    """
    if not validate_license_key_format(request.key):
        return {
            "valid": False,
            "error": "تنسيق المفتاح غير صحيح"
        }
    
    result = await validate_license_key(request.key)
    return result


@router.get("/usage/{license_id}")
async def get_subscription_usage(
    license_id: int,
    days: int = 30,
    _: None = Depends(verify_admin)
):
    """Get usage statistics for a subscription"""
    import aiosqlite
    from database import DATABASE_PATH
    
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            
            # Get usage logs
            async with db.execute("""
                SELECT 
                    DATE(created_at) as date,
                    action_type,
                    COUNT(*) as count
                FROM usage_logs
                WHERE license_key_id = ? 
                AND created_at >= datetime('now', '-' || ? || ' days')
                GROUP BY DATE(created_at), action_type
                ORDER BY date DESC
            """, (license_id, days)) as cursor:
                rows = await cursor.fetchall()
                usage_stats = [dict(row) for row in rows]
            
            # Get total counts
            async with db.execute("""
                SELECT 
                    COUNT(*) as total_requests,
                    COUNT(DISTINCT DATE(created_at)) as active_days
                FROM usage_logs
                WHERE license_key_id = ? 
                AND created_at >= datetime('now', '-' || ? || ' days')
            """, (license_id, days)) as cursor:
                totals = dict(await cursor.fetchone())
            
            return {
                "license_id": license_id,
                "period_days": days,
                "usage_stats": usage_stats,
                "totals": totals
            }
    
    except Exception as e:
        from logging_config import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error getting usage stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="حدث خطأ أثناء جلب إحصائيات الاستخدام")

