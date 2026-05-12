"""File upload model definitions for MediBook."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


class File(Base):
    """Represents uploaded medical files (reports, prescriptions, etc.)."""

    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False, unique=True)
    file_type = Column(String(50), nullable=False)  # pdf, image, document
    file_size = Column(Integer, nullable=False)  # in bytes
    description = Column(Text, nullable=True)
    
    # Relations
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    
    # Metadata
    is_public = Column(String(20), default="private")  # private, shared-with-doctor
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    uploader = relationship("User", foreign_keys=[uploaded_by])
    appointment = relationship("Appointment", foreign_keys=[appointment_id])
