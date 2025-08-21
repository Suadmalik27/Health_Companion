# frontend/pages/5_Profile.py (100% Complete with Theme Selector)

import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURATION & API CLIENT ---
if "API_BASE_URL" in st.secrets:
    API_BASE_URL = st.secrets["API_BASE_URL"]
else:
    API_BASE_URL = "http://127.0.0.1:8000"

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
            return requests.request(method, f"{self.base_url}{endpoint}", headers=self._get_headers(), **kwargs)
        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Could not connect to the backend server."); return None
    def get(self, endpoint, params=None): return self._make_request("GET", endpoint, params=params)
    def put(self, endpoint, json=None, files=None): return self._make_request("PUT", endpoint, json=json, files=files)
    def delete(self, endpoint): return self._make_request("DELETE", endpoint)

api = ApiClient(API_BASE_URL)

# --- SECURITY CHECK ---
if 'token' not in st.session_state:
    st.warning("Please login first to access this page."); st.stop()

# --- PAGE CONFIG ---
st.set_page_config(page_title="My Profile", layout="wide")

# --- PROFILE PAGE CONTENT ---
st.header("My Profile & Settings")

with st.spinner("Loading your profile..."):
    response = api.get("/users/me")
    if not response or response.status_code != 200:
        st.error("Could not fetch your profile data."); st.stop()
    user_data = response.json()

# --- MAIN LAYOUT ---
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.subheader("👤 Your Photo")
    pfp_url = user_data.get("profile_picture_url")
    if pfp_url:
        full_image_url = f"{API_BASE_URL}/{pfp_url.replace('\\', '/')}"
        st.image(full_image_url, caption="Current Profile Picture")
    else:
        st.image("https://via.placeholder.com/300x300.png?text=No+Photo", caption="Upload a photo")
    with st.form("photo_upload_form", clear_on_submit=True):
        uploaded_file = st.file_uploader("Change your profile picture", type=["png", "jpg", "jpeg"])
        submitted = st.form_submit_button("Upload New Photo", use_container_width=True)
        if submitted and uploaded_file is not None:
            with st.spinner("Uploading..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                upload_response = requests.put(f"{API_BASE_URL}/users/me/photo", headers=api._get_headers(), files=files)
            if upload_response and upload_response.status_code == 200:
                st.success("Photo updated!"); st.rerun()
            else:
                st.error(f"Failed to upload photo.")
        elif submitted and uploaded_file is None:
            st.warning("Please select a file to upload.")

with col2:
    with st.form("update_profile_form"):
        with st.container(border=True):
            st.subheader("📝 Update Your Information")
            full_name = st.text_input("Full Name", value=user_data.get('full_name', ''))
            dob_val = user_data.get('date_of_birth')
            try:
                dob_default = datetime.fromisoformat(dob_val).date() if dob_val else None
            except:
                dob_default = None
            dob = st.date_input("Date of Birth", value=dob_default)
            address = st.text_area("Address", value=user_data.get('address', ''))

        with st.container(border=True):
            st.subheader("⚙️ Settings")
            time_format = st.radio(
                "Preferred Time Format", ("12h", "24h"),
                index=0 if user_data.get('time_format', '12h') == '12h' else 1,
                horizontal=True, help="Choose how times are displayed across the app."
            )
            st.divider()
            theme = st.radio(
                "App Theme", ["light", "dark"],
                captions=["☀️ Light Mode", "🌙 Dark Mode"],
                index=0 if user_data.get('theme', 'light') == 'light' else 1,
                horizontal=True, help="Choose a theme that's easy on your eyes."
            )

        if st.form_submit_button("Save Changes", use_container_width=True, type="primary"):
            with st.spinner("Saving..."):
                update_data = {
                    "full_name": full_name,
                    "date_of_birth": dob.isoformat() if dob else None,
                    "address": address,
                    "time_format": time_format,
                    "theme": theme
                }
                update_response = api.put("/users/me", json=update_data)
            if update_response and update_response.status_code == 200:
                st.success("Profile and settings updated successfully!"); st.rerun()
            else:
                st.error("Failed to update profile.")

    with st.container(border=True):
        st.subheader("🔑 Change Your Password")
        with st.form("update_password_form", clear_on_submit=True):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_new_password = st.text_input("Confirm New Password", type="password")
            if st.form_submit_button("Update Password", use_container_width=True):
                if not all([current_password, new_password, confirm_new_password]):
                    st.warning("Please fill in all password fields.")
                elif new_password != confirm_new_password:
                    st.error("New passwords do not match.")
                else:
                    with st.spinner("Updating password..."):
                        pass_response = api.put("/users/me/password", json={"current_password": current_password, "new_password": new_password})
                    if pass_response and pass_response.status_code == 200:
                        st.success("Password updated successfully!")
                    else:
                        error_detail = "An error occurred."
                        if pass_response and pass_response.text:
                            try:
                                error_detail = pass_response.json().get('detail', error_detail)
                            except:
                                pass
                        st.error(f"Failed to update password: {error_detail}")

st.divider()
with st.container(border=True):
    st.subheader("🗑️ Delete Account")
    st.warning("DANGER ZONE: This is permanent. All your data will be erased.", icon="⚠️")
    agree_to_delete = st.checkbox("I understand the consequences and wish to permanently delete my account.", key="delete_confirm")
    if st.button("Yes, Delete My Account Permanently", type="primary", disabled=not agree_to_delete, use_container_width=True):
        with st.spinner("Deleting your account..."):
            delete_response = api.delete("/users/me")
        if delete_response and delete_response.status_code == 204:
            st.toast("Account deleted successfully."); st.session_state.clear(); st.rerun()
        else:
            st.error("Could not delete account. Please try again.")