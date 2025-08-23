# frontend/pages/Medications.py (Fixed - No config import)

import streamlit as st
import requests
from datetime import datetime, time
import io
from PIL import Image
import base64
import os

# Page configuration
st.set_page_config(
    page_title="Medications - Health Companion",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get API base URL directly
def get_api_base_url():
    """Get the API base URL from secrets, environment variables, or use default"""
    try:
        return st.secrets["API_BASE_URL1"]
    except:
        try:
            return os.environ.get("https://health-companion-backend-44ug.onrender.com")
        except:
            return "https://health-companion-backend-44ug.onrender.com"

def get_auth_headers():
    """Get authorization headers with access token"""
    if 'access_token' not in st.session_state:
        return None
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

def make_api_request(method, endpoint, **kwargs):
    """Make an API request with proper error handling"""
    base_url = get_api_base_url()
    url = f"{base_url}{endpoint}"
    headers = get_auth_headers()
    
    if headers:
        if 'headers' in kwargs:
            kwargs['headers'].update(headers)
        else:
            kwargs['headers'] = headers
    
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
    .medication-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1.5rem;
        margin-top: 1.5rem;
    }
    .medication-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 4px solid #4CAF50;
    }
    .medication-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    }
    .medication-image {
        width: 100%;
        height: 150px;
        object-fit: cover;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .medication-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .medication-name {
        font-size: 1.25rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
    }
    .medication-dosage {
        background: #e8f5e9;
        color: #2e7d32;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .medication-time {
        background: #e3f2fd;
        color: #1565c0;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        display: inline-block;
    }
    .medication-status {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    .status-active {
        background: #e8f5e9;
        color: #2e7d32;
    }
    .status-inactive {
        background: #ffebee;
        color: #c62828;
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
    .action-buttons {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

def fetch_medications():
    """Fetch user's medications"""
    response = make_api_request("GET", "/medications/")
    if response and response.status_code == 200:
        return response.json()
    return []

def create_medication(medication_data):
    """Create a new medication"""
    headers = get_auth_headers()
    if not headers:
        return False, "Not authenticated"
    
    response = make_api_request("POST", "/medications/", json=medication_data, headers=headers)
    if response and response.status_code == 201:
        return True, response.json()
    return False, "Failed to create medication"

def update_medication(medication_id, medication_data):
    """Update an existing medication"""
    headers = get_auth_headers()
    if not headers:
        return False, "Not authenticated"
    
    response = make_api_request("PUT", f"/medications/{medication_id}", json=medication_data, headers=headers)
    if response and response.status_code == 200:
        return True, response.json()
    return False, "Failed to update medication"

def delete_medication(medication_id):
    """Delete a medication"""
    headers = get_auth_headers()
    if not headers:
        return False
    
    response = make_api_request("DELETE", f"/medications/{medication_id}", headers=headers)
    return response and response.status_code == 204

def upload_medication_photo(medication_id, file):
    """Upload photo for a medication"""
    headers = get_auth_headers()
    if not headers:
        return False
    
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = make_api_request("PUT", f"/medications/{medication_id}/photo", files=files, headers=headers)
        return response and response.status_code == 200
    except Exception as e:
        st.error(f"Error uploading photo: {str(e)}")
        return False

def get_medication_log():
    """Get today's medication log"""
    today = datetime.now().date().isoformat()
    response = make_api_request("GET", f"/medications/log/{today}")
    if response and response.status_code == 200:
        return response.json()
    return []

def log_medication_taken(medication_id):
    """Log that a medication was taken"""
    headers = get_auth_headers()
    if not headers:
        return False
    
    response = make_api_request("POST", f"/medications/{medication_id}/log", headers=headers)
    return response and response.status_code == 201

# Check if user is logged in
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access medications")
    st.stop()

# Initialize session state
if 'edit_medication' not in st.session_state:
    st.session_state.edit_medication = None
if 'show_form' not in st.session_state:
    st.session_state.show_form = False

# Page header
st.title("💊 Medication Management")
st.markdown("Manage your medications, set reminders, and track your daily intake")

# Fetch data
medications = fetch_medications()
medication_log = get_medication_log()
taken_meds = set(medication_log)

# Add/Edit Medication Form
if st.session_state.show_form:
    st.markdown("### 📝 " + ("Edit Medication" if st.session_state.edit_medication else "Add New Medication"))
    
    with st.form("medication_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Medication Name", 
                               value=st.session_state.edit_medication.get('name', '') if st.session_state.edit_medication else "",
                               placeholder="e.g., Metformin, Lisinopril")
            dosage = st.text_input("Dosage",
                                 value=st.session_state.edit_medication.get('dosage', '') if st.session_state.edit_medication else "",
                                 placeholder="e.g., 500mg, 10mg once daily")
        
        with col2:
            # Handle time input
            default_time = time(9, 0)
            if st.session_state.edit_medication and st.session_state.edit_medication.get('timing'):
                try:
                    if isinstance(st.session_state.edit_medication['timing'], str):
                        if 'T' in st.session_state.edit_medication['timing']:
                            default_time = datetime.fromisoformat(
                                st.session_state.edit_medication['timing'].replace('Z', '+00:00')
                            ).time()
                        else:
                            default_time = datetime.strptime(
                                st.session_state.edit_medication['timing'], "%H:%M:%S"
                            ).time()
                except:
                    pass
            
            timing = st.time_input("Time to take", value=default_time)
            is_active = st.checkbox("Active", value=st.session_state.edit_medication.get('is_active', True) if st.session_state.edit_medication else True)
        
        # Photo upload
        if st.session_state.edit_medication and st.session_state.edit_medication.get('photo_url'):
            try:
                photo_url = st.session_state.edit_medication['photo_url']
                if photo_url.startswith('/'):
                    photo_url = f"{get_api_base_url()}{photo_url}"
                response = requests.get(photo_url, timeout=10)
                if response.status_code == 200:
                    img = Image.open(io.BytesIO(response.content))
                    st.image(img, caption="Current Photo", width=200)
            except:
                st.write("Could not load current photo")
        
        photo_file = st.file_uploader("Upload medication photo (optional)", type=['jpg', 'jpeg', 'png'])
        
        submitted = st.form_submit_button("💾 Save Medication")
        
        if submitted:
            if not name or not dosage:
                st.error("Please provide medication name and dosage")
            else:
                medication_data = {
                    "name": name,
                    "dosage": dosage,
                    "timing": timing.strftime("%H:%M:%S"),
                    "is_active": is_active
                }
                
                if st.session_state.edit_medication:
                    success, result = update_medication(st.session_state.edit_medication['id'], medication_data)
                else:
                    success, result = create_medication(medication_data)
                
                if success:
                    # Upload photo if provided
                    if photo_file:
                        medication_id = st.session_state.edit_medication['id'] if st.session_state.edit_medication else result['id']
                        upload_success = upload_medication_photo(medication_id, photo_file)
                        if upload_success:
                            st.success("Photo uploaded successfully!")
                    
                    st.success("Medication saved successfully!")
                    st.session_state.show_form = False
                    st.session_state.edit_medication = None
                    st.rerun()
                else:
                    st.error(f"Error saving medication: {result}")
    
    if st.button("← Back to medications"):
        st.session_state.show_form = False
        st.session_state.edit_medication = None
        st.rerun()

else:
    # Action buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.info("💡 Add your medications to get reminders and track your intake")
    
    with col3:
        if st.button("➕ Add New Medication", use_container_width=True):
            st.session_state.show_form = True
            st.session_state.edit_medication = None
            st.rerun()

    # Medications Grid
    if medications:
        st.markdown(f"### 📋 Your Medications ({len(medications)})")
        
        # Filter buttons
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            show_all = st.button("All", use_container_width=True)
        with col2:
            show_active = st.button("Active", use_container_width=True)
        with col3:
            show_inactive = st.button("Inactive", use_container_width=True)
        
        # Filter medications based on selection
        filtered_medications = medications
        if show_active:
            filtered_medications = [m for m in medications if m.get('is_active', True)]
        elif show_inactive:
            filtered_medications = [m for m in medications if not m.get('is_active', True)]
        
        if not filtered_medications:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">💊</div>
                <h3>No medications found</h3>
                <p>Try changing your filters or add new medications</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display medications in a grid
            st.markdown('<div class="medication-grid">', unsafe_allow_html=True)
            
            for med in filtered_medications:
                # Parse time
                med_time = None
                if isinstance(med['timing'], str):
                    if 'T' in med['timing']:
                        med_time = datetime.fromisoformat(med['timing'].replace('Z', '+00:00')).time()
                    else:
                        med_time = datetime.strptime(med['timing'], "%H:%M:%S").time()
                else:
                    med_time = med['timing']
                
                time_format = st.session_state.get('time_format', '12h')
                time_str = med_time.strftime("%I:%M %p") if time_format == '12h' else med_time.strftime("%H:%M")
                
                # Check if taken today
                is_taken = med['id'] in taken_meds
                
                # Create medication card
                card_html = f"""
                <div class="medication-card">
                    <div class="medication-header">
                        <h3 class="medication-name">{med['name']}</h3>
                        <span class="medication-dosage">{med['dosage']}</span>
                    </div>
                """
                
                # Add image if available
                if med.get('photo_url'):
                    try:
                        photo_url = med['photo_url']
                        if photo_url.startswith('/'):
                            photo_url = f"{get_api_base_url()}{photo_url}"
                        response = requests.get(photo_url, timeout=10)
                        if response.status_code == 200:
                            img = Image.open(io.BytesIO(response.content))
                            buffered = io.BytesIO()
                            img.save(buffered, format="JPEG")
                            img_str = base64.b64encode(buffered.getvalue()).decode()
                            card_html += f'<img src="data:image/jpeg;base64,{img_str}" class="medication-image">'
                    except Exception as e:
                        # Silently fail if image can't be loaded
                        pass
                
                card_html += f"""
                    <div class="medication-time">⏰ {time_str}</div>
                    <div class="medication-status {'status-active' if med.get('is_active', True) else 'status-inactive'}">
                        {'Active' if med.get('is_active', True) else 'Inactive'}
                    </div>
                    {"<div class='medication-status status-active'>✅ Taken today</div>" if is_taken else ""}
                </div>
                """
                
                st.markdown(card_html, unsafe_allow_html=True)
                
                # Action buttons for each medication
                col1, col2, col3 = st.columns(3)
                with col1:
                    if not is_taken and med.get('is_active', True):
                        if st.button("✅ Mark Taken", key=f"take_{med['id']}"):
                            if log_medication_taken(med['id']):
                                st.success(f"Marked {med['name']} as taken")
                                st.rerun()
                with col2:
                    if st.button("✏️ Edit", key=f"edit_{med['id']}"):
                        st.session_state.edit_medication = med
                        st.session_state.show_form = True
                        st.rerun()
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{med['id']}"):
                        if delete_medication(med['id']):
                            st.success("Medication deleted successfully")
                            st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Empty state
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">💊</div>
            <h3>No medications yet</h3>
            <p>Add your first medication to get started with tracking</p>
            <p>Click the "Add New Medication" button to begin</p>
        </div>
        """, unsafe_allow_html=True)

# Statistics section
if medications:
    st.markdown("---")
    st.markdown("### 📊 Medication Statistics")
    
    active_meds = [m for m in medications if m.get('is_active', True)]
    inactive_meds = [m for m in medications if not m.get('is_active', True)]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Medications", len(medications))
    with col2:
        st.metric("Active Medications", len(active_meds))
    with col3:
        st.metric("Inactive Medications", len(inactive_meds))
    with col4:
        st.metric("Taken Today", len(taken_meds))

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Health Companion - Senior Citizen Care App</div>", unsafe_allow_html=True)
