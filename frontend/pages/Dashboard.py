# frontend/pages/Dashboard.py (Fully Fixed Version)

import streamlit as st
import requests
from datetime import datetime, date, timedelta
import time

# Set page config first
st.set_page_config(page_title="Dashboard", layout="wide")

# --- CONFIGURATION & API CLIENT ---
# Use the same logic as main app for API URL
if 'RENDER' in st.secrets or 'RENDER' in os.environ:
    API_BASE_URL = "https://health-companion-backend-44ug.onrender.com"
else:
    API_BASE_URL = "http://localhost:8000"

# --- API CLIENT CLASS ---
class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def _get_headers(self):
        token = st.session_state.get("token", None)
        if token: 
            return {"Authorization": f"Bearer {token}"}
        return {}
    
    def _make_request(self, method, endpoint, **kwargs):
        try:
            response = requests.request(
                method, 
                f"{self.base_url}{endpoint}", 
                headers=self._get_headers(), 
                timeout=10, 
                **kwargs
            )
            return response
        except requests.exceptions.RequestException as e:
            st.error(f"Connection Error: Could not connect to backend. Error: {str(e)}")
            return None
    
    def get(self, endpoint, params=None): 
        return self._make_request("GET", endpoint, params=params)
    
    def post(self, endpoint, json=None): 
        return self._make_request("POST", endpoint, json=json)

api = ApiClient(API_BASE_URL)

# --- SECURITY CHECK ---
if 'token' not in st.session_state:
    st.warning("Please login first to access this page.")
    st.stop()

# --- STYLING (For the beautiful cards) ---
st.markdown("""
<style>
.card {
    background-color: #FFFFFF;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    transition: all 0.2s ease-in-out;
    height: 100%;
    border: 1px solid #e0e0e0;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}
.card h3 {
    margin-top: 0;
    font-size: 1.2rem;
    color: #333;
}
.card p {
    font-size: 2.5rem;
    font-weight: bold;
    margin: 0;
}
.card-green p { color: #2e7d32; }
.card-blue p { color: #0277bd; }
.card-orange p { color: #ef6c00; }
.card-tip p {
    font-size: 1rem;
    font-weight: normal;
    color: #555;
    line-height: 1.4;
}
.live-clock {
    font-size: 2rem;
    font-weight: bold;
    color: #0068c9;
    text-align: right;
}
.live-date {
    font-size: 1rem;
    color: #555;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

# --- LIVE CLOCK COMPONENT ---
def create_live_clock():
    current_time = datetime.now().strftime("%I:%M:%S %p")
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    
    clock_html = f"""
        <div style="text-align: right; margin-bottom: 1rem;">
            <div class="live-clock">{current_time}</div>
            <div class="live-date">{current_date}</div>
        </div>
    """
    
    clock_placeholder = st.empty()
    clock_placeholder.markdown(clock_html, unsafe_allow_html=True)
    
    return clock_placeholder

# --- DATA LOADING FUNCTIONS ---
def load_user_profile():
    """Load user profile data"""
    response = api.get("/users/me")
    if response and response.status_code == 200:
        return response.json()
    return None

def load_appointments():
    """Load appointments for the next 7 days"""
    today = date.today().isoformat()
    next_week = (date.today() + timedelta(days=7)).isoformat()
    
    response = api.get(f"/appointments/?start_date={today}&end_date={next_week}")
    if response and response.status_code == 200:
        return response.json()
    return []

def load_medications():
    """Load user medications"""
    response = api.get("/medications/")
    if response and response.status_code == 200:
        return response.json()
    return []

def load_health_tip():
    """Load random health tip"""
    response = api.get("/tips/random")
    if response and response.status_code == 200:
        return response.json()
    return None

def load_medication_log():
    """Load medication log for today"""
    today = date.today().isoformat()
    response = api.get(f"/medications/log/{today}")
    if response and response.status_code == 200:
        return response.json()
    return []

# --- CALLBACK FUNCTION FOR BUTTONS ---
def handle_med_taken(med_id):
    with st.spinner("Logging..."):
        response = api.post(f"/medications/{med_id}/log")
    if response and response.status_code in [201, 200]:
        st.toast("Medication logged successfully! ✅")
        # Clear cache to refresh data
        st.cache_data.clear()
        st.rerun()
    else:
        st.error("Failed to log medication.")

# --- MAIN DASHBOARD UI ---
def main_dashboard():
    # Create live clock
    clock_placeholder = create_live_clock()
    
    # Load all data
    with st.spinner("Loading your dashboard..."):
        user_profile = load_user_profile()
        all_appointments = load_appointments() or []
        all_medications = load_medications() or []
        health_tip = load_health_tip()
        taken_med_ids = load_medication_log() or []
    
    if not user_profile:
        st.error("Could not load your profile data. Please try refreshing.")
        st.stop()
    
    # Update live clock every second
    if st.session_state.get('clock_running', True):
        while st.session_state.clock_running:
            current_time = datetime.now().strftime("%I:%M:%S %p")
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            
            clock_html = f"""
                <div style="text-align: right; margin-bottom: 1rem;">
                    <div class="live-clock">{current_time}</div>
                    <div class="live-date">{current_date}</div>
                </div>
            """
            
            clock_placeholder.markdown(clock_html, unsafe_allow_html=True)
            time.sleep(1)
    
    # Personalized Welcome Message
    user_name = user_profile.get('full_name', 'User').split(' ')[0] if user_profile else 'User'
    st.header(f"👋 Welcome Back, {user_name}!")
    st.write(f"Here's your summary for **{date.today().strftime('%A, %d %B %Y')}**.")
    
    # Process data
    today = date.today()
    time_format_pref = user_profile.get("time_format", "12h")
    time_format_str = "%I:%M %p" if time_format_pref == "12h" else "%H:%M"
    
    # Filter today's appointments
    today_appointments = []
    for app in all_appointments:
        try:
            if 'appointment_datetime' in app:
                app_datetime = datetime.fromisoformat(app['appointment_datetime'].replace('Z', '+00:00'))
                if app_datetime.date() == today:
                    today_appointments.append(app)
        except (ValueError, TypeError):
            continue
    
    # Filter active medications for today
    active_medications = [med for med in all_medications if med.get('is_active', True)]
    
    # Track taken medications
    st.session_state.taken_med_ids = taken_med_ids
    
    # --- "DAY SUMMARY" CARD SECTION ---
    st.subheader("Today's Summary")
    s_col1, s_col2, s_col3 = st.columns(3)
    
    with s_col1:
        total_meds = len(active_medications)
        meds_taken_count = len([mid for mid in taken_med_ids if mid in [m.get('id') for m in active_medications]])
        st.markdown(f"""
        <div class="card card-green">
            <h3>✅ Medicines Taken</h3>
            <p>{meds_taken_count} / {total_meds}</p>
        </div>""", unsafe_allow_html=True)
    
    with s_col2:
        st.markdown(f"""
        <div class="card card-blue">
            <h3>🗓️ Appointments Today</h3>
            <p>{len(today_appointments)}</p>
        </div>""", unsafe_allow_html=True)
    
    with s_col3:
        tip_content = health_tip['content'] if health_tip else "Stay hydrated and take your medications on time."
        tip_category = health_tip['category'] if health_tip else "Health Tip"
        st.markdown(f"""
        <div class="card card-orange card-tip">
            <h3>💡 {tip_category}</h3>
            <p>{tip_content}</p>
        </div>""", unsafe_allow_html=True)
    
    st.divider()
    
    # --- MAIN CONTENT AREA ---
    d_col1, d_col2 = st.columns(2, gap="large")
    
    with d_col1:
        st.subheader("Today's Medications")
        if not active_medications:
            st.info("No medications scheduled today.")
        else:
            for med in active_medications:
                is_taken = med.get('id') in taken_med_ids
                
                with st.container(border=True):
                    m_col1, m_col2 = st.columns([1, 4])
                    
                    with m_col1:
                        pfp_url = med.get("photo_url")
                        if pfp_url: 
                            st.image(f"{API_BASE_URL}/{pfp_url}", width=70)
                        else: 
                            st.image("https://via.placeholder.com/70x70.png?text=💊", width=70)
                    
                    with m_col2:
                        st.markdown(f"**{med.get('name', 'Unknown Medication')}**")
                        try:
                            med_time = datetime.strptime(med['timing'], '%H:%M:%S').strftime(time_format_str)
                        except:
                            med_time = med.get('timing', 'Unknown time')
                        st.caption(f"{med.get('dosage', '')} - Due at {med_time}")
                    
                    st.button(
                        "✅ Taken" if is_taken else "Mark as Taken", 
                        key=f"med_taken_{med.get('id')}",
                        on_click=handle_med_taken, 
                        args=(med.get('id'),), 
                        disabled=is_taken,
                        use_container_width=True, 
                        type="primary" if not is_taken else "secondary"
                    )
    
    with d_col2:
        st.subheader("Today's Appointments")
        if not today_appointments:
            st.info("No appointments today.")
        else:
            for app in today_appointments:
                with st.container(border=True):
                    a_col1, a_col2 = st.columns([1, 4])
                    
                    with a_col1:
                        pfp_url = app.get("photo_url")
                        if pfp_url: 
                            st.image(f"{API_BASE_URL}/{pfp_url}", width=70)
                        else: 
                            st.image("https://via.placeholder.com/70x70.png?text=👨‍⚕️", width=70)
                    
                    with a_col2:
                        st.markdown(f"**{app.get('doctor_name', 'Unknown Doctor')}**")
                        try:
                            app_time = datetime.fromisoformat(
                                app['appointment_datetime'].replace('Z', '+00:00')
                            ).strftime(time_format_str)
                        except:
                            app_time = "Unknown time"
                        
                        st.caption(f"{app.get('purpose', 'Check-up')} at {app_time}")
                        st.caption(f"📍 {app.get('location', 'Not specified')}")
                    
                    if st.button("View Details", key=f"view_app_{app.get('id')}", use_container_width=True):
                        st.session_state.current_page = "Appointments"
                        st.rerun()
    
    # Add refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Initialize clock state
if 'clock_running' not in st.session_state:
    st.session_state.clock_running = True

# Run the dashboard
try:
    main_dashboard()
except Exception as e:
    st.error(f"Error loading dashboard: {str(e)}")
    st.info("Please try refreshing the page or contact support if the issue persists.")
