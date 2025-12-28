"""MCP Tool: list_tasks - Retrieve the user's tasks."""

from sqlmodel import Session

from src.core.database import engine
from src.mcp.server import mcp
from src.services.task_service import TaskService


@mcp.tool()
def list_tasks(user_id: str, status: str = "all") -> dict:
    """Retrieve the user's tasks with optional filtering by status.

    Args:
        user_id: The authenticated user's ID (UUID)
        status: Filter tasks by status - "all", "pending", or "completed" (default: "all")

    Returns:
        dict with success status, tasks array, total count, and message
    """
    if not user_id:
        return {
            "success": False,
            "tasks": [],
            "total": 0,
            "message": "User ID is required",
            "error": "VALIDATION_ERROR",
        }

    # Validate status filter
    valid_statuses = ["all", "pending", "completed"]
    if status not in valid_statuses:
        return {
            "success": False,
            "tasks": [],
            "total": 0,
            "message": f"Invalid status filter. Use one of: {', '.join(valid_statuses)}",
            "error": "VALIDATION_ERROR",
        }

    with Session(engine) as db:
        task_service = TaskService(db)

        # Convert "all" to None for the task service
        status_filter = None if status == "all" else status
        tasks = task_service.list_tasks(user_id, status_filter)

        task_list = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "created_at": task.created_at.isoformat(),
            }
            for task in tasks
        ]

        # Generate appropriate message
        total = len(task_list)
        if status == "all":
            message = f"Found {total} task{'s' if total != 1 else ''}"
        else:
            message = f"Found {total} {status} task{'s' if total != 1 else ''}"

        if total == 0:
            if status == "all":
                message = "You don't have any tasks yet"
            else:
                message = f"You don't have any {status} tasks"

        return {
            "success": True,
            "tasks": task_list,
            "total": total,
            "message": message,
        }
