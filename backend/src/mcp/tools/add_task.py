"""MCP Tool: add_task - Create a new task for the user."""

from sqlmodel import Session

from src.core.database import engine
from src.mcp.server import mcp
from src.schemas.task import TaskCreate
from src.services.task_service import TaskService


@mcp.tool()
def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Create a new task for the user.

    Args:
        user_id: The authenticated user's ID (UUID)
        title: The task title (required, 1-200 characters)
        description: Optional task description (max 1000 characters)

    Returns:
        dict with success status, created task details, and message
    """
    if not user_id:
        return {
            "success": False,
            "task": None,
            "message": "User ID is required",
            "error": "VALIDATION_ERROR",
        }

    if not title or len(title.strip()) == 0:
        return {
            "success": False,
            "task": None,
            "message": "Task title is required",
            "error": "VALIDATION_ERROR",
        }

    if len(title) > 200:
        return {
            "success": False,
            "task": None,
            "message": "Task title must be 200 characters or less",
            "error": "VALIDATION_ERROR",
        }

    if description and len(description) > 1000:
        return {
            "success": False,
            "task": None,
            "message": "Task description must be 1000 characters or less",
            "error": "VALIDATION_ERROR",
        }

    with Session(engine) as db:
        task_service = TaskService(db)
        task_data = TaskCreate(title=title.strip(), description=description.strip() if description else None)
        created_task = task_service.create_task(user_id, task_data)

        return {
            "success": True,
            "task": {
                "id": created_task.id,
                "title": created_task.title,
                "description": created_task.description,
                "status": created_task.status,
                "created_at": created_task.created_at.isoformat(),
            },
            "message": f"Task '{created_task.title}' created successfully",
        }
