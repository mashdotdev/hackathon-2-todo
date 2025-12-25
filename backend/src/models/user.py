"""User model for database storage."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User model for authentication.

    Attributes:
        id: Unique identifier (UUID)
        email: User email (unique, indexed)
        hashed_password: Bcrypt hashed password
        is_active: Account status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "users"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
