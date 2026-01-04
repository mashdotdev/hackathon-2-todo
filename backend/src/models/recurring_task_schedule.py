"""RecurringTaskSchedule model for managing recurring tasks."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class RecurrencePatternEnum(str, Enum):
    """Recurrence patterns for recurring tasks."""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class RecurringTaskSchedule(SQLModel, table=True):
    """Tracks recurring task schedules and next execution times.

    Used by the Recurring Tasks microservice to generate new task instances
    automatically based on the recurrence pattern.

    Attributes:
        schedule_id: Unique identifier (UUID)
        parent_task_id: ID of the parent task template (foreign key)
        user_id: Owner user ID
        recurrence_pattern: How often to repeat (daily/weekly/monthly)
        next_execution_time: When to create the next instance
        is_active: Whether schedule is currently active
        created_at: When schedule was created
        last_executed_at: When last instance was created
    """

    __tablename__ = "recurring_task_schedules"

    schedule_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    parent_task_id: str = Field(
        foreign_key="tasks.id",
        unique=True,
    )
    user_id: str = Field(index=True)
    recurrence_pattern: str = Field(max_length=20)
    next_execution_time: datetime = Field(index=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_executed_at: Optional[datetime] = None
