# frontend/pages/Dashboard.py (VERSION 10.0 - MODERN UI)

# --- 1. LIBRARY IMPORTS ---
import streamlit as st
from streamlit_cookies_manager import CookieManager
import time
from datetime import datetime, timezone, timedelta 
import pytz
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Custom local imports
from auth.service import TOKEN_COOKIE_NAME, get_dashboard_data, mark_medication_as_taken
from components.sidebar import authenticated_sidebar

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
    
    /* Sidebar Styling */
    .css-1d391kg, .css-1vq4p4l {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
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
    
    .card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        transform: translateY(-2px);
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
    
    /* Button Styling */
    .stButton>button {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        padding: 0.5rem 1rem;
        background-color: white;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #f1f5f9;
        border-color: #cbd5e1;
        transform: translateY(-1px);
    }
    
    .sos-button {
        background-color: white;
        color: #dc2626;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 700;
        text-align: center;
        margin-top: 1rem;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .sos-button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .sos-button a {
        color: #dc2626;
        text-decoration: none;
    }
    
    /* List Items */
    .list-item {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
    }
    
    .list-item:hover {
        background-color: #f1f5f9;
    }
    
    .list-item-icon {
        font-size: 1.5rem;
        margin-right: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        background-color: #e0f2fe;
        border-radius: 8px;
        color: #0369a1;
    }
    
    .list-item-info {
        flex: 1;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background-color: #f8fafc;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: 1px solid #e2e8f0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
    }
    
    /* Progress Bar Styling */
    .stProgress > div > div > div {
        background-color: #3b82f6;
    }
    
    /* Divider Styling */
    .stDivider {
        margin: 1.5rem 0;
    }
    
    /* Animation for cards */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .card {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Custom metric styling */
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    /* Custom checkbox styling */
    .stCheckbox > label {
        font-weight: 500;
    }
    
    /* Adjust spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* Custom tab content padding */
    .stTab {
        padding-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. AUTHENTICATION & COOKIE MANAGEMENT ---
cookies = CookieManager()
if not cookies.ready():
    st.spinner("Initializing Session...")
    st.stop()
token = cookies.get(TOKEN_COOKIE_NAME)
if not token:
    st.warning("🔒 You are not logged in. Please log in to your Wellness Hub.")
    st.link_button("Go to Login Page", "Home.py")
    st.stop()
authenticated_sidebar(cookies)

# --- 5. LOAD STYLES ---
load_css()

# --- 6. DATA FETCHING & STATE MANAGEMENT ---
IST = pytz.timezone('Asia/Kolkata')

@st.cache_data(show_spinner="Updating your Wellness Hub...")
def load_data(token_param):
    is_success, data = get_dashboard_data(token_param)
    if not is_success:
        st.error(f"Failed to fetch data: {data}. Please try again later.")
        return None
    return data

def handle_med_taken_action(med_id):
    is_marked, msg = mark_medication_as_taken(token, med_id)
    if is_marked:
        st.toast("Great job! Your log has been updated.", icon="🎉")
        st.cache_data.clear()
        st.rerun()
    else:
        st.error(f"Could not log medication: {msg}")
        st.rerun()

dashboard_data = load_data(token)
if dashboard_data is None:
    st.stop()

# --- 7. DATA EXTRACTION & PRE-PROCESSING ---
summary_data = dashboard_data.get("summary", {})
meds_data = dashboard_data.get("medications_today", {})
appt_data = dashboard_data.get("appointments", {})
emergency_contacts = dashboard_data.get("emergency_contacts", [])
health_tip = dashboard_data.get("health_tip", "Remember to stay hydrated and have a great day!")
user_name = dashboard_data.get("user_full_name", "User")
primary_contact = emergency_contacts[0] if emergency_contacts else None
all_daily_meds = sorted(meds_data.get("all_daily", []), key=lambda x: x.get('specific_time') or "23:59")
taken_today_ids = set(meds_data.get("taken_ids", []))
pending_meds = [med for med in all_daily_meds if med['id'] not in taken_today_ids]
completed_meds = [med for med in all_daily_meds if med['id'] in taken_today_ids]
todays_appointments = appt_data.get("today", [])
upcoming_appointments = appt_data.get("upcoming", [])
adherence_score = summary_data.get("adherence_score", 100)
adherence_message = summary_data.get("adherence_message", "Keep up the good work!")

# Generate sample data for charts
dates = pd.date_range(start=(datetime.now(IST) - timedelta(days=6)), end=datetime.now(IST), freq='D')
medication_adherence = [85, 90, 100, 75, 95, 100, adherence_score]
mood_data = [3, 4, 5, 4, 3, 4, 5]  # Sample mood data (1-5 scale)
steps_data = [6543, 7234, 5678, 8345, 7890, 9123, 8456]  # Sample step count

# --- 8. UI RENDERING FUNCTIONS ---
def get_time_based_theme():
    """ Determines a greeting icon based on the current time in India. """
    now = datetime.now(IST)
    hour = now.hour
    if 5 <= hour < 12: return "☀️"
    elif 12 <= hour < 17: return "👋"
    else: return "🌙"

greeting_icon = get_time_based_theme()

def render_header():
    header_cols = st.columns([3, 1])
    with header_cols[0]:
        st.title(f"{greeting_icon} Welcome, {user_name.split()[0]}!")
        st.markdown("Here is your wellness summary for today.")
    with header_cols[1]:
        clock_placeholder = st.empty()
    st.divider()
    return clock_placeholder

def render_left_panel():
    st.subheader("Quick Actions")
    
    # EMERGENCY SOS CARD
    st.markdown('<div class="card emergency-card">', unsafe_allow_html=True)
    st.markdown('<h3>🚨 EMERGENCY SOS</h3>', unsafe_allow_html=True)
    if primary_contact:
        st.markdown(f"<p style='font-size: 1rem; color: white;'>Click to call<br><b>{primary_contact['contact_name']}</b></p>", unsafe_allow_html=True)
        st.markdown(f"<div class='sos-button'><a href='tel:{primary_contact['phone_number']}'>📞 CALL NOW</a></div>", unsafe_allow_html=True)
    else: 
        st.markdown("<p style='font-size: 1rem; color: white;'>Please add an emergency contact in your profile.</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # WEEKLY REPORT CARD
    st.markdown('<div class="card metric-card">', unsafe_allow_html=True)
    st.markdown('<h3>📈 Weekly Adherence</h3>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{adherence_score}%</div>', unsafe_allow_html=True)
    st.caption(adherence_message)
    
    # Adherence progress bar
    st.progress(adherence_score/100)
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
    st.subheader("Today's Focus")
    
    # Today's Focus Card (Meds & Appointments)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    tabs = st.tabs(["💊 Medications", "🗓️ Appointments"])
    
    with tabs[0]:
        if not pending_meds: 
            st.success("All medications for today have been taken! Great job!")
        for med in pending_meds:
            med_timing_str = med.get('meal_timing') or (datetime.strptime(med['specific_time'], '%H:%M:%S').strftime('%I:%M %p') if med.get('specific_time') else 'Anytime')
            st.markdown("<div class='list-item'>", unsafe_allow_html=True)
            item_cols = st.columns([1, 4, 1])
            with item_cols[0]:
                st.markdown('<div class="list-item-icon">💊</div>', unsafe_allow_html=True)
            with item_cols[1]:
                st.markdown(f"<div class='list-item-info'><b>{med['name']}</b> ({med['dosage']})<br><small>Due: {med_timing_str}</small></div>", unsafe_allow_html=True)
            with item_cols[2]:
                st.checkbox("Taken", value=False, key=f"d_{med['id']}", on_change=handle_med_taken_action, args=(med['id'],), label_visibility="hidden")
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tabs[1]:
        if not todays_appointments:
            st.info("You have no appointments scheduled for today.")
        else:
            for appt in todays_appointments:
                appt_dt_utc = datetime.fromisoformat(appt['appointment_datetime'])
                appt_dt_ist = appt_dt_utc.astimezone(IST)
                st.markdown("<div class='list-item'>", unsafe_allow_html=True)
                st.markdown('<div class="list-item-icon">🗓️</div>', unsafe_allow_html=True)
                st.markdown(f"<div class='list-item-info'><b>{appt_dt_ist.strftime('%I:%M %p')} with Dr. {appt.get('doctor_name', 'N/A')}</b><br><small>Location: {appt.get('location', 'N/A')}</small></div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
    
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
    st.subheader("Upcoming & Info")
    
    # UPCOMING APPOINTMENTS CARD
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<h5>🗓️ Upcoming Appointments</h5>", unsafe_allow_html=True)
    if not upcoming_appointments:
        st.info("No appointments scheduled for the upcoming week.")
    else:
        for appt in upcoming_appointments:
            appt_dt_utc = datetime.fromisoformat(appt['appointment_datetime'])
            appt_dt_ist = appt_dt_utc.astimezone(IST)
            day_str = "Today" if appt_dt_ist.date() == datetime.now(IST).date() else appt_dt_ist.strftime('%A, %b %d')
            st.markdown(f"<div class='list-item'><div class='list-item-info'><b>{day_str} at {appt_dt_ist.strftime('%I:%M %p')}</b><br><small>Dr. {appt.get('doctor_name', 'N/A')}</small></div></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # HEALTH TIP CARD
    st.markdown('<div class="card tip-card">', unsafe_allow_html=True)
    st.markdown(f"<h5>💡 Daily Health Tip</h5><p>{health_tip}</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # DATA EXPORT FEATURE
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<h5>📄 Data & Reports</h5>", unsafe_allow_html=True)
    st.markdown("<small>Export your medication and appointment history for your doctor's visit.</small>", unsafe_allow_html=True)
    
    med_history_df = pd.DataFrame({
        'Date': [(datetime.now(IST) - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)],
        'Medication': ['Lisinopril', 'Metformin', 'Lisinopril', 'Atorvastatin', 'Metformin', 'Lisinopril', 'Metformin'],
        'Status': ['Taken', 'Taken', 'Missed', 'Taken', 'Taken', 'Taken', 'Missed']
    })
    
    st.download_button(
        label="📥 Export Report (CSV)",
        data=med_history_df.to_csv(index=False).encode('utf-8'),
        file_name='wellness_report.csv',
        mime='text/csv',
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# --- 9. MAIN LAYOUT & APP EXECUTION ---
if 'welcomed' not in st.session_state:
    st.info("Welcome to your Wellness Hub! This is your main dashboard where you can see all your daily tasks at a glance.")
    st.session_state.welcomed = True

clock_placeholder = render_header()
main_cols = st.columns([1, 2, 1], gap="large")

with main_cols[0]:
    render_left_panel()

with main_cols[1]:
    render_center_panel()

with main_cols[2]:
    render_right_panel()

# --- 10. LIVE CLOCK BACKGROUND PROCESS ---
# Note: This while loop will run continuously, updating the clock
# In a production environment, consider using a different approach
while True:
    now_ist = datetime.now(IST)
    time_str = now_ist.strftime("%I:%M:%S %p")
    date_str = now_ist.strftime("%A, %B %d, %Y")
    with clock_placeholder.container():
        st.markdown(f"<div style='text-align: right;'><h2 style='font-weight: 700; margin-bottom: -15px; color: #212121;'>{time_str}</h2><p style='color: #616161;'>{date_str}</p></div>", unsafe_allow_html=True)
    time.sleep(1)