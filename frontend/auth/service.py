# frontend/auth/service.py (FINAL, VERIFIED AND COMPLETE VERSION)

import requests
from typing import List, Dict, Any

# Define the base URL of your FastAPI backend
BASE_URL = "https://health-companion-backend-44ug.onrender.com/api/v1"
TOKEN_COOKIE_NAME = "senior_citizen_support_token"

# --- AUTHENTICATION & USER MANAGEMENT ---

def register_user(full_name: str, email: str, password: str) -> tuple[bool, str]:
    """ Registers a new user account. """
    url = f"{BASE_URL}/users/"
    user_data = {"full_name": full_name, "email": email, "password": password}
    try:
        response = requests.post(url, json=user_data)
        if response.status_code == 201: return True, "Account created successfully! Please login."
        else: return False, f"Registration failed: {response.json().get('detail', 'Unknown error')}"
    except requests.RequestException: return False, "Server communication error."

def login_user(email: str, password: str) -> tuple[bool, str | dict]:
    """ Logs in a user and retrieves an access token. """
    url = f"{BASE_URL}/auth/login/access-token"
    form_data = {"username": email, "password": password}
    try:
        response = requests.post(url, data=form_data)
        if response.status_code == 200: return True, response.json()
        else: return False, f"Login failed: {response.json().get('detail', 'Unknown error')}"
    except requests.RequestException: return False, "Server communication error."

def request_password_reset(email: str) -> tuple[bool, str]:
    """ Sends a password reset request email. """
    url = f"{BASE_URL}/auth/forgot-password"
    payload = {"email": email}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200: return True, response.json().get("msg")
        else: return False, response.json().get("detail", "An unknown error occurred.")
    except requests.RequestException: return False, "Server communication error."

def set_new_password(token: str, new_password: str) -> tuple[bool, str]:
    """ Sets a new password using a reset token. """
    url = f"{BASE_URL}/auth/reset-password"
    payload = {"token": token, "new_password": new_password}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200: return True, response.json().get("msg")
        else: return False, response.json().get("detail", "Failed to reset password.")
    except requests.RequestException: return False, "Server communication error."

# --- MAIN DATA FETCHING ---

def get_dashboard_data(token: str) -> tuple[bool, dict | str]:
    """ Fetches the main dashboard data for the current user. """
    url = f"{BASE_URL}/dashboard/"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200: return True, response.json()
        else: return False, response.json().get("detail", "Authentication failed.")
    except requests.RequestException: return False, "Server communication error."

# --- MEDICATIONS ---

def get_medications(token: str) -> tuple[bool, List[Dict[str, Any]] | str]:
    """ Fetches all medications for the user. """
    url = f"{BASE_URL}/medications/"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200: return True, response.json()
        else: return False, response.json().get("detail", "Failed to fetch medications.")
    except requests.RequestException: return False, "Server communication error."

def add_medication(token: str, payload: dict) -> tuple[bool, str]:
    """ Adds a new medication for the user. """
    url = f"{BASE_URL}/medications/"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201: return True, "Medication added successfully!"
        else: return False, response.json().get("detail", "Failed to add medication.")
    except requests.RequestException: return False, "Server communication error."

def delete_medication(token: str, med_id: int) -> tuple[bool, str]:
    """ Deletes a medication for the user. """
    url = f"{BASE_URL}/medications/{med_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200: return True, "Medication deleted successfully."
        else: return False, response.json().get("detail", "Failed to delete medication.")
    except requests.RequestException: return False, "Server communication error."

def mark_medication_as_taken(token: str, med_id: int) -> tuple[bool, str]:
    """ Marks a medication as taken by creating a log entry. """
    url = f"{BASE_URL}/medications/{med_id}/taken"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200: return True, "Medication marked as taken."
        else: return False, response.json().get("detail", "Failed to mark as taken.")
    except requests.RequestException: return False, "Server communication error."

# --- APPOINTMENTS ---

def get_appointments(token: str) -> tuple[bool, List[Dict[str, Any]] | str]:
    """ Fetches all appointments for the user. """
    url = f"{BASE_URL}/appointments/"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200: return True, response.json()
        else: return False, response.json().get("detail", "Failed to fetch appointments.")
    except requests.RequestException: return False, "Server communication error."

def add_appointment(token: str, payload: dict) -> tuple[bool, str]:
    """ Adds a new appointment for the user. """
    url = f"{BASE_URL}/appointments/"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201: return True, "Appointment added successfully!"
        else:
            detail = response.json().get("detail", "Failed to add appointment.")
            if isinstance(detail, list): detail = " ".join([d.get('msg', '') for d in detail])
            return False, str(detail)
    except requests.RequestException: return False, "Server communication error."

def delete_appointment(token: str, appt_id: int) -> tuple[bool, str]:
    """ Deletes an appointment for the user. """
    url = f"{BASE_URL}/appointments/{appt_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200: return True, "Appointment deleted successfully."
        else: return False, response.json().get("detail", "Failed to delete appointment.")
    except requests.RequestException: return False, "Server communication error."

# --- CONTACTS ---

def get_contacts(token: str) -> tuple[bool, List[Dict[str, Any]] | str]:
    """ Fetches all emergency contacts for the user. """
    url = f"{BASE_URL}/contacts/"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200: return True, response.json()
        else: return False, response.json().get("detail", "Failed to fetch contacts.")
    except requests.RequestException: return False, "Server communication error."

def add_contact(token: str, payload: dict) -> tuple[bool, str]:
    """ Adds a new emergency contact for the user. """
    url = f"{BASE_URL}/contacts/"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201: return True, "Contact added successfully!"
        else: return False, response.json().get("detail", "Failed to add contact.")
    except requests.RequestException: return False, "Server communication error."

def delete_contact(token: str, contact_id: int) -> tuple[bool, str]:
    """ Deletes an emergency contact for the user. """
    url = f"{BASE_URL}/contacts/{contact_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200: return True, "Contact deleted successfully."
        else: return False, response.json().get("detail", "Failed to delete contact.")
    except requests.RequestException: return False, "Server communication error."

# --- PROFILE ---

def get_profile(token: str) -> tuple[bool, dict | str]:
    """ Fetches the profile for the current logged-in user. """
    url = f"{BASE_URL}/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200: return True, response.json()
        else: return False, response.json().get("detail", "Failed to fetch profile.")
    except requests.RequestException: return False, "Server communication error."

def update_profile(token: str, payload: dict) -> tuple[bool, str]:
    """ Updates the current user's profile information. """
    url = f"{BASE_URL}/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.put(url, headers=headers, json=payload)
        if response.status_code == 200: return True, "Profile updated successfully!"
        else: return False, response.json().get("detail", "Failed to update profile.")
    except requests.RequestException: return False, "Server communication error."

# --- HEALTH TIPS (FOR ADMINS) ---

def get_all_tips(token: str) -> tuple[bool, List[Dict[str, Any]] | str]:
    """ Fetches all health tips from the database. """
    url = f"{BASE_URL}/tips/"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200: return True, response.json()
        else: return False, response.json().get("detail", "Failed to fetch tips.")
    except requests.RequestException: return False, "Server communication error."

def add_health_tip(token: str, payload: dict) -> tuple[bool, str]:
    """ Adds a new health tip to the database. """
    url = f"{BASE_URL}/tips/"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            return True, "Health tip added successfully!"
        else:
            return False, response.json().get("detail", "Failed to add health tip.")
    except requests.RequestException: return False, "Server communication error."

def delete_health_tip(token: str, tip_id: int) -> tuple[bool, str]:
    """ Deletes a specific health tip from the database. """
    url = f"{BASE_URL}/tips/{tip_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200: return True, "Tip deleted successfully."
        else: return False, response.json().get("detail", "Failed to delete tip.")
    except requests.RequestException: return False, "Server communication error."




