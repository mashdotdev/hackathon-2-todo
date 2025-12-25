"""Task model for database storage."""

import uuid
from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class TaskStatus(str, Enum):
    """Task completion status."""

    PENDING = "pending"
    COMPLETED = "completed"


class Task(SQLModel, table=True):
    """Task model for todo items.

    Attributes:
        id: Unique identifier (UUID)
        title: Task title (required, 1-200 chars)
        description: Optional task description (max 1000 chars)
        status: Current status (pending/completed)
        user_id: Owner user ID (foreign key)
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last updated
    """

    __tablename__ = "tasks"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == TaskStatus.COMPLETED
