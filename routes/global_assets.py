"""
Al-Mudeer - Global Assets Management
Admin-only routes to manage tasks and library items for all users (license_id 0)
"""

from fastapi import APIRouter, HTTPException, Depends, Header, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import uuid

from models.tasks import create_task, get_tasks, delete_task
from models.library import add_library_item, get_library_items, delete_library_item
from routes.notifications import verify_admin
from services.websocket_manager import broadcast_global_sync

router = APIRouter(prefix="/api/admin/global-assets", tags=["Admin - Global Assets"])

class GlobalTaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: str = Field(default="medium")
    category: Optional[str] = None

class GlobalNoteCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    item_type: str = Field(default="note")

# --- Tasks ---

@router.get("/tasks")
async def list_global_tasks(_: None = Depends(verify_admin)):
    """List all global tasks (license_id 0)"""
    try:
        tasks = await get_tasks(0)
        return {"success": True, "tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks")
async def add_global_task(
    data: GlobalTaskCreate,
    background_tasks: BackgroundTasks,
    _: None = Depends(verify_admin)
):
    """Add a global task visible to everyone (license_id 0)"""
    try:
        task_data = data.model_dump()
        task_data["id"] = uuid.uuid4().hex
        
        result = await create_task(0, task_data)
        
        # Trigger real-time sync across all clients
        background_tasks.add_task(broadcast_global_sync, "task_sync")
        
        return {"success": True, "task": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tasks/{task_id}")
async def remove_global_task(
    task_id: str,
    background_tasks: BackgroundTasks,
    _: None = Depends(verify_admin)
):
    """Delete a global task"""
    try:
        success = await delete_task(0, task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
            
        # Trigger real-time sync across all clients
        background_tasks.add_task(broadcast_global_sync, "task_sync")
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Library Items / Notes ---

@router.get("/library")
async def list_global_library_items(_: None = Depends(verify_admin)):
    """List all global library items (license_id 0)"""
    try:
        items = await get_library_items(0)
        return {"success": True, "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/library")
async def add_global_library_item(
    data: GlobalNoteCreate,
    background_tasks: BackgroundTasks,
    _: None = Depends(verify_admin)
):
    """Add a global library item (note, link, etc.) visible to everyone"""
    try:
        result = await add_library_item(
            license_id=0,
            item_type=data.item_type,
            title=data.title,
            content=data.content
        )
        
        # Trigger real-time sync across all clients
        background_tasks.add_task(broadcast_global_sync, "library_sync")
        
        return {"success": True, "item": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/library/{item_id}")
async def remove_global_library_item(
    item_id: int,
    background_tasks: BackgroundTasks,
    _: None = Depends(verify_admin)
):
    """Delete a global library item"""
    try:
        success = await delete_library_item(0, item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Library item not found")
            
        # Trigger real-time sync across all clients
        background_tasks.add_task(broadcast_global_sync, "library_sync")
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
