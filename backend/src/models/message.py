"""Message model for chat persistence."""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.conversation import Conversation


class MessageRole(str, Enum):
    """Role of message sender."""

    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """Message model for chat messages.

    Represents a single message in a conversation, from either the user or assistant.

    Attributes:
        id: Unique identifier (UUID)
        conversation_id: Parent conversation reference
        role: Message sender role (user or assistant)
        content: Message content
        created_at: When message was sent
    """

    __tablename__ = "messages"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    conversation_id: str = Field(foreign_key="conversations.id", index=True)
    role: MessageRole = Field(sa_column_kwargs={"nullable": False})
    content: str = Field(max_length=10000, sa_column_kwargs={"nullable": False})
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
