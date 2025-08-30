# backend/app/core/config.py

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# It's a good practice to load the .env file explicitly
# This ensures it works correctly even when run from different directories
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

class Settings(BaseSettings):
    """
    Application settings are defined here.
    Pydantic automatically reads environment variables for these settings.
    """
    
    # --- DATABASE SETTINGS ---
    DATABASE_URL: str

    # --- JWT AUTHENTICATION SETTINGS ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- EMAIL SETTINGS FOR PASSWORD RESET ---
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str

    # --- FRONTEND SETTINGS ---
    FRONTEND_URL: str

    class Config:
        # This tells Pydantic to look for a .env file if the variables aren't
        # already in the environment. While we load it manually above,
        # this is a good fallback.
        env_file = ".env"

# Create a single, reusable instance of the settings
settings = Settings()