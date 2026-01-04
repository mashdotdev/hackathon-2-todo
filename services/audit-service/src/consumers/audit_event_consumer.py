"""Audit event consumer for the Audit Service.

T075: Kafka consumer that creates audit log entries in the database.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session

from ..models import AuditLog

logger = logging.getLogger(__name__)


class AuditEventConsumer:
    """Consumer for all events from Kafka via Dapr.

    Creates audit log entries for every event received.
    """

    def __init__(self, db: Session) -> None:
        """Initialize consumer with database session."""
        self.db = db

    def process_event(
        self,
        event_data: dict[str, Any],
        event_category: str,
    ) -> dict[str, Any]:
        """Process an event and create an audit log entry.

        T075: Saves audit log entry to database.

        Args:
            event_data: Event data from Dapr
            event_category: Category of event (task/reminder/update)

        Returns:
            Processing result
        """
        # Extract event details
        data = event_data.get("data", event_data)
        event_id = data.get("event_id", str(uuid.uuid4()))
        event_type = data.get("event_type", "unknown")
        task_id = data.get("task_id", "")
        user_id = data.get("user_id", "")
        timestamp_str = data.get("timestamp")
        payload = data.get("payload", {})

        # Parse timestamp
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            except ValueError:
                timestamp = datetime.utcnow()
        else:
            timestamp = datetime.utcnow()

        # Determine action type
        action_type = self._get_action_type(event_type)

        # Create audit log entry
        audit_log = AuditLog(
            audit_id=str(uuid.uuid4()),
            user_id=user_id,
            action_type=action_type,
            resource_type="task",
            resource_id=task_id,
            event_data={
                "event_id": event_id,
                "event_type": event_type,
                "category": event_category,
                "payload": payload,
            },
            correlation_id=event_id,
            timestamp=timestamp,
        )

        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)

        logger.info(
            f"Audit log created: {action_type} on task {task_id} by user {user_id}",
            extra={"audit_id": audit_log.audit_id},
        )

        return {
            "success": True,
            "audit_id": audit_log.audit_id,
            "action_type": action_type,
        }

    def _get_action_type(self, event_type: str) -> str:
        """Map event type to action type for audit logging."""
        mapping = {
            "task-created": "create",
            "task-updated": "update",
            "task-completed": "complete",
            "task-deleted": "delete",
            "reminder-scheduled": "schedule",
            "reminder-triggered": "trigger",
        }
        return mapping.get(event_type, "unknown")
