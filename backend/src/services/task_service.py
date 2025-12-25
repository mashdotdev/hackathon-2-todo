"""Task service for database CRUD operations."""

from datetime import datetime

from sqlmodel import Session, select

from src.models.task import Task
from src.schemas.task import TaskCreate, TaskResponse, TaskUpdate


class TaskService:
    """Service for managing tasks in database.

    Provides CRUD operations for tasks with database persistence.
    All operations are scoped to the authenticated user.
    """

    def __init__(self, db: Session) -> None:
        """Initialize the task service with database session."""
        self.db = db

    def create_task(self, user_id: str, task_data: TaskCreate) -> TaskResponse:
        """Create a new task.

        Args:
            user_id: Owner user ID
            task_data: Task creation data

        Returns:
            The created task response
        """
        task = Task(
            title=task_data.title,
            description=task_data.description,
            user_id=user_id,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return TaskResponse.model_validate(task)

    def get_task(self, task_id: str, user_id: str) -> TaskResponse | None:
        """Get a task by ID.

        Args:
            task_id: The task identifier
            user_id: The owner user ID

        Returns:
            Task response if found, None otherwise
        """
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = self.db.exec(statement).first()
        if task is None:
            return None
        return TaskResponse.model_validate(task)

    def list_tasks(
        self,
        user_id: str,
        status_filter: str | None = None,
    ) -> list[TaskResponse]:
        """List all tasks for a user, optionally filtered by status.

        Args:
            user_id: The owner user ID
            status_filter: Filter by status string (optional)

        Returns:
            List of tasks matching the filter
        """
        statement = select(Task).where(Task.user_id == user_id)

        if status_filter and status_filter in ("pending", "completed"):
            statement = statement.where(Task.status == status_filter)

        statement = statement.order_by(Task.created_at.desc())
        tasks = self.db.exec(statement).all()
        return [TaskResponse.model_validate(task) for task in tasks]

    def update_task(
        self,
        task_id: str,
        user_id: str,
        task_data: TaskUpdate,
    ) -> TaskResponse | None:
        """Update an existing task.

        Args:
            task_id: The task identifier
            user_id: The owner user ID
            task_data: Task update data

        Returns:
            Updated task response if found, None otherwise
        """
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = self.db.exec(statement).first()
        if task is None:
            return None

        update_data = task_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)

        task.updated_at = datetime.utcnow()
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return TaskResponse.model_validate(task)

    def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete a task by ID.

        Args:
            task_id: The task identifier
            user_id: The owner user ID

        Returns:
            True if deleted, False if not found
        """
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = self.db.exec(statement).first()
        if task is None:
            return False

        self.db.delete(task)
        self.db.commit()
        return True

    def toggle_complete(self, task_id: str, user_id: str) -> TaskResponse | None:
        """Toggle task completion status.

        Args:
            task_id: The task identifier
            user_id: The owner user ID

        Returns:
            Updated task response if found, None otherwise
        """
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = self.db.exec(statement).first()
        if task is None:
            return None

        if task.status == "completed":
            task.status = "pending"
        else:
            task.status = "completed"

        task.updated_at = datetime.utcnow()
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return TaskResponse.model_validate(task)
