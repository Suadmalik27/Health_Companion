# backend/app/routes/medication_routes.py (Updated with Logging Endpoints)

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime
import os
import shutil

# Local imports
from .. import models # models ko poora import karein
from ..database import get_db
from ..schemas import medication_schema
from ..auth import get_current_user

router = APIRouter(
    prefix="/medications",
    tags=["Medications"]
)

# Directory jahan photos save hongi
UPLOAD_DIRECTORY = "./uploaded_images"

@router.post("/", response_model=medication_schema.MedicationShow, status_code=status.HTTP_201_CREATED)
def create_medication(
    med: medication_schema.MedicationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Creates a new medication record for the current user."""
    new_med = models.Medication(**med.model_dump(), owner_id=current_user.id)
    db.add(new_med)
    db.commit()
    db.refresh(new_med)
    return new_med

@router.get("/", response_model=List[medication_schema.MedicationShow])
def get_user_medications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Gets a list of all medications for the current user."""
    meds = db.query(models.Medication).filter(models.Medication.owner_id == current_user.id).all()
    return meds

@router.put("/{med_id}", response_model=medication_schema.MedicationShow)
def update_medication(
    med_id: int,
    med_update: medication_schema.MedicationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Updates a specific medication by its ID."""
    med_query = db.query(models.Medication).filter(
        models.Medication.id == med_id,
        models.Medication.owner_id == current_user.id
    )
    db_med = med_query.first()
    if not db_med:
        raise HTTPException(status_code=404, detail=f"Medication with id {med_id} not found")
    
    update_data = med_update.model_dump(exclude_unset=True)
    med_query.update(update_data, synchronize_session=False)
    db.commit()
    updated_med = db.query(models.Medication).filter(models.Medication.id == med_id).first()
    return updated_med

@router.delete("/{med_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication(
    med_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Deletes a medication by its ID."""
    medication_query = db.query(models.Medication).filter(
        models.Medication.id == med_id,
        models.Medication.owner_id == current_user.id
    )
    medication = medication_query.first()
    if not medication:
        raise HTTPException(status_code=404, detail=f"Medication with id {med_id} not found")
    
    medication_query.delete(synchronize_session=False)
    db.commit()
    return None

@router.put("/{med_id}/photo", response_model=medication_schema.MedicationShow)
def upload_medication_photo(
    med_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    file: UploadFile = File(...)
):
    """Uploads a photo for a specific medication."""
    medication = db.query(models.Medication).filter(
        models.Medication.id == med_id,
        models.Medication.owner_id == current_user.id
    ).first()
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")

    file_extension = os.path.splitext(file.filename)[1]
    filename = f"medication_{medication.id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    medication.photo_url = file_path.replace("\\", "/")
    db.commit()
    db.refresh(medication)
    return medication

# --- NAYA CODE: MEDICATION LOGGING ENDPOINTS ---

@router.post("/{med_id}/log", status_code=status.HTTP_201_CREATED)
def log_medication_taken(
    med_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Logs that a specific medication has been taken by the user today."""
    medication = db.query(models.Medication).filter(
        models.Medication.id == med_id,
        models.Medication.owner_id == current_user.id
    ).first()
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")

    today = date.today()
    
    existing_log = db.query(models.MedicationLog).filter(
        models.MedicationLog.medication_id == med_id,
        models.MedicationLog.owner_id == current_user.id,
        models.MedicationLog.date_taken == today
    ).first()
    if existing_log:
        return {"message": "Medication already logged for today."}

    new_log = models.MedicationLog(
        medication_id=med_id,
        owner_id=current_user.id,
        date_taken=today,
        time_taken=datetime.now().time()
    )
    db.add(new_log)
    db.commit()
    return {"message": "Medication logged successfully."}

@router.get("/log/{log_date}", response_model=List[int])
def get_medication_log_for_date(
    log_date: date,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Returns a list of medication IDs taken on a specific date."""
    logs = db.query(models.MedicationLog).filter(
        models.MedicationLog.owner_id == current_user.id,
        models.MedicationLog.date_taken == log_date
    ).all()
    return [log.medication_id for log in logs]

# --- NAYA CODE KHATAM ---