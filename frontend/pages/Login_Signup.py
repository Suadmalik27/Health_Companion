import streamlit as st
import requests
from auth_utils import check_login

# --- Check login session ---
check_login()

# --- API Base URL ---
API_BASE_URL = "https://health-companion-backend-44ug.onrender.com"

# --- Page Config ---
st.set_page_config(
    page_title="Login & Signup",
    page_icon="🔐",
    layout="centered"
)

# --- Title ---
st.markdown(
    "<h2 style='text-align: center; color: #2c3e50;'>🔐 Welcome to Health Companion</h2>",
    unsafe_allow_html=True
)
st.write("Please login or signup to continue.")

# --- Tabs for Login / Signup ---
tab_login, tab_signup = st.tabs(["Login", "Signup"])

# ==========================
# LOGIN TAB
# ==========================
with tab_login:
    st.subheader("Login to your account")

    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", use_container_width=True, type="primary"):
        if not login_email or not login_password:
            st.warning("⚠️ Please fill in all fields.")
        else:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/auth/login",
                    json={"email": login_email, "password": login_password},
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state["logged_in"] = True
                    st.session_state["token"] = data.get("token")
                    st.success("✅ Login successful! Redirecting...")
                    st.rerun()
                elif response.status_code == 401:
                    st.error("❌ Invalid credentials. Please try again.")
                else:
                    st.error(f"⚠️ Login failed. Error code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"🚨 Network Error: {e}")

# ==========================
# SIGNUP TAB
# ==========================
with tab_signup:
    st.subheader("Create a new account")

    signup_name = st.text_input("Full Name", key="signup_name")
    signup_email = st.text_input("Email", key="signup_email")
    signup_password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

    if st.button("Signup", use_container_width=True, type="primary"):
        if not signup_name or not signup_email or not signup_password or not confirm_password:
            st.warning("⚠️ Please fill in all fields.")
        elif signup_password != confirm_password:
            st.error("❌ Passwords do not match.")
        else:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/auth/signup",
                    json={"name": signup_name, "email": signup_email, "password": signup_password},
                    timeout=10
                )
                if response.status_code == 201:
                    st.success("🎉 Signup successful! Please login now.")
                elif response.status_code == 409:
                    st.error("❌ Email already registered. Try another.")
                else:
                    st.error(f"⚠️ Signup failed. Error code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"🚨 Network Error: {e}")
