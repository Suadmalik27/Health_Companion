# frontend/pages/Profile.py (Premium UI Version)
import streamlit as st
import requests
from datetime import datetime
import time

# --- CONFIGURATION & API CLIENT ---
API_BASE_URL = "https://health-companion-backend-44ug.onrender.com"

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
    
    def put(self, endpoint, json=None): 
        return self._make_request("PUT", endpoint, json=json)
    
    def delete(self, endpoint): 
        return self._make_request("DELETE", endpoint)

api = ApiClient(API_BASE_URL)

# --- SECURITY CHECK ---
if 'token' not in st.session_state:
    st.warning("Please login first to access this page.")
    st.stop()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="My Profile", 
    layout="wide",
    page_icon="👤"
)

# --- PREMIUM STYLING ---
st.markdown("""
<style>
/* Main Container Styling */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Card Styling */
.profile-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    padding: 2rem;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.settings-card {
    background: white;
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    border: 1px solid #e0e0e0;
}

.danger-card {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    color: white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

/* Form Elements */
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    border-radius: 10px;
    border: 2px solid #e0e0e0;
    padding: 12px;
}

.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

/* Buttons */
.stButton>button {
    border-radius: 10px;
    padding: 12px 24px;
    font-weight: 600;
    border: none;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

/* Radio Buttons */
.stRadio>div {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 10px;
    border: 2px solid #e0e0e0;
}

.stRadio>div:hover {
    border-color: #667eea;
}

/* Profile Photo */
.profile-photo-container {
    text-align: center;
    padding: 1rem;
}

.profile-photo {
    width: 200px;
    height: 200px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid white;
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

/* Section Headers */
.section-header {
    font-size: 1.5rem;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 3px solid #667eea;
}

/* Status Messages */
.success-message {
    background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}

.error-message {
    background: linear-gradient(135deg, #ff6b6b 0%, #c44d4d 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}

/* Loading Spinner */
.stSpinner>div>div {
    border-color: #667eea transparent transparent transparent;
}

/* Custom Checkbox */
.stCheckbox>label {
    font-weight: 600;
    color: #dc3545;
}

/* Responsive Design */
@media (max-width: 768px) {
    .profile-photo {
        width: 150px;
        height: 150px;
    }
}
</style>
""", unsafe_allow_html=True)

# --- PROFILE PAGE CONTENT ---
st.markdown("""
<div class="profile-card">
    <h1 style="margin: 0; color: white; font-size: 2.5rem;">👤 My Profile</h1>
    <p style="margin: 0; opacity: 0.9; font-size: 1.1rem;">Manage your personal information and preferences</p>
</div>
""", unsafe_allow_html=True)

# Load user data
with st.spinner("Loading your profile..."):
    response = api.get("/users/me")
    if not response or response.status_code != 200:
        st.error("Could not fetch your profile data. Please try refreshing.")
        st.stop()
    user_data = response.json()

# --- MAIN LAYOUT ---
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    # Profile Photo Section
    st.markdown("""
    <div class="settings-card">
        <h3 style="margin: 0 0 1rem 0; color: #2c3e50;">📸 Profile Photo</h3>
    """, unsafe_allow_html=True)
    
    pfp_url = user_data.get("profile_picture_url")
    if pfp_url:
        full_image_url = f"{API_BASE_URL}/{pfp_url.replace('\\', '/')}"
        st.markdown(f"""
        <div class="profile-photo-container">
            <img src="{full_image_url}" class="profile-photo" alt="Profile Picture">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="profile-photo-container">
            <img src="https://via.placeholder.com/200x200/667eea/ffffff?text=👤" class="profile-photo" alt="Default Profile">
        </div>
        """, unsafe_allow_html=True)
    
    # Photo Upload
    with st.expander("🔄 Change Photo", expanded=False):
        uploaded_file = st.file_uploader(
            "Choose a new profile photo", 
            type=["png", "jpg", "jpeg"], 
            help="Select a clear photo for better recognition"
        )
        if uploaded_file and st.button("📤 Upload Photo", use_container_width=True):
            with st.spinner("Uploading your photo..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                upload_response = requests.put(
                    f"{API_BASE_URL}/users/me/photo", 
                    headers=api._get_headers(), 
                    files=files
                )
            if upload_response and upload_response.status_code == 200:
                st.markdown("""
                <div class="success-message">
                    ✅ Photo updated successfully!
                </div>
                """, unsafe_allow_html=True)
                time.sleep(2)
                st.rerun()
            else:
                st.markdown("""
                <div class="error-message">
                    ❌ Failed to upload photo. Please try again.
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    # Personal Information Form
    st.markdown("""
    <div class="settings-card">
        <h3 style="margin: 0 0 1rem 0; color: #2c3e50;">📝 Personal Information</h3>
    """, unsafe_allow_html=True)
    
    with st.form("update_profile_form"):
        col_a, col_b = st.columns(2)
        
        with col_a:
            full_name = st.text_input(
                "Full Name *", 
                value=user_data.get('full_name', ''),
                placeholder="Enter your full name",
                help="Your complete name as you'd like it to appear"
            )
        
        with col_b:
            dob_val = user_data.get('date_of_birth')
            dob_default = None
            if dob_val:
                try: 
                    dob_default = datetime.fromisoformat(dob_val).date()
                except (ValueError, TypeError): 
                    pass
            dob = st.date_input(
                "Date of Birth", 
                value=dob_default, 
                max_value=datetime.today().date(),
                help="Your birth date for personalized experience"
            )
        
        address = st.text_area(
            "Address", 
            value=user_data.get('address', ''),
            placeholder="Enter your complete address",
            help="Your residential address for emergency purposes",
            height=100
        )
        
        if st.form_submit_button("💾 Save Personal Info", use_container_width=True, type="primary"):
            if not full_name:
                st.markdown("""
                <div class="error-message">
                    ❌ Please provide your full name.
                </div>
                """, unsafe_allow_html=True)
            else:
                with st.spinner("Saving your information..."):
                    update_data = {
                        "full_name": full_name,
                        "date_of_birth": dob.isoformat() if dob else None,
                        "address": address
                    }
                    update_response = api.put("/users/me", json=update_data)
                if update_response and update_response.status_code == 200:
                    st.markdown("""
                    <div class="success-message">
                        ✅ Personal information updated successfully!
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(2)
                    st.rerun()
                else:
                    st.markdown("""
                    <div class="error-message">
                        ❌ Failed to update information. Please try again.
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # App Preferences
    st.markdown("""
    <div class="settings-card">
        <h3 style="margin: 0 0 1rem 0; color: #2c3e50;">⚙️ App Preferences</h3>
    """, unsafe_allow_html=True)
    
    with st.form("preferences_form"):
        col_x, col_y = st.columns(2)
        
        with col_x:
            current_theme = user_data.get('theme', 'light')
            theme = st.radio(
                "🎨 App Theme",
                options=["light", "dark"],
                captions=["☀️ Light Mode - Bright and clear", "🌙 Dark Mode - Easy on eyes"],
                index=0 if current_theme == 'light' else 1,
                help="Choose the visual theme that suits your preference"
            )
        
        with col_y:
            current_time_format = user_data.get('time_format', '12h')
            time_format = st.radio(
                "⏰ Time Format",
                options=["12h", "24h"],
                captions=["12-hour (AM/PM)", "24-hour format"],
                index=0 if current_time_format == '12h' else 1,
                help="Choose how time is displayed throughout the app"
            )
        
        if st.form_submit_button("💾 Save Preferences", use_container_width=True, type="primary"):
            with st.spinner("Saving preferences..."):
                pref_response = api.put("/users/me", json={
                    "theme": theme,
                    "time_format": time_format
                })
            if pref_response and pref_response.status_code == 200:
                st.session_state['theme'] = theme
                st.session_state['time_format'] = time_format
                st.markdown("""
                <div class="success-message">
                    ✅ Preferences saved successfully!
                </div>
                """, unsafe_allow_html=True)
                time.sleep(2)
                st.rerun()
            else:
                st.markdown("""
                <div class="error-message">
                    ❌ Failed to save preferences. Please try again.
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Password Change Section
st.markdown("""
<div class="settings-card">
    <h3 style="margin: 0 0 1rem 0; color: #2c3e50;">🔒 Security Settings</h3>
""", unsafe_allow_html=True)

with st.form("update_password_form", clear_on_submit=True):
    st.write("Change your account password:")
    
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        current_password = st.text_input(
            "Current Password *", 
            type="password",
            placeholder="Enter current password",
            help="Your current account password"
        )
    
    with col_p2:
        new_password = st.text_input(
            "New Password *", 
            type="password",
            placeholder="Enter new password",
            help="Choose a strong, unique password"
        )
    
    confirm_new_password = st.text_input(
        "Confirm New Password *", 
        type="password",
        placeholder="Confirm new password",
        help="Re-enter your new password to confirm"
    )
    
    if st.form_submit_button("🔑 Update Password", use_container_width=True, type="primary"):
        if not all([current_password, new_password, confirm_new_password]):
            st.markdown("""
            <div class="error-message">
                ❌ Please fill in all password fields.
            </div>
            """, unsafe_allow_html=True)
        elif new_password != confirm_new_password:
            st.markdown("""
            <div class="error-message">
                ❌ New passwords do not match.
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.spinner("Updating password..."):
                pass_response = api.put("/users/me/password", json={
                    "current_password": current_password, 
                    "new_password": new_password
                })
            if pass_response and pass_response.status_code == 200:
                st.markdown("""
                <div class="success-message">
                    ✅ Password updated successfully!
                </div>
                """, unsafe_allow_html=True)
            else:
                error_detail = "Incorrect current password or server error."
                if pass_response is not None and pass_response.text:
                    try: 
                        error_detail = pass_response.json().get('detail', error_detail)
                    except: 
                        pass
                st.markdown(f"""
                <div class="error-message">
                    ❌ Failed to update password: {error_detail}
                </div>
                """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Account Deletion Section
st.markdown("""
<div class="danger-card">
    <h3 style="margin: 0 0 1rem 0; color: white;">⚠️ Danger Zone</h3>
    <p style="margin: 0 0 1rem 0; opacity: 0.9;">
        This action cannot be undone. All your data will be permanently deleted.
    </p>
""", unsafe_allow_html=True)

agree_to_delete = st.checkbox(
    "I understand the consequences and wish to permanently delete my account",
    key="delete_confirm"
)

if st.button("🗑️ Delete My Account", type="primary", disabled=not agree_to_delete, use_container_width=True):
    with st.spinner("Deleting your account..."):
        delete_response = api.delete("/users/me")
    if delete_response and delete_response.status_code == 204:
        st.markdown("""
        <div class="success-message">
            ✅ Account deleted successfully. Redirecting...
        </div>
        """, unsafe_allow_html=True)
        time.sleep(3)
        st.session_state.clear()
        st.rerun()
    else:
        st.markdown("""
        <div class="error-message">
            ❌ Could not delete account. Please try again.
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; color: #6c757d;">
    <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 2rem 0;">
    <p>🩺 Health Companion • Your trusted medical assistant</p>
</div>
""", unsafe_allow_html=True)
