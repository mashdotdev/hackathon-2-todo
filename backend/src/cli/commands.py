"""CLI commands for Todo application."""

import sys

import typer
from rich.console import Console
from rich.table import Table

from src.models.task import TaskStatus
from src.services.task_service import get_task_service

# Use legacy_windows mode for better Windows compatibility
console = Console(legacy_windows=sys.platform == "win32")
app = typer.Typer(help="Manage your todo tasks")

# ASCII-safe status indicators
OK = "[green]OK[/green]"
FAIL = "[red]X[/red]"
PENDING = "[yellow]o[/yellow]"
DONE = "[green]+[/green]"


@app.command("add")
def add_task(
    title: str = typer.Argument(..., help="Task title"),
    description: str | None = typer.Option(
        None, "--desc", "-d", help="Task description"
    ),
) -> None:
    """Add a new task to the list."""
    service = get_task_service()
    try:
        task = service.add_task(title=title, description=description)
        console.print(f"{OK} Task added: [bold]{task.title}[/bold] (ID: {task.id})")
    except ValueError as e:
        console.print(f"[red]X[/red] Error: {e}")
        raise typer.Exit(1)


@app.command("list")
def list_tasks(
    status: str | None = typer.Option(
        None, "--status", "-s", help="Filter by status: pending, completed, all"
    ),
    show_all: bool = typer.Option(
        False, "--all", "-a", help="Show all tasks (same as --status all)"
    ),
) -> None:
    """List all tasks."""
    service = get_task_service()

    # Determine filter
    filter_status: TaskStatus | None = None
    if status and status.lower() != "all":
        try:
            filter_status = TaskStatus(status.lower())
        except ValueError:
            console.print(
                f"[red]X[/red] Invalid status: {status}. Use: pending, completed, all"
            )
            raise typer.Exit(1)

    # show_all is just a convenience flag, same as --status all
    _ = show_all  # Explicitly mark as intentionally unused

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
        status_icon = "[green]+[/green]" if task.is_completed else "[yellow]o[/yellow]"
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
    title: str | None = typer.Option(None, "--title", "-t", help="New title"),
    description: str | None = typer.Option(
        None, "--desc", "-d", help="New description"
    ),
) -> None:
    """Update an existing task."""
    if title is None and description is None:
        console.print("[red]X[/red] Provide at least --title or --desc to update")
        raise typer.Exit(1)

    service = get_task_service()
    try:
        task = service.update_task(
            task_id=task_id, title=title, description=description
        )
        if task is None:
            console.print(f"[red]X[/red] Task not found: {task_id}")
            raise typer.Exit(1)
        console.print(f"[green]+[/green] Task updated: [bold]{task.title}[/bold]")
    except ValueError as e:
        console.print(f"[red]X[/red] Error: {e}")
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
        console.print(f"[red]X[/red] Task not found: {task_id}")
        raise typer.Exit(1)

    # Confirm deletion
    if not force:
        confirm = typer.confirm(f"Delete task '{task.title}'?")
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(0)

    service.delete_task(task_id)
    console.print(f"[green]+[/green] Task deleted: [bold]{task.title}[/bold]")


@app.command("complete")
def complete_task(
    task_id: str = typer.Argument(..., help="Task ID to mark complete"),
) -> None:
    """Mark a task as completed."""
    service = get_task_service()
    task = service.complete_task(task_id)

    if task is None:
        console.print(f"[red]X[/red] Task not found: {task_id}")
        raise typer.Exit(1)

    console.print(f"[green]+[/green] Task completed: [bold]{task.title}[/bold]")


@app.command("uncomplete")
def uncomplete_task(
    task_id: str = typer.Argument(..., help="Task ID to mark incomplete"),
) -> None:
    """Mark a task as incomplete/pending."""
    service = get_task_service()
    task = service.uncomplete_task(task_id)

    if task is None:
        console.print(f"[red]X[/red] Task not found: {task_id}")
        raise typer.Exit(1)

    console.print(f"[yellow]o[/yellow] Task marked pending: [bold]{task.title}[/bold]")


@app.command("show")
def show_task(
    task_id: str = typer.Argument(..., help="Task ID to show"),
) -> None:
    """Show details of a specific task."""
    service = get_task_service()
    task = service.get_task(task_id)

    if task is None:
        console.print(f"[red]X[/red] Task not found: {task_id}")
        raise typer.Exit(1)

    status_str = (
        "[green]Completed[/green]" if task.is_completed else "[yellow]Pending[/yellow]"
    )
    console.print("\n[bold]Task Details[/bold]")
    console.print(f"  ID:          {task.id}")
    console.print(f"  Title:       {task.title}")
    console.print(f"  Description: {task.description or '-'}")
    console.print(f"  Status:      {status_str}")
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

    if stats["total"] > 0:
        percentage = (stats["completed"] / stats["total"]) * 100
        console.print(f"  Completion rate: {percentage:.1f}%")
