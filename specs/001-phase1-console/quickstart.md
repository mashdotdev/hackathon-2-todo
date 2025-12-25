# Quickstart Guide: Phase I Console Todo Application

**Feature**: 001-phase1-console
**Date**: 2025-12-25

## Prerequisites

- Python 3.13+
- UV package manager

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd hackathon-2-todo

# Install dependencies with UV
uv sync

# Or install in development mode
uv pip install -e ".[dev]"
```

## Running the Application

```bash
# Run with UV
uv run python -m src.main

# Or after installation
todo --help
```

## Basic Commands

### Add a Task

```bash
# Add task with title only
todo add "Buy groceries"

# Add task with title and description
todo add "Buy groceries" --description "Milk, eggs, bread"
```

**Output**:
```
✓ Task created: a1b2c3d4
  Title: Buy groceries
```

### View All Tasks

```bash
# View all tasks
todo list

# View only pending tasks
todo list --status pending

# View only completed tasks
todo list --status completed
```

**Output**:
```
┌──────────┬────────────────┬───────────┬─────────────────┐
│ ID       │ Title          │ Status    │ Created         │
├──────────┼────────────────┼───────────┼─────────────────┤
│ a1b2c3d4 │ Buy groceries  │ [ ] pending│ Dec 25, 10:30  │
│ e5f6g7h8 │ Call mom       │ [x] done  │ Dec 25, 09:15  │
└──────────┴────────────────┴───────────┴─────────────────┘

Total: 2 | Pending: 1 | Completed: 1
```

### Mark Task Complete/Incomplete

```bash
# Mark as complete
todo complete a1b2c3d4

# Toggle back to pending
todo complete a1b2c3d4
```

**Output**:
```
✓ Task a1b2c3d4 marked as completed
```

### Update a Task

```bash
# Update title
todo update a1b2c3d4 --title "Buy groceries and snacks"

# Update description
todo update a1b2c3d4 --description "Milk, eggs, bread, chips"

# Update both
todo update a1b2c3d4 --title "Shopping" --description "Weekly groceries"
```

**Output**:
```
✓ Task a1b2c3d4 updated
  Title: Buy groceries and snacks
```

### Delete a Task

```bash
# Delete with confirmation prompt
todo delete a1b2c3d4

# Delete without confirmation (force)
todo delete a1b2c3d4 --force
```

**Output**:
```
Delete task "Buy groceries"? [y/N]: y
✓ Task a1b2c3d4 deleted
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_task.py

# Run with verbose output
uv run pytest -v
```

### Code Quality

```bash
# Format code
uv run ruff format src tests

# Lint code
uv run ruff check src tests

# Type checking
uv run mypy src
```

### Project Structure

```
hackathon-2-todo/
├── src/
│   ├── __init__.py
│   ├── main.py              # CLI entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py          # Task dataclass
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py  # CRUD operations
│   └── cli/
│       ├── __init__.py
│       └── commands.py      # Typer commands
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── unit/
│   │   ├── test_task.py
│   │   └── test_task_service.py
│   └── integration/
│       └── test_cli.py
└── pyproject.toml
```

## Important Notes

- **In-Memory Storage**: All tasks are stored in memory only. Data is lost when the application exits.
- **Single Session**: This is a Phase I limitation. Persistence comes in Phase II.
- **Task IDs**: 8-character hex identifiers (e.g., `a1b2c3d4`)

## Troubleshooting

### Command Not Found

```bash
# Use module syntax instead
uv run python -m src.main --help
```

### Permission Errors

```bash
# On Unix systems, ensure script is executable
chmod +x src/main.py
```

### Invalid Task ID

```
Error: Task with ID 'xyz12345' not found

# List tasks to find valid IDs
todo list
```

## Next Steps

After Phase I:
- Phase II adds Neon PostgreSQL persistence
- Phase III adds AI chatbot interface
- Phase IV adds Kubernetes deployment
- Phase V adds cloud deployment with monitoring
