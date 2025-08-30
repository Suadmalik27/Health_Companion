# frontend/pages/Emergency_Contacts.py (VERSION 3.0 - MODERN & SAFE)

import streamlit as st
from streamlit_cookies_manager import CookieManager

from auth.service import (
    TOKEN_COOKIE_NAME,
    get_contacts,
    add_contact,
    delete_contact
)
from components.sidebar import authenticated_sidebar

# --- 1. PAGE CONFIGURATION & AUTHENTICATION ---
st.set_page_config(page_title="Manage Emergency Contacts", page_icon="📞", layout="wide")

cookies = CookieManager()
if not cookies.ready():
    st.spinner("Initializing...")
    st.stop()

token = cookies.get(TOKEN_COOKIE_NAME)
if not token:
    st.warning("🔒 You are not logged in. Please log in to continue.")
    st.stop()

authenticated_sidebar(cookies)

# --- 2. CUSTOM STYLING ---
st.markdown("""
<style>
    /* --- Main Content Card Styling --- */
    .content-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #E0E0E0;
        padding: 2rem;
        margin-bottom: 1.5rem;
    }
    /* Styling for each contact item in the list */
    .contact-item {
        padding: 1rem;
        border-bottom: 1px solid #f0f0f0;
    }
    .contact-item:last-child {
        border-bottom: none;
    }
</style>
""", unsafe_allow_html=True)


# --- 3. STATE MANAGEMENT for Delete Confirmation ---
if 'confirming_delete_contact_id' not in st.session_state:
    st.session_state.confirming_delete_contact_id = None

# --- 4. DATA FETCHING ---
@st.cache_data(show_spinner="Loading your contacts...")
def load_contacts_data(token_param):
    is_success, contacts_data = get_contacts(token_param)
    if not is_success:
        st.error(f"Could not load contacts: {contacts_data}")
        return []
    return contacts_data

contacts = load_contacts_data(token)

# --- 5. PAGE UI ---
st.title("📞 Manage Your Emergency Contacts")
st.markdown("Here you can add or remove your important contacts for quick access during an emergency.")
st.markdown("---")

# --- Form to Add a New Contact ---
st.markdown('<div class="content-card">', unsafe_allow_html=True)
with st.expander("➕ Add a New Contact", expanded=True):
    with st.form("new_contact_form", clear_on_submit=True):
        st.subheader("New Contact Details")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            contact_name = st.text_input("Contact's Full Name", placeholder="e.g., Kumar Sharma")
        with c2:
            phone_number = st.text_input("Phone Number", placeholder="e.g., 9876543210")
        with c3:
            relationship = st.text_input("Relationship", placeholder="e.g., Son, Doctor")

        submitted = st.form_submit_button("Add Contact to List", use_container_width=True, type="primary")
        if submitted:
            if not contact_name or not phone_number:
                st.warning("Please fill in the Contact Name and Phone Number.")
            else:
                payload = {
                    "contact_name": contact_name,
                    "phone_number": phone_number,
                    "relationship_type": relationship
                }
                is_success, message = add_contact(token, payload)
                if is_success:
                    st.success("Contact added successfully!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"Failed to add contact: {message}")
st.markdown('</div>', unsafe_allow_html=True)


# --- Display Existing Contacts ---
st.markdown('<div class="content-card">', unsafe_allow_html=True)
st.subheader("Your Saved Contact List")
if not contacts:
    st.info("You haven't added any contacts yet. Use the form above to add one.")
else:
    for contact in reversed(contacts): # Show newest contacts first
        contact_id = contact['id']
        
        st.markdown("<div class='contact-item'>", unsafe_allow_html=True)
        
        if st.session_state.confirming_delete_contact_id == contact_id:
            st.warning(f"**Are you sure you want to delete {contact['contact_name']}?**")
            del_cols = st.columns([1, 1, 4])
            with del_cols[0]:
                if st.button("✅ Yes, Delete", key=f"conf_contact_{contact_id}", use_container_width=True, type="primary"):
                    del_success, del_message = delete_contact(token, contact_id)
                    st.session_state.confirming_delete_contact_id = None
                    if del_success:
                        st.success(del_message)
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(del_message)
            with del_cols[1]:
                if st.button("❌ No, Cancel", key=f"cancel_contact_{contact_id}", use_container_width=True):
                    st.session_state.confirming_delete_contact_id = None
                    st.rerun()
        else:
            main_cols = st.columns([2, 2, 1, 1])
            with main_cols[0]:
                st.markdown(f"**{contact['contact_name']}**")
            with main_cols[1]:
                st.markdown(f"_{contact.get('relationship_type', 'Contact')}_")
            with main_cols[2]:
                st.link_button(f"📞 Call", f"tel:{contact['phone_number']}", use_container_width=True)
            with main_cols[3]:
                if st.button("Delete", key=f"del_contact_{contact_id}", use_container_width=True):
                    st.session_state.confirming_delete_contact_id = contact_id
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

