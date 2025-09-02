# frontend/pages/reset_password.py - FINAL, CORRECT VERSION

import sys
from pathlib import Path

# --- THIS IS THE CRITICAL FIX FOR DEPLOYMENT ---
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)
# --- END OF FIX ---

import streamlit as st
from auth.service import set_new_password
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Reset Password", layout="centered")
st.title("Create a New Password")

# Get token from URL
try:
    token = st.query_params["token"]
except KeyError:
    st.error("Invalid reset link. Token is missing.")
    st.stop()

# --- FORM ---
with st.form("reset_password_form"):
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")
    submitted = st.form_submit_button("Reset Password", use_container_width=True)

    if submitted:
        if not new_password or not confirm_password:
            st.warning("Please fill in both fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        elif len(new_password) < 6:
            st.error("Password must be at least 6 characters long.")
        else:
            is_success, message = set_new_password(token, new_password)
            if is_success:
                st.success(message)
                st.info("Redirecting to the login page...")
                time.sleep(3)
                st.switch_page("Home.py")
            else:
                st.error(message)
