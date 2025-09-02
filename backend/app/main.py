# backend/app/main.py (FINAL, COMPLETE & DEPLOYMENT-READY VERSION)

import sys
import os

# --- CRITICAL PATH FIX (MUST BE AT THE TOP) ---
# This ensures all 'app.' imports work correctly everywhere.
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)
# --- END OF FIX ---

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.database import engine, Base
from app.utils.scheduler import send_daily_reminders

# --- Database Initialization ---
# This creates all tables defined in models.py when the app starts
Base.metadata.create_all(bind=engine)

# --- Scheduler Setup ---
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown events."""
    print("--- Starting up application and scheduler ---")
    # Schedule the job to run every day at 8:00 AM India time
    scheduler.add_job(
        send_daily_reminders, 
        'cron', 
        hour=8, 
        minute=0, 
        timezone='Asia/Kolkata',
        id="daily_reminder_job",
        replace_existing=True
    )
    scheduler.start()
    yield
    # On shutdown
    print("--- Shutting down application and scheduler ---")
    scheduler.shutdown()

# --- FastAPI Application Instance ---
app = FastAPI(
    title="Senior Citizen Support API",
    description="API for managing senior citizen's health information like medications, appointments, and contacts.",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json", # Standardized URL for docs
    lifespan=lifespan # Use the modern lifespan event handler
)

# --- CORS (Cross-Origin Resource Sharing) Configuration ---
# Allows your frontend to communicate with your backend
app.add_middleware(
    CORSMiddleware,
    # Add all allowed origins here
    allow_origins=[
        settings.FRONTEND_URL,          # For local development from .env
                 # Explicitly for local dev
        "https://healthcompanion3.streamlit.app" # Your deployed app URL
    ],
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# --- Static File Serving (for future image uploads) ---
# Create the directory if it doesn't exist to prevent errors on startup
os.makedirs("uploaded_images", exist_ok=True) 
# This line serves files from the 'uploaded_images' directory at the '/uploaded_images' URL
app.mount("/uploaded_images", StaticFiles(directory="uploaded_images"), name="uploaded_images")


# --- Include API Routers ---
# This attaches all your specific API endpoints (users, meds, etc.) to the main app
app.include_router(api_router, prefix="/api/v1")


# --- Root Endpoint ---
# A simple endpoint to check if the API is running
@app.get("/", tags=["Root"])
def read_root():
    """A simple health check endpoint."""
    return {"message": "Welcome to the Senior Citizen Support API hello!"}

