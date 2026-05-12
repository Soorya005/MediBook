"""Prescription routes for MediBook."""

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.appointment import Appointment
from models.prescription import Prescription
from models.user import User
from schemas.appointment import PrescriptionCreate, PrescriptionPublic, PrescriptionListResponse
from utils.auth import get_current_user, require_role, ensure_active_user

router = APIRouter(prefix="/api/prescriptions", tags=["prescriptions"])


@router.post("", response_model=PrescriptionPublic, status_code=status.HTTP_201_CREATED)
def create_prescription(
    payload: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PrescriptionPublic:
    """Create a prescription for an appointment (doctor only)."""
    ensure_active_user(current_user)
    require_role(current_user, "doctor")

    appt = db.query(Appointment).filter(Appointment.id == payload.appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appt.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your appointment")

    prescription = Prescription(
        appointment_id=appt.id,
        doctor_id=current_user.id,
        patient_id=appt.patient_id,
        medication=payload.medication,
        dosage=payload.dosage,
        instructions=payload.instructions,
    )
    db.add(prescription)
    db.commit()
    db.refresh(prescription)

    return PrescriptionPublic.from_orm(prescription)


@router.get("/{appointment_id}", response_model=PrescriptionListResponse)
def get_prescriptions(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PrescriptionListResponse:
    """Fetch prescriptions for an appointment."""
    ensure_active_user(current_user)

    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if current_user.role == "doctor" and appt.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your appointment")
    if current_user.role == "patient" and appt.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your appointment")

    items = db.query(Prescription).filter(Prescription.appointment_id == appointment_id).all()
    return PrescriptionListResponse(items=[PrescriptionPublic.from_orm(p) for p in items])


@router.get("", response_model=PrescriptionListResponse)
def list_my_prescriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PrescriptionListResponse:
    """List prescriptions for the current user."""
    ensure_active_user(current_user)
    if current_user.role == "doctor":
        query = db.query(Prescription).filter(Prescription.doctor_id == current_user.id)
    else:
        query = db.query(Prescription).filter(Prescription.patient_id == current_user.id)
    items = query.order_by(Prescription.created_at.desc()).all()
    return PrescriptionListResponse(items=[PrescriptionPublic.from_orm(p) for p in items])


@router.get("/recent/{days}", response_model=PrescriptionListResponse)
def list_recent_prescriptions(
    days: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PrescriptionListResponse:
    """List prescriptions from the past N days for the current user."""
    ensure_active_user(current_user)
    since = datetime.utcnow() - timedelta(days=max(days, 1))
    if current_user.role == "doctor":
        query = db.query(Prescription).filter(
            Prescription.doctor_id == current_user.id,
            Prescription.created_at >= since,
        )
    else:
        query = db.query(Prescription).filter(
            Prescription.patient_id == current_user.id,
            Prescription.created_at >= since,
        )
    items = query.order_by(Prescription.created_at.desc()).all()
    return PrescriptionListResponse(items=[PrescriptionPublic.from_orm(p) for p in items])
