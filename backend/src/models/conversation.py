"""Conversation model for chat persistence."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.message import Message
    from src.models.user import User


class Conversation(SQLModel, table=True):
    """Conversation model for chat sessions.

    Each user has exactly one conversation (single thread per user).

    Attributes:
        id: Unique identifier (UUID)
        user_id: Owner reference (unique - one conversation per user)
        created_at: When conversation started
        updated_at: Last activity timestamp
    """

    __tablename__ = "conversations"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    user_id: str = Field(foreign_key="users.id", unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="conversation")
    messages: list["Message"] = Relationship(back_populates="conversation")
