# backend/app/db/models.py (VERSION 3.0 - ADVANCED REMINDERS)

from sqlalchemy import (
    Boolean, Column, Integer, String, DateTime, Date, ForeignKey, Text, Time, JSON
)
from sqlalchemy.orm import relationship
import datetime

from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    dob = Column(Date)
    address = Column(String)
    reset_password_token = Column(String, unique=True, nullable=True)
    reset_token_expires_at = Column(DateTime, nullable=True)
    
    # --- YEH NAYA COLUMN HAI ---
    # User ko email reminders chahiye ya nahi, isko control karne ke liye
    notifications_enabled = Column(Boolean, default=True)
    
    medications = relationship("Medication", back_populates="owner")
    appointments = relationship("Appointment", back_populates="owner")
    contacts = relationship("EmergencyContact", back_populates="owner")
    medication_logs = relationship("MedicationLog", back_populates="owner")


class Medication(Base):
    __tablename__ = "medications"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    
    timing_type = Column(String, default="Meal-Related")
    meal_timing = Column(String, nullable=True)
    specific_time = Column(Time, nullable=True)
    
    # --- YEH BADLAAV HAIN ---
    # Purane 'frequency' column ko 'frequency_type' se replace kiya ja raha hai
    frequency_type = Column(String, default="Daily") # Options: Daily, Weekly, Monthly, Specific Days, As Needed
    
    # Is naye column mein frequency ki details save hongi (e.g., ["Monday"], 15)
    frequency_details = Column(JSON, nullable=True) 

    last_taken_at = Column(DateTime, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="medications")
    logs = relationship("MedicationLog", back_populates="medication")


class MedicationLog(Base):
    __tablename__ = "medication_logs"
    id = Column(Integer, primary_key=True, index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    taken_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    medication = relationship("Medication", back_populates="logs")
    owner = relationship("User", back_populates="medication_logs")

# --- Baaki ke models (Appointment, EmergencyContact, HealthTip) pehle jaise hi रहेंगे ---

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    doctor_name = Column(String, nullable=False)
    appointment_datetime = Column(DateTime, nullable=False)
    location = Column(String)
    purpose = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="appointments")

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"
    id = Column(Integer, primary_key=True, index=True)
    contact_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    relationship_type = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="contacts")

class HealthTip(Base):
    __tablename__ = "health_tips"
    id = Column(Integer, primary_key=True, index=True)
    tip_text = Column(Text, nullable=False)
    category = Column(String, default="General")

