"""Chat schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Single chat message in a request.

    Attributes:
        id: Message ID (optional, generated if not provided)
        role: Who sent the message (user or assistant)
        content: Message content (max 1000 chars)
    """

    id: Optional[str] = None
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(max_length=1000)


class ChatRequest(BaseModel):
    """Chat request body.

    Attributes:
        messages: Conversation messages (last message should be from user)
    """

    messages: list[ChatMessage] = Field(min_length=1)


class StoredMessage(BaseModel):
    """Message stored in the database.

    Attributes:
        id: Message UUID
        role: Who sent the message
        content: Message content
        created_at: When message was sent
    """

    id: str
    role: str
    content: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    """Response containing conversation history.

    Attributes:
        conversation_id: Conversation identifier
        messages: List of stored messages
    """

    conversation_id: str
    messages: list[StoredMessage]
