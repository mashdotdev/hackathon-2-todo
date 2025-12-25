"""Task service for CRUD operations with in-memory storage."""


from src.models.task import Task, TaskStatus


class TaskService:
    """Service for managing tasks in memory.

    Provides CRUD operations for tasks with in-memory storage.
    Data is lost when the application exits.
    """

    def __init__(self) -> None:
        """Initialize the task service with empty storage."""
        self._tasks: dict[str, Task] = {}

    def add_task(
        self,
        title: str,
        description: str | None = None,
    ) -> Task:
        """Create a new task.

        Args:
            title: Task title (required)
            description: Task description (optional)

        Returns:
            The created Task object

        Raises:
            ValueError: If title is invalid
        """
        task = Task(title=title, description=description)
        self._tasks[task.id] = task
        return task

    def get_task(self, task_id: str) -> Task | None:
        """Get a task by ID.

        Args:
            task_id: The task identifier

        Returns:
            Task if found, None otherwise
        """
        return self._tasks.get(task_id)

    def list_tasks(
        self,
        status: TaskStatus | None = None,
    ) -> list[Task]:
        """List all tasks, optionally filtered by status.

        Args:
            status: Filter by status (optional)

        Returns:
            List of tasks matching the filter
        """
        tasks = list(self._tasks.values())
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)

    def update_task(
        self,
        task_id: str,
        title: str | None = None,
        description: str | None = None,
    ) -> Task | None:
        """Update an existing task.

        Args:
            task_id: The task identifier
            title: New title (optional)
            description: New description (optional)

        Returns:
            Updated Task if found, None otherwise

        Raises:
            ValueError: If title is invalid
        """
        task = self._tasks.get(task_id)
        if task is None:
            return None
        task.update(title=title, description=description)
        return task

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID.

        Args:
            task_id: The task identifier

        Returns:
            True if deleted, False if not found
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def complete_task(self, task_id: str) -> Task | None:
        """Mark a task as completed.

        Args:
            task_id: The task identifier

        Returns:
            Updated Task if found, None otherwise
        """
        task = self._tasks.get(task_id)
        if task is None:
            return None
        task.mark_complete()
        return task

    def uncomplete_task(self, task_id: str) -> Task | None:
        """Mark a task as incomplete/pending.

        Args:
            task_id: The task identifier

        Returns:
            Updated Task if found, None otherwise
        """
        task = self._tasks.get(task_id)
        if task is None:
            return None
        task.mark_incomplete()
        return task

    def get_stats(self) -> dict[str, int]:
        """Get task statistics.

        Returns:
            Dictionary with task counts
        """
        total = len(self._tasks)
        completed = sum(1 for t in self._tasks.values() if t.is_completed)
        return {
            "total": total,
            "completed": completed,
            "pending": total - completed,
        }

    def clear_all(self) -> int:
        """Delete all tasks.

        Returns:
            Number of tasks deleted
        """
        count = len(self._tasks)
        self._tasks.clear()
        return count


# Global singleton instance for CLI usage
_task_service: TaskService | None = None


def get_task_service() -> TaskService:
    """Get the global TaskService instance.

    Returns:
        The singleton TaskService instance
    """
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
    return _task_service


def reset_task_service() -> None:
    """Reset the global TaskService instance (for testing)."""
    global _task_service
    _task_service = None
