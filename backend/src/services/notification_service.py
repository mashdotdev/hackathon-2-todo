"""Notification service for managing in-app notifications.

Creates and manages notifications for task events and reminders.
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from src.models.notification import DeliveryStatus, Notification, NotificationType


class NotificationService:
    """Service for managing notifications.

    Provides methods for creating, listing, and updating notifications.
    """

    def __init__(self, db: Session) -> None:
        """Initialize notification service with database session."""
        self.db = db

    def create_notification(
        self,
        user_id: str,
        notification_type: NotificationType | str,
        message: str,
        task_id: Optional[str] = None,
    ) -> Notification:
        """Create a new notification.

        Args:
            user_id: User to notify
            notification_type: Type of notification
            message: Notification message
            task_id: Optional related task ID

        Returns:
            The created Notification
        """
        if isinstance(notification_type, NotificationType):
            notification_type = notification_type.value

        notification = Notification(
            user_id=user_id,
            task_id=task_id,
            notification_type=notification_type,
            message=message,
            sent_at=datetime.utcnow(),
            delivery_status=DeliveryStatus.SENT.value,
        )

        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
    ) -> tuple[list[Notification], int]:
        """Get notifications for a user.

        Args:
            user_id: User ID
            unread_only: Filter to unread only
            limit: Maximum number to return

        Returns:
            Tuple of (notifications list, unread count)
        """
        statement = select(Notification).where(Notification.user_id == user_id)

        if unread_only:
            statement = statement.where(
                Notification.delivery_status == DeliveryStatus.SENT.value
            )

        statement = statement.order_by(Notification.sent_at.desc()).limit(limit)
        notifications = list(self.db.exec(statement).all())

        # Get unread count
        unread_stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.delivery_status == DeliveryStatus.SENT.value)
        )
        unread_count = len(list(self.db.exec(unread_stmt).all()))

        return notifications, unread_count

    def mark_as_read(
        self,
        notification_id: str,
        user_id: str,
    ) -> Optional[Notification]:
        """Mark a notification as read.

        Args:
            notification_id: Notification ID
            user_id: Owner user ID

        Returns:
            Updated notification or None if not found
        """
        statement = select(Notification).where(
            Notification.notification_id == notification_id,
            Notification.user_id == user_id,
        )
        notification = self.db.exec(statement).first()

        if notification is None:
            return None

        notification.delivery_status = DeliveryStatus.READ.value
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def create_task_notification(
        self,
        user_id: str,
        task_id: str,
        task_title: str,
        event_type: str,
    ) -> Notification:
        """Create a notification for a task event.

        Args:
            user_id: User to notify
            task_id: Related task ID
            task_title: Task title for message
            event_type: Type of task event

        Returns:
            The created Notification
        """
        messages = {
            "task-created": f"New task created: {task_title}",
            "task-updated": f"Task updated: {task_title}",
            "task-completed": f"Task completed: {task_title}",
            "task-deleted": f"Task deleted: {task_title}",
        }

        notification_types = {
            "task-created": NotificationType.TASK_CREATED,
            "task-updated": NotificationType.TASK_UPDATED,
            "task-completed": NotificationType.TASK_COMPLETED,
        }

        message = messages.get(event_type, f"Task event: {task_title}")
        notification_type = notification_types.get(
            event_type, NotificationType.TASK_UPDATED
        )

        return self.create_notification(
            user_id=user_id,
            notification_type=notification_type,
            message=message,
            task_id=task_id,
        )

    def create_reminder_notification(
        self,
        user_id: str,
        task_id: str,
        task_title: str,
        due_date: datetime,
        lead_time_minutes: int,
    ) -> Notification:
        """Create a reminder notification for an upcoming task.

        Args:
            user_id: User to notify
            task_id: Related task ID
            task_title: Task title
            due_date: Task due date
            lead_time_minutes: Minutes before due date

        Returns:
            The created Notification
        """
        if lead_time_minutes >= 60:
            time_str = f"{lead_time_minutes // 60} hour(s)"
        else:
            time_str = f"{lead_time_minutes} minute(s)"

        message = f"Reminder: '{task_title}' is due in {time_str}"

        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.REMINDER,
            message=message,
            task_id=task_id,
        )


def get_notification_service(db: Session) -> NotificationService:
    """Factory function to create NotificationService instance."""
    return NotificationService(db)
