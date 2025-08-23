# frontend/streamlit_app.py (Fixed Login Issue)
import streamlit as st
import requests
import time
import os

# --- CONFIGURATION & PAGE CONFIG ---
st.set_page_config(
    page_title="Health Companion", 
    layout="wide", 
    initial_sidebar_state="expanded",
    menu_items=None
)

# === PRODUCTION/LOCAL URL DETECTION ===
API_BASE_URL = st.secrets.get("API_BASE_URL", "https://health-companion-backend-44ug.onrender.com")

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
            return requests.request(
                method, 
                f"{self.base_url}{endpoint}", 
                headers=self._get_headers(), 
                timeout=10, 
                **kwargs
            )
        except requests.exceptions.RequestException as e:
            st.error(f"Connection Error: Could not connect to backend. Error: {str(e)}")
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
            /* Main content area */
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 5rem;
            }
            
            /* Sidebar styling */
            section[data-testid="stSidebar"] {
                background-color: #f0f2f6;
            }
            
            section[data-testid="stSidebar"] .stButton button {
                width: 100%;
                margin: 5px 0;
                text-align: left;
                padding: 10px 15px;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                background-color: white;
                color: #262730;
            }
            
            section[data-testid="stSidebar"] .stButton button:hover {
                background-color: #0068c9;
                color: white;
                border-color: #0068c9;
            }
            
            /* Header styling */
            .header-container {
                background: linear-gradient(135deg, #0068c9 0%, #004d99 100%);
                color: white;
                padding: 1.5rem;
                border-radius: 12px;
                margin-bottom: 2rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            
            /* Emergency bar */
            .emergency-bar {
                background-color: #D32F2F; 
                color: white;
                position: fixed; 
                bottom: 0; 
                left: 0; 
                width: 100%; 
                text-align: center;
                padding: 15px 0; 
                font-size: 1.2rem; 
                font-weight: bold;
                z-index: 1000; 
                text-decoration: none; 
                border-top: 3px solid #B71C1C;
            }
            .emergency-bar:hover { 
                background-color: #B71C1C; 
                color: white; 
            }

            /* Dark mode compatibility */
            h1, h2, h3, h4, h5, h6, p, span, div {
                color: var(--text-color, #262730) !important;
            }
        </style>
    """, unsafe_allow_html=True)

# --- HEADER COMPONENT ---
def create_header():
    current_time = time.strftime("%I:%M:%S %p")
    current_date = time.strftime("%A, %B %d, %Y")
    
    header_html = f"""
        <div class="header-container">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1 style="margin: 0; font-weight: 700;">Health Companion</h1>
                    <p style="margin: 0; opacity: 0.9;">Your Medical Reminder & Support Assistant</p>
                </div>
                <div style="text-align: right;">
                    <h2 style="margin: 0; font-weight: 600;">{current_time}</h2>
                    <p style="margin: 0; opacity: 0.9;">{current_date}</p>
                </div>
            </div>
        </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

# --- AUTHENTICATION PAGE FUNCTION ---
def show_login_register_page():
    # Center the login form
    st.markdown("""
        <style>
            .main .block-container {
                padding-top: 5rem;
                display: flex;
                justify-content: center;
                align-items: center;
            }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # App title
        st.markdown(
            """<div style="text-align: center;">
                <h1 style="color: #0068c9; font-weight: 700;">🩺 Health Companion</h1>
                <p style="color: #555; font-size: 1.2rem;">Your Medical Reminder & Support Assistant</p>
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
                            st.session_state["user_name"] = email.split('@')[0]
                            st.session_state["logged_in"] = True  # Add this flag
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

# --- SIDEBAR COMPONENT ---
def create_sidebar():
    with st.sidebar:
        st.title("🏥 Navigation")
        st.write(f"Welcome, **{st.session_state.get('user_name', 'User')}**!")
        st.divider()
        
         
        for option in nav_options:
            if st.button(f"{option['icon']} {option['label']}", key=f"nav_{option['page']}", use_container_width=True):
                st.session_state.current_page = option['page']
                st.rerun()
        
        st.divider()
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.toast("Logged out successfully.")
            st.rerun()

# --- MAIN DASHBOARD CONTENT ---
def show_dashboard():
    create_header()
    
    # Welcome message
    st.write(f"### 👋 Welcome back, {st.session_state.get('user_name', 'User')}!")
    st.write("Here's your health summary for today.")
    
    # Quick stats cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("#### 💊 Medications Today")
        st.write("**3 scheduled**")
        st.write("2 taken ✅")
        st.write("1 remaining ⏰")
    
    with col2:
        st.info("#### 🗓️ Appointments")
        st.write("**1 today**")
        st.write("Dr. Smith - 3:00 PM")
        st.write("Check-up ✅")
    
    with col3:
        st.info("#### 💡 Health Tip")
        st.write("**Stay Hydrated**")
        st.write("Drink at least 8 glasses of water today to stay hydrated and support your medication effectiveness.")
    
    st.divider()
    
    # Recent activity
    st.write("### 📋 Recent Activity")
    
    activity_col1, activity_col2 = st.columns(2)
    
    with activity_col1:
        st.write("**Today's Medications**")
        st.write("• Vitamin D - 9:00 AM ✅")
        st.write("• Blood Pressure - 2:00 PM ⏰")
        st.write("• Pain Relief - 8:00 PM ⏰")
    
    with activity_col2:
        st.write("**Upcoming Appointments**")
        st.write("• Dr. Smith - Today 3:00 PM")
        st.write("• Dentist - Aug 25 10:00 AM")
        st.write("• Eye Doctor - Sep 5 11:30 AM")
    
    st.divider()
    
    # Quick actions
    st.write("### ⚡ Quick Actions")
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("Add Medication", use_container_width=True):
            st.session_state.current_page = "Medications"
            st.rerun()
    
    with action_col2:
        if st.button("Schedule Appointment", use_container_width=True):
            st.session_state.current_page = "Appointments"
            st.rerun()
    
    with action_col3:
        if st.button("Add Emergency Contact", use_container_width=True):
            st.session_state.current_page = "Contacts"
            st.rerun()

# --- MAIN APPLICATION CONTROLLER ---
def main():
    apply_global_styles()

    # Initialize session state variables
    if "token" not in st.session_state:
        st.session_state.token = None
    
    if "show_forgot_password" not in st.session_state:
        st.session_state.show_forgot_password = False
    
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
        
    if "user_name" not in st.session_state:
        st.session_state.user_name = None
        
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # Show appropriate page based on authentication status
    if not st.session_state.get("logged_in", False) and not st.session_state.token:
        show_login_register_page()
    else:
        # Create sidebar navigation
        create_sidebar()
        
        # Show main content based on current page
        if st.session_state.current_page == "Dashboard":
            show_dashboard()
        elif st.session_state.current_page == "Medications":
            st.switch_page("pages/Medications.py")
        elif st.session_state.current_page == "Appointments":
            st.switch_page("pages/Appointments.py")
        elif st.session_state.current_page == "Contacts":
            st.switch_page("pages/Contacts.py")
        elif st.session_state.current_page == "Health_Tips":
            st.switch_page("pages/Health_Tips.py")
        elif st.session_state.current_page == "Profile":
            st.switch_page("pages/Profile.py")
        
        # Emergency SOS bar (only show if not on contacts page)
        if st.session_state.current_page != "Contacts":
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

if __name__ == "__main__":
    main()
