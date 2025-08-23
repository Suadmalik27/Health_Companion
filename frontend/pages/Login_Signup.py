import streamlit as st
import requests
from auth_utils import check_login

# --- Authentication Check ---
check_login()

# --- API Base URL ---
API_BASE_URL = "https://health-companion-backend-44ug.onrender.com"

# --- Streamlit Page Config ---
st.set_page_config(page_title="Login & Signup", page_icon="🔐", layout="centered")

# --- Custom CSS for Styling ---
st.markdown("""
    <style>
        .main {
            background-color: #f7f9fc;
        }
        .stTabs [data-baseweb="tab-list"] {
            display: flex;
            justify-content: center;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 16px;
            padding: 10px 20px;
        }
        .stTextInput>div>div>input {
            border-radius: 10px;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 10px;
            padding: 10px 20px;
            border: none;
            font-size: 16px;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .forgot-link {
            font-size: 14px;
            color: #0066cc;
            cursor: pointer;
            text-decoration: underline;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("<h2 style='text-align: center;'>🔐 Welcome to Health Companion</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Please login or sign up to continue.</p>", unsafe_allow_html=True)

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Login", "Signup", "Forgot Password"])

# --- LOGIN TAB ---
with tab1:
    st.subheader("Login to your account")

    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
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
                st.error(f"⚠️ Error: {e}")

    st.markdown(
        "<p style='text-align:center;margin-top:10px;'>"
        "<span class='forgot-link'>Forgot Password?</span>"
        "</p>",
        unsafe_allow_html=True
    )

# --- SIGNUP TAB ---
with tab2:
    st.subheader("Create a new account")

    signup_name = st.text_input("Full Name", key="signup_name")
    signup_email = st.text_input("Email", key="signup_email")
    signup_password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

    if st.button("Signup", key="signup_button"):
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
                st.error(f"⚠️ Error: {e}")

# --- FORGOT PASSWORD TAB ---
with tab3:
    st.subheader("Reset your password")

    forgot_email = st.text_input("Enter your registered email", key="forgot_email")

    if st.button("Send Reset Link", key="forgot_button"):
        if not forgot_email:
            st.warning("⚠️ Please enter your email.")
        else:
            try:
                response = requests.post(f"{API_BASE_URL}/auth/forgot-password", json={
                    "email": forgot_email
                })
                if response.status_code == 200:
                    st.success("📩 A password reset link has been sent to your email.")
                else:
                    st.error("❌ Email not found. Please try again.")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
