# backend/app/config.py (Fully Updated Code)

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Manages application settings by loading them from a .env file.
    """
    # This line tells Pydantic to load settings from a file named '.env'
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- Database Settings ---
    DATABASE_URL: str

    # --- JWT Authentication Settings ---
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # --- NAYA CODE: Email Settings for Password Reset ---
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str

    # --- NAYA CODE: Frontend URL for building reset links ---
    FRONTEND_URL: str
    # --- NAYA CODE KHATAM ---


# We create a single, global instance of the Settings class.
# We will import this 'settings' object into other files.
settings = Settings()