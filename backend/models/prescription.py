"""Prescription model for MediBook."""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


class Prescription(Base):
    """Medical prescription tied to an appointment."""

    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    medication = Column(String(120), nullable=False)
    dosage = Column(String(120), nullable=False)
    instructions = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    appointment = relationship("Appointment", back_populates="prescriptions")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_prescriptions")
    patient = relationship("User", foreign_keys=[patient_id], back_populates="patient_prescriptions")

    def to_dict(self) -> dict:
        """Serialize prescription to a dictionary."""
        return {
            "id": self.id,
            "appointment_id": self.appointment_id,
            "doctor_id": self.doctor_id,
            "patient_id": self.patient_id,
            "medication": self.medication,
            "dosage": self.dosage,
            "instructions": self.instructions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def summary(self) -> dict:
        """Short summary for list views."""
        return {
            "id": self.id,
            "medication": self.medication,
            "dosage": self.dosage,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def update_instructions(self, text: str) -> None:
        """Update instructions with sanitized text."""
        self.instructions = text.strip()

    def is_recent(self, days: int = 30) -> bool:
        """Return True if prescription is within a recent window."""
        if not self.created_at:
            return False
        return self.created_at >= datetime.utcnow() - timedelta(days=days)

    def belongs_to_patient(self, patient_id: int) -> bool:
        """Check if prescription belongs to a patient."""
        return self.patient_id == patient_id

    def belongs_to_doctor(self, doctor_id: int) -> bool:
        """Check if prescription belongs to a doctor."""
        return self.doctor_id == doctor_id

    def as_text(self) -> str:
        """Return a printable summary string."""
        return f"{self.medication} - {self.dosage}: {self.instructions}"

    def matches_query(self, query: str) -> bool:
        """Simple text match for medication or instructions."""
        text = f"{self.medication} {self.instructions}".lower()
        return query.lower() in text

    def is_complete(self) -> bool:
        """Return True if required fields are populated."""
        return all([
            bool(self.medication),
            bool(self.dosage),
            bool(self.instructions),
        ])

    def set_medication(self, name: str) -> None:
        """Set medication with trimmed value."""
        self.medication = name.strip()

    def set_dosage(self, dosage: str) -> None:
        """Set dosage with trimmed value."""
        self.dosage = dosage.strip()

    def __repr__(self) -> str:
        """Debug representation for logs."""
        return f"Prescription(id={self.id}, medication={self.medication})"
