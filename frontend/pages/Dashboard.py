import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import pytz
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(
    page_title="Health Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
        background-color: white;
    }
    .medication-taken {
        background-color: #e6f7e6;
        border-left: 5px solid #2ecc71;
    }
    .medication-missed {
        background-color: #ffe6e6;
        border-left: 5px solid #e74c3c;
    }
    .appointment-card {
        background-color: #e6f3ff;
        border-left: 5px solid #3498db;
    }
    .health-tip {
        background-color: #fff8e6;
        border-left: 5px solid #f39c12;
        font-style: italic;
    }
    .contact-card {
        background-color: #f9e6ff;
        border-left: 5px solid #9b59b6;
    }
    .metric-card {
        text-align: center;
        padding: 15px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 1rem;
        color: #7f8c8d;
    }
</style>
""", unsafe_allow_html=True)

# Mock data function - Replace with actual API call
def fetch_dashboard_data():
    # In a real implementation, you would make an API call to your backend
    # For example:
    # response = requests.get("http://your-api-url/api/v1/dashboard", 
    #                       headers={"Authorization": f"Bearer {st.session_state.token}"})
    # return response.json()
    
    # Mock data based on your backend structure
    return {
        "user_full_name": "Rahul Sharma",
        "summary": {
            "personalized_message": "Namaste, Rahul! You have 2 appointment(s) today.",
            "adherence_score": 95,
            "adherence_message": "Keep up the great work!"
        },
        "medications_today": {
            "all_daily": [
                {
                    "id": 1,
                    "name": "Metformin",
                    "dosage": "500mg",
                    "frequency": "Twice daily",
                    "frequency_type": "Daily"
                },
                {
                    "id": 2,
                    "name": "Atorvastatin",
                    "dosage": "20mg",
                    "frequency": "Once daily",
                    "frequency_type": "Daily"
                },
                {
                    "id": 3,
                    "name": "Aspirin",
                    "dosage": "81mg",
                    "frequency": "Once daily",
                    "frequency_type": "Daily"
                }
            ],
            "taken_ids": [1, 3]
        },
        "appointments": {
            "today": [
                {
                    "id": 1,
                    "title": "Endocrinologist Visit",
                    "doctor_name": "Dr. Patel",
                    "appointment_datetime": datetime.now().replace(hour=10, minute=0, second=0, microsecond=0).isoformat(),
                    "location": "City Hospital"
                },
                {
                    "id": 2,
                    "title": "Blood Test",
                    "doctor_name": "Lab Technician",
                    "appointment_datetime": datetime.now().replace(hour=15, minute=30, second=0, microsecond=0).isoformat(),
                    "location": "Diagnostic Center"
                }
            ],
            "upcoming": [
                {
                    "id": 3,
                    "title": "Cardiologist Follow-up",
                    "doctor_name": "Dr. Kumar",
                    "appointment_datetime": (datetime.now() + timedelta(days=3)).replace(hour=11, minute=0, second=0, microsecond=0).isoformat(),
                    "location": "Specialty Clinic"
                }
            ]
        },
        "reminders": {
            "refills": [
                {
                    "medication_name": "Metformin",
                    "remaining_days": 5
                }
            ]
        },
        "health_vitals": {
            "blood_pressure": "120/80",
            "blood_sugar": "110 mg/dL",
            "heart_rate": "72 bpm"
        },
        "emergency_contacts": [
            {
                "id": 1,
                "name": "Priya Sharma",
                "relationship": "Wife",
                "phone": "+91 98765 43210"
            },
            {
                "id": 2,
                "name": "Dr. Patel",
                "relationship": "Primary Care",
                "phone": "+91 97654 32109"
            }
        ],
        "health_tip": "Regular exercise helps maintain stable blood sugar levels."
    }

# Initialize session state for user data
if 'dashboard_data' not in st.session_state:
    st.session_state.dashboard_data = fetch_dashboard_data()

# Header section
st.markdown(f"<h1 class='main-header'>Welcome, {st.session_state.dashboard_data['user_full_name']}</h1>", unsafe_allow_html=True)

# Summary metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='card metric-card'>
        <div class='metric-value'>{len(st.session_state.dashboard_data['medications_today']['all_daily'])}</div>
        <div class='metric-label'>Medications Today</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='card metric-card'>
        <div class='metric-value'>{st.session_state.dashboard_data['summary']['adherence_score']}%</div>
        <div class='metric-label'>Adherence Score</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='card metric-card'>
        <div class='metric-value'>{len(st.session_state.dashboard_data['appointments']['today'])}</div>
        <div class='metric-label'>Appointments Today</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='card metric-card'>
        <div class='metric-value'>{len(st.session_state.dashboard_data['emergency_contacts'])}</div>
        <div class='metric-label'>Emergency Contacts</div>
    </div>
    """, unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    # Medications section
    st.subheader("Today's Medications")
    
    for med in st.session_state.dashboard_data['medications_today']['all_daily']:
        is_taken = med['id'] in st.session_state.dashboard_data['medications_today']['taken_ids']
        
        status_class = "medication-taken" if is_taken else "medication-missed"
        status_text = "✓ Taken" if is_taken else "✗ Not Taken Yet"
        
        st.markdown(f"""
        <div class='card {status_class}'>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3>{med['name']} ({med['dosage']})</h3>
                    <p>{med['frequency']}</p>
                </div>
                <div>
                    {status_text}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Appointments section
    st.subheader("Today's Appointments")
    
    if st.session_state.dashboard_data['appointments']['today']:
        for appointment in st.session_state.dashboard_data['appointments']['today']:
            appt_time = datetime.fromisoformat(appointment['appointment_datetime'])
            formatted_time = appt_time.strftime("%I:%M %p")
            
            st.markdown(f"""
            <div class='card appointment-card'>
                <h3>{appointment['title']}</h3>
                <p><strong>Time:</strong> {formatted_time}</p>
                <p><strong>Doctor:</strong> {appointment['doctor_name']}</p>
                <p><strong>Location:</strong> {appointment['location']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No appointments scheduled for today.")
    
    # Upcoming appointments
    st.subheader("Upcoming Appointments")
    
    if st.session_state.dashboard_data['appointments']['upcoming']:
        for appointment in st.session_state.dashboard_data['appointments']['upcoming']:
            appt_time = datetime.fromisoformat(appointment['appointment_datetime'])
            formatted_date = appt_time.strftime("%B %d, %Y")
            formatted_time = appt_time.strftime("%I:%M %p")
            
            st.markdown(f"""
            <div class='card appointment-card'>
                <h3>{appointment['title']}</h3>
                <p><strong>Date:</strong> {formatted_date}</p>
                <p><strong>Time:</strong> {formatted_time}</p>
                <p><strong>Doctor:</strong> {appointment['doctor_name']}</p>
                <p><strong>Location:</strong> {appointment['location']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No upcoming appointments.")

with col2:
    # Health tip
    st.subheader("Health Tip of the Day")
    st.markdown(f"""
    <div class='card health-tip'>
        <p>{st.session_state.dashboard_data['health_tip']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Emergency contacts
    st.subheader("Emergency Contacts")
    
    for contact in st.session_state.dashboard_data['emergency_contacts']:
        st.markdown(f"""
        <div class='card contact-card'>
            <h3>{contact['name']}</h3>
            <p><strong>Relationship:</strong> {contact['relationship']}</p>
            <p><strong>Phone:</strong> {contact['phone']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Refill reminders
    st.subheader("Refill Reminders")
    
    if st.session_state.dashboard_data['reminders']['refills']:
        for refill in st.session_state.dashboard_data['reminders']['refills']:
            st.warning(f"{refill['medication_name']} needs refill in {refill['remaining_days']} days")
    else:
        st.info("No refills needed soon.")
    
    # Health vitals
    st.subheader("Health Vitals")
    
    if 'health_vitals' in st.session_state.dashboard_data and st.session_state.dashboard_data['health_vitals']:
        vitals = st.session_state.dashboard_data['health_vitals']
        
        # Create a small chart for blood pressure trend (mock data)
        dates = pd.date_range(end=datetime.today(), periods=7).tolist()
        systolic = [120, 122, 118, 121, 119, 120, 120]
        diastolic = [80, 82, 78, 81, 79, 80, 80]
        
        fig = make_subplots(specs=[[{"secondary_y": False}]])
        fig.add_trace(go.Scatter(x=dates, y=systolic, name="Systolic", line=dict(color='red')))
        fig.add_trace(go.Scatter(x=dates, y=diastolic, name="Diastolic", line=dict(color='blue')))
        fig.update_layout(height=200, showlegend=True, margin=dict(l=20, r=20, t=30, b=20))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display current vitals
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Blood Pressure", vitals.get('blood_pressure', 'N/A'))
        with col2:
            st.metric("Blood Sugar", vitals.get('blood_sugar', 'N/A'))
        with col3:
            st.metric("Heart Rate", vitals.get('heart_rate', 'N/A'))
    else:
        st.info("No health vitals recorded yet.")

# Adherence chart (mock data)
st.subheader("Medication Adherence Trend")
adherence_data = pd.DataFrame({
    'Date': pd.date_range(end=datetime.today(), periods=30),
    'Adherence': [92, 94, 96, 95, 93, 95, 96, 97, 95, 94, 
                  96, 95, 97, 96, 95, 94, 96, 97, 95, 96, 
                  97, 96, 95, 94, 96, 97, 98, 96, 95, 95]
})

fig = px.line(adherence_data, x='Date', y='Adherence', 
              title='30-Day Adherence Trend',
              labels={'Adherence': 'Adherence (%)'})
fig.update_traces(line=dict(color='green', width=3))
fig.update_layout(height=300)
st.plotly_chart(fig, use_container_width=True)

# Footer with last updated time
ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist).strftime("%B %d, %Y at %I:%M %p %Z")
st.caption(f"Last updated: {current_time}")

# Refresh button
if st.button("Refresh Data"):
    st.session_state.dashboard_data = fetch_dashboard_data()
    st.rerun()
