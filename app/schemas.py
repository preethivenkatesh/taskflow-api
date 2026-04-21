from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models import Priority, TaskStatus


# ── Users ──────────────────────────────────────────────


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Tasks ──────────────────────────────────────────────


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: Priority
    owner_id: int
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ── Comments ───────────────────────────────────────────


class CommentCreate(BaseModel):
    body: str = Field(..., min_length=1)


class CommentResponse(BaseModel):
    id: int
    body: str
    task_id: int
    author_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Analytics ──────────────────────────────────────────


class TaskAnalytics(BaseModel):
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    avg_completion_hours: Optional[float]
    tasks_by_priority: dict[str, int]
    tasks_by_status: dict[str, int]
