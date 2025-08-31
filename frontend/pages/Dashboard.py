import streamlit as st
import datetime
import pytz
from datetime import timedelta
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Wellness Hub Dashboard",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS STYLING FOR SENIOR CITIZENS ---
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 2rem;
        background-color: #f8fafc;
    }
    
    /* Header styling */
    .header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .header h1 {
        font-size: 2.8rem !important;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .header p {
        font-size: 1.4rem !important;
        margin: 0;
    }
    
    /* Card styling */
    .card {
        background-color: white;
        border-radius: 15px;
        padding: 1.8rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        border: none;
        height: 100%;
        transition: transform 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.12);
    }
    
    .card-title {
        font-size: 1.6rem !important;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Medication card specific */
    .medication-item {
        display: flex;
        align-items: center;
        padding: 1rem;
        background-color: #f7fafc;
        border-radius: 10px;
        margin-bottom: 0.8rem;
        border-left: 4px solid #4299e1;
    }
    
    .medication-time {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2d3748;
        min-width: 100px;
    }
    
    .medication-details {
        flex-grow: 1;
    }
    
    .medication-name {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.2rem;
    }
    
    .medication-dosage {
        font-size: 1.1rem;
        color: #718096;
    }
    
    /* Appointment card specific */
    .appointment-item {
        padding: 1rem;
        background-color: #f0fff4;
        border-radius: 10px;
        margin-bottom: 0.8rem;
        border-left: 4px solid #48bb78;
    }
    
    .appointment-date {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    
    .appointment-details {
        font-size: 1.1rem;
        color: #4a5568;
    }
    
    /* Health tip card specific */
    .health-tip {
        padding: 1.5rem;
        background-color: #ebf8ff;
        border-radius: 10px;
        border-left: 4px solid #4299e1;
    }
    
    .tip-text {
        font-size: 1.3rem !important;
        color: #2d3748;
        line-height: 1.6;
        font-style: italic;
    }
    
    /* Emergency button styling */
    .emergency-button {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
    }
    
    .emergency-btn {
        background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 1.5rem 3rem;
        font-size: 1.8rem;
        font-weight: 700;
        cursor: pointer;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        width: 100%;
        text-align: center;
    }
    
    .emergency-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        background: linear-gradient(135deg, #c53030 0%, #9b2c2c 100%);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f7fafc;
    }
    
    /* Button styling throughout app */
    .stButton > button {
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        font-size: 1.2rem;
    }
    
    /* Make all text larger for better readability */
    .stMarkdown {
        font-size: 1.1rem;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .header h1 {
            font-size: 2.2rem !important;
        }
        
        .card-title {
            font-size: 1.4rem !important;
        }
        
        .emergency-btn {
            padding: 1.2rem 2rem;
            font-size: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("❤️ Wellness Hub")
    st.markdown("---")
    
    # Navigation options - FIXED: Use proper page paths
    # For main app file, use the actual file name (usually app.py or main.py)
    # For pages, use the correct path relative to main app
    
    # If your main app file is Home.py:
    st.page_link("Home.py", label="🏠 Dashboard", icon="📊")
    
    # If your pages are in a pages directory:
    st.page_link("pages/Medications.py", label="💊 Medications", icon="💊")
    st.page_link("pages/Appointments.py", label="🗓️ Appointments", icon="🗓️")
    st.page_link("pages/Emergency_Contacts.py", label="🆘 Emergency", icon="🆘")
    st.page_link("pages/Profile.py", label="👤 Profile", icon="👤")
    st.page_link("pages/HealthTips.py", label="💡 Health Tips", icon="💡")
    
    st.markdown("---")
    
    # Logout button
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        st.success("Logged out successfully!")
        # Here you would typically clear session state or cookies

# --- SAMPLE DATA ---
def get_current_time():
    """Get current time in a readable format"""
    return datetime.datetime.now().strftime("%I:%M %p")

def get_todays_medications():
    """Sample data for today's medications"""
    return [
        {"name": "Blood Pressure Meds", "dosage": "10mg", "time": "08:00 AM", "taken": True},
        {"name": "Diabetes Medication", "dosage": "5mg", "time": "12:30 PM", "taken": False},
        {"name": "Cholesterol Pills", "dosage": "20mg", "time": "06:00 PM", "taken": False},
        {"name": "Vitamin D Supplement", "dosage": "1000IU", "time": "08:00 PM", "taken": False}
    ]

def get_upcoming_appointments():
    """Sample data for upcoming appointments"""
    today = datetime.date.today()
    return [
        {"date": (today + timedelta(days=1)).strftime("%b %d"), "time": "10:00 AM", "doctor": "Dr. Smith", "type": "Regular Checkup"},
        {"date": (today + timedelta(days=3)).strftime("%b %d"), "time": "02:30 PM", "doctor": "Dr. Johnson", "type": "Cardiology"},
        {"date": (today + timedelta(days=7)).strftime("%b %d"), "time": "11:15 AM", "doctor": "Dr. Williams", "type": "Dental Checkup"}
    ]

def get_daily_health_tip():
    """Get a random health tip from a list"""
    health_tips = [
        "Stay hydrated! Drink at least 8 glasses of water throughout the day.",
        "Take a short walk after meals to aid digestion and maintain mobility.",
        "Remember to do gentle stretching exercises every morning.",
        "Get 7-8 hours of sleep each night for optimal health and recovery.",
        "Eat a balanced diet with plenty of fruits and vegetables.",
        "Practice deep breathing exercises to reduce stress and improve lung capacity.",
        "Stay socially connected with friends and family for mental wellbeing."
    ]
    
    # Select a tip based on day of week to vary it daily
    day_of_week = datetime.datetime.now().weekday()
    return health_tips[day_of_week % len(health_tips)]

# --- DASHBOARD LAYOUT ---

# Header Section
st.markdown(f"""
<div class="header">
    <h1>Welcome to your Wellness Hub!</h1>
    <p>Hello, John! Here's your overview for {datetime.datetime.now().strftime('%A, %B %d')}</p>
</div>
""", unsafe_allow_html=True)

# Main Dashboard Grid - 2x2 layout
col1, col2 = st.columns(2, gap="large")
col3, col4 = st.columns(2, gap="large")

# Card 1: Today's Medication Schedule
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">💊 Today\'s Medications</div>', unsafe_allow_html=True)
    
    medications = get_todays_medications()
    
    for med in medications:
        # Determine if medication is upcoming or past
        status = "✅ Taken" if med["taken"] else "⏰ Upcoming"
        status_color = "#38a169" if med["taken"] else "#d69e2e"
        
        st.markdown(f"""
        <div class="medication-item">
            <div class="medication-time" style="color: {status_color};">{med['time']}</div>
            <div class="medication-details">
                <div class="medication-name">{med['name']}</div>
                <div class="medication-dosage">{med['dosage']} • {status}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add button to manage medications
    if st.button("Manage Medications", use_container_width=True, type="secondary"):
        st.switch_page("pages/Medications.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Card 2: Upcoming Appointments
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🗓️ Upcoming Appointments</div>', unsafe_allow_html=True)
    
    appointments = get_upcoming_appointments()
    
    for apt in appointments:
        st.markdown(f"""
        <div class="appointment-item">
            <div class="appointment-date">{apt['date']} at {apt['time']}</div>
            <div class="appointment-details">
                <strong>{apt['doctor']}</strong><br>
                {apt['type']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add button to manage appointments
    if st.button("Schedule Appointment", use_container_width=True, type="secondary"):
        st.switch_page("pages/Appointments.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Card 3: Daily Health Tip
with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">💡 Daily Health Tip</div>', unsafe_allow_html=True)
    
    health_tip = get_daily_health_tip()
    st.markdown(f'<div class="health-tip"><p class="tip-text">"{health_tip}"</p></div>', unsafe_allow_html=True)
    
    # Add button to view more health tips
    if st.button("More Health Tips", use_container_width=True, type="secondary"):
        st.switch_page("pages/HealthTips.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Card 4: Emergency Button
with col4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🆘 Emergency Assistance</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="emergency-button">
        <button class="emergency-btn" onclick="alert('Emergency alert sent! Help is on the way.')">
            🚨 EMERGENCY CALL
        </button>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-top: 1rem;">
        <p style="font-size: 1.1rem;">In case of emergency, press this button to immediately contact your emergency contacts and emergency services.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add button to manage emergency contacts
    if st.button("Manage Emergency Contacts", use_container_width=True, type="secondary"):
        st.switch_page("pages/Emergency.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- BOTTOM STATUS BAR ---
st.markdown("---")
current_time = datetime.datetime.now().strftime("%I:%M %p")
st.caption(f"Last updated: {current_time} • Wellness Hub v1.0")

