"""Notification schemas for API validation.

Phase V: Notification endpoints for in-app notifications.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


NotificationTypeType = Literal["reminder", "completion", "created", "updated"]
DeliveryStatusType = Literal["sent", "read", "failed"]


class NotificationResponse(BaseModel):
    """Schema for notification response."""

    notification_id: str
    user_id: str
    task_id: Optional[str]
    notification_type: NotificationTypeType
    message: str
    sent_at: datetime
    delivery_status: DeliveryStatusType
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """Response for notification list endpoint."""

    notifications: list[NotificationResponse]
    unread_count: int
