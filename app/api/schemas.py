from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.task import TaskStatus


class TaskResponse(BaseModel):
    id: int
    status: TaskStatus
    original_path: str
    result_path: Optional[str] = None
    task_metadata: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskStatusResponse(BaseModel):
    id: int
    status: TaskStatus
    result_path: Optional[str] = None
    task_metadata: Optional[str] = None


class NewTaskResponse(BaseModel):
    task_id: int
    message: str


class WebhookPayload(BaseModel):
    task_id: int
    status: TaskStatus
    result_path: Optional[str] = None
    task_metadata: Optional[str] = None
