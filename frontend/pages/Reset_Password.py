# /frontend/pages/Reset_Password.py

import streamlit as st
import requests

# API_BASE_URL ko yahan bhi define karna zaroori hai
if "API_BASE_URL" in st.secrets:
    API_BASE_URL = st.secrets["API_BASE_URL"]
else:
    API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Reset Password", layout="centered")

st.title("Reset Your Password")

# URL se token nikaalein
try:
    token = st.query_params["token"]
except KeyError:
    st.error("Invalid password reset link. The link may be incomplete or expired.")
    st.info("Please request a new password reset link from the login page.")
    st.stop()

with st.form("reset_password_form"):
    new_password = st.text_input("Enter New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")
    
    submitted = st.form_submit_button("Reset Password")
    
    if submitted:
        if not new_password or not confirm_password:
            st.warning("Please fill in both fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match!")
        else:
            response = requests.post(
                f"{API_BASE_URL}/users/reset-password",
                json={"token": token, "new_password": new_password}
            )
            if response.status_code == 200:
                st.success("Your password has been reset successfully!")
                st.info("You can now close this page and log in with your new password.")
                st.balloons()
            else:
                st.error(response.json().get("detail", "An error occurred. The link may have expired."))

st.page_link("streamlit_app.py", label="Back to Login Page")