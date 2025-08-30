# frontend/pages/Admin_Tips.py (UPDATED WITH API FUNCTIONS)

import streamlit as st
from streamlit_cookies_manager import CookieManager
import requests # API calls ke liye zaroori hai

# --- FIX: Galti se import kiye gaye functions ko hatana ---
from auth.service import TOKEN_COOKIE_NAME
from components.sidebar import authenticated_sidebar

# --- 1. PAGE CONFIGURATION & AUTHENTICATION ---
st.set_page_config(page_title="Manage Health Tips", page_icon="💡", layout="wide")

cookies = CookieManager()
if not cookies.ready():
    st.spinner("Initializing...")
    st.stop()

token = cookies.get(TOKEN_COOKIE_NAME)
if not token:
    st.warning("🔒 You are not logged in. Please log in to continue.")
    st.stop()

authenticated_sidebar(cookies)

# --- NAYA SECTION: API SERVICE FUNCTIONS (ERROR KA FIX) ---
# Yeh functions aam taur par auth/service.py mein hone chahiye,
# lekin error theek karne ke liye inhein yahan joda gaya hai.

API_BASE_URL = "http://127.0.0.1:8080" # Isko production mein settings se lena chahiye

def get_all_tips(token: str):
    """ Backend se saari health tips ko fetch karta hai. """
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/tips/", headers=headers)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json().get("detail", "Unknown error")
    except requests.exceptions.RequestException as e:
        return False, f"Server communication error: {e}"

def add_health_tip(token: str, payload: dict):
    """ Backend mein ek nayi health tip add karta hai. """
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/tips/", headers=headers, json=payload)
        # HTTP 201 ka matlab hai "Created" (safalta se ban gaya)
        if response.status_code == 201:
            return True, response.json()
        else:
            return False, response.json().get("detail", "Failed to add tip")
    except requests.exceptions.RequestException as e:
        return False, f"Server communication error: {e}"

def delete_health_tip(token: str, tip_id: int):
    """ Backend se ek specific health tip ko delete karta hai. """
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.delete(f"{API_BASE_URL}/api/v1/tips/{tip_id}", headers=headers)
        if response.status_code == 200:
            return True, "Tip deleted successfully."
        else:
            return False, response.json().get("detail", "Failed to delete tip")
    except requests.exceptions.RequestException as e:
        return False, f"Server communication error: {e}"

# Asli application mein, yahan user ka role (e.g., 'admin') check karna chahiye
# user_profile = get_user_profile(token)
# if user_profile.get('role') != 'admin':
#     st.error("You do not have permission to access this page.")
#     st.stop()


# --- 2. DATA FETCHING ---
@st.cache_data(show_spinner="Loading all health tips...")
def load_tips_data(token_param):
    """ Backend se saari health tips ko fetch karta hai. """
    is_success, tips_data = get_all_tips(token_param)
    if not is_success:
        st.error(f"Could not load health tips: {tips_data}")
        return []
    return tips_data

all_tips = load_tips_data(token)

# --- 3. PAGE UI ---
st.title("💡 Manage Health Tips")
st.markdown("Is page ka istemal karke aap users ko unke dashboard par dikhne wali health tips ko jod ya hata sakte hain.")
st.markdown("---")

# Nayi tip add karne ka form
with st.expander("➕ Add a New Health Tip", expanded=True):
    with st.form("new_tip_form", clear_on_submit=True):
        st.subheader("New Tip Details")
        
        tip_text = st.text_area(
            "Tip Text", 
            placeholder="e.g., Drink at least 8 glasses of water daily to stay hydrated.", 
            height=150
        )
        
        category = st.text_input(
            "Category", 
            value="General", 
            help="e.g., Diet, Exercise, Mental Health"
        )
        
        submitted = st.form_submit_button("Add Health Tip to Database")
        if submitted:
            if tip_text and len(tip_text) > 10:
                payload = {"tip_text": tip_text, "category": category}
                is_added, msg = add_health_tip(token, payload)
                if is_added:
                    st.success("Health tip added successfully!")
                    st.cache_data.clear() # Cache clear karna zaroori hai
                    st.rerun()
                else:
                    st.error(f"Failed to add tip: {msg}")
            else:
                st.warning("Please enter a tip that is at least 10 characters long.")

st.markdown("---")

# Pehle se maujood tips ko display karna
st.subheader("All Saved Health Tips in the Database")
if not all_tips:
    st.info("There are no health tips in the database yet. Add one using the form above.")
else:
    for tip in reversed(all_tips): # reversed() taaki nayi tip sabse upar dikhe
        with st.container(border=True):
            cols = st.columns([4, 1])
            with cols[0]:
                st.markdown(f"**[{tip.get('category', 'General')}]**")
                st.write(tip['tip_text'])
            with cols[1]:
                if st.button("Delete Tip", key=f"del_tip_{tip['id']}", use_container_width=True, type="primary"):
                    is_deleted, msg = delete_health_tip(token, tip['id'])
                    if is_deleted:
                        st.success("Tip deleted successfully!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"Failed to delete: {msg}")

