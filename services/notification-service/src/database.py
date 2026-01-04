"""Database configuration for Notification Service."""

from sqlmodel import Session, SQLModel, create_engine

from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)


def get_db() -> Session:
    """Get database session."""
    with Session(engine) as session:
        return session


def init_db() -> None:
    """Initialize database (create tables if needed)."""
    SQLModel.metadata.create_all(engine)
