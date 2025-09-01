import streamlit as st
from streamlit_cookies_manager import CookieManager
from auth.service import login_user, TOKEN_COOKIE_NAME
from pathlib import Path
import base64
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Welcome - Senior Wellness Hub",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. INITIALIZE COOKIE MANAGER ---
cookies = CookieManager()
if not cookies.ready():
    st.spinner()
    st.stop()

# --- 3. PERSISTENT LOGIN CHECK ---
# If user is already logged in, redirect them directly to Dashboard
token = cookies.get(TOKEN_COOKIE_NAME)
if token:
    st.switch_page("pages/Dashboard.py")

# --- 4. PAGE LAYOUT ---
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

# Main title
st.title("Senior Citizen Medical Reminder & Support Hub")
st.markdown("---")

# Two-column layout (original layout)
col1, col2 = st.columns([1.5, 1], gap="large")

with col1:
    # Display app logo
    if img_base64:
        st.image(f"data:image/png;base64,{img_base64}", width=150)
    
    # App introduction
    st.header("Your Digital Health Companion")
    
    # App description with benefits
    st.markdown("""
    We're here to help you manage your health with ease. 
    This platform serves as your digital assistant, designed to help you:
    - **💊 Take your medications** at the right time
    - **🗓️ Keep track** of your upcoming doctor appointments  
    - **📞 Access emergency contact numbers** when needed
    
    Our platform is designed to be simple and easy to use. To get started, please log into your account.
    """)

with col2:
    # Login form section
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        email = st.text_input("Email Address", placeholder="Enter your email here")
        password = st.text_input("Password", type="password", placeholder="Enter your password here")
        
        # Form options in columns (original layout)
        form_cols = st.columns([1, 1])
        with form_cols[0]:
            remember_me = st.checkbox("Remember Me", value=True)
        with form_cols[1]:
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

    # Divider and additional options
    st.markdown("---")
    st.write("Don't have an account or forgot your password?")
    
    # Action buttons (original layout)
    btn_cols = st.columns(2)
    with btn_cols[0]:
        if st.button("New User? Register Here", use_container_width=True):
            st.switch_page("pages/Register.py")
    with btn_cols[1]:
        if st.button("Forgot Password?", use_container_width=True):
            st.switch_page("pages/forgot_password.py")


