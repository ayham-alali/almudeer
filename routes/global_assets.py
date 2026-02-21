"""
Al-Mudeer - Global Assets Management
Admin-only routes to manage tasks and library items for all users (license_id 0)
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import Optional, List
import os

from models.tasks import create_task
from models.library import add_library_item
from routes.notifications import verify_admin

router = APIRouter(prefix="/api/admin/global-assets", tags=["Admin - Global Assets"])

class GlobalTaskCreate(BaseModel):
    id: str = Field(..., description="Unique task ID")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: str = Field(default="medium")
    category: Optional[str] = None

class GlobalNoteCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    item_type: str = Field(default="note")

@router.post("/tasks")
async def add_global_task(
    data: GlobalTaskCreate,
    _: None = Depends(verify_admin)
):
    """Add a global task visible to everyone (license_id 0)"""
    try:
        task_data = data.model_dump()
        result = await create_task(0, task_data)
        return {"success": True, "task": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/library")
async def add_global_library_item(
    data: GlobalNoteCreate,
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
        return {"success": True, "item": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
