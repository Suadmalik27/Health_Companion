# backend/app/crud/crud_appointment.py

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from app.db import models
from app.schemas import appointment as appointment_schema

def get_appointments_by_user(db: Session, owner_id: int) -> List[models.Appointment]:
    """
    Retrieves all appointments for a specific user, ordered by most recent first.
    """
    return (
        db.query(models.Appointment)
        .filter(models.Appointment.owner_id == owner_id)
        .order_by(desc(models.Appointment.appointment_datetime))
        .all()
    )


def create_user_appointment(
    db: Session, appointment: appointment_schema.AppointmentCreate, owner_id: int
) -> models.Appointment:
    """
    Creates a new appointment associated with a user.
    """
    db_appointment = models.Appointment(**appointment.model_dump(), owner_id=owner_id)
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment