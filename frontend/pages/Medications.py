# frontend/pages/Medications.py

import streamlit as st
import requests
from datetime import datetime, time
import io
from PIL import Image
import base64

# Page configuration
st.set_page_config(
    page_title="Medications - Health Companion",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Always fixed API URL ---
def get_api_base_url():
    return "https://health-companion-backend-44ug.onrender.com"

def get_auth_headers():
    """Get authorization headers with access token"""
    if 'access_token' not in st.session_state:
        return None
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

def make_api_request(method, endpoint, **kwargs):
    """Make an API request with auth + error handling"""
    base_url = get_api_base_url()
    url = f"{base_url}{endpoint}"
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
        st.error("❌ Cannot connect to server")
        return None
    except requests.exceptions.Timeout:
        st.error("⏳ Request timed out")
        return None
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
        return None


# ---------------- Custom CSS ----------------
def local_css():
    st.markdown("""<style>
    .medication-grid {display: grid;grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));gap: 1.5rem;margin-top: 1.5rem;}
    .medication-card {background: white;border-radius: 12px;padding: 1.5rem;box-shadow: 0 4px 12px rgba(0,0,0,0.1);border-left: 4px solid #4CAF50;}
    .medication-card:hover {transform: translateY(-5px);box-shadow: 0 8px 24px rgba(0,0,0,0.15);}
    .medication-image {width: 100%;height: 150px;object-fit: cover;border-radius: 8px;margin-bottom: 1rem;}
    .medication-header {display: flex;justify-content: space-between;align-items: center;margin-bottom: 1rem;}
    .medication-name {font-size: 1.25rem;font-weight: bold;color: #2c3e50;margin: 0;}
    .medication-dosage {background: #e8f5e9;color: #2e7d32;padding: 0.25rem 0.75rem;border-radius: 20px;font-size: 0.9rem;}
    .medication-time {background: #e3f2fd;color: #1565c0;padding: 0.25rem 0.75rem;border-radius: 20px;font-size: 0.9rem;margin-top: 0.5rem;display: inline-block;}
    .status-active {background: #e8f5e9;color: #2e7d32;}
    .status-inactive {background: #ffebee;color: #c62828;}
    .empty-state {text-align: center;padding: 3rem;color: #78909c;}
    .empty-state-icon {font-size: 4rem;margin-bottom: 1rem;}
    .form-container {background: white;padding: 2rem;border-radius: 12px;box-shadow: 0 4px 12px rgba(0,0,0,0.1);margin-bottom: 2rem;}
    </style>""", unsafe_allow_html=True)

local_css()

# ---------------- API Wrappers ----------------
def fetch_medications():
    r = make_api_request("GET", "/medications/")
    return r.json() if r and r.status_code == 200 else []

def create_medication(data):
    if not get_auth_headers(): return False, "Not authenticated"
    r = make_api_request("POST", "/medications/", json=data)
    return (True, r.json()) if r and r.status_code == 201 else (False, "Failed to create medication")

def update_medication(med_id, data):
    if not get_auth_headers(): return False, "Not authenticated"
    r = make_api_request("PUT", f"/medications/{med_id}", json=data)
    return (True, r.json()) if r and r.status_code == 200 else (False, "Failed to update medication")

def delete_medication(med_id):
    if not get_auth_headers(): return False
    r = make_api_request("DELETE", f"/medications/{med_id}")
    return r and r.status_code == 204

def upload_medication_photo(med_id, file):
    if not get_auth_headers(): return False
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        r = make_api_request("PUT", f"/medications/{med_id}/photo", files=files)
        return r and r.status_code == 200
    except Exception as e:
        st.error(f"Upload error: {e}")
        return False

def get_medication_log():
    today = datetime.now().date().isoformat()
    r = make_api_request("GET", f"/medications/log/{today}")
    return r.json() if r and r.status_code == 200 else []

def log_medication_taken(med_id):
    if not get_auth_headers(): return False
    r = make_api_request("POST", f"/medications/{med_id}/log")
    return r and r.status_code == 201


# ---------------- Auth Check ----------------
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 Please log in to access medications")
    st.stop()

# ---------------- State Init ----------------
if 'edit_medication' not in st.session_state: st.session_state.edit_medication = None
if 'show_form' not in st.session_state: st.session_state.show_form = False

# ---------------- UI ----------------
st.title("💊 Medication Management")
st.markdown("Manage your medications, set reminders, and track your daily intake")

medications = fetch_medications()
med_log = get_medication_log()
taken_meds = set(med_log)

# ---------------- Form ----------------
if st.session_state.show_form:
    st.markdown("### 📝 " + ("Edit Medication" if st.session_state.edit_medication else "Add New Medication"))

    with st.form("medication_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Medication Name", value=st.session_state.edit_medication.get('name', '') if st.session_state.edit_medication else "")
            dosage = st.text_input("Dosage", value=st.session_state.edit_medication.get('dosage', '') if st.session_state.edit_medication else "")
        with col2:
            default_time = time(9, 0)
            if st.session_state.edit_medication and st.session_state.edit_medication.get('timing'):
                try:
                    default_time = datetime.strptime(st.session_state.edit_medication['timing'], "%H:%M:%S").time()
                except: pass
            timing = st.time_input("Time to take", value=default_time)
            is_active = st.checkbox("Active", value=st.session_state.edit_medication.get('is_active', True) if st.session_state.edit_medication else True)

        photo_file = st.file_uploader("Upload medication photo (optional)", type=['jpg','jpeg','png'])
        submitted = st.form_submit_button("💾 Save Medication")

        if submitted:
            if not name or not dosage:
                st.error("❌ Name & dosage required")
            else:
                med_data = {"name": name,"dosage": dosage,"timing": timing.strftime("%H:%M:%S"),"is_active": is_active}
                if st.session_state.edit_medication:
                    success, result = update_medication(st.session_state.edit_medication['id'], med_data)
                else:
                    success, result = create_medication(med_data)

                if success:
                    if photo_file:
                        med_id = st.session_state.edit_medication['id'] if st.session_state.edit_medication else result['id']
                        if upload_medication_photo(med_id, photo_file): st.success("📷 Photo uploaded!")
                    st.success("✅ Medication saved!")
                    st.session_state.show_form = False
                    st.session_state.edit_medication = None
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result}")

    if st.button("← Back"):
        st.session_state.show_form = False
        st.session_state.edit_medication = None
        st.rerun()

else:
    col1, _, col3 = st.columns([2,1,1])
    with col1: st.info("💡 Add your medications to get reminders and track intake")
    with col3:
        if st.button("➕ Add New Medication", use_container_width=True):
            st.session_state.show_form = True
            st.session_state.edit_medication = None
            st.rerun()

    if medications:
        st.markdown(f"### 📋 Your Medications ({len(medications)})")
        st.markdown('<div class="medication-grid">', unsafe_allow_html=True)
        for med in medications:
            med_time = datetime.strptime(med['timing'], "%H:%M:%S").time() if isinstance(med['timing'], str) else med['timing']
            time_str = med_time.strftime("%I:%M %p")

            card_html = f"""
            <div class="medication-card">
              <div class="medication-header"><h3 class="medication-name">{med['name']}</h3>
              <span class="medication-dosage">{med['dosage']}</span></div>
              <div class="medication-time">⏰ {time_str}</div>
              <div class="medication-status {'status-active' if med.get('is_active', True) else 'status-inactive'}">
                {'Active' if med.get('is_active', True) else 'Inactive'}
              </div>
              {"<div class='medication-status status-active'>✅ Taken today</div>" if med['id'] in taken_meds else ""}
            </div>"""
            st.markdown(card_html, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                if med['id'] not in taken_meds and med.get('is_active', True):
                    if st.button("✅ Mark Taken", key=f"take_{med['id']}"):
                        if log_medication_taken(med['id']): st.rerun()
            with c2:
                if st.button("✏️ Edit", key=f"edit_{med['id']}"):
                    st.session_state.edit_medication = med
                    st.session_state.show_form = True
                    st.rerun()
            with c3:
                if st.button("🗑️ Delete", key=f"delete_{med['id']}"):
                    if delete_medication(med['id']): st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("No medications yet. Click 'Add New Medication' to begin.")

# Footer
st.markdown("---")
st.markdown("<div style='text-align:center;color:#666;'>Health Companion - Senior Citizen Care App</div>", unsafe_allow_html=True)
