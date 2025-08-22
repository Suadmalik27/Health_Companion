# frontend/pages/Contacts.py

import streamlit as st
import requests
import re
from PIL import Image
import io
import base64
import os
from config import get_api_base_url, get_auth_headers, make_api_request

# Page configuration
st.set_page_config(
    page_title="Emergency Contacts - Health Companion",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get API URL from secrets or use default
API_BASE_URL = st.secrets.get( "https://health-companion-backend-44ug.onrender.com")

# Custom CSS for styling
def local_css():
    st.markdown("""
    <style>
    .contacts-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1.5rem;
        margin-top: 1.5rem;
    }
    .contact-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 4px solid #FF5252;
        position: relative;
    }
    .contact-card.primary {
        border-left: 4px solid #FF0000;
        background: linear-gradient(135deg, #fff5f5 0%, #ffe5e5 100%);
    }
    .contact-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    }
    .contact-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .contact-name {
        font-size: 1.25rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
    }
    .contact-relationship {
        background: #ffebee;
        color: #c62828;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .contact-phone {
        color: #1565c0;
        font-size: 1.1rem;
        font-weight: 500;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .contact-actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    .sos-badge {
        position: absolute;
        top: -10px;
        right: -10px;
        background: #ff0000;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(255, 0, 0, 0.3);
    }
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #78909c;
    }
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    .form-container {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    .stButton button {
        border-radius: 20px;
        padding: 0.5rem 1.5rem;
    }
    .quick-action-btn {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-bottom: 0.5rem;
    }
    .quick-action-btn:hover {
        background: #e9ecef;
        transform: translateY(-2px);
    }
    .limit-warning {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

def get_auth_headers():
    """Get authorization headers with access token"""
    if 'access_token' not in st.session_state:
        return None
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

def fetch_contacts():
    """Fetch user's emergency contacts"""
    headers = get_auth_headers()
    if not headers:
        return []
    
    try:
        response = requests.get(f"{API_BASE_URL}/contacts/", headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching contacts: {str(e)}")
        return []

def create_contact(contact_data):
    """Create a new emergency contact"""
    headers = get_auth_headers()
    if not headers:
        return False, "Not authenticated"
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/contacts/",
            json=contact_data,
            headers=headers
        )
        if response.status_code == 201:
            return True, response.json()
        return False, response.json().get("detail", "Failed to create contact")
    except Exception as e:
        return False, f"Error: {str(e)}"

def update_contact(contact_id, contact_data):
    """Update an existing contact"""
    headers = get_auth_headers()
    if not headers:
        return False, "Not authenticated"
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/contacts/{contact_id}",
            json=contact_data,
            headers=headers
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json().get("detail", "Failed to update contact")
    except Exception as e:
        return False, f"Error: {str(e)}"

def delete_contact(contact_id):
    """Delete a contact"""
    headers = get_auth_headers()
    if not headers:
        return False
    
    try:
        response = requests.delete(
            f"{API_BASE_URL}/contacts/{contact_id}",
            headers=headers
        )
        return response.status_code == 204
    except Exception as e:
        st.error(f"Error deleting contact: {str(e)}")
        return False

def validate_phone_number(phone):
    """Validate phone number format"""
    # Remove any non-digit characters
    phone = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (10 digits for most countries)
    if len(phone) not in [10, 11]:
        return False, "Phone number should be 10-11 digits"
    
    return True, phone

def make_call(phone_number):
    """Simulate making a phone call"""
    st.success(f"📞 Calling {phone_number}...")
    # In a real app, this would trigger the device's phone dialer

def send_sms(phone_number):
    """Simulate sending an SMS"""
    st.success(f"💬 Opening SMS to {phone_number}...")
    # In a real app, this would trigger the device's SMS app

# Check if user is logged in
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access emergency contacts")
    st.stop()

# Initialize session state
if 'edit_contact' not in st.session_state:
    st.session_state.edit_contact = None
if 'show_form' not in st.session_state:
    st.session_state.show_form = False

# Page header
st.title("📞 Emergency Contacts")
st.markdown("Manage your emergency contacts for quick access during urgent situations")

# Fetch contacts
contacts = fetch_contacts()

# Add/Edit Contact Form
if st.session_state.show_form:
    st.markdown("### 📝 " + ("Edit Contact" if st.session_state.edit_contact else "Add New Contact"))
    
    with st.form("contact_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Contact Name", 
                               value=st.session_state.edit_contact.get('name', '') if st.session_state.edit_contact else "",
                               placeholder="e.g., John Smith, Dr. Miller")
            relationship = st.text_input("Relationship",
                                       value=st.session_state.edit_contact.get('relationship_type', '') if st.session_state.edit_contact else "",
                                       placeholder="e.g., Son, Doctor, Neighbor")
        
        with col2:
            phone_number = st.text_input("Phone Number",
                                       value=st.session_state.edit_contact.get('phone_number', '') if st.session_state.edit_contact else "",
                                       placeholder="e.g., 555-123-4567")
        
        submitted = st.form_submit_button("💾 Save Contact")
        
        if submitted:
            if not name or not phone_number:
                st.error("Please provide contact name and phone number")
            else:
                # Validate phone number
                is_valid, phone_validation = validate_phone_number(phone_number)
                if not is_valid:
                    st.error(phone_validation)
                else:
                    contact_data = {
                        "name": name,
                        "phone_number": phone_validation,
                        "relationship_type": relationship
                    }
                    
                    if st.session_state.edit_contact:
                        success, result = update_contact(st.session_state.edit_contact['id'], contact_data)
                    else:
                        # Check contact limit (5 contacts max)
                        if len(contacts) >= 5:
                            st.error("Cannot add more than 5 emergency contacts")
                        else:
                            success, result = create_contact(contact_data)
                    
                    if success:
                        st.success("Contact saved successfully!")
                        st.session_state.show_form = False
                        st.session_state.edit_contact = None
                        st.rerun()
                    else:
                        st.error(f"Error saving contact: {result}")
    
    if st.button("← Back to contacts"):
        st.session_state.show_form = False
        st.session_state.edit_contact = None
        st.rerun()

else:
    # Action buttons and info
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.info("💡 Add emergency contacts for quick access during urgent situations")
        
        # Show contact limit warning if approaching limit
        if len(contacts) >= 4:
            st.markdown(f"""
            <div class="limit-warning">
                ⚠️ You have {len(contacts)} out of 5 emergency contacts. 
                {f"Only {5 - len(contacts)} more can be added." if len(contacts) < 5 else "Maximum limit reached."}
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if st.button("➕ Add New Contact", use_container_width=True, disabled=len(contacts) >= 5):
            st.session_state.show_form = True
            st.session_state.edit_contact = None
            st.rerun()

    # Quick SOS Section
    if contacts:
        st.markdown("### 🚨 Quick Emergency Actions")
        sos_col1, sos_col2, sos_col3 = st.columns(3)
        
        primary_contact = contacts[0]  # First contact is considered primary
        
        with sos_col1:
            st.markdown(f"""
            <div class="quick-action-btn" onclick="alert('Calling {primary_contact['name']}...')">
                📞 Call {primary_contact['name']}
            </div>
            """, unsafe_allow_html=True)
            
        with sos_col2:
            st.markdown(f"""
            <div class="quick-action-btn" onclick="alert('Messaging {primary_contact['name']}...')">
                💬 SMS {primary_contact['name']}
            </div>
            """, unsafe_allow_html=True)
            
        with sos_col3:
            st.markdown(f"""
            <div class="quick-action-btn" onclick="alert('Emergency alert sent to all contacts!')">
                📢 Alert All Contacts
            </div>
            """, unsafe_allow_html=True)

    # Contacts Grid
    if contacts:
        st.markdown(f"### 📋 Your Emergency Contacts ({len(contacts)}/5)")
        
        st.markdown('<div class="contacts-grid">', unsafe_allow_html=True)
        
        for i, contact in enumerate(contacts):
            is_primary = i == 0  # First contact is primary
            
            # Format phone number for display
            phone = contact['phone_number']
            if len(phone) == 10:
                formatted_phone = f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
            else:
                formatted_phone = phone
            
            contact_html = f"""
            <div class="contact-card {'primary' if is_primary else ''}">
                {f'<div class="sos-badge">PRIMARY</div>' if is_primary else ''}
                <div class="contact-header">
                    <h3 class="contact-name">{contact['name']}</h3>
                    <span class="contact-relationship">{contact.get('relationship_type', 'Contact')}</span>
                </div>
                <div class="contact-phone">
                    📞 {formatted_phone}
                </div>
            </div>
            """
            
            st.markdown(contact_html, unsafe_allow_html=True)
            
            # Action buttons for each contact
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📞 Call", key=f"call_{contact['id']}", use_container_width=True):
                    make_call(formatted_phone)
            
            with col2:
                if st.button("💬 SMS", key=f"sms_{contact['id']}", use_container_width=True):
                    send_sms(formatted_phone)
            
            with col3:
                if st.button("✏️ Edit", key=f"edit_{contact['id']}", use_container_width=True):
                    st.session_state.edit_contact = contact
                    st.session_state.show_form = True
                    st.rerun()
            
            with col4:
                if st.button("🗑️ Delete", key=f"delete_{contact['id']}", use_container_width=True):
                    if delete_contact(contact['id']):
                        st.success("Contact deleted successfully")
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Contact management tips
        st.markdown("---")
        st.markdown("### 💡 Tips for Emergency Contacts")
        
        tip_col1, tip_col2, tip_col3 = st.columns(3)
        
        with tip_col1:
            st.info("""
            **Primary Contact**  
            The first contact is your primary emergency contact. 
            They will be called first in SOS situations.
            """)
        
        with tip_col2:
            st.info("""
            **Contact Types**  
            Include different types of contacts:
            - Family members
            - Doctors
            - Neighbors
            - Close friends
            """)
        
        with tip_col3:
            st.info("""
            **Keep Updated**  
            Regularly review and update your emergency contacts 
            to ensure they're current and reachable.
            """)
    
    else:
        # Empty state
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📞</div>
            <h3>No emergency contacts yet</h3>
            <p>Add your first emergency contact for quick access during urgent situations</p>
            <p>Click the "Add New Contact" button to begin</p>
        </div>
        """, unsafe_allow_html=True)

# Emergency Preparedness Section
st.markdown("---")
st.markdown("### 🚑 Emergency Preparedness")

prep_col1, prep_col2, prep_col3 = st.columns(3)

with prep_col1:
    st.warning("""
    **Medical Information**  
    Ensure your emergency contacts know about:
    - Your medical conditions
    - Current medications
    - Allergies
    - Doctor's contact information
    """)

with prep_col2:
    st.warning("""
    **Emergency Plan**  
    Discuss with your contacts:
    - Where to meet in emergencies
    - Who to contact first
    - How to access your home
    - Location of important documents
    """)

with prep_col3:
    st.warning("""
    **Regular Testing**  
    Periodically test your emergency contacts:
    - Make test calls
    - Send test messages
    - Verify they can respond quickly
    - Update numbers if needed
    """)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Health Companion - Senior Citizen Care App</div>", unsafe_allow_html=True)

# JavaScript for actual phone functionality (would work in a mobile app context)
st.markdown("""
<script>
function makeCall(phoneNumber) {
    // This would work in a mobile app or with appropriate permissions
    window.location.href = 'tel:' + phoneNumber;
}

function sendSMS(phoneNumber) {
    // This would work in a mobile app or with appropriate permissions
    window.location.href = 'sms:' + phoneNumber;
}
</script>
""", unsafe_allow_html=True)
