"""Task model for in-memory storage."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """Task completion status."""

    PENDING = "pending"
    COMPLETED = "completed"


@dataclass
class Task:
    """Represents a todo task.

    Attributes:
        id: Unique identifier for the task
        title: Task title (required, 1-200 chars)
        description: Optional task description (max 1000 chars)
        status: Current status (pending/completed)
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last updated
    """

    title: str
    description: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate task data after initialization."""
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Task title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")
        if self.description and len(self.description) > 1000:
            raise ValueError("Task description cannot exceed 1000 characters")
        self.title = self.title.strip()
        if self.description:
            self.description = self.description.strip()

    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == TaskStatus.COMPLETED

    def mark_complete(self) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.updated_at = datetime.now()

    def mark_incomplete(self) -> None:
        """Mark task as pending/incomplete."""
        self.status = TaskStatus.PENDING
        self.updated_at = datetime.now()

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
    ) -> None:
        """Update task details.

        Args:
            title: New title (optional)
            description: New description (optional)
        """
        if title is not None:
            if len(title.strip()) == 0:
                raise ValueError("Task title cannot be empty")
            if len(title) > 200:
                raise ValueError("Task title cannot exceed 200 characters")
            self.title = title.strip()
        if description is not None:
            if len(description) > 1000:
                raise ValueError("Task description cannot exceed 1000 characters")
            self.description = description.strip() if description else None
        self.updated_at = datetime.now()

    def to_dict(self) -> dict[str, str | None]:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
