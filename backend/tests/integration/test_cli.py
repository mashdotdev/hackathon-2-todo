"""Integration tests for Todo CLI."""

import pytest
from typer.testing import CliRunner

from src.main import app
from src.services.task_service import get_task_service


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
        # Extract ID from output (format: "ID: xxxxxxxx)")
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


class TestCLIShowTask:
    """Tests for show command."""

    def test_show_task_details(self, runner: CliRunner) -> None:
        """Show command should display task details."""
        add_result = runner.invoke(app, ["task", "add", "Show me", "--desc", "Details"])
        task_id = add_result.output.split("ID: ")[1].split(")")[0]

        result = runner.invoke(app, ["task", "show", task_id])
        assert result.exit_code == 0
        assert "Show me" in result.output
        assert "Details" in result.output

    def test_show_nonexistent_task(self, runner: CliRunner) -> None:
        """Show nonexistent task should fail."""
        result = runner.invoke(app, ["task", "show", "nonexistent"])
        assert result.exit_code == 1
        assert "not found" in result.output


class TestCLIStats:
    """Tests for stats command."""

    def test_stats_empty(self, runner: CliRunner) -> None:
        """Stats with no tasks should show zeros."""
        result = runner.invoke(app, ["task", "stats"])
        assert result.exit_code == 0
        assert "Total tasks:" in result.output
        assert "0" in result.output

    def test_stats_with_tasks(self, runner: CliRunner) -> None:
        """Stats should reflect actual counts."""
        runner.invoke(app, ["task", "add", "Task 1"])
        runner.invoke(app, ["task", "add", "Task 2"])
        result = runner.invoke(app, ["task", "stats"])
        assert result.exit_code == 0
        assert "Total tasks:" in result.output
