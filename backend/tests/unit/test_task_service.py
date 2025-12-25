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
