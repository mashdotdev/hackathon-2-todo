"""Notification Service - FastAPI application.

Consumes task events from Kafka via Dapr and creates in-app notifications.
T062-T064: Implements Kafka consumer with idempotency and notification creation.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session

from .config import DAPR_HTTP_PORT, PUBSUB_NAME, TOPIC_NAME
from .database import engine
from .consumers.task_event_consumer import TaskEventConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    logger.info("Notification Service starting...")
    yield
    logger.info("Notification Service shutting down...")


app = FastAPI(
    title="Notification Service",
    description="Phase V - Task event consumer and notification creator",
    version="2.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for liveness probe."""
    return {"status": "healthy", "service": "notification-service"}


@app.get("/ready")
async def readiness_check() -> dict[str, str]:
    """Readiness check endpoint."""
    return {"status": "ready", "service": "notification-service"}


@app.get("/dapr/subscribe")
async def subscribe() -> list[dict]:
    """Dapr subscription configuration.
    
    Tells Dapr which topics this service subscribes to.
    """
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TOPIC_NAME,
            "route": "/events/task",
        }
    ]


@app.post("/events/task")
async def handle_task_event(request: Request) -> JSONResponse:
    """Handle incoming task events from Kafka via Dapr.

    T063: Creates notifications for task-created and task-completed events.
    T064: Includes idempotency check to prevent duplicate notifications.
    """
    try:
        event_data = await request.json()
        logger.info(f"Received task event: {event_data.get('type', 'unknown')}")

        # Process event with database session
        with Session(engine) as db:
            consumer = TaskEventConsumer(db)
            result = consumer.process_event(event_data)

        return JSONResponse(status_code=200, content=result)

    except Exception as e:
        logger.error(f"Error processing task event: {e}")
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


def _get_notification_message(event_type: str, task_title: str) -> str:
    """Generate notification message based on event type."""
    messages = {
        "task-created": f"New task created: {task_title}",
        "task-updated": f"Task updated: {task_title}",
        "task-completed": f"Task completed: {task_title}",
        "task-deleted": f"Task deleted: {task_title}",
    }
    return messages.get(event_type, f"Task event: {task_title}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
