# API Contracts: Phase V

**Feature**: Phase V - Cloud Deployment with Event-Driven Architecture
**Date**: 2025-12-30

## Overview

This document defines all API contracts for Phase V, including REST endpoints, Kafka event schemas, and Dapr service invocation contracts.

---

## 1. Task API (Extended)

**Base Path**: `/api/{user_id}/tasks`

### Endpoints

#### GET /api/{user_id}/tasks
**Description**: List and filter tasks

**Query Parameters**:
- `status` (optional): Filter by status (pending|in_progress|completed)
- `priority` (optional): Filter by priority (High|Medium|Low)
- `tags` (optional): Filter by tags (comma-separated)
- `due_date_from` (optional): Filter tasks due after this date (ISO 8601)
- `due_date_to` (optional): Filter tasks due before this date (ISO 8601)
- `sort` (optional): Sort field (priority|due_date|created_at), default: created_at
- `order` (optional): Sort order (asc|desc), default: desc

**Response**: `200 OK`
```json
{
  "tasks": [
    {
      "task_id": "uuid",
      "user_id": "uuid",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "pending",
      "priority": "High",
      "tags": ["personal", "errands"],
      "due_date": "2025-12-31T18:00:00Z",
      "recurrence_pattern": "weekly",
      "reminder_lead_time": 60,
      "created_at": "2025-12-30T10:00:00Z",
      "updated_at": "2025-12-30T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

#### GET /api/{user_id}/tasks/search
**Description**: Full-text search tasks

**Query Parameters**:
- `q` (required): Search query (searches title and description)

**Response**: Same as GET /tasks

---

#### POST /api/{user_id}/tasks
**Description**: Create new task

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "High",
  "tags": ["personal", "errands"],
  "due_date": "2025-12-31T18:00:00Z",
  "recurrence_pattern": "weekly",
  "reminder_lead_time": 60
}
```

**Response**: `201 Created`
```json
{
  "task_id": "uuid",
  "user_id": "uuid",
  "title": "Buy groceries",
  ...
}
```

**Events Published**:
- `task-created` to `task-events` Kafka topic

---

#### PATCH /api/{user_id}/tasks/{task_id}
**Description**: Partial update task

**Request Body** (all fields optional):
```json
{
  "title": "Buy groceries and fruit",
  "priority": "Medium",
  "tags": ["personal"],
  "status": "completed"
}
```

**Response**: `200 OK` (full task object)

**Events Published**:
- `task-updated` to `task-events` if metadata changed
- `task-completed` to `task-events` if status changed to completed

---

#### DELETE /api/{user_id}/tasks/{task_id}
**Description**: Delete task

**Response**: `204 No Content`

**Events Published**:
- `task-deleted` to `task-events` Kafka topic

---

## 2. Notification API

**Base Path**: `/api/{user_id}/notifications`

### Endpoints

#### GET /api/{user_id}/notifications
**Description**: List notifications

**Query Parameters**:
- `unread_only` (optional): Filter unread notifications (true|false), default: false
- `limit` (optional): Max results, default: 50

**Response**: `200 OK`
```json
{
  "notifications": [
    {
      "notification_id": "uuid",
      "user_id": "uuid",
      "task_id": "uuid",
      "notification_type": "reminder",
      "message": "Reminder: Buy groceries is due in 1 hour",
      "sent_at": "2025-12-31T17:00:00Z",
      "delivery_status": "sent",
      "created_at": "2025-12-31T17:00:00Z"
    }
  ],
  "unread_count": 5
}
```

---

#### PATCH /api/{user_id}/notifications/{notification_id}/mark_read
**Description**: Mark notification as read

**Response**: `200 OK`
```json
{
  "notification_id": "uuid",
  "delivery_status": "read"
}
```

---

## 3. Audit Log API

**Base Path**: `/api/{user_id}/audit_logs`

### Endpoints

#### GET /api/{user_id}/audit_logs
**Description**: List audit logs

**Query Parameters**:
- `resource_id` (optional): Filter by task ID
- `action_type` (optional): Filter by action (create|update|delete|complete)
- `limit` (optional): Max results, default: 100

**Response**: `200 OK`
```json
{
  "audit_logs": [
    {
      "audit_id": "uuid",
      "user_id": "uuid",
      "action_type": "update",
      "resource_type": "task",
      "resource_id": "uuid",
      "event_data": {
        "changes": {
          "status": {"from": "pending", "to": "completed"}
        }
      },
      "correlation_id": "uuid",
      "timestamp": "2025-12-30T12:00:00Z"
    }
  ],
  "total": 1
}
```

---

## 4. Kafka Event Schemas

### Topic: `task-events`

**Event Types**:
- `task-created`
- `task-updated`
- `task-completed`
- `task-deleted`

**Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["event_id", "event_type", "task_id", "user_id", "timestamp", "payload"],
  "properties": {
    "event_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique event identifier for idempotency"
    },
    "event_type": {
      "type": "string",
      "enum": ["task-created", "task-updated", "task-completed", "task-deleted"]
    },
    "task_id": {
      "type": "string",
      "format": "uuid"
    },
    "user_id": {
      "type": "string",
      "format": "uuid"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "payload": {
      "type": "object",
      "description": "Full task object snapshot at event time"
    }
  }
}
```

**Example**:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "task-created",
  "task_id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440002",
  "timestamp": "2025-12-30T12:00:00Z",
  "payload": {
    "title": "Buy groceries",
    "priority": "High",
    "tags": ["personal"],
    "status": "pending"
  }
}
```

---

### Topic: `reminders`

**Event Types**:
- `reminder-scheduled`
- `reminder-triggered`

**Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["event_id", "event_type", "task_id", "user_id", "reminder_time"],
  "properties": {
    "event_id": {"type": "string", "format": "uuid"},
    "event_type": {"type": "string", "enum": ["reminder-scheduled", "reminder-triggered"]},
    "task_id": {"type": "string", "format": "uuid"},
    "user_id": {"type": "string", "format": "uuid"},
    "reminder_time": {"type": "string", "format": "date-time"},
    "task_title": {"type": "string"},
    "due_date": {"type": "string", "format": "date-time"}
  }
}
```

---

## 5. Internal Microservice APIs

### Notification Service

**POST /internal/notifications**
**Description**: Create notification (called by Kafka consumer)

**Request Body**:
```json
{
  "user_id": "uuid",
  "task_id": "uuid",
  "notification_type": "reminder",
  "message": "Reminder: Buy groceries is due in 1 hour"
}
```

**Response**: `201 Created`

---

### Recurring Tasks Service

**POST /internal/schedules**
**Description**: Create recurring schedule

**Request Body**:
```json
{
  "parent_task_id": "uuid",
  "user_id": "uuid",
  "recurrence_pattern": "weekly",
  "next_execution_time": "2026-01-06T00:00:00Z"
}
```

**Response**: `201 Created`

---

**GET /internal/schedules/due**
**Description**: Get schedules due for execution

**Response**: `200 OK`
```json
{
  "schedules": [
    {
      "schedule_id": "uuid",
      "parent_task_id": "uuid",
      "user_id": "uuid",
      "recurrence_pattern": "weekly",
      "next_execution_time": "2025-12-30T12:00:00Z"
    }
  ]
}
```

---

### Audit Service

**POST /internal/audit_logs**
**Description**: Create audit log entry (called by Kafka consumer)

**Request Body**:
```json
{
  "user_id": "uuid",
  "action_type": "update",
  "resource_id": "uuid",
  "event_data": {
    "changes": {"status": {"from": "pending", "to": "completed"}}
  },
  "correlation_id": "uuid"
}
```

**Response**: `201 Created`

---

## 6. Dapr Service Invocation Contracts

### Backend → Recurring Tasks Service

**Method**: POST
**App ID**: `recurring-tasks-service`
**Endpoint**: `/schedules`
**Purpose**: Create recurring schedule when task with recurrence created

---

### Backend → Notification Service (Optional)

**Method**: POST
**App ID**: `notification-service`
**Endpoint**: `/notifications`
**Purpose**: Direct notification creation (bypassing Kafka for urgent notifications)

---

## Contract Testing

All endpoints should have contract tests validating:
- Request/response schemas
- Status codes
- Error responses (400, 401, 404, 500)
- Idempotency (for POST/PATCH)

**Test Framework**: Pact or OpenAPI validation with pytest

---

## Summary

| API | Endpoints | Purpose |
|-----|-----------|---------|
| **Task API** | 5 endpoints | CRUD + search/filter tasks |
| **Notification API** | 2 endpoints | List and mark read notifications |
| **Audit Log API** | 1 endpoint | Query audit trail |
| **Internal (Notification)** | 1 endpoint | Kafka consumer creates notifications |
| **Internal (Recurring)** | 2 endpoints | Schedule management |
| **Internal (Audit)** | 1 endpoint | Kafka consumer creates audit logs |
| **Kafka Events** | 2 topics | task-events, reminders |

**Next Step**: Generate quickstart.md with deployment guide.
