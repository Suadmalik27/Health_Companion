# frontend/pages/Reset_Password.py (Fixed - No config import)

import streamlit as st
import requests
from urllib.parse import parse_qs, urlparse
import os

# Page configuration
st.set_page_config(
    page_title="Reset Password - Health Companion",
    page_icon="🔒",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Get API base URL directly
def get_api_base_url():
    """Get the API base URL from secrets, environment variables, or use default"""
    try:
        return st.secrets["API_BASE_URL"]
    except:
        try:
            return os.environ.get("API_BASE_URL", "https://health-companion-backend-44ug.onrender.com")
        except:
            return "https://health-companion-backend-44ug.onrender.com"

def make_api_request(method, endpoint, **kwargs):
    """Make an API request with proper error handling"""
    base_url = get_api_base_url()
    url = f"{base_url}{endpoint}"
    
    # Add timeout if not specified
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 10
    
    try:
        response = requests.request(method, url, **kwargs)
        return response
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the server. Please check your internet connection.")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

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
    .reset-container {
        background-color: white;
        padding: 2.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        width: 100%;
        max-width: 500px;
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
    .info-message {
        background-color: #e3f2fd;
        color: #1565c0;
        padding: 0.75rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        border-left: 4px solid #1565c0;
    }
    .password-strength {
        margin-top: 0.5rem;
        padding: 0.5rem;
        border-radius: 5px;
        font-size: 0.9rem;
    }
    .strength-weak {
        background-color: #ffebee;
        color: #c62828;
        border-left: 4px solid #c62828;
    }
    .strength-medium {
        background-color: #fff3e0;
        color: #ef6c00;
        border-left: 4px solid #ef6c00;
    }
    .strength-strong {
        background-color: #e8f5e9;
        color: #2e7d32;
        border-left: 4px solid #2e7d32;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

def check_password_strength(password):
    """Check password strength and provide feedback"""
    if len(password) == 0:
        return "", ""
    
    strength = 0
    feedback = []
    
    # Length check
    if len(password) >= 8:
        strength += 1
    else:
        feedback.append("At least 8 characters")
    
    # uppercase check
    if any(char.isupper() for char in password):
        strength += 1
    else:
        feedback.append("Uppercase letters")
    
    # lowercase check
    if any(char.islower() for char in password):
        strength += 1
    else:
        feedback.append("Lowercase letters")
    
    # digit check
    if any(char.isdigit() for char in password):
        strength += 1
    else:
        feedback.append("Numbers")
    
    # special character check
    if any(not char.isalnum() for char in password):
        strength += 1
    else:
        feedback.append("Special characters")
    
    if strength <= 2:
        return "weak", feedback
    elif strength <= 4:
        return "medium", feedback
    else:
        return "strong", feedback

def reset_password(token, new_password):
    """Reset password using the provided token"""
    try:
        reset_data = {
            "token": token,
            "new_password": new_password
        }
        
        response = make_api_request("POST", "/users/reset-password", json=reset_data)
        
        if response and response.status_code == 200:
            return True, "Password has been reset successfully!"
        elif response:
            error_detail = response.json().get("detail", "Failed to reset password")
            return False, error_detail
        else:
            return False, "Failed to connect to the server"
            
    except Exception as e:
        return False, f"An error occurred: {str(e)}"

def request_password_reset(email):
    """Request a password reset link"""
    try:
        reset_data = {
            "email": email
        }
        
        response = make_api_request("POST", "/users/forgot-password", json=reset_data)
        
        if response and response.status_code == 200:
            return True, "If an account with that email exists, a reset link has been sent."
        elif response:
            # For security, we don't reveal if the email exists or not
            return True, "If an account with that email exists, a reset link has been sent."
        else:
            return False, "Failed to connect to the server"
            
    except Exception as e:
        return False, f"An error occurred: {str(e)}"

# Check if user is already logged in
if 'logged_in' in st.session_state and st.session_state.logged_in:
    st.warning("You are already logged in. Please logout first to reset your password.")
    st.stop()

# Get token from URL parameters
query_params = st.experimental_get_query_params()
token = query_params.get("token", [None])[0]

# Main content
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown('<div class="reset-container">', unsafe_allow_html=True)
    
    # Logo and tagline
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="logo">🔒 Health Companion</h1>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">Password Recovery</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Password Reset Form (if token is provided)
    if token:
        st.markdown("### Set New Password")
        st.markdown("""
        <div class="info-message">
            Please enter your new password below. Make sure it's strong and secure.
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("reset_password_form"):
            new_password = st.text_input("New Password", type="password", 
                                       help="Must be at least 8 characters with uppercase, lowercase, number, and special character")
            
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            # Password strength indicator
            if new_password:
                strength, feedback = check_password_strength(new_password)
                strength_class = f"strength-{strength}"
                strength_display = strength.capitalize()
                
                if strength == "weak":
                    st.markdown(f"""
                    <div class="password-strength {strength_class}">
                        ⚠️ Password Strength: {strength_display}
                        <br><small>Missing: {', '.join(feedback)}</small>
                    </div>
                    """, unsafe_allow_html=True)
                elif strength == "medium":
                    st.markdown(f"""
                    <div class="password-strength {strength_class}">
                        ⚠️ Password Strength: {strength_display}
                        <br><small>Could be stronger: {', '.join(feedback)}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="password-strength {strength_class}">
                        ✅ Password Strength: {strength_display}
                    </div>
                    """, unsafe_allow_html=True)
            
            submitted = st.form_submit_button("🔓 Reset Password")
            
            if submitted:
                if not new_password or not confirm_password:
                    st.error("Please fill in both password fields")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    strength, feedback = check_password_strength(new_password)
                    if strength == "weak":
                        st.error("Password is too weak. Please choose a stronger password.")
                    else:
                        with st.spinner("Resetting password..."):
                            success, message = reset_password(token, new_password)
                            if success:
                                st.success(message)
                                # Clear the token from URL
                                st.experimental_set_query_params()
                                st.balloons()
                            else:
                                st.error(message)
    
    else:
        # Password Reset Request Form
        st.markdown("### Forgot Your Password?")
        st.markdown("""
        <div class="info-message">
            Enter your email address below and we'll send you a link to reset your password.
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("forgot_password_form"):
            email = st.text_input("Email Address", 
                                placeholder="Enter your registered email address",
                                help="We'll send a password reset link to this email")
            
            submitted = st.form_submit_button("📧 Send Reset Link")
            
            if submitted:
                if not email:
                    st.error("Please enter your email address")
                else:
                    with st.spinner("Sending reset link..."):
                        success, message = request_password_reset(email)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
        
        st.markdown("---")
        st.markdown("### Remembered your password?")
        if st.button("← Back to Login"):
            st.switch_page("streamlit_app.py")
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close reset-container
    
    # Footer
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown('© 2024 Health Companion | Senior Citizen Care App')
    st.markdown('</div>', unsafe_allow_html=True)
