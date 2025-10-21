"""
Database configuration and session management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./echoforge.db"  # Default to SQLite for easy setup
)

# For PostgreSQL migration:
# DATABASE_URL = postgresql://user:password@localhost/echoforge

# Create engine
# For SQLite, we need check_same_thread=False to allow FastAPI async
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Used with FastAPI's Depends() for automatic session management.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables.
    Call this on application startup.
    """
    from .models import Base
    Base.metadata.create_all(bind=engine)


def reset_db():
    """
    Drop and recreate all tables.
    WARNING: This deletes all data! Only use for development/testing.
    """
    from .models import Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
