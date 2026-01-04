"""Task event consumer for notification service.

T062-T064: Kafka consumer via Dapr with idempotency and notification creation.
"""

import logging
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from ..models import DeliveryStatus, Notification, NotificationType, ProcessedEvent

logger = logging.getLogger(__name__)


class TaskEventConsumer:
    """Consumer for task events from Kafka via Dapr.

    Creates notifications for task-created and task-completed events.
    Implements idempotency using ProcessedEvent table.
    """

    def __init__(self, db: Session) -> None:
        """Initialize consumer with database session."""
        self.db = db

    def is_event_processed(self, event_id: str) -> bool:
        """Check if event has already been processed.

        T064: Idempotency check to prevent duplicate notifications.
        """
        statement = select(ProcessedEvent).where(ProcessedEvent.event_id == event_id)
        result = self.db.exec(statement).first()
        return result is not None

    def mark_event_processed(self, event_id: str, event_type: str) -> None:
        """Mark event as processed for idempotency."""
        processed = ProcessedEvent(
            event_id=event_id,
            event_type=event_type,
            processed_at=datetime.utcnow(),
        )
        self.db.add(processed)
        self.db.commit()

    def process_event(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Process a task event and create notification.

        T063: Event handler creates Notification record in database.

        Args:
            event_data: Event data from Dapr

        Returns:
            Processing result
        """
        # Extract event details
        data = event_data.get("data", event_data)
        event_id = data.get("event_id", "")
        event_type = data.get("event_type", "")
        task_id = data.get("task_id", "")
        user_id = data.get("user_id", "")
        payload = data.get("payload", {})

        logger.info(
            f"Processing event {event_id}: {event_type}",
            extra={"event_id": event_id, "event_type": event_type},
        )

        # T064: Idempotency check
        if self.is_event_processed(event_id):
            logger.info(f"Event {event_id} already processed, skipping")
            return {"success": True, "skipped": True, "reason": "already_processed"}

        # Only create notifications for specific event types
        if event_type not in ("task-created", "task-completed"):
            logger.debug(f"Skipping notification for event type: {event_type}")
            return {"success": True, "skipped": True, "reason": "event_type_not_tracked"}

        # T063: Create Notification record
        task_title = payload.get("title", "Unknown task")
        notification = self._create_notification(
            user_id=user_id,
            task_id=task_id,
            event_type=event_type,
            task_title=task_title,
        )

        # Mark event as processed
        self.mark_event_processed(event_id, event_type)

        logger.info(
            f"Created notification {notification.notification_id} for user {user_id}",
            extra={"notification_id": notification.notification_id},
        )

        return {
            "success": True,
            "notification_id": notification.notification_id,
            "message": notification.message,
        }

    def _create_notification(
        self,
        user_id: str,
        task_id: str,
        event_type: str,
        task_title: str,
    ) -> Notification:
        """Create notification record in database.

        Args:
            user_id: User to notify
            task_id: Related task ID
            event_type: Type of task event
            task_title: Task title for message

        Returns:
            Created Notification
        """
        # Map event type to notification type
        notification_types = {
            "task-created": NotificationType.TASK_CREATED,
            "task-completed": NotificationType.TASK_COMPLETED,
            "task-updated": NotificationType.TASK_UPDATED,
        }

        # Generate notification message
        messages = {
            "task-created": f"New task created: {task_title}",
            "task-completed": f"Task completed: {task_title}",
            "task-updated": f"Task updated: {task_title}",
        }

        notification_type = notification_types.get(
            event_type, NotificationType.TASK_UPDATED
        )
        message = messages.get(event_type, f"Task event: {task_title}")

        notification = Notification(
            user_id=user_id,
            task_id=task_id,
            notification_type=notification_type.value,
            message=message,
            sent_at=datetime.utcnow(),
            delivery_status=DeliveryStatus.SENT.value,
        )

        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        return notification
