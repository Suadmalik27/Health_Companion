# /backend/app/schemas/appointment_schema.py (Updated)
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AppointmentBase(BaseModel):
    doctor_name: str
    appointment_datetime: datetime
    purpose: Optional[str] = None
    location: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    doctor_name: Optional[str] = None
    appointment_datetime: Optional[datetime] = None
    purpose: Optional[str] = None
    location: Optional[str] = None

class AppointmentShow(AppointmentBase):
    id: int
    photo_url: Optional[str] = None # <-- YEH LINE ADD KAREIN

    class Config:
        from_attributes = True