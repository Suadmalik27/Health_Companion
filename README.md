# 🩺 Health Companion - Senior Citizen Care App

A comprehensive web application designed to assist senior citizens in managing their daily health routines, including medication schedules, doctor appointments, and emergency contacts. Built with a FastAPI backend and a Streamlit frontend.

## ✨ Features

- ✅ **User Authentication:** Secure login, registration, and password reset functionality.
- ✅ **Dashboard:** A clean, at-a-glance view of today's medications, appointments, and a daily health tip.
- ✅ **Medication Management:** Add, edit, delete, and track medications. Includes photo uploads for easy identification.
- ✅ **Appointment Management:** Schedule and manage doctor appointments with a visual calendar view and photo uploads for doctors.
- ✅ **Emergency SOS:** A persistent, one-click SOS bar for quick access to the primary emergency contact.
- ✅ **Tip Management:** A dedicated page to add, edit, and delete health tips that appear on the dashboard.
- ✅ **Advanced Personalization:**
    - User profile photo uploads.
    - Choice of 12-hour or 24-hour time format.
    - ☀️ Light Mode & 🌙 Dark Mode theme selection.
- ✅ **Automatic Reminders:** A background scheduler sends email reminders for upcoming medications.

## 🛠️ Tech Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL (on Supabase)
- **Frontend:** Streamlit
- **Authentication:** JWT with Passlib for password hashing
- **Key Libraries:** Uvicorn, Psycopg2, APScheduler, Streamlit-Calendar, Python-Dotenv

## 🚀 Setup & Installation

### 1. Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment (e.g., using Python 3.10)
py -3.10 -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create a .env file from the .env.example and fill in your details
# (Database URL, Secret Key, Email credentials, etc.)

# Run the backend server
uvicorn app.main:app --reload

# Open a new terminal
# Navigate to the frontend directory
cd frontend

# Activate the same virtual environment from the backend setup
..\backend\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run streamlit_app.py