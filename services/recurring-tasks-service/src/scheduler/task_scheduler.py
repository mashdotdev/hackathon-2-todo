"""Task scheduler for processing recurring task schedules.

T069-T071: Implements recurring task instance generation.
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Any

import httpx
from dateutil.relativedelta import relativedelta
from sqlmodel import Session, select

from ..models import RecurringTaskSchedule, Task

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
PUBSUB_NAME = os.getenv("PUBSUB_NAME", "pubsub")
TOPIC_NAME = os.getenv("TOPIC_NAME", "task-events")


def calculate_next_execution(current: datetime, pattern: str) -> datetime:
    """Calculate the next execution time based on recurrence pattern.

    Args:
        current: The current datetime
        pattern: Recurrence pattern (daily/weekly/monthly)

    Returns:
        The next execution datetime
    """
    if pattern == "daily":
        return current + relativedelta(days=1)
    elif pattern == "weekly":
        return current + relativedelta(weeks=1)
    elif pattern == "monthly":
        return current + relativedelta(months=1)
    else:
        raise ValueError(f"Invalid recurrence pattern: {pattern}")


class TaskScheduler:
    """Scheduler for processing due recurring task schedules.

    Queries for due schedules, generates new task instances, and updates schedules.
    """

    def __init__(self, db: Session) -> None:
        """Initialize scheduler with database session."""
        self.db = db

    async def process_due_schedules(self) -> dict[str, Any]:
        """Process all due recurring task schedules.

        T069: Query RecurringTaskSchedule where next_execution_time <= now()
        T070: Generate new task instances and publish events
        T071: Update schedule with next_execution_time

        Returns:
            Processing result summary
        """
        now = datetime.utcnow()
        logger.info(f"Processing due schedules at {now.isoformat()}")

        # T069: Query for due schedules
        statement = (
            select(RecurringTaskSchedule)
            .where(RecurringTaskSchedule.next_execution_time <= now)
            .where(RecurringTaskSchedule.is_active == True)
        )
        due_schedules = list(self.db.exec(statement).all())

        logger.info(f"Found {len(due_schedules)} due schedules")

        processed = 0
        errors = 0

        for schedule in due_schedules:
            try:
                await self._process_schedule(schedule, now)
                processed += 1
            except Exception as e:
                logger.error(
                    f"Error processing schedule {schedule.schedule_id}: {e}"
                )
                errors += 1

        return {
            "processed": processed,
            "errors": errors,
            "timestamp": now.isoformat(),
        }

    async def _process_schedule(
        self,
        schedule: RecurringTaskSchedule,
        now: datetime,
    ) -> None:
        """Process a single recurring task schedule.

        Args:
            schedule: The schedule to process
            now: Current timestamp
        """
        # Get parent task
        parent_task = self.db.exec(
            select(Task).where(Task.id == schedule.parent_task_id)
        ).first()

        if parent_task is None:
            logger.warning(
                f"Parent task {schedule.parent_task_id} not found, "
                f"deactivating schedule {schedule.schedule_id}"
            )
            schedule.is_active = False
            self.db.add(schedule)
            self.db.commit()
            return

        # T070: Generate new task instance
        new_task = self._create_task_instance(parent_task, schedule)

        # T070: Publish task-created event via Dapr
        await self._publish_task_created(new_task)

        # T071: Update schedule
        schedule.last_executed_at = now
        schedule.next_execution_time = calculate_next_execution(
            now, schedule.recurrence_pattern
        )
        self.db.add(schedule)
        self.db.commit()

        logger.info(
            f"Created task instance {new_task.id} from schedule {schedule.schedule_id}, "
            f"next execution at {schedule.next_execution_time.isoformat()}"
        )

    def _create_task_instance(
        self,
        parent_task: Task,
        schedule: RecurringTaskSchedule,
    ) -> Task:
        """Create a new task instance from parent task.

        T070: Copy parent task and update due_date based on pattern.

        Args:
            parent_task: The parent/template task
            schedule: The recurring schedule

        Returns:
            Created Task instance
        """
        # Calculate new due date based on pattern
        new_due_date = None
        if parent_task.due_date:
            new_due_date = calculate_next_execution(
                parent_task.due_date, schedule.recurrence_pattern
            )

        new_task = Task(
            id=str(uuid.uuid4()),
            title=parent_task.title,
            description=parent_task.description,
            status="pending",
            user_id=parent_task.user_id,
            priority=parent_task.priority,
            tags=parent_task.tags.copy() if parent_task.tags else [],
            due_date=new_due_date or schedule.next_execution_time,
            recurrence_pattern="none",  # Instance is not recurring
            reminder_lead_time=parent_task.reminder_lead_time,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)

        return new_task

    async def _publish_task_created(self, task: Task) -> bool:
        """Publish task-created event via Dapr.

        Args:
            task: The created task

        Returns:
            True if published successfully
        """
        try:
            dapr_url = (
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/"
                f"{PUBSUB_NAME}/{TOPIC_NAME}"
            )

            event_data = {
                "event_id": str(uuid.uuid4()),
                "event_type": "task-created",
                "task_id": task.id,
                "user_id": task.user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "payload": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "tags": task.tags,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "recurrence_pattern": task.recurrence_pattern,
                    "created_at": task.created_at.isoformat(),
                },
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    dapr_url,
                    json=event_data,
                    headers={
                        "Content-Type": "application/json",
                        "partitionKey": task.id,
                    },
                    params={"metadata.partitionKey": task.id},
                    timeout=5.0,
                )
                return response.status_code in (200, 204)

        except Exception as e:
            logger.warning(f"Failed to publish task-created event: {e}")
            return False

    def get_due_schedules_count(self) -> int:
        """Get count of due schedules for monitoring."""
        now = datetime.utcnow()
        statement = (
            select(RecurringTaskSchedule)
            .where(RecurringTaskSchedule.next_execution_time <= now)
            .where(RecurringTaskSchedule.is_active == True)
        )
        return len(list(self.db.exec(statement).all()))
