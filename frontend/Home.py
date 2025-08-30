import streamlit as st
from streamlit_cookies_manager import CookieManager
from auth.service import login_user, TOKEN_COOKIE_NAME
from pathlib import Path
import base64
import time
from components.custom_css import load_css  # Central CSS import

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Welcome - Senior Wellness Hub",
    page_icon="❤️",
    layout="centered",  # Changed to centered layout
    initial_sidebar_state="collapsed"
)

# --- 2. LOAD STYLES ---
load_css()  # Load centralized CSS styles

# Add custom CSS for centering
st.markdown("""
<style>
.centered-container {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    padding: 2rem;
}
.login-card {
    background-color: white;
    border-radius: 10px;
    padding: 2rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
    border: 1px solid #e0e0e0;
}
[data-theme="dark"] .login-card {
    background-color: #262730;
    border: 1px solid #444;
}
</style>
""", unsafe_allow_html=True)

# --- 3. INITIALIZE COOKIE MANAGER ---
cookies = CookieManager()
if not cookies.ready():
    st.spinner()
    st.stop()

# --- 4. PERSISTENT LOGIN CHECK ---
# If user is already logged in, redirect them directly to Dashboard
token = cookies.get(TOKEN_COOKIE_NAME)
if token:
    st.switch_page("pages/Dashboard.py")

# --- 5. PAGE LAYOUT ---
# This code will only execute if user is not logged in

# Function to read image as base64
def get_image_as_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return None

# Load image
image_path = Path(__file__).parent / "assets" / "download.jpeg"
img_base64 = get_image_as_base64(image_path)

# Main centered container
st.markdown('<div class="centered-container">', unsafe_allow_html=True)

# Display app logo centered
if img_base64:
    st.image(f"data:image/png;base64,{img_base64}", width=120)

# App title
st.header("Your Digital Health Companion", anchor=False)

# App description
st.markdown("""
<div class="intro-text" style="text-align: center; margin-bottom: 2rem;">
We're here to help you manage your health with ease. 
This platform serves as your digital assistant to help you stay on track with medications, appointments, and emergency contacts.
</div>
""", unsafe_allow_html=True)

# Login card
st.markdown('<div class="login-card">', unsafe_allow_html=True)

# Login form section
st.subheader("Login to Your Account", anchor=False)

with st.form("login_form"):
    email = st.text_input("Email Address", placeholder="Enter your email here")
    password = st.text_input("Password", type="password", placeholder="Enter your password here")
    
    # Form options
    remember_me = st.checkbox("Remember Me", value=True)
    
    # Centered login button
    submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

    # Form submission handling
    if submitted:
        if not email or not password:
            st.warning("Please enter both email and password.")
        else:
            with st.spinner("Logging you in..."):
                is_success, data = login_user(email, password)
            
            if is_success:
                token_data = data.get("access_token")
                if token_data:
                    cookies[TOKEN_COOKIE_NAME] = token_data
                
                st.success("Login Successful! Redirecting to your dashboard...")
                time.sleep(1)
                st.rerun()
            else:
                st.error(data)

# Close login card div
st.markdown('</div>', unsafe_allow_html=True)

# Additional options below the login form
st.markdown("""
<div style="text-align: center; margin-top: 1.5rem;">
    <p style="margin-bottom: 1rem;">Don't have an account or forgot your password?</p>
</div>
""", unsafe_allow_html=True)

# Action buttons centered
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("New User? Register Here", use_container_width=True):
        st.switch_page("pages/Register.py")
    if st.button("Forgot Password?", use_container_width=True):
        st.switch_page("pages/Forgot_Password.py")

# Close centered container div
st.markdown('</div>', unsafe_allow_html=True)
