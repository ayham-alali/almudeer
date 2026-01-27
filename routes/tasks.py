from fastapi import APIRouter, HTTPException, Depends
from typing import List
from schemas.tasks import TaskCreate, TaskResponse, TaskUpdate
from models.tasks import get_tasks, create_task, update_task, delete_task, get_task
from dependencies import get_license_from_header

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
    """Create or sync a task"""
    license_id = license["license_id"]
    
    # Check if exists for THIS license (normal sync/upsert)
    existing = await get_task(license_id, task.id)
    if existing:
        return await update_task(license_id, task.id, task.model_dump(exclude_unset=True))
    
    # Check if the ID exists GLOBALLY to prevent unique constraint violation
    # If it exists for a DIFFERENT license, we should either return an error
    # or generate a new ID. Since the client sends UUIDs, collisions are rare
    # but the logs show it happened. We will return 409 Conflict if hijacked.
    from db_helper import get_db, fetch_one
    async with get_db() as db:
        global_check = await fetch_one(db, "SELECT license_key_id FROM tasks WHERE id = ?", (task.id,))
        if global_check:
            # Task ID exists for another license!
            if global_check["license_key_id"] != license_id:
                raise HTTPException(
                    status_code=409, 
                    detail=f"Task ID already exists for a different account. Please use a unique ID."
                )
            # If it's the same license but get_task missed it (unlikely), update it
            return await update_task(license_id, task.id, task.model_dump(exclude_unset=True))
        
    result = await create_task(license_id, task.model_dump())
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create task")
    return result

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
