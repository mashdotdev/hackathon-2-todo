"""Task management routes.

Phase V: Extended with advanced filtering, sorting, search, PATCH endpoints,
and event publishing via Dapr pub/sub.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlmodel import Session

from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.schemas.task import (
    TaskCreate,
    TaskResponse,
    TaskUpdate,
    TaskListQuery,
    TaskListResponse,
)
from src.services.event_publisher import EventPublisher
from src.services.task_service import TaskService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = Query(None),
    tags: Optional[str] = Query(None, description="Comma-separated tag names"),
    due_date_from: Optional[datetime] = Query(None),
    due_date_to: Optional[datetime] = Query(None),
    sort: str = Query("created_at", regex="^(priority|due_date|created_at)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskListResponse:
    """List all tasks for the current user with optional filtering and sorting.

    T038: Extended with query parameters for priority, tags, due_date range, sort, order.
    """
    task_service = TaskService(db)

    # Build query object from parameters
    query = TaskListQuery(
        status=status_filter,
        priority=priority,
        tags=tags,
        due_date_from=due_date_from,
        due_date_to=due_date_to,
        sort=sort,
        order=order,
    )

    tasks = task_service.list_tasks(current_user.id, query=query)
    return TaskListResponse(tasks=tasks, total=len(tasks))


@router.get("/search", response_model=TaskListResponse)
async def search_tasks(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskListResponse:
    """Search tasks by title and description using full-text search.

    T041: Full-text search endpoint using PostgreSQL ILIKE.
    """
    task_service = TaskService(db)
    tasks = task_service.search_tasks(current_user.id, q)
    return TaskListResponse(tasks=tasks, total=len(tasks))


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """Create a new task with Phase V features.

    T036-T037: Extended to accept priority, tags, due_date, recurrence_pattern,
    reminder_lead_time with validation.
    T056: Publishes task-created event to Kafka via Dapr.
    """
    try:
        task_service = TaskService(db)
        task = task_service.create_task(current_user.id, task_data)

        # T056: Publish task-created event (async, non-blocking)
        async def publish_event():
            try:
                publisher = EventPublisher(db)
                await publisher.publish_task_created(
                    task_id=task.id,
                    user_id=current_user.id,
                    payload=task.model_dump(mode="json"),
                )
            except Exception as e:
                logger.error(f"Failed to publish task-created event: {e}")

        background_tasks.add_task(publish_event)
        return task

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """Get a specific task by ID."""
    task_service = TaskService(db)
    task = task_service.get_task(task_id, current_user.id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """Update a task.

    T057: Publishes task-updated or task-completed event to Kafka via Dapr.
    """
    task_service = TaskService(db)

    # Get original task to detect status changes
    original = task_service.get_task(task_id, current_user.id)
    if original is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    task = task_service.update_task(task_id, current_user.id, task_data)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # T057: Publish appropriate event based on status change
    async def publish_event():
        try:
            publisher = EventPublisher(db)
            payload = task.model_dump(mode="json")

            # If status changed to completed, publish task-completed event
            if task_data.status == "completed" and original.status != "completed":
                await publisher.publish_task_completed(
                    task_id=task.id,
                    user_id=current_user.id,
                    payload=payload,
                )
            else:
                await publisher.publish_task_updated(
                    task_id=task.id,
                    user_id=current_user.id,
                    payload=payload,
                )
        except Exception as e:
            logger.error(f"Failed to publish task-updated event: {e}")

    background_tasks.add_task(publish_event)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def patch_task(
    task_id: str,
    task_data: TaskUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """Partial update for a task.

    T042: PATCH endpoint for partial updates - supports updating any task field
    including priority, tags, due_date, status, etc.
    T057: Publishes task-updated or task-completed event to Kafka via Dapr.
    """
    task_service = TaskService(db)

    # Get original task to detect status changes
    original = task_service.get_task(task_id, current_user.id)
    if original is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    task = task_service.update_task(task_id, current_user.id, task_data)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # T057: Publish appropriate event based on status change
    async def publish_event():
        try:
            publisher = EventPublisher(db)
            payload = task.model_dump(mode="json")

            if task_data.status == "completed" and original.status != "completed":
                await publisher.publish_task_completed(
                    task_id=task.id,
                    user_id=current_user.id,
                    payload=payload,
                )
            else:
                await publisher.publish_task_updated(
                    task_id=task.id,
                    user_id=current_user.id,
                    payload=payload,
                )
        except Exception as e:
            logger.error(f"Failed to publish task-updated event: {e}")

    background_tasks.add_task(publish_event)
    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Delete a task.

    T058: Publishes task-deleted event to Kafka via Dapr before deletion.
    """
    task_service = TaskService(db)

    # Get task data before deletion for the event payload
    task = task_service.get_task(task_id, current_user.id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Store task data for event before deletion
    task_payload = task.model_dump(mode="json")

    success = task_service.delete_task(task_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # T058: Publish task-deleted event
    async def publish_event():
        try:
            publisher = EventPublisher(db)
            await publisher.publish_task_deleted(
                task_id=task_id,
                user_id=current_user.id,
                payload=task_payload,
            )
        except Exception as e:
            logger.error(f"Failed to publish task-deleted event: {e}")

    background_tasks.add_task(publish_event)
    return {"message": "Task deleted successfully"}


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_complete(
    task_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """Toggle task completion status.

    T057: Publishes task-completed or task-updated event depending on new status.
    """
    task_service = TaskService(db)

    # Get original status
    original = task_service.get_task(task_id, current_user.id)
    if original is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    task = task_service.toggle_complete(task_id, current_user.id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Publish event based on new status
    async def publish_event():
        try:
            publisher = EventPublisher(db)
            payload = task.model_dump(mode="json")

            if task.status == "completed":
                await publisher.publish_task_completed(
                    task_id=task.id,
                    user_id=current_user.id,
                    payload=payload,
                )
            else:
                await publisher.publish_task_updated(
                    task_id=task.id,
                    user_id=current_user.id,
                    payload=payload,
                )
        except Exception as e:
            logger.error(f"Failed to publish task completion event: {e}")

    background_tasks.add_task(publish_event)
    return task
