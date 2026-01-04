"""Notification model for in-app notifications."""

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
    """In-app notifications for task reminders and events.

    Created by the Notification microservice when consuming Kafka events.

    Attributes:
        notification_id: Unique identifier (UUID)
        user_id: User who should receive the notification
        task_id: Related task ID (optional, can be None)
        notification_type: Type of notification
        message: Notification message text
        sent_at: When notification was sent
        delivery_status: Current delivery status (sent/read/failed)
        created_at: When notification record was created
    """

    __tablename__ = "notifications"

    notification_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    user_id: str = Field(foreign_key="users.id", index=True)
    task_id: Optional[str] = Field(default=None, foreign_key="tasks.id")
    notification_type: str = Field(max_length=50)
    message: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    delivery_status: str = Field(default="sent", max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
