# frontend/pages/Appointments.py (VERSION 2.1 - TIMEZONE IMPORT FIX)

import streamlit as st
from streamlit_cookies_manager import CookieManager
from datetime import datetime, time, date
import pytz # <-- YEH FINAL FIX HAI

from auth.service import (
    TOKEN_COOKIE_NAME,
    get_appointments,
    add_appointment,
    delete_appointment
)
from components.sidebar import authenticated_sidebar

# --- 1. PAGE CONFIGURATION & AUTHENTICATION ---
st.set_page_config(page_title="Manage Appointments", page_icon="🗓️", layout="wide")

cookies = CookieManager()
if not cookies.ready():
    st.spinner("Initializing...")
    st.stop()

token = cookies.get(TOKEN_COOKIE_NAME)
if not token:
    st.warning("🔒 You are not logged in. Please log in to continue.")
    st.stop()

authenticated_sidebar(cookies)

# Session state ka istemal delete confirmation ke liye
if 'confirming_delete_appt_id' not in st.session_state:
    st.session_state.confirming_delete_appt_id = None

# --- 2. DATA FETCHING ---
@st.cache_data(show_spinner="Loading your appointments...")
def load_appointments_data(token_param):
    is_success, appts_data = get_appointments(token_param)
    if not is_success:
        st.error(f"Could not load appointments: {appts_data}")
        return []
    # Sort appointments by date
    if appts_data:
        appts_data.sort(key=lambda x: x['appointment_datetime'], reverse=True)
    return appts_data

appointments = load_appointments_data(token)

# --- 3. PAGE UI ---
st.title("🗓️ Manage Your Appointments")
st.markdown("Yahan aap apne doctor ke appointments ko jod ya hata sakte hain.")
st.markdown("---")

# Naya appointment add karne ka form
with st.expander("➕ Add a New Appointment", expanded=True):
    with st.form("new_appointment_form", clear_on_submit=True):
        st.subheader("New Appointment Details")
        doc_name = st.text_input("Doctor's Name", placeholder="e.g., Dr. Gupta")
        
        col1, col2 = st.columns(2)
        with col1:
            appt_date = st.date_input("Date of Appointment", min_value=date.today())
        with col2:
            appt_time = st.time_input("Time of Appointment", value=time(10, 30))
        
        appt_location = st.text_input("Location / Clinic Address", placeholder="e.g., City Hospital, 123 Main St")
        appt_purpose = st.text_area("Purpose of Visit", placeholder="e.g., Annual Check-up, Follow-up")

        submitted = st.form_submit_button("Add Appointment")
        if submitted:
            if not doc_name or not appt_date or not appt_time:
                st.warning("Please fill in the Doctor's Name, Date, and Time.")
            else:
                combined_datetime = datetime.combine(appt_date, appt_time)
                # Assume the user is entering time in their local timezone (IST)
                # We need to make it timezone-aware before sending to backend
                local_tz = pytz.timezone('Asia/Kolkata')
                aware_datetime = local_tz.localize(combined_datetime)
                iso_datetime_str = aware_datetime.isoformat()

                payload = {
                    "doctor_name": doc_name,
                    "appointment_datetime": iso_datetime_str,
                    "location": appt_location,
                    "purpose": appt_purpose
                }
                is_success, message = add_appointment(token, payload)
                if is_success:
                    st.success("Appointment added successfully!")
                    # --- YEH SABSE ZAROORI FIX HAI ---
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"Failed to add appointment: {message}")

st.markdown("---")

# Maujooda appointments ki list
st.header("Your Upcoming Appointments")
if not appointments:
    st.info("You haven't added any appointments yet. Use the form above to add one.")
else:
    for appt in appointments:
        appt_id = appt['id']
        with st.container(border=True):
            if st.session_state.confirming_delete_appt_id == appt_id:
                st.warning(f"**Are you sure you want to delete the appointment with Dr. {appt['doctor_name']}?**")
                del_cols = st.columns([1, 1, 3])
                with del_cols[0]:
                    if st.button("✅ Yes, Delete", key=f"conf_appt_{appt_id}", use_container_width=True, type="primary"):
                        del_success, del_message = delete_appointment(token, appt_id)
                        st.session_state.confirming_delete_appt_id = None
                        if del_success:
                            st.success(del_message)
                            # --- YEH BHI ZAROORI FIX HAI ---
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(del_message)
                with del_cols[1]:
                    if st.button("❌ No, Cancel", key=f"cancel_appt_{appt_id}", use_container_width=True):
                        st.session_state.confirming_delete_appt_id = None
                        st.rerun()
            else:
                main_cols = st.columns([3, 1])
                with main_cols[0]:
                    # Convert string from backend to datetime object
                    appt_dt_utc = datetime.fromisoformat(appt['appointment_datetime'])
                    # Convert to IST for display
                    appt_dt_ist = appt_dt_utc.astimezone(pytz.timezone('Asia/Kolkata'))

                    st.subheader(f"Dr. {appt['doctor_name']}")
                    st.markdown(f"**When:** {appt_dt_ist.strftime('%A, %B %d, %Y at %I:%M %p')}")
                    if appt.get('location'):
                        st.write(f"**Where:** {appt['location']}")
                    if appt.get('purpose'):
                        st.write(f"**Purpose:** {appt['purpose']}")
                with main_cols[1]:
                    if st.button("Delete Appointment", key=f"del_appt_{appt_id}", use_container_width=True):
                        st.session_state.confirming_delete_appt_id = appt_id
                        st.rerun()

