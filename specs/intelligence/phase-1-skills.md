# Phase I: Reusable Intelligence Skills

> **Bonus Points**: +200 for Reusable Intelligence

This document describes the custom Claude Code skills created for Phase I of the Todo hackathon project.

## Overview

Phase I skills automate the setup and generation of a Python console application with in-memory task management.

```
.claude/commands/
├── todo.setup.md    # Project initialization
├── todo.crud.md     # CRUD operations generator
└── todo.test.md     # Test suite generator
```

## Skills Catalog

### `/todo.setup` - Project Initialization

**Purpose**: Initialize a complete Python console application with UV, pytest, and proper project structure.

**Invocation**:
```
/todo.setup
```

**What it generates**:
- Project structure (`src/`, `tests/`)
- UV project with `pyproject.toml`
- Dependencies (typer, rich, pytest, ruff, mypy)
- Configuration for linting, formatting, and type checking
- Base entry point (`src/main.py`)
- Test fixtures (`tests/conftest.py`)
- `.gitignore` entries

**Time saved**: ~30 minutes of manual setup

---

### `/todo.crud` - CRUD Operations Generator

**Purpose**: Generate the complete Task model and CRUD service for in-memory task management.

**Invocation**:
```
/todo.crud
```

**What it generates**:

| Component | File | Description |
|-----------|------|-------------|
| Task Model | `src/models/task.py` | Dataclass with validation |
| Task Service | `src/services/task_service.py` | CRUD operations + stats |
| CLI Commands | `src/cli/commands.py` | All 5 basic feature commands |
| Entry Point | `src/main.py` | Updated with task commands |

**Basic Features Implemented**:
- `todo task add <title>` - Add Task
- `todo task delete <id>` - Delete Task
- `todo task update <id>` - Update Task
- `todo task list` - View Task List
- `todo task complete <id>` - Mark as Complete

**Time saved**: ~1 hour of implementation

---

### `/todo.test` - Test Suite Generator

**Purpose**: Generate comprehensive test suites following TDD principles.

**Invocation**:
```
/todo.test           # Generate all tests
/todo.test unit      # Unit tests only
/todo.test integration   # Integration tests only
```

**What it generates**:

| Test Suite | File | Tests |
|------------|------|-------|
| Task Model | `tests/unit/test_task.py` | 15 tests |
| Task Service | `tests/unit/test_task_service.py` | 20 tests |
| CLI Integration | `tests/integration/test_cli.py` | 12 tests |
| **Total** | | **47 tests** |

**Test Coverage**:
- Creation and validation
- CRUD operations
- Status transitions
- Error handling
- CLI command execution

**Time saved**: ~1 hour of test writing

---

## Usage Workflow

```mermaid
graph LR
    A[/todo.setup] --> B[/todo.crud]
    B --> C[/todo.test]
    C --> D[Run Tests]
    D --> E[/sp.specify]
```

### Recommended Sequence

1. **Initialize project**:
   ```
   /todo.setup
   ```

2. **Generate CRUD operations**:
   ```
   /todo.crud
   ```

3. **Generate tests**:
   ```
   /todo.test
   ```

4. **Verify everything works**:
   ```bash
   uv run pytest
   uv run todo task add "Test task"
   uv run todo task list
   ```

5. **Create specification**:
   ```
   /sp.specify Phase I console app
   ```

---

## Skill Design Principles

These skills follow the constitution's principles:

| Principle | Implementation |
|-----------|----------------|
| **Spec-Driven** | Skills generate code that matches constitution requirements |
| **No Manual Coding** | Full implementation generated, no hand-coding needed |
| **Test-First** | Tests generated to verify all features |
| **Simplicity** | Minimal dependencies, clean architecture |
| **Security** | Input validation, no hardcoded secrets |

---

## Future Skills (Phases II-V)

Skills for later phases will be created incrementally:

| Phase | Skills | Status |
|-------|--------|--------|
| Phase I | `todo.setup`, `todo.crud`, `todo.test` | ✅ Created |
| Phase II | `todo.api`, `todo.component`, `todo.db` | 🔜 Pending |
| Phase III | `todo.mcp-tool`, `todo.agent` | 🔜 Pending |
| Phase IV | `todo.dockerfile`, `todo.helm` | 🔜 Pending |
| Phase V | `todo.dapr`, `todo.kafka` | 🔜 Pending |

---

## Metrics

| Metric | Value |
|--------|-------|
| Skills Created | 3 |
| Total Lines Generated | ~800 |
| Time Saved | ~2.5 hours |
| Test Coverage | 47 tests |
