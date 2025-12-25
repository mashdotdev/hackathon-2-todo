# Research: Phase I Console Todo Application

**Feature**: 001-phase1-console
**Date**: 2025-12-25

## Overview

This document captures research findings and technical decisions for Phase I implementation.

## Technology Decisions

### 1. CLI Framework: Typer

**Decision**: Use Typer for command-line interface

**Rationale**:
- Type hints automatically generate CLI arguments and options
- Built on Click but with modern Python features
- Rich integration for beautiful terminal output
- Less boilerplate than argparse or raw Click
- Excellent documentation and active maintenance

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| argparse | Too verbose, manual type conversion |
| Click | Typer provides better DX with type hints |
| Fire | Less control over CLI structure |

### 2. Terminal Output: Rich

**Decision**: Use Rich for terminal formatting

**Rationale**:
- Beautiful tables for task list display
- Colored output for status indicators (green/yellow)
- Easy progress bars and spinners if needed
- Seamless integration with Typer
- No additional terminal dependencies

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| Colorama | Only colors, no tables |
| Tabulate | Tables only, no colors |
| Plain print | Poor user experience |

### 3. Data Storage: In-Memory Dict

**Decision**: Use Python dictionary with task ID as key

**Rationale**:
- Simplest possible storage for Phase I
- O(1) lookup by ID
- No persistence overhead
- Easy to understand and test
- Constitution Principle IX (Simplicity) compliance

**Data Structure**:
```python
_tasks: dict[str, Task] = {}  # key: task_id, value: Task object
```

### 4. Task ID Format: Short UUID

**Decision**: Use first 8 characters of UUID4

**Rationale**:
- Short enough for user to type (8 chars vs 36 for full UUID)
- Collision probability negligible for ~100 tasks per session
- No sequential ordering (privacy-friendly)
- Standard library, no dependencies

**Format Example**: `a1b2c3d4`

### 5. Task Model: Python Dataclass

**Decision**: Use `@dataclass` with validation in `__post_init__`

**Rationale**:
- Built-in Python feature, no dependencies
- Automatic `__init__`, `__repr__`, `__eq__`
- Type hints for IDE support and mypy
- Easy to extend for Phase II (add fields)

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| Pydantic | Over-engineered for Phase I |
| NamedTuple | Immutable, harder to update |
| Plain class | More boilerplate |

### 6. Testing Strategy

**Decision**: pytest with fixtures and CLI runner

**Rationale**:
- pytest is constitution-mandated
- Fixtures enable clean test setup/teardown
- `typer.testing.CliRunner` for CLI integration tests
- pytest-cov for coverage reporting

**Test Categories**:
| Category | Purpose | Count |
|----------|---------|-------|
| Unit (Task) | Model validation | ~15 tests |
| Unit (Service) | CRUD operations | ~20 tests |
| Integration (CLI) | End-to-end commands | ~12 tests |

## Best Practices Applied

### Python Project Structure

Following Python packaging best practices:
- `src/` layout for proper imports
- `pyproject.toml` for modern packaging
- Type hints everywhere (mypy strict mode)
- Docstrings for public functions

### Code Quality

Following constitution Code Quality Standards:
- `ruff` for linting and formatting (faster than black+flake8)
- `mypy` in strict mode for type checking
- Pre-commit ready (will add in later phases)

### Error Handling

- Validation errors raise `ValueError` with descriptive message
- CLI catches exceptions and displays user-friendly errors
- Non-zero exit codes for failures

## Resolved Clarifications

| Topic | Resolution |
|-------|------------|
| Task ID format | 8-char UUID prefix (e.g., `a1b2c3d4`) |
| Timestamp format | ISO 8601 for storage, human-readable for display |
| Delete confirmation | Prompt with y/n, skip with `--force` flag |
| Empty list behavior | Display "No tasks found" message |
| Status filter values | `all`, `pending`, `completed` |

## Dependencies Summary

| Package | Version | Purpose |
|---------|---------|---------|
| typer | >=0.9.0 | CLI framework |
| rich | >=13.0.0 | Terminal output |
| pytest | >=8.0.0 | Testing (dev) |
| pytest-cov | >=4.0.0 | Coverage (dev) |
| ruff | >=0.1.0 | Linting (dev) |
| mypy | >=1.0.0 | Type checking (dev) |

## Next Steps

1. Generate data model (`data-model.md`)
2. Generate quickstart guide (`quickstart.md`)
3. Proceed to task breakdown (`/sp.tasks`)
