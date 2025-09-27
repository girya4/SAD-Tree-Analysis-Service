from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.task import TaskStatus, TreeType, DamageType


class DamageAnalysis(BaseModel):
    type: str
    confidence: float
    severity: str
    description: str
    recommendations: List[str]


class MLAnalysisResults(BaseModel):
    tree_type: str
    tree_type_confidence: float
    damages_detected: List[DamageAnalysis]
    overall_health_score: float
    processing_time: float
    ml_model_version: str


class TaskResponse(BaseModel):
    id: int
    status: TaskStatus
    original_path: str
    result_path: Optional[str] = None
    task_metadata: Optional[str] = None
    
    # ML Analysis Results
    tree_type: Optional[str] = None
    tree_type_confidence: Optional[float] = None
    damages_detected: Optional[str] = None  # JSON string
    overall_health_score: Optional[float] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskStatusResponse(BaseModel):
    id: int
    status: TaskStatus
    result_path: Optional[str] = None
    task_metadata: Optional[str] = None
    
    # ML Analysis Results
    tree_type: Optional[str] = None
    tree_type_confidence: Optional[float] = None
    damages_detected: Optional[str] = None  # JSON string
    overall_health_score: Optional[float] = None


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    page: int
    per_page: int


class NewTaskResponse(BaseModel):
    task_id: int
    message: str


class NewTasksResponse(BaseModel):
    task_ids: List[int]
    message: str


class WebhookPayload(BaseModel):
    task_id: int
    status: TaskStatus
    result_path: Optional[str] = None
    task_metadata: Optional[str] = None
    
    # ML Analysis Results
    tree_type: Optional[str] = None
    tree_type_confidence: Optional[float] = None
    damages_detected: Optional[str] = None
    overall_health_score: Optional[float] = None
