# frontend/streamlit_app.py (Final Polished Version with Centered Login & Hidden Sidebar)

import streamlit as st
import requests
import time
import os

# --- CONFIGURATION & PAGE CONFIG ---
st.set_page_config(page_title="Health Companion", layout="wide", initial_sidebar_state="collapsed")

if "API_BASE_URL" in st.secrets:
    API_BASE_URL = st.secrets["API_BASE_URL"]
else:
    API_BASE_URL = "http://127.0.0.1:8000"

# --- API CLIENT CLASS ---
class ApiClient:
    def __init__(self, base_url): self.base_url = base_url
    def _get_headers(self):
        token = st.session_state.get("token", None)
        if token: return {"Authorization": f"Bearer {token}"}
        return {}
    def _make_request(self, method, endpoint, **kwargs):
        try:
            return requests.request(method, f"{self.base_url}{endpoint}", headers=self._get_headers(), **kwargs)
        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Could not connect to the backend server."); return None
    def get(self, endpoint, params=None): return self._make_request("GET", endpoint, params=params)
    def post(self, endpoint, data=None, json=None): return self._make_request("POST", endpoint, data=data, json=json)

api = ApiClient(API_BASE_URL)


# --- STYLING FUNCTIONS ---
def apply_global_styles():
    st.markdown("""
        <style>
            /* General Font and Button styles */
            html, body, [class*="st-"], .st-emotion-cache-1avcm0n {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 18px;
            }
            .stButton > button {
                padding: 0.75rem 1.25rem !important; font-size: 1.1rem !important;
                font-weight: bold !important; border-radius: 10px !important;
                transition: all 0.2s ease-in-out;
            }
            .stButton > button:hover {
                transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1);
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
            html, body, [class*="st-"] {{ color: {text_color}; background-color: {bg_color}; }}
            .st-emotion-cache-16txtl3 {{ background-color: {secondary_bg}; }}
            .card, .st-emotion-cache-1r6slb0, .login-container {{
                background-color: {card_bg}; border: 1px solid #44444455;
            }}
            .stButton > button {{
                background-color: {primary_color} !important; color: white !important;
                border: 2px solid {primary_color} !important;
            }}
            .stButton > button:hover {{
                background-color: {hover_color} !important; border-color: {hover_color} !important;
            }}
            .stButton > button[kind="secondary"] {{
                background-color: transparent !important; color: {primary_color} !important;
            }}
            .emergency-bar {{
                background-color: #D32F2F; color: white;
                position: fixed; bottom: 0; left: 0; width: 100%; text-align: center;
                padding: 15px 0; font-size: 1.5rem; font-weight: bold;
                z-index: 1000; text-decoration: none; border-top: 3px solid #B71C1C;
            }}
            .emergency-bar:hover {{ background-color: #B71C1C; color: white; }}
        </style>
    """, unsafe_allow_html=True)


# --- HEADER COMPONENT ---
def create_header():
    theme = st.session_state.get('theme', 'light')
    header_bg = '#252526' if theme == 'dark' else 'white'
    header_html = f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; background-color: {header_bg}; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 2rem;">
            <div><h1 style="margin: 0; color: #0055a3; font-weight: 700;">Health Companion</h1><p style="margin: 0; color: #555;">Your Medical Reminder & Support Assistant</p></div>
            <div id="clock-container" style="text-align: right;"><h2 style="margin: 0; color: #0055a3; font-weight: 600;">{{time}}</h2><p style="margin: 0; color: #555;">{{date}}</p></div>
        </div>
    """
    header_placeholder = st.empty()
    while True:
        current_time = time.strftime("%I:%M:%S %p")
        current_date = time.strftime("%A, %B %d, %Y")
        header_placeholder.markdown(header_html.format(time=current_time, date=current_date), unsafe_allow_html=True)
        time.sleep(1)


# --- AUTHENTICATION PAGE FUNCTION ---
def show_login_register_page():
    st.markdown("""
        <style>
            /* Hide the sidebar on the login page */
            section[data-testid="stSidebar"] {
                display: none;
            }
            /* Use Flexbox to vertically center the login form */
            .st-emotion-cache-1y4p8pa {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<div class="login-container" style="box-shadow: 0 8px 16px rgba(0,0,0,0.1); padding: 2rem 3rem; border-radius: 15px;">', unsafe_allow_html=True)
            st.markdown(
                """
                <div style="text-align: center;">
                    <h1 style="color: #0055a3; font-weight: 700;">🩺 Welcome!</h1>
                    <p style="color: #555; font-size: 1.2rem;">Your Health Companion</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.write("")
            if st.session_state.get('just_registered', False):
                st.success("Registration successful!"); del st.session_state['just_registered']

            login_tab, register_tab = st.tabs(["**Sign In**", "**Create Account**"])
            with login_tab:
                with st.form("login_form"):
                    email = st.text_input("Email", placeholder="you@example.com")
                    password = st.text_input("Password", type="password")
                    if st.form_submit_button("Sign In", use_container_width=True):
                        with st.spinner("Authenticating..."):
                            response = api.post("/users/token", data={"username": email, "password": password})
                        if response and response.status_code == 200:
                            st.session_state["token"] = response.json()["access_token"]; st.session_state["user_email"] = email
                            st.toast("Login Successful!", icon="🎉"); st.rerun()
                        else: st.error("Login Failed: Incorrect email or password.")
            
            with register_tab:
                with st.form("register_form"):
                    full_name = st.text_input("Full Name")
                    new_email = st.text_input("Email", placeholder="you@example.com")
                    new_password = st.text_input("Create Password", type="password")
                    if st.form_submit_button("Create Account", use_container_width=True):
                        with st.spinner("Registering..."):
                            response = api.post("/users/register", json={"full_name": full_name, "email": new_email, "password": new_password})
                        if response and response.status_code == 201:
                            st.session_state['just_registered'] = True; st.rerun()
                        else:
                            error = response.json().get('detail', 'Email may already exist.') if response else "Server is down."
                            st.error(f"Registration Failed: {error}")
            
            st.write("---")
            if st.session_state.get("show_forgot_password", False):
                st.subheader("Reset Your Password")
                st.write("Enter your email, and we'll send you a reset link.")
                email_reset = st.text_input("Email Address", key="reset_email")
                c1_reset, c2_reset = st.columns(2)
                with c1_reset:
                    if st.button("Send Reset Link", use_container_width=True, type="primary"):
                        with st.spinner("Sending..."):
                            response = api.post("/users/forgot-password", json={"email": email_reset})
                        if response and response.status_code == 200:
                            st.success("Reset link sent! Please check your email."); st.session_state.show_forgot_password = False; st.rerun()
                        else: st.error("Something went wrong.")
                with c2_reset:
                    if st.button("Cancel", use_container_width=True):
                        st.session_state.show_forgot_password = False; st.rerun()
            else:
                 if st.button("Forgot Password?", type="secondary", use_container_width=True):
                    st.session_state.show_forgot_password = True; st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN APPLICATION CONTROLLER ---
def main():
    """The main gatekeeper of the application."""
    apply_global_styles()

    if "token" not in st.session_state:
        if "show_forgot_password" not in st.session_state:
            st.session_state.show_forgot_password = False
        show_login_register_page()
    else:
        # --- LOGGED-IN VIEW ---
        if 'theme' not in st.session_state:
            with st.spinner("Loading settings..."):
                response = api.get("/users/me")
            if response and response.status_code == 200:
                st.session_state['theme'] = response.json().get('theme', 'light')
            else:
                st.session_state['theme'] = 'light'
        apply_themed_styles()

        st.sidebar.title("Navigation")
        st.sidebar.markdown(f"Welcome, \n**{st.session_state.get('user_email', 'User')}**!")
        if st.sidebar.button("Logout", use_container_width=True):
            st.session_state.clear(); st.toast("Logged out successfully."); st.rerun()

        response = api.get("/contacts/")
        if response and response.status_code == 200 and response.json():
            emergency_number = response.json()[0]['phone_number']
            st.markdown(f'<a href="tel:{emergency_number}" class="emergency-bar">🚨 EMERGENCY SOS 🚨</a>', unsafe_allow_html=True)
        else:
            st.markdown(f'<a href="/Contacts" class="emergency-bar">⚠️ ADD SOS CONTACT ⚠️</a>', unsafe_allow_html=True)
        
        create_header()
        st.info("Please select a page from the sidebar to manage your health information.", icon="👈")

if __name__ == "__main__":
    main()
