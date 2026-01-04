"""Notification management routes.

Phase V: T047-T048 - Notification listing and marking as read.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.schemas.notification import NotificationResponse, NotificationListResponse
from src.services.notification_service import NotificationService

router = APIRouter()


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    unread_only: bool = Query(False, description="Filter to unread notifications only"),
    limit: int = Query(50, ge=1, le=100, description="Maximum notifications to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationListResponse:
    """List notifications for the current user.

    T047: List notifications with unread_only filter and unread_count.
    """
    notification_service = NotificationService(db)
    notifications, unread_count = notification_service.get_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
    )

    return NotificationListResponse(
        notifications=[
            NotificationResponse.model_validate(n) for n in notifications
        ],
        unread_count=unread_count,
    )


@router.patch("/{notification_id}/mark_read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationResponse:
    """Mark a notification as read.

    T048: Update delivery_status to 'read'.
    """
    notification_service = NotificationService(db)
    notification = notification_service.mark_as_read(
        notification_id=notification_id,
        user_id=current_user.id,
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return NotificationResponse.model_validate(notification)
