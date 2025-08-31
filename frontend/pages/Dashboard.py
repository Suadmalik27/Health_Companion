import streamlit as st
from streamlit_cookies_manager import CookieManager
import time
from datetime import datetime, timedelta 
import pytz
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Custom local imports
from auth.service import TOKEN_COOKIE_NAME, get_dashboard_data, mark_medication_as_taken
from components.sidebar import authenticated_sidebar

# --- PAGE CONFIGURATION & INITIALIZATION ---
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
    /* Global Styles */
    .main {
        padding: 0 1rem;
    }
    
    /* Card Styling */
    .card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border: 1px solid #e0e0e0;
    }
    
    .emergency-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        color: white;
    }
    
    .tip-card {
        background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
    }
    
    /* Button Styling */
    .stButton > button {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-size: 1.1rem;
    }
    
    .sos-button {
        background-color: white;
        color: #ff4b4b;
        padding: 1rem 2rem;
        border-radius: 8px;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        margin-top: 1rem;
        cursor: pointer;
    }
    
    /* Text sizing for senior citizens */
    .big-text {
        font-size: 1.4rem !important;
    }
    
    .medium-text {
        font-size: 1.2rem !important;
    }
    
    /* List items */
    .list-item {
        display: flex;
        align-items: center;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
    }
    
    .list-item-icon {
        font-size: 1.5rem;
        margin-right: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- AUTHENTICATION & COOKIE MANAGEMENT ---
# Initialize cookies first
cookies = CookieManager()

# Check if cookies are ready
if not cookies.ready():
    st.spinner("Loading your session...")
    st.stop()

# Check authentication
token = cookies.get(TOKEN_COOKIE_NAME)
if not token:
    st.warning("You are not logged in. Please log in to continue.")
    if st.button("Go to Login Page"):
        st.switch_page("Home.py")
    st.stop()

# Load sidebar after authentication check
authenticated_sidebar(cookies)

# --- LOAD STYLES ---
load_css()

# --- DATA FETCHING & STATE MANAGEMENT ---
IST = pytz.timezone('Asia/Kolkata')

@st.cache_data(show_spinner="Loading your dashboard...")
def load_data(token_param):
    is_success, data = get_dashboard_data(token_param)
    if not is_success:
        st.error(f"Failed to fetch data: {data}. Please try again later.")
        return None
    return data

def handle_med_taken_action(med_id):
    is_marked, msg = mark_medication_as_taken(token, med_id)
    if is_marked:
        st.toast("Great job! Medication marked as taken.", icon="✅")
        # Clear cache to refresh data
        st.cache_data.clear()
        st.rerun()
    else:
        st.error(f"Could not mark medication: {msg}")

# Load dashboard data
dashboard_data = load_data(token)
if dashboard_data is None:
    st.stop()

# --- DATA PROCESSING ---
user_name = dashboard_data.get("user_full_name", "User")
medications_today = dashboard_data.get("medications_today", [])
appointments = dashboard_data.get("appointments", {})
emergency_contacts = dashboard_data.get("emergency_contacts", [])
health_tip = dashboard_data.get("health_tip", "Remember to stay hydrated and have a great day!")

# Process medications
pending_meds = [med for med in medications_today if not med.get('taken', False)]
completed_meds = [med for med in medications_today if med.get('taken', False)]

# Process appointments
todays_appointments = appointments.get("today", [])
upcoming_appointments = appointments.get("upcoming", [])

# Get primary emergency contact
primary_contact = emergency_contacts[0] if emergency_contacts else None

# Calculate adherence score
total_meds = len(medications_today)
taken_meds = len(completed_meds)
adherence_score = (taken_meds / total_meds * 100) if total_meds > 0 else 100

# Generate sample data for charts
dates = pd.date_range(start=(datetime.now() - timedelta(days=6)), end=datetime.now(), freq='D')
medication_adherence = [85, 90, 100, 75, 95, 100, adherence_score]
mood_data = [3, 4, 5, 4, 3, 4, 5]  # Sample mood data (1-5 scale)
steps_data = [6543, 7234, 5678, 8345, 7890, 9123, 8456]  # Sample step count

# --- UI COMPONENTS ---
def render_header():
    """Render the dashboard header with greeting"""
    hour = datetime.now(IST).hour
    if 5 <= hour < 12:
        greeting = "Good Morning"
    elif 12 <= hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    st.title(f"{greeting}, {user_name.split()[0]}!")
    st.markdown("Here's your wellness summary for today")
    st.divider()

def render_left_panel():
    """Render the left panel with emergency contacts and metrics"""
    st.subheader("Quick Actions")
    
    # EMERGENCY CARD
    st.markdown('<div class="card emergency-card">', unsafe_allow_html=True)
    st.markdown('<h3>🚨 EMERGENCY CONTACT</h3>', unsafe_allow_html=True)
    
    if primary_contact:
        st.markdown(f"<p class='big-text'><b>{primary_contact['contact_name']}</b></p>", unsafe_allow_html=True)
        st.markdown(f"<p class='medium-text'>{primary_contact.get('relationship_type', 'Contact')}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='medium-text'>📞 {primary_contact['phone_number']}</p>", unsafe_allow_html=True)
        
        # Call button
        if st.button("📞 CALL NOW", use_container_width=True, type="primary"):
            st.info(f"Calling {primary_contact['contact_name']}...")
    else:
        st.info("No emergency contacts set up yet.")
        if st.button("➕ Add Emergency Contact", use_container_width=True):
            st.switch_page("pages/Emergency_Contacts.py")
            
    st.markdown('</div>', unsafe_allow_html=True)
    
    # PROGRESS CARD
    st.markdown('<div class="card metric-card">', unsafe_allow_html=True)
    st.markdown('<h3>📊 Today\'s Progress</h3>', unsafe_allow_html=True)
    
    st.markdown(f'<p class="big-text">{taken_meds}/{total_meds} Medications Taken</p>', unsafe_allow_html=True)
    st.progress(adherence_score / 100)
    
    if adherence_score == 100 and total_meds > 0:
        st.success("🎉 All medications taken today!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # HEALTH METRICS CARD
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h4>📊 Health Metrics</h4>', unsafe_allow_html=True)
    
    # Create a simple chart for steps
    fig_steps = go.Figure(go.Scatter(
        x=dates, 
        y=steps_data,
        mode='lines+markers',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=6)
    ))
    
    fig_steps.update_layout(
        height=200,
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False, title="Steps")
    )
    
    st.plotly_chart(fig_steps, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_center_panel():
    """Render the center panel with medications and appointments"""
    st.subheader("Today's Schedule")
    
    # MEDICATIONS CARD
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>💊 Today\'s Medications</h3>', unsafe_allow_html=True)
    
    if not medications_today:
        st.info("No medications scheduled for today.")
    else:
        for med in medications_today:
            status = "✅ Taken" if med.get('taken') else "⏰ Pending"
            st.markdown(f"""
            <div class="list-item">
                <div class="list-item-icon">💊</div>
                <div>
                    <b>{med['name']}</b> ({med['dosage']}) - {med.get('timing', 'Anytime')}<br>
                    <small>{status}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if not med.get('taken'):
                if st.button("Mark as Taken", key=f"med_{med['id']}"):
                    handle_med_taken_action(med['id'])
    
    if st.button("➕ Add Medication", use_container_width=True):
        st.switch_page("pages/Medications.py")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # APPOINTMENTS CARD
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>🗓️ Today\'s Appointments</h3>', unsafe_allow_html=True)
    
    if not todays_appointments:
        st.info("No appointments scheduled for today.")
    else:
        for appt in todays_appointments:
            appt_time = datetime.fromisoformat(appt['appointment_datetime'].replace('Z', '+00:00')).astimezone(IST).strftime('%I:%M %p')
            st.markdown(f"""
            <div class="list-item">
                <div class="list-item-icon">🗓️</div>
                <div>
                    <b>{appt_time} with Dr. {appt.get('doctor_name', 'Unknown')}</b><br>
                    <small>{appt.get('location', 'No location specified')}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    if st.button("➕ Schedule Appointment", use_container_width=True):
        st.switch_page("pages/Appointments.py")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # HEALTH TRENDS CARD
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h4>📈 Weekly Trends</h4>', unsafe_allow_html=True)
    
    # Create a chart with two y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add adherence trace
    fig.add_trace(
        go.Scatter(x=dates, y=medication_adherence, name="Adherence %", 
                  line=dict(color='#3b82f6', width=3)),
        secondary_y=False,
    )
    
    # Add mood trace
    fig.add_trace(
        go.Scatter(x=dates, y=mood_data, name="Mood", 
                  line=dict(color='#10b981', width=3, dash='dot')),
        secondary_y=True,
    )
    
    # Set axis titles
    fig.update_yaxes(title_text="Adherence %", secondary_y=False)
    fig.update_yaxes(title_text="Mood (1-5)", secondary_y=True)
    
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_right_panel():
    """Render the right panel with health tips and additional info"""
    st.subheader("Health & Wellness")
    
    # HEALTH TIP CARD
    st.markdown('<div class="card tip-card">', unsafe_allow_html=True)
    st.markdown('<h3>💡 Daily Health Tip</h3>', unsafe_allow_html=True)
    st.info(health_tip)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # UPCOMING APPOINTMENTS CARD
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>📅 Upcoming Appointments</h3>', unsafe_allow_html=True)
    
    if not upcoming_appointments:
        st.info("No upcoming appointments.")
    else:
        for appt in upcoming_appointments[:3]:  # Show only next 3 appointments
            appt_dt = datetime.fromisoformat(appt['appointment_datetime'].replace('Z', '+00:00')).astimezone(IST)
            appt_date = appt_dt.strftime('%b %d')
            appt_time = appt_dt.strftime('%I:%M %p')
            st.markdown(f"""
            <div class="list-item">
                <div class="list-item-icon">📅</div>
                <div>
                    <b>{appt_date} at {appt_time}</b><br>
                    <small>Dr. {appt.get('doctor_name', 'Unknown')}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # QUICK ACTIONS CARD
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>⚡ Quick Actions</h3>', unsafe_allow_html=True)
    
    if st.button("👤 View Profile", use_container_width=True):
        st.switch_page("pages/Profile.py")
        
    if st.button("💡 More Health Tips", use_container_width=True):
        st.switch_page("pages/Health_Tips.py")
        
    if st.button("📞 Manage Contacts", use_container_width=True):
        st.switch_page("pages/Emergency_Contacts.py")
    st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN LAYOUT ---
render_header()

# Create three-column layout
left_col, center_col, right_col = st.columns([1, 2, 1], gap="large")

with left_col:
    render_left_panel()

with center_col:
    render_center_panel()

with right_col:
    render_right_panel()

# --- LIVE CLOCK ---
# Display current time (simplified version without infinite loop)
now_ist = datetime.now(IST)
time_str = now_ist.strftime("%I:%M:%S %p")
date_str = now_ist.strftime("%A, %B %d, %Y")

st.sidebar.markdown(f"**Current Time:** {time_str}")
st.sidebar.markdown(f"**Date:** {date_str}")
    # time.sleep(1)
