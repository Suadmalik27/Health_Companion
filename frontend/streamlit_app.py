# frontend/streamlit_app.py (Premium Dark/Light Mode Version)
import streamlit as st
import requests
import time
import os
from datetime import datetime

# --- CONFIGURATION ---
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

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Health Companion", 
    layout="wide", 
    initial_sidebar_state="expanded",
    menu_items=None,
    page_icon="🩺"
)

# --- GLOBAL STYLING WITH DARK/LIGHT MODE SUPPORT ---
def apply_global_styles():
    st.markdown(f"""
    <style>
    /* CSS Variables for Theme Switching */
    :root {{
        --primary-color: #0068c9;
        --primary-hover: #0052a3;
        --secondary-color: #6c757d;
        --success-color: #28a745;
        --danger-color: #dc3545;
        --warning-color: #ffc107;
        --info-color: #17a2b8;
        --light-bg: #ffffff;
        --dark-bg: #0e1117;
        --light-text: #262730;
        --dark-text: #fafafa;
        --light-border: #e0e0e0;
        --dark-border: #2d3748;
        --light-card: #ffffff;
        --dark-card: #1a1d29;
        --light-input: #ffffff;
        --dark-input: #2d3748;
        --light-sidebar: #f0f2f6;
        --dark-sidebar: #1a1d29;
    }}

    /* Dark Mode Detection and Application */
    [data-theme="dark"] {{
        --background-color: var(--dark-bg);
        --text-color: var(--dark-text);
        --card-background: var(--dark-card);
        --card-text: var(--dark-text);
        --border-color: var(--dark-border);
        --input-background: var(--dark-input);
        --input-text: var(--dark-text);
        --sidebar-background: var(--dark-sidebar);
        --sidebar-text: var(--dark-text);
        --sidebar-border: var(--dark-border);
    }}

    [data-theme="light"] {{
        --background-color: var(--light-bg);
        --text-color: var(--light-text);
        --card-background: var(--light-card);
        --card-text: var(--light-text);
        --border-color: var(--light-border);
        --input-background: var(--light-input);
        --input-text: var(--light-text);
        --sidebar-background: var(--light-sidebar);
        --sidebar-text: var(--light-text);
        --sidebar-border: var(--light-border);
    }}

    /* Main Container */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 5rem;
        background-color: var(--background-color);
        color: var(--text-color) !important;
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: var(--sidebar-background) !important;
        border-right: 1px solid var(--sidebar-border);
    }}

    section[data-testid="stSidebar"] .stButton button {{
        width: 100%;
        margin: 5px 0;
        text-align: left;
        padding: 12px 16px;
        border-radius: 10px;
        border: 1px solid var(--border-color);
        background-color: var(--card-background);
        color: var(--text-color) !important;
        transition: all 0.3s ease;
        font-weight: 500;
    }}

    section[data-testid="stSidebar"] .stButton button:hover {{
        background-color: var(--primary-color);
        color: white !important;
        border-color: var(--primary-color);
        transform: translateX(5px);
    }}

    /* Header Styling */
    .header-container {{
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
        color: white !important;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }}

    /* Emergency Bar */
    .emergency-bar {{
        background-color: var(--danger-color) !important; 
        color: white !important;
        position: fixed; 
        bottom: 0; 
        left: 0; 
        width: 100%; 
        text-align: center;
        padding: 16px 0; 
        font-size: 1.3rem; 
        font-weight: bold;
        z-index: 1000; 
        text-decoration: none; 
        border-top: 3px solid #B71C1C;
        transition: background-color 0.3s ease;
    }}

    .emergency-bar:hover {{ 
        background-color: #B71C1C !important; 
        color: white !important; 
    }}

    /* Text Elements - Force Visibility */
    h1, h2, h3, h4, h5, h6, p, span, div, .stMarkdown {{
        color: var(--text-color) !important;
    }}

    /* Form Elements */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: var(--input-background) !important;
        color: var(--input-text) !important;
        border: 2px solid var(--border-color);
        border-radius: 10px;
        padding: 12px;
    }}

    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {{
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(0, 104, 201, 0.1);
    }}

    /* Buttons */
    .stButton>button {{
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }}

    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }}

    /* Cards and Containers */
    .stContainer, .element-container {{
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }}

    /* Info/Warning/Success Boxes */
    .stAlert, .stSuccess, .stWarning, .stError {{
        background-color: var(--card-background) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color);
        border-radius: 10px;
    }}

    /* Login Page Specific */
    .login-container {{
        background: var(--card-background);
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color);
        margin: 2rem auto;
        max-width: 500px;
    }}

    /* Theme Toggle Button */
    .theme-toggle {{
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1001;
        background: var(--card-background);
        border: 2px solid var(--border-color);
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }}

    .theme-toggle:hover {{
        transform: rotate(30deg);
        border-color: var(--primary-color);
    }}

    /* Responsive Design */
    @media (max-width: 768px) {{
        .header-container {{
            padding: 1.5rem;
        }}
        
        .theme-toggle {{
            top: 10px;
            right: 10px;
            width: 40px;
            height: 40px;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # JavaScript for theme switching
    st.markdown("""
    <script>
    // Function to set theme
    function setTheme(theme) {{
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }}

    // Function to toggle theme
    function toggleTheme() {{
        const currentTheme = localStorage.getItem('theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
    }}

    // Initialize theme
    document.addEventListener('DOMContentLoaded', function() {{
        const savedTheme = localStorage.getItem('theme') || 'light';
        setTheme(savedTheme);
        
        // Create theme toggle button
        const toggleBtn = document.createElement('div');
        toggleBtn.className = 'theme-toggle';
        toggleBtn.innerHTML = savedTheme === 'light' ? '🌙' : '☀️';
        toggleBtn.onclick = toggleTheme;
        document.body.appendChild(toggleBtn);
    }});
    </script>
    """, unsafe_allow_html=True)

# --- HEADER COMPONENT ---
def create_header():
    current_time = datetime.now().strftime("%I:%M:%S %p")
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    
    header_html = f"""
        <div class="header-container">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <h1 style="margin: 0; font-weight: 700; font-size: 2.5rem;">🩺 Health Companion</h1>
                    <p style="margin: 0; opacity: 0.9; font-size: 1.1rem;">Your Medical Reminder & Support Assistant</p>
                </div>
                <div style="text-align: right;">
                    <h2 style="margin: 0; font-weight: 600; font-size: 1.8rem;">{current_time}</h2>
                    <p style="margin: 0; opacity: 0.9;">{current_date}</p>
                </div>
            </div>
        </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

# --- AUTHENTICATION PAGE FUNCTION ---
def show_login_register_page():
    st.markdown("""
    <div class="login-container">
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: var(--primary-color); font-weight: 700; font-size: 2.5rem;">🩺 Health Companion</h1>
            <p style="color: var(--text-color); font-size: 1.2rem; opacity: 0.8;">Your Medical Reminder & Support Assistant</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.get('just_registered', False):
        st.success("🎉 Registration successful! Please login.")
        del st.session_state['just_registered']

    # Login/Register tabs
    login_tab, register_tab = st.tabs(["**Sign In**", "**Create Account**"])
    
    with login_tab:
        with st.form("login_form", clear_on_submit=True):
            st.subheader("Welcome Back")
            email = st.text_input("📧 Email", placeholder="you@example.com", key="login_email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_password")
            
            if st.form_submit_button("🚀 Sign In", use_container_width=True, type="primary"):
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
                        st.session_state["logged_in"] = True
                        st.session_state["user_theme"] = "light"  # Default theme
                        st.toast("Login Successful! 🎉")
                        st.rerun()
                    else:
                        st.error("❌ Login Failed: Incorrect email or password.")
    
    with register_tab:
        with st.form("register_form", clear_on_submit=True):
            st.subheader("Create Account")
            full_name = st.text_input("👤 Full Name", placeholder="Enter your full name")
            new_email = st.text_input("📧 Email", placeholder="you@example.com")
            new_password = st.text_input("🔒 Create Password", type="password", placeholder="Choose a strong password")
            
            if st.form_submit_button("✨ Create Account", use_container_width=True, type="primary"):
                if not all([full_name, new_email, new_password]):
                    st.error("Please fill all fields")
                else:
                    with st.spinner("Creating your account..."):
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
                        if response is not None and response.text:
                            try: 
                                error_detail = response.json().get('detail', 'Email may already exist.')
                            except: 
                                error_detail = "Server error occurred"
                        st.error(f"❌ Registration Failed: {error_detail}")
    
    # Forgot password section
    st.markdown("</div>", unsafe_allow_html=True)
    st.write("---")
    
    if st.session_state.get("show_forgot_password", False):
        with st.form("reset_form"):
            st.subheader("Reset Password")
            email_reset = st.text_input("📧 Email Address", key="reset_email")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("📩 Send Reset Link", use_container_width=True, type="primary"):
                    if not email_reset:
                        st.error("Please enter your email")
                    else:
                        with st.spinner("Sending reset link..."):
                            response = api.post(
                                "/users/forgot-password", 
                                json={"email": email_reset}
                            )
                        
                        if response and response.status_code == 200:
                            st.success("✅ Reset link sent! Please check your email.")
                            st.session_state.show_forgot_password = False
                            st.rerun()
                        else:
                            st.error("❌ Something went wrong. Please try again.")
            
            with col2:
                if st.form_submit_button("↩️ Cancel", use_container_width=True):
                    st.session_state.show_forgot_password = False
                    st.rerun()
    else:
        if st.button("🔑 Forgot Password?", use_container_width=True, type="secondary"):
            st.session_state.show_forgot_password = True
            st.rerun()

# --- SIDEBAR COMPONENT ---
def create_sidebar():
    with st.sidebar:
        # User profile section
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">👤</div>
            <h3 style="margin: 0; color: var(--text-color);">{st.session_state.get('user_name', 'User')}</h3>
            <p style="margin: 0; opacity: 0.7; font-size: 0.9rem; color: var(--text-color);">
                {st.session_state.get('user_email', '')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation options
        st.subheader("🏥 Navigation")
        
        nav_options = [
            {"icon": "📊", "label": "Dashboard", "page": "Dashboard"},
            {"icon": "💊", "label": "Medications", "page": "Medications"},
            {"icon": "🗓️", "label": "Appointments", "page": "Appointments"},
            {"icon": "📞", "label": "Emergency Contacts", "page": "Contacts"},
            {"icon": "💡", "label": "Health Tips", "page": "Health_Tips"},
            {"icon": "⚙️", "label": "Profile & Settings", "page": "Profile"}
        ]
        
        for option in nav_options:
            if st.button(
                f"{option['icon']} {option['label']}", 
                key=f"nav_{option['page']}", 
                use_container_width=True,
                type="primary" if st.session_state.get('current_page') == option['page'] else "secondary"
            ):
                st.session_state.current_page = option['page']
                st.rerun()
        
        st.divider()
        
        # Additional actions
        st.subheader("Quick Actions")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
            
        if st.button("ℹ️ Help & Support", use_container_width=True):
            st.session_state.show_help = True
        
        st.divider()
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.toast("Logged out successfully. 👋")
            st.rerun()

# --- MAIN DASHBOARD CONTENT ---
def show_dashboard():
    create_header()
    
    # Welcome message with user's name
    user_name = st.session_state.get('user_name', 'User')
    st.markdown(f"""
    <div style="background: var(--card-background); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem; border: 1px solid var(--border-color);">
        <h2 style="margin: 0; color: var(--text-color);">👋 Welcome back, {user_name}!</h2>
        <p style="margin: 0; opacity: 0.8; color: var(--text-color);">
            Here's your health summary for {datetime.now().strftime('%A, %B %d, %Y')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats cards
    st.subheader("📊 Today's Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: var(--card-background); padding: 1.5rem; border-radius: 15px; text-align: center; border: 1px solid var(--border-color);">
            <h3 style="margin: 0 0 1rem 0; color: var(--text-color);">💊 Medications</h3>
            <p style="font-size: 2rem; font-weight: bold; margin: 0; color: var(--primary-color);">3/5</p>
            <p style="margin: 0; opacity: 0.8; color: var(--text-color);">taken today</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: var(--card-background); padding: 1.5rem; border-radius: 15px; text-align: center; border: 1px solid var(--border-color);">
            <h3 style="margin: 0 0 1rem 0; color: var(--text-color);">🗓️ Appointments</h3>
            <p style="font-size: 2rem; font-weight: bold; margin: 0; color: var(--info-color);">1</p>
            <p style="margin: 0; opacity: 0.8; color: var(--text-color);">scheduled today</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: var(--card-background); padding: 1.5rem; border-radius: 15px; text-align: center; border: 1px solid var(--border-color);">
            <h3 style="margin: 0 0 1rem 0; color: var(--text-color);">💡 Health Tip</h3>
            <p style="font-size: 1rem; margin: 0; color: var(--text-color);">
                Stay hydrated and take your medications on time for best results.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Quick actions section
    st.subheader("⚡ Quick Actions")
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("➕ Add Medication", use_container_width=True, icon="💊"):
            st.session_state.current_page = "Medications"
            st.rerun()
    
    with action_col2:
        if st.button("📅 Schedule Appointment", use_container_width=True, icon="🗓️"):
            st.session_state.current_page = "Appointments"
            st.rerun()
    
    with action_col3:
        if st.button("📞 Add Emergency Contact", use_container_width=True, icon="📞"):
            st.session_state.current_page = "Contacts"
            st.rerun()

# --- MAIN APPLICATION CONTROLLER ---
def main():
    # Apply global styles with theme support
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
    
    if "user_theme" not in st.session_state:
        st.session_state.user_theme = "light"

    # Show appropriate page based on authentication status
    if not st.session_state.get("logged_in", False):
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
