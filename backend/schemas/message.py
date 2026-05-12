"""Pydantic schemas for messaging operations."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MessageCreate(BaseModel):
    """Schema for creating a message."""

    content: str
    recipient_id: int
    message_type: str = "text"
    appointment_id: Optional[int] = None


class MessageUpdate(BaseModel):
    """Schema for updating message status."""

    is_read: Optional[bool] = None


class MessageResponse(BaseModel):
    """Schema for message response."""

    id: int
    content: str
    message_type: str
    sender_id: int
    recipient_id: int
    is_read: bool
    read_at: Optional[datetime]
    appointment_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """Schema for message list response with sender/recipient info."""

    id: int
    content: str
    message_type: str
    sender: dict  # Simplified user info
    recipient: dict  # Simplified user info
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
