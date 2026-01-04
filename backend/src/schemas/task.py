"""Task schemas for API validation.

Phase V: Extended with priority, tags, due_date, recurrence, and reminders.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

TaskStatusType = Literal["pending", "in_progress", "completed"]
PriorityType = Literal["High", "Medium", "Low"]
RecurrencePatternType = Literal["none", "daily", "weekly", "monthly"]


class TaskCreate(BaseModel):
    """Schema for creating a new task.

    Phase V additions: priority, tags, due_date, recurrence_pattern, reminder_lead_time
    """

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    priority: PriorityType = Field(default="Medium")
    tags: list[str] = Field(default_factory=list, max_length=10)
    due_date: datetime | None = None
    recurrence_pattern: RecurrencePatternType = Field(default="none")
    reminder_lead_time: int | None = Field(default=None, gt=0)


class TaskUpdate(BaseModel):
    """Schema for updating an existing task.

    All fields are optional for partial updates.
    """

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    status: TaskStatusType | None = None
    priority: PriorityType | None = None
    tags: list[str] | None = Field(default=None, max_length=10)
    due_date: datetime | None = None
    recurrence_pattern: RecurrencePatternType | None = None
    reminder_lead_time: int | None = None


class TaskResponse(BaseModel):
    """Schema for task response.

    Phase V: Includes all advanced task features.
    """

    id: str
    title: str
    description: str | None
    status: TaskStatusType
    priority: PriorityType
    tags: list[str]
    due_date: datetime | None
    recurrence_pattern: RecurrencePatternType
    reminder_lead_time: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListQuery(BaseModel):
    """Query parameters for listing tasks with filtering and sorting."""

    status: TaskStatusType | None = None
    priority: PriorityType | None = None
    tags: str | None = None  # Comma-separated tag names
    due_date_from: datetime | None = None
    due_date_to: datetime | None = None
    sort: Literal["priority", "due_date", "created_at"] = "created_at"
    order: Literal["asc", "desc"] = "desc"


class TaskSearchQuery(BaseModel):
    """Query parameters for full-text search."""

    q: str = Field(min_length=1, max_length=200)


class TaskListResponse(BaseModel):
    """Response for task list endpoints."""

    tasks: list[TaskResponse]
    total: int
