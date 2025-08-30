# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.database import engine
from app.db import models
from app.utils.scheduler import send_daily_reminders # <-- IMPORT our job

# Create the table
models.Base.metadata.create_all(bind=engine)

# --- SCHEDULER SETUP ---
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    print("--- Starting up application and scheduler ---")
    # Schedule the job to run every day at 8:00 AM India time
    scheduler.add_job(send_daily_reminders, 'cron', hour=8, minute=0, timezone='Asia/Kolkata')
    # scheduler.add_job(send_daily_reminders, 'interval', seconds=60) # Runs every 60 seconds
    scheduler.start()
    yield
    # On shutdown
    print("--- Shutting down application and scheduler ---")
    scheduler.shutdown()

# Create the main FastAPI application instance with the lifespan event handler
app = FastAPI(
    title="Senior Citizen Support API",
    openapi_url=f"/api/v1/openapi.json",
    lifespan=lifespan
)

# --- CORS Middleware (remains the same) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... (rest of the file remains the same) ...
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Senior Citizen Support API!"}