"""Task service for database CRUD operations.

Phase V: Extended with advanced filtering, sorting, and search capabilities.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select, or_

from src.models.task import Task
from src.models.recurring_task_schedule import RecurringTaskSchedule
from src.schemas.task import (
    TaskCreate,
    TaskResponse,
    TaskUpdate,
    TaskListQuery,
    TaskSearchQuery,
)
from src.services.recurrence_service import calculate_initial_execution


# Priority ordering for sorting (High > Medium > Low)
PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}


class TaskService:
    """Service for managing tasks in database.

    Provides CRUD operations for tasks with database persistence.
    All operations are scoped to the authenticated user.
    Phase V: Extended with filtering, sorting, and search.
    """

    def __init__(self, db: Session) -> None:
        """Initialize the task service with database session."""
        self.db = db

    def create_task(self, user_id: str, task_data: TaskCreate) -> TaskResponse:
        """Create a new task with Phase V advanced features.

        Args:
            user_id: Owner user ID
            task_data: Task creation data including priority, tags, due_date, etc.

        Returns:
            The created task response

        Raises:
            ValueError: If validation fails (tags > 10, due_date in past, etc.)
        """
        # T037: Validation
        if task_data.tags and len(task_data.tags) > 10:
            raise ValueError("Maximum 10 tags allowed per task")

        if task_data.due_date:
            # Handle both timezone-aware and naive datetimes
            due_date = task_data.due_date
            now = datetime.now(timezone.utc)
            # Make due_date timezone-aware if it's naive
            if due_date.tzinfo is None:
                due_date = due_date.replace(tzinfo=timezone.utc)
            if due_date < now:
                raise ValueError("Due date must be in the future")

        task = Task(
            title=task_data.title,
            description=task_data.description,
            user_id=user_id,
            priority=task_data.priority,
            tags=task_data.tags or [],
            due_date=task_data.due_date,
            recurrence_pattern=task_data.recurrence_pattern,
            reminder_lead_time=task_data.reminder_lead_time,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        # T044: Create RecurringTaskSchedule if recurrence_pattern != 'none'
        if task_data.recurrence_pattern and task_data.recurrence_pattern != "none":
            self._create_recurring_schedule(task, user_id)

        return TaskResponse.model_validate(task)

    def _create_recurring_schedule(self, task: Task, user_id: str) -> RecurringTaskSchedule:
        """Create a RecurringTaskSchedule entry for a recurring task.

        Args:
            task: The parent task
            user_id: Owner user ID

        Returns:
            The created RecurringTaskSchedule
        """
        next_execution = calculate_initial_execution(
            task.due_date,
            task.recurrence_pattern,
        )

        schedule = RecurringTaskSchedule(
            parent_task_id=task.id,
            user_id=user_id,
            recurrence_pattern=task.recurrence_pattern,
            next_execution_time=next_execution,
            is_active=True,
        )
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

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
        query: Optional[TaskListQuery] = None,
    ) -> list[TaskResponse]:
        """List all tasks for a user with optional filtering and sorting.

        T038-T040: Extended with Phase V query parameters.

        Args:
            user_id: The owner user ID
            status_filter: Filter by status string (optional, legacy)
            query: TaskListQuery with advanced filters and sort options

        Returns:
            List of tasks matching the filters, sorted as specified
        """
        statement = select(Task).where(Task.user_id == user_id)

        # Legacy status filter support
        if status_filter and status_filter in ("pending", "completed", "in_progress"):
            statement = statement.where(Task.status == status_filter)

        # T039: Apply advanced filters from query
        if query:
            if query.status:
                statement = statement.where(Task.status == query.status)

            if query.priority:
                statement = statement.where(Task.priority == query.priority)

            if query.tags:
                # Filter by tags (array contains any of the specified tags)
                tag_list = [t.strip() for t in query.tags.split(",")]
                for tag in tag_list:
                    statement = statement.where(Task.tags.contains([tag]))

            if query.due_date_from:
                statement = statement.where(Task.due_date >= query.due_date_from)

            if query.due_date_to:
                statement = statement.where(Task.due_date <= query.due_date_to)

            # T040: Apply sorting
            if query.sort == "due_date":
                if query.order == "asc":
                    statement = statement.order_by(Task.due_date.asc().nullslast())
                else:
                    statement = statement.order_by(Task.due_date.desc().nullsfirst())
            elif query.sort == "priority":
                # Custom priority ordering: High > Medium > Low
                # Use CASE expression for proper ordering
                from sqlalchemy import case
                priority_case = case(
                    (Task.priority == "High", 0),
                    (Task.priority == "Medium", 1),
                    (Task.priority == "Low", 2),
                    else_=3,
                )
                if query.order == "asc":
                    statement = statement.order_by(priority_case.asc())
                else:
                    statement = statement.order_by(priority_case.desc())
            else:  # created_at (default)
                if query.order == "asc":
                    statement = statement.order_by(Task.created_at.asc())
                else:
                    statement = statement.order_by(Task.created_at.desc())
        else:
            statement = statement.order_by(Task.created_at.desc())

        tasks = self.db.exec(statement).all()
        return [TaskResponse.model_validate(task) for task in tasks]

    def search_tasks(
        self,
        user_id: str,
        search_query: str,
    ) -> list[TaskResponse]:
        """Search tasks by title and description using ILIKE.

        T041: Full-text search implementation.

        Args:
            user_id: The owner user ID
            search_query: Search string

        Returns:
            List of matching tasks
        """
        search_pattern = f"%{search_query}%"
        statement = (
            select(Task)
            .where(Task.user_id == user_id)
            .where(
                or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern),
                )
            )
            .order_by(Task.created_at.desc())
        )
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
        """Delete a task by ID with cascade deletion of recurring schedule.

        T045: When parent task is deleted, delete associated RecurringTaskSchedule.

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

        # T045: Delete associated recurring schedule if exists
        schedule_stmt = select(RecurringTaskSchedule).where(
            RecurringTaskSchedule.parent_task_id == task_id
        )
        schedule = self.db.exec(schedule_stmt).first()
        if schedule:
            schedule.is_active = False
            self.db.add(schedule)
            self.db.delete(schedule)

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
