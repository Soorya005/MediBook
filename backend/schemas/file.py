"""Pydantic schemas for file operations."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FileCreate(BaseModel):
    """Schema for creating a file."""

    filename: str
    file_type: str
    description: Optional[str] = None
    appointment_id: Optional[int] = None
    is_public: str = "private"


class FileUpdate(BaseModel):
    """Schema for updating file metadata."""

    description: Optional[str] = None
    is_public: Optional[str] = None


class FileResponse(BaseModel):
    """Schema for file response."""

    id: int
    filename: str
    file_path: str
    file_type: str
    file_size: int
    description: Optional[str]
    is_public: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
