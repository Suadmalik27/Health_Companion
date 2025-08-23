# frontend/streamlit_app.py (Final Version with Fixed API URL)

import streamlit as st
import requests
import time
import os
from datetime import datetime

# --- CONFIGURATION ---
API_BASE_URL = "https://health-companion-backend-44ug.onrender.com"


# --- AUTH FUNCTIONS ---
def login_user(username, password):
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": username, "password": password},
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "Login failed")}
    except Exception as e:
        return {"error": str(e)}


def register_user(username, password):
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={"username": username, "password": password},
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "Registration failed")}
    except Exception as e:
        return {"error": str(e)}


# --- SESSION STATE INIT ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""


# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Health Companion")
menu = st.sidebar.radio("Navigate", ["Home", "Login", "Register", "Profile", "Logout"])


# --- HOME PAGE ---
if menu == "Home":
    st.title("🏥 Health Companion")
    st.write("Your AI-powered health assistant to track, analyze, and guide your health.")


# --- LOGIN PAGE ---
elif menu == "Login":
    st.title("🔑 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        result = login_user(username, password)
        if "error" in result:
            st.error(result["error"])
        else:
            st.success("Login successful!")
            st.session_state.logged_in = True
            st.session_state.username = username
            time.sleep(1)
            st.experimental_rerun()


# --- REGISTER PAGE ---
elif menu == "Register":
    st.title("📝 Register")

    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")

    if st.button("Register"):
        result = register_user(username, password)
        if "error" in result:
            st.error(result["error"])
        else:
            st.success("Registration successful! Please login.")
            time.sleep(1)
            st.experimental_rerun()


# --- PROFILE PAGE ---
elif menu == "Profile":
    if not st.session_state.logged_in:
        st.warning("Please login first.")
    else:
        st.title("👤 Profile")
        st.write(f"Welcome, **{st.session_state.username}** 🎉")

        # Example protected API call
        try:
            response = requests.get(f"{API_BASE_URL}/protected/profile")
            if response.status_code == 200:
                profile_data = response.json()
                st.json(profile_data)
            else:
                st.error("Could not fetch profile data.")
        except Exception as e:
            st.error(str(e))


# --- LOGOUT PAGE ---
elif menu == "Logout":
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.success("Logged out successfully!")
    time.sleep(1)
    st.experimental_rerun()
