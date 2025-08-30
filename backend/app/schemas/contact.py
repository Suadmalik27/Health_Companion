# backend/app/schemas/contact.py

from pydantic import BaseModel, Field
from typing import Optional

# --- Base Schema ---
class ContactBase(BaseModel):
    contact_name: str = Field(..., max_length=100)
    phone_number: str = Field(..., max_length=20)
    relationship_type: Optional[str] = Field(None, max_length=50) # e.g., "Son", "Doctor"


# --- Schema for Creating a Contact ---
class ContactCreate(ContactBase):
    pass


# --- Schema for Reading/Returning a Contact ---
class Contact(ContactBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True