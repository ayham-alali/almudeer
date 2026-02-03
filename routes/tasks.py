from fastapi import APIRouter, HTTPException, Depends
from typing import List
from schemas.tasks import TaskCreate, TaskResponse, TaskUpdate
from models.tasks import get_tasks, create_task, update_task, delete_task, get_task
from dependencies import get_license_from_header
from errors import NotFoundError

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(license: dict = Depends(get_license_from_header)):
    """Get all tasks"""
    tasks = await get_tasks(license["license_id"])
    return tasks

@router.post("/", response_model=TaskResponse)
async def create_new_task(
    task: TaskCreate,
    license: dict = Depends(get_license_from_header)
):
    """Create or sync a task (atomic upsert)"""
    license_id = license["license_id"]
    
    try:
        result = await create_task(license_id, task.model_dump())
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create/sync task")
        return result
    except Exception as e:
        # If we get a unique constraint error, it might be a collision across licenses
        if "unique constraint" in str(e).lower() or "already exists" in str(e).lower():
            # Verify if it exists for another license
            from db_helper import get_db, fetch_one
            async with get_db() as db:
                global_check = await fetch_one(db, "SELECT license_key_id FROM tasks WHERE id = ?", (task.id,))
                if global_check and global_check["license_key_id"] != license_id:
                    raise HTTPException(
                        status_code=409, 
                        detail="Task ID already exists for a different account."
                    )
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put("/{task_id}", response_model=TaskResponse)
async def update_existing_task(
    task_id: str,
    task: TaskUpdate,
    license: dict = Depends(get_license_from_header)
):
    """Update a task"""
    result = await update_task(license["license_id"], task_id, task.model_dump(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result

@router.delete("/{task_id}")
async def delete_existing_task(
    task_id: str,
    license: dict = Depends(get_license_from_header)
):
    """Delete a task"""
    success = await delete_task(license["license_id"], task_id)
    if not success:
        raise NotFoundError(resource="Task", resource_id=task_id)
    return {"success": True}


# ============ Smart AI Features ============

from pydantic import BaseModel

class TaskSuggestionRequest(BaseModel):
    title: str

@router.post("/suggest", tags=["Tasks"])
async def suggest_task_details(
    data: TaskSuggestionRequest,
    license: dict = Depends(get_license_from_header)
):
    """
    Analyze task title and suggest details (Priority, Color, Subtasks).
    Uses Gemini AI.
    """
    from services.task_ai import analyze_task_intent
    
    # Analyze
    suggestions = await analyze_task_intent(data.title)
    
    return {
        "success": True,
        "data": suggestions
    }
