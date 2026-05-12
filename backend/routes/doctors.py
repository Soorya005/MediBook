"""Doctor routes for MediBook."""

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.appointment import Appointment
from models.user import User
from schemas.user import AvailabilitySlot, DoctorPublic

router = APIRouter(prefix="/api/doctors", tags=["doctors"])


def _build_time_slots(days: int = 7) -> list[datetime]:
    """Generate a list of appointment slots for upcoming days."""
    slots: list[datetime] = []
    now = datetime.utcnow()
    start_day = datetime(now.year, now.month, now.day, 9, 0)
    for day_offset in range(days):
        day = start_day + timedelta(days=day_offset)
        for hour in (9, 11, 14, 16):
            slots.append(day.replace(hour=hour, minute=0, second=0, microsecond=0))
    return slots


def _normalize_specialization(value: str | None) -> str | None:
    """Normalize specialization filters for partial matches."""
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned if cleaned else None


@router.get("", response_model=list[DoctorPublic])
def list_doctors(
    specialization: str | None = Query(None, description="Filter by specialization"),
    db: Session = Depends(get_db),
) -> list[DoctorPublic]:
    """List doctors, optionally filtered by specialization."""
    specialization = _normalize_specialization(specialization)
    query = db.query(User).filter(User.role == "doctor", User.is_active.is_(True))
    if specialization:
        query = query.filter(User.specialization.ilike(f"%{specialization}%"))
    doctors = query.order_by(User.full_name.asc()).all()
    return [DoctorPublic.from_orm(doc) for doc in doctors]


@router.get("/specializations")
def list_specializations(db: Session = Depends(get_db)) -> list[str]:
    """Return distinct doctor specializations."""
    rows = (
        db.query(User.specialization)
        .filter(User.role == "doctor", User.specialization.isnot(None))
        .distinct()
        .all()
    )
    return sorted({row[0] for row in rows if row[0]})


@router.get("/{doctor_id}", response_model=DoctorPublic)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)) -> DoctorPublic:
    """Get a single doctor by ID."""
    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return DoctorPublic.from_orm(doctor)


@router.get("/count")
def doctor_count(db: Session = Depends(get_db)) -> dict:
    """Return total active doctor count."""
    total = db.query(User).filter(User.role == "doctor", User.is_active.is_(True)).count()
    return {"total": total}


@router.get("/{doctor_id}/availability", response_model=list[AvailabilitySlot])
def get_availability(doctor_id: int, db: Session = Depends(get_db)) -> list[AvailabilitySlot]:
    """Return availability slots for a doctor."""
    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    slots = _build_time_slots(days=7)
    booked = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status.in_(["scheduled", "confirmed", "rescheduled"]),
        )
        .all()
    )
    booked_times = {appt.scheduled_at for appt in booked}

    results: list[AvailabilitySlot] = []
    for slot in slots:
        results.append(
            AvailabilitySlot(
                datetime=slot.isoformat(),
                available=slot not in booked_times,
            )
        )
    return results
