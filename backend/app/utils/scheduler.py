# backend/utils/scheduler.py (VERSION 2.0 - ADVANCED REMINDER LOGIC)

from sqlalchemy import and_
from datetime import datetime
import pytz

from app.db.database import SessionLocal
from app.db import models
from .email_utils import send_email

def send_daily_reminders():
    """
    The main job that runs daily. It now uses advanced logic to figure out
    which medications are due today based on their frequency settings.
    """
    print(f"--- Running daily reminder job at {datetime.now()} ---")
    db = SessionLocal()
    
    # Set the timezone to India Standard Time
    IST = pytz.timezone('Asia/Kolkata')
    now_in_ist = datetime.now(IST)
    today_in_ist = now_in_ist.date()
    today_weekday = now_in_ist.strftime('%A') # e.g., "Monday"
    today_day_of_month = now_in_ist.day # e.g., 15

    try:
        # Get all active users who have notifications enabled
        users_to_remind = db.query(models.User).filter(
            models.User.is_active == True,
            models.User.notifications_enabled == True
        ).all()
        
        for user in users_to_remind:
            meds_due_today = []
            
            # Get all medications for the user
            all_user_meds = db.query(models.Medication).filter(models.Medication.owner_id == user.id).all()

            # --- YEH NAYA, SMART FILTERING LOGIC HAI ---
            for med in all_user_meds:
                is_due = False
                freq_type = med.frequency_type
                freq_details = med.frequency_details

                if freq_type == "Daily":
                    is_due = True
                elif freq_type == "Weekly" and isinstance(freq_details, list):
                    if today_weekday in freq_details:
                        is_due = True
                elif freq_type == "Monthly" and isinstance(freq_details, int):
                    if today_day_of_month == freq_details:
                        is_due = True
                
                if is_due:
                    # Check if it has already been taken today
                    log_today = db.query(models.MedicationLog).filter(
                        models.MedicationLog.owner_id == user.id,
                        models.MedicationLog.medication_id == med.id,
                        cast(models.MedicationLog.taken_at.op('AT TIME ZONE')('Asia/Kolkata'), Date) == today_in_ist
                    ).first()

                    if not log_today:
                        meds_due_today.append(med)

            # --- Find appointments for today for this user (logic remains similar) ---
            appts_today = db.query(models.Appointment).filter(
                models.Appointment.owner_id == user.id,
                cast(models.Appointment.appointment_datetime.op('AT TIME ZONE')('Asia/Kolkata'), Date) == today_in_ist
            ).all()

            # If there's nothing to remind, skip to the next user
            if not meds_due_today and not appts_today:
                continue

            # --- Format and Send the Email ---
            subject = "Your Daily Health Reminders"
            html_content = f"<html><body><h2>Hello {user.full_name},</h2><p>Here are your health reminders for today, {today_in_ist.strftime('%B %d, %Y')}:</p>"
            text_content = f"Hello {user.full_name},\nHere are your reminders for today:\n"

            if meds_due_today:
                html_content += "<h3>💊 Medications to Take:</h3><ul>"
                text_content += "\n--- Medications to Take ---\n"
                for med in meds_due_today:
                    timing = med.meal_timing or (med.specific_time.strftime('%I:%M %p') if med.specific_time else 'Anytime')
                    html_content += f"<li><b>{med.name}</b> ({med.dosage}) - Take {timing}</li>"
                    text_content += f"- {med.name} ({med.dosage}) - Take {timing}\n"
                html_content += "</ul>"

            if appts_today:
                html_content += "<h3>🗓️ Appointments Today:</h3><ul>"
                text_content += "\n--- Appointments Today ---\n"
                for appt in appts_today:
                    appt_dt_ist = appt.appointment_datetime.astimezone(IST)
                    appt_time_str = appt_dt_ist.strftime('%I:%M %p')
                    html_content += f"<li><b>Dr. {appt.doctor_name}</b> at {appt_time_str}</li>"
                    text_content += f"- Dr. {appt.doctor_name} at {appt_time_str}\n"
                html_content += "</ul>"
            
            html_content += "<p>Have a healthy day!</p></body></html>"
            
            send_email(user.email, subject, html_content, text_content)

    finally:
        db.close()
    print("--- Daily reminder job finished ---")
