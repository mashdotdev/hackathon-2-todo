# Data Model: Phase V - Cloud Deployment with Event-Driven Architecture

**Feature**: Phase V
**Date**: 2025-12-30
**Database**: PostgreSQL (Neon Serverless)

## Overview

Phase V extends the existing Task model with advanced features and introduces four new entities for event-driven architecture.

---

## Entity Relationship Diagram

```
┌─────────────────┐
│      User       │
│  (from Phase II)│
└────────┬────────┘
         │ 1
         │
         │ *
┌────────┴────────────────────────┐
│         Task (Extended)         │
│─────────────────────────────────│
│ task_id: UUID (PK)              │
│ user_id: UUID (FK)              │
│ title: String                   │
│ description: String             │
│ status: Enum                    │
│ priority: Enum (NEW)            │  ┌──────────────────────┐
│ tags: Array<String> (NEW)       │  │   TaskEvent (NEW)    │
│ due_date: Timestamp (NEW)       │──┤ Published to Kafka   │
│ recurrence_pattern: Enum (NEW)  │  └──────────────────────┘
│ reminder_lead_time: Int (NEW)   │
│ created_at: Timestamp           │
│ updated_at: Timestamp           │
└─────────┬────────────────────────┘
          │ 1
          │
          │ 0..1
┌─────────┴──────────────────────┐
│ RecurringTaskSchedule (NEW)   │
│───────────────────────────────│
│ schedule_id: UUID (PK)        │
│ parent_task_id: UUID (FK)     │
│ recurrence_pattern: Enum      │
│ next_execution_time: Timestamp│
│ is_active: Boolean            │
└───────────────────────────────┘

┌──────────────────────────────┐       ┌──────────────────────────┐
│   Notification (NEW)          │       │   AuditLog (NEW)         │
│──────────────────────────────│       │──────────────────────────│
│ notification_id: UUID (PK)   │       │ audit_id: UUID (PK)      │
│ user_id: UUID (FK)           │       │ user_id: UUID            │
│ task_id: UUID (FK, nullable) │       │ action_type: String      │
│ notification_type: Enum      │       │ resource_type: String    │
│ message: Text                │       │ resource_id: UUID        │
│ sent_at: Timestamp           │       │ event_data: JSON         │
│ delivery_status: Enum        │       │ correlation_id: UUID     │
│ created_at: Timestamp        │       │ timestamp: Timestamp     │
└──────────────────────────────┘       └──────────────────────────┘
```

---

## 1. Task (Extended)

**Purpose**: Core todo item with advanced features for priorities, tags, scheduling, and recurrence.

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import ARRAY, String
from typing import Optional, List
from enum import Enum
from datetime import datetime
import uuid

class PriorityEnum(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class RecurrencePatternEnum(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class StatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    task_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.user_id", index=True)

    # Existing fields (Phase II)
    title: str = Field(max_length=200)
    description: Optional[str] = None
    status: StatusEnum = Field(default=StatusEnum.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # NEW: Phase V advanced fields
    priority: PriorityEnum = Field(default=PriorityEnum.MEDIUM)
    tags: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    due_date: Optional[datetime] = None
    recurrence_pattern: RecurrencePatternEnum = Field(default=RecurrencePatternEnum.NONE)
    reminder_lead_time: Optional[int] = None  # minutes before due_date

    class Config:
        schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "status": "pending",
                "priority": "High",
                "tags": ["personal", "errands"],
                "due_date": "2025-12-31T18:00:00Z",
                "recurrence_pattern": "weekly",
                "reminder_lead_time": 60  # 1 hour before
            }
        }
```

### Database Schema

```sql
ALTER TABLE tasks
    ADD COLUMN priority VARCHAR(10) DEFAULT 'Medium' CHECK (priority IN ('High', 'Medium', 'Low')),
    ADD COLUMN tags TEXT[] DEFAULT '{}',
    ADD COLUMN due_date TIMESTAMP,
    ADD COLUMN recurrence_pattern VARCHAR(20) DEFAULT 'none' CHECK (recurrence_pattern IN ('none', 'daily', 'weekly', 'monthly')),
    ADD COLUMN reminder_lead_time INTEGER;

CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_recurrence ON tasks(recurrence_pattern) WHERE recurrence_pattern != 'none';
```

### Validation Rules

- `title`: Required, 1-200 characters
- `priority`: Must be High, Medium, or Low
- `tags`: Max 10 tags, each max 50 characters
- `due_date`: Must be in future (> now)
- `recurrence_pattern`: Must be none, daily, weekly, or monthly
- `reminder_lead_time`: If set, must be > 0 and due_date must be set

---

## 2. TaskEvent (NEW)

**Purpose**: Immutable event log for all task operations, published to Kafka for event-driven processing.

### SQLModel Definition

```python
class TaskEventType(str, Enum):
    TASK_CREATED = "task-created"
    TASK_UPDATED = "task-updated"
    TASK_COMPLETED = "task-completed"
    TASK_DELETED = "task-deleted"

class TaskEvent(SQLModel, table=True):
    __tablename__ = "task_events"

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    event_type: TaskEventType
    task_id: uuid.UUID = Field(index=True)
    user_id: uuid.UUID = Field(index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    payload: dict = Field(sa_column=Column(JSON))  # Task snapshot
    published_to_kafka: bool = Field(default=False)

    class Config:
        schema_extra = {
            "example": {
                "event_type": "task-created",
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "payload": {
                    "title": "Buy groceries",
                    "priority": "High",
                    "tags": ["personal"]
                }
            }
        }
```

### Database Schema

```sql
CREATE TABLE task_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,
    task_id UUID NOT NULL,
    user_id UUID NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    payload JSONB NOT NULL,
    published_to_kafka BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_task_events_task_id ON task_events(task_id);
CREATE INDEX idx_task_events_user_id ON task_events(user_id);
CREATE INDEX idx_task_events_timestamp ON task_events(timestamp DESC);
CREATE INDEX idx_task_events_type ON task_events(event_type);
```

### Kafka Message Format

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "task-created",
  "task_id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440002",
  "timestamp": "2025-12-30T12:00:00Z",
  "payload": {
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "status": "pending",
    "priority": "High",
    "tags": ["personal", "errands"]
  }
}
```

**Partitioning**: Kafka messages partitioned by `task_id` to ensure ordering.

---

## 3. RecurringTaskSchedule (NEW)

**Purpose**: Tracks recurring task schedules and next execution times for automatic task generation.

### SQLModel Definition

```python
class RecurringTaskSchedule(SQLModel, table=True):
    __tablename__ = "recurring_task_schedules"

    schedule_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    parent_task_id: uuid.UUID = Field(foreign_key="tasks.task_id", unique=True)
    user_id: uuid.UUID = Field(index=True)
    recurrence_pattern: RecurrencePatternEnum
    next_execution_time: datetime = Field(index=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_executed_at: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "parent_task_id": "550e8400-e29b-41d4-a716-446655440000",
                "recurrence_pattern": "weekly",
                "next_execution_time": "2026-01-06T00:00:00Z",
                "is_active": True
            }
        }
```

### Database Schema

```sql
CREATE TABLE recurring_task_schedules (
    schedule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_task_id UUID UNIQUE NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    recurrence_pattern VARCHAR(20) NOT NULL,
    next_execution_time TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_executed_at TIMESTAMP
);

CREATE INDEX idx_schedules_next_execution ON recurring_task_schedules(next_execution_time)
    WHERE is_active = TRUE;
CREATE INDEX idx_schedules_user ON recurring_task_schedules(user_id);
```

### Next Execution Calculation

```python
from dateutil.relativedelta import relativedelta

def calculate_next_execution(current: datetime, pattern: RecurrencePatternEnum) -> datetime:
    if pattern == RecurrencePatternEnum.DAILY:
        return current + relativedelta(days=1)
    elif pattern == RecurrencePatternEnum.WEEKLY:
        return current + relativedelta(weeks=1)
    elif pattern == RecurrencePatternEnum.MONTHLY:
        return current + relativedelta(months=1)
    else:
        raise ValueError(f"Invalid recurrence pattern: {pattern}")
```

---

## 4. Notification (NEW)

**Purpose**: In-app notifications for task reminders and events.

### SQLModel Definition

```python
class NotificationType(str, Enum):
    REMINDER = "reminder"
    TASK_COMPLETED = "completion"
    TASK_CREATED = "created"
    TASK_UPDATED = "updated"

class DeliveryStatus(str, Enum):
    SENT = "sent"
    READ = "read"
    FAILED = "failed"

class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    notification_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.user_id", index=True)
    task_id: Optional[uuid.UUID] = Field(foreign_key="tasks.task_id", nullable=True)
    notification_type: NotificationType
    message: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    delivery_status: DeliveryStatus = Field(default=DeliveryStatus.SENT)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "task_id": "550e8400-e29b-41d4-a716-446655440001",
                "notification_type": "reminder",
                "message": "Reminder: Buy groceries is due in 1 hour",
                "delivery_status": "sent"
            }
        }
```

### Database Schema

```sql
CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id),
    task_id UUID REFERENCES tasks(task_id) ON DELETE SET NULL,
    notification_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    sent_at TIMESTAMP NOT NULL DEFAULT NOW(),
    delivery_status VARCHAR(20) DEFAULT 'sent',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notifications_user_status ON notifications(user_id, delivery_status);
CREATE INDEX idx_notifications_sent_at ON notifications(sent_at DESC);
```

---

## 5. AuditLog (NEW)

**Purpose**: Immutable audit trail for all task operations, consumed from Kafka events.

### SQLModel Definition

```python
class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    audit_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(index=True)
    action_type: str = Field(index=True)  # "create", "update", "delete", "complete"
    resource_type: str = "task"
    resource_id: uuid.UUID
    event_data: dict = Field(sa_column=Column(JSON))
    correlation_id: uuid.UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)

    class Config:
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "action_type": "update",
                "resource_type": "task",
                "resource_id": "550e8400-e29b-41d4-a716-446655440001",
                "event_data": {
                    "changes": {
                        "status": {"from": "pending", "to": "completed"}
                    }
                },
                "correlation_id": "550e8400-e29b-41d4-a716-446655440003"
            }
        }
```

### Database Schema

```sql
CREATE TABLE audit_logs (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL DEFAULT 'task',
    resource_id UUID NOT NULL,
    event_data JSONB NOT NULL,
    correlation_id UUID NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_resource ON audit_logs(resource_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_correlation ON audit_logs(correlation_id);
```

---

## 6. Conversation (Existing, Enhanced with Dapr State)

**Purpose**: AI chatbot conversation state, now managed via Dapr state store (Redis).

**Migration**: No database schema change. Conversations are stored in Dapr state store instead of PostgreSQL for performance.

### Dapr State Store Format

```python
# Save conversation state
from dapr.clients import DaprClient

conversation_state = {
    "conversation_id": str(uuid.uuid4()),
    "user_id": user_id,
    "messages": [
        {"role": "user", "content": "Add task to buy milk"},
        {"role": "assistant", "content": "Task created: Buy milk"}
    ],
    "state": {"last_task_id": task_id},
    "last_updated": datetime.utcnow().isoformat()
}

with DaprClient() as client:
    client.save_state(
        store_name="statestore",
        key=f"conversation:{user_id}",
        value=json.dumps(conversation_state)
    )

# Retrieve conversation state
with DaprClient() as client:
    state = client.get_state(
        store_name="statestore",
        key=f"conversation:{user_id}"
    )
    conversation = json.loads(state.data)
```

---

## Data Model Summary

| Entity | Purpose | Storage | Key Features |
|--------|---------|---------|--------------|
| **Task** | Todo items | PostgreSQL | Extended with priority, tags, due dates, recurrence |
| **TaskEvent** | Event log | PostgreSQL + Kafka | Immutable audit, published to Kafka |
| **RecurringTaskSchedule** | Recurring tasks | PostgreSQL | Next execution time, APScheduler jobs |
| **Notification** | User notifications | PostgreSQL | In-app messages, delivery status |
| **AuditLog** | Audit trail | PostgreSQL | Compliance, debugging, consumed from Kafka |
| **Conversation** | Chat state | Dapr/Redis | Fast access, stateless service design |

**Total New Tables**: 4 (TaskEvent, RecurringTaskSchedule, Notification, AuditLog)
**Extended Tables**: 1 (Task)
**Dapr State Store**: 1 (Conversation)

**Next Step**: Generate API contracts in `contracts/` directory.
