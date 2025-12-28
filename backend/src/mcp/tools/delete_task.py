"""MCP Tool: delete_task - Delete a task from the user's list."""

from sqlmodel import Session, select

from src.core.database import engine
from src.mcp.server import mcp
from src.models.task import Task
from src.services.task_service import TaskService


def fuzzy_match_task(db: Session, user_id: str, task_title: str) -> list[Task]:
    """Find tasks matching a title using fuzzy matching."""
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
def delete_task(
    user_id: str,
    task_id: str = "",
    task_title: str = "",
    confirmed: bool = False,
) -> dict:
    """Delete a task from the user's list.

    Args:
        user_id: The authenticated user's ID (UUID)
        task_id: The task ID to delete (optional if task_title provided)
        task_title: Task title for fuzzy matching (optional if task_id provided)
        confirmed: Whether deletion has been confirmed by user (default: False)

    Returns:
        dict with success status, deleted task details, confirmation requirement, and message
    """
    if not user_id:
        return {
            "success": False,
            "deleted_task": None,
            "requires_confirmation": False,
            "message": "User ID is required",
            "error": "VALIDATION_ERROR",
        }

    if not task_id and not task_title:
        return {
            "success": False,
            "deleted_task": None,
            "requires_confirmation": False,
            "message": "Either task_id or task_title is required",
            "error": "VALIDATION_ERROR",
        }

    with Session(engine) as db:
        task_service = TaskService(db)
        task_to_delete = None

        # If task_id is provided, use it directly
        if task_id:
            task = task_service.get_task(task_id, user_id)
            if not task:
                return {
                    "success": False,
                    "deleted_task": None,
                    "requires_confirmation": False,
                    "message": f"Task with ID '{task_id}' not found",
                    "error": "TASK_NOT_FOUND",
                }
            task_to_delete = {"id": task.id, "title": task.title}
        else:
            # Use fuzzy matching on title
            matches = fuzzy_match_task(db, user_id, task_title)

            if not matches:
                return {
                    "success": False,
                    "deleted_task": None,
                    "requires_confirmation": False,
                    "message": f"Could not find a task matching '{task_title}'",
                    "error": "TASK_NOT_FOUND",
                }

            if len(matches) > 1:
                matching_tasks = [{"id": t.id, "title": t.title} for t in matches]
                return {
                    "success": False,
                    "deleted_task": None,
                    "requires_confirmation": False,
                    "message": f"Found multiple tasks matching '{task_title}'",
                    "error": "AMBIGUOUS_TASK",
                    "matching_tasks": matching_tasks,
                    "suggestions": ["Please specify which task you mean"],
                }

            task_id = matches[0].id
            task_to_delete = {"id": matches[0].id, "title": matches[0].title}

        # If not confirmed, require confirmation
        if not confirmed:
            return {
                "success": False,
                "deleted_task": None,
                "requires_confirmation": True,
                "task_to_delete": task_to_delete,
                "message": f"Are you sure you want to delete '{task_to_delete['title']}'?",
            }

        # Perform deletion
        success = task_service.delete_task(task_id, user_id)

        if success:
            return {
                "success": True,
                "deleted_task": task_to_delete,
                "requires_confirmation": False,
                "message": f"Task '{task_to_delete['title']}' has been deleted",
            }
        else:
            return {
                "success": False,
                "deleted_task": None,
                "requires_confirmation": False,
                "message": "Failed to delete task",
                "error": "INTERNAL_ERROR",
            }
