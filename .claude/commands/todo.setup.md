---
description: Initialize Phase I Python console app with UV, pytest, and proper project structure
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

This skill initializes a Python console application for Phase I of the Todo hackathon project. It sets up the project structure, dependencies, and configuration following the constitution's technology stack requirements.

## Execution Steps

### 1. Verify Prerequisites

Check that the following are available:
- Python 3.13+ installed
- UV package manager installed (`uv --version`)
- Git repository initialized

If any prerequisite is missing, provide installation instructions and stop.

### 2. Create Project Structure

Create the following directory structure at repository root:

```
src/
├── __init__.py
├── main.py              # CLI entry point
├── models/
│   ├── __init__.py
│   └── task.py          # Task model (in-memory)
├── services/
│   ├── __init__.py
│   └── task_service.py  # CRUD operations
└── cli/
    ├── __init__.py
    └── commands.py      # CLI command handlers

tests/
├── __init__.py
├── conftest.py          # pytest fixtures
├── unit/
│   ├── __init__.py
│   └── test_task.py
└── integration/
    ├── __init__.py
    └── test_cli.py
```

### 3. Initialize UV Project

Run the following commands:

```bash
# Initialize UV project if pyproject.toml doesn't exist
uv init --name todo-console --python ">=3.13"

# Add dependencies
uv add typer rich

# Add dev dependencies
uv add --dev pytest pytest-cov ruff mypy
```

### 4. Configure pyproject.toml

Ensure pyproject.toml includes:

```toml
[project]
name = "todo-console"
version = "0.1.0"
description = "Phase I: In-memory Todo Console Application"
requires-python = ">=3.13"
dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[project.scripts]
todo = "src.main:app"

[tool.ruff]
line-length = 88
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_ignores = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --cov=src --cov-report=term-missing"
```

### 5. Create Base Files

**src/__init__.py**:
```python
"""Todo Console Application - Phase I."""
```

**src/main.py**:
```python
"""Main entry point for Todo CLI application."""
import typer

app = typer.Typer(
    name="todo",
    help="Todo Console Application - Phase I",
    add_completion=False,
)


@app.command()
def version() -> None:
    """Show application version."""
    typer.echo("Todo Console v0.1.0")


if __name__ == "__main__":
    app()
```

**tests/conftest.py**:
```python
"""Pytest fixtures for Todo application tests."""
import pytest


@pytest.fixture
def sample_task_data() -> dict[str, str]:
    """Return sample task data for testing."""
    return {
        "title": "Test Task",
        "description": "This is a test task",
    }
```

### 6. Create .gitignore Entries

Append to .gitignore if not present:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
.uv/

# Testing
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/

# IDE
.vscode/
.idea/

# Environment
.env
.env.local
```

### 7. Verify Setup

Run verification commands:
```bash
# Sync dependencies
uv sync

# Run linting
uv run ruff check src/

# Run type checking
uv run mypy src/

# Run tests (should pass with no tests yet)
uv run pytest

# Verify CLI works
uv run todo version
```

### 8. Output Summary

Report:
- ✅ Project structure created
- ✅ UV project initialized with dependencies
- ✅ Linting and type checking configured
- ✅ Test framework ready
- ✅ CLI entry point working

**Next Steps**:
1. Run `/todo.crud` to generate Task model and CRUD operations
2. Run `/todo.test` to generate test cases
3. Run `/sp.specify` to create Phase I specification

---

## Notes

- This skill follows the constitution's Phase I technology stack
- Uses Typer for CLI (modern, type-safe alternative to argparse)
- Uses Rich for beautiful terminal output
- Configured for strict type checking with mypy
