# frontend/pages/Profile.py

import streamlit as st
import requests
from datetime import datetime, date
from PIL import Image
import io
import base64
import os

# Page configuration
st.set_page_config(
    page_title="Profile - Health Companion",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get API URL from secrets with fallback
try:
    API_BASE_URL = st.secrets["API_BASE_URL"]
except:
    API_BASE_URL = "https://health-companion-backend-44ug.onrender.com"

# Custom CSS for styling
def local_css():
    st.markdown("""
    <style>
    .profile-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    .profile-header {
        display: flex;
        align-items: center;
        gap: 2rem;
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 2px solid #f0f0f0;
    }
    .profile-image-container {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
    }
    .profile-image {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    .profile-image-placeholder {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        color: white;
        border: 4px solid #667eea;
    }
    .profile-info {
        flex: 1;
    }
    .profile-name {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0 0 0.5rem 0;
    }
    .profile-email {
        color: #666;
        font-size: 1.1rem;
        margin: 0 0 1rem 0;
    }
    .profile-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    .stat-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        border-left: 4px solid #667eea;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
        margin: 0;
    }
    .stat-label {
        color: #666;
        margin: 0;
    }
    .preference-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border-left: 4px solid #4CAF50;
    }
    .danger-zone {
        background: #fff5f5;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #ffebee;
        margin-top: 2rem;
    }
    .danger-zone h3 {
        color: #c62828;
        margin-top: 0;
    }
    .form-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .theme-option {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-bottom: 0.5rem;
    }
    .theme-option:hover {
        border-color: #667eea;
        background: #f0f4ff;
    }
    .theme-option.selected {
        border-color: #667eea;
        background: #e8f0ff;
    }
    .theme-preview {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .theme-light {
        background: white;
        border: 2px solid #e0e0e0;
    }
    .theme-dark {
        background: #2c3e50;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

def get_auth_headers():
    """Get authorization headers with access token"""
    if 'access_token' not in st.session_state:
        return None
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

def fetch_user_data():
    """Fetch current user's data"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    try:
        response = requests.get(f"{API_BASE_URL}/users/me", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        st.error(f"Failed to fetch user data: {response.status_code}")
        return None
    except Exception as e:
        st.error(f"Error fetching user data: {str(e)}")
        return None

def fetch_medications():
    """Fetch user's medications for stats"""
    headers = get_auth_headers()
    if not headers:
        return []
    
    try:
        response = requests.get(f"{API_BASE_URL}/medications/", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def fetch_appointments():
    """Fetch user's appointments for stats"""
    headers = get_auth_headers()
    if not headers:
        return []
    
    try:
        response = requests.get(f"{API_BASE_URL}/appointments/", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def fetch_contacts():
    """Fetch user's contacts for stats"""
    headers = get_auth_headers()
    if not headers:
        return []
    
    try:
        response = requests.get(f"{API_BASE_URL}/contacts/", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def update_user_profile(user_data):
    """Update user profile information"""
    headers = get_auth_headers()
    if not headers:
        return False, "Not authenticated"
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/users/me",
            json=user_data,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json().get("detail", "Failed to update profile")
    except Exception as e:
        return False, f"Error: {str(e)}"

def update_user_password(password_data):
    """Update user password"""
    headers = get_auth_headers()
    if not headers:
        return False, "Not authenticated"
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/users/me/password",
            json=password_data,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json().get("detail", "Failed to update password")
    except Exception as e:
        return False, f"Error: {str(e)}"

def upload_profile_photo(file):
    """Upload profile photo"""
    headers = get_auth_headers()
    if not headers:
        return False
    
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.put(
            f"{API_BASE_URL}/users/me/photo",
            files=files,
            headers=headers,
            timeout=30  # Longer timeout for file uploads
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error uploading photo: {str(e)}")
        return False

def delete_user_account():
    """Delete user account"""
    headers = get_auth_headers()
    if not headers:
        return False
    
    try:
        response = requests.delete(
            f"{API_BASE_URL}/users/me",
            headers=headers,
            timeout=10
        )
        return response.status_code == 204
    except Exception as e:
        st.error(f"Error deleting account: {str(e)}")
        return False

# Check if user is logged in
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access your profile")
    st.stop()

# Initialize session state
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "profile"

# Fetch data
user_data = fetch_user_data()
medications = fetch_medications()
appointments = fetch_appointments()
contacts = fetch_contacts()

# Page header
st.title("👤 User Profile")
st.markdown("Manage your personal information and account settings")

if not user_data:
    st.error("Failed to load user data. Please try refreshing the page.")
    st.stop()

# Profile Header
st.markdown('<div class="profile-container">', unsafe_allow_html=True)
st.markdown('<div class="profile-header">', unsafe_allow_html=True)

# Profile Image
st.markdown('<div class="profile-image-container">', unsafe_allow_html=True)

if user_data and user_data.get('profile_picture_url'):
    try:
        photo_url = user_data['profile_picture_url']
        if photo_url.startswith('/'):
            photo_url = f"{API_BASE_URL}{photo_url}"
        
        response = requests.get(photo_url, timeout=10)
        if response.status_code == 200:
            img = Image.open(io.BytesIO(response.content))
            st.image(img, use_column_width=False, width=120, output_format='auto')
        else:
            st.markdown('<div class="profile-image-placeholder">👤</div>', unsafe_allow_html=True)
    except Exception as e:
        st.markdown('<div class="profile-image-placeholder">👤</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="profile-image-placeholder">👤</div>', unsafe_allow_html=True)

# Photo upload
photo_file = st.file_uploader("Change profile photo", type=['jpg', 'jpeg', 'png'], key="profile_photo")
if photo_file:
    if upload_profile_photo(photo_file):
        st.success("Profile photo updated successfully!")
        st.rerun()
    else:
        st.error("Failed to upload profile photo")

st.markdown('</div>', unsafe_allow_html=True)  # Close profile-image-container

# Profile Info
st.markdown('<div class="profile-info">', unsafe_allow_html=True)
st.markdown(f'<h1 class="profile-name">{user_data.get("full_name", "User")}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="profile-email">📧 {user_data.get("email", "")}</p>', unsafe_allow_html=True)

# User Stats
st.markdown('<div class="profile-stats">', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    active_meds = len([m for m in medications if m.get('is_active', True)])
    st.markdown(f"""
    <div class="stat-card">
        <h3 class="stat-number">{active_meds}</h3>
        <p class="stat-label">Active Medications</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <h3 class="stat-number">{len(appointments)}</h3>
        <p class="stat-label">Appointments</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <h3 class="stat-number">{len(contacts)}</h3>
        <p class="stat-label">Emergency Contacts</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    account_age = "Today"
    if user_data.get('date_joined'):
        account_age = "1 day"  # Simplified for demo
    st.markdown(f"""
    <div class="stat-card">
        <h3 class="stat-number">{account_age}</h3>
        <p class="stat-label">Account Age</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close profile-stats
st.markdown('</div>', unsafe_allow_html=True)  # Close profile-info
st.markdown('</div>', unsafe_allow_html=True)  # Close profile-header

# Tab navigation
tab1, tab2, tab3 = st.tabs(["📝 Profile Information", "⚙️ Preferences", "🚨 Account Settings"])

with tab1:
    st.markdown("### Personal Information")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input(
                "Full Name",
                value=user_data.get('full_name', ''),
                placeholder="Enter your full name"
            )
            email = st.text_input(
                "Email Address",
                value=user_data.get('email', ''),
                disabled=True,
                help="Email cannot be changed"
            )
        
        with col2:
            date_of_birth = st.date_input(
                "Date of Birth",
                value=datetime.strptime(user_data.get('date_of_birth', '2000-01-01'), '%Y-%m-%d').date() if user_data.get('date_of_birth') else date(2000, 1, 1),
                max_value=date.today()
            )
            address = st.text_area(
                "Address",
                value=user_data.get('address', ''),
                placeholder="Enter your complete address",
                height=100
            )
        
        submitted = st.form_submit_button("💾 Update Profile")
        
        if submitted:
            if not full_name:
                st.error("Please provide your full name")
            else:
                update_data = {
                    "full_name": full_name,
                    "date_of_birth": date_of_birth.isoformat(),
                    "address": address
                }
                
                success, result = update_user_profile(update_data)
                if success:
                    st.success("Profile updated successfully!")
                    st.rerun()
                else:
                    st.error(f"Error updating profile: {result}")

with tab2:
    st.markdown("### Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🕒 Time Format")
        time_format = st.radio(
            "Select your preferred time format:",
            ["12-hour", "24-hour"],
            index=0 if user_data.get('time_format', '12h') == '12h' else 1,
            key="time_format"
        )
    
    with col2:
        st.markdown("#### 🎨 Theme Preference")
        theme = st.radio(
            "Select your preferred theme:",
            ["Light", "Dark"],
            index=0 if user_data.get('theme', 'light') == 'light' else 1,
            key="theme"
        )
    
    if st.button("💾 Save Preferences", key="save_prefs"):
        prefs_data = {
            "time_format": '12h' if time_format == '12-hour' else '24h',
            "theme": theme.lower()
        }
        
        success, result = update_user_profile(prefs_data)
        if success:
            st.success("Preferences saved successfully!")
            # Update session state
            st.session_state.time_format = prefs_data['time_format']
            st.session_state.theme = prefs_data['theme']
            st.rerun()
        else:
            st.error(f"Error saving preferences: {result}")

with tab3:
    st.markdown("### Change Password")
    
    with st.form("password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submitted = st.form_submit_button("🔒 Change Password")
        
        if submitted:
            if not current_password or not new_password or not confirm_password:
                st.error("Please fill in all password fields")
            elif new_password != confirm_password:
                st.error("New passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters long")
            else:
                password_data = {
                    "current_password": current_password,
                    "new_password": new_password
                }
                
                success, result = update_user_password(password_data)
                if success:
                    st.success("Password changed successfully!")
                else:
                    st.error(f"Error changing password: {result}")
    
    st.markdown("---")
    st.markdown("### 🚨 Danger Zone")
    
    st.markdown("""
    <div class="danger-zone">
        <h3>⚠️ Delete Account</h3>
        <p>Permanently delete your account and all associated data. This action cannot be undone.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗑️ Delete My Account", type="secondary"):
        st.warning("Are you sure you want to delete your account? This action cannot be undone.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Delete My Account", type="primary"):
                if delete_user_account():
                    st.success("Account deleted successfully")
                    # Clear session and redirect to login
                    st.session_state.logged_in = False
                    st.session_state.access_token = None
                    st.session_state.user_email = None
                    st.rerun()
                else:
                    st.error("Failed to delete account")
        
        with col2:
            if st.button("❌ Cancel", type="secondary"):
                st.rerun()

st.markdown('</div>', unsafe_allow_html=True)  # Close profile-container

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Health Companion - Senior Citizen Care App</div>", unsafe_allow_html=True)
