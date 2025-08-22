# frontend/pages/Appointments.py

import streamlit as st
import requests
from datetime import datetime, date, timedelta
import calendar
from PIL import Image
import io
import base64
import os

# Page configuration
st.set_page_config(
    page_title="Appointments - Health Companion",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get API URL from secrets or use default
API_BASE_URL = st.secrets.get("API_BASE_URL", "https://health-companion-backend-44ug.onrender.com")

# Custom CSS for styling
def local_css():
    st.markdown("""
    <style>
    .appointment-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
        gap: 1.5rem;
        margin-top: 1.5rem;
    }
    .appointment-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 4px solid #2196F3;
        position: relative;
    }
    .appointment-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    }
    .appointment-image {
        width: 100%;
        height: 150px;
        object-fit: cover;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .appointment-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    .appointment-doctor {
        font-size: 1.25rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
    }
    .appointment-date {
        background: #e3f2fd;
        color: #1565c0;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .appointment-purpose {
        color: #666;
        margin: 0.5rem 0;
    }
    .appointment-location {
        color: #888;
        font-size: 0.9rem;
        margin: 0.25rem 0;
    }
    .appointment-status {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    .status-upcoming {
        background: #e8f5e9;
        color: #2e7d32;
    }
    .status-today {
        background: #fff3e0;
        color: #ef6c00;
    }
    .status-past {
        background: #f5f5f5;
        color: #757575;
    }
    .calendar-day {
        text-align: center;
        padding: 0.5rem;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .calendar-day:hover {
        background-color: #f0f0f0;
    }
    .calendar-day.has-appointment {
        background-color: #e3f2fd;
        font-weight: bold;
    }
    .calendar-day.selected {
        background-color: #2196F3;
        color: white;
    }
    .calendar-day.today {
        border: 2px solid #2196F3;
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

def get_auth_headers():
    """Get authorization headers with access token"""
    if 'access_token' not in st.session_state:
        return None
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

def fetch_appointments(start_date=None, end_date=None):
    """Fetch user's appointments with optional date range"""
    headers = get_auth_headers()
    if not headers:
        return []
    
    try:
        url = f"{API_BASE_URL}/appointments/"
        if start_date and end_date:
            url += f"?start_date={start_date}&end_date={end_date}"
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching appointments: {str(e)}")
        return []

def create_appointment(appointment_data):
    """Create a new appointment"""
    headers = get_auth_headers()
    if not headers:
        return False, "Not authenticated"
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/appointments/",
            json=appointment_data,
            headers=headers
        )
        if response.status_code == 201:
            return True, response.json()
        return False, response.json().get("detail", "Failed to create appointment")
    except Exception as e:
        return False, f"Error: {str(e)}"

def update_appointment(appointment_id, appointment_data):
    """Update an existing appointment"""
    headers = get_auth_headers()
    if not headers:
        return False, "Not authenticated"
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/appointments/{appointment_id}",
            json=appointment_data,
            headers=headers
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json().get("detail", "Failed to update appointment")
    except Exception as e:
        return False, f"Error: {str(e)}"

def delete_appointment(appointment_id):
    """Delete an appointment"""
    headers = get_auth_headers()
    if not headers:
        return False
    
    try:
        response = requests.delete(
            f"{API_BASE_URL}/appointments/{appointment_id}",
            headers=headers
        )
        return response.status_code == 204
    except Exception as e:
        st.error(f"Error deleting appointment: {str(e)}")
        return False

def upload_appointment_photo(appointment_id, file):
    """Upload photo for an appointment"""
    headers = get_auth_headers()
    if not headers:
        return False
    
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.put(
            f"{API_BASE_URL}/appointments/{appointment_id}/photo",
            files=files,
            headers=headers
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error uploading photo: {str(e)}")
        return False

def generate_calendar(year, month, appointments):
    """Generate calendar view with appointment indicators"""
    cal = calendar.monthcalendar(year, month)
    today = date.today()
    
    st.markdown(f"### {calendar.month_name[month]} {year}")
    
    # Calendar header
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cols = st.columns(7)
    for i, day in enumerate(days):
        cols[i].write(f"**{day}**")
    
    # Calendar body
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
            else:
                current_date = date(year, month, day)
                has_appointment = any(
                    appt_date.date() == current_date 
                    for appt in appointments 
                    if (appt_date := parse_appointment_datetime(appt['appointment_datetime']))
                )
                
                day_class = "calendar-day"
                if has_appointment:
                    day_class += " has-appointment"
                if current_date == today:
                    day_class += " today"
                if current_date == st.session_state.get('selected_date', today):
                    day_class += " selected"
                
                if cols[i].button(str(day), key=f"day_{day}", use_container_width=True):
                    st.session_state.selected_date = current_date
                    st.rerun()
                
                # Add some visual indicators using HTML
                day_html = f"<div class='{day_class}'>{day}</div>"
                cols[i].markdown(day_html, unsafe_allow_html=True)

def parse_appointment_datetime(datetime_str):
    """Parse appointment datetime from string"""
    try:
        if 'T' in datetime_str:
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        else:
            return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S")
    except:
        return datetime.now()

def get_appointment_status(appointment_datetime):
    """Get status of appointment (upcoming, today, past)"""
    appt_time = parse_appointment_datetime(appointment_datetime)
    today = datetime.now().date()
    appt_date = appt_time.date()
    
    if appt_date == today:
        return "today", "Today"
    elif appt_date > today:
        return "upcoming", "Upcoming"
    else:
        return "past", "Past"

# Check if user is logged in
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access appointments")
    st.stop()

# Initialize session state
if 'edit_appointment' not in st.session_state:
    st.session_state.edit_appointment = None
if 'show_form' not in st.session_state:
    st.session_state.show_form = False
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = date.today()
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "calendar"  # or "list"

# Page header
st.title("📅 Appointment Management")
st.markdown("Schedule and manage your doctor appointments")

# Fetch appointments for the current month
current_date = datetime.now()
appointments = fetch_appointments()

# View mode toggle
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.info("💡 Schedule your doctor appointments and set reminders")
with col3:
    view_mode = st.radio("View:", ["Calendar", "List"], horizontal=True, index=0 if st.session_state.view_mode == "calendar" else 1)
    st.session_state.view_mode = view_mode.lower()

# Calendar View
if st.session_state.view_mode == "calendar":
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Month navigation
        nav_col1, nav_col2, nav_col3 = st.columns(3)
        with nav_col1:
            if st.button("← Prev"):
                current_date = current_date.replace(day=1) - timedelta(days=1)
                st.session_state.selected_date = current_date
        with nav_col2:
            st.write(f"{current_date.strftime('%B %Y')}")
        with nav_col3:
            if st.button("Next →"):
                next_month = current_date.replace(day=28) + timedelta(days=4)
                current_date = next_month.replace(day=1)
                st.session_state.selected_date = current_date
        
        # Generate calendar
        generate_calendar(current_date.year, current_date.month, appointments)
        
        # Add new appointment button
        if st.button("➕ New Appointment", use_container_width=True):
            st.session_state.show_form = True
            st.session_state.edit_appointment = None
            st.rerun()
    
    with col2:
        # Show appointments for selected date
        selected_appointments = [
            appt for appt in appointments 
            if parse_appointment_datetime(appt['appointment_datetime']).date() == st.session_state.selected_date
        ]
        
        st.markdown(f"### Appointments on {st.session_state.selected_date.strftime('%B %d, %Y')}")
        
        if selected_appointments:
            for appointment in selected_appointments:
                appt_time = parse_appointment_datetime(appointment['appointment_datetime'])
                status_class, status_text = get_appointment_status(appointment['appointment_datetime'])
                
                time_format = st.session_state.get('time_format', '12h')
                time_str = appt_time.strftime("%I:%M %p") if time_format == '12h' else appt_time.strftime("%H:%M")
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="appointment-card">
                        <div class="appointment-header">
                            <h3 class="appointment-doctor">Dr. {appointment['doctor_name']}</h3>
                            <span class="appointment-date">{time_str}</span>
                        </div>
                        <p class="appointment-purpose">{appointment.get('purpose', 'General checkup')}</p>
                        <p class="appointment-location">📍 {appointment.get('location', 'Not specified')}</p>
                        <span class="appointment-status status-{status_class}">{status_text}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("✏️ Edit", key=f"edit_{appointment['id']}"):
                        st.session_state.edit_appointment = appointment
                        st.session_state.show_form = True
                        st.rerun()
                    if st.button("🗑️ Delete", key=f"delete_{appointment['id']}"):
                        if delete_appointment(appointment['id']):
                            st.success("Appointment deleted successfully")
                            st.rerun()
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📅</div>
                <h3>No appointments scheduled</h3>
                <p>No appointments scheduled for this date</p>
            </div>
            """, unsafe_allow_html=True)

# List View
else:
    # Filter options
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        date_filter = st.selectbox("Filter by:", ["All", "Upcoming", "Today", "Past"])
    with col4:
        if st.button("➕ New Appointment", use_container_width=True):
            st.session_state.show_form = True
            st.session_state.edit_appointment = None
            st.rerun()
    
    # Filter appointments
    filtered_appointments = appointments
    if date_filter != "All":
        today = datetime.now().date()
        filtered_appointments = [
            appt for appt in appointments 
            if get_appointment_status(appt['appointment_datetime'])[0] == date_filter.lower()
        ]
    
    if filtered_appointments:
        st.markdown(f"### {len(filtered_appointments)} Appointments")
        
        for appointment in filtered_appointments:
            appt_time = parse_appointment_datetime(appointment['appointment_datetime'])
            status_class, status_text = get_appointment_status(appointment['appointment_datetime'])
            
            time_format = st.session_state.get('time_format', '12h')
            time_str = appt_time.strftime("%I:%M %p") if time_format == '12h' else appt_time.strftime("%H:%M")
            date_str = appt_time.strftime("%b %d, %Y")
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Display doctor photo if available
                photo_html = ""
                if appointment.get('photo_url'):
                    try:
                        photo_url = appointment['photo_url']
                        if photo_url.startswith('/'):
                            photo_url = f"{API_BASE_URL}{photo_url}"
                        response = requests.get(photo_url)
                        if response.status_code == 200:
                            img = Image.open(io.BytesIO(response.content))
                            buffered = io.BytesIO()
                            img.save(buffered, format="JPEG")
                            img_str = base64.b64encode(buffered.getvalue()).decode()
                            photo_html = f'<img src="data:image/jpeg;base64,{img_str}" class="appointment-image">'
                    except:
                        pass
                
                st.markdown(f"""
                <div class="appointment-card">
                    {photo_html}
                    <div class="appointment-header">
                        <h3 class="appointment-doctor">Dr. {appointment['doctor_name']}</h3>
                        <span class="appointment-date">{date_str} at {time_str}</span>
                    </div>
                    <p class="appointment-purpose">{appointment.get('purpose', 'General checkup')}</p>
                    <p class="appointment-location">📍 {appointment.get('location', 'Not specified')}</p>
                    <span class="appointment-status status-{status_class}">{status_text}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("✏️ Edit", key=f"edit_{appointment['id']}"):
                    st.session_state.edit_appointment = appointment
                    st.session_state.show_form = True
                    st.rerun()
                if st.button("🗑️ Delete", key=f"delete_{appointment['id']}"):
                    if delete_appointment(appointment['id']):
                        st.success("Appointment deleted successfully")
                        st.rerun()
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📅</div>
            <h3>No appointments found</h3>
            <p>Try changing your filters or schedule a new appointment</p>
        </div>
        """, unsafe_allow_html=True)

# Add/Edit Appointment Form
if st.session_state.show_form:
    st.markdown("### 📝 " + ("Edit Appointment" if st.session_state.edit_appointment else "New Appointment"))
    
    with st.form("appointment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            doctor_name = st.text_input("Doctor's Name", 
                                      value=st.session_state.edit_appointment.get('doctor_name', '') if st.session_state.edit_appointment else "",
                                      placeholder="e.g., Dr. Smith")
            purpose = st.text_input("Purpose of Visit",
                                  value=st.session_state.edit_appointment.get('purpose', '') if st.session_state.edit_appointment else "",
                                  placeholder="e.g., Routine checkup, Follow-up")
        
        with col2:
            appointment_datetime = st.datetime_input("Date & Time",
                                                   value=parse_appointment_datetime(st.session_state.edit_appointment['appointment_datetime']) if st.session_state.edit_appointment else datetime.now() + timedelta(hours=1),
                                                   min_value=datetime.now())
            location = st.text_input("Location",
                                   value=st.session_state.edit_appointment.get('location', '') if st.session_state.edit_appointment else "",
                                   placeholder="e.g., City Hospital, Room 101")
        
        # Photo upload
        if st.session_state.edit_appointment and st.session_state.edit_appointment.get('photo_url'):
            try:
                photo_url = st.session_state.edit_appointment['photo_url']
                if photo_url.startswith('/'):
                    photo_url = f"{API_BASE_URL}{photo_url}"
                response = requests.get(photo_url)
                if response.status_code == 200:
                    img = Image.open(io.BytesIO(response.content))
                    st.image(img, caption="Current Doctor Photo", width=200)
            except:
                st.write("Could not load current photo")
        
        photo_file = st.file_uploader("Upload doctor photo (optional)", type=['jpg', 'jpeg', 'png'])
        
        submitted = st.form_submit_button("💾 Save Appointment")
        
        if submitted:
            if not doctor_name:
                st.error("Please provide doctor's name")
            else:
                appointment_data = {
                    "doctor_name": doctor_name,
                    "purpose": purpose,
                    "location": location,
                    "appointment_datetime": appointment_datetime.isoformat()
                }
                
                if st.session_state.edit_appointment:
                    success, result = update_appointment(st.session_state.edit_appointment['id'], appointment_data)
                else:
                    success, result = create_appointment(appointment_data)
                
                if success:
                    # Upload photo if provided
                    if photo_file:
                        appointment_id = st.session_state.edit_appointment['id'] if st.session_state.edit_appointment else result['id']
                        upload_success = upload_appointment_photo(appointment_id, photo_file)
                        if upload_success:
                            st.success("Photo uploaded successfully!")
                    
                    st.success("Appointment saved successfully!")
                    st.session_state.show_form = False
                    st.session_state.edit_appointment = None
                    st.rerun()
                else:
                    st.error(f"Error saving appointment: {result}")
    
    if st.button("← Back to appointments"):
        st.session_state.show_form = False
        st.session_state.edit_appointment = None
        st.rerun()

# Statistics section
if appointments:
    st.markdown("---")
    st.markdown("### 📊 Appointment Statistics")
    
    today = datetime.now().date()
    upcoming_appointments = [appt for appt in appointments if parse_appointment_datetime(appt['appointment_datetime']).date() > today]
    past_appointments = [appt for appt in appointments if parse_appointment_datetime(appt['appointment_datetime']).date() < today]
    today_appointments = [appt for appt in appointments if parse_appointment_datetime(appt['appointment_datetime']).date() == today]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Appointments", len(appointments))
    with col2:
        st.metric("Upcoming", len(upcoming_appointments))
    with col3:
        st.metric("Today", len(today_appointments))
    with col4:
        st.metric("Past", len(past_appointments))

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Health Companion - Senior Citizen Care App</div>", unsafe_allow_html=True)
