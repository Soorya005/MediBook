"""Appointment booking routes for MediBook."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.appointment import Appointment
from models.user import User
from schemas.appointment import AppointmentCancel, AppointmentCreate, AppointmentPublic, AppointmentReschedule, AppointmentListResponse
from utils.auth import get_current_user, require_role, ensure_active_user
from utils.email import appointment_confirmation, appointment_canceled, appointment_rescheduled

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


def _ensure_future_time(scheduled_at: datetime) -> None:
    if scheduled_at <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Appointment time must be in the future")


def _doctor_is_available(db: Session, doctor_id: int, scheduled_at: datetime) -> bool:
    existing = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.scheduled_at == scheduled_at,
            Appointment.status.in_(["scheduled", "confirmed", "rescheduled"]),
        )
        .first()
    )
    return existing is None


@router.get("", response_model=AppointmentListResponse)
def list_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AppointmentListResponse:
    """List appointments for the current user."""
    ensure_active_user(current_user)
    if current_user.role == "doctor":
        appts = (
            db.query(Appointment)
            .filter(Appointment.doctor_id == current_user.id)
            .order_by(Appointment.scheduled_at.asc())
            .all()
        )
    else:
        appts = (
            db.query(Appointment)
            .filter(Appointment.patient_id == current_user.id)
            .order_by(Appointment.scheduled_at.asc())
            .all()
        )
    return AppointmentListResponse(items=[AppointmentPublic.from_orm(a) for a in appts])


@router.post("", response_model=AppointmentPublic, status_code=status.HTTP_201_CREATED)
def book_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AppointmentPublic:
    """Book a new appointment for a patient."""
    ensure_active_user(current_user)
    require_role(current_user, "patient")
    _ensure_future_time(payload.scheduled_at)

    doctor = db.query(User).filter(User.id == payload.doctor_id, User.role == "doctor").first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if not _doctor_is_available(db, doctor.id, payload.scheduled_at):
        raise HTTPException(status_code=409, detail="Doctor not available at that time")

    appt = Appointment(
        doctor_id=doctor.id,
        patient_id=current_user.id,
        scheduled_at=payload.scheduled_at,
        status="scheduled",
        reason=payload.reason,
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)

    appointment_confirmation(
        to_email=current_user.email,
        patient_name=current_user.full_name,
        doctor_name=doctor.full_name,
        when=appt.scheduled_at.isoformat(),
    )

    return AppointmentPublic.from_orm(appt)


@router.post("/{appointment_id}/cancel", response_model=AppointmentPublic)
def cancel_appointment(
    appointment_id: int,
    payload: AppointmentCancel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AppointmentPublic:
    """Cancel an existing appointment."""
    ensure_active_user(current_user)
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if current_user.role == "patient" and appt.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to cancel this appointment")
    if current_user.role == "doctor" and appt.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to cancel this appointment")

    appt.cancel(payload.reason)
    db.commit()
    db.refresh(appt)

    doctor = db.query(User).filter(User.id == appt.doctor_id).first()
    appointment_canceled(
        to_email=current_user.email,
        patient_name=current_user.full_name,
        doctor_name=doctor.full_name if doctor else "Doctor",
        when=appt.scheduled_at.isoformat(),
    )

    return AppointmentPublic.from_orm(appt)


@router.post("/{appointment_id}/reschedule", response_model=AppointmentPublic)
def reschedule_appointment(
    appointment_id: int,
    payload: AppointmentReschedule,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AppointmentPublic:
    """Reschedule an appointment."""
    ensure_active_user(current_user)
    _ensure_future_time(payload.scheduled_at)

    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if current_user.role == "patient" and appt.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to reschedule this appointment")

    if not _doctor_is_available(db, appt.doctor_id, payload.scheduled_at):
        raise HTTPException(status_code=409, detail="Doctor not available at that time")

    appt.reschedule(payload.scheduled_at)
    db.commit()
    db.refresh(appt)

    doctor = db.query(User).filter(User.id == appt.doctor_id).first()
    appointment_rescheduled(
        to_email=current_user.email,
        patient_name=current_user.full_name,
        doctor_name=doctor.full_name if doctor else "Doctor",
        when=appt.scheduled_at.isoformat(),
    )

    return AppointmentPublic.from_orm(appt)
