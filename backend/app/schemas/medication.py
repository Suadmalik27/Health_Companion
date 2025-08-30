# backend/app/schemas/medication.py (VERSION 3.0 - ADVANCED REMINDERS)

from pydantic import BaseModel, Field
from typing import Optional, Any, List
from datetime import time, datetime

# --- Base Schema for Medication ---
# Ismein woh common fields hain jo har medication schema mein honge.
class MedicationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    dosage: str = Field(..., min_length=1, max_length=100)
    
    timing_type: str # "Meal-Related" or "Specific-Time"
    meal_timing: Optional[str] = None
    specific_time: Optional[time] = None
    
    # --- YEH BADLAAV HAIN ---
    # Purane 'frequency' ko 'frequency_type' se replace kiya gaya hai
    frequency_type: str # Options: Daily, Weekly, Monthly, Specific Days, As Needed
    
    # Is naye field mein frequency ki details save hongi (e.g., ["Monday"], 15)
    # 'Any' ka matlab hai ki yeh list (dinon ke liye) ya integer (tareekh ke liye) ho sakti hai.
    frequency_details: Optional[Any] = None


# --- Schema for Creating a Medication ---
# Jab frontend se nayi dawai add karne ki request aayegi, toh woh is format mein hogi.
class MedicationCreate(MedicationBase):
    pass


# --- Schema for Updating a Medication ---
# Update karte waqt saare fields optional hote hain.
class MedicationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    dosage: Optional[str] = Field(None, min_length=1, max_length=100)
    
    timing_type: Optional[str] = None
    meal_timing: Optional[str] = None
    specific_time: Optional[time] = None
    
    # --- YEH BADLAAV HAIN ---
    frequency_type: Optional[str] = None
    frequency_details: Optional[Any] = None
    
    last_taken_at: Optional[datetime] = None


# --- Schema for Reading/Returning a Medication ---
# Jab API database se ek dawai return karega, toh woh is format mein hogi.
class Medication(MedicationBase):
    id: int
    owner_id: int
    last_taken_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Schema for Reading/Returning a Medication Log Entry ---
# Yeh "diary ke note" ka template hai.
class MedicationLog(BaseModel):
    id: int
    medication_id: int
    owner_id: int
    taken_at: datetime

    class Config:
        from_attributes = True

