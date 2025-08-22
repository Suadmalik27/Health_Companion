# backend/app/config.py (Updated for Production)

from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from urllib.parse import quote_plus

class Settings(BaseSettings):
    """
    Manages application settings by loading them from environment variables.
    """
    # Load from .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- Database Settings ---
    DATABASE_URL: str

    # --- JWT Authentication Settings ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- Email Settings for Password Reset ---
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"

    # --- Frontend URL for building reset links ---
    FRONTEND_URL: str = "http://localhost:8501"

    def get_database_url(self):
        """Handle special characters in database URL"""
        if '%' in self.DATABASE_URL:
            return self.DATABASE_URL
        return self.DATABASE_URL


# Create settings instance
settings = Settings()
