# /backend/app/models/medication.py (Updated)
from sqlalchemy import Column, Integer, String, Time, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Medication(Base):
    __tablename__ = "medications"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    dosage = Column(String)
    timing = Column(Time)
    is_active = Column(Boolean, default=True)
    photo_url = Column(String, nullable=True) # <-- YEH LINE ADD KAREIN
    
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="medications")