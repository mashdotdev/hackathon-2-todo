"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.schemas.user import AuthResponse, UserCreate, UserLogin, UserResponse
from src.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)) -> AuthResponse:
    """Register a new user."""
    auth_service = AuthService(db)
    result = auth_service.register(user_data)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    return result


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)) -> AuthResponse:
    """Login with email and password."""
    auth_service = AuthService(db)
    result = auth_service.login(credentials)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return result


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    """Logout the current user."""
    # For JWT-based auth, logout is handled client-side by removing the token
    # Server-side token blacklisting can be added for enhanced security
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at,
    )
