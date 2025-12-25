"""Main entry point for Todo API application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="Todo API",
    description="Phase II: Full-Stack Todo Application API",
    version="0.2.0",
    lifespan=lifespan,
)

# Configure CORS - allow localhost origins for development
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    settings.FRONTEND_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


# Import and include routers after app creation to avoid circular imports
def setup_routes() -> None:
    """Setup API routes."""
    from src.api.routes import auth, tasks

    app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
    app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])


setup_routes()
