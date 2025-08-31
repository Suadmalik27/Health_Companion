# frontend/pages/Dashboard.py (DYNAMIC VERSION)

# --- 1. LIBRARY IMPORTS ---
import streamlit as st
import time
from datetime import datetime, timedelta
import pytz
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Mock data function - Replace with actual API call
def fetch_dashboard_data():
    """Fetches or generates mock dashboard data."""
    # In a real app, this would be an API call to your backend
    # e.g., requests.get("http://your-backend/api/dashboard").json()

    # Mock data for demonstration
    return {
        "user_full_name": "Rahul Sharma",
        "summary": {
            "adherence_score": 95,
            "adherence_message": "Keep up the great work!"
        },
        "medications_today": {
            "all_daily": [
                {"id": 1, "name": "Metformin", "dosage": "500mg", "frequency": "Twice daily", "frequency_type": "Daily"},
                {"id": 2, "name": "Atorvastatin", "dosage": "20mg", "frequency": "Once daily", "frequency_type": "Daily"},
                {"id": 3, "name": "Aspirin", "dosage": "81mg", "frequency": "Once daily", "frequency_type": "Daily"}
            ],
            "taken_ids": [1, 3]
        },
        "appointments": {
            "today": [
                {"id": 1, "title": "Endocrinologist Visit", "doctor_name": "Dr. Patel", "appointment_datetime": datetime.now().replace(hour=10, minute=0, second=0, microsecond=0).isoformat(), "location": "City Hospital"},
                {"id": 2, "title": "Blood Test", "doctor_name": "Lab Technician", "appointment_datetime": datetime.now().replace(hour=15, minute=30, second=0, microsecond=0).isoformat(), "location": "Diagnostic Center"}
            ],
            "upcoming": [
                {"id": 3, "title": "Cardiologist Follow-up", "doctor_name": "Dr. Kumar", "appointment_datetime": (datetime.now() + timedelta(days=3)).replace(hour=11, minute=0, second=0, microsecond=0).isoformat(), "location": "Specialty Clinic"}
            ]
        },
        "emergency_contacts": [
            {"id": 1, "name": "Priya Sharma", "relationship": "Wife", "phone": "+91 98765 43210"},
            {"id": 2, "name": "Dr. Patel", "relationship": "Primary Care", "phone": "+91 97654 32109"}
        ],
        "health_tip": "Regular exercise helps maintain stable blood sugar levels.",
        "health_vitals": {
            "blood_pressure": "120/80",
            "blood_sugar": "110 mg/dL",
            "heart_rate": "72 bpm"
        }
    }

# --- 2. PAGE CONFIGURATION & INITIALIZATION ---
st.set_page_config(
    page_title="My Wellness Dashboard",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 3. CUSTOM CSS STYLING ---
def load_css():
    st.markdown("""
    <style>
    /* Global Styles */
    .main {
        padding: 0 1rem;
    }
    
    /* Card Styling */
    .card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
    }
    
    .emergency-card {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    
    .tip-card {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }

    /* Adjust Streamlit components */
    .stProgress > div > div > div {
        background-color: #3b82f6;
    }
    
    /* Custom metric styling */
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 1rem;
    }
    
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA FETCHING & STATE MANAGEMENT ---
IST = pytz.timezone('Asia/Kolkata')
if 'dashboard_data' not in st.session_state:
    st.session_state.dashboard_data = fetch_dashboard_data()

# --- 5. UI RENDERING FUNCTIONS ---
def get_time_based_greeting():
    """Determines a greeting based on the current time in India."""
    now = datetime.now(IST)
    hour = now.hour
    if 5 <= hour < 12: return "Good Morning"
    elif 12 <= hour < 17: return "Good Afternoon"
    else: return "Good Evening"

def render_header():
    header_cols = st.columns([1, 4, 1])
    with header_cols[0]:
        st.image("https://via.placeholder.com/100x50?text=Logo", use_column_width=True) # Replace with your logo
    with header_cols[1]:
        st.title(f"{get_time_based_greeting()}, {st.session_state.dashboard_data['user_full_name']}!")
        st.markdown("Here is your wellness summary.")
    with header_cols[2]:
        clock_placeholder = st.empty()
    st.divider()
    return clock_placeholder

def render_left_panel():
    st.subheader("Quick Insights")
    summary_data = st.session_state.dashboard_data['summary']
    
    st.markdown('<div class="card metric-card">', unsafe_allow_html=True)
    st.markdown('<h3>📈 Adherence Score</h3>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{summary_data["adherence_score"]}%</div>', unsafe_allow_html=True)
    st.caption(summary_data["adherence_message"])
    st.progress(summary_data["adherence_score"] / 100)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.subheader("Emergency Contacts")
    for contact in st.session_state.dashboard_data['emergency_contacts']:
        st.markdown(f"""
        <div class='card emergency-card'>
            <h4>{contact['name']}</h4>
            <p><strong>Relationship:</strong> {contact['relationship']}</p>
            <p><strong>Phone:</strong> {contact['phone']}</p>
        </div>
        """, unsafe_allow_html=True)

def render_center_panel():
    st.subheader("Today's To-Do List")
    
    # Medications Tab
    st.subheader("Today's Medications")
    meds_data = st.session_state.dashboard_data['medications_today']
    for med in meds_data['all_daily']:
        is_taken = med['id'] in meds_data['taken_ids']
        status_text = "✓ Taken" if is_taken else "✗ Not Taken"
        status_class = "medication-taken" if is_taken else "medication-missed"
        
        st.markdown(f"""
        <div class='card {status_class}'>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4>{med['name']} ({med['dosage']})</h4>
                    <small>Frequency: {med['frequency']}</small>
                </div>
                <div>
                    <b>{status_text}</b>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Appointments Section
    st.subheader("Appointments")
    tabs = st.tabs(["Today's Appointments", "Upcoming Appointments"])
    
    with tabs[0]:
        if st.session_state.dashboard_data['appointments']['today']:
            for appt in st.session_state.dashboard_data['appointments']['today']:
                appt_time = datetime.fromisoformat(appt['appointment_datetime']).strftime("%I:%M %p")
                st.markdown(f"""
                <div class='card appointment-card'>
                    <h4>{appt['title']} with Dr. {appt['doctor_name']}</h4>
                    <p><strong>Time:</strong> {appt_time}</p>
                    <p><strong>Location:</strong> {appt['location']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No appointments scheduled for today.")
            
    with tabs[1]:
        if st.session_state.dashboard_data['appointments']['upcoming']:
            for appt in st.session_state.dashboard_data['appointments']['upcoming']:
                appt_dt = datetime.fromisoformat(appt['appointment_datetime'])
                st.markdown(f"""
                <div class='card appointment-card'>
                    <h4>{appt['title']} with Dr. {appt['doctor_name']}</h4>
                    <p><strong>Date:</strong> {appt_dt.strftime('%B %d, %Y')}</p>
                    <p><strong>Time:</strong> {appt_dt.strftime('%I:%M %p')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No upcoming appointments.")

def render_right_panel():
    st.subheader("Health & Trends")
    
    # Health Tip
    st.markdown('<div class="card tip-card">', unsafe_allow_html=True)
    st.markdown(f"<h4>💡 Daily Health Tip</h4><p>{st.session_state.dashboard_data['health_tip']}</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Health Vitals
    st.subheader("Health Vitals")
    vitals = st.session_state.dashboard_data.get('health_vitals', {})
    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        st.metric("Blood Pressure", vitals.get('blood_pressure', 'N/A'))
    with col_v2:
        st.metric("Blood Sugar", vitals.get('blood_sugar', 'N/A'))
    with col_v3:
        st.metric("Heart Rate", vitals.get('heart_rate', 'N/A'))

    # Adherence Chart
    st.subheader("Medication Adherence Trend")
    dates = pd.date_range(end=datetime.today(), periods=30)
    adherence = [92, 94, 96, 95, 93, 95, 96, 97, 95, 94, 96, 95, 97, 96, 95, 94, 96, 97, 95, 96, 97, 96, 95, 94, 96, 97, 98, 96, 95, 95]
    adherence_data = pd.DataFrame({'Date': dates, 'Adherence': adherence})
    fig = px.line(adherence_data, x='Date', y='Adherence', title='30-Day Adherence Trend', labels={'Adherence': 'Adherence (%)'})
    fig.update_traces(line=dict(color='green', width=3))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

# --- 6. MAIN LAYOUT & APP EXECUTION ---
load_css()
clock_placeholder = render_header()
main_cols = st.columns([1, 2, 1], gap="large")

with main_cols[0]:
    render_left_panel()

with main_cols[1]:
    render_center_panel()

with main_cols[2]:
    render_right_panel()

st.button("Refresh Data")
if st.button("Refresh Data"):
    st.session_state.dashboard_data = fetch_dashboard_data()
    st.rerun()

# --- 7. LIVE CLOCK BACKGROUND PROCESS ---
while True:
    now_ist = datetime.now(IST)
    time_str = now_ist.strftime("%I:%M:%S %p")
    date_str = now_ist.strftime("%A, %B %d, %Y")
    with clock_placeholder.container():
        st.markdown(f"<div style='text-align: right;'><h2 style='font-weight: 700; margin-bottom: -15px; color: #212121;'>{time_str}</h2><p style='color: #616161;'>{date_str}</p></div>", unsafe_allow_html=True)
    time.sleep(1)
