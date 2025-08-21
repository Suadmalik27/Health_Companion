# frontend/pages/2_Medications.py (100% Complete and Fully Updated)

import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURATION & API CLIENT ---
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
st.set_page_config(page_title="My Medications", layout="wide")

# --- MEDICATION PAGE CONTENT ---
st.header("💊 My Medications")
st.write("Manage your daily medication schedule here. Add photos to easily identify your medicines.")

# --- ADD NEW MEDICATION FORM ---
with st.expander("➕ Add New Medication"):
    with st.form("new_med_form", clear_on_submit=True):
        name = st.text_input("Medication Name", placeholder="e.g., Vitamin D")
        dosage = st.text_input("Dosage", placeholder="e.g., 1 tablet")
        timing = st.time_input("Time to Take")
        if st.form_submit_button("Add Medication", use_container_width=True):
            if not name or not dosage:
                st.warning("Please provide a name and dosage.")
            else:
                with st.spinner("Adding..."):
                    response = api.post("/medications/", json={"name": name, "dosage": dosage, "timing": timing.strftime("%H:%M:%S")})
                if response and response.status_code == 201:
                    st.success("Medication added successfully!"); st.rerun()
                else:
                    st.error("Failed to add medication.")

# --- DISPLAY ACTIVE MEDICATIONS ---
st.subheader("Your Active Medications")

with st.spinner("Loading medications..."):
    response = api.get("/medications/")

if response and response.status_code == 200:
    all_meds = sorted(response.json(), key=lambda x: datetime.strptime(x['timing'], '%H:%M:%S').time())
    active_meds = [m for m in all_meds if m.get('is_active', True)]
    inactive_meds = [m for m in all_meds if not m.get('is_active', True)]

    if not active_meds:
        st.info("You have no active medications. Add one using the form above.")

    for med in active_meds:
        with st.container(border=True):
            col1, col2 = st.columns([1, 4])

            with col1:
                pfp_url = med.get("photo_url")
                if pfp_url:
                    full_image_url = f"{API_BASE_URL}/{pfp_url}"
                    st.image(full_image_url, width=120)
                else:
                    st.image("https://via.placeholder.com/120x120.png?text=No+Photo", width=120)

            with col2:
                if st.session_state.get('editing_med_id') == med['id']:
                    with st.form(key=f"edit_form_{med['id']}"):
                        st.subheader(f"Editing: {med['name']}")
                        new_name = st.text_input("Name", value=med['name'])
                        new_dosage = st.text_input("Dosage", value=med['dosage'])
                        new_timing = st.time_input("Time", value=datetime.strptime(med['timing'], '%H:%M:%S').time())
                        c1_form, c2_form = st.columns(2)
                        with c1_form:
                            if st.form_submit_button("Save Changes", use_container_width=True):
                                with st.spinner("Saving..."):
                                    update_data = {"name": new_name, "dosage": new_dosage, "timing": new_timing.strftime("%H:%M:%S")}
                                    put_response = api.put(f"/medications/{med['id']}", json=update_data)
                                if put_response and put_response.status_code == 200:
                                    st.success("Medication updated!"); del st.session_state['editing_med_id']; st.rerun()
                                else:
                                    st.error("Failed to update medication.")
                        with c2_form:
                            if st.form_submit_button("Cancel", type="secondary", use_container_width=True):
                                del st.session_state['editing_med_id']; st.rerun()
                
                elif st.session_state.get('uploading_photo_for_med_id') == med['id']:
                    st.subheader(f"Change Photo for: {med['name']}")
                    uploaded_file = st.file_uploader("Upload a new photo", type=["png", "jpg", "jpeg"], key=f"uploader_{med['id']}")
                    if uploaded_file:
                        with st.spinner("Uploading..."):
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                            upload_response = requests.put(f"{API_BASE_URL}/medications/{med['id']}/photo", headers=api._get_headers(), files=files)
                        if upload_response and upload_response.status_code == 200:
                            st.success("Photo updated!"); del st.session_state['uploading_photo_for_med_id']; st.rerun()
                        else:
                            st.error("Failed to upload photo.")
                    if st.button("Cancel", key=f"cancel_upload_{med['id']}", use_container_width=True, type="secondary"):
                        del st.session_state['uploading_photo_for_med_id']; st.rerun()

                else:
                    st.subheader(med['name'])
                    st.write(f"**Dosage:** {med['dosage']} at **{datetime.strptime(med['timing'], '%H:%M:%S').strftime('%I:%M %p')}**")
                    btn_cols = st.columns(4)
                    with btn_cols[0]:
                        if st.button("Edit Details", key=f"edit_med_{med['id']}", use_container_width=True):
                            st.session_state.editing_med_id = med['id']; st.rerun()
                    with btn_cols[1]:
                        if st.button("Change Photo", key=f"photo_med_{med['id']}", use_container_width=True):
                            st.session_state.uploading_photo_for_med_id = med['id']; st.rerun()
                    with btn_cols[2]:
                        if st.button("To History", key=f"deact_med_{med['id']}", use_container_width=True, type="secondary"):
                            with st.spinner("Moving..."):
                                update_response = api.put(f"/medications/{med['id']}", json={"is_active": False})
                            if update_response and update_response.status_code == 200:
                                st.toast(f"'{med['name']}' moved to history."); st.rerun()
                            else:
                                st.error("Could not update medication status.")
                    with btn_cols[3]:
                        if st.button("Delete", key=f"del_med_{med['id']}", use_container_width=True, type="secondary"):
                            with st.spinner("Deleting..."):
                                delete_response = api.delete(f"/medications/{med['id']}")
                            if delete_response and delete_response.status_code == 204:
                                st.toast("Medication deleted."); st.rerun()
                            else:
                                st.error("Failed to delete medication.")

    # --- INACTIVE MEDICATIONS (HISTORY) ---
    st.divider()
    st.subheader("Medication History (Inactive)")
    if not inactive_meds:
        st.info("Your medication history is empty.")

    for med in inactive_meds:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.write(f"**{med['name']}** - {med['dosage']} (Taken at {datetime.strptime(med['timing'], '%H:%M:%S').strftime('%I:%M %p')})")
            with c2:
                if st.button("Move to Active", key=f"act_med_{med['id']}", use_container_width=True):
                    with st.spinner("Moving..."):
                        update_response = api.put(f"/medications/{med['id']}", json={"is_active": True})
                    if update_response and update_response.status_code == 200:
                        st.toast(f"'{med['name']}' is now active again."); st.rerun()
                    else:
                        st.error("Could not update medication status.")
else:
    st.error("Could not load your medication data from the server.")