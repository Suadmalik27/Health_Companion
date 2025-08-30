# backend/app/crud/crud_medication.py (VERSION 3.0 - HANDLES ADVANCED FREQUENCY)

from sqlalchemy.orm import Session
from typing import List, Optional

from app.db import models
from app.schemas import medication as medication_schema

def get_medication_by_id(db: Session, medication_id: int) -> Optional[models.Medication]:
    """
    Retrieves a single medication by its ID.
    """
    return db.query(models.Medication).filter(models.Medication.id == medication_id).first()

def get_medications_by_user(db: Session, owner_id: int) -> List[models.Medication]:
    """
    Retrieves all medications for a specific user.
    """
    return db.query(models.Medication).filter(models.Medication.owner_id == owner_id).all()


def create_user_medication(
    db: Session, medication: medication_schema.MedicationCreate, owner_id: int
) -> models.Medication:
    """
    Creates a new medication associated with a user, including advanced frequency details.
    """
    # --- YEH BADLAAV HAI ---
    # Ab hum .model_dump() ka istemal kar rahe hain jo naye Pydantic versions ke liye behtar hai
    # aur saare naye fields ko automatically handle karta hai.
    db_medication = models.Medication(**medication.model_dump(), owner_id=owner_id)
    db.add(db_medication)
    db.commit()
    db.refresh(db_medication)
    return db_medication


def update_medication(
    db: Session, db_medication: models.Medication, medication_in: medication_schema.MedicationUpdate
) -> models.Medication:
    """
    Updates a medication's details, including advanced frequency.
    """
    # --- YEH BADLAAV HAI ---
    # Yeh function ab naye frequency_type aur frequency_details fields ko bhi update kar sakta hai.
    update_data = medication_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_medication, key, value)
    
    db.add(db_medication)
    db.commit()
    db.refresh(db_medication)
    return db_medication


def delete_medication(db: Session, db_medication: models.Medication) -> models.Medication:
    """
    Deletes a medication from the database.
    """
    db.delete(db_medication)
    db.commit()
    return db_medication

def create_medication_log(
    db: Session, medication_id: int, owner_id: int
) -> models.MedicationLog:
    """
    Creates a new log entry in the MedicationLog table.
    """
    db_log = models.MedicationLog(
        medication_id=medication_id,
        owner_id=owner_id
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

