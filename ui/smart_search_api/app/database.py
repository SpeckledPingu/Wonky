from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the SQLite database URL.
# For a file-based database, the format is "sqlite:///./filename.db"
SQLALCHEMY_DATABASE_URL = "sqlite:///./mock_data.sqlite"

# Create the SQLAlchemy engine.
# The 'check_same_thread' argument is needed only for SQLite.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a SessionLocal class, which will be the factory for new Session objects.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for our models to inherit from.
Base = declarative_base()

# Dependency to get a DB session.
# This will be used in API endpoints to get a database session and ensure it's closed after the request.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
