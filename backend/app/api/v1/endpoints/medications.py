# backend/app/api/v1/endpoints/medications.py (VERSION 3.0 - WITH ADVANCED VALIDATION)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from app.api import deps
from app.db import models
from app.crud import crud_medication
from app.schemas import medication as medication_schema

router = APIRouter()

@router.get("/", response_model=List[medication_schema.Medication])
def read_medications(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Retrieve all medications for the current logged-in user.
    """
    return crud_medication.get_medications_by_user(db, owner_id=current_user.id)


@router.post("/", response_model=medication_schema.Medication, status_code=status.HTTP_201_CREATED)
def create_medication(
    *,
    db: Session = Depends(deps.get_db),
    medication_in: medication_schema.MedicationCreate,
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Create a new medication with validation for advanced frequency types.
    """
    # --- YEH NAYA VALIDATION LOGIC HAI ---
    
    # Basic timing validation
    if medication_in.timing_type == "Specific-Time" and not medication_in.specific_time:
        raise HTTPException(status_code=400, detail="Specific time is required for this timing type.")
    if medication_in.timing_type == "Meal-Related" and not medication_in.meal_timing:
        raise HTTPException(status_code=400, detail="Meal timing is required for this timing type.")

    # Advanced frequency validation
    freq_type = medication_in.frequency_type
    freq_details = medication_in.frequency_details
    
    if freq_type == "Weekly" and (not isinstance(freq_details, list) or not freq_details):
        raise HTTPException(status_code=400, detail="For a weekly frequency, you must select at least one day.")
    
    if freq_type == "Monthly" and (not isinstance(freq_details, int) or not (1 <= freq_details <= 31)):
        raise HTTPException(status_code=400, detail="For a monthly frequency, you must provide a valid day of the month (1-31).")

    return crud_medication.create_user_medication(
        db=db, medication=medication_in, owner_id=current_user.id
    )


@router.put("/{med_id}", response_model=medication_schema.Medication)
def update_medication(
    *,
    db: Session = Depends(deps.get_db),
    med_id: int,
    medication_in: medication_schema.MedicationUpdate,
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Update a medication's details for the current user.
    """
    db_medication = crud_medication.get_medication_by_id(db, medication_id=med_id)
    if not db_medication or db_medication.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Medication not found")
    
    return crud_medication.update_medication(db, db_medication=db_medication, medication_in=medication_in)


@router.delete("/{med_id}", response_model=medication_schema.Medication)
def delete_medication(
    *,
    db: Session = Depends(deps.get_db),
    med_id: int,
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Delete a medication for the current user.
    """
    db_medication = crud_medication.get_medication_by_id(db, medication_id=med_id)
    if not db_medication or db_medication.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Medication not found")
        
    return crud_medication.delete_medication(db, db_medication=db_medication)


@router.post("/{med_id}/taken", response_model=medication_schema.MedicationLog)
def mark_medication_as_taken(
    *,
    db: Session = Depends(deps.get_db),
    med_id: int,
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Mark a medication as taken by creating a new log entry.
    """
    db_medication = crud_medication.get_medication_by_id(db, medication_id=med_id)
    if not db_medication or db_medication.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Medication not found")
    
    log_entry = crud_medication.create_medication_log(
        db=db, medication_id=med_id, owner_id=current_user.id
    )
    
    update_data = medication_schema.MedicationUpdate(last_taken_at=datetime.now(timezone.utc))
    crud_medication.update_medication(db, db_medication=db_medication, medication_in=update_data)
    
    return log_entry

