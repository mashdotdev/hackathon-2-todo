"""Pytest fixtures for Todo application tests."""

import pytest

from src.models.task import Task
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
