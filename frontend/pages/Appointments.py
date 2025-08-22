# frontend/pages/3_Appointments.py (Updated with Photo Upload Functionality)

import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURATION & API CLIENT ---
API_BASE_URL ="https://health-companion-backend-44ug.onrender.com"
if "API_BASE_URL" in st.secrets:
    API_BASE_URL = st.secrets["API_BASE_URL"]
else:
    API_BASE_URL = "http://127.0.0.1:8000"

# --- API CLIENT CLASS (Robust Version) ---
class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
    def _get_headers(self):
        token = st.session_state.get("token", None)
        if token: return {"Authorization": f"Bearer {token}"}
        return {}
    def _make_request(self, method, endpoint, **kwargs):
        try:
            return requests.request(method, f"{self.base_url}{endpoint}", headers=self._get_headers(), **kwargs)
        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Could not connect to the backend server."); return None
    def post(self, endpoint, json=None): return self._make_request("POST", endpoint, json=json)
    def get(self, endpoint, params=None): return self._make_request("GET", endpoint, params=params)
    def put(self, endpoint, json=None): return self._make_request("PUT", endpoint, json=json)
    def delete(self, endpoint): return self._make_request("DELETE", endpoint)

api = ApiClient(API_BASE_URL)

# --- SECURITY CHECK ---
if 'token' not in st.session_state:
    st.warning("Please login first to access this page."); st.stop()

# --- PAGE CONFIG ---
st.set_page_config(page_title="My Appointments", layout="wide")

# --- APPOINTMENTS PAGE CONTENT ---
st.header("🗓️ My Appointments")
st.write("Manage your doctor appointments here. Add photos to easily recognize your doctors.")

# --- ADD NEW APPOINTMENT FORM ---
with st.expander("➕ Add New Appointment"):
    with st.form("new_app_form", clear_on_submit=True):
        doctor_name = st.text_input("Doctor's Name*", placeholder="e.g., Dr. Smith")
        purpose = st.text_input("Purpose of Visit", placeholder="e.g., Annual Check-up")
        app_date = st.date_input("Appointment Date", min_value=datetime.today().date())
        app_time = st.time_input("Appointment Time")
        location = st.text_area("Clinic/Hospital Address")
        if st.form_submit_button("Add Appointment", use_container_width=True):
            if not doctor_name:
                st.warning("Please enter the doctor's name.")
            else:
                with st.spinner("Adding..."):
                    app_datetime = datetime.combine(app_date, app_time)
                    response = api.post("/appointments/", json={
                        "doctor_name": doctor_name, "purpose": purpose,
                        "appointment_datetime": app_datetime.isoformat(), "location": location
                    })
                if response and response.status_code == 201:
                    st.success("Appointment added successfully!"); st.rerun()
                else:
                    st.error("Failed to add appointment.")

# --- DISPLAY UPCOMING APPOINTMENTS ---
st.subheader("Upcoming Appointments")

with st.spinner("Loading appointments..."):
    response = api.get("/appointments/")

if response and response.status_code == 200:
    all_apps = response.json()
    now = datetime.now()
    upcoming_apps = sorted([app for app in all_apps if datetime.fromisoformat(app['appointment_datetime']) >= now], key=lambda x: x['appointment_datetime'])
    past_apps = sorted([app for app in all_apps if datetime.fromisoformat(app['appointment_datetime']) < now], key=lambda x: x['appointment_datetime'], reverse=True)

    if not upcoming_apps:
        st.info("You have no upcoming appointments. Add one using the form above.")

    for app in upcoming_apps:
        with st.container(border=True):
            col1, col2 = st.columns([1, 4])

            with col1:
                pfp_url = app.get("photo_url")
                if pfp_url:
                    full_image_url = f"{API_BASE_URL}/{pfp_url}"
                    st.image(full_image_url, width=120)
                else:
                    st.image("https://via.placeholder.com/120x120.png?text=No+Photo", width=120)

            with col2:
                app_dt = datetime.fromisoformat(app['appointment_datetime'])
                if st.session_state.get('editing_app_id') == app['id']:
                    # Edit details form
                    with st.form(key=f"edit_form_{app['id']}"):
                        st.subheader(f"Editing: {app['doctor_name']}")
                        new_doctor = st.text_input("Doctor's Name", value=app['doctor_name'])
                        new_purpose = st.text_input("Purpose", value=app.get('purpose', ''))
                        new_date = st.date_input("Date", value=app_dt.date())
                        new_time = st.time_input("Time", value=app_dt.time())
                        new_location = st.text_area("Location", value=app.get('location', ''))
                        c1_form, c2_form = st.columns(2)
                        with c1_form:
                            if st.form_submit_button("Save Changes", use_container_width=True):
                                with st.spinner("Saving..."):
                                    new_datetime = datetime.combine(new_date, new_time)
                                    update_data = {
                                        "doctor_name": new_doctor, "purpose": new_purpose,
                                        "appointment_datetime": new_datetime.isoformat(),
                                        "location": new_location
                                    }
                                    put_response = api.put(f"/appointments/{app['id']}", json=update_data)
                                if put_response and put_response.status_code == 200:
                                    st.success("Appointment updated!"); del st.session_state['editing_app_id']; st.rerun()
                                else:
                                    st.error("Failed to update appointment.")
                            
                            
                                
                                st.rerun()
                        with c2_form:
                            if st.form_submit_button("Cancel", type="secondary", use_container_width=True):
                                del st.session_state['editing_app_id']; st.rerun()

                elif st.session_state.get('uploading_photo_for_app_id') == app['id']:
                    # Photo upload UI
                    st.subheader(f"Change Photo for: {app['doctor_name']}")
                    uploaded_file = st.file_uploader("Upload a new photo", type=["png", "jpg", "jpeg"], key=f"uploader_{app['id']}")
                    if uploaded_file:
                        with st.spinner("Uploading..."):
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                            upload_response = requests.put(f"{API_BASE_URL}/appointments/{app['id']}/photo", headers=api._get_headers(), files=files)
                        if upload_response and upload_response.status_code == 200:
                            st.success("Photo updated!"); del st.session_state['uploading_photo_for_app_id']; st.rerun()
                        else:
                            st.error("Failed to upload photo.")
                    if st.button("Cancel", key=f"cancel_upload_{app['id']}", use_container_width=True, type="secondary"):
                        del st.session_state['uploading_photo_for_app_id']; st.rerun()

                else:
                    # Default display view
                    st.subheader(app['doctor_name'])
                    st.write(f"**On:** {app_dt.strftime('%A, %d %b %Y at %I:%M %p')}")
                    st.caption(f"Purpose: {app.get('purpose', 'N/A')} | Location: {app.get('location', 'N/A')}")
                    btn_cols = st.columns(3)
                    with btn_cols[0]:
                        if st.button("Edit Details", key=f"edit_app_{app['id']}", use_container_width=True):
                            st.session_state.editing_app_id = app['id']; st.rerun()
                    with btn_cols[1]:
                        if st.button("Change Photo", key=f"photo_app_{app['id']}", use_container_width=True):
                            st.session_state.uploading_photo_for_app_id = app['id']; st.rerun()
                    with btn_cols[2]:
                        if st.button("Delete", key=f"del_app_{app['id']}", use_container_width=True, type="secondary"):
                            with st.spinner("Deleting..."):
                                delete_response = api.delete(f"/appointments/{app['id']}")
                            if delete_response and delete_response.status_code == 204:
                                st.toast("Appointment deleted."); st.rerun()
                            else:
                                st.error("Failed to delete appointment.")
                         
                            st.rerun()

    # --- PAST APPOINTMENTS ---
    st.divider()
    st.subheader("Past Appointments")
    if not past_apps:
        st.info("You have no past appointments.")
    for app in past_apps:
        with st.container(border=True):
            app_dt = datetime.fromisoformat(app['appointment_datetime'])
            st.write(f"**{app['doctor_name']}** on **{app_dt.strftime('%d %b %Y, %I:%M %p')}**")
            st.caption(f"Purpose: {app.get('purpose', 'N/A')} | Location: {app.get('location', 'N/A')}")
else:
    st.error("Could not load your appointment data from the server.")
