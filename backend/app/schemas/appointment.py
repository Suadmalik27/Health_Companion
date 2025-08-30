# backend/app/schemas/appointment.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# --- Base Schema ---
class AppointmentBase(BaseModel):
    doctor_name: str = Field(..., max_length=100)
    appointment_datetime: datetime
    location: Optional[str] = Field(None, max_length=200)
    purpose: Optional[str] = Field(None, max_length=300)


# --- Schema for Creating an Appointment ---
class AppointmentCreate(AppointmentBase):
    pass


# --- Schema for Updating an Appointment ---
class AppointmentUpdate(BaseModel):
    doctor_name: Optional[str] = Field(None, max_length=100)
    appointment_datetime: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=200)
    purpose: Optional[str] = Field(None, max_length=300)


# --- Schema for Reading/Returning an Appointment ---
class Appointment(AppointmentBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True