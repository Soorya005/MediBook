"""User model definitions for MediBook."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    """Represents both patients and doctors.

    Roles:
    - patient: can book and manage their own appointments
    - doctor: can manage availability and create prescriptions
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, index=True)

    specialization = Column(String(120), nullable=True)
    bio = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient_appointments = relationship(
        "Appointment",
        foreign_keys="Appointment.patient_id",
        back_populates="patient",
        cascade="all, delete",
    )

    doctor_appointments = relationship(
        "Appointment",
        foreign_keys="Appointment.doctor_id",
        back_populates="doctor",
        cascade="all, delete",
    )

    doctor_prescriptions = relationship(
        "Prescription",
        foreign_keys="Prescription.doctor_id",
        back_populates="doctor",
        cascade="all, delete",
    )

    patient_prescriptions = relationship(
        "Prescription",
        foreign_keys="Prescription.patient_id",
        back_populates="patient",
        cascade="all, delete",
    )

    def is_doctor(self) -> bool:
        """Return True if user has doctor role."""
        return self.role == "doctor"

    def is_patient(self) -> bool:
        """Return True if user has patient role."""
        return self.role == "patient"

    def display_name(self) -> str:
        """Provide a safe display name."""
        return self.full_name.strip()

    def short_profile(self) -> dict:
        """Return a short dictionary representation for list views."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "specialization": self.specialization,
            "role": self.role,
        }

    def to_public_dict(self) -> dict:
        """Return a public representation for API responses."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "specialization": self.specialization,
            "bio": self.bio,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_doctor_dict(self) -> dict:
        """Return doctor-specific public fields."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "specialization": self.specialization,
            "bio": self.bio,
            "is_active": self.is_active,
        }

    def to_patient_dict(self) -> dict:
        """Return patient-specific public fields."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
        }

    def ensure_doctor_profile(self) -> None:
        """Ensure doctor profile fields are populated."""
        if self.role != "doctor":
            return
        if not self.specialization:
            self.specialization = "General"

    def update_profile(self, full_name: str | None = None, bio: str | None = None) -> None:
        """Update mutable profile fields."""
        if full_name:
            self.full_name = full_name.strip()
        if bio is not None:
            self.bio = bio.strip() or None

    def __repr__(self) -> str:
        """Debug representation for logs."""
        return f"User(id={self.id}, email={self.email}, role={self.role})"
