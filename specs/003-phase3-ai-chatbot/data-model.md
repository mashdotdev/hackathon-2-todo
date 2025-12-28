# Data Model: Phase III AI-Powered Chatbot

**Date**: 2025-12-26
**Feature**: 003-phase3-ai-chatbot

## Overview

Phase III extends the Phase II data model with two new entities for conversation persistence: `Conversation` and `Message`. The existing `User` and `Task` entities remain unchanged but gain new relationships.

---

## Entity Relationship Diagram

```
┌─────────────┐       1:1        ┌──────────────────┐
│    User     │─────────────────▶│   Conversation   │
│             │                  │                  │
│ id (PK)     │                  │ id (PK)          │
│ email       │                  │ user_id (FK, UQ) │
│ password    │◀─────────────────│ created_at       │
│ is_active   │       1:N        │ updated_at       │
│ created_at  │                  └──────────────────┘
│ updated_at  │                           │
└─────────────┘                           │ 1:N
       │                                  ▼
       │ 1:N                     ┌──────────────────┐
       ▼                         │     Message      │
┌─────────────┐                  │                  │
│    Task     │                  │ id (PK)          │
│             │                  │ conversation_id  │
│ id (PK)     │                  │ role             │
│ title       │                  │ content          │
│ description │                  │ created_at       │
│ status      │                  └──────────────────┘
│ user_id (FK)│
│ created_at  │
│ updated_at  │
└─────────────┘
```

---

## Existing Entities (Unchanged)

### User

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| email | String | Unique, Indexed | User's email address |
| hashed_password | String | Not Null | Bcrypt hashed password |
| is_active | Boolean | Default: true | Account active status |
| created_at | Timestamp | Default: now() | Creation timestamp |
| updated_at | Timestamp | Default: now() | Last update timestamp |

### Task

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| title | String(200) | Not Null, 1-200 chars | Task title |
| description | String(1000) | Nullable | Optional task description |
| status | Enum | Default: "pending" | "pending" or "completed" |
| user_id | UUID | FK → users.id, Indexed | Owner reference |
| created_at | Timestamp | Default: now() | Creation timestamp |
| updated_at | Timestamp | Default: now() | Last update timestamp |

---

## New Entities

### Conversation

Represents a single chat session for a user. Each user has exactly one conversation (single thread per user, per spec).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK → users.id, Unique | Owner (one conversation per user) |
| created_at | Timestamp | Default: now() | When conversation started |
| updated_at | Timestamp | Default: now() | Last activity timestamp |

**Relationships:**
- Belongs to exactly one `User`
- Has many `Message` records

**Validation Rules:**
- `user_id` must reference an existing, active user
- Only one conversation per user (enforced by unique constraint)

### Message

Represents a single message in a conversation, from either the user or the assistant.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| conversation_id | UUID | FK → conversations.id, Indexed | Parent conversation |
| role | Enum | Not Null | "user" or "assistant" |
| content | Text | Not Null, max 10000 chars | Message content |
| created_at | Timestamp | Default: now() | When message was sent |

**Relationships:**
- Belongs to exactly one `Conversation`

**Validation Rules:**
- `role` must be either "user" or "assistant"
- `content` cannot be empty
- `content` maximum length: 10,000 characters (to accommodate assistant responses with task lists)
- `conversation_id` must reference an existing conversation

---

## State Transitions

### Conversation Lifecycle

```
┌─────────────┐     User sends      ┌─────────────┐
│   (None)    │────first message───▶│   Active    │
└─────────────┘                     └─────────────┘
                                          │
                                    User interacts
                                          │
                                          ▼
                                    ┌─────────────┐
                                    │   Active    │
                                    │ (messages   │
                                    │  appended)  │
                                    └─────────────┘
```

- Conversation is created lazily on first message
- No explicit "closed" state (always available)
- `updated_at` reflects last message timestamp

### Message States

Messages are immutable once created. No state transitions.

---

## Indexes

### Existing Indexes (from Phase II)
- `users.email` - Unique index for login lookup
- `tasks.user_id` - Index for user's task queries

### New Indexes (Phase III)
- `conversations.user_id` - Unique index (enforces one conversation per user)
- `messages.conversation_id` - Index for loading conversation history
- `messages.created_at` - Index for chronological ordering

---

## SQLModel Definitions

### Conversation Model

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="conversation")
    messages: list["Message"] = Relationship(back_populates="conversation")
```

### Message Model

```python
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: MessageRole = Field(nullable=False)
    content: str = Field(nullable=False, max_length=10000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
```

### User Model Extension

```python
# Add to existing User model
class User(SQLModel, table=True):
    # ... existing fields ...

    # New relationship
    conversation: Optional["Conversation"] = Relationship(back_populates="user")
```

---

## Migration Notes

### Alembic Migration Script (Pseudocode)

```python
def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Text(), primary_key=True),
        sa.Column('user_id', sa.Text(), sa.ForeignKey('users.id'), unique=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow),
    )
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Text(), primary_key=True),
        sa.Column('conversation_id', sa.Text(), sa.ForeignKey('conversations.id')),
        sa.Column('role', sa.Text(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
    )
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
```

---

## Query Patterns

### Get or Create Conversation
```python
async def get_or_create_conversation(db: Session, user_id: UUID) -> Conversation:
    conversation = db.exec(
        select(Conversation).where(Conversation.user_id == user_id)
    ).first()

    if not conversation:
        conversation = Conversation(user_id=user_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    return conversation
```

### Load Conversation History
```python
async def get_messages(db: Session, conversation_id: UUID, limit: int = 20) -> list[Message]:
    return db.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()[::-1]  # Reverse to chronological order
```

### Add Message
```python
async def add_message(db: Session, conversation_id: UUID, role: MessageRole, content: str) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    db.add(message)

    # Update conversation timestamp
    conversation = db.get(Conversation, conversation_id)
    conversation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(message)
    return message
```

---

## Data Retention

Per spec assumptions:
- No explicit retention policy
- Messages persist indefinitely
- No auto-cleanup of old messages (out of scope)

For future consideration:
- Archive messages older than 90 days
- Limit messages per conversation (e.g., 1000)
