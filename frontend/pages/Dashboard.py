# frontend/pages/Dashboard.py

import streamlit as st
import requests
from datetime import datetime, date, time, timedelta
import pytz
from PIL import Image
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Dashboard - Health Companion",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
def local_css():
    st.markdown("""
    <style>
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    }
    .medication-card, .appointment-card, .tip-card {
        border-left: 4px solid;
        padding-left: 1rem;
    }
    .medication-card {
        border-left-color: #4CAF50;
    }
    .appointment-card {
        border-left-color: #2196F3;
    }
    .tip-card {
        border-left-color: #FF9800;
    }
    .sos-button {
        background: linear-gradient(135deg, #ff4b4b 0%, #c00000 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .sos-button:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.3);
    }
    .time-display {
        font-size: 2.5rem;
        font-weight: bold;
        color: white;
    }
    .date-display {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.8);
    }
    .greeting {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .section-title {
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
        color: #333;
    }
    .empty-state {
        text-align: center;
        padding: 2rem;
        color: #888;
    }
    .empty-state i {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    .profile-img {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid white;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# API base URL
API_BASE_URL = "http://localhost:8000"

def get_auth_headers():
    """Get authorization headers with access token"""
    if 'access_token' not in st.session_state:
        return None
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

def fetch_user_data():
    """Fetch current user's data"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    try:
        response = requests.get(f"{API_BASE_URL}/users/me", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def fetch_medications():
    """Fetch user's medications"""
    headers = get_auth_headers()
    if not headers:
        return []
    
    try:
        response = requests.get(f"{API_BASE_URL}/medications/", headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def fetch_appointments():
    """Fetch user's appointments for today"""
    headers = get_auth_headers()
    if not headers:
        return []
    
    try:
        today = date.today()
        response = requests.get(
            f"{API_BASE_URL}/appointments/?start_date={today}&end_date={today}", 
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def fetch_random_tip():
    """Fetch a random health tip"""
    try:
        response = requests.get(f"{API_BASE_URL}/tips/random")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def log_medication_taken(medication_id):
    """Log that a medication was taken"""
    headers = get_auth_headers()
    if not headers:
        return False
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/medications/{medication_id}/log", 
            headers=headers
        )
        return response.status_code == 201
    except:
        return False

def get_medication_log():
    """Get today's medication log"""
    headers = get_auth_headers()
    if not headers:
        return []
    
    try:
        today = date.today()
        response = requests.get(
            f"{API_BASE_URL}/medications/log/{today}", 
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_primary_contact():
    """Get primary emergency contact"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    try:
        response = requests.get(f"{API_BASE_URL}/contacts/", headers=headers)
        if response.status_code == 200 and response.json():
            return response.json()[0]  # Return first contact
        return None
    except:
        return None

def make_sos_call():
    """Initiate SOS call to primary contact"""
    contact = get_primary_contact()
    if contact:
        st.success(f"🆘 SOS alert sent to {contact['name']} ({contact['phone_number']})")
        # In a real app, this would trigger an actual call/SMS
    else:
        st.warning("No emergency contacts found. Please add contacts in the Contacts page.")

# Check if user is logged in
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access the dashboard")
    st.stop()

# Fetch data
user_data = fetch_user_data()
medications = fetch_medications()
today_appointments = fetch_appointments()
health_tip = fetch_random_tip()
medication_log = get_medication_log()
primary_contact = get_primary_contact()

# Get current time based on user preference
time_format = user_data.get('time_format', '12h') if user_data else '12h'
current_time = datetime.now()
if time_format == '12h':
    time_str = current_time.strftime("%I:%M %p")
else:
    time_str = current_time.strftime("%H:%M")
date_str = current_time.strftime("%A, %B %d, %Y")

# Dashboard Header
st.markdown('<div class="dashboard-header">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if user_data:
        greeting = "Good "
        hour = current_time.hour
        if 5 <= hour < 12:
            greeting += "Morning"
        elif 12 <= hour < 17:
            greeting += "Afternoon"
        elif 17 <= hour < 21:
            greeting += "Evening"
        else:
            greeting += "Night"
        
        st.markdown(f'<div class="greeting">{greeting}, {user_data.get("full_name", "User")}!</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="time-display">{time_str}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="date-display">{date_str}</div>', unsafe_allow_html=True)

with col3:
    if user_data and user_data.get('profile_picture_url'):
        try:
            # Display profile picture
            response = requests.get(user_data['profile_picture_url'])
            img = Image.open(io.BytesIO(response.content))
            st.image(img, use_column_width=False, width=80, output_format='auto')
        except:
            st.image("👤", width=80)
    else:
        st.image("👤", width=80)
    
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.access_token = None
        st.session_state.user_email = None
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)  # Close dashboard-header

# SOS Emergency Button
if primary_contact:
    st.markdown(f"""
    <div class="sos-button" onclick="alert('SOS activated! Calling {primary_contact['name']} at {primary_contact['phone_number']}')">
        🆘 EMERGENCY SOS - CALL {primary_contact['name'].upper()}
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="sos-button" onclick="alert('Please add emergency contacts first')">
        🆘 EMERGENCY SOS - ADD CONTACTS FIRST
    </div>
    """, unsafe_allow_html=True)

# Main Content
col1, col2 = st.columns([2, 1])

with col1:
    # Today's Medications
    st.markdown("### 💊 Today's Medications")
    
    if medications:
        active_meds = [med for med in medications if med.get('is_active', True)]
        taken_meds = set(medication_log)
        
        for med in active_meds:
            med_time = datetime.strptime(med['timing'], "%H:%M:%S").time() if isinstance(med['timing'], str) else med['timing']
            is_taken = med['id'] in taken_meds
            is_upcoming = datetime.now().time() < med_time
            
            med_col1, med_col2 = st.columns([3, 1])
            
            with med_col1:
                status_icon = "✅" if is_taken else "⏰" if is_upcoming else "❌"
                st.markdown(f"""
                <div class="card medication-card">
                    <b>{med['name']}</b> - {med['dosage']}<br>
                    <small>Time: {med_time.strftime('%I:%M %p') if time_format == '12h' else med_time.strftime('%H:%M')}</small>
                    <div>{status_icon} {'Taken' if is_taken else 'Upcoming' if is_upcoming else 'Missed'}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with med_col2:
                if not is_taken and is_upcoming:
                    if st.button("Mark Taken", key=f"med_{med['id']}"):
                        if log_medication_taken(med['id']):
                            st.success(f"Marked {med['name']} as taken")
                            st.rerun()
    else:
        st.markdown("""
        <div class="empty-state">
            <i>💊</i>
            <p>No medications scheduled for today</p>
            <p>Add medications in the Medications page</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Today's Appointments
    st.markdown("### 📅 Today's Appointments")
    
    if today_appointments:
        for appointment in today_appointments:
            appt_time = datetime.fromisoformat(appointment['appointment_datetime'].replace('Z', '+00:00'))
            formatted_time = appt_time.strftime('%I:%M %p') if time_format == '12h' else appt_time.strftime('%H:%M')
            
            st.markdown(f"""
            <div class="card appointment-card">
                <b>Dr. {appointment['doctor_name']}</b><br>
                <small>Time: {formatted_time}</small><br>
                <small>Purpose: {appointment.get('purpose', 'General checkup')}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <i>📅</i>
            <p>No appointments scheduled for today</p>
            <p>Schedule appointments in the Appointments page</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    # Daily Health Tip
    st.markdown("### 💡 Daily Health Tip")
    
    if health_tip:
        st.markdown(f"""
        <div class="card tip-card">
            <div class="section-title">Health Wisdom</div>
            <p>{health_tip['content']}</p>
            <small>Category: {health_tip.get('category', 'General')}</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <i>💡</i>
            <p>No health tips available</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Stats
    st.markdown("### 📊 Quick Stats")
    
    stats_card = f"""
    <div class="card">
        <div class="section-title">Today's Summary</div>
        <p>💊 Medications: {len([m for m in medications if m.get('is_active', True)])} scheduled, {len(medication_log)} taken</p>
        <p>📅 Appointments: {len(today_appointments)} today</p>
        <p>👥 Emergency Contacts: {len([c for c in [primary_contact] if c]) if primary_contact else 0} set up</p>
    </div>
    """
    st.markdown(stats_card, unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    action_col1, action_col2 = st.columns(2)
    
    with action_col1:
        if st.button("Add Medication", use_container_width=True):
            st.switch_page("pages/Medications.py")
        if st.button("Schedule Appointment", use_container_width=True):
            st.switch_page("pages/Appointments.py")
    
    with action_col2:
        if st.button("Add Contact", use_container_width=True):
            st.switch_page("pages/Contacts.py")
        if st.button("View Profile", use_container_width=True):
            st.switch_page("pages/Profile.py")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Health Companion - Senior Citizen Care App</div>", unsafe_allow_html=True)
