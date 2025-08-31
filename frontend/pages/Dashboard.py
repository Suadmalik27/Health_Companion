import streamlit as st
from streamlit_cookies_manager import CookieManager
import time
from datetime import datetime, timedelta 
import pytz
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Custom local imports
from auth.service import TOKEN_COOKIE_NAME, get_dashboard_data, mark_medication_as_taken
from components.sidebar import authenticated_sidebar

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="My Wellness Dashboard",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS STYLING ---
def load_css():
    st.markdown("""
    <style>
    .main {
        padding: 0 1rem;
    }
    
    .card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border: 1px solid #e2e8f0;
    }
    
    .emergency-card {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
    }
    
    .tip-card {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .stButton>button {
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    
    .list-item {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
    }
    
    .list-item-icon {
        font-size: 1.5rem;
        margin-right: 0.75rem;
        width: 40px;
        height: 40px;
        background-color: #e0f2fe;
        border-radius: 8px;
        color: #0369a1;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- AUTHENTICATION & INITIALIZATION ---
cookies = CookieManager()

if not cookies.ready():
    st.spinner("Loading session...")
    st.stop()

token = cookies.get(TOKEN_COOKIE_NAME)
if not token:
    st.warning("Please log in to access your dashboard")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()

authenticated_sidebar(cookies)

# --- LOAD STYLES ---
load_css()

# --- DATA MANAGEMENT ---
IST = pytz.timezone('Asia/Kolkata')

def get_mock_data():
    """Return sample data when server is unavailable"""
    return {
        "user_full_name": "Demo User",
        "medications_today": {
            "all_daily": [
                {"id": 1, "name": "Metformin", "dosage": "500mg", "timing": "Morning", "specific_time": "08:00:00"},
                {"id": 2, "name": "Lisinopril", "dosage": "10mg", "timing": "Evening", "specific_time": "20:00:00"}
            ],
            "taken_ids": [2]
        },
        "appointments": {
            "today": [
                {"appointment_datetime": f"{datetime.now().date()}T10:00:00Z", "doctor_name": "Dr. Smith", "location": "Main Clinic"}
            ],
            "upcoming": [
                {"appointment_datetime": f"{(datetime.now() + timedelta(days=3)).date()}T14:00:00Z", "doctor_name": "Dr. Johnson", "location": "Health Center"}
            ]
        },
        "emergency_contacts": [
            {"contact_name": "Emergency Contact", "relationship_type": "Family", "phone_number": "+1234567890"}
        ],
        "health_tip": "Stay hydrated and maintain a regular medication schedule for better health.",
        "summary": {
            "adherence_score": 85,
            "adherence_message": "Good job! Keep it up."
        }
    }

@st.cache_data(show_spinner="Loading your dashboard...")
def load_data(token_param):
    is_success, data = get_dashboard_data(token_param)
    
    if not is_success:
        st.warning("⚠️ Using demo data. Backend server is not available.")
        return get_mock_data()
    
    return data

def handle_med_taken(med_id):
    success, message = mark_medication_as_taken(token, med_id)
    if success:
        st.toast("Medication marked as taken! ✅")
        st.cache_data.clear()
        st.rerun()
    else:
        st.error(f"Error: {message}")

# Load data
dashboard_data = load_data(token)

# --- DATA PROCESSING ---
user_name = dashboard_data.get("user_full_name", "User")
meds_data = dashboard_data.get("medications_today", {})
appt_data = dashboard_data.get("appointments", {})
emergency_contacts = dashboard_data.get("emergency_contacts", [])
health_tip = dashboard_data.get("health_tip", "Remember to stay hydrated!")
summary_data = dashboard_data.get("summary", {})

# Process medications
all_meds = meds_data.get("all_daily", [])
taken_ids = set(meds_data.get("taken_ids", []))
pending_meds = [med for med in all_meds if med['id'] not in taken_ids]
completed_meds = [med for med in all_meds if med['id'] in taken_ids]

# Process appointments
today_appts = appt_data.get("today", [])
upcoming_appts = appt_data.get("upcoming", [])

# Get primary contact
primary_contact = emergency_contacts[0] if emergency_contacts else None

# Calculate metrics
adherence_score = summary_data.get("adherence_score", 100)
adherence_message = summary_data.get("adherence_message", "Keep up the good work!")

# Generate chart data
dates = pd.date_range(start=(datetime.now(IST) - timedelta(days=6)), end=datetime.now(IST), freq='D')
medication_adherence = [85, 90, 100, 75, 95, 100, adherence_score]
mood_data = [3, 4, 5, 4, 3, 4, 5]
steps_data = [6543, 7234, 5678, 8345, 7890, 9123, 8456]

# --- UI COMPONENTS ---
def render_header():
    """Render dashboard header"""
    hour = datetime.now(IST).hour
    if 5 <= hour < 12:
        greeting = "Good Morning"
    elif 12 <= hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"{greeting}, {user_name.split()[0]}!")
        st.caption("Your daily wellness summary")
    with col2:
        now = datetime.now(IST)
        st.markdown(f"""
        <div style='text-align: right;'>
            <h3 style='margin-bottom: 0;'>{now.strftime('%I:%M %p')}</h3>
            <p style='color: #666; margin-top: 0;'>{now.strftime('%A, %b %d')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()

def render_left_panel():
    """Left panel with emergency contacts and metrics"""
    st.subheader("Quick Actions")
    
    # Emergency Card
    with st.container():
        st.markdown('<div class="card emergency-card">', unsafe_allow_html=True)
        st.markdown("### 🚨 Emergency Contact")
        
        if primary_contact:
            st.markdown(f"**{primary_contact['contact_name']}**")
            st.markdown(f"*{primary_contact.get('relationship_type', 'Contact')}*")
            st.markdown(f"📞 {primary_contact['phone_number']}")
            
            if st.button("📞 Call Now", use_container_width=True, type="primary"):
                st.info(f"Calling {primary_contact['contact_name']}...")
        else:
            st.info("No emergency contacts set up")
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Progress Card
    with st.container():
        st.markdown('<div class="card metric-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Today's Progress")
        st.markdown(f'<div class="metric-value">{adherence_score}%</div>', unsafe_allow_html=True)
        st.caption(adherence_message)
        st.progress(adherence_score / 100)
        st.markdown('</div>', unsafe_allow_html=True)

def render_center_panel():
    """Center panel with medications and appointments"""
    st.subheader("Today's Schedule")
    
    # Medications
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 💊 Medications")
        
        if not pending_meds:
            st.success("All medications taken today! ✅")
        else:
            for med in pending_meds:
                time_str = med.get('specific_time', 'Anytime')
                if ':' in time_str:
                    try:
                        time_obj = datetime.strptime(time_str, '%H:%M:%S')
                        time_str = time_obj.strftime('%I:%M %p')
                    except:
                        pass
                
                col1, col2, col3 = st.columns([1, 3, 2])
                with col1:
                    st.markdown('<div class="list-item-icon">💊</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f"**{med['name']}** ({med['dosage']})")
                    st.caption(f"Due: {time_str}")
                with col3:
                    st.button("Mark Taken", key=f"med_{med['id']}", 
                             on_click=handle_med_taken, args=(med['id'],))
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Appointments
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🗓️ Appointments")
        
        if not today_appts:
            st.info("No appointments today")
        else:
            for apt in today_appts:
                try:
                    apt_time = datetime.fromisoformat(apt['appointment_datetime'].replace('Z', '+00:00'))
                    apt_time = apt_time.astimezone(IST).strftime('%I:%M %p')
                except:
                    apt_time = "Unknown time"
                
                st.markdown(f"**{apt_time}** - Dr. {apt.get('doctor_name', 'Unknown')}")
                st.caption(apt.get('location', 'No location specified'))
                st.divider()
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_right_panel():
    """Right panel with health tips and info"""
    st.subheader("Health & Info")
    
    # Health Tip
    with st.container():
        st.markdown('<div class="card tip-card">', unsafe_allow_html=True)
        st.markdown("### 💡 Health Tip")
        st.info(health_tip)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Upcoming Appointments
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📅 Upcoming")
        
        if not upcoming_appts:
            st.info("No upcoming appointments")
        else:
            for apt in upcoming_appts[:3]:
                try:
                    apt_date = datetime.fromisoformat(apt['appointment_datetime'].replace('Z', '+00:00'))
                    apt_date = apt_date.astimezone(IST).strftime('%b %d')
                    apt_time = apt_date.strftime('%I:%M %p')
                except:
                    apt_date = "Unknown date"
                    apt_time = "Unknown time"
                
                st.markdown(f"**{apt_date}** at {apt_time}")
                st.caption(f"Dr. {apt.get('doctor_name', 'Unknown')}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN LAYOUT ---
render_header()

# Three-column layout
col1, col2, col3 = st.columns([1, 2, 1], gap="large")

with col1:
    render_left_panel()

with col2:
    render_center_panel()

with col3:
    render_right_panel()

# Server status indicator
st.sidebar.divider()
if "Demo User" in user_name:
    st.sidebar.warning("🔴 Using demo data")
    st.sidebar.info("Start backend server for real data")
else:
    st.sidebar.success("🟢 Connected to server")
