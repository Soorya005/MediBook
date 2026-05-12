"""Triggers and notifications routes for MediBook."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models.trigger import Notification, Trigger
from models.user import User
from schemas.trigger import (
    NotificationCreate,
    NotificationResponse,
    TriggerCreate,
    TriggerResponse,
    TriggerUpdate,
)
from utils.auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])
trigger_router = APIRouter(prefix="/api/triggers", tags=["triggers"])


# ============ Notification Endpoints ============


@router.post("", response_model=NotificationResponse)
def create_notification(
    payload: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationResponse:
    """Create a notification."""
    notification = Notification(
        title=payload.title,
        message=payload.message,
        notification_type=payload.notification_type,
        user_id=payload.user_id,
        appointment_id=payload.appointment_id,
        message_id=payload.message_id,
        trigger_event=payload.trigger_event,
        recall_at=payload.recall_at,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return NotificationResponse.from_orm(notification)


@router.get("", response_model=list[NotificationResponse])
def list_notifications(
    only_unread: bool = Query(False),
    notification_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[NotificationResponse]:
    """Get user's notifications."""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if only_unread:
        query = query.filter(Notification.is_read == False)

    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)

    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    return [NotificationResponse.from_orm(n) for n in notifications]


@router.get("/unread/count")
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Get count of unread notifications."""
    count = db.query(Notification).filter(
        (Notification.user_id == current_user.id) & (Notification.is_read == False)
    ).count()

    return {"unread_count": count}


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationResponse:
    """Get a specific notification."""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this notification")

    return NotificationResponse.from_orm(notification)


@router.patch("/{notification_id}", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationResponse:
    """Mark notification as read."""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    notification.is_read = True
    db.commit()
    db.refresh(notification)

    return NotificationResponse.from_orm(notification)


@router.post("/mark-all-read", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Mark all notifications as read."""
    db.query(Notification).filter(
        (Notification.user_id == current_user.id) & (Notification.is_read == False)
    ).update({"is_read": True})

    db.commit()


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a notification."""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(notification)
    db.commit()


# ============ Trigger Endpoints ============


@trigger_router.post("", response_model=TriggerResponse)
def create_trigger(
    payload: TriggerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TriggerResponse:
    """Create an automation trigger (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create triggers")

    trigger = Trigger(
        name=payload.name,
        description=payload.description,
        event_type=payload.event_type,
        action_type=payload.action_type,
        action_config=payload.action_config,
        is_active=payload.is_active,
        created_by=current_user.id,
    )

    db.add(trigger)
    db.commit()
    db.refresh(trigger)

    return TriggerResponse.from_orm(trigger)


@trigger_router.get("", response_model=list[TriggerResponse])
def list_triggers(
    event_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TriggerResponse]:
    """List triggers (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can list triggers")

    query = db.query(Trigger)

    if event_type:
        query = query.filter(Trigger.event_type == event_type)

    if is_active is not None:
        query = query.filter(Trigger.is_active == is_active)

    triggers = query.order_by(Trigger.created_at.desc()).all()
    return [TriggerResponse.from_orm(t) for t in triggers]


@trigger_router.get("/{trigger_id}", response_model=TriggerResponse)
def get_trigger(
    trigger_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TriggerResponse:
    """Get a specific trigger."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view triggers")

    trigger = db.query(Trigger).filter(Trigger.id == trigger_id).first()

    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    return TriggerResponse.from_orm(trigger)


@trigger_router.patch("/{trigger_id}", response_model=TriggerResponse)
def update_trigger(
    trigger_id: int,
    payload: TriggerUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TriggerResponse:
    """Update a trigger."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update triggers")

    trigger = db.query(Trigger).filter(Trigger.id == trigger_id).first()

    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    if payload.name is not None:
        trigger.name = payload.name
    if payload.description is not None:
        trigger.description = payload.description
    if payload.action_config is not None:
        trigger.action_config = payload.action_config
    if payload.is_active is not None:
        trigger.is_active = payload.is_active

    trigger.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(trigger)

    return TriggerResponse.from_orm(trigger)


@trigger_router.delete("/{trigger_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_trigger(
    trigger_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a trigger."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete triggers")

    trigger = db.query(Trigger).filter(Trigger.id == trigger_id).first()

    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    db.delete(trigger)
    db.commit()
