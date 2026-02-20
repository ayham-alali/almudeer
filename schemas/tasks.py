from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    is_completed: bool = False
    due_date: Optional[datetime] = None
    alarm_enabled: bool = False
    alarm_time: Optional[datetime] = None
    recurrence: Optional[str] = None
    sub_tasks: Optional[List[dict]] = []
    category: Optional[str] = None
    order_index: float = 0.0
    created_by: Optional[str] = None
    assigned_to: Optional[str] = None

class TaskCreate(TaskBase):
    id: str = Field(..., description="UUID from client")

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    alarm_enabled: Optional[bool] = None
    alarm_time: Optional[datetime] = None
    recurrence: Optional[str] = None
    sub_tasks: Optional[List[dict]] = None
    category: Optional[str] = None
    order_index: Optional[float] = None
    assigned_to: Optional[str] = None

class TaskResponse(TaskBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
