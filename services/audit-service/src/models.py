"""AuditLog model for the Audit Service.

Replicates the backend AuditLog model for database operations.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Field, SQLModel, Column, JSON


class AuditLog(SQLModel, table=True):
    """Immutable audit trail for all task operations.

    Created by the Audit microservice when consuming Kafka events.
    """

    __tablename__ = "audit_logs"

    audit_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    user_id: str = Field(index=True)
    action_type: str = Field(max_length=50, index=True)
    resource_type: str = Field(default="task", max_length=50)
    resource_id: str = Field(index=True)
    event_data: dict[str, Any] = Field(sa_column=Column(JSON))
    correlation_id: str = Field(index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
