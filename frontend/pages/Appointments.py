# frontend/pages/Appointments.py (Fixed & Consistent)

import streamlit as st
import requests
from datetime import datetime, date, timedelta
import calendar
from PIL import Image
import io
import base64

# ---------------- Page config ----------------
st.set_page_config(
    page_title="Appointments - Health Companion",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Fixed API URL ----------------
def get_api_base_url():
    return "https://health-companion-backend-44ug.onrender.com"

# ---------------- Auth / Requests ----------------
def get_auth_headers():
    """
    Use the SAME key as streamlit_app.py -> st.session_state['token']
    """
    token = st.session_state.get("token")
    if not token:
        return None
    return {"Authorization": f"Bearer {token}"}

def make_api_request(method, endpoint, **kwargs):
    """
    Centralized request with auth + timeouts + error handling
    """
    base_url = get_api_base_url()
    url = f"{base_url}{endpoint}"

    auth_headers = get_auth_headers()
    if auth_headers:
        if "headers" in kwargs and kwargs["headers"]:
            kwargs["headers"].update(auth_headers)
        else:
            kwargs["headers"] = auth_headers

    if "timeout" not in kwargs:
        kwargs["timeout"] = 10

    try:
        resp = requests.request(method, url, **kwargs)
        return resp
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the server. Please check your internet connection.")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# ---------------- CSS ----------------
def local_css():
    st.markdown("""
    <style>
    .appointment-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 1.5rem; margin-top: 1.5rem; }
    .appointment-card { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); transition: transform 0.3s ease, box-shadow 0.3s ease; border-left: 4px solid #2196F3; position: relative; }
    .appointment-card:hover { transform: translateY(-5px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15); }
    .appointment-image { width: 100%; height: 150px; object-fit: cover; border-radius: 8px; margin-bottom: 1rem; }
    .appointment-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }
    .appointment-doctor { font-size: 1.25rem; font-weight: bold; color: #2c3e50; margin: 0; }
    .appointment-date { background: #e3f2fd; color: #1565c0; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.9rem; font-weight: 500; }
    .appointment-purpose { color: #666; margin: 0.5rem 0; }
    .appointment-location { color: #888; font-size: 0.9rem; margin: 0.25rem 0; }
    .appointment-status { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 500; margin-top: 0.5rem; }
    .status-upcoming { background: #e8f5e9; color: #2e7d32; }
    .status-today { background: #fff3e0; color: #ef6c00; }
    .status-past { background: #f5f5f5; color: #757575; }
    .empty-state { text-align: center; padding: 3rem; color: #78909c; }
    .empty-state-icon { font-size: 4rem; margin-bottom: 1rem; }
    .form-container { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 2rem; }
    .calendar-wrap { background: white; padding: 1rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .calendar-day { text-align: center; padding: 0.5rem; border-radius: 8px; cursor: pointer; transition: background-color 0.3s ease; }
    .calendar-day:hover { background-color: #f0f0f0; }
    .calendar-day.has-appointment { background-color: #e3f2fd; font-weight: bold; }
    .calendar-day.today { border: 2px solid #2196F3; }
    </style>
    """, unsafe_allow_html=True)

local_css()

# ---------------- API helpers ----------------
def fetch_appointments(start_date=None, end_date=None):
    url = "/appointments/"
    if start_date and end_date:
        url += f"?start_date={start_date}&end_date={end_date}"
    resp = make_api_request("GET", url)
    if resp and resp.status_code == 200:
        return resp.json()
    return []

def create_appointment(payload):
    if not get_auth_headers():
        return False, "Not authenticated"
    resp = make_api_request("POST", "/appointments/", json=payload)
    if resp and resp.status_code == 201:
        return True, resp.json()
    detail = None
    try:
        detail = resp.json().get("detail")
    except Exception:
        pass
    return False, detail or "Failed to create appointment"

def update_appointment(appointment_id, payload):
    if not get_auth_headers():
        return False, "Not authenticated"
    resp = make_api_request("PUT", f"/appointments/{appointment_id}", json=payload)
    if resp and resp.status_code == 200:
        return True, resp.json()
    detail = None
    try:
        detail = resp.json().get("detail")
    except Exception:
        pass
    return False, detail or "Failed to update appointment"

def delete_appointment(appointment_id):
    if not get_auth_headers():
        return False
    resp = make_api_request("DELETE", f"/appointments/{appointment_id}")
    return resp and resp.status_code == 204

# ---------------- Auth gate ----------------
if not st.session_state.get("logged_in", False) or not st.session_state.get("token"):
    st.warning("🔒 Please log in to access appointments.")
    if st.button("Login"):
        st.session_state["page"] = "login"
        st.rerun()
    st.stop()

# ---------------- State init ----------------
if "edit_appt" not in st.session_state:
    st.session_state.edit_appt = None
if "show_form" not in st.session_state:
    st.session_state.show_form = False
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

# ---------------- Header ----------------
st.title("📅 Appointment Management")
st.markdown("Add, edit, and track your medical appointments with a calendar view.")

# ---------------- Data ----------------
appointments = fetch_appointments()
# Normalize to list of dicts
appointments = appointments if isinstance(appointments, list) else []

# ---------------- Helpers ----------------
def appt_status(appt_date_str):
    try:
        d = datetime.fromisoformat(appt_date_str).date()
    except ValueError:
        try:
            d = datetime.strptime(appt_date_str, "%Y-%m-%d").date()
        except Exception:
            return "past"
    today = date.today()
    if d == today:
        return "today"
    return "upcoming" if d > today else "past"

def month_has_appointments(year, month):
    return {
        a["date"][:10]
        for a in appointments
        if "date" in a and a["date"].startswith(f"{year:04d}-{month:02d}")
    }

# ---------------- Form ----------------
if st.session_state.show_form:
    st.markdown("### 📝 " + ("Edit Appointment" if st.session_state.edit_appt else "Add New Appointment"))
    with st.form("appt_form"):
        c1, c2 = st.columns(2)
        with c1:
            doctor = st.text_input(
                "Doctor / Clinic",
                value=(st.session_state.edit_appt.get("doctor", "") if st.session_state.edit_appt else "")
            )
            purpose = st.text_input(
                "Purpose",
                value=(st.session_state.edit_appt.get("purpose", "") if st.session_state.edit_appt else "")
            )
            location = st.text_input(
                "Location",
                value=(st.session_state.edit_appt.get("location", "") if st.session_state.edit_appt else "")
            )
        with c2:
            # Date & Time
            default_dt = datetime.now()
            if st.session_state.edit_appt and st.session_state.edit_appt.get("date"):
                try:
                    default_dt = datetime.fromisoformat(st.session_state.edit_appt["date"])
                except Exception:
                    try:
                        default_dt = datetime.strptime(st.session_state.edit_appt["date"], "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        pass
            appt_date = st.date_input("Date", value=default_dt.date())
            appt_time = st.time_input("Time", value=default_dt.time())

            notes = st.text_area(
                "Notes (optional)",
                value=(st.session_state.edit_appt.get("notes", "") if st.session_state.edit_appt else "")
            )

        submitted = st.form_submit_button("💾 Save Appointment")

        if submitted:
            if not doctor or not purpose:
                st.error("Please provide doctor/clinic and purpose.")
            else:
                dt_iso = datetime.combine(appt_date, appt_time).isoformat()
                payload = {
                    "doctor": doctor,
                    "purpose": purpose,
                    "location": location,
                    "date": dt_iso,
                    "notes": notes
                }
                if st.session_state.edit_appt:
                    ok, res = update_appointment(st.session_state.edit_appt["id"], payload)
                else:
                    ok, res = create_appointment(payload)

                if ok:
                    st.success("✅ Appointment saved!")
                    st.session_state.show_form = False
                    st.session_state.edit_appt = None
                    st.rerun()
                else:
                    st.error(f"Error: {res}")

    if st.button("← Back to appointments"):
        st.session_state.show_form = False
        st.session_state.edit_appt = None
        st.rerun()

else:
    # Top actions/info
    left, mid, right = st.columns([2,1,1])
    with left:
        st.info("💡 Use the calendar to view dates with appointments. Click 'Add New Appointment' to create one.")
    with right:
        if st.button("➕ Add New Appointment", use_container_width=True):
            st.session_state.show_form = True
            st.session_state.edit_appt = None
            st.rerun()

    # Calendar + List
    st.markdown("### 🗓️ Calendar")
    c1, c2 = st.columns([1,2])

    with c1:
        today = date.today()
        year = st.session_state.selected_date.year
        month = st.session_state.selected_date.month
        cal = calendar.monthcalendar(year, month)
        has_appt_days = month_has_appointments(year, month)

        st.markdown(f"**{calendar.month_name[month]} {year}**")
        # Month navigation
        nav1, nav2, nav3 = st.columns([1,1,1])
        with nav1:
            if st.button("← Prev"):
                new_month = (month - 2) % 12 + 1
                new_year = year - 1 if month == 1 else year
                st.session_state.selected_date = date(new_year, new_month, 1)
                st.rerun()
        with nav2:
            if st.button("Today"):
                st.session_state.selected_date = today
                st.rerun()
        with nav3:
            if st.button("Next →"):
                new_month = (month % 12) + 1
                new_year = year + 1 if month == 12 else year
                st.session_state.selected_date = date(new_year, new_month, 1)
                st.rerun()

        # Render calendar grid
        # Headers
        st.write("Mo Tu We Th Fr Sa Su")
        for week in cal:
            row = []
            for i, d in enumerate(week):
                if d == 0:
                    row.append("  ")
                else:
                    d_str = f"{year:04d}-{month:02d}-{d:02d}"
                    classes = ["calendar-day"]
                    if d_str in has_appt_days:
                        classes.append("has-appointment")
                    if date(year, month, d) == today:
                        classes.append("today")
                    row.append(f"<span class='{ ' '.join(classes) }'>{d:02d}</span>")
            st.markdown(" ".join(row), unsafe_allow_html=True)

        # Date selector
        sel_date = st.date_input("Jump to date", value=st.session_state.selected_date, key="select_date")
        if sel_date != st.session_state.selected_date:
            st.session_state.selected_date = sel_date
            st.rerun()

    with c2:
        # Filter appointments by selected date's month for quick overview
        sel_month_prefix = st.session_state.selected_date.strftime("%Y-%m")
        month_appts = [a for a in appointments if a.get("date", "").startswith(sel_month_prefix)]

        st.markdown(f"### 📋 Appointments in {calendar.month_name[month]} {year} ({len(month_appts)})")

        if not month_appts:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📅</div>
                <h3>No appointments found</h3>
                <p>Use the button above to add a new appointment</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="appointment-grid">', unsafe_allow_html=True)
            for a in month_appts:
                a_date = a.get("date", "")
                a_dt = None
                try:
                    a_dt = datetime.fromisoformat(a_date)
                except Exception:
                    try:
                        a_dt = datetime.strptime(a_date, "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        pass

                date_str = a_dt.strftime("%b %d, %Y • %I:%M %p") if a_dt else a_date
                status = appt_status(a_date)
                status_html = {
                    "today": "<span class='appointment-status status-today'>Today</span>",
                    "upcoming": "<span class='appointment-status status-upcoming'>Upcoming</span>",
                    "past": "<span class='appointment-status status-past'>Past</span>",
                }[status]

                card = f"""
                <div class="appointment-card">
                    <div class="appointment-header">
                        <h3 class="appointment-doctor">{a.get('doctor','(No doctor)')}</h3>
                        <span class="appointment-date">{date_str}</span>
                    </div>
                    <p class="appointment-purpose">📝 {a.get('purpose','')}</p>
                    <p class="appointment-location">📍 {a.get('location','')}</p>
                    {status_html}
                </div>
                """
                st.markdown(card, unsafe_allow_html=True)

                cA, cB, cC = st.columns(3)
                with cA:
                    if st.button("✏️ Edit", key=f"edit_{a['id']}"):
                        st.session_state.edit_appt = a
                        st.session_state.show_form = True
                        st.rerun()
                with cB:
                    if st.button("🗑️ Delete", key=f"del_{a['id']}"):
                        if delete_appointment(a["id"]):
                            st.success("Deleted")
                            st.rerun()
                        else:
                            st.error("Failed to delete")
                with cC:
                    if status != "past":
                        st.caption("⏰ Reminder set by backend (if enabled)")

            st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Footer ----------------
st.markdown("---")
st.markdown("<div style='text-align:center;color:#666;'>Health Companion - Senior Citizen Care App</div>", unsafe_allow_html=True)
