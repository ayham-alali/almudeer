from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
from datetime import datetime
from schemas.tasks import TaskCreate, TaskResponse, TaskUpdate
from models.tasks import get_tasks, create_task, update_task, delete_task, get_task
from dependencies import get_license_from_header
from services.jwt_auth import get_current_user
from errors import NotFoundError
from services.websocket_manager import broadcast_task_sync
from services.fcm_mobile_service import send_fcm_to_user

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])
 
async def notify_assignment(license_id: int, task_id: str, title: str, assignee: str, sender_name: str):
    """Send push notification to assignee"""
    try:
        await send_fcm_to_user(
            license_id=license_id,
            user_id=assignee,
            title="مهمة جديدة مسندة إليك",
            body=f"قام {sender_name} بإسناد المهمة: {title}",
            data={
                "type": "task_assigned",
                "task_id": task_id,
            },
            link=f"/tasks/{task_id}"
        )
    except Exception as e:
        print(f"Failed to send assignment notification: {e}")

@router.get("/collaborators", response_model=List[dict])
async def list_collaborators(
    user: dict = Depends(get_current_user)
):
    """Get all users sharing the same license key"""
    license_id = user["license_id"]
    from db_helper import get_db, fetch_all
    async with get_db() as db:
        rows = await fetch_all(db, "SELECT email, name, role FROM users WHERE license_key_id = ?", (license_id,))
        return [dict(row) for row in rows]

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    since: Optional[datetime] = None,
    license: dict = Depends(get_license_from_header)
):
    """Get all tasks, optionally filtered by last update time (delta sync)"""
    tasks = await get_tasks(license["license_id"], since=since)
    return tasks

@router.post("/", response_model=TaskResponse)
async def create_new_task(
    task: TaskCreate,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Create or sync a task (atomic upsert)"""
    license_id = user["license_id"]
    
    # Set created_by if not present
    task_dict = task.model_dump()
    if not task_dict.get("created_by"):
        task_dict["created_by"] = user["user_id"]
        
    try:
        result = await create_task(license_id, task_dict)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create/sync task")
        
        # Trigger real-time sync across other devices
        background_tasks.add_task(broadcast_task_sync, license_id)
        
        # If assigned, notify assignee
        if task_dict.get("assigned_to") and task_dict["assigned_to"] != user["user_id"]:
            background_tasks.add_task(
                notify_assignment, 
                license_id, 
                result["id"], 
                result["title"], 
                task_dict["assigned_to"],
                user.get("name") or user["user_id"]
            )
        
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
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Update a task"""
    license_id = user["license_id"]
    
    # Get current task to check for assignment changes
    current_task = await get_task(license_id, task_id)
    if not current_task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    update_data = task.model_dump(exclude_unset=True)
    result = await update_task(license_id, task_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Trigger real-time sync across other devices
    background_tasks.add_task(broadcast_task_sync, license_id)
    
    # If assigned_to changed, notify new assignee
    if "assigned_to" in update_data:
        new_assignee = update_data["assigned_to"]
        old_assignee = current_task.get("assigned_to")
        
        if new_assignee and new_assignee != old_assignee and new_assignee != user["user_id"]:
            background_tasks.add_task(
                notify_assignment, 
                license_id, 
                task_id, 
                result["title"], 
                new_assignee,
                user.get("name") or user["user_id"]
            )
            
    return result

@router.delete("/{task_id}")
async def delete_existing_task(
    task_id: str,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Delete a task"""
    license_id = user["license_id"]
    success = await delete_task(license_id, task_id)
    if not success:
        raise NotFoundError(resource="Task", resource_id=task_id)
    
    # Trigger real-time sync across other devices
    background_tasks.add_task(broadcast_task_sync, license_id)
    
    return {"success": True}
