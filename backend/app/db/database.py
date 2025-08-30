# backend/app/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Import the settings object from our config file
from app.core.config import settings

# Create the SQLAlchemy engine
# The engine is the starting point for any SQLAlchemy application. It's the
# 'home base' for the actual database and its DBAPI.
# The pool_pre_ping=True argument helps in handling stale database connections.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)

# Create a SessionLocal class
# Each instance of the SessionLocal class will be a database session.
# The class itself is not a database session yet, but when we create an
# instance of it (e.g., db = SessionLocal()), that instance is the session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class
# We will inherit from this class to create each of the database models (ORM models).
# This is the magic base class that all of our models will be built upon.
Base = declarative_base()

# --- Dependency for getting a DB session ---
def get_db():
    """
    A dependency that provides a database session for each request.
    It ensures the database connection is always closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()