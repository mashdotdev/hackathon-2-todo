"""TaskEvent model for event sourcing."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from sqlmodel import Field, SQLModel, Column, JSON


class TaskEventType(str, Enum):
    """Event types for task operations."""

    TASK_CREATED = "task-created"
    TASK_UPDATED = "task-updated"
    TASK_COMPLETED = "task-completed"
    TASK_DELETED = "task-deleted"


class TaskEvent(SQLModel, table=True):
    """Immutable event log for all task operations.

    Published to Kafka for event-driven processing by microservices.

    Attributes:
        event_id: Unique event identifier (UUID) for idempotency
        event_type: Type of event (created/updated/completed/deleted)
        task_id: ID of the task this event relates to
        user_id: ID of the user who triggered the event
        timestamp: When the event occurred (UTC)
        payload: Full task snapshot at event time (JSON)
        published_to_kafka: Whether event was successfully published
        created_at: When event record was created in database
    """

    __tablename__ = "task_events"

    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    event_type: str = Field(max_length=50, index=True)
    task_id: str = Field(index=True)
    user_id: str = Field(index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    payload: dict[str, Any] = Field(sa_column=Column(JSON))
    published_to_kafka: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
