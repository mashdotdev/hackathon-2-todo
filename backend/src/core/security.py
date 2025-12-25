"""Security utilities for JWT and password hashing."""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from src.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    # Truncate password to 72 bytes (bcrypt limit)
    password_bytes = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    """Hash a password."""
    # Truncate password to 72 bytes (bcrypt limit)
    password_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict[str, str | datetime], expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> dict[str, str] | None:
    """Verify a JWT token and return the payload."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
