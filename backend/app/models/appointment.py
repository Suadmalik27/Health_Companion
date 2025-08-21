# /backend/app/models/appointment.py (Updated)
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_name = Column(String, index=True)
    purpose = Column(String, nullable=True)
    appointment_datetime = Column(DateTime)
    location = Column(String, nullable=True)
    photo_url = Column(String, nullable=True) # <-- YEH LINE ADD KAREIN
    
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="appointments")