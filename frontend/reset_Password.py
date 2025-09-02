# frontend/Reset_Password.py (VERSION 2.0 - MODERN & SENIOR-FRIENDLY)

import streamlit as st
from auth.service import set_new_password
import time
from pathlib import Path
import base64

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Reset Password - Senior Wellness Hub",
    page_icon="❤️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM STYLING ---
# Consistent styling with other pages like Login and Register
st.markdown("""
<style>
    /* --- Hide default Streamlit elements for a cleaner look --- */
    header, footer { visibility: hidden !important; }
    
    /* --- Center and style the main title --- */
    h1 {
        text-align: center;
        padding-bottom: 20px;
    }

    /* --- Style the form container as a card --- */
    .content-card {
        background: #FFFFFF;
        padding: 2.5rem;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTION FOR IMAGE ---
def get_image_as_base64(path):
    """ Reads an image file and returns it as a base64 encoded string. """
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return None

# --- 4. PAGE LAYOUT ---

# Load and display the app icon
image_path = Path(__file__).parent.parent / "assets" / "download.jpeg"
img_base64 = get_image_as_base64(image_path)
if img_base64:
    st.image(f"data:image/png;base64,{img_base64}", width=100)

st.title("Create a New Password")

# Get the reset token from the URL query parameters
try:
    token = st.query_params["token"]
except KeyError:
    st.error("Invalid password reset link. The token is missing.")
    st.info("Please request a new password reset link from the 'Forgot Password' page.")
    st.stop()

st.markdown('<div class="content-card">', unsafe_allow_html=True)

st.markdown("Please enter and confirm your new password below. Make sure it is at least 6 characters long.")

with st.form("reset_password_form"):
    new_password = st.text_input("New Password", type="password", placeholder="Enter your new password")
    confirm_password = st.text_input("Confirm New Password", type="password", placeholder="Confirm your new password")
    
    submitted = st.form_submit_button(
        "Reset Password", 
        use_container_width=True, 
        type="primary"
    )

    if submitted:
        # --- Form Validation Logic ---
        if not new_password or not confirm_password:
            st.warning("Please fill in both password fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match. Please try again.")
        elif len(new_password) < 6:
            st.error("Password must be at least 6 characters long.")
        else:
            with st.spinner("Resetting your password..."):
                is_success, message = set_new_password(token, new_password)
            
            if is_success:
                st.success(message)
                st.info("Redirecting you to the login page...")
                time.sleep(3)
                st.switch_page("Home.py")
            else:
                st.error(message)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
if st.button("Back to Login", use_container_width=True):
    st.switch_page("Home.py")

