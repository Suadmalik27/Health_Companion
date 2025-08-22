# backend/app/config.py (Fully Updated Code)

from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    """
    Manages application settings by loading them from a .env file.
    """
    # This line tells Pydantic to load settings from a file named '.env'
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra='ignore')

    # --- Database Settings ---
    DATABASE_URL: str = "sqlite:///./test.db"  # Default for development

    # --- JWT Authentication Settings ---
    SECRET_KEY: str = "default-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- Email Settings for Password Reset ---
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@healthcompanion.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"

    # --- Frontend URL for building reset links ---
    FRONTEND_URL: str = "http://localhost:8501"


# We create a single, global instance of the Settings class.
# We will import this 'settings' object into other files.
settings = Settings()
