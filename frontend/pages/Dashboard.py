# frontend/pages/Dashboard.py

import streamlit as st
import requests
from datetime import datetime, date, timedelta

# --- CONFIGURATION & API CLIENT ---
# Backend URL ko permanent set kar diya gaya hai aapke request ke anusaar.
API_BASE_URL = "https://health-companion-backend-44ug.onrender.com"

# --- API CLIENT CLASS ---
class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
    def _get_headers(self):
        token = st.session_state.get("token", None)
        if token: return {"Authorization": f"Bearer {token}"}
        return {}
    def _make_request(self, method, endpoint, **kwargs):
        try:
            return requests.request(method, f"{self.base_url}{endpoint}", headers=self._get_headers(), timeout=10, **kwargs)
        except requests.exceptions.RequestException:
            st.error("Connection Error: Could not connect to the backend server."); return None
    def get(self, endpoint, params=None): return self._make_request("GET", endpoint, params=params)
    def post(self, endpoint, json=None): return self._make_request("POST", endpoint, json=json)

api = ApiClient(API_BASE_URL)

# --- SECURITY CHECK ---
if 'token' not in st.session_state:
    st.warning("Please login first to access this page."); st.stop()

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
        else: data[key] = None
    return data

# --- CALLBACK FUNCTION FOR BUTTONS ---
def handle_med_taken(med_id):
    with st.spinner("Logging..."):
        response = api.post(f"/medications/{med_id}/log")
    if response and response.status_code in [201, 200]:
        st.toast(f"Great job!", icon="✅")
        # Ensure 'taken_med_ids' exists and is a list before appending
        if 'taken_med_ids' not in st.session_state or not isinstance(st.session_state.taken_med_ids, list):
            st.session_state.taken_med_ids = []
        st.session_state.taken_med_ids.append(med_id)
        st.cache_data.clear() # Clear cache to refetch data
        st.rerun() # Rerun to update the UI instantly
    else:
        st.error("Failed to log medication.")

# --- MAIN DASHBOARD UI ---
st.set_page_config(page_title="Dashboard", layout="wide")

with st.spinner("Loading your dashboard..."):
    dashboard_data = load_dashboard_data(api)
    user_profile = dashboard_data.get("user_profile")
    all_appointments = dashboard_data.get("appointments")
    all_medications = dashboard_data.get("medications")
    health_tip = dashboard_data.get("tip")
    taken_med_ids_from_api = dashboard_data.get("med_log", [])

if not all_medications:
    st.error("Could not load medication data. Please try refreshing."); st.stop()

# Robustly initialize session state for taken medications
session_taken = st.session_state.get('taken_med_ids', []) or []
api_taken = [log['medication_id'] for log in taken_med_ids_from_api] if taken_med_ids_from_api else []
st.session_state.taken_med_ids = list(set(session_taken + api_taken))

time_format_pref = user_profile.get("time_format", "12h") if user_profile else "12h"
time_format_str = "%I:%M %p" if time_format_pref == "12h" else "%H:%M"
today = date.today()
today_appointments = [app for app in all_appointments if datetime.fromisoformat(app['appointment_datetime']).date() == today] if all_appointments else []
today_medications = [med for med in all_medications if med.get('is_active', True)]

# --- "DAY SUMMARY" CARD SECTION ---
st.subheader("Today's Summary")
s_col1, s_col2, s_col3 = st.columns(3)
with s_col1:
    total_meds = len(today_medications)
    meds_taken_count = len(st.session_state.get('taken_med_ids', []))
    st.markdown(f"""
    <div class="card" style="padding: 1rem; border-radius: 10px; background-color: #e8f5e9; text-align: center;">
        <h3 style="color: #4caf50;">✅ Medicines Taken</h3>
        <p style="font-size: 2.5rem; font-weight: bold; margin: 0; color: #4caf50;">{meds_taken_count} / {total_meds}</p>
    </div>""", unsafe_allow_html=True)

with s_col2:
    st.markdown(f"""
    <div class="card" style="padding: 1rem; border-radius: 10px; background-color: #e3f2fd; text-align: center;">
        <h3 style="color: #1c83e1;">🗓️ Appointments Today</h3>
        <p style="font-size: 2.5rem; font-weight: bold; margin: 0; color: #1c83e1;">{len(today_appointments)}</p>
    </div>""", unsafe_allow_html=True)
with s_col3:
    tip_content = health_tip['content'] if health_tip else "Stay hydrated."
    tip_category = health_tip['category'] if health_tip else "Health Tip"
    st.markdown(f"""
    <div class="card" style="padding: 1rem; border-radius: 10px; background-color: #fff3e0; text-align: center;">
        <h3 style="color: #ff9800;">💡 {tip_category}</h3>
        <p style="font-size: 1rem; margin: 0;">{tip_content}</p>
    </div>""", unsafe_allow_html=True)

st.divider()

d_col1, d_col2 = st.columns(2, gap="large")
with d_col1:
    st.subheader("Today's Medications")
    if not today_medications:
        st.info("No medications scheduled today.")
    else:
        for med in sorted(today_medications, key=lambda x: datetime.strptime(x['timing'], '%H:%M:%S').time()):
            is_taken = med['id'] in st.session_state.get('taken_med_ids', [])
            with st.container(border=True):
                m_col1, m_col2 = st.columns([1, 4])
                with m_col1:
                    pfp_url = med.get("photo_url")
                    if pfp_url: st.image(f"{API_BASE_URL}/{pfp_url}", width=70)
                    else: st.image("https://via.placeholder.com/70x70.png?text=💊", width=70)
                with m_col2:
                    st.markdown(f"**{med['name']}**")
                    st.caption(f"{med['dosage']} - Due at {datetime.strptime(med['timing'], '%H:%M:%S').strftime(time_format_str)}")
                st.button(
                    "✅ Taken" if is_taken else "Mark as Taken", key=f"med_taken_{med['id']}",
                    on_click=handle_med_taken, args=(med['id'],), disabled=is_taken,
                    use_container_width=True, type="primary" if not is_taken else "secondary"
                )
with d_col2:
    st.subheader("Today's Appointments")
    if not today_appointments:
        st.info("No appointments today.")
    else:
        for app in sorted(today_appointments, key=lambda x: x['appointment_datetime']):
            with st.container(border=True):
                a_col1, a_col2 = st.columns([1, 4])
                with a_col1:
                    pfp_url = app.get("photo_url")
                    if pfp_url: st.image(f"{API_BASE_URL}/{pfp_url}", width=70)
                    else: st.image("https://via.placeholder.com/70x70.png?text=👨‍⚕️", width=70)
                with a_col2:
                    st.markdown(f"**{app['doctor_name']}**")
                    st.caption(f"{app.get('purpose', 'Check-up')} at {datetime.fromisoformat(app['appointment_datetime']).strftime(time_format_str)}")
                    st.caption(f"📍 {app.get('location', 'Not specified')}")
