import streamlit as st
import datetime
import pytz
from datetime import timedelta
import requests
import json

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Wellness Hub Dashboard",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS STYLING ---
st.markdown("""
<style>
    /* Your existing CSS styles here */
    .main { padding: 2rem; background-color: #f8fafc; }
    .header { text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
    .header h1 { font-size: 2.8rem !important; font-weight: 700; margin-bottom: 0.5rem; }
    .header p { font-size: 1.4rem !important; margin: 0; }
    .card { background-color: white; border-radius: 15px; padding: 1.8rem; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08); margin-bottom: 1.5rem; border: none; height: 100%; transition: transform 0.3s ease; }
    .card:hover { transform: translateY(-5px); box-shadow: 0 6px 12px rgba(0, 0, 0, 0.12); }
    .card-title { font-size: 1.6rem !important; font-weight: 600; color: #2d3748; margin-bottom: 1.2rem; display: flex; align-items: center; gap: 0.5rem; }
    .medication-item { display: flex; align-items: center; padding: 1rem; background-color: #f7fafc; border-radius: 10px; margin-bottom: 0.8rem; border-left: 4px solid #4299e1; }
    .medication-time { font-size: 1.2rem; font-weight: 600; color: #2d3748; min-width: 100px; }
    .medication-details { flex-grow: 1; }
    .medication-name { font-size: 1.3rem; font-weight: 600; color: #2d3748; margin-bottom: 0.2rem; }
    .medication-dosage { font-size: 1.1rem; color: #718096; }
    .appointment-item { padding: 1rem; background-color: #f0fff4; border-radius: 10px; margin-bottom: 0.8rem; border-left: 4px solid #48bb78; }
    .appointment-date { font-size: 1.2rem; font-weight: 600; color: #2d3748; margin-bottom: 0.5rem; }
    .appointment-details { font-size: 1.1rem; color: #4a5568; }
    .health-tip { padding: 1.5rem; background-color: #ebf8ff; border-radius: 10px; border-left: 4px solid #4299e1; }
    .tip-text { font-size: 1.3rem !important; color: #2d3748; line-height: 1.6; font-style: italic; }
    .emergency-button { display: flex; justify-content: center; align-items: center; height: 100%; }
    .emergency-btn { background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%); color: white; border: none; border-radius: 50px; padding: 1.5rem 3rem; font-size: 1.8rem; font-weight: 700; cursor: pointer; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); transition: all 0.3s ease; width: 100%; text-align: center; }
    .emergency-btn:hover { transform: scale(1.05); box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15); background: linear-gradient(135deg, #c53030 0%, #9b2c2c 100%); }
</style>
""", unsafe_allow_html=True)

# --- API CONFIGURATION ---
# Replace with your actual API endpoints
API_BASE_URL = "http://localhost:8000/api"  # Change to your backend URL

def get_user_data():
    """Fetch user-specific data from backend API"""
    try:
        # In a real app, you would get the user ID from session/auth token
        user_id = st.session_state.get('user_id', 1)  # Default to user 1 for demo
        
        # Fetch medications
        meds_response = requests.get(f"{API_BASE_URL}/users/{user_id}/medications/today")
        medications = meds_response.json() if meds_response.status_code == 200 else []
        
        # Fetch appointments
        apps_response = requests.get(f"{API_BASE_URL}/users/{user_id}/appointments/upcoming")
        appointments = apps_response.json() if apps_response.status_code == 200 else []
        
        # Fetch user profile
        profile_response = requests.get(f"{API_BASE_URL}/users/{user_id}/profile")
        profile = profile_response.json() if profile_response.status_code == 200 else {}
        
        return {
            'medications': medications,
            'appointments': appointments,
            'profile': profile
        }
    except requests.exceptions.RequestException:
        # Fallback to sample data if API is unavailable
        return get_sample_data()

def get_sample_data():
    """Sample data for when API is unavailable"""
    today = datetime.date.today()
    return {
        'medications': [
            {"id": 1, "name": "Blood Pressure Meds", "dosage": "10mg", "time": "08:00", "taken": True},
            {"id": 2, "name": "Diabetes Medication", "dosage": "5mg", "time": "12:30", "taken": False},
            {"id": 3, "name": "Cholesterol Pills", "dosage": "20mg", "time": "18:00", "taken": False},
            {"id": 4, "name": "Vitamin D Supplement", "dosage": "1000IU", "time": "20:00", "taken": False}
        ],
        'appointments': [
            {"id": 1, "date": (today + timedelta(days=1)).isoformat(), "time": "10:00", "doctor": "Dr. Smith", "type": "Regular Checkup"},
            {"id": 2, "date": (today + timedelta(days=3)).isoformat(), "time": "14:30", "doctor": "Dr. Johnson", "type": "Cardiology"},
            {"id": 3, "date": (today + timedelta(days=7)).isoformat(), "time": "11:15", "doctor": "Dr. Williams", "type": "Dental Checkup"}
        ],
        'profile': {
            'name': 'John Doe',
            'emergency_contacts': [
                {'name': 'Sarah Wilson', 'relationship': 'Daughter', 'phone': '+1234567890'}
            ]
        }
    }

def mark_medication_taken(medication_id):
    """Mark a medication as taken via API"""
    try:
        response = requests.post(f"{API_BASE_URL}/medications/{medication_id}/taken")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        # For demo purposes, just update local state
        if 'taken_medications' not in st.session_state:
            st.session_state.taken_medications = set()
        st.session_state.taken_medications.add(medication_id)
        return True

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("❤️ Wellness Hub")
    st.markdown("---")
    
    # Navigation
    if st.button("🏠 Dashboard", use_container_width=True):
        st.rerun()  # Refresh the current page
        
    if st.button("💊 Medications", use_container_width=True):
        st.switch_page("pages/Medications.py")
        
    if st.button("🗓️ Appointments", use_container_width=True):
        st.switch_page("pages/Appointments.py")
        
    if st.button("🆘 Emergency", use_container_width=True):
        st.switch_page("pages/Emergency.py")
        
    if st.button("👤 Profile", use_container_width=True):
        st.switch_page("pages/Profile.py")
        
    if st.button("💡 Health Tips", use_container_width=True):
        st.switch_page("pages/HealthTips.py")
    
    st.markdown("---")
    
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        st.success("Logged out successfully!")

# --- LOAD USER DATA ---
user_data = get_user_data()
medications = user_data['medications']
appointments = user_data['appointments']
user_profile = user_data['profile']

# Apply taken status from session (for demo)
if 'taken_medications' in st.session_state:
    for med in medications:
        if med['id'] in st.session_state.taken_medications:
            med['taken'] = True

# --- DASHBOARD LAYOUT ---

# Header Section
user_name = user_profile.get('name', 'Guest')
st.markdown(f"""
<div class="header">
    <h1>Welcome to your Wellness Hub!</h1>
    <p>Hello, {user_name}! Here's your overview for {datetime.datetime.now().strftime('%A, %B %d')}</p>
</div>
""", unsafe_allow_html=True)

# Main Dashboard Grid
col1, col2 = st.columns(2, gap="large")
col3, col4 = st.columns(2, gap="large")

# Card 1: Today's Medication Schedule
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">💊 Today\'s Medications</div>', unsafe_allow_html=True)
    
    if not medications:
        st.info("No medications scheduled for today.")
    else:
        for med in medications:
            # Format time to 12-hour format
            try:
                time_obj = datetime.datetime.strptime(med['time'], '%H:%M')
                time_str = time_obj.strftime('%I:%M %p')
            except:
                time_str = med['time']
            
            status = "✅ Taken" if med.get('taken', False) else "⏰ Upcoming"
            status_color = "#38a169" if med.get('taken', False) else "#d69e2e"
            
            st.markdown(f"""
            <div class="medication-item">
                <div class="medication-time" style="color: {status_color};">{time_str}</div>
                <div class="medication-details">
                    <div class="medication-name">{med['name']}</div>
                    <div class="medication-dosage">{med['dosage']} • {status}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Mark as taken button for upcoming medications
            if not med.get('taken', False):
                if st.button("Mark Taken", key=f"med_{med['id']}"):
                    if mark_medication_taken(med['id']):
                        st.success(f"Marked {med['name']} as taken!")
                        st.rerun()
    
    if st.button("Manage Medications", use_container_width=True, type="secondary"):
        st.switch_page("pages/Medications.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Card 2: Upcoming Appointments
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🗓️ Upcoming Appointments</div>', unsafe_allow_html=True)
    
    if not appointments:
        st.info("No upcoming appointments.")
    else:
        for apt in appointments:
            # Format appointment date
            try:
                apt_date = datetime.datetime.fromisoformat(apt['date'].replace('Z', '+00:00'))
                date_str = apt_date.strftime('%b %d')
                
                # Format time to 12-hour format
                time_obj = datetime.datetime.strptime(apt['time'], '%H:%M')
                time_str = time_obj.strftime('%I:%M %p')
            except:
                date_str = apt['date']
                time_str = apt['time']
            
            st.markdown(f"""
            <div class="appointment-item">
                <div class="appointment-date">{date_str} at {time_str}</div>
                <div class="appointment-details">
                    <strong>{apt['doctor']}</strong><br>
                    {apt['type']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    if st.button("Schedule Appointment", use_container_width=True, type="secondary"):
        st.switch_page("pages/Appointments.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Card 3: Daily Health Tip
with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">💡 Daily Health Tip</div>', unsafe_allow_html=True)
    
    health_tips = [
        "Stay hydrated! Drink at least 8 glasses of water throughout the day.",
        "Take a short walk after meals to aid digestion and maintain mobility.",
        "Remember to do gentle stretching exercises every morning.",
        "Get 7-8 hours of sleep each night for optimal health and recovery.",
        "Eat a balanced diet with plenty of fruits and vegetables.",
        "Practice deep breathing exercises to reduce stress and improve lung capacity.",
        "Stay socially connected with friends and family for mental wellbeing."
    ]
    
    # Select tip based on day of week
    day_of_week = datetime.datetime.now().weekday()
    health_tip = health_tips[day_of_week % len(health_tips)]
    
    st.markdown(f'<div class="health-tip"><p class="tip-text">"{health_tip}"</p></div>', unsafe_allow_html=True)
    
    if st.button("More Health Tips", use_container_width=True, type="secondary"):
        st.switch_page("pages/HealthTips.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Card 4: Emergency Button
with col4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🆘 Emergency Assistance</div>', unsafe_allow_html=True)
    
    emergency_contacts = user_profile.get('emergency_contacts', [])
    
    if emergency_contacts:
        primary_contact = emergency_contacts[0]
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 1rem;">
            <p style="font-size: 1.2rem; font-weight: 600;">Primary Contact:</p>
            <p style="font-size: 1.1rem;">{primary_contact['name']} ({primary_contact['relationship']})</p>
            <p style="font-size: 1.1rem;">📞 {primary_contact['phone']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="emergency-button">
        <button class="emergency-btn" onclick="alert('Emergency alert sent! Help is on the way.')">
            🚨 EMERGENCY CALL
        </button>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-top: 1rem;">
        <p style="font-size: 1.1rem;">Press this button to contact emergency services and your emergency contacts.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Manage Emergency Contacts", use_container_width=True, type="secondary"):
        st.switch_page("pages/Emergency.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- BOTTOM STATUS BAR ---
st.markdown("---")
current_time = datetime.datetime.now().strftime("%I:%M %p")
st.caption(f"Last updated: {current_time} • Wellness Hub v1.0")

# Display API status
try:
    response = requests.get(f"{API_BASE_URL}/health", timeout=2)
    if response.status_code == 200:
        st.sidebar.success("✅ Connected to server")
    else:
        st.sidebar.warning("⚠️ Using demo data")
except:
    st.sidebar.warning("⚠️ Using demo data")
