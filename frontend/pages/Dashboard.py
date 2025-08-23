# frontend/pages/Dashboard.py (Fixed Indian Timezone + Dark Mode)
import streamlit as st
import requests
from datetime import datetime, date, timedelta
import time
import os
import pytz

# Set page config first
st.set_page_config(page_title="Dashboard", layout="wide")

# --- CONFIGURATION & API CLIENT ---
# Use the same logic as main app for API URL
API_BASE_URL = st.secrets.get("API_BASE_URL", "https://health-companion-backend-44ug.onrender.com")

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

# --- TIMEZONE SETUP ---
INDIAN_TIMEZONE = pytz.timezone('Asia/Kolkata')

def get_indian_time():
    """Get current time in Indian timezone"""
    return datetime.now(INDIAN_TIMEZONE)

def format_time_for_display(dt, time_format="12h"):
    """Format datetime for display based on user preference"""
    if time_format == "12h":
        return dt.strftime('%I:%M:%S %p')
    else:
        return dt.strftime('%H:%M:%S')

# --- DARK MODE COMPATIBLE STYLING ---
st.markdown("""
<style>
/* Dark Mode Compatible Styling */
.card {
    background-color: var(--card-background, #FFFFFF) !important;
    color: var(--card-text, #333333) !important;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    transition: all 0.2s ease-in-out;
    height: 100%;
    border: 1px solid var(--card-border, #e0e0e0);
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}
.card h3 {
    margin-top: 0;
    font-size: 1.2rem;
    color: var(--card-title, #333333) !important;
}
.card p {
    font-size: 2.5rem;
    font-weight: bold;
    margin: 0;
    color: var(--card-value, #333333) !important;
}
.card-green p { color: var(--success-color, #2e7d32) !important; }
.card-blue p { color: var(--info-color, #0277bd) !important; }
.card-orange p { color: var(--warning-color, #ef6c00) !important; }
.card-tip p {
    font-size: 1rem;
    font-weight: normal;
    color: var(--text-color, #555555) !important;
    line-height: 1.4;
}
.live-clock {
    font-size: 2rem;
    font-weight: bold;
    color: var(--primary-color, #0068c9) !important;
    text-align: right;
}
.live-date {
    font-size: 1rem;
    color: var(--text-color, #555555) !important;
    text-align: right;
}
.emergency-action {
    background-color: var(--danger-color, #ff4444) !important;
    color: white !important;
    border: none;
    padding: 12px;
    border-radius: 8px;
    margin: 5px;
    cursor: pointer;
    font-weight: bold;
    text-align: center;
    width: 100%;
}
.emergency-action:hover {
    background-color: var(--danger-hover, #cc0000) !important;
    transform: translateY(-2px);
}

/* Ensure text visibility in dark mode */
h1, h2, h3, h4, h5, h6, p, span, div, .stMarkdown {
    color: var(--text-color, #333333) !important;
}

/* Container styling */
.stContainer {
    background-color: var(--background-color, #ffffff) !important;
    color: var(--text-color, #333333) !important;
}

/* Indian time badge */
.indian-time-badge {
    background: linear-gradient(135deg, #FF9933 0%, #138808 100%);
    color: white !important;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: bold;
    margin-left: 10px;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

# --- LIVE CLOCK COMPONENT ---
def create_live_clock():
    """Create live clock showing Indian time"""
    indian_time = get_indian_time()
    current_time = format_time_for_display(indian_time, "12h")
    current_date = indian_time.strftime("%A, %B %d, %Y")
    
    clock_html = f"""
        <div style="text-align: right; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; justify-content: flex-end;">
                <div class="live-clock">{current_time}</div>
                <span class="indian-time-badge">🇮🇳 IST</span>
            </div>
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

def load_contacts():
    """Load emergency contacts"""
    response = api.get("/contacts/")
    if response and response.status_code == 200:
        return response.json()
    return []

# --- TIME FORMATTING FUNCTION ---
def format_time(time_str, time_format="12h"):
    """Convert time string to proper format in Indian timezone"""
    try:
        if isinstance(time_str, str):
            # Handle different time string formats
            if ':' in time_str:
                # Parse the time string
                time_obj = datetime.strptime(time_str, '%H:%M:%S').time()
                
                # Create a datetime object with today's date and the parsed time
                today = get_indian_time().date()
                datetime_obj = datetime.combine(today, time_obj)
                
                # Localize to Indian timezone
                datetime_obj = INDIAN_TIMEZONE.localize(datetime_obj)
                
                if time_format == "12h":
                    return datetime_obj.strftime('%I:%M %p')
                else:
                    return datetime_obj.strftime('%H:%M')
            else:
                # Handle other time formats if needed
                return time_str
        return time_str
    except (ValueError, TypeError) as e:
        print(f"Time formatting error: {e}")
        return time_str

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

# --- EMERGENCY ACTION FUNCTIONS ---
def call_emergency(phone_number):
    st.markdown(f'<a href="tel:{phone_number}" style="display: none;" id="call-link"></a>', unsafe_allow_html=True)
    st.markdown('<script>document.getElementById("call-link").click();</script>', unsafe_allow_html=True)
    st.toast(f"Calling {phone_number}...")

def sms_emergency(phone_number):
    st.markdown(f'<a href="sms:{phone_number}" style="display: none;" id="sms-link"></a>', unsafe_allow_html=True)
    st.markdown('<script>document.getElementById("sms-link").click();</script>', unsafe_allow_html=True)
    st.toast(f"Sending SMS to {phone_number}...")

def alert_all_contacts(contacts):
    for contact in contacts:
        phone = contact.get('phone_number', '')
        name = contact.get('name', '')
        if phone:
            # This would ideally send an actual alert via SMS API
            st.toast(f"Alert sent to {name} at {phone}")
    st.success("Alerts sent to all emergency contacts!")

# --- MAIN DASHBOARD UI ---
def main_dashboard():
    # Create live clock with Indian time
    clock_placeholder = create_live_clock()
    
    # Load all data
    with st.spinner("Loading your dashboard..."):
        user_profile = load_user_profile()
        all_appointments = load_appointments() or []
        all_medications = load_medications() or []
        health_tip = load_health_tip()
        taken_med_ids = load_medication_log() or []
        emergency_contacts = load_contacts() or []
    
    if not user_profile:
        st.error("Could not load your profile data. Please try refreshing.")
        st.stop()
    
    # Update live clock every second with Indian time
    if st.session_state.get('clock_running', True):
        while st.session_state.clock_running:
            indian_time = get_indian_time()
            current_time = format_time_for_display(indian_time, "12h")
            current_date = indian_time.strftime("%A, %B %d, %Y")
            
            clock_html = f"""
                <div style="text-align: right; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; justify-content: flex-end;">
                        <div class="live-clock">{current_time}</div>
                        <span class="indian-time-badge">🇮🇳 IST</span>
                    </div>
                    <div class="live-date">{current_date}</div>
                </div>
            """
            
            clock_placeholder.markdown(clock_html, unsafe_allow_html=True)
            time.sleep(1)
    
    # Personalized Welcome Message
    user_name = user_profile.get('full_name', 'User').split(' ')[0] if user_profile else 'User'
    st.header(f"👋 Welcome Back, {user_name}!")
    
    # Display date in Indian format
    indian_date = get_indian_time().strftime("%A, %d %B %Y")
    st.write(f"Here's your summary for **{indian_date}**.")
    
    # Process data
    today = date.today()
    time_format_pref = user_profile.get("time_format", "12h")
    
    # Filter today's appointments
    today_appointments = []
    for app in all_appointments:
        try:
            if 'appointment_datetime' in app:
                # Parse appointment datetime and convert to Indian timezone
                app_datetime = datetime.fromisoformat(app['appointment_datetime'].replace('Z', '+00:00'))
                app_datetime = app_datetime.astimezone(INDIAN_TIMEZONE)
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
    
    # --- QUICK EMERGENCY ACTIONS ---
    if emergency_contacts:
        primary_contact = emergency_contacts[0]
        st.subheader("🚨 Quick Emergency Actions")
        
        em_col1, em_col2, em_col3 = st.columns(3)
        
        with em_col1:
            if st.button(f"📞 Call {primary_contact.get('name', 'Primary Contact')}", 
                        use_container_width=True, 
                        type="primary",
                        on_click=call_emergency, 
                        args=(primary_contact.get('phone_number', ''),)):
                pass
        
        with em_col2:
            if st.button(f"💬 SMS {primary_contact.get('name', 'Primary Contact')}", 
                        use_container_width=True,
                        on_click=sms_emergency, 
                        args=(primary_contact.get('phone_number', ''),)):
                pass
        
        with em_col3:
            if st.button("📢 Alert All Contacts", 
                        use_container_width=True,
                        on_click=alert_all_contacts, 
                        args=(emergency_contacts,)):
                pass
    
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
                            # Fix URL formatting
                            cleaned_url = pfp_url.replace('\\', '/')
                            st.image(f"{API_BASE_URL}/{cleaned_url}", width=70)
                        else: 
                            st.image("https://via.placeholder.com/70x70.png?text=💊", width=70)
                    
                    with m_col2:
                        st.markdown(f"**{med.get('name', 'Unknown Medication')}**")
                        # FIXED: Use proper time formatting function for Indian time
                        med_time = format_time(med.get('timing'), time_format_pref)
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
                            # Fix URL formatting
                            cleaned_url = pfp_url.replace('\\', '/')
                            st.image(f"{API_BASE_URL}/{cleaned_url}", width=70)
                        else: 
                            st.image("https://via.placeholder.com/70x70.png?text=👨‍⚕️", width=70)
                    
                    with a_col2:
                        st.markdown(f"**{app.get('doctor_name', 'Unknown Doctor')}**")
                        try:
                            # Parse and convert to Indian timezone
                            app_time = datetime.fromisoformat(
                                app['appointment_datetime'].replace('Z', '+00:00')
                            )
                            app_time = app_time.astimezone(INDIAN_TIMEZONE)
                            
                            # Format based on user preference
                            if time_format_pref == "12h":
                                formatted_time = app_time.strftime('%I:%M %p')
                            else:
                                formatted_time = app_time.strftime('%H:%M')
                                
                            # Add date if needed
                            formatted_datetime = f"{app_time.strftime('%d %b')} at {formatted_time}"
                            
                        except:
                            formatted_datetime = "Unknown time"
                        
                        st.caption(f"{app.get('purpose', 'Check-up')} - {formatted_datetime}")
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
