import streamlit as st
import requests
 
from auth_utils import check_login

check_login()


API_BASE_URL = "https://health-companion-backend-44ug.onrender.com"

st.set_page_config(page_title="Login & Signup", page_icon="🔐", layout="centered")

# --- Page Title ---
st.markdown("<h2 style='text-align: center;'>🔐 Welcome to Health Companion</h2>", unsafe_allow_html=True)
st.write("Please log in or sign up to continue.")

# --- Tabs for Login / Signup ---
tab1, tab2 = st.tabs(["Login", "Signup"])

# --- LOGIN TAB ---
with tab1:
    st.subheader("Login to your account")

    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if not login_email or not login_password:
            st.warning("⚠️ Please fill in all fields.")
        else:
            try:
                response = requests.post(f"{API_BASE_URL}/auth/login", json={
                    "email": login_email,
                    "password": login_password
                })
                if response.status_code == 200:
                    data = response.json()
                    st.session_state["logged_in"] = True
                    st.session_state["token"] = data.get("token")
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")
            except Exception as e:
                st.error(f"Error: {e}")

# --- SIGNUP TAB ---
with tab2:
    st.subheader("Create a new account")

    signup_name = st.text_input("Full Name", key="signup_name")
    signup_email = st.text_input("Email", key="signup_email")
    signup_password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

    if st.button("Signup"):
        if not signup_name or not signup_email or not signup_password or not confirm_password:
            st.warning("⚠️ Please fill in all fields.")
        elif signup_password != confirm_password:
            st.error("❌ Passwords do not match.")
        else:
            try:
                response = requests.post(f"{API_BASE_URL}/auth/signup", json={
                    "name": signup_name,
                    "email": signup_email,
                    "password": signup_password
                })
                if response.status_code == 201:
                    st.success("🎉 Signup successful! Please log in.")
                else:
                    st.error("❌ Signup failed. Try a different email.")
            except Exception as e:
                st.error(f"Error: {e}")
