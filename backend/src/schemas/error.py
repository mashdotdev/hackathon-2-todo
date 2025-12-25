"""Error schemas for API responses."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str


class ValidationErrorDetail(BaseModel):
    """Schema for validation error details."""

    loc: list[str | int]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses."""

    detail: list[ValidationErrorDetail]
