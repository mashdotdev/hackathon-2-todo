---
description: Generate Task model and CRUD operations for the Todo console app (Phase I)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

This skill generates the complete Task model and CRUD (Create, Read, Update, Delete) operations for Phase I of the Todo hackathon. It implements all 5 Basic Level features:
1. Add Task
2. Delete Task
3. Update Task
4. View Task List
5. Mark as Complete

## Prerequisites

- Project structure exists (run `/todo.setup` first if not)
- `src/models/` and `src/services/` directories exist

## Execution Steps

### 1. Generate Task Model

Create `src/models/task.py`:

```python
"""Task model for in-memory storage."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class TaskStatus(Enum):
    """Task completion status."""
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass
class Task:
    """Represents a todo task.

    Attributes:
        id: Unique identifier for the task
        title: Task title (required, 1-200 chars)
        description: Optional task description (max 1000 chars)
        status: Current status (pending/completed)
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last updated
    """
    title: str
    description: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate task data after initialization."""
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Task title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")
        if self.description and len(self.description) > 1000:
            raise ValueError("Task description cannot exceed 1000 characters")
        self.title = self.title.strip()
        if self.description:
            self.description = self.description.strip()

    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == TaskStatus.COMPLETED

    def mark_complete(self) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.updated_at = datetime.now()

    def mark_incomplete(self) -> None:
        """Mark task as pending/incomplete."""
        self.status = TaskStatus.PENDING
        self.updated_at = datetime.now()

    def update(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """Update task details.

        Args:
            title: New title (optional)
            description: New description (optional)
        """
        if title is not None:
            if len(title.strip()) == 0:
                raise ValueError("Task title cannot be empty")
            if len(title) > 200:
                raise ValueError("Task title cannot exceed 200 characters")
            self.title = title.strip()
        if description is not None:
            if len(description) > 1000:
                raise ValueError("Task description cannot exceed 1000 characters")
            self.description = description.strip() if description else None
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
```

Update `src/models/__init__.py`:
```python
"""Models package."""
from src.models.task import Task, TaskStatus

__all__ = ["Task", "TaskStatus"]
```

### 2. Generate Task Service

Create `src/services/task_service.py`:

```python
"""Task service for CRUD operations with in-memory storage."""
from typing import Optional

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
        description: Optional[str] = None,
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

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID.

        Args:
            task_id: The task identifier

        Returns:
            Task if found, None otherwise
        """
        return self._tasks.get(task_id)

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
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
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Task]:
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

    def complete_task(self, task_id: str) -> Optional[Task]:
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

    def uncomplete_task(self, task_id: str) -> Optional[Task]:
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
_task_service: Optional[TaskService] = None


def get_task_service() -> TaskService:
    """Get the global TaskService instance.

    Returns:
        The singleton TaskService instance
    """
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
    return _task_service
```

Update `src/services/__init__.py`:
```python
"""Services package."""
from src.services.task_service import TaskService, get_task_service

__all__ = ["TaskService", "get_task_service"]
```

### 3. Generate CLI Commands

Create `src/cli/commands.py`:

```python
"""CLI commands for Todo application."""
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from src.models.task import TaskStatus
from src.services.task_service import get_task_service

console = Console()
app = typer.Typer(help="Manage your todo tasks")


@app.command("add")
def add_task(
    title: str = typer.Argument(..., help="Task title"),
    description: Optional[str] = typer.Option(
        None, "--desc", "-d", help="Task description"
    ),
) -> None:
    """Add a new task to the list."""
    service = get_task_service()
    try:
        task = service.add_task(title=title, description=description)
        console.print(f"[green]✓[/green] Task added: [bold]{task.title}[/bold] (ID: {task.id})")
    except ValueError as e:
        console.print(f"[red]✗[/red] Error: {e}")
        raise typer.Exit(1)


@app.command("list")
def list_tasks(
    status: Optional[str] = typer.Option(
        None, "--status", "-s", help="Filter by status: pending, completed, all"
    ),
    show_all: bool = typer.Option(
        False, "--all", "-a", help="Show all tasks (same as --status all)"
    ),
) -> None:
    """List all tasks."""
    service = get_task_service()

    # Determine filter
    filter_status: Optional[TaskStatus] = None
    if status and status.lower() != "all":
        try:
            filter_status = TaskStatus(status.lower())
        except ValueError:
            console.print(f"[red]✗[/red] Invalid status: {status}. Use: pending, completed, all")
            raise typer.Exit(1)

    tasks = service.list_tasks(status=filter_status)

    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        return

    # Create table
    table = Table(title="Todo List", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=10)
    table.add_column("Status", width=10)
    table.add_column("Title", min_width=20)
    table.add_column("Description", min_width=30)

    for task in tasks:
        status_icon = "[green]✓[/green]" if task.is_completed else "[yellow]○[/yellow]"
        table.add_row(
            task.id,
            status_icon,
            task.title,
            task.description or "-",
        )

    console.print(table)

    # Show stats
    stats = service.get_stats()
    console.print(
        f"\n[dim]Total: {stats['total']} | "
        f"Completed: {stats['completed']} | "
        f"Pending: {stats['pending']}[/dim]"
    )


@app.command("update")
def update_task(
    task_id: str = typer.Argument(..., help="Task ID to update"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="New title"),
    description: Optional[str] = typer.Option(None, "--desc", "-d", help="New description"),
) -> None:
    """Update an existing task."""
    if title is None and description is None:
        console.print("[red]✗[/red] Provide at least --title or --desc to update")
        raise typer.Exit(1)

    service = get_task_service()
    try:
        task = service.update_task(task_id=task_id, title=title, description=description)
        if task is None:
            console.print(f"[red]✗[/red] Task not found: {task_id}")
            raise typer.Exit(1)
        console.print(f"[green]✓[/green] Task updated: [bold]{task.title}[/bold]")
    except ValueError as e:
        console.print(f"[red]✗[/red] Error: {e}")
        raise typer.Exit(1)


@app.command("delete")
def delete_task(
    task_id: str = typer.Argument(..., help="Task ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete a task from the list."""
    service = get_task_service()

    # Check if task exists
    task = service.get_task(task_id)
    if task is None:
        console.print(f"[red]✗[/red] Task not found: {task_id}")
        raise typer.Exit(1)

    # Confirm deletion
    if not force:
        confirm = typer.confirm(f"Delete task '{task.title}'?")
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(0)

    service.delete_task(task_id)
    console.print(f"[green]✓[/green] Task deleted: [bold]{task.title}[/bold]")


@app.command("complete")
def complete_task(
    task_id: str = typer.Argument(..., help="Task ID to mark complete"),
) -> None:
    """Mark a task as completed."""
    service = get_task_service()
    task = service.complete_task(task_id)

    if task is None:
        console.print(f"[red]✗[/red] Task not found: {task_id}")
        raise typer.Exit(1)

    console.print(f"[green]✓[/green] Task completed: [bold]{task.title}[/bold]")


@app.command("uncomplete")
def uncomplete_task(
    task_id: str = typer.Argument(..., help="Task ID to mark incomplete"),
) -> None:
    """Mark a task as incomplete/pending."""
    service = get_task_service()
    task = service.uncomplete_task(task_id)

    if task is None:
        console.print(f"[red]✗[/red] Task not found: {task_id}")
        raise typer.Exit(1)

    console.print(f"[yellow]○[/yellow] Task marked pending: [bold]{task.title}[/bold]")


@app.command("show")
def show_task(
    task_id: str = typer.Argument(..., help="Task ID to show"),
) -> None:
    """Show details of a specific task."""
    service = get_task_service()
    task = service.get_task(task_id)

    if task is None:
        console.print(f"[red]✗[/red] Task not found: {task_id}")
        raise typer.Exit(1)

    status = "[green]Completed[/green]" if task.is_completed else "[yellow]Pending[/yellow]"
    console.print(f"\n[bold]Task Details[/bold]")
    console.print(f"  ID:          {task.id}")
    console.print(f"  Title:       {task.title}")
    console.print(f"  Description: {task.description or '-'}")
    console.print(f"  Status:      {status}")
    console.print(f"  Created:     {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    console.print(f"  Updated:     {task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")


@app.command("stats")
def show_stats() -> None:
    """Show task statistics."""
    service = get_task_service()
    stats = service.get_stats()

    console.print("\n[bold]Task Statistics[/bold]")
    console.print(f"  Total tasks:     {stats['total']}")
    console.print(f"  Completed:       [green]{stats['completed']}[/green]")
    console.print(f"  Pending:         [yellow]{stats['pending']}[/yellow]")

    if stats['total'] > 0:
        percentage = (stats['completed'] / stats['total']) * 100
        console.print(f"  Completion rate: {percentage:.1f}%")
```

Update `src/cli/__init__.py`:
```python
"""CLI package."""
from src.cli.commands import app

__all__ = ["app"]
```

### 4. Update Main Entry Point

Update `src/main.py`:

```python
"""Main entry point for Todo CLI application."""
import typer

from src.cli.commands import app as task_app

app = typer.Typer(
    name="todo",
    help="Todo Console Application - Phase I\n\nManage your tasks from the command line.",
    add_completion=False,
)

# Add task commands as subcommands
app.add_typer(task_app, name="task")


@app.command()
def version() -> None:
    """Show application version."""
    typer.echo("Todo Console v0.1.0 (Phase I)")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Todo Console Application - Phase I."""
    if ctx.invoked_subcommand is None:
        # Show help if no command provided
        typer.echo(ctx.get_help())


if __name__ == "__main__":
    app()
```

### 5. Verify Implementation

Run verification:
```bash
# Lint check
uv run ruff check src/

# Type check
uv run mypy src/

# Test CLI
uv run todo version
uv run todo task --help
uv run todo task add "My first task" --desc "Testing the app"
uv run todo task list
```

### 6. Output Summary

Report:
- ✅ Task model with validation (`src/models/task.py`)
- ✅ TaskService with CRUD operations (`src/services/task_service.py`)
- ✅ CLI commands for all 5 Basic features (`src/cli/commands.py`)
- ✅ Main entry point updated (`src/main.py`)

**Basic Features Implemented**:
| Feature | Command | Status |
|---------|---------|--------|
| Add Task | `todo task add <title>` | ✅ |
| Delete Task | `todo task delete <id>` | ✅ |
| Update Task | `todo task update <id>` | ✅ |
| View Task List | `todo task list` | ✅ |
| Mark Complete | `todo task complete <id>` | ✅ |

**Next Steps**:
1. Run `/todo.test` to generate test cases
2. Run tests with `uv run pytest`
3. Create Phase I specification with `/sp.specify`
