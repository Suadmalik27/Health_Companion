

# frontend/pages/forgot_password.py
import sys
from pathlib import Path

# --- THIS IS THE CRITICAL FIX FOR DEPLOYMENT ---
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)
# --- END OF FIX ---

import streamlit as st
from auth.service import request_password_reset

st.set_page_config(page_title="Forgot Password", layout="centered")
st.title("Forgot Your Password?")

with st.form("forgot_password_form"):
    email = st.text_input("Your Email Address")
    submitted = st.form_submit_button("Send Reset Link")

    if submitted:
        is_success, message = request_password_reset(email)
        st.success("If an account with that email exists, a password reset link has been sent.")
