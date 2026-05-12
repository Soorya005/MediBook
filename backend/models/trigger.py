"""Trigger and notification model definitions for MediBook."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship

from database import Base


class Notification(Base):
    """Automated notifications and triggers."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # appointment_reminder, prescription_ready, message_received, etc.
    
    # Target user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    
    # Related entities
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    
    # Metadata
    trigger_event = Column(String(100), nullable=True)  # appointment_scheduled, prescription_created, etc.
    recall_at = Column(DateTime, nullable=True)  # When to remind (e.g., 24 hours before appointment)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    appointment = relationship("Appointment", foreign_keys=[appointment_id])
    message = relationship("Message", foreign_keys=[message_id])


class Trigger(Base):
    """Workflow triggers for automation."""

    __tablename__ = "triggers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Trigger configuration
    event_type = Column(String(100), nullable=False)  # appointment_created, prescription_created, file_uploaded, etc.
    action_type = Column(String(100), nullable=False)  # send_notification, send_email, create_task, etc.
    action_config = Column(Text, nullable=False)  # JSON config for the action
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
