from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

from intelligent_backend.core.config import settings

# Create the SQLAlchemy engine.
# The pool_pre_ping setting helps prevent issues with stale database connections.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Create a configured "Session" class.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """
    FastAPI dependency that provides a database session.
    It ensures that the database session is always closed after the request,
    even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
