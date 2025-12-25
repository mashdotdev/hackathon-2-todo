"""Unit tests for Task model."""

from datetime import datetime

import pytest

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
        # Allow for minor time differences
        diff = abs((task.updated_at - task.created_at).total_seconds())
        assert diff < 1


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
