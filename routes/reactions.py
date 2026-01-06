"""
Al-Mudeer - Message Reactions Routes
API endpoints for managing emoji reactions on messages
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from pydantic import BaseModel

from dependencies import get_license_from_header
from models.reactions import (
    add_reaction,
    remove_reaction,
    get_message_reactions,
    has_user_reacted
)

router = APIRouter(prefix="/api/reactions", tags=["Chat Features"])


class ReactionRequest(BaseModel):
    emoji: str
    user_type: str = "agent"  # agent, customer


@router.get("/{message_id}")
async def get_reactions(
    message_id: int,
    license: dict = Depends(get_license_from_header)
):
    """Get all reactions for a message"""
    reactions = await get_message_reactions(message_id)
    return {"reactions": reactions}


@router.post("/{message_id}")
async def create_reaction(
    message_id: int,
    data: ReactionRequest,
    license: dict = Depends(get_license_from_header)
):
    """Add a reaction to a message"""
    result = await add_reaction(
        message_id,
        license["license_id"],
        data.emoji,
        data.user_type
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
        
    return result


@router.delete("/{message_id}")
async def delete_reaction(
    message_id: int,
    emoji: str,
    user_type: str = "agent",
    license: dict = Depends(get_license_from_header)
):
    """Remove a reaction from a message"""
    result = await remove_reaction(
        message_id,
        license["license_id"],
        emoji,
        user_type
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
        
    return result
