"""Main entry point for Todo CLI application."""

import typer

from src.cli.commands import app as task_app

app = typer.Typer(
    name="todo",
    help="Todo Console Application - Phase I\n\nManage your tasks.",
    add_completion=False,
    no_args_is_help=True,
)

# Add task commands directly to main app
app.add_typer(task_app, name="task")


@app.command()
def version() -> None:
    """Show application version."""
    typer.echo("Todo Console v0.1.0 (Phase I)")


if __name__ == "__main__":
    app()
