"""Notification model for database storage.

Replicates the backend Notification model for use in the microservice.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class NotificationType(str, Enum):
    """Types of notifications."""

    REMINDER = "reminder"
    TASK_COMPLETED = "completion"
    TASK_CREATED = "created"
    TASK_UPDATED = "updated"


class DeliveryStatus(str, Enum):
    """Notification delivery status."""

    SENT = "sent"
    READ = "read"
    FAILED = "failed"


class Notification(SQLModel, table=True):
    """In-app notifications for task reminders and events."""

    __tablename__ = "notifications"

    notification_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    user_id: str = Field(index=True)
    task_id: Optional[str] = Field(default=None)
    notification_type: str = Field(max_length=50)
    message: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    delivery_status: str = Field(default="sent", max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProcessedEvent(SQLModel, table=True):
    """Track processed events for idempotency."""

    __tablename__ = "processed_events"

    event_id: str = Field(primary_key=True)
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    event_type: str = Field(max_length=50)
