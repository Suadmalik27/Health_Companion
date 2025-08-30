# frontend/Home.py (VERSION 2.2 - CLEANED WITH CENTRAL CSS)

import streamlit as st
from streamlit_cookies_manager import CookieManager
from auth.service import login_user, TOKEN_COOKIE_NAME
from pathlib import Path
import base64
import time
from components.custom_css import load_css # <-- NAYA IMPORT

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Welcome - Senior Wellness Hub",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. LOAD STYLES ---
# Ab hum central CSS file ko load karne ke liye simple function call karte hain
load_css()


# --- 3. INITIALIZE COOKIE MANAGER ---
cookies = CookieManager()
if not cookies.ready():
    st.spinner()
    st.stop()

# --- 4. PERSISTENT LOGIN CHECK ---
# Agar user pehle se logged in hai, toh use seedhe Dashboard par bhej do.
token = cookies.get(TOKEN_COOKIE_NAME)
if token:
    st.switch_page("pages/Dashboard.py")

# --- 5. PAGE LAYOUT ---
# Yeh code tabhi chalega jab user logged in nahi hai.
st.title("Senior Citizen Medical Reminder & Support Hub")
st.markdown("---")

# Function to read image as base64
def get_image_as_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return None

# Image ko load karna
image_path = Path(__file__).parent / "assets" / "icon.png"
img_base64 = get_image_as_base64(image_path)

col1, col2 = st.columns([1.5, 1], gap="large")

with col1:
    if img_base64:
        st.image(f"data:image/png;base64,{img_base64}", width=150)
    
    st.header("Aapke Swasthya ka Digital Sahayak")
    # Using markdown with a class for potential future specific styling
    st.markdown("""
        <div class="intro-text">
        Hum yahan aapke swasthya ka khayal rakhne mein aapki madad karne ke liye hain.
        Yeh website aapke digital assistant ki tarah kaam karti hai, jo aapko yeh sab yaad dilane ke liye design ki gayi hai:
        <ul>
            <li><span>💊</span> Sahi samay par apni dawaiyan lena.</li>
            <li><span>🗓️</span> Doctor ke saath aapke aane wale appointments.</li>
            <li><span>📞</span> Emergency mein apne parivar ke contact numbers.</li>
        </ul>
        Is platform ka istemal karna bahut aasan hai. Shuruaat karne ke liye, kripya apne account mein login karein.
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        email = st.text_input("Email Address", placeholder="Enter your email here")
        password = st.text_input("Password", type="password", placeholder="Enter your password here")
        
        form_cols = st.columns([1,1])
        with form_cols[0]:
            remember_me = st.checkbox("Remember Me", value=True)
        with form_cols[1]:
            submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

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

    st.markdown("---")
    st.write("Don't have an account or forgot your password?")
    
    btn_cols = st.columns(2)
    with btn_cols[0]:
        if st.button("New User? Register Here", use_container_width=True):
            st.switch_page("pages/Register.py")
    with btn_cols[1]:
        if st.button("Forgot Password?", use_container_width=True):
            st.switch_page("pages/Forgot_Password.py")

