"""MCP Tool: complete_task - Mark a task as completed."""

from sqlmodel import Session, select

from src.core.database import engine
from src.mcp.server import mcp
from src.models.task import Task
from src.schemas.task import TaskUpdate
from src.services.task_service import TaskService


def fuzzy_match_task(db: Session, user_id: str, task_title: str) -> list[Task]:
    """Find tasks matching a title using fuzzy matching.

    Returns list of matching tasks (exact match first, then contains match).
    """
    # First try exact match (case-insensitive)
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.title.ilike(task_title),
    )
    exact_matches = list(db.exec(statement).all())
    if exact_matches:
        return exact_matches

    # Then try contains match
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.title.ilike(f"%{task_title}%"),
    )
    return list(db.exec(statement).all())


@mcp.tool()
def complete_task(user_id: str, task_id: str = "", task_title: str = "") -> dict:
    """Mark a task as completed.

    Args:
        user_id: The authenticated user's ID (UUID)
        task_id: The task ID to complete (optional if task_title provided)
        task_title: Task title for fuzzy matching (optional if task_id provided)

    Returns:
        dict with success status, completed task details, and message
    """
    if not user_id:
        return {
            "success": False,
            "task": None,
            "message": "User ID is required",
            "error": "VALIDATION_ERROR",
        }

    if not task_id and not task_title:
        return {
            "success": False,
            "task": None,
            "message": "Either task_id or task_title is required",
            "error": "VALIDATION_ERROR",
        }

    with Session(engine) as db:
        task_service = TaskService(db)

        # If task_id is provided, use it directly
        if task_id:
            task = task_service.get_task(task_id, user_id)
            if not task:
                return {
                    "success": False,
                    "task": None,
                    "message": f"Task with ID '{task_id}' not found",
                    "error": "TASK_NOT_FOUND",
                }
        else:
            # Use fuzzy matching on title
            matches = fuzzy_match_task(db, user_id, task_title)

            if not matches:
                return {
                    "success": False,
                    "task": None,
                    "message": f"Could not find a task matching '{task_title}'",
                    "error": "TASK_NOT_FOUND",
                }

            if len(matches) > 1:
                matching_tasks = [{"id": t.id, "title": t.title} for t in matches]
                return {
                    "success": False,
                    "task": None,
                    "message": f"Found multiple tasks matching '{task_title}'",
                    "error": "AMBIGUOUS_TASK",
                    "matching_tasks": matching_tasks,
                    "suggestions": ["Please specify which task you mean"],
                }

            task_id = matches[0].id
            task = task_service.get_task(task_id, user_id)

        # Check if already completed
        if task.status == "completed":
            return {
                "success": True,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status,
                },
                "message": f"Task '{task.title}' is already completed",
            }

        # Mark as completed
        updated_task = task_service.update_task(
            task_id,
            user_id,
            TaskUpdate(status="completed"),
        )

        return {
            "success": True,
            "task": {
                "id": updated_task.id,
                "title": updated_task.title,
                "status": updated_task.status,
            },
            "message": f"Task '{updated_task.title}' marked as completed",
        }
