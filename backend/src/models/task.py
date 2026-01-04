"""Task model for database storage."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import ARRAY, String


class TaskStatus(str, Enum):
    """Task completion status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class PriorityEnum(str, Enum):
    """Task priority levels."""

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class RecurrencePatternEnum(str, Enum):
    """Recurrence patterns for recurring tasks."""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Task(SQLModel, table=True):
    """Task model for todo items.

    Extended in Phase V with advanced features: priorities, tags,
    due dates, recurring tasks, and reminders.

    Attributes:
        id: Unique identifier (UUID)
        title: Task title (required, 1-200 chars)
        description: Optional task description (max 1000 chars)
        status: Current status (pending/in_progress/completed)
        user_id: Owner user ID (foreign key)
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last updated

        Phase V additions:
        priority: Task priority (High/Medium/Low)
        tags: Array of tags for categorization
        due_date: Optional due date/time
        recurrence_pattern: How often task repeats (none/daily/weekly/monthly)
        reminder_lead_time: Minutes before due_date to send reminder
    """

    __tablename__ = "tasks"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    status: str = Field(default="pending")
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Phase V: Advanced features
    priority: str = Field(default="Medium", max_length=10, index=True)
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(String)),
    )
    due_date: Optional[datetime] = Field(default=None, index=True)
    recurrence_pattern: str = Field(default="none", max_length=20)
    reminder_lead_time: Optional[int] = None  # minutes before due_date

    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == "completed"
