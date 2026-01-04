"""Audit Service - FastAPI application.

Consumes all task events from Kafka via Dapr and creates audit log entries.
T075: Implements Kafka consumer with database persistence.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session

from .config import DAPR_HTTP_PORT, PUBSUB_NAME
from .database import engine
from .consumers.audit_event_consumer import AuditEventConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    logger.info("Audit Service starting...")
    yield
    logger.info("Audit Service shutting down...")


app = FastAPI(
    title="Audit Service",
    description="Phase V - Consumes events and creates audit logs",
    version="2.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for liveness probe."""
    return {"status": "healthy", "service": "audit-service"}


@app.get("/ready")
async def readiness_check() -> dict[str, str]:
    """Readiness check endpoint."""
    return {"status": "ready", "service": "audit-service"}


@app.get("/dapr/subscribe")
async def subscribe() -> list[dict]:
    """Dapr subscription configuration.
    
    Subscribes to all relevant topics for comprehensive audit logging.
    """
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "task-events",
            "route": "/events/task",
        },
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "reminders",
            "route": "/events/reminder",
        },
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "task-updates",
            "route": "/events/update",
        },
    ]


@app.post("/events/task")
async def handle_task_event(request: Request) -> JSONResponse:
    """Handle incoming task events and create audit logs."""
    return await _process_event(request, "task")


@app.post("/events/reminder")
async def handle_reminder_event(request: Request) -> JSONResponse:
    """Handle incoming reminder events and create audit logs."""
    return await _process_event(request, "reminder")


@app.post("/events/update")
async def handle_update_event(request: Request) -> JSONResponse:
    """Handle incoming update events and create audit logs."""
    return await _process_event(request, "update")


async def _process_event(request: Request, event_category: str) -> JSONResponse:
    """Process an event and create an audit log entry.

    T075: Saves audit log to database via AuditEventConsumer.
    """
    try:
        event_data = await request.json()

        # Process event with database session
        with Session(engine) as db:
            consumer = AuditEventConsumer(db)
            result = consumer.process_event(event_data, event_category)

        return JSONResponse(status_code=200, content=result)

    except Exception as e:
        logger.error(f"Error creating audit log: {e}")
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


def _get_action_type(event_type: str) -> str:
    """Map event type to action type for audit logging."""
    mapping = {
        "task-created": "create",
        "task-updated": "update",
        "task-completed": "complete",
        "task-deleted": "delete",
        "reminder-scheduled": "schedule",
        "reminder-triggered": "trigger",
    }
    return mapping.get(event_type, "unknown")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
