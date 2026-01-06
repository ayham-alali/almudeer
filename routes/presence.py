"""
Al-Mudeer - Presence and Real-time Indicators Routes
API endpoints for broadcasting typing, recording, and presence status
"""

from fastapi import APIRouter, Depends, Body
from typing import Dict, Any
from pydantic import BaseModel

from dependencies import get_license_from_header
from services.websocket_manager import broadcast_typing_indicator, broadcast_recording_indicator

router = APIRouter(prefix="/api/presence", tags=["Chat Features"])


class IndicatorRequest(BaseModel):
    sender_contact: str
    is_active: bool


@router.post("/typing")
async def send_typing_indicator(
    data: IndicatorRequest,
    license: dict = Depends(get_license_from_header)
):
    """
    Broadcast that an agent is typing in a conversation.
    This informs other connected clients/UIs.
    """
    license_id = license.get("license_id")
    await broadcast_typing_indicator(
        license_id=license_id,
        sender_contact=data.sender_contact,
        is_typing=data.is_active
    )
    return {"success": True}


@router.post("/recording")
async def send_recording_indicator(
    data: IndicatorRequest,
    license: dict = Depends(get_license_from_header)
):
    """
    Broadcast that an agent is recording audio in a conversation.
    """
    license_id = license.get("license_id")
    await broadcast_recording_indicator(
        license_id=license_id,
        sender_contact=data.sender_contact,
        is_recording=data.is_active
    )
    return {"success": True}
