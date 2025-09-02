# frontend/Home.py - FINAL, CORRECT VERSION

import sys
from pathlib import Path

# --- THIS IS THE CRITICAL FIX FOR DEPLOYMENT ---
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.append(project_root)
# --- END OF FIX ---

import streamlit as st
from streamlit_cookies_manager import CookieManager
from auth.service import login_user, TOKEN_COOKIE_NAME
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Welcome", layout="wide", initial_sidebar_state="collapsed")

# --- COOKIE & LOGIN CHECK ---
cookies = CookieManager()
if not cookies.ready():
    st.spinner()
    st.stop()
if cookies.get(TOKEN_COOKIE_NAME):
    st.switch_page("pages/Dashboard.py")

# --- UI CODE ---
st.title("Senior Citizen Medical Reminder & Support Hub")
st.markdown("---")
col1, col2 = st.columns([1.5, 1], gap="large")
with col1:
    st.header("Your Digital Health Companion")
    st.markdown("""
    We're here to help you manage your health with ease. This platform serves as your digital assistant, designed to help you:
    - **💊 Take your medications** at the right time
    - **🗓️ Keep track** of your upcoming doctor appointments  
    - **📞 Access emergency contact numbers** when needed
    """)
with col2:
    st.subheader("Login to Your Account")
    with st.form("login_form"):
        email = st.text_input("Email Address", placeholder="Enter your email here")
        password = st.text_input("Password", type="password", placeholder="Enter your password here")
        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

        if submitted:
            is_success, data = login_user(email, password)
            if is_success:
                token_data = data.get("access_token")
                cookies[TOKEN_COOKIE_NAME] = token_data
                st.success("Login Successful!")
                time.sleep(1)
                st.rerun()
            else:
                st.error(str(data))

    st.markdown("---")
    btn_cols = st.columns(2)
    with btn_cols[0]:
        if st.button("New User? Register Here", use_container_width=True):
            st.switch_page("pages/Register.py")
    with btn_cols[1]:
        if st.button("Forgot Password?", use_container_width=True):
            st.switch_page("pages/forgot_password.py") # Use correct lowercase filename
