"""Recurring Tasks Service - FastAPI application.

Runs scheduled jobs to generate new task instances from recurring schedules.
T069-T071: Implements recurring task generation with Dapr event publishing.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI
from sqlmodel import Session

from .config import DAPR_HTTP_PORT
from .database import engine
from .scheduler.task_scheduler import TaskScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def process_due_schedules() -> None:
    """Process all due recurring task schedules.

    T069-T071: Called every minute to check and execute due schedules.
    """
    logger.info(f"Checking for due schedules at {datetime.utcnow().isoformat()}")

    try:
        with Session(engine) as db:
            task_scheduler = TaskScheduler(db)
            result = await task_scheduler.process_due_schedules()
            logger.info(f"Schedule check completed: {result}")
    except Exception as e:
        logger.error(f"Error processing schedules: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    logger.info("Recurring Tasks Service starting...")
    
    # Add scheduled job
    scheduler.add_job(
        process_due_schedules,
        trigger=IntervalTrigger(minutes=1),
        id="process_due_schedules",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started - checking schedules every minute")
    
    yield
    
    scheduler.shutdown()
    logger.info("Recurring Tasks Service shutting down...")


app = FastAPI(
    title="Recurring Tasks Service",
    description="Phase V - Generates task instances from recurring schedules",
    version="2.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for liveness probe."""
    return {"status": "healthy", "service": "recurring-tasks-service"}


@app.get("/ready")
async def readiness_check() -> dict[str, str]:
    """Readiness check endpoint."""
    scheduler_running = scheduler.running
    status = "ready" if scheduler_running else "not_ready"
    return {
        "status": status,
        "service": "recurring-tasks-service",
        "scheduler": "running" if scheduler_running else "stopped",
    }


@app.get("/schedules/due")
async def get_due_schedules() -> dict:
    """Get schedules due for execution.

    Internal endpoint for debugging/monitoring.
    """
    now = datetime.utcnow()
    try:
        with Session(engine) as db:
            task_scheduler = TaskScheduler(db)
            count = task_scheduler.get_due_schedules_count()
            return {
                "current_time": now.isoformat(),
                "due_count": count,
            }
    except Exception as e:
        return {
            "current_time": now.isoformat(),
            "error": str(e),
        }


@app.post("/schedules/trigger")
async def trigger_schedule_check() -> dict:
    """Manually trigger schedule processing.
    
    Internal endpoint for testing.
    """
    await process_due_schedules()
    return {"triggered": True, "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
