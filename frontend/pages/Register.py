# frontend/pages/Register.py (VERSION 2.1 - CLEANED WITH CENTRAL CSS)

import streamlit as st
import re
import time
from auth.service import register_user
from pathlib import Path
import base64
from components.custom_css import load_css # <-- NAYA IMPORT

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Register Account - Senior Wellness Hub",
    page_icon="❤️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. LOAD STYLES ---
# Ab hum central CSS file ko load karne ke liye simple function call karte hain
load_css()

# --- 3. HELPER FUNCTIONS ---

def is_valid_email(email):
    """ Validate the email address using a regular expression. """
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.match(regex, email)

def check_password_strength(password):
    """ Check the strength of the password. """
    strength = 0
    if len(password) >= 8: strength += 1
    if re.search(r"[a-z]", password) and re.search(r"[A-Z]", password): strength += 1
    if re.search(r"\d", password): strength += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): strength += 1
    
    if strength < 2: return "Weak", "weak"
    elif strength == 2: return "Medium", "medium"
    else: return "Strong", "strong"

def get_image_as_base64(path):
    """ Reads an image file and returns it as a base64 encoded string. """
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return None

# --- 4. REGISTRATION PAGE LAYOUT ---

image_path = Path(__file__).parent.parent / "assets" / "icon.png"
img_base64 = get_image_as_base64(image_path)
if img_base64:
    st.image(f"data:image/png;base64,{img_base64}", width=100)

st.title("Create a New Account")
st.markdown("Please fill out the form below to join our community.")
st.markdown("---")

with st.form("register_form"):
    st.subheader("Your Personal Details")
    
    full_name = st.text_input("Full Name", placeholder="Your full name")
    email = st.text_input("Email Address", placeholder="Your email address")
    
    st.subheader("Create a Secure Password")
    
    password = st.text_input("Password", type="password", placeholder="Create a strong password")
    
    # Password Strength Indicator
    if password:
        strength_text, strength_class = check_password_strength(password)
        st.markdown(f"Password Strength: **{strength_text}**")
        # Note: The styling for this is in the central style.css file
        st.markdown(f'<div class="strength-bar-container"><div class="strength-bar {strength_class}"></div></div>', unsafe_allow_html=True)

    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
    
    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Create My Account", use_container_width=True, type="primary")

    if submitted:
        # --- Form Validation Logic ---
        if not full_name or not email or not password or not confirm_password:
            st.warning("Please fill out all the fields.")
        elif not is_valid_email(email):
            st.error("Please enter a valid email address.")
        elif password != confirm_password:
            st.error("Passwords do not match. Please try again.")
        elif len(password) < 6:
            st.error("Password should be at least 6 characters long.")
        else:
            with st.spinner("Creating your account..."):
                is_success, message = register_user(full_name, email, password)
            
            if is_success:
                st.success(message)
                st.info("Redirecting you to the login page...")
                time.sleep(2)
                st.switch_page("Home.py")
            else:
                st.error(message)

st.markdown("---")
if st.button("Already have an account? Login Here", use_container_width=True):
    st.switch_page("Home.py")

