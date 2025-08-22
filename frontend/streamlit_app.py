# frontend/streamlit_app.py

import streamlit as st
import requests
from datetime import datetime
import time
from PIL import Image
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Health Companion - Login",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
def local_css():
    st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .login-container {
        background-color: white;
        padding: 2.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        width: 100%;
        max-width: 450px;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 2rem;
    }
    .logo {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .tagline {
        color: #666;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 50px;
        font-weight: bold;
        margin-top: 1rem;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        color: #888;
        font-size: 0.9rem;
    }
    .error-message {
        background-color: #ffebee;
        color: #c62828;
        padding: 0.75rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        border-left: 4px solid #c62828;
    }
    .success-message {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 0.75rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        border-left: 4px solid #2e7d32;
    }
    .register-link {
        text-align: center;
        margin-top: 1.5rem;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# API base URL
API_BASE_URL = "https://health-companion-backend-44ug.onrender.com/"  # Update this if your backend is hosted elsewhere

def login_user(email, password):
    """Authenticate user with the backend API"""
    try:
        # Prepare the form data for OAuth2 password flow
        form_data = {
            "username": email,
            "password": password,
            "grant_type": "password",
            "scope": "",
            "client_id": "",
            "client_secret": ""
        }
        
        # Make the request to the login endpoint
        response = requests.post(
            f"{API_BASE_URL}/users/token",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            # Successful login
            token_data = response.json()
            # Store the token in session state
            st.session_state.access_token = token_data["access_token"]
            st.session_state.logged_in = True
            st.session_state.user_email = email
            return True, "Login successful!"
        else:
            # Failed login
            return False, "Invalid email or password"
            
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to the server. Please try again later."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"

def register_user(full_name, email, password):
    """Register a new user with the backend API"""
    try:
        user_data = {
            "full_name": full_name,
            "email": email,
            "password": password
        }
        
        response = requests.post(
            f"{API_BASE_URL}/users/register",
            json=user_data
        )
        
        if response.status_code == 201:
            return True, "Registration successful! Please log in."
        else:
            error_detail = response.json().get("detail", "Registration failed")
            return False, error_detail
            
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to the server. Please try again later."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'show_register' not in st.session_state:
    st.session_state.show_register = False

# If user is already logged in, redirect to dashboard
if st.session_state.logged_in and st.session_state.access_token:
    st.switch_page("pages/Dashboard.py")

# Main login/register interface
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Logo and tagline
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="logo">🩺 Health Companion</h1>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">Your personal health management assistant</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show registration form if needed
    if st.session_state.show_register:
        st.subheader("Create an Account")
        
        with st.form("register_form"):
            full_name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            register_submitted = st.form_submit_button("Register")
            
            if register_submitted:
                if not full_name or not email or not password:
                    st.error("Please fill in all fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = register_user(full_name, email, password)
                    if success:
                        st.success(message)
                        st.session_state.show_register = False
                    else:
                        st.error(message)
        
        st.markdown('<div class="register-link">', unsafe_allow_html=True)
        if st.button("Already have an account? Log in"):
            st.session_state.show_register = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Show login form
    else:
        st.subheader("Sign In to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            login_submitted = st.form_submit_button("Sign In")
            
            if login_submitted:
                if not email or not password:
                    st.error("Please enter both email and password")
                else:
                    with st.spinner("Signing in..."):
                        success, message = login_user(email, password)
                        if success:
                            st.success(message)
                            time.sleep(1)  # Brief delay to show success message
                            st.rerun()
                        else:
                            st.error(message)
        
        st.markdown('<div class="register-link">', unsafe_allow_html=True)
        if st.button("Don't have an account? Register here"):
            st.session_state.show_register = True
            st.rerun()
            
        if st.button("Forgot Password?"):
            st.info("Password reset functionality will be implemented soon")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close login-container
    
    # Footer
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown('© 2024 Health Companion | Senior Citizen Care App')
    st.markdown('</div>', unsafe_allow_html=True)
