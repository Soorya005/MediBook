"""Database configuration and helpers for MediBook."""
"This is for checking CI/CD working "

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DB_PATH = os.getenv("MEDIBOOK_DB_PATH", "./medibook.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# SQLite needs check_same_thread=False for multi-threaded FastAPI usage.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for request-scoped dependencies."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Context-managed session for one-off scripts or seeding."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Create database tables if they do not exist."""
    from backend.models.user import User  # noqa: F401
    from backend.models.appointment import Appointment  # noqa: F401
    from backend.models.prescription import Prescription  # noqa: F401

    Base.metadata.create_all(bind=engine)


def db_healthcheck() -> dict:
    """Basic healthcheck to verify engine can connect."""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


def get_database_url() -> str:
    """Return the resolved database URL for logging and diagnostics."""
    return DATABASE_URL


def reset_db() -> None:
    """Drop and recreate tables. Use only in development."""
    from backend.models.user import User  # noqa: F401
    from backend.models.appointment import Appointment  # noqa: F401
    from backend.models.prescription import Prescription  # noqa: F401

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def ensure_db_dir() -> None:
    """Ensure the database directory exists for the configured path."""
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)


def dispose_engine() -> None:
    """Dispose the SQLAlchemy engine to close pooled connections."""
    engine.dispose()


def get_sessionmaker() -> sessionmaker:
    """Return the sessionmaker for advanced dependency usage."""
    return SessionLocal


def get_base() -> type:
    """Return the declarative Base class."""
    return Base
