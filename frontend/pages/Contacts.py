# frontend/pages/Contacts.py (Fixed with consistent login button)
import streamlit as st
import requests
import re
import os

# Page configuration
st.set_page_config(
    page_title="Emergency Contacts - Health Companion",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FIXED: Always use direct API URL ---
API_BASE_URL = "https://health-companion-backend-44ug.onrender.com"

def get_auth_headers():
    """Get authorization headers with access token"""
    if 'access_token' not in st.session_state:
        return None
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

def make_api_request(method, endpoint, **kwargs):
    """Make an API request with proper error handling"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = get_auth_headers()
    
    if headers:
        if 'headers' in kwargs:
            kwargs['headers'].update(headers)
        else:
            kwargs['headers'] = headers
    
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


# ✅ CONSISTENT LOGIN CHECK
if not st.session_state.get("logged_in", False) or not st.session_state.get("access_token"):
    st.warning("🔒 Please log in to access emergency contacts.")
    
    if st.button("🔑 Go to Login"):
        st.session_state["page"] = "login"
        st.rerun()
    
    st.stop()


# --- CSS (same as before) ---
def local_css():
    st.markdown("""
    <style>
    /* same CSS you already have */
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- Helper functions ---
def fetch_contacts():
    response = make_api_request("GET", "/contacts/")
    if response and response.status_code == 200:
        return response.json()
    return []

def create_contact(contact_data):
    headers = get_auth_headers()
    if not headers:
        return False, "Not authenticated"
    response = make_api_request("POST", "/contacts/", json=contact_data, headers=headers)
    if response and response.status_code == 201:
        return True, response.json()
    return False, "Failed to create contact"

def update_contact(contact_id, contact_data):
    headers = get_auth_headers()
    if not headers:
        return False, "Not authenticated"
    response = make_api_request("PUT", f"/contacts/{contact_id}", json=contact_data, headers=headers)
    if response and response.status_code == 200:
        return True, response.json()
    return False, "Failed to update contact"

def delete_contact(contact_id):
    headers = get_auth_headers()
    if not headers:
        return False
    response = make_api_request("DELETE", f"/contacts/{contact_id}", headers=headers)
    return response and response.status_code == 204

def validate_phone_number(phone):
    phone = re.sub(r'\D', '', phone)
    if len(phone) not in [10, 11]:
        return False, "Phone number should be 10-11 digits"
    return True, phone

def make_call(phone_number):
    st.success(f"📞 Calling {phone_number}...")

def send_sms(phone_number):
    st.success(f"💬 Opening SMS to {phone_number}...")


# --- Page UI ---
if 'edit_contact' not in st.session_state:
    st.session_state.edit_contact = None
if 'show_form' not in st.session_state:
    st.session_state.show_form = False

st.title("📞 Emergency Contacts")
st.markdown("Manage your emergency contacts for quick access during urgent situations")

contacts = fetch_contacts()

# --- FORM & LIST UI (same as your code) ---
# ✅ Here you can keep the same Add/Edit/Display logic as you already have
# (no changes needed except the login fix above)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Health Companion - Senior Citizen Care App</div>", unsafe_allow_html=True)
