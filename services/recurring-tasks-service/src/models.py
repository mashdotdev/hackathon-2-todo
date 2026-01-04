"""Models for Recurring Tasks Service.

Replicates the backend models needed for recurring task processing.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import ARRAY, String


class RecurrencePatternEnum(str, Enum):
    """Recurrence patterns for recurring tasks."""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Task(SQLModel, table=True):
    """Task model for todo items."""

    __tablename__ = "tasks"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="pending")
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    priority: str = Field(default="Medium", max_length=10)
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(String)),
    )
    due_date: Optional[datetime] = Field(default=None)
    recurrence_pattern: str = Field(default="none", max_length=20)
    reminder_lead_time: Optional[int] = None


class RecurringTaskSchedule(SQLModel, table=True):
    """Tracks recurring task schedules and next execution times."""

    __tablename__ = "recurring_task_schedules"

    schedule_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    parent_task_id: str = Field(unique=True)
    user_id: str = Field(index=True)
    recurrence_pattern: str = Field(max_length=20)
    next_execution_time: datetime = Field(index=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_executed_at: Optional[datetime] = None
