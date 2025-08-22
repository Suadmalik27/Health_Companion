# backend/app/database.py (Updated for Supabase)

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Create the SQLAlchemy engine using the URL from settings
# For PostgreSQL with special characters, we need to handle encoding
try:
    engine = create_engine(
        settings.get_database_url(),
        pool_size=20,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800
    )
except Exception as e:
    print(f"Error creating database engine: {e}")
    # Fallback for development
    engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session for API endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
