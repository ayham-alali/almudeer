"""
Al-Mudeer - Stories API Routes
Handling story creation, listing, viewing, and real-time broadcasts
"""

import os
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from starlette.requests import Request

from db_helper import get_db, fetch_one
from dependencies import get_license_from_header
from services.jwt_auth import get_current_user_optional
from models.stories import (
    add_story,
    get_active_stories,
    mark_story_viewed,
    get_story_viewers,
    delete_story,
    update_story
)
from schemas.stories import (
    StoryCreateText, 
    StoriesListResponse, 
    StoryResponse, 
    StoryViewerDetails,
    StoryUpdate
)
from services.file_storage_service import get_file_storage
from services.websocket_manager import get_websocket_manager, WebSocketMessage
from security import sanitize_string

router = APIRouter(prefix="/api/stories", tags=["Stories"])

# File storage service instance
file_storage = get_file_storage()

@router.get("/", response_model=StoriesListResponse)
async def list_stories(
    viewer_contact: Optional[str] = Query(None),
    license: dict = Depends(get_license_from_header)
):
    """List active stories for the license."""
    stories = await get_active_stories(license["license_id"], viewer_contact=viewer_contact)
    return {"success": True, "stories": stories}

@router.post("/text", response_model=StoryResponse)
async def create_text_story(
    data: StoryCreateText,
    license: dict = Depends(get_license_from_header),
    user: Optional[dict] = Depends(get_current_user_optional)
):
    """Create a new text-only story."""
    user_id = user.get("user_id") if user else None
    user_name = license.get("company_name", "مستخدم")
    
    if user_id:
        async with get_db() as db:
            user_row = await fetch_one(db, "SELECT name FROM users WHERE email = ?", [user_id])
            if user_row and user_row.get("name"):
                user_name = user_row["name"]

    story = await add_story(
        license_id=license["license_id"],
        story_type="text",
        user_id=user_id,
        user_name=user_name,
        title=sanitize_string(data.title) if data.title else None,
        content=sanitize_string(data.content, max_length=1000),
        duration_hours=data.duration_hours
    )
    
    # Broadcast to all connected clients for this license
    manager = get_websocket_manager()
    await manager.send_to_license(
        license["license_id"],
        WebSocketMessage(event="new_story", data=story)
    )
    
    return story

@router.post("/upload", response_model=StoryResponse)
async def upload_media_story(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    duration_hours: int = Form(24),
    license: dict = Depends(get_license_from_header),
    user: Optional[dict] = Depends(get_current_user_optional)
):
    """Upload a media story (image/video/audio)."""
    user_id = user.get("user_id") if user else None
    user_name = license.get("company_name", "مستخدم")
    
    if user_id:
        async with get_db() as db:
            user_row = await fetch_one(db, "SELECT name FROM users WHERE email = ?", [user_id])
            if user_row and user_row.get("name"):
                user_name = user_row["name"]

    content_type = file.content_type or "application/octet-stream"
    
    # Determine type
    story_type = "file"
    if content_type.startswith("image/"):
        story_type = "image"
    elif content_type.startswith("video/"):
        story_type = "video"
    elif content_type.startswith("audio/"):
        story_type = "audio"

    try:
        # Security/Reliability block (approx check before saving)
        # Note: True file size checking for streaming is done implicitly by catching large files
        # but here we rely on the client not sending unreasonably large files since it's chunked.
        
        # Save file asynchronously
        relative_path, public_url = await file_storage.save_upload_file_async(
            upload_file=file,
            filename=file.filename,
            mime_type=content_type,
            subfolder="stories"
        )
        
        story = await add_story(
            license_id=license["license_id"],
            story_type=story_type,
            user_id=user_id,
            user_name=user_name,
            title=sanitize_string(title) if title else None,
            media_path=public_url,
            duration_hours=duration_hours
        )
        
        # Broadcast real-time update
        manager = get_websocket_manager()
        await manager.send_to_license(
            license["license_id"],
            WebSocketMessage(event="new_story", data=story)
        )
        
        return story
    except Exception as e:
        logger.error(f"Error in upload_media_story: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"حدث خطأ أثناء رفع القصة: {str(e)}")

@router.put("/{story_id}", response_model=StoryResponse)
async def update_story_content(
    story_id: int,
    data: StoryUpdate,
    license: dict = Depends(get_license_from_header),
    user: Optional[dict] = Depends(get_current_user_optional)
):
    """Update an existing story (text/title only)."""
    user_id = user.get("user_id") if user else None
    if not user_id:
        raise HTTPException(status_code=403, detail="يجب تسجيل الدخول لتعديل القصة")
        
    story = await update_story(
        story_id=story_id,
        license_id=license["license_id"],
        user_id=user_id,
        title=sanitize_string(data.title) if data.title else None,
        content=sanitize_string(data.content) if data.content else None
    )
    
    if not story:
        raise HTTPException(status_code=404, detail="القصة غير موجودة أو لا تملك صلاحية تعديلها")
        
    # Broadcast real-time update
    manager = get_websocket_manager()
    await manager.send_to_license(
        license["license_id"],
        WebSocketMessage(event="story_updated", data=story)
    )
    
    return story

@router.post("/{story_id}/view")
async def view_story(
    story_id: int,
    viewer_contact: str = Form(...),
    viewer_name: Optional[str] = Form(None),
    license: dict = Depends(get_license_from_header)
):
    """Mark a story as viewed by a contact."""
    success = await mark_story_viewed(story_id, viewer_contact, viewer_name)
    return {"success": success}

@router.get("/{story_id}/viewers", response_model=List[StoryViewerDetails])
async def list_story_viewers(
    story_id: int,
    license: dict = Depends(get_license_from_header)
):
    """Get list of people who viewed this story."""
    viewers = await get_story_viewers(story_id, license["license_id"])
    return viewers

@router.delete("/{story_id}")
async def remove_story(
    story_id: int,
    license: dict = Depends(get_license_from_header),
    user: Optional[dict] = Depends(get_current_user_optional)
):
    """Delete a story. Ensures only owner or admin can delete."""
    user_id = user.get("user_id") if user else None
    success = await delete_story(story_id, license["license_id"], user_id=user_id)
    
    if success:
        # Broadcast real-time delete
        manager = get_websocket_manager()
        await manager.send_to_license(
            license["license_id"],
            WebSocketMessage(event="story_deleted", data={"id": story_id})
        )
        
    return {"success": success}
