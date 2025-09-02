# backend/app/api/v1/api.py (FINAL VERSION - WITH TIPS ROUTER)

from fastapi import APIRouter
from .endpoints.auth import router as auth_router

from app.api.v1.endpoints import (
    users, 
    auth, 
    dashboard, 
    medications,
    appointments,
    contacts,
    tips # <-- Naye tips endpoint ko yahan import karna hai
)

# Create the main router for API version 1
api_router = APIRouter()

# --- Yahan saare routers ko joda jaata hai ---
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(medications.router, prefix="/medications", tags=["Medications"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["Contacts"])
api_router.include_router(tips.router, prefix="/tips", tags=["Health Tips"]) # <-- Naye tips router ko yahan jodna hai
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])

