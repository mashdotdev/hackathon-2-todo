# MCP Tool Contracts: Phase III AI Chatbot

**Date**: 2025-12-26
**Feature**: 003-phase3-ai-chatbot

## Overview

This document defines the MCP tool contracts for the Phase III AI chatbot. These tools enable the AI agent to perform CRUD operations on tasks through natural language commands.

All tools:
- Require `user_id` parameter for user isolation
- Return structured JSON responses
- Follow the Model Context Protocol (MCP) specification

---

## Tool: add_task

**Description**: Create a new task for the user.

### Input Schema

```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "The authenticated user's ID"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "The task title (required)"
    },
    "description": {
      "type": "string",
      "maxLength": 1000,
      "description": "Optional task description"
    }
  },
  "required": ["user_id", "title"]
}
```

### Output Schema

```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "task": {
      "type": "object",
      "properties": {
        "id": { "type": "string", "format": "uuid" },
        "title": { "type": "string" },
        "description": { "type": "string", "nullable": true },
        "status": { "type": "string", "enum": ["pending", "completed"] },
        "created_at": { "type": "string", "format": "date-time" }
      }
    },
    "message": { "type": "string" }
  }
}
```

### Example

**Natural Language**: "Add a task to buy groceries"

**Tool Call**:
```json
{
  "tool": "add_task",
  "arguments": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries"
  }
}
```

**Response**:
```json
{
  "success": true,
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Buy groceries",
    "description": null,
    "status": "pending",
    "created_at": "2025-12-26T10:30:00Z"
  },
  "message": "Task 'Buy groceries' created successfully"
}
```

---

## Tool: list_tasks

**Description**: Retrieve the user's tasks with optional filtering by status.

### Input Schema

```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "The authenticated user's ID"
    },
    "status": {
      "type": "string",
      "enum": ["all", "pending", "completed"],
      "default": "all",
      "description": "Filter tasks by status"
    }
  },
  "required": ["user_id"]
}
```

### Output Schema

```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string", "format": "uuid" },
          "title": { "type": "string" },
          "description": { "type": "string", "nullable": true },
          "status": { "type": "string", "enum": ["pending", "completed"] },
          "created_at": { "type": "string", "format": "date-time" }
        }
      }
    },
    "total": { "type": "integer" },
    "message": { "type": "string" }
  }
}
```

### Example

**Natural Language**: "Show me my pending tasks"

**Tool Call**:
```json
{
  "tool": "list_tasks",
  "arguments": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "pending"
  }
}
```

**Response**:
```json
{
  "success": true,
  "tasks": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Buy groceries",
      "description": null,
      "status": "pending",
      "created_at": "2025-12-26T10:30:00Z"
    },
    {
      "id": "223e4567-e89b-12d3-a456-426614174001",
      "title": "Call mom",
      "description": "Wish her happy birthday",
      "status": "pending",
      "created_at": "2025-12-26T09:00:00Z"
    }
  ],
  "total": 2,
  "message": "Found 2 pending tasks"
}
```

---

## Tool: complete_task

**Description**: Mark a task as completed.

### Input Schema

```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "The authenticated user's ID"
    },
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "The task ID to complete"
    },
    "task_title": {
      "type": "string",
      "description": "Alternative: task title for fuzzy matching"
    }
  },
  "required": ["user_id"],
  "oneOf": [
    { "required": ["task_id"] },
    { "required": ["task_title"] }
  ]
}
```

### Output Schema

```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "task": {
      "type": "object",
      "properties": {
        "id": { "type": "string", "format": "uuid" },
        "title": { "type": "string" },
        "status": { "type": "string", "enum": ["completed"] }
      }
    },
    "message": { "type": "string" },
    "error": { "type": "string", "nullable": true }
  }
}
```

### Example

**Natural Language**: "I finished buying groceries"

**Tool Call**:
```json
{
  "tool": "complete_task",
  "arguments": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "task_title": "Buy groceries"
  }
}
```

**Response**:
```json
{
  "success": true,
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Buy groceries",
    "status": "completed"
  },
  "message": "Task 'Buy groceries' marked as completed"
}
```

### Error Response (Task Not Found)

```json
{
  "success": false,
  "task": null,
  "message": "Could not find a task matching 'vacation planning'",
  "error": "TASK_NOT_FOUND"
}
```

---

## Tool: update_task

**Description**: Update a task's title or description.

### Input Schema

```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "The authenticated user's ID"
    },
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "The task ID to update"
    },
    "task_title": {
      "type": "string",
      "description": "Alternative: current task title for fuzzy matching"
    },
    "new_title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "New title for the task"
    },
    "new_description": {
      "type": "string",
      "maxLength": 1000,
      "description": "New description for the task"
    }
  },
  "required": ["user_id"],
  "anyOf": [
    { "required": ["new_title"] },
    { "required": ["new_description"] }
  ]
}
```

### Output Schema

```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "task": {
      "type": "object",
      "properties": {
        "id": { "type": "string", "format": "uuid" },
        "title": { "type": "string" },
        "description": { "type": "string", "nullable": true },
        "status": { "type": "string" }
      }
    },
    "message": { "type": "string" }
  }
}
```

### Example

**Natural Language**: "Change 'Buy groceries' to 'Buy organic groceries'"

**Tool Call**:
```json
{
  "tool": "update_task",
  "arguments": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "task_title": "Buy groceries",
    "new_title": "Buy organic groceries"
  }
}
```

**Response**:
```json
{
  "success": true,
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Buy organic groceries",
    "description": null,
    "status": "pending"
  },
  "message": "Task updated from 'Buy groceries' to 'Buy organic groceries'"
}
```

---

## Tool: delete_task

**Description**: Delete a task from the user's list.

### Input Schema

```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "The authenticated user's ID"
    },
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "The task ID to delete"
    },
    "task_title": {
      "type": "string",
      "description": "Alternative: task title for fuzzy matching"
    },
    "confirmed": {
      "type": "boolean",
      "default": false,
      "description": "Whether deletion has been confirmed by user"
    }
  },
  "required": ["user_id"]
}
```

### Output Schema

```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "deleted_task": {
      "type": "object",
      "properties": {
        "id": { "type": "string", "format": "uuid" },
        "title": { "type": "string" }
      },
      "nullable": true
    },
    "requires_confirmation": { "type": "boolean" },
    "message": { "type": "string" }
  }
}
```

### Example (Requires Confirmation)

**Natural Language**: "Delete the groceries task"

**Tool Call** (first attempt):
```json
{
  "tool": "delete_task",
  "arguments": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "task_title": "groceries",
    "confirmed": false
  }
}
```

**Response**:
```json
{
  "success": false,
  "deleted_task": null,
  "requires_confirmation": true,
  "message": "Are you sure you want to delete 'Buy organic groceries'?"
}
```

### Example (Confirmed)

**Natural Language**: "Yes, delete it"

**Tool Call** (confirmed):
```json
{
  "tool": "delete_task",
  "arguments": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "confirmed": true
  }
}
```

**Response**:
```json
{
  "success": true,
  "deleted_task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Buy organic groceries"
  },
  "requires_confirmation": false,
  "message": "Task 'Buy organic groceries' has been deleted"
}
```

---

## Error Handling

All tools return consistent error responses:

### Error Codes

| Code | Description |
|------|-------------|
| `TASK_NOT_FOUND` | No task matches the given ID or title |
| `AMBIGUOUS_TASK` | Multiple tasks match the given title |
| `VALIDATION_ERROR` | Input validation failed |
| `UNAUTHORIZED` | User cannot access this task |
| `INTERNAL_ERROR` | Unexpected server error |

### Error Response Format

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "suggestions": ["Suggested action 1", "Suggested action 2"]
}
```

---

## Fuzzy Matching

Tools that accept `task_title` use fuzzy matching to find tasks:

1. Exact match (case-insensitive)
2. Contains match (title contains search term)
3. If multiple matches, return `AMBIGUOUS_TASK` error with list

```json
{
  "success": false,
  "error": "AMBIGUOUS_TASK",
  "message": "Found multiple tasks matching 'meeting'",
  "matching_tasks": [
    { "id": "...", "title": "Team meeting" },
    { "id": "...", "title": "Client meeting prep" }
  ],
  "suggestions": ["Please specify which task you mean"]
}
```
