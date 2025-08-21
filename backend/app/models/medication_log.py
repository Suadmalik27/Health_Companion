# /backend/app/models/medication_log.py (New File)

from sqlalchemy import Column, Integer, Date, Time, ForeignKey
from ..database import Base

class MedicationLog(Base):
    __tablename__ = "medication_logs"

    id = Column(Integer, primary_key=True, index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    date_taken = Column(Date, nullable=False)
    time_taken = Column(Time, nullable=False)