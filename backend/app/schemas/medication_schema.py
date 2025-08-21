# /backend/app/schemas/medication_schema.py (Updated)
from pydantic import BaseModel
from datetime import time
from typing import Optional

class MedicationBase(BaseModel):
    name: str
    dosage: str
    timing: time
    is_active: Optional[bool] = True

class MedicationCreate(MedicationBase):
    pass

class MedicationUpdate(BaseModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    timing: Optional[time] = None
    is_active: Optional[bool] = None

class MedicationShow(MedicationBase):
    id: int
    photo_url: Optional[str] = None # <-- YEH LINE ADD KAREIN

    class Config:
        from_attributes = True