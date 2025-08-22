# /frontend/pages/Reset_Password.py

import streamlit as st
import requests
import time
import os

# --- CONFIGURATION ---
# Use the same logic as main app for API URL
if 'RENDER' in st.secrets or 'RENDER' in os.environ:
    API_BASE_URL = "https://health-companion-backend-44ug.onrender.com"
else:
    API_BASE_URL = "http://localhost:8000"

# --- PAGE CONFIG ---
st.set_page_config(page_title="Reset Password", layout="centered", initial_sidebar_state="collapsed")

# --- Custom Styling ---
st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)


st.title("Reset Your Password 🔑")

# URL se token nikaalein (using the recommended st.query_params)
token = st.query_params.get("token")

if not token:
    st.error("Invalid password reset link. The link may be incomplete or expired.")
    st.info("Please request a new password reset link from the login page.")
    st.stop()

with st.form("reset_password_form"):
    st.write("Please enter a new, strong password below.")
    new_password = st.text_input("Enter New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")
    
    submitted = st.form_submit_button("Reset Password", use_container_width=True)
    
    if submitted:
        if not new_password or not confirm_password:
            st.warning("Please fill in both fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match!")
        else:
            with st.spinner("Resetting your password..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/users/reset-password",
                        json={"token": token, "new_password": new_password},
                        timeout=10
                    )
                    if response.status_code == 200:
                        st.success("Your password has been reset successfully!")
                        st.info("You can now close this page and log in with your new password.")
                        st.balloons()
                        time.sleep(3)
                        st.switch_page("streamlit_app.py")
                    else:
                        error_detail = response.json().get("detail", "An error occurred. The link may have expired.")
                        st.error(error_detail)
                except requests.exceptions.RequestException:
                    st.error("Connection Error: Could not connect to the server.")

st.page_link("streamlit_app.py", label="← Back to Login Page")
