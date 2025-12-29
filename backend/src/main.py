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
    description="Phase III: AI-Powered Todo Application with MCP",
    version="0.3.0",
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
    """Health check endpoint for liveness probe."""
    return {"status": "healthy"}


@app.get("/ready")
async def readiness_check() -> dict[str, str | dict[str, str]]:
    """Readiness check endpoint for Kubernetes readiness probe.

    Verifies database connectivity before accepting traffic.
    """
    from sqlmodel import text

    from src.core.database import engine

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready", "checks": {"database": "connected"}}
    except Exception as e:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "checks": {"database": str(e)}},
        )


# Import and include routers after app creation to avoid circular imports
def setup_routes() -> None:
    """Setup API routes."""
    from src.api.routes import auth, chat, tasks

    app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
    app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
    app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])


def setup_mcp() -> None:
    """Setup MCP server endpoint."""
    from src.mcp.server import mcp

    # Mount MCP server at /mcp endpoint with SSE transport
    app.mount("/mcp", mcp.sse_app())


def setup_chatkit() -> None:
    """Setup ChatKit endpoint."""
    from fastapi import Depends, Request
    from fastapi.responses import Response, StreamingResponse

    from src.api.deps import get_current_user
    from src.chatkit.server import chatkit_server
    from src.chatkit.store import RequestContext
    from src.models.user import User

    @app.post("/chatkit")
    async def chatkit_endpoint(
        request: Request,
        current_user: User = Depends(get_current_user),
    ) -> Response:
        """ChatKit endpoint for AI-powered chat."""
        from chatkit.server import StreamingResult

        context = RequestContext(user_id=current_user.id)
        result = await chatkit_server.process(await request.body(), context=context)

        if isinstance(result, StreamingResult):
            return StreamingResponse(result, media_type="text/event-stream")
        return Response(content=result.json, media_type="application/json")


setup_routes()
setup_mcp()
setup_chatkit()
