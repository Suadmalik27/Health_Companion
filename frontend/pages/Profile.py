# frontend/pages/5_Profile.py

import streamlit as st
import requests
from datetime import datetime

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
    def put(self, endpoint, json=None): return self._make_request("PUT", endpoint, json=json)
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
    
    with st.expander("Change Profile Photo"):
        uploaded_file = st.file_uploader("Upload a new photo", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        if uploaded_file:
            if st.button("Upload New Photo", use_container_width=True):
                with st.spinner("Uploading..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    # Use a direct requests call for multipart file upload
                    upload_response = requests.put(f"{API_BASE_URL}/users/me/photo", headers=api._get_headers(), files=files)
                if upload_response and upload_response.status_code == 200:
                    st.success("Photo updated!"); st.rerun()
                else:
                    st.error("Failed to upload photo.")

with col2:
    with st.form("update_profile_form"):
        with st.container(border=True):
            st.subheader("📝 Update Your Information")
            full_name = st.text_input("Full Name", value=user_data.get('full_name', ''))
            dob_val = user_data.get('date_of_birth')
            dob_default = None
            if dob_val:
                try: dob_default = datetime.fromisoformat(dob_val).date()
                except (ValueError, TypeError): pass
            dob = st.date_input("Date of Birth", value=dob_default, max_value=datetime.today().date())
            address = st.text_area("Address", value=user_data.get('address', ''))

        with st.container(border=True):
            st.subheader("⚙️ Settings")
            current_theme_index = 1 if user_data.get('theme', 'light') == 'dark' else 0
            theme = st.radio(
                "App Theme", ["light", "dark"],
                captions=["☀️ Light Mode", "🌙 Dark Mode"],
                index=current_theme_index, horizontal=True,
                help="Choose a theme that's easy on your eyes."
            )

        if st.form_submit_button("Save Changes", use_container_width=True, type="primary"):
            with st.spinner("Saving..."):
                update_data = {
                    "full_name": full_name,
                    "date_of_birth": dob.isoformat() if dob else None,
                    "address": address,
                    "theme": theme
                }
                update_response = api.put("/users/me", json=update_data)
            if update_response and update_response.status_code == 200:
                # Update theme in session state immediately for instant change
                st.session_state['theme'] = theme
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
                        error_detail = "Incorrect current password or other error."
                        if pass_response is not None and pass_response.text:
                            try: error_detail = pass_response.json().get('detail', error_detail)
                            except: pass
                        st.error(f"Failed to update password: {error_detail}")

st.divider()
with st.container(border=True):
    st.subheader("🗑️ Delete Account")
    st.warning("DANGER ZONE: This is permanent. All your data will be erased.", icon="⚠️")
    agree_to_delete = st.checkbox("I understand and wish to permanently delete my account.", key="delete_confirm")
    if st.button("Yes, Delete My Account Permanently", type="primary", disabled=not agree_to_delete, use_container_width=True):
        with st.spinner("Deleting your account..."):
            delete_response = api.delete("/users/me")
        if delete_response and delete_response.status_code == 204:
            st.toast("Account deleted successfully."); st.session_state.clear(); st.rerun()
        else:
            st.error("Could not delete account. Please try again.")
