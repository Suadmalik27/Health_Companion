# backend/app/main.py (Fully Updated with Static File Serving)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # <-- YEH IMPORT ADD KIYA GAYA HAI
from .scheduler import scheduler, send_medication_reminders
# Import database and models
from .database import engine, Base 

# Import all your routers
from .routes import user_routes
from .routes import medication_routes
from .routes import appointment_routes
from .routes import contact_routes
from .routes import tip_routes


# --- Database Initialization ---
# This creates all the tables in your database when the application starts.
Base.metadata.create_all(bind=engine)


# --- FastAPI Application Instance ---
app = FastAPI(
    title="Senior Health Support API",
    description="API for managing senior citizen's health information like medications, appointments, and contacts.",
    version="1.0.0",
)


# --- CORS (Cross-Origin Resource Sharing) Configuration ---
# Allows your Streamlit frontend to communicate with your FastAPI backend.
origins = [
    "http://localhost",
    "http://localhost:8501",
    # Add your deployed Streamlit Cloud URL here later
    # "https://your-streamlit-app-url.streamlit.app", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- NAYA CODE: STATIC FILE SERVING ---
# This line tells FastAPI to serve the images from the 'uploaded_images' directory
# at the URL path '/uploaded_images'. This is how the frontend will display them.
app.mount("/uploaded_images", StaticFiles(directory="uploaded_images"), name="uploaded_images")
# --- NAYA CODE KHATAM ---


# --- Include Routers ---
# Attaches all your specific API endpoints to the main application.
app.include_router(user_routes.router)
app.include_router(medication_routes.router)
app.include_router(appointment_routes.router)
app.include_router(contact_routes.router)
app.include_router(tip_routes.router)
@app.on_event("startup")
async def startup_event():
    """Starts the scheduler when the FastAPI application starts."""
    # Har minute 'send_medication_reminders' function ko chalao
    scheduler.add_job(send_medication_reminders, 'interval', minutes=1, id="med_reminder_job")
    scheduler.start()
    print("Scheduler started...")

@app.on_event("shutdown")
async def shutdown_event():
    """Stops the scheduler when the FastAPI application shuts down."""
    scheduler.shutdown()
    print("Scheduler stopped...")

# --- Root Endpoint (Optional) ---
# A simple endpoint to check if the API is running.
@app.get("/")
def root():
    return {"message": "Welcome to the Senior Health Support API! Visit /docs for API documentation."}