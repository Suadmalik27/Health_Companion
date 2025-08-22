# frontend/pages/Dashboard.py (Simplified Working Version)

import streamlit as st
import requests
from datetime import datetime, date, timedelta
import time
import os

# Set page config first
st.set_page_config(page_title="Dashboard", layout="wide")

# --- CONFIGURATION & API CLIENT ---
if 'RENDER' in os.environ:
    API_BASE_URL = "https://health-companion-backend-44ug.onrender.com"
else:
    API_BASE_URL = "http://localhost:8000"

class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def _get_headers(self):
        token = st.session_state.get("token")
        return {"Authorization": f"Bearer {token}"} if token else {}
    
    def _make_request(self, method, endpoint, **kwargs):
        try:
            return requests.request(method, f"{self.base_url}{endpoint}", 
                                  headers=self._get_headers(), timeout=10, **kwargs)
        except requests.exceptions.RequestException:
            st.error("Could not connect to backend server")
            return None
    
    def get(self, endpoint, params=None): 
        return self._make_request("GET", endpoint, params=params)
    
    def post(self, endpoint, json=None): 
        return self._make_request("POST", endpoint, json=json)

api = ApiClient(API_BASE_URL)

# --- SECURITY CHECK ---
if 'token' not in st.session_state:
    st.warning("Please login first")
    st.stop()

# --- DATA LOADING FUNCTIONS ---
def load_data():
    """Load all dashboard data"""
    with st.spinner("Loading your dashboard..."):
        # Load user profile
        user_response = api.get("/users/me")
        user_data = user_response.json() if user_response and user_response.status_code == 200 else {}
        
        # Load medications
        meds_response = api.get("/medications/")
        medications = meds_response.json() if meds_response and meds_response.status_code == 200 else []
        
        # Load appointments
        today = date.today().isoformat()
        next_week = (date.today() + timedelta(days=7)).isoformat()
        apps_response = api.get(f"/appointments/?start_date={today}&end_date={next_week}")
        appointments = apps_response.json() if apps_response and apps_response.status_code == 200 else []
        
        # Load health tip
        tip_response = api.get("/tips/random")
        health_tip = tip_response.json() if tip_response and tip_response.status_code == 200 else None
        
        # Load medication log
        log_response = api.get(f"/medications/log/{today}")
        taken_meds = log_response.json() if log_response and log_response.status_code == 200 else []
        
        return user_data, medications, appointments, health_tip, taken_meds

# --- MAIN DASHBOARD ---
def main():
    # Load data
    user_data, medications, appointments, health_tip, taken_meds = load_data()
    
    # Display live clock
    current_time = datetime.now().strftime("%I:%M:%S %p")
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    
    st.markdown(f"""
    <div style="text-align: right; margin-bottom: 1rem;">
        <div style="font-size: 2rem; font-weight: bold; color: #0068c9;">{current_time}</div>
        <div style="font-size: 1rem; color: #555;">{current_date}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome message
    user_name = user_data.get('full_name', 'User').split(' ')[0] if user_data else 'User'
    st.header(f"👋 Welcome Back, {user_name}!")
    
    # Today's summary cards
    st.subheader("Today's Summary")
    col1, col2, col3 = st.columns(3)
    
    # Count today's medications
    active_meds = [m for m in medications if m.get('is_active', True)]
    meds_taken = len(taken_meds)
    
    with col1:
        st.info("#### 💊 Medications")
        st.write(f"**{meds_taken} / {len(active_meds)}** taken today")
    
    with col2:
        # Count today's appointments
        today_apps = [app for app in appointments if 'appointment_datetime' in app 
                     and datetime.fromisoformat(app['appointment_datetime'].replace('Z', '+00:00')).date() == date.today()]
        st.info("#### 🗓️ Appointments")
        st.write(f"**{len(today_apps)}** today")
    
    with col3:
        st.info("#### 💡 Health Tip")
        tip_content = health_tip['content'] if health_tip else "Stay hydrated and take your medications on time."
        st.write(tip_content[:50] + "..." if len(tip_content) > 50 else tip_content)
    
    st.divider()
    
    # Quick actions
    st.write("### ⚡ Quick Actions")
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("💊 Add Medication", use_container_width=True):
            st.session_state.current_page = "Medications"
            st.rerun()
    
    with action_col2:
        if st.button("🗓️ Schedule Appointment", use_container_width=True):
            st.session_state.current_page = "Appointments"
            st.rerun()
    
    with action_col3:
        if st.button("📞 Add Contact", use_container_width=True):
            st.session_state.current_page = "Contacts"
            st.rerun()
    
    st.divider()
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

if __name__ == "__main__":
    main()
