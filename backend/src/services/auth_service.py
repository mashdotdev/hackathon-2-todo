"""Authentication service for user registration and login."""

from datetime import datetime

from sqlmodel import Session, select

from src.core.security import create_access_token, get_password_hash, verify_password
from src.models.user import User
from src.schemas.user import AuthResponse, UserCreate, UserLogin, UserResponse


class AuthService:
    """Service for user authentication operations."""

    def __init__(self, db: Session) -> None:
        """Initialize auth service with database session."""
        self.db = db

    def register(self, user_data: UserCreate) -> AuthResponse | None:
        """Register a new user.

        Args:
            user_data: User registration data

        Returns:
            AuthResponse with token and user info, or None if email exists
        """
        # Check if email already exists
        statement = select(User).where(User.email == user_data.email)
        existing_user = self.db.exec(statement).first()
        if existing_user:
            return None

        # Create new user
        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Generate access token
        access_token = create_access_token(data={"sub": user.id})

        return AuthResponse(
            access_token=access_token,
            user=UserResponse(
                id=user.id,
                email=user.email,
                created_at=user.created_at,
            ),
        )

    def login(self, credentials: UserLogin) -> AuthResponse | None:
        """Authenticate a user.

        Args:
            credentials: Login credentials

        Returns:
            AuthResponse with token and user info, or None if invalid
        """
        statement = select(User).where(User.email == credentials.email)
        user = self.db.exec(statement).first()

        if not user:
            return None

        if not verify_password(credentials.password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        # Update last login time
        user.updated_at = datetime.utcnow()
        self.db.add(user)
        self.db.commit()

        # Generate access token
        access_token = create_access_token(data={"sub": user.id})

        return AuthResponse(
            access_token=access_token,
            user=UserResponse(
                id=user.id,
                email=user.email,
                created_at=user.created_at,
            ),
        )

    def get_user_by_id(self, user_id: str) -> User | None:
        """Get user by ID.

        Args:
            user_id: User identifier

        Returns:
            User if found, None otherwise
        """
        statement = select(User).where(User.id == user_id)
        return self.db.exec(statement).first()
