# Data Model: Phase II Full-Stack Web Application

**Feature**: 002-phase2-web
**Date**: 2025-12-25
**Spec**: [spec.md](./spec.md)

## Overview

This document defines the data structures for Phase II persistent storage using Neon PostgreSQL with SQLModel ORM.

## Entities

### User

Represents a registered user who can own tasks.

```python
from datetime import datetime
from sqlmodel import SQLModel, Field
from uuid import uuid4


class User(SQLModel, table=True):
    """
    Registered user account.

    Attributes:
        id: UUID primary key
        email: Unique email address (used for login)
        password_hash: Bcrypt hashed password
        created_at: Account creation timestamp
        is_active: Account status (for future soft delete)
    """
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
```

### Task

Represents a todo item owned by a user.

```python
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field
from uuid import uuid4


class TaskStatus(str, Enum):
    """Task completion status."""
    PENDING = "pending"
    COMPLETED = "completed"


class Task(SQLModel, table=True):
    """
    Todo task item.

    Attributes:
        id: UUID primary key
        title: Task title (1-200 characters)
        description: Optional description (max 1000 characters)
        status: pending or completed
        created_at: Task creation timestamp
        updated_at: Last modification timestamp
        user_id: Foreign key to owning user
    """
    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: str = Field(foreign_key="users.id", index=True)
```

## Entity Relationship Diagram

```
┌─────────────────────┐         ┌─────────────────────┐
│        User         │         │        Task         │
├─────────────────────┤         ├─────────────────────┤
│ id: UUID (PK)       │────┐    │ id: UUID (PK)       │
│ email: str (unique) │    │    │ title: str          │
│ password_hash: str  │    │    │ description: str?   │
│ created_at: datetime│    │    │ status: enum        │
│ is_active: bool     │    └───→│ user_id: UUID (FK)  │
└─────────────────────┘         │ created_at: datetime│
                                │ updated_at: datetime│
        1                       └─────────────────────┘
        │                                 ↑
        │                                 │
        └────────── owns ────────────────→*
                  (one-to-many)
```

## Field Specifications

### User Fields

| Field | Type | Required | Constraints | Default |
|-------|------|----------|-------------|---------|
| id | UUID | Auto | Primary key | uuid4() |
| email | str | Yes | Unique, max 255, valid email format | - |
| password_hash | str | Yes | Bcrypt hash, max 255 | - |
| created_at | datetime | Auto | UTC timestamp | utcnow() |
| is_active | bool | No | - | True |

### Task Fields

| Field | Type | Required | Constraints | Default |
|-------|------|----------|-------------|---------|
| id | UUID | Auto | Primary key | uuid4() |
| title | str | Yes | 1-200 chars, non-empty | - |
| description | str | No | Max 1000 chars | None |
| status | enum | No | pending/completed | pending |
| created_at | datetime | Auto | UTC timestamp | utcnow() |
| updated_at | datetime | Auto | UTC timestamp | utcnow() |
| user_id | UUID | Yes | FK to users.id | - |

## Validation Rules

### User Validation

1. **Email**:
   - Must be valid email format (RFC 5322)
   - Must be unique across all users
   - Case-insensitive comparison (store lowercase)

2. **Password** (before hashing):
   - Minimum 8 characters
   - No maximum (hashed result is fixed size)

### Task Validation

1. **Title**:
   - Required, non-empty after trimming whitespace
   - Maximum 200 characters
   - Whitespace trimmed on save

2. **Description**:
   - Optional (null allowed)
   - Maximum 1000 characters if provided

3. **User Isolation**:
   - All task queries MUST filter by user_id
   - Users can only access their own tasks

## Database Indexes

```sql
-- Automatic from Field definitions
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Recommended for query patterns
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
```

## Migration Strategy

### Initial Schema (Phase II)

```sql
-- 001_initial_schema.sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE tasks (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
```

### Migration from Phase I

Phase I uses in-memory storage only. No data migration needed - users start fresh with Phase II.

## Pydantic Schemas (API Layer)

```python
from pydantic import BaseModel, EmailStr
from datetime import datetime


# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str  # Min 8 chars, validated in route


class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime


# Task schemas
class TaskCreate(BaseModel):
    title: str  # 1-200 chars
    description: str | None = None  # Max 1000 chars


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime
```

## State Transitions

### Task Status

```
┌──────────┐     mark_complete()     ┌───────────┐
│ PENDING  │ ──────────────────────→ │ COMPLETED │
└──────────┘ ←────────────────────── └───────────┘
              mark_incomplete()
```

Both transitions are allowed at any time (toggle behavior).

### User Status

```
┌──────────┐     deactivate()     ┌────────────┐
│ ACTIVE   │ ──────────────────→  │ INACTIVE   │
└──────────┘                      └────────────┘
```

Note: User deactivation is out of scope for Phase II but schema supports it.

## Soft Delete Strategy

Per constitution, soft deletes are preferred:

- **Users**: Use `is_active` field (already included)
- **Tasks**: Hard delete for Phase II (soft delete added in Phase IV if needed)

Rationale: Task soft delete adds complexity without clear benefit for MVP.

## Timezone Handling

- All timestamps stored in UTC
- Frontend converts to local timezone for display
- API accepts/returns ISO 8601 format: `2025-12-25T10:30:00Z`
