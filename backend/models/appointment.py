"""Appointment model definitions for MediBook."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


class Appointment(Base):
    """Appointment between a patient and doctor."""

    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    scheduled_at = Column(DateTime, nullable=False, index=True)
    status = Column(String(20), default="scheduled", index=True)
    reason = Column(Text, nullable=True)

    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    doctor = relationship(
        "User",
        foreign_keys=[doctor_id],
        back_populates="doctor_appointments",
    )

    patient = relationship(
        "User",
        foreign_keys=[patient_id],
        back_populates="patient_appointments",
    )

    prescriptions = relationship(
        "Prescription",
        back_populates="appointment",
        cascade="all, delete",
    )

    def is_active(self) -> bool:
        """Return True if appointment is active."""
        return self.status in {"scheduled", "confirmed"}

    @staticmethod
    def allowed_statuses() -> set[str]:
        """Return the set of allowed status values."""
        return {"scheduled", "confirmed", "canceled", "rescheduled", "completed"}

    def confirm(self) -> None:
        """Mark appointment as confirmed."""
        self.status = "confirmed"

    def cancel(self, reason: str | None = None) -> None:
        """Cancel the appointment with optional reason."""
        self.status = "canceled"
        if reason:
            self.reason = reason

    def reschedule(self, new_time: datetime) -> None:
        """Reschedule appointment to a new time."""
        self.scheduled_at = new_time
        self.status = "rescheduled"

    def complete(self) -> None:
        """Mark appointment as completed."""
        self.status = "completed"

    def can_reschedule(self) -> bool:
        """Check if appointment is eligible for reschedule."""
        return self.status in {"scheduled", "confirmed", "rescheduled"}

    def status_label(self) -> str:
        """Human readable status label."""
        return self.status.replace("_", " ").title()

    def to_summary(self) -> dict:
        """Return a summary dict for API lists."""
        return {
            "id": self.id,
            "scheduled_at": self.scheduled_at.isoformat(),
            "status": self.status,
            "doctor_id": self.doctor_id,
            "patient_id": self.patient_id,
            "reason": self.reason,
        }

    def to_detail(self) -> dict:
        """Return a richer dictionary representation."""
        return {
            **self.to_summary(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
