"""Tests for task endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.models.task import Task, TaskStatus
from src.models.user import User


class TestListTasks:
    """Tests for GET /api/tasks."""

    def test_list_tasks_empty(self, client: TestClient, auth_headers: dict[str, str]):
        """Should return empty list when no tasks exist."""
        response = client.get("/api/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["tasks"] == []
        assert data["total"] == 0

    def test_list_tasks_with_tasks(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        multiple_tasks: list[Task],
    ):
        """Should return all user tasks."""
        response = client.get("/api/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["tasks"]) == 3

    def test_list_tasks_filter_pending(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        multiple_tasks: list[Task],
    ):
        """Should filter tasks by pending status."""
        response = client.get(
            "/api/tasks", params={"status_filter": "pending"}, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert all(t["status"] == "pending" for t in data["tasks"])

    def test_list_tasks_filter_completed(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        multiple_tasks: list[Task],
    ):
        """Should filter tasks by completed status."""
        response = client.get(
            "/api/tasks", params={"status_filter": "completed"}, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert all(t["status"] == "completed" for t in data["tasks"])

    def test_list_tasks_no_auth(self, client: TestClient):
        """Should return 401 without authentication."""
        response = client.get("/api/tasks")
        assert response.status_code == 401


class TestCreateTask:
    """Tests for POST /api/tasks."""

    def test_create_task_success(self, client: TestClient, auth_headers: dict[str, str]):
        """Should create a new task."""
        response = client.post(
            "/api/tasks",
            json={"title": "New Task", "description": "Task description"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["description"] == "Task description"
        assert data["status"] == "pending"
        assert "id" in data

    def test_create_task_minimal(self, client: TestClient, auth_headers: dict[str, str]):
        """Should create task with only title."""
        response = client.post(
            "/api/tasks",
            json={"title": "Minimal Task"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["description"] is None

    def test_create_task_empty_title(
        self, client: TestClient, auth_headers: dict[str, str]
    ):
        """Should return 422 for empty title."""
        response = client.post(
            "/api/tasks",
            json={"title": ""},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_task_no_auth(self, client: TestClient):
        """Should return 401 without authentication."""
        response = client.post("/api/tasks", json={"title": "Test"})
        assert response.status_code == 401


class TestGetTask:
    """Tests for GET /api/tasks/{task_id}."""

    def test_get_task_success(
        self, client: TestClient, auth_headers: dict[str, str], test_task: Task
    ):
        """Should return task by ID."""
        response = client.get(f"/api/tasks/{test_task.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_task.id
        assert data["title"] == test_task.title

    def test_get_task_not_found(
        self, client: TestClient, auth_headers: dict[str, str]
    ):
        """Should return 404 for nonexistent task."""
        response = client.get("/api/tasks/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404

    def test_get_task_no_auth(self, client: TestClient, test_task: Task):
        """Should return 401 without authentication."""
        response = client.get(f"/api/tasks/{test_task.id}")
        assert response.status_code == 401


class TestUpdateTask:
    """Tests for PUT /api/tasks/{task_id}."""

    def test_update_task_title(
        self, client: TestClient, auth_headers: dict[str, str], test_task: Task
    ):
        """Should update task title."""
        response = client.put(
            f"/api/tasks/{test_task.id}",
            json={"title": "Updated Title"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == test_task.description

    def test_update_task_description(
        self, client: TestClient, auth_headers: dict[str, str], test_task: Task
    ):
        """Should update task description."""
        response = client.put(
            f"/api/tasks/{test_task.id}",
            json={"description": "New description"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["description"] == "New description"

    def test_update_task_status(
        self, client: TestClient, auth_headers: dict[str, str], test_task: Task
    ):
        """Should update task status."""
        response = client.put(
            f"/api/tasks/{test_task.id}",
            json={"status": "completed"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    def test_update_task_not_found(
        self, client: TestClient, auth_headers: dict[str, str]
    ):
        """Should return 404 for nonexistent task."""
        response = client.put(
            "/api/tasks/nonexistent-id",
            json={"title": "Test"},
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestDeleteTask:
    """Tests for DELETE /api/tasks/{task_id}."""

    def test_delete_task_success(
        self, client: TestClient, auth_headers: dict[str, str], test_task: Task
    ):
        """Should delete task."""
        response = client.delete(f"/api/tasks/{test_task.id}", headers=auth_headers)
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

        # Verify task is deleted
        response = client.get(f"/api/tasks/{test_task.id}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_task_not_found(
        self, client: TestClient, auth_headers: dict[str, str]
    ):
        """Should return 404 for nonexistent task."""
        response = client.delete("/api/tasks/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404


class TestToggleTaskComplete:
    """Tests for PATCH /api/tasks/{task_id}/complete."""

    def test_toggle_to_completed(
        self, client: TestClient, auth_headers: dict[str, str], test_task: Task
    ):
        """Should toggle task from pending to completed."""
        assert test_task.status == TaskStatus.PENDING
        response = client.patch(
            f"/api/tasks/{test_task.id}/complete", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    def test_toggle_to_pending(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        session: Session,
        test_user: User,
    ):
        """Should toggle task from completed to pending."""
        # Create a completed task
        task = Task(
            title="Completed Task",
            user_id=test_user.id,
            status=TaskStatus.COMPLETED,
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        response = client.patch(f"/api/tasks/{task.id}/complete", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "pending"

    def test_toggle_not_found(self, client: TestClient, auth_headers: dict[str, str]):
        """Should return 404 for nonexistent task."""
        response = client.patch(
            "/api/tasks/nonexistent-id/complete", headers=auth_headers
        )
        assert response.status_code == 404
