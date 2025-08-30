# frontend/pages/Profile.py (VERSION 3.0 - WITH NOTIFICATION TOGGLE)

import streamlit as st
from streamlit_cookies_manager import CookieManager
from datetime import datetime

# Sahi service functions ko import karna
from auth.service import TOKEN_COOKIE_NAME, get_profile, update_profile
from components.sidebar import authenticated_sidebar

# --- 1. PAGE CONFIGURATION & AUTHENTICATION ---
st.set_page_config(page_title="My Profile", page_icon="👤", layout="wide")

cookies = CookieManager()
if not cookies.ready():
    st.spinner("Initializing...")
    st.stop()

token = cookies.get(TOKEN_COOKIE_NAME)
if not token:
    st.warning("🔒 You are not logged in. Please log in to continue.")
    st.stop()

authenticated_sidebar(cookies)

# --- 2. CUSTOM STYLING ---
st.markdown("""
<style>
    /* --- Main Content Card Styling --- */
    .content-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #E0E0E0;
        padding: 2rem;
        margin-bottom: 1.5rem;
    }
    /* Info item styling for profile details */
    .info-item {
        padding: 0.8rem 0;
        border-bottom: 1px solid #f0f0f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .info-item b {
        color: #333;
    }
    .info-item span {
        color: #616161;
    }
</style>
""", unsafe_allow_html=True)


# --- 3. DATA FETCHING ---
@st.cache_data(show_spinner="Loading your profile...")
def load_profile_data(token_param):
    is_success, profile_data = get_profile(token_param)
    if not is_success:
        st.error(f"Could not load your profile: {profile_data}")
        return None
    return profile_data

profile_data = load_profile_data(token)

# --- 4. PAGE UI ---
st.title("👤 My Profile & Settings")
st.markdown("Here you can view and update your personal information and preferences.")
st.markdown("---")

if profile_data is None:
    st.stop()

# Main layout ko do columns mein baantna
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("Current Information")
    
    # Profile details ko behtar tareeke se dikhana
    st.markdown(f"<div class='info-item'><b>Email:</b> <span>{profile_data.get('email')}</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='info-item'><b>Full Name:</b> <span>{profile_data.get('full_name', 'Not set')}</span></div>", unsafe_allow_html=True)
    
    dob = profile_data.get('dob')
    display_dob = datetime.strptime(dob, '%Y-%m-%d').strftime('%B %d, %Y') if dob else "Not set"
    st.markdown(f"<div class='info-item'><b>Date of Birth:</b> <span>{display_dob}</span></div>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='info-item'><b>Address:</b> <span>{profile_data.get('address', 'Not set')}</span></div>", unsafe_allow_html=True)
    
    # Display notification status
    notifications_on = profile_data.get('notifications_enabled', True)
    status_text = "Enabled" if notifications_on else "Disabled"
    status_icon = "✅" if notifications_on else "❌"
    st.markdown(f"<div class='info-item'><b>Email Reminders:</b> <span>{status_icon} {status_text}</span></div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("Update Your Information")
    
    with st.form("update_profile_form"):
        # Form ko pehle se bhari hui jaankari ke saath dikhana
        full_name = st.text_input("Full Name", value=profile_data.get('full_name', ''))
        
        current_dob = None
        if profile_data.get('dob'):
            current_dob = datetime.strptime(profile_data.get('dob'), '%Y-%m-%d').date()
        
        dob = st.date_input("Date of Birth", value=current_dob, max_value=datetime.today())
        
        address = st.text_area("Address", value=profile_data.get('address', ''), height=100)
        
        # --- YEH NAYA TOGGLE SWITCH HAI ---
        st.markdown("**Notification Settings**")
        notifications_enabled = st.toggle(
            "Receive Daily Email Reminders", 
            value=profile_data.get('notifications_enabled', True)
        )
        
        submitted = st.form_submit_button("Save Changes", use_container_width=True, type="primary")
        if submitted:
            # Prepare payload with all fields, even if unchanged, plus the new toggle value
            payload = {
                "full_name": full_name,
                "dob": dob.isoformat() if dob else None,
                "address": address,
                "notifications_enabled": notifications_enabled
            }

            update_success, update_message = update_profile(token, payload)
            if update_success:
                st.success("Profile updated successfully!")
                st.cache_data.clear() # Cache clear karna zaroori hai
                st.rerun()
            else:
                st.error(update_message)
                    
    st.markdown('</div>', unsafe_allow_html=True)

