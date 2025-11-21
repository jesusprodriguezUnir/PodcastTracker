"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import logging

from ..config import settings
from .models import Base

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class _EngineProxy:
    """Proxy object that allows runtime engine replacement."""
    _engine = engine
    
    @classmethod
    def get(cls):
        """Get the current engine."""
        return cls._engine
    
    @classmethod
    def set(cls, new_engine):
        """Set a new engine."""
        cls._engine = new_engine


class _SessionLocalProxy:
    """Proxy object that allows runtime SessionLocal replacement."""
    _sessionlocal = SessionLocal
    
    @classmethod
    def get(cls):
        """Get the current SessionLocal."""
        return cls._sessionlocal
    
    @classmethod
    def set(cls, new_sessionlocal):
        """Set a new SessionLocal."""
        cls._sessionlocal = new_sessionlocal


def init_db() -> None:
    """Initialize database, create all tables."""
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=_EngineProxy.get())
    logger.info("Database initialized successfully")


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Usage:
        with get_db() as db:
            db.query(Podcast).all()
    """
    SessionLocalCurrent = _SessionLocalProxy.get()
    db = SessionLocalCurrent()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes.
    
    Usage:
        @app.get("/")
        def route(db: Session = Depends(get_db_session)):
            ...
    """
    SessionLocalCurrent = _SessionLocalProxy.get()
    db = SessionLocalCurrent()
    try:
        yield db
    finally:
        db.close()
