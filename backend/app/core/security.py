# backend/app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

# Import the settings object from our config file
from app.core.config import settings

# --- Password Hashing Setup ---
# We use passlib's CryptContext to handle password hashing.
# "bcrypt" is the recommended hashing algorithm.
# The "auto" scheme will automatically use bcrypt for new hashes and also
# be able to verify passwords hashed with other algorithms if we add more later.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Security Functions ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that a plain-text password matches a hashed password.

    Args:
        plain_password: The password provided by the user during login.
        hashed_password: The password hash stored in the database.

    Returns:
        True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashes a plain-text password.

    Args:
        password: The plain-text password provided by the user during registration.

    Returns:
        A securely hashed version of the password.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a new JWT access token.

    Args:
        data: A dictionary containing the data to encode in the token (e.g., user's email).
        expires_delta: An optional timedelta object for when the token should expire.
                       If not provided, the default from settings is used.

    Returns:
        The encoded JWT access token as a string.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt