"""File handling routes for MediBook."""

from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models.file import File as FileModel
from models.user import User
from models.appointment import Appointment
from schemas.file import FileCreate, FileResponse, FileUpdate
from utils.auth import get_current_user

router = APIRouter(prefix="/api/files", tags=["files"])

# Directory for file storage
UPLOAD_DIR = Path("uploads/files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "doc", "docx", "txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def _get_file_extension(filename: str) -> str:
    """Extract file extension."""
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""


def _is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return _get_file_extension(filename) in ALLOWED_EXTENSIONS


@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    appointment_id: Optional[int] = Query(None),
    is_public: str = Query("private"),
    description: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    """Upload a medical file."""
    if not _is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read file and check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB",
        )

    # Validate appointment if provided
    if appointment_id:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        if appointment.doctor_id != current_user.id and appointment.patient_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized for this appointment")

    # Save file
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_")
    safe_filename = timestamp + file.filename
    file_path = UPLOAD_DIR / safe_filename

    with open(file_path, "wb") as f:
        f.write(content)

    # Create database record
    db_file = FileModel(
        filename=file.filename,
        file_path=str(file_path),
        file_type=_get_file_extension(file.filename),
        file_size=len(content),
        description=description,
        uploaded_by=current_user.id,
        appointment_id=appointment_id,
        is_public=is_public,
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return FileResponse.from_orm(db_file)


@router.get("", response_model=list[FileResponse])
def list_files(
    appointment_id: Optional[int] = Query(None),
    file_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[FileResponse]:
    """List user's files with optional filters."""
    query = db.query(FileModel).filter(
        (FileModel.uploaded_by == current_user.id) | (FileModel.is_public == "shared-with-doctor")
    )

    if appointment_id:
        query = query.filter(FileModel.appointment_id == appointment_id)

    if file_type:
        query = query.filter(FileModel.file_type == file_type)

    files = query.order_by(FileModel.created_at.desc()).all()
    return [FileResponse.from_orm(f) for f in files]


@router.get("/{file_id}", response_model=FileResponse)
def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    """Get file details."""
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()

    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Check access rights
    if db_file.uploaded_by != current_user.id and db_file.is_public != "shared-with-doctor":
        if db_file.appointment_id:
            appointment = db.query(Appointment).filter(Appointment.id == db_file.appointment_id).first()
            if not appointment or (appointment.doctor_id != current_user.id and appointment.patient_id != current_user.id):
                raise HTTPException(status_code=403, detail="Not authorized to access this file")
        else:
            raise HTTPException(status_code=403, detail="Not authorized to access this file")

    return FileResponse.from_orm(db_file)


@router.patch("/{file_id}", response_model=FileResponse)
def update_file(
    file_id: int,
    payload: FileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    """Update file metadata."""
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()

    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    if db_file.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only uploader can update file")

    if payload.description is not None:
        db_file.description = payload.description
    if payload.is_public is not None:
        db_file.is_public = payload.is_public

    db_file.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_file)

    return FileResponse.from_orm(db_file)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a file."""
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()

    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    if db_file.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only uploader can delete file")

    # Delete physical file
    try:
        if os.path.exists(db_file.file_path):
            os.remove(db_file.file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

    # Delete database record
    db.delete(db_file)
    db.commit()
