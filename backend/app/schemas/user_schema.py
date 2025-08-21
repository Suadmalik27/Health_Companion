# backend/app/schemas/user_schema.py (Fully Updated)

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

# --- Base and Create Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

# --- Update Schemas ---
class UserUpdate(BaseModel):
    """Schema for updating user profile information."""
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    time_format: Optional[str] = None
    theme: Optional[str] = None 

class PasswordUpdate(BaseModel):
    """Schema for updating the user's password."""
    current_password: str
    new_password: str

# --- Display Schema ---
class UserShow(UserBase):
    """Schema for displaying public user information."""
    id: int
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    profile_picture_url: Optional[str] = None
    time_format: Optional[str] = "12h"
    theme: Optional[str] = "light"

    class Config:
        from_attributes = True

# --- NAYA CODE: Password Reset Schemas ---
# In classes ko add karna zaroori hai

class PasswordResetRequest(BaseModel):
    """Schema for requesting a password reset. Expects an email."""
    email: EmailStr

class PasswordReset(BaseModel):
    """Schema for resetting the password. Expects the token and new password."""
    token: str
    new_password: str
# --- NAYA CODE KHATAM ---