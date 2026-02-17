from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    is_completed: bool = False
    due_date: Optional[datetime] = None
    priority: str = Field("medium", pattern="^(low|medium|high)$")
    color: Optional[int] = None
    sub_tasks: Optional[list[str]] = []
    alarm_enabled: bool = False
    alarm_time: Optional[datetime] = None

class TaskCreate(TaskBase):
    id: str = Field(..., description="UUID from client")

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    color: Optional[int] = None
    sub_tasks: Optional[list[str]] = None

class TaskResponse(TaskBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
