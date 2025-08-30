# backend/app/api/v1/endpoints/dashboard.py (FINAL, GUARANTEED PYTHON-BASED TIMEZONE FIX)

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone # Use Python's built-in timezone for awareness
import random
import pytz # Still needed for IST conversion

from app.api import deps
from app.db import models
from app.crud import crud_contact

router = APIRouter()

@router.get("/")
def get_dashboard_data(
    *,
    response: Response,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Retrieve dashboard data with a reliable, Python-based timezone conversion.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    IST = pytz.timezone('Asia/Kolkata')
    today_in_ist = datetime.now(IST).date()
    
    # --- 1. Get ALL daily medications ---
    all_daily_meds = db.query(models.Medication).filter(
        models.Medication.owner_id == current_user.id,
        # Sahi code (Naya)
        models.Medication.frequency_type == "Daily"
    ).all()
    
    # --- YEH FINAL, SABSE ROBUST FIX HAI: Python mein Timezone ko aache se handle karna ---
    # Hum user ke saare logs le kar unhe Python mein check karenge.
    all_user_logs = db.query(models.MedicationLog).filter(models.MedicationLog.owner_id == current_user.id).all()
    
    taken_today_ids = set() # Use a set to avoid duplicates
    for log in all_user_logs:
        timestamp = log.taken_at
        
        # Step 1: We know time is saved as UTC. If the DB driver returns a "naive"
        # datetime (no timezone info), we make it "aware" by setting its tz to UTC.
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        # Step 2: Now that we have a guaranteed UTC-aware datetime, convert it to IST.
        timestamp_ist = timestamp.astimezone(IST)
        
        # Step 3: Compare the date part.
        if timestamp_ist.date() == today_in_ist:
            taken_today_ids.add(log.medication_id)

    # --- 2. Get today's appointments using the same robust logic ---
    all_appointments = db.query(models.Appointment).filter(
        models.Appointment.owner_id == current_user.id
    ).all()

    todays_appointments = []
    upcoming_appointments = []
    for appt in all_appointments:
        if appt.appointment_datetime:
            timestamp = appt.appointment_datetime
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            
            timestamp_ist = timestamp.astimezone(IST)
            if timestamp_ist.date() >= today_in_ist:
                upcoming_appointments.append(appt)
                if timestamp_ist.date() == today_in_ist:
                    todays_appointments.append(appt)
    
    # Sort appointments by time
    upcoming_appointments.sort(key=lambda x: x.appointment_datetime)
    todays_appointments.sort(key=lambda x: x.appointment_datetime)
    
    # 3. Get emergency contacts and health tip
    emergency_contacts = crud_contact.get_contacts_by_user(db, owner_id=current_user.id)
    random_health_tip = db.query(models.HealthTip).order_by(func.random()).first()
    
    # 4. Prepare the final data payload
    return {
        "user_full_name": current_user.full_name,
        "summary": {
            "personalized_message": f"Namaste, {current_user.full_name.split()[0]}! You have {len(todays_appointments)} appointment(s) today.",
            "adherence_score": 95, # Dummy score for now
            "adherence_message": "Keep up the great work!"
        },
        "medications_today": {
            "all_daily": all_daily_meds,
            "taken_ids": list(taken_today_ids) # Convert set to list for JSON
        },
        "appointments": {
            "today": todays_appointments,
            "upcoming": upcoming_appointments
        },
        "reminders": { "refills": [] },
        "health_vitals": {},
        "emergency_contacts": emergency_contacts,
        "health_tip": random_health_tip.tip_text if random_health_tip else "Remember to stay active!"
    }

