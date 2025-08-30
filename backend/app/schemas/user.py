# backend/app/schemas/user.py (VERSION 2.0 - WITH NOTIFICATION PREFERENCE)

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date

# --- Base Schemas ---
# These contain the common fields shared across other schemas.

class UserBase(BaseModel):
    """Base schema for user, contains shared attributes."""
    email: EmailStr
    full_name: Optional[str] = None
    dob: Optional[date] = None
    address: Optional[str] = None
    
    # --- YEH NAYA FIELD HAI ---
    # User ki notification preference ko handle karne ke liye
    notifications_enabled: Optional[bool] = True


# --- Schemas for Specific Operations ---

# Schema for creating a new user (e.g., in a POST request)
# This schema expects a password.
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


# Schema for updating a user's profile
# All fields are optional, so the user can update only what they need.
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    dob: Optional[date] = None
    address: Optional[str] = None
    
    # --- YEH NAYA FIELD HAI ---
    # User ko profile update karte waqt isko badalne ka option dena
    notifications_enabled: Optional[bool] = None


# Schema for reading/returning user data (e.g., in a GET response)
# This schema should NEVER include the password.
class User(UserBase):
    id: int
    is_active: bool
    # 'notifications_enabled' yahan UserBase se inherit ho jaayega

    class Config:
        # This tells Pydantic to read the data even if it is not a dict,
        # but an ORM model (or any other arbitrary object with attributes).
        from_attributes = True
