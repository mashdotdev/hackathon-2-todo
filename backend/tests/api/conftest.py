"""Pytest fixtures for API tests."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.api.deps import get_db
from src.core.security import create_access_token, get_password_hash
from src.main import app
from src.models.task import Task
from src.models.user import User


@pytest.fixture(name="engine")
def engine_fixture():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine):
    """Create a new database session for each test."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with database session override."""

    def get_session_override():
        yield session

    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(test_user: User) -> dict[str, str]:
    """Create authorization headers for the test user."""
    token = create_access_token(data={"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="test_task")
def test_task_fixture(session: Session, test_user: User) -> Task:
    """Create a test task."""
    task = Task(
        title="Test Task",
        description="Test description",
        user_id=test_user.id,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@pytest.fixture(name="multiple_tasks")
def multiple_tasks_fixture(session: Session, test_user: User) -> list[Task]:
    """Create multiple test tasks."""
    tasks = [
        Task(title="Task 1", user_id=test_user.id),
        Task(title="Task 2", user_id=test_user.id, status="completed"),
        Task(title="Task 3", description="With description", user_id=test_user.id),
    ]
    for task in tasks:
        session.add(task)
    session.commit()
    for task in tasks:
        session.refresh(task)
    return tasks
