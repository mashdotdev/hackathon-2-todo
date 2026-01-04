"""Event publisher service for Dapr pub/sub.

Publishes task events to Kafka via Dapr sidecar for event-driven processing.
"""

import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session

from src.models.task_event import TaskEvent, TaskEventType

logger = logging.getLogger(__name__)

# Dapr configuration
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
PUBSUB_NAME = os.getenv("PUBSUB_NAME", "pubsub")
TOPIC_NAME = os.getenv("TOPIC_NAME", "task-events")


class EventPublisher:
    """Service for publishing task events to Kafka via Dapr pub/sub.

    Events are stored in the database first (outbox pattern), then published
    to Kafka. This ensures durability and at-least-once delivery semantics.
    """

    def __init__(self, db: Session) -> None:
        """Initialize the event publisher with database session."""
        self.db = db
        self._dapr_client = None

    async def publish_task_created(
        self,
        task_id: str,
        user_id: str,
        payload: dict[str, Any],
    ) -> TaskEvent:
        """Publish a task-created event.

        Args:
            task_id: ID of the created task
            user_id: ID of the user who created the task
            payload: Task data snapshot

        Returns:
            The created TaskEvent record
        """
        return await self._publish_event(
            event_type=TaskEventType.TASK_CREATED,
            task_id=task_id,
            user_id=user_id,
            payload=payload,
        )

    async def publish_task_updated(
        self,
        task_id: str,
        user_id: str,
        payload: dict[str, Any],
    ) -> TaskEvent:
        """Publish a task-updated event.

        Args:
            task_id: ID of the updated task
            user_id: ID of the user who updated the task
            payload: Task data snapshot with changes

        Returns:
            The created TaskEvent record
        """
        return await self._publish_event(
            event_type=TaskEventType.TASK_UPDATED,
            task_id=task_id,
            user_id=user_id,
            payload=payload,
        )

    async def publish_task_completed(
        self,
        task_id: str,
        user_id: str,
        payload: dict[str, Any],
    ) -> TaskEvent:
        """Publish a task-completed event.

        Args:
            task_id: ID of the completed task
            user_id: ID of the user who completed the task
            payload: Task data snapshot

        Returns:
            The created TaskEvent record
        """
        return await self._publish_event(
            event_type=TaskEventType.TASK_COMPLETED,
            task_id=task_id,
            user_id=user_id,
            payload=payload,
        )

    async def publish_task_deleted(
        self,
        task_id: str,
        user_id: str,
        payload: dict[str, Any],
    ) -> TaskEvent:
        """Publish a task-deleted event.

        Args:
            task_id: ID of the deleted task
            user_id: ID of the user who deleted the task
            payload: Last known task state

        Returns:
            The created TaskEvent record
        """
        return await self._publish_event(
            event_type=TaskEventType.TASK_DELETED,
            task_id=task_id,
            user_id=user_id,
            payload=payload,
        )

    async def _publish_event(
        self,
        event_type: TaskEventType,
        task_id: str,
        user_id: str,
        payload: dict[str, Any],
    ) -> TaskEvent:
        """Internal method to create and publish an event.

        1. Create event record in database (outbox pattern)
        2. Attempt to publish to Kafka via Dapr
        3. Update published_to_kafka flag on success

        Args:
            event_type: Type of the event
            task_id: ID of the related task
            user_id: ID of the user
            payload: Event payload data

        Returns:
            The TaskEvent record (with published_to_kafka status)
        """
        event = TaskEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type.value,
            task_id=task_id,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            payload=payload,
            published_to_kafka=False,
        )

        # Store event in database first (outbox pattern)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        # Attempt to publish to Dapr
        try:
            published = await self._publish_to_dapr(event)
            if published:
                event.published_to_kafka = True
                self.db.add(event)
                self.db.commit()
                logger.info(
                    f"Published event {event.event_id} to {TOPIC_NAME}",
                    extra={"event_type": event_type.value, "task_id": task_id},
                )
        except Exception as e:
            logger.error(
                f"Failed to publish event {event.event_id}: {e}",
                extra={"event_type": event_type.value, "task_id": task_id},
            )
            # Event is still in database, will be retried by outbox processor

        return event

    async def _publish_to_dapr(self, event: TaskEvent) -> bool:
        """Publish event to Kafka via Dapr HTTP API with partitioning.

        Uses the Dapr sidecar HTTP endpoint for pub/sub.
        T059: Partitions messages by task_id to ensure ordering per task.

        Args:
            event: The TaskEvent to publish

        Returns:
            True if published successfully, False otherwise
        """
        try:
            import httpx

            dapr_url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{TOPIC_NAME}"

            event_data = {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "task_id": event.task_id,
                "user_id": event.user_id,
                "timestamp": event.timestamp.isoformat(),
                "payload": event.payload,
            }

            # T059: Add partition key metadata for Kafka
            # Dapr uses rawPayload=true and partitionKey for Kafka partitioning
            headers = {
                "Content-Type": "application/json",
                # Dapr Kafka binding uses this header for partition key
                "partitionKey": event.task_id,
            }

            # Add Dapr metadata for raw payload and partition key
            metadata = {
                "partitionKey": event.task_id,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    dapr_url,
                    json=event_data,
                    headers=headers,
                    params={"metadata.partitionKey": event.task_id},
                    timeout=5.0,
                )
                return response.status_code in (200, 204)

        except Exception as e:
            logger.warning(f"Dapr publish failed (may not be running): {e}")
            return False


def get_event_publisher(db: Session) -> EventPublisher:
    """Factory function to create EventPublisher instance."""
    return EventPublisher(db)
