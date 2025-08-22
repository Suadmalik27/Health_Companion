# frontend/streamlit_app.py (Fixed with proper sidebar navigation)

import streamlit as st
import requests
import time
import os

# --- CONFIGURATION & PAGE CONFIG ---
st.set_page_config(page_title="Health Companion", layout="wide", initial_sidebar_state="expanded")

# === PRODUCTION/LOCAL URL DETECTION ===
# Check if we're running on Render (production) or locally
if 'RENDER' in os.environ:
    # Production environment - use Render URL
    API_BASE_URL = "https://health-companion-backend-44ug.onrender.com"
else:
    # Local development - use localhost
    API_BASE_URL = "http://localhost:8000"

# --- API CLIENT CLASS ---
class ApiClient:
    def __init__(self, base_url): 
        self.base_url = base_url
    
    def _get_headers(self):
        token = st.session_state.get("token", None)
        if token: 
            return {"Authorization": f"Bearer {token}"}
        return {}
    
    def _make_request(self, method, endpoint, **kwargs):
        try:
            # Request timeout (10 seconds)
            return requests.request(
                method, 
                f"{self.base_url}{endpoint}", 
                headers=self._get_headers(), 
                timeout=10, 
                **kwargs
            )
        except requests.exceptions.RequestException as e:
            st.error(f"Connection Error: Could not connect to the backend server. Error: {str(e)}")
            return None
    
    def get(self, endpoint, params=None): 
        return self._make_request("GET", endpoint, params=params)
    
    def post(self, endpoint, data=None, json=None): 
        return self._make_request("POST", endpoint, data=data, json=json)
    
    def put(self, endpoint, json=None): 
        return self._make_request("PUT", endpoint, json=json)
    
    def delete(self, endpoint): 
        return self._make_request("DELETE", endpoint)

api = ApiClient(API_BASE_URL)

# --- STYLING FUNCTIONS ---
def apply_global_styles():
    st.markdown("""
        <style>
            /* General Font and Button styles */
            html, body, [class*="st-"] {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                font-size: 18px;
            }
            .stButton > button {
                padding: 0.75rem 1.25rem !important; 
                font-size: 1.1rem !important;
                font-weight: bold !important; 
                border-radius: 10px !important;
                transition: all 0.2s ease-in-out;
            }
            .stButton > button:hover {
                transform: translateY(-2px); 
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            /* Hide sidebar on login page */
            .login-page section[data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

def apply_themed_styles():
    theme = st.session_state.get("theme", "light")
    if theme == "dark":
        bg_color, text_color, secondary_bg, card_bg = "#1E1E1E", "#EAEAEA", "#2D2D2D", "#252526"
        primary_color, hover_color = "#3B82F6", "#2563EB"
    else:
        bg_color, text_color, secondary_bg, card_bg = "#F8F9FA", "#212529", "#FFFFFF", "#FFFFFF"
        primary_color, hover_color = "#0068C9", "#0055A3"
    
    st.markdown(f"""
        <style>
            html, body, [class*="st-"] {{ 
                color: {text_color}; 
                background-color: {bg_color}; 
            }}
            .st-emotion-cache-16txtl3 {{ 
                background-color: {secondary_bg}; 
            }}
            .card, .st-emotion-cache-1r6slb0, .login-container {{
                background-color: {card_bg}; 
                border: 1px solid #44444455;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
            }}
            .stButton > button {{
                background-color: {primary_color} !important; 
                color: white !important;
                border: 2px solid {primary_color} !important;
            }}
            .stButton > button:hover {{
                background-color: {hover_color} !important; 
                border-color: {hover_color} !important;
            }}
            .stButton > button[kind="secondary"] {{
                background-color: transparent !important; 
                color: {primary_color} !important;
            }}
            .emergency-bar {{
                background-color: #D32F2F; 
                color: white;
                position: fixed; 
                bottom: 0; 
                left: 0; 
                width: 100%; 
                text-align: center;
                padding: 15px 0; 
                font-size: 1.5rem; 
                font-weight: bold;
                z-index: 1000; 
                text-decoration: none; 
                border-top: 3px solid #B71C1C;
            }}
            .emergency-bar:hover {{ 
                background-color: #B71C1C; 
                color: white; 
            }}
            .login-tabs {{
                background-color: {card_bg};
                border-radius: 10px;
                padding: 20px;
            }}
        </style>
    """, unsafe_allow_html=True)

# --- HEADER COMPONENT ---
def create_header():
    theme = st.session_state.get('theme', 'light')
    header_bg = '#252526' if theme == 'dark' else 'white'
    
    current_time = time.strftime("%I:%M:%S %p")
    current_date = time.strftime("%A, %B %d, %Y")
    
    header_html = f"""
        <div style="display: flex; justify-content: space-between; align-items: center; 
                   padding: 1rem; background-color: {header_bg}; border-radius: 15px; 
                   box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 2rem;">
            <div>
                <h1 style="margin: 0; color: #0055a3; font-weight: 700;">Health Companion</h1>
                <p style="margin: 0; color: #555;">Your Medical Reminder & Support Assistant</p>
            </div>
            <div style="text-align: right;">
                <h2 style="margin: 0; color: #0055a3; font-weight: 600;">{current_time}</h2>
                <p style="margin: 0; color: #555;">{current_date}</p>
            </div>
        </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

# --- AUTHENTICATION PAGE FUNCTION ---
def show_login_register_page():
    st.markdown('<div class="login-page">', unsafe_allow_html=True)
    
    # Center the login form
    st.markdown("""
        <style>
            .login-page .main .block-container {
                padding-top: 5rem;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # App title
        st.markdown(
            """<div style="text-align: center;">
                <h1 style="color: #0055a3; font-weight: 700;">🩺 Welcome!</h1>
                <p style="color: #555; font-size: 1.2rem;">Your Health Companion</p>
            </div>""",
            unsafe_allow_html=True
        )
        
        st.write("")
        
        if st.session_state.get('just_registered', False):
            st.success("Registration successful!")
            del st.session_state['just_registered']

        # Login/Register tabs
        login_tab, register_tab = st.tabs(["**Sign In**", "**Create Account**"])
        
        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Sign In", use_container_width=True):
                    if not email or not password:
                        st.error("Please enter both email and password")
                    else:
                        with st.spinner("Authenticating..."):
                            response = api.post(
                                "/users/token", 
                                data={"username": email, "password": password, "grant_type": "password"}
                            )
                        
                        if response and response.status_code == 200:
                            st.session_state["token"] = response.json()["access_token"]
                            st.session_state["user_email"] = email
                            st.toast("Login Successful!", icon="🎉")
                            st.rerun()
                        else:
                            st.error("Login Failed: Incorrect email or password.")
        
        with register_tab:
            with st.form("register_form"):
                full_name = st.text_input("Full Name")
                new_email = st.text_input("Email", placeholder="you@example.com")
                new_password = st.text_input("Create Password", type="password")
                
                if st.form_submit_button("Create Account", use_container_width=True):
                    if not all([full_name, new_email, new_password]):
                        st.error("Please fill all fields")
                    else:
                        with st.spinner("Registering..."):
                            response = api.post(
                                "/users/register", 
                                json={
                                    "full_name": full_name, 
                                    "email": new_email, 
                                    "password": new_password
                                }
                            )
                        
                        if response and response.status_code == 201:
                            st.session_state['just_registered'] = True
                            st.rerun()
                        else:
                            error_detail = "Registration failed"
                            if response is not None:
                                try: 
                                    error_detail = response.json().get('detail', 'Email may already exist.')
                                except: 
                                    error_detail = "Server error occurred"
                            st.error(f"Registration Failed: {error_detail}")
        
        # Forgot password section
        st.write("---")
        
        if st.session_state.get("show_forgot_password", False):
            st.subheader("Reset Your Password")
            with st.form("reset_form"):
                email_reset = st.text_input("Email Address", key="reset_email")
                c1_reset, c2_reset = st.columns(2)
                
                with c1_reset:
                    if st.form_submit_button("Send Reset Link", use_container_width=True, type="primary"):
                        if not email_reset:
                            st.error("Please enter your email")
                        else:
                            with st.spinner("Sending..."):
                                response = api.post(
                                    "/users/forgot-password", 
                                    json={"email": email_reset}
                                )
                            
                            if response and response.status_code == 200:
                                st.success("Reset link sent! Please check your email.")
                                st.session_state.show_forgot_password = False
                                st.rerun()
                            else:
                                st.error("Something went wrong. Please try again.")
                
                with c2_reset:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.session_state.show_forgot_password = False
                        st.rerun()
        else:
            if st.button("Forgot Password?", type="secondary", use_container_width=True):
                st.session_state.show_forgot_password = True
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN APPLICATION LAYOUT ---
def main_app_layout():
    # Sidebar navigation
    with st.sidebar:
        st.title("🏥 Health Companion")
        st.markdown(f"Welcome, **{st.session_state.get('user_email', 'User')}**!")
        st.divider()
        
        # Navigation options
        if st.button("📊 Dashboard", use_container_width=True, key="nav_dashboard"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        
        if st.button("💊 Medications", use_container_width=True, key="nav_medications"):
            st.session_state.current_page = "Medications"
            st.rerun()
            
        if st.button("🗓️ Appointments", use_container_width=True, key="nav_appointments"):
            st.session_state.current_page = "Appointments"
            st.rerun()
            
        if st.button("📞 Contacts", use_container_width=True, key="nav_contacts"):
            st.session_state.current_page = "Contacts"
            st.rerun()
            
        if st.button("💡 Health Tips", use_container_width=True, key="nav_tips"):
            st.session_state.current_page = "Health_Tips"
            st.rerun()
            
        if st.button("👤 Profile", use_container_width=True, key="nav_profile"):
            st.session_state.current_page = "Profile"
            st.rerun()
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.toast("Logged out successfully.")
            st.rerun()
    
    # Emergency SOS bar
    response = api.get("/contacts/")
    if response and response.status_code == 200 and response.json():
        emergency_number = response.json()[0]['phone_number']
        st.markdown(
            f'<a href="tel:{emergency_number}" class="emergency-bar">🚨 EMERGENCY SOS - CALL {emergency_number} 🚨</a>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<a href="#" class="emergency-bar">⚠️ ADD EMERGENCY CONTACTS IN CONTACTS PAGE ⚠️</a>', 
            unsafe_allow_html=True
        )
    
    # Main content area - Show current page or dashboard
    current_page = st.session_state.get("current_page", "Dashboard")
    
    if current_page == "Dashboard":
        create_header()
        st.info("""
        Welcome to your Health Companion Dashboard! Here you can:
        - View your daily medications and mark them as taken
        - See today's appointments
        - Get daily health tips
        - Manage your health information
        
        Use the sidebar to navigate to different sections of the app.
        """, icon="👈")
        
        # Show quick stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Medications Today", "0", help="Number of medications scheduled for today")
        
        with col2:
            st.metric("Appointments Today", "0", help="Number of appointments scheduled for today")
        
        with col3:
            st.metric("Health Tips", "12", help="Total health tips available")
    
    elif current_page == "Medications":
        st.switch_page("pages/2_Medications.py")
    elif current_page == "Appointments":
        st.switch_page("pages/3_Appointments.py")
    elif current_page == "Contacts":
        st.switch_page("pages/4_Contacts.py")
    elif current_page == "Health_Tips":
        st.switch_page("pages/6_Health_Tips.py")
    elif current_page == "Profile":
        st.switch_page("pages/5_Profile.py")

# --- MAIN APPLICATION CONTROLLER ---
def main():
    apply_global_styles()

    # Initialize session state variables if they don't exist
    if "token" not in st.session_state:
        st.session_state.token = None
    
    if "show_forgot_password" not in st.session_state:
        st.session_state.show_forgot_password = False
    
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
        
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"

    # Show appropriate page based on authentication status
    if not st.session_state.token:
        show_login_register_page()
    else:
        # Load user theme preference
        if 'theme' not in st.session_state:
            with st.spinner("Loading settings..."):
                response = api.get("/users/me")
            
            if response and response.status_code == 200:
                st.session_state['theme'] = response.json().get('theme', 'light')
            else:
                st.session_state['theme'] = 'light'
        
        apply_themed_styles()
        main_app_layout()

if __name__ == "__main__":
    main()
