# pages/Dashboard.py

import streamlit as st
import requests
import pytz
from datetime import datetime

# --- API Base URL ---
API_BASE_URL = "https://health-companion-backend-44ug.onrender.com"

# --- Page Config ---
st.set_page_config(page_title="Dashboard | Health Companion", page_icon="📊", layout="wide")

# --- Check if user is logged in ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("⚠️ Please log in to access the Dashboard.")
    st.stop()

# --- Get Token ---
token = st.session_state.get("token", None)

# --- Fetch Profile Data ---
user_data = {}
if token:
    try:
        response = requests.get(f"{API_BASE_URL}/user/profile", headers={"Authorization": f"Bearer {token}"})
        if response.status_code == 200:
            user_data = response.json()
        else:
            st.warning("⚠️ Failed to fetch profile data.")
    except Exception as e:
        st.error(f"Error fetching profile: {e}")

# --- Header Section ---
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("<h2>📊 Dashboard</h2>", unsafe_allow_html=True)
    if user_data:
        st.markdown(f"👋 Welcome, **{user_data.get('name', 'User')}**!")

with col2:
    india_tz = pytz.timezone("Asia/Kolkata")
    current_time = datetime.now(india_tz).strftime("%d-%m-%Y %I:%M %p")
    st.markdown(f"<div style='text-align:right; font-size:16px;'>🕒 {current_time}</div>", unsafe_allow_html=True)

st.markdown("---")

# --- Dashboard Stats ---
colA, colB, colC = st.columns(3)

with colA:
    st.metric("👤 Name", user_data.get("name", "N/A"))

with colB:
    st.metric("📧 Email", user_data.get("email", "N/A"))

with colC:
    st.metric("📅 Joined", user_data.get("created_at", "N/A"))

st.markdown("---")

# --- Quick Links / Features ---
st.subheader("🚀 Quick Actions")
quick1, quick2, quick3, quick4 = st.columns(4)

with quick1:
    if st.button("💊 My Medications"):
        st.switch_page("pages/Meds.py")

with quick2:
    if st.button("📅 Appointments"):
        st.switch_page("pages/Appointments.py")

with quick3:
    if st.button("📞 Contacts"):
        st.switch_page("pages/Contacts.py")

with quick4:
    if st.button("📄 Reports"):
        st.switch_page("pages/Reports.py")

