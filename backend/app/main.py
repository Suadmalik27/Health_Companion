# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .scheduler import scheduler, send_medication_reminders
# Import database and models
from .database import engine, Base 

# Import all your routers
from .routes import user_routes
from .routes import medication_routes
from .routes import appointment_routes
from .routes import contact_routes
from .routes import tip_routes
import os


# --- Database Initialization ---
# Yeh application start hone par aapke database mein saare tables banata hai.
Base.metadata.create_all(bind=engine)


# --- FastAPI Application Instance ---
app = FastAPI(
    title="Senior Health Support API",
    description="API for managing senior citizen's health information like medications, appointments, and contacts.",
    version="1.0.0",
)

# --- CORS Middleware Configuration ---
# YEH NAYA CODE: CORS ke liye allowed origins define karein
origins = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "https://health-companion-backend-44ug.onrender.com",
    "https://health-companion-app.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- STATIC FILE SERVING ---
# Yeh line FastAPI ko 'uploaded_images' directory se images serve karne ke liye kehti hai.
# Hum yahan directory banate hain taaki yeh hamesha maujood rahe.
os.makedirs("uploaded_images", exist_ok=True)
app.mount("/uploaded_images", StaticFiles(directory="uploaded_images"), name="uploaded_images")


# --- Include Routers ---
# Yeh aapke sabhi API endpoints ko main application se jodta hai.
app.include_router(user_routes.router)
app.include_router(medication_routes.router)
app.include_router(appointment_routes.router)
app.include_router(contact_routes.router)
app.include_router(tip_routes.router)


# --- Scheduler Events ---
@app.on_event("startup")
async def startup_event():
    """FastAPI application start hone par scheduler ko start karta hai."""
    try:
        scheduler.add_job(send_medication_reminders, 'interval', minutes=1, id="med_reminder_job", replace_existing=True)
        scheduler.start()
        print("Scheduler started...")
    except Exception as e:
        print(f"Error starting scheduler: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """FastAPI application band hone par scheduler ko rokta hai."""
    scheduler.shutdown()
    print("Scheduler stopped...")


# --- Root Endpoint (Optional) ---
# Ek simple endpoint yeh check karne ke liye ki API chal rahi hai ya nahi.
@app.get("/")
def root():
    return {"message": "Welcome to the Senior Health Support API! Visit /docs for API documentation new ."}
