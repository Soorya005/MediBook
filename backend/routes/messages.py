"""Messaging routes for MediBook."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models.message import Message
from models.user import User
from schemas.message import MessageCreate, MessageResponse, MessageUpdate
from utils.auth import get_current_user

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.post("", response_model=MessageResponse)
def send_message(
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Send a message to another user."""
    # Validate recipient exists
    recipient = db.query(User).filter(User.id == payload.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    if payload.recipient_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send message to yourself")

    # Create message
    message = Message(
        content=payload.content,
        message_type=payload.message_type,
        sender_id=current_user.id,
        recipient_id=payload.recipient_id,
        appointment_id=payload.appointment_id,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return MessageResponse.from_orm(message)


@router.get("", response_model=list[MessageResponse])
def list_messages(
    conversation_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MessageResponse]:
    """Get user's messages (sent or received).
    
    If conversation_id is provided, get messages with that user.
    Otherwise, get recent messages.
    """
    query = db.query(Message).filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    )

    if conversation_id:
        query = query.filter(
            ((Message.sender_id == current_user.id) & (Message.recipient_id == conversation_id))
            | ((Message.sender_id == conversation_id) & (Message.recipient_id == current_user.id))
        )

    messages = query.order_by(Message.created_at.desc()).offset(skip).limit(limit).all()
    return [MessageResponse.from_orm(m) for m in reversed(messages)]


@router.get("/conversation/{conversation_id}", response_model=list[MessageResponse])
def get_conversation(
    conversation_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MessageResponse]:
    """Get conversation history with a specific user."""
    messages = (
        db.query(Message)
        .filter(
            ((Message.sender_id == current_user.id) & (Message.recipient_id == conversation_id))
            | ((Message.sender_id == conversation_id) & (Message.recipient_id == current_user.id))
        )
        .order_by(Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [MessageResponse.from_orm(m) for m in reversed(messages)]


@router.get("/{message_id}", response_model=MessageResponse)
def get_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Get a specific message."""
    message = db.query(Message).filter(Message.id == message_id).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    if message.sender_id != current_user.id and message.recipient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this message")

    return MessageResponse.from_orm(message)


@router.patch("/{message_id}", response_model=MessageResponse)
def update_message(
    message_id: int,
    payload: MessageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Update message status (mark as read)."""
    message = db.query(Message).filter(Message.id == message_id).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    if message.recipient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only recipient can update message status")

    if payload.is_read and not message.is_read:
        message.is_read = True
        message.read_at = datetime.utcnow()

    db.commit()
    db.refresh(message)

    return MessageResponse.from_orm(message)


@router.get("/unread/count")
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Get count of unread messages."""
    count = db.query(Message).filter(
        (Message.recipient_id == current_user.id) & (Message.is_read == False)
    ).count()
    
    return {"unread_count": count}


@router.post("/mark-as-read", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def mark_all_as_read(
    conversation_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Mark messages as read."""
    query = db.query(Message).filter(
        (Message.recipient_id == current_user.id) & (Message.is_read == False)
    )

    if conversation_id:
        query = query.filter(Message.sender_id == conversation_id)

    messages = query.all()
    for msg in messages:
        msg.is_read = True
        msg.read_at = datetime.utcnow()

    db.commit()


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a message."""
    message = db.query(Message).filter(Message.id == message_id).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    if message.sender_id != current_user.id and message.recipient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this message")

    db.delete(message)
    db.commit()
