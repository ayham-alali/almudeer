"""
Al-Mudeer - Version Analytics API
Provides insights into app update adoption and performance
"""

from fastapi import APIRouter, Header, HTTPException, Query
from typing import Optional, List, Dict, Any
import os
import secrets
from database import (
    get_version_distribution,
    get_update_funnel,
    get_time_to_update_metrics,
    get_update_events
)

router = APIRouter(tags=["Version Analytics"])

# Admin key for manual operations
_ADMIN_KEY = os.getenv("ADMIN_KEY", "")

def compare_secure(a: Optional[str], b: str) -> bool:
    """Constant-time comparison to prevent timing attacks"""
    if not a: return False
    return secrets.compare_digest(a, b)


@router.get("/api/app/version-distribution", summary="Get user version distribution (admin only)")
async def get_version_distribution_stats(
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")
):
    """
    Get the distribution of users across different app build numbers.
    Based on the most recent update check event for each unique device/license.
    
    Requires: X-Admin-Key header
    """
    if not compare_secure(x_admin_key, _ADMIN_KEY):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    distribution = await get_version_distribution()
    return {
        "distribution": distribution,
        "total_active_users": sum(d.get("user_count", 0) for d in distribution)
    }


@router.get("/api/app/update-funnel", summary="Get update funnel metrics (admin only)")
async def get_update_funnel_stats(
    days: int = Query(30, ge=1, le=365, description="Lookback window in days"),
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")
):
    """
    Get conversion metrics for the update process:
    Viewed -> Clicked Update -> Installed
    
    Requires: X-Admin-Key header
    """
    if not compare_secure(x_admin_key, _ADMIN_KEY):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    funnel = await get_update_funnel(days=days)
    
    # Calculate conversion rates
    views = funnel.get("views", 0)
    clicks = funnel.get("clicks", 0)
    installs = funnel.get("installs", 0)
    
    conversion_rate = 0
    if views > 0:
        conversion_rate = round((installs / views) * 100, 1)
        
    return {
        "funnel": funnel,
        "conversion_rate_percent": conversion_rate,
        "window_days": days
    }


@router.get("/api/app/time-to-update", summary="Get time-to-update metrics (admin only)")
async def get_time_to_update_stats(
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")
):
    """
    Get metrics on how long it takes for users to update after seeing the prompt.
    Returns average and median time in hours.
    
    Requires: X-Admin-Key header
    """
    if not compare_secure(x_admin_key, _ADMIN_KEY):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return await get_time_to_update_metrics()


@router.get("/api/app/update-analytics", summary="Get raw update events (admin only)")
async def get_raw_update_events(
    limit: int = Query(100, ge=1, le=1000),
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")
):
    """
    Get raw list of recent update events.
    
    Requires: X-Admin-Key header
    """
    if not compare_secure(x_admin_key, _ADMIN_KEY):
        raise HTTPException(status_code=403, detail="Admin access required")
        
    return await get_update_events(limit=limit)
