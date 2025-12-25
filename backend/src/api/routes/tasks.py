"""Task management routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from src.services.task_service import TaskService

router = APIRouter()


@router.get("", response_model=dict[str, list[TaskResponse] | int])
async def list_tasks(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, list[TaskResponse] | int]:
    """List all tasks for the current user."""
    task_service = TaskService(db)
    tasks = task_service.list_tasks(current_user.id, status_filter)
    return {"tasks": tasks, "total": len(tasks)}


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """Create a new task."""
    task_service = TaskService(db)
    return task_service.create_task(current_user.id, task_data)


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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """Update a task."""
    task_service = TaskService(db)
    task = task_service.update_task(task_id, current_user.id, task_data)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Delete a task."""
    task_service = TaskService(db)
    success = task_service.delete_task(task_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return {"message": "Task deleted successfully"}


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_complete(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """Toggle task completion status."""
    task_service = TaskService(db)
    task = task_service.toggle_complete(task_id, current_user.id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task
