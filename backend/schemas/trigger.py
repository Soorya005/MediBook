"""Pydantic schemas for triggers and notifications."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationCreate(BaseModel):
    """Schema for creating a notification."""

    title: str
    message: str
    notification_type: str
    user_id: int
    appointment_id: Optional[int] = None
    message_id: Optional[int] = None
    trigger_event: Optional[str] = None
    recall_at: Optional[datetime] = None


class NotificationResponse(BaseModel):
    """Schema for notification response."""

    id: int
    title: str
    message: str
    notification_type: str
    user_id: int
    is_read: bool
    is_sent: bool
    created_at: datetime
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True


class TriggerCreate(BaseModel):
    """Schema for creating a trigger."""

    name: str
    description: Optional[str] = None
    event_type: str
    action_type: str
    action_config: str  # JSON string with action configuration
    is_active: bool = True


class TriggerUpdate(BaseModel):
    """Schema for updating a trigger."""

    name: Optional[str] = None
    description: Optional[str] = None
    action_config: Optional[str] = None
    is_active: Optional[bool] = None


class TriggerResponse(BaseModel):
    """Schema for trigger response."""

    id: int
    name: str
    description: Optional[str]
    event_type: str
    action_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
