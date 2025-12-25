# Data Model: Phase I Console Todo Application

**Feature**: 001-phase1-console
**Date**: 2025-12-25
**Spec**: [spec.md](./spec.md)

## Overview

This document defines the data structures for Phase I in-memory storage. All data is ephemeral and lost when the application exits.

## Core Entity: Task

### Definition

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


class TaskStatus(Enum):
    """Task completion status."""
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass
class Task:
    """
    Represents a todo item.

    Attributes:
        id: Unique 8-character identifier (first 8 chars of UUID4)
        title: Required task title (1-200 characters)
        description: Optional task description (up to 1000 characters)
        status: Current completion status (pending/completed)
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last modified
    """
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    id: str = field(default_factory=lambda: uuid4().hex[:8])
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate task fields after initialization."""
        self._validate_title()
        self._validate_description()

    def _validate_title(self) -> None:
        """Validate title is non-empty and within length limits."""
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")

    def _validate_description(self) -> None:
        """Validate description length."""
        if len(self.description) > 1000:
            raise ValueError("Task description cannot exceed 1000 characters")
```

## Field Specifications

| Field | Type | Required | Constraints | Default |
|-------|------|----------|-------------|---------|
| id | str | Auto | 8 characters, hex | UUID4[:8] |
| title | str | Yes | 1-200 chars, non-empty | - |
| description | str | No | 0-1000 chars | "" |
| status | TaskStatus | No | pending/completed | pending |
| created_at | datetime | Auto | ISO 8601 | now() |
| updated_at | datetime | Auto | ISO 8601 | now() |

## Storage Structure

### In-Memory Dictionary

```python
# Global storage (module-level)
_tasks: dict[str, Task] = {}

# Key: task.id (8-char string)
# Value: Task instance
```

### Operations Complexity

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Add | O(1) | Dict insertion |
| Get by ID | O(1) | Dict lookup |
| List all | O(n) | Iterate values |
| Update | O(1) | Dict lookup + update |
| Delete | O(1) | Dict removal |
| Filter by status | O(n) | Iterate and filter |

## Validation Rules

### Title Validation

1. **Not empty**: `title.strip()` must have length > 0
2. **Max length**: Must not exceed 200 characters
3. **Special characters**: All printable characters allowed

### Description Validation

1. **Optional**: Empty string is valid
2. **Max length**: Must not exceed 1000 characters

### Status Transitions

```
+----------+     mark_complete()     +-----------+
| PENDING  | ----------------------> | COMPLETED |
+----------+ <---------------------- +-----------+
              mark_incomplete()
```

Both transitions are allowed at any time (toggle behavior).

## Display Formats

### Task ID Format

- **Storage**: `a1b2c3d4` (8 lowercase hex characters)
- **Display**: `a1b2c3d4` (same as storage)

### Timestamp Formats

| Context | Format | Example |
|---------|--------|---------|
| Storage | ISO 8601 | `2025-12-25T10:30:00` |
| Display | Human-readable | `Dec 25, 2025 10:30 AM` |

### Status Indicators

| Status | CLI Display | Color |
|--------|-------------|-------|
| PENDING | `[ ]` or `pending` | Yellow |
| COMPLETED | `[x]` or `completed` | Green |

## Error Responses

| Error Case | Message Format |
|------------|----------------|
| Empty title | "Task title cannot be empty" |
| Title too long | "Task title cannot exceed 200 characters" |
| Description too long | "Task description cannot exceed 1000 characters" |
| Task not found | "Task with ID '{id}' not found" |

## Relationships

Phase I has a single entity with no relationships. Future phases will add:

- Phase II: Persistence (Neon Serverless PostgreSQL)
- Phase III: AI-generated subtasks, categories
- Phase IV+: Multi-user, projects, tags

## Migration Notes

For Phase II persistence:
- `id` maps directly to primary key
- `status` enum stored as string value
- `created_at`/`updated_at` stored as ISO 8601 strings
- No schema migrations needed (greenfield in each phase)
