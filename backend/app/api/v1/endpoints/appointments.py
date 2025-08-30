# backend/app/api/v1/endpoints/appointments.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.db import models
from app.crud import crud_appointment, crud_user # We need crud_appointment for a helper
from app.schemas import appointment as appointment_schema

router = APIRouter()

# Helper function to get and verify an appointment
def get_appointment_and_verify_owner(db: Session, appt_id: int, current_user: models.User) -> models.Appointment:
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appt_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appointment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return appointment

@router.get("/", response_model=List[appointment_schema.Appointment])
def read_appointments(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Retrieve all appointments for the current logged-in user."""
    return crud_appointment.get_appointments_by_user(db, owner_id=current_user.id)

@router.post("/", response_model=appointment_schema.Appointment, status_code=status.HTTP_201_CREATED)
def create_appointment(
    *,
    db: Session = Depends(deps.get_db),
    appointment_in: appointment_schema.AppointmentCreate,
    current_user: models.User = Depends(deps.get_current_user)
):
    """Create a new appointment for the current logged-in user."""
    return crud_appointment.create_user_appointment(
        db=db, appointment=appointment_in, owner_id=current_user.id
    )

@router.delete("/{appt_id}", response_model=appointment_schema.Appointment)
def delete_appointment(
    *,
    db: Session = Depends(deps.get_db),
    appt_id: int,
    current_user: models.User = Depends(deps.get_current_user)
):
    """Delete an appointment for the current user."""
    appointment = get_appointment_and_verify_owner(db, appt_id, current_user)
    
    db.delete(appointment)
    db.commit()
    return appointment