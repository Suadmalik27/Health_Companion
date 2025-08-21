# /backend/app/scheduler.py (New File)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta, time
from .database import SessionLocal
from . import models
from .utils import send_email

async def send_medication_reminders():
    """
    This job runs every minute to check for upcoming medications and sends email reminders.
    """
    print(f"[{datetime.now()}] Running medication reminder job...")
    db = SessionLocal()
    try:
        # 1. Saare users ko database se nikaalein
        users = db.query(models.User).all()

        for user in users:
            # 2. Har user ki active dawaiyon ko nikaalein
            medications = db.query(models.Medication).filter(
                models.Medication.owner_id == user.id,
                models.Medication.is_active == True
            ).all()

            if not medications:
                continue

            # 3. Agle 15 minute mein aane waali dawaiyon ko check karein
            now = datetime.now()
            # Hum 15 minute pehle reminder bhejenge
            reminder_window_start = (now + timedelta(minutes=14)).time()
            reminder_window_end = (now + timedelta(minutes=15)).time()

            for med in medications:
                # Check karein ki dawai ka samay reminder window ke beech mein hai ya nahi
                if reminder_window_start <= med.timing <= reminder_window_end:
                    print(f"Found upcoming medication for {user.email}: {med.name}")
                    
                    # 4. Email Bhejein
                    subject = f"Reminder: Time to take your medication - {med.name}"
                    body = f"""
                        <p>Hello {user.full_name or 'there'},</p>
                        <p>This is a friendly reminder to take your medication:</p>
                        <ul>
                            <li><strong>Medication:</strong> {med.name}</li>
                            <li><strong>Dosage:</strong> {med.dosage}</li>
                            <li><strong>Time:</strong> {med.timing.strftime('%I:%M %p')}</li>
                        </ul>
                        <p>Stay healthy!</p>
                        <p><em>- Your Health Companion App</em></p>
                    """
                    await send_email(subject, [user.email], body)
                    print(f"Reminder email sent to {user.email} for {med.name}.")

    finally:
        db.close()

# Scheduler ka ek instance banayein jise hum main app mein istemaal karenge
scheduler = AsyncIOScheduler(timezone="UTC") # Aap apne timezone ke hisaab se badal sakte hain