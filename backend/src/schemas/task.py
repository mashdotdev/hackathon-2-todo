"""Task schemas for API validation."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

TaskStatusType = Literal["pending", "completed"]


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    status: TaskStatusType | None = None


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: str
    title: str
    description: str | None
    status: TaskStatusType
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
