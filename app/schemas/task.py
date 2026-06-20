from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.task import TaskStatus


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[str] = None  


class TaskRead(TaskBase):
    id: str
    status: TaskStatus
    project_id: str
    assignee_id: Optional[str] = None  
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)