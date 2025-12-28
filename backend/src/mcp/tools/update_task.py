"""MCP Tool: update_task - Update a task's title or description."""

from sqlmodel import Session, select

from src.core.database import engine
from src.mcp.server import mcp
from src.models.task import Task
from src.schemas.task import TaskUpdate
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
def update_task(
    user_id: str,
    task_id: str = "",
    task_title: str = "",
    new_title: str = "",
    new_description: str = "",
) -> dict:
    """Update a task's title or description.

    Args:
        user_id: The authenticated user's ID (UUID)
        task_id: The task ID to update (optional if task_title provided)
        task_title: Current task title for fuzzy matching (optional if task_id provided)
        new_title: New title for the task (optional)
        new_description: New description for the task (optional)

    Returns:
        dict with success status, updated task details, and message
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

    if not new_title and not new_description:
        return {
            "success": False,
            "task": None,
            "message": "Either new_title or new_description is required",
            "error": "VALIDATION_ERROR",
        }

    if new_title and len(new_title) > 200:
        return {
            "success": False,
            "task": None,
            "message": "Task title must be 200 characters or less",
            "error": "VALIDATION_ERROR",
        }

    if new_description and len(new_description) > 1000:
        return {
            "success": False,
            "task": None,
            "message": "Task description must be 1000 characters or less",
            "error": "VALIDATION_ERROR",
        }

    with Session(engine) as db:
        task_service = TaskService(db)
        old_title = None

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
            old_title = task.title
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
            old_title = matches[0].title

        # Build update data
        update_data = {}
        if new_title:
            update_data["title"] = new_title.strip()
        if new_description:
            update_data["description"] = new_description.strip()

        # Perform update
        updated_task = task_service.update_task(
            task_id,
            user_id,
            TaskUpdate(**update_data),
        )

        # Generate message
        if new_title and new_title != old_title:
            message = f"Task updated from '{old_title}' to '{new_title}'"
        elif new_description:
            message = f"Task '{updated_task.title}' description updated"
        else:
            message = f"Task '{updated_task.title}' updated"

        return {
            "success": True,
            "task": {
                "id": updated_task.id,
                "title": updated_task.title,
                "description": updated_task.description,
                "status": updated_task.status,
            },
            "message": message,
        }
