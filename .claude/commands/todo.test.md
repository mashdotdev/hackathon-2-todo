---
description: Generate comprehensive tests for the Todo console app (Phase I)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).
- If user specifies "unit" → generate only unit tests
- If user specifies "integration" → generate only integration tests
- If user specifies "all" or empty → generate all tests

## Purpose

This skill generates comprehensive test suites for Phase I of the Todo hackathon. It follows the Test-First Development principle from the constitution, creating tests that verify all 5 Basic Level features.

## Prerequisites

- Project structure exists (run `/todo.setup` first)
- Task model and services exist (run `/todo.crud` first)
- pytest is installed (`uv run pytest --version`)

## Execution Steps

### 1. Create Test Fixtures

Update `tests/conftest.py`:

```python
"""Pytest fixtures for Todo application tests."""
import pytest

from src.models.task import Task, TaskStatus
from src.services.task_service import TaskService


@pytest.fixture
def task_service() -> TaskService:
    """Create a fresh TaskService instance for each test."""
    return TaskService()


@pytest.fixture
def sample_task_data() -> dict[str, str]:
    """Return sample task data for testing."""
    return {
        "title": "Test Task",
        "description": "This is a test task description",
    }


@pytest.fixture
def sample_task(task_service: TaskService, sample_task_data: dict[str, str]) -> Task:
    """Create a sample task in the service."""
    return task_service.add_task(**sample_task_data)


@pytest.fixture
def multiple_tasks(task_service: TaskService) -> list[Task]:
    """Create multiple tasks for testing list operations."""
    tasks = [
        task_service.add_task("Task 1", "First task"),
        task_service.add_task("Task 2", "Second task"),
        task_service.add_task("Task 3", "Third task"),
    ]
    # Complete one task for status filtering tests
    task_service.complete_task(tasks[1].id)
    return tasks
```

### 2. Generate Unit Tests for Task Model

Create `tests/unit/test_task.py`:

```python
"""Unit tests for Task model."""
import pytest
from datetime import datetime

from src.models.task import Task, TaskStatus


class TestTaskCreation:
    """Tests for Task creation and validation."""

    def test_create_task_with_title_only(self) -> None:
        """Task can be created with just a title."""
        task = Task(title="Buy groceries")
        assert task.title == "Buy groceries"
        assert task.description is None
        assert task.status == TaskStatus.PENDING
        assert task.id is not None
        assert len(task.id) == 8

    def test_create_task_with_description(self) -> None:
        """Task can be created with title and description."""
        task = Task(title="Buy groceries", description="Milk, eggs, bread")
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"

    def test_create_task_strips_whitespace(self) -> None:
        """Task title and description should be stripped of whitespace."""
        task = Task(title="  Buy groceries  ", description="  Get milk  ")
        assert task.title == "Buy groceries"
        assert task.description == "Get milk"

    def test_create_task_empty_title_raises_error(self) -> None:
        """Empty title should raise ValueError."""
        with pytest.raises(ValueError, match="title cannot be empty"):
            Task(title="")

    def test_create_task_whitespace_only_title_raises_error(self) -> None:
        """Whitespace-only title should raise ValueError."""
        with pytest.raises(ValueError, match="title cannot be empty"):
            Task(title="   ")

    def test_create_task_title_too_long_raises_error(self) -> None:
        """Title exceeding 200 characters should raise ValueError."""
        long_title = "x" * 201
        with pytest.raises(ValueError, match="cannot exceed 200 characters"):
            Task(title=long_title)

    def test_create_task_description_too_long_raises_error(self) -> None:
        """Description exceeding 1000 characters should raise ValueError."""
        long_desc = "x" * 1001
        with pytest.raises(ValueError, match="cannot exceed 1000 characters"):
            Task(title="Test", description=long_desc)

    def test_task_has_created_timestamp(self) -> None:
        """Task should have created_at timestamp."""
        before = datetime.now()
        task = Task(title="Test")
        after = datetime.now()
        assert before <= task.created_at <= after

    def test_task_has_updated_timestamp(self) -> None:
        """Task should have updated_at timestamp equal to created_at initially."""
        task = Task(title="Test")
        assert task.updated_at == task.created_at


class TestTaskStatus:
    """Tests for Task status operations."""

    def test_new_task_is_pending(self) -> None:
        """New task should have PENDING status."""
        task = Task(title="Test")
        assert task.status == TaskStatus.PENDING
        assert not task.is_completed

    def test_mark_complete(self) -> None:
        """Task can be marked as completed."""
        task = Task(title="Test")
        task.mark_complete()
        assert task.status == TaskStatus.COMPLETED
        assert task.is_completed

    def test_mark_incomplete(self) -> None:
        """Completed task can be marked as incomplete."""
        task = Task(title="Test")
        task.mark_complete()
        task.mark_incomplete()
        assert task.status == TaskStatus.PENDING
        assert not task.is_completed

    def test_mark_complete_updates_timestamp(self) -> None:
        """Marking complete should update the updated_at timestamp."""
        task = Task(title="Test")
        original_updated = task.updated_at
        task.mark_complete()
        assert task.updated_at >= original_updated


class TestTaskUpdate:
    """Tests for Task update operations."""

    def test_update_title(self) -> None:
        """Task title can be updated."""
        task = Task(title="Original")
        task.update(title="Updated")
        assert task.title == "Updated"

    def test_update_description(self) -> None:
        """Task description can be updated."""
        task = Task(title="Test")
        task.update(description="New description")
        assert task.description == "New description"

    def test_update_both_title_and_description(self) -> None:
        """Both title and description can be updated at once."""
        task = Task(title="Original", description="Old desc")
        task.update(title="New Title", description="New desc")
        assert task.title == "New Title"
        assert task.description == "New desc"

    def test_update_empty_title_raises_error(self) -> None:
        """Updating to empty title should raise ValueError."""
        task = Task(title="Test")
        with pytest.raises(ValueError, match="title cannot be empty"):
            task.update(title="")

    def test_update_updates_timestamp(self) -> None:
        """Update should change the updated_at timestamp."""
        task = Task(title="Test")
        original_updated = task.updated_at
        task.update(title="Updated")
        assert task.updated_at >= original_updated


class TestTaskSerialization:
    """Tests for Task serialization."""

    def test_to_dict(self) -> None:
        """Task can be converted to dictionary."""
        task = Task(title="Test", description="Desc")
        data = task.to_dict()

        assert data["id"] == task.id
        assert data["title"] == "Test"
        assert data["description"] == "Desc"
        assert data["status"] == "pending"
        assert "created_at" in data
        assert "updated_at" in data
```

### 3. Generate Unit Tests for Task Service

Create `tests/unit/test_task_service.py`:

```python
"""Unit tests for TaskService."""
import pytest

from src.models.task import Task, TaskStatus
from src.services.task_service import TaskService


class TestTaskServiceAdd:
    """Tests for adding tasks."""

    def test_add_task_returns_task(self, task_service: TaskService) -> None:
        """Adding a task should return the created Task."""
        task = task_service.add_task("New task")
        assert isinstance(task, Task)
        assert task.title == "New task"

    def test_add_task_with_description(self, task_service: TaskService) -> None:
        """Task can be added with description."""
        task = task_service.add_task("Task", description="Description")
        assert task.description == "Description"

    def test_add_task_is_retrievable(self, task_service: TaskService) -> None:
        """Added task can be retrieved by ID."""
        task = task_service.add_task("Test")
        retrieved = task_service.get_task(task.id)
        assert retrieved is not None
        assert retrieved.id == task.id

    def test_add_invalid_task_raises_error(self, task_service: TaskService) -> None:
        """Adding task with invalid data should raise ValueError."""
        with pytest.raises(ValueError):
            task_service.add_task("")


class TestTaskServiceGet:
    """Tests for getting tasks."""

    def test_get_existing_task(
        self, task_service: TaskService, sample_task: Task
    ) -> None:
        """Existing task can be retrieved."""
        retrieved = task_service.get_task(sample_task.id)
        assert retrieved is not None
        assert retrieved.id == sample_task.id
        assert retrieved.title == sample_task.title

    def test_get_nonexistent_task_returns_none(
        self, task_service: TaskService
    ) -> None:
        """Getting nonexistent task should return None."""
        result = task_service.get_task("nonexistent")
        assert result is None


class TestTaskServiceList:
    """Tests for listing tasks."""

    def test_list_empty_returns_empty_list(self, task_service: TaskService) -> None:
        """Empty service should return empty list."""
        tasks = task_service.list_tasks()
        assert tasks == []

    def test_list_all_tasks(
        self, task_service: TaskService, multiple_tasks: list[Task]
    ) -> None:
        """Should return all tasks."""
        tasks = task_service.list_tasks()
        assert len(tasks) == 3

    def test_list_pending_tasks(
        self, task_service: TaskService, multiple_tasks: list[Task]
    ) -> None:
        """Should filter to pending tasks only."""
        tasks = task_service.list_tasks(status=TaskStatus.PENDING)
        assert len(tasks) == 2
        assert all(t.status == TaskStatus.PENDING for t in tasks)

    def test_list_completed_tasks(
        self, task_service: TaskService, multiple_tasks: list[Task]
    ) -> None:
        """Should filter to completed tasks only."""
        tasks = task_service.list_tasks(status=TaskStatus.COMPLETED)
        assert len(tasks) == 1
        assert all(t.status == TaskStatus.COMPLETED for t in tasks)

    def test_list_sorted_by_created_desc(self, task_service: TaskService) -> None:
        """Tasks should be sorted by created_at descending."""
        task1 = task_service.add_task("First")
        task2 = task_service.add_task("Second")
        task3 = task_service.add_task("Third")

        tasks = task_service.list_tasks()
        assert tasks[0].id == task3.id  # Most recent first
        assert tasks[2].id == task1.id  # Oldest last


class TestTaskServiceUpdate:
    """Tests for updating tasks."""

    def test_update_existing_task(
        self, task_service: TaskService, sample_task: Task
    ) -> None:
        """Existing task can be updated."""
        result = task_service.update_task(sample_task.id, title="Updated Title")
        assert result is not None
        assert result.title == "Updated Title"

    def test_update_nonexistent_task_returns_none(
        self, task_service: TaskService
    ) -> None:
        """Updating nonexistent task should return None."""
        result = task_service.update_task("nonexistent", title="New")
        assert result is None

    def test_update_persists_changes(
        self, task_service: TaskService, sample_task: Task
    ) -> None:
        """Updates should be persisted."""
        task_service.update_task(sample_task.id, title="Persisted")
        retrieved = task_service.get_task(sample_task.id)
        assert retrieved is not None
        assert retrieved.title == "Persisted"


class TestTaskServiceDelete:
    """Tests for deleting tasks."""

    def test_delete_existing_task(
        self, task_service: TaskService, sample_task: Task
    ) -> None:
        """Existing task can be deleted."""
        result = task_service.delete_task(sample_task.id)
        assert result is True

    def test_delete_removes_task(
        self, task_service: TaskService, sample_task: Task
    ) -> None:
        """Deleted task should no longer be retrievable."""
        task_service.delete_task(sample_task.id)
        assert task_service.get_task(sample_task.id) is None

    def test_delete_nonexistent_task_returns_false(
        self, task_service: TaskService
    ) -> None:
        """Deleting nonexistent task should return False."""
        result = task_service.delete_task("nonexistent")
        assert result is False


class TestTaskServiceComplete:
    """Tests for completing tasks."""

    def test_complete_task(
        self, task_service: TaskService, sample_task: Task
    ) -> None:
        """Task can be marked as complete."""
        result = task_service.complete_task(sample_task.id)
        assert result is not None
        assert result.is_completed

    def test_complete_nonexistent_task_returns_none(
        self, task_service: TaskService
    ) -> None:
        """Completing nonexistent task should return None."""
        result = task_service.complete_task("nonexistent")
        assert result is None

    def test_uncomplete_task(
        self, task_service: TaskService, sample_task: Task
    ) -> None:
        """Completed task can be marked as incomplete."""
        task_service.complete_task(sample_task.id)
        result = task_service.uncomplete_task(sample_task.id)
        assert result is not None
        assert not result.is_completed


class TestTaskServiceStats:
    """Tests for task statistics."""

    def test_stats_empty_service(self, task_service: TaskService) -> None:
        """Empty service should have zero counts."""
        stats = task_service.get_stats()
        assert stats["total"] == 0
        assert stats["completed"] == 0
        assert stats["pending"] == 0

    def test_stats_with_tasks(
        self, task_service: TaskService, multiple_tasks: list[Task]
    ) -> None:
        """Stats should reflect actual task counts."""
        stats = task_service.get_stats()
        assert stats["total"] == 3
        assert stats["completed"] == 1  # One was completed in fixture
        assert stats["pending"] == 2


class TestTaskServiceClear:
    """Tests for clearing all tasks."""

    def test_clear_all_returns_count(
        self, task_service: TaskService, multiple_tasks: list[Task]
    ) -> None:
        """Clear should return number of deleted tasks."""
        count = task_service.clear_all()
        assert count == 3

    def test_clear_all_removes_tasks(
        self, task_service: TaskService, multiple_tasks: list[Task]
    ) -> None:
        """Clear should remove all tasks."""
        task_service.clear_all()
        assert task_service.list_tasks() == []
```

### 4. Generate Integration Tests for CLI

Create `tests/integration/test_cli.py`:

```python
"""Integration tests for Todo CLI."""
import pytest
from typer.testing import CliRunner

from src.main import app
from src.services.task_service import get_task_service, TaskService


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture(autouse=True)
def reset_service() -> None:
    """Reset the task service before each test."""
    # Clear the global service state
    service = get_task_service()
    service.clear_all()


class TestCLIVersion:
    """Tests for version command."""

    def test_version_command(self, runner: CliRunner) -> None:
        """Version command should show version info."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "v0.1.0" in result.output


class TestCLIAddTask:
    """Tests for add command."""

    def test_add_task_success(self, runner: CliRunner) -> None:
        """Adding a task should succeed."""
        result = runner.invoke(app, ["task", "add", "Buy milk"])
        assert result.exit_code == 0
        assert "Task added" in result.output
        assert "Buy milk" in result.output

    def test_add_task_with_description(self, runner: CliRunner) -> None:
        """Adding a task with description should succeed."""
        result = runner.invoke(
            app, ["task", "add", "Buy groceries", "--desc", "Milk and eggs"]
        )
        assert result.exit_code == 0
        assert "Task added" in result.output


class TestCLIListTasks:
    """Tests for list command."""

    def test_list_empty(self, runner: CliRunner) -> None:
        """Listing with no tasks should show message."""
        result = runner.invoke(app, ["task", "list"])
        assert result.exit_code == 0
        assert "No tasks found" in result.output

    def test_list_with_tasks(self, runner: CliRunner) -> None:
        """Listing with tasks should show table."""
        # Add a task first
        runner.invoke(app, ["task", "add", "Test task"])
        result = runner.invoke(app, ["task", "list"])
        assert result.exit_code == 0
        assert "Test task" in result.output
        assert "Total:" in result.output

    def test_list_filter_by_status(self, runner: CliRunner) -> None:
        """Listing can filter by status."""
        runner.invoke(app, ["task", "add", "Task 1"])
        result = runner.invoke(app, ["task", "list", "--status", "pending"])
        assert result.exit_code == 0
        assert "Task 1" in result.output


class TestCLICompleteTask:
    """Tests for complete command."""

    def test_complete_task_success(self, runner: CliRunner) -> None:
        """Completing a task should succeed."""
        # Add and get task ID
        add_result = runner.invoke(app, ["task", "add", "Complete me"])
        # Extract ID from output (format: "ID: xxxxxxxx")
        task_id = add_result.output.split("ID: ")[1].split(")")[0]

        result = runner.invoke(app, ["task", "complete", task_id])
        assert result.exit_code == 0
        assert "Task completed" in result.output

    def test_complete_nonexistent_task(self, runner: CliRunner) -> None:
        """Completing nonexistent task should fail."""
        result = runner.invoke(app, ["task", "complete", "nonexistent"])
        assert result.exit_code == 1
        assert "not found" in result.output


class TestCLIDeleteTask:
    """Tests for delete command."""

    def test_delete_task_with_force(self, runner: CliRunner) -> None:
        """Deleting with --force should skip confirmation."""
        add_result = runner.invoke(app, ["task", "add", "Delete me"])
        task_id = add_result.output.split("ID: ")[1].split(")")[0]

        result = runner.invoke(app, ["task", "delete", task_id, "--force"])
        assert result.exit_code == 0
        assert "Task deleted" in result.output

    def test_delete_nonexistent_task(self, runner: CliRunner) -> None:
        """Deleting nonexistent task should fail."""
        result = runner.invoke(app, ["task", "delete", "nonexistent", "--force"])
        assert result.exit_code == 1
        assert "not found" in result.output


class TestCLIUpdateTask:
    """Tests for update command."""

    def test_update_task_title(self, runner: CliRunner) -> None:
        """Updating task title should succeed."""
        add_result = runner.invoke(app, ["task", "add", "Original"])
        task_id = add_result.output.split("ID: ")[1].split(")")[0]

        result = runner.invoke(
            app, ["task", "update", task_id, "--title", "Updated"]
        )
        assert result.exit_code == 0
        assert "Task updated" in result.output

    def test_update_without_options_fails(self, runner: CliRunner) -> None:
        """Update without --title or --desc should fail."""
        add_result = runner.invoke(app, ["task", "add", "Test"])
        task_id = add_result.output.split("ID: ")[1].split(")")[0]

        result = runner.invoke(app, ["task", "update", task_id])
        assert result.exit_code == 1
        assert "Provide at least" in result.output
```

### 5. Run Tests

Execute test verification:
```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=term-missing

# Run only unit tests
uv run pytest tests/unit/

# Run only integration tests
uv run pytest tests/integration/

# Run with verbose output
uv run pytest -v
```

### 6. Output Summary

Report:
- ✅ Test fixtures created (`tests/conftest.py`)
- ✅ Unit tests for Task model (`tests/unit/test_task.py`)
- ✅ Unit tests for TaskService (`tests/unit/test_task_service.py`)
- ✅ Integration tests for CLI (`tests/integration/test_cli.py`)

**Test Coverage**:
| Category | Tests | Coverage |
|----------|-------|----------|
| Task Model | 15 tests | Creation, validation, status, update, serialization |
| TaskService | 20 tests | CRUD, filtering, stats, clear |
| CLI Integration | 12 tests | All 5 basic commands + edge cases |
| **Total** | **47 tests** | Full Basic Level coverage |

**Next Steps**:
1. Run `uv run pytest` to execute all tests
2. Fix any failing tests
3. Run `/sp.specify` to create Phase I specification
4. Commit with `/sp.git.commit_pr`
