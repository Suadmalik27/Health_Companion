# backend/app/api/v1/endpoints/contacts.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.db import models
from app.crud import crud_contact
from app.schemas import contact as contact_schema

router = APIRouter()

def get_contact_and_verify_owner(db: Session, contact_id: int, current_user: models.User) -> models.EmergencyContact:
    """Helper function to get a contact and verify its owner."""
    contact = db.query(models.EmergencyContact).filter(models.EmergencyContact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    if contact.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return contact

@router.get("/", response_model=List[contact_schema.Contact])
def read_contacts(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Retrieve all emergency contacts for the current logged-in user.
    """
    contacts = crud_contact.get_contacts_by_user(db, owner_id=current_user.id)
    return contacts


@router.post("/", response_model=contact_schema.Contact, status_code=status.HTTP_201_CREATED)
def create_contact(
    *,
    db: Session = Depends(deps.get_db),
    contact_in: contact_schema.ContactCreate,
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Create a new emergency contact for the current logged-in user.
    """
    # Optional: Check if the user already has the maximum number of contacts (e.g., 3)
    # current_contacts = crud_contact.get_contacts_by_user(db, owner_id=current_user.id)
    # if len(current_contacts) >= 3:
    #     raise HTTPException(status_code=400, detail="Maximum number of emergency contacts reached.")
        
    contact = crud_contact.create_user_contact(
        db=db, contact=contact_in, owner_id=current_user.id
    )
    return contact


@router.delete("/{contact_id}", response_model=contact_schema.Contact)
def delete_contact(
    *,
    db: Session = Depends(deps.get_db),
    contact_id: int,
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Delete an emergency contact for the current user.
    """
    contact = get_contact_and_verify_owner(db, contact_id, current_user)
    deleted_contact = crud_contact.delete_contact(db, db_contact=contact)
    return deleted_contact