"""User schemas for API validation."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response (excludes password)."""

    id: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Schema for authentication response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
