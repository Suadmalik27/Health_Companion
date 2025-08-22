# frontend/pages/Dashboard.py

import streamlit as st
import requests
from datetime import datetime, date, timedelta

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
            return requests.request(
                method, 
                f"{self.base_url}{endpoint}", 
                headers=self._get_headers(), 
                timeout=10, 
                **kwargs
            )
        except requests.exceptions.RequestException:
            st.error("Connection Error: Could not connect to the backend server.")
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
</style>
""", unsafe_allow_html=True)

# --- DATA LOADING (EFFICIENT & CACHED) ---
@st.cache_data(ttl=30)
def load_dashboard_data(_api_client: ApiClient):
    today_iso = date.today().isoformat()
    endpoints = {
        "user_profile": "/users/me",
        "appointments": f"/appointments/?start_date={today_iso}&end_date={(date.today() + timedelta(days=6)).isoformat()}",
        "medications": "/medications/",
        "tip": "/tips/random",
        "med_log": f"/medications/log/{today_iso}"
    }
    data = {}
    for key, endpoint in endpoints.items():
        response = _api_client.get(endpoint)
        if response and response.status_code == 200:
            data[key] = response.json()
        else: 
            data[key] = None
    return data

# --- CALLBACK FUNCTION FOR BUTTONS ---
def handle_med_taken(med_id):
    with st.spinner("Logging..."):
        response = api.post(f"/medications/{med_id}/log")
    if response and response.status_code in [201, 200]:
        st.toast(f"Great job!", icon="✅")
        if 'taken_med_ids' not in st.session_state:
            st.session_state.taken_med_ids = []
        st.session_state.taken_med_ids.append(med_id)
        st.cache_data.clear()
        st.rerun()
    else:
        st.error("Failed to log medication.")

# --- MAIN DASHBOARD UI ---
with st.spinner("Loading your dashboard..."):
    dashboard_data = load_dashboard_data(api)
    user_profile = dashboard_data.get("user_profile")
    all_appointments = dashboard_data.get("appointments") or []
    all_medications = dashboard_data.get("medications") or []
    health_tip = dashboard_data.get("tip")
    taken_med_ids_from_api = dashboard_data.get("med_log") or []

if all_medications is None:
    st.error("Could not load medication data. Please try refreshing.")
    st.stop()

# Personalized Welcome Message
user_name = user_profile.get('full_name', 'User').split(' ')[0] if user_profile else 'User'
st.header(f"👋 Welcome Back, {user_name}!")
st.write(f"Here's your summary for **{date.today().strftime('%A, %d %B %Y')}**.")

# Track taken medications
session_taken = st.session_state.get('taken_med_ids', [])
api_taken = taken_med_ids_from_api
st.session_state.taken_med_ids = list(set(session_taken + api_taken))

time_format_pref = user_profile.get("time_format", "12h") if user_profile else "12h"
time_format_str = "%I:%M %p" if time_format_pref == "12h" else "%H:%M"
today = date.today()

# Filter today's appointments
today_appointments = []
for app in all_appointments:
    try:
        app_date = datetime.fromisoformat(app['appointment_datetime'].replace('Z', '+00:00')).date()
        if app_date == today:
            today_appointments.append(app)
    except (ValueError, KeyError):
        continue

# Filter active medications
today_medications = [med for med in all_medications if med.get('is_active', True)]

# --- "DAY SUMMARY" CARD SECTION (IMPROVED UI) ---
st.subheader("Today's Summary")
s_col1, s_col2, s_col3 = st.columns(3)

with s_col1:
    total_meds = len(today_medications)
    meds_taken_count = len([mid for mid in st.session_state.get('taken_med_ids', []) 
                           if mid in [m['id'] for m in today_medications]])
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
    if not today_medications:
        st.info("No medications scheduled today.")
    else:
        for med in sorted(today_medications, key=lambda x: x['timing']):
            is_taken = med['id'] in st.session_state.get('taken_med_ids', [])
            
            with st.container(border=True):
                m_col1, m_col2 = st.columns([1, 4])
                
                with m_col1:
                    pfp_url = med.get("photo_url")
                    if pfp_url: 
                        st.image(f"{API_BASE_URL}/{pfp_url}", width=70)
                    else: 
                        st.image("https://via.placeholder.com/70x70.png?text=💊", width=70)
                
                with m_col2:
                    st.markdown(f"**{med['name']}**")
                    try:
                        med_time = datetime.strptime(med['timing'], '%H:%M:%S').strftime(time_format_str)
                    except:
                        med_time = med['timing']
                    st.caption(f"{med['dosage']} - Due at {med_time}")
                
                st.button(
                    "✅ Taken" if is_taken else "Mark as Taken", 
                    key=f"med_taken_{med['id']}",
                    on_click=handle_med_taken, 
                    args=(med['id'],), 
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
                    st.markdown(f"**{app['doctor_name']}**")
                    try:
                        app_time = datetime.fromisoformat(
                            app['appointment_datetime'].replace('Z', '+00:00')
                        ).strftime(time_format_str)
                    except:
                        app_time = "Unknown time"
                    
                    st.caption(f"{app.get('purpose', 'Check-up')} at {app_time}")
                    st.caption(f"📍 {app.get('location', 'Not specified')}")
                
                if st.button("View Details", key=f"view_app_{app['id']}", use_container_width=True):
                    st.switch_page("pages/3_Appointments.py")
