# backend/app/crud/crud_contact.py

from sqlalchemy.orm import Session
from typing import List

from app.db import models
from app.schemas import contact as contact_schema

def get_contacts_by_user(db: Session, owner_id: int) -> List[models.EmergencyContact]:
    """
    Retrieves all emergency contacts for a specific user.
    """
    return db.query(models.EmergencyContact).filter(models.EmergencyContact.owner_id == owner_id).all()


def create_user_contact(
    db: Session, contact: contact_schema.ContactCreate, owner_id: int
) -> models.EmergencyContact:
    """
    Creates a new emergency contact associated with a user.
    """
    db_contact = models.EmergencyContact(**contact.model_dump(), owner_id=owner_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, db_contact: models.EmergencyContact) -> models.EmergencyContact:
    """
    Deletes an emergency contact from the database.
    """
    db.delete(db_contact)
    db.commit()
    return db_contact