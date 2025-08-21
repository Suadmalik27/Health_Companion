# backend/app/routes/appointment_routes.py (Updated Code)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional # <--- Optional ko import karein
from datetime import date, datetime, time # <--- Inhein import karein

from .. import models
from ..database import get_db
from ..schemas import appointment_schema
from ..auth import get_current_user
from fastapi import File, UploadFile
import os
import shutil

# Directory jahan photos save hongi
UPLOAD_DIRECTORY = "./uploaded_images"

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)

@router.post("/", response_model=appointment_schema.AppointmentShow, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment: appointment_schema.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Creates a new appointment for the current user."""
    new_appointment = models.Appointment(
        **appointment.model_dump(),
        owner_id=current_user.id
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment

# --- YEH FUNCTION UPDATE HUA HAI ---
@router.get("/", response_model=List[appointment_schema.AppointmentShow])
def get_all_user_appointments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    start_date: Optional[date] = None, # Optional start date parameter
    end_date: Optional[date] = None    # Optional end date parameter
):
    """
    Gets a list of all appointments for the current user.
    Can be filtered by a start and end date.
    """
    # Start the base query
    query = db.query(models.Appointment).filter(models.Appointment.owner_id == current_user.id)

    # If start_date is provided, filter from the beginning of that day
    if start_date:
        query = query.filter(models.Appointment.appointment_datetime >= datetime.combine(start_date, time.min))

    # If end_date is provided, filter until the end of that day
    if end_date:
        query = query.filter(models.Appointment.appointment_datetime <= datetime.combine(end_date, time.max))

    # Order the results by date and execute the query
    appointments = query.order_by(models.Appointment.appointment_datetime.asc()).all()
    return appointments
# --- UPDATE KHATAM ---


@router.get("/{appointment_id}", response_model=appointment_schema.AppointmentShow)
def get_appointment_by_id(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Gets a specific appointment by its ID."""
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id,
        models.Appointment.owner_id == current_user.id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with id {appointment_id} not found"
        )
    return appointment

@router.put("/{appointment_id}", response_model=appointment_schema.AppointmentShow)
def update_appointment(
    appointment_id: int,
    appointment_update: appointment_schema.AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Updates a specific appointment by its ID."""
    appointment_query = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id,
        models.Appointment.owner_id == current_user.id
    )
    db_appointment = appointment_query.first()

    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with id {appointment_id} not found"
        )
    
    update_data = appointment_update.model_dump(exclude_unset=True)
    appointment_query.update(update_data, synchronize_session=False)
    
    db.commit()
    updated_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    return updated_appointment

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Deletes an appointment by its ID."""
    appointment_query = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id,
        models.Appointment.owner_id == current_user.id
    )
    appointment = appointment_query.first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with id {appointment_id} not found"
        )
    
    appointment_query.delete(synchronize_session=False)
    db.commit()
    
    return None
@router.put("/{appointment_id}/photo", response_model=appointment_schema.AppointmentShow)
def upload_appointment_photo(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    file: UploadFile = File(...)
):
    """Uploads a photo for a specific appointment."""
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id,
        models.Appointment.owner_id == current_user.id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    file_extension = os.path.splitext(file.filename)[1]
    filename = f"appointment_{appointment.id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    appointment.photo_url = file_path.replace("\\", "/")
    db.commit()
    db.refresh(appointment)
    return appointment