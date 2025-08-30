# frontend/pages/Medications.py (VERSION 3.1 - COMPLETED WITH DISPLAY LOGIC)

import streamlit as st
from streamlit_cookies_manager import CookieManager
from datetime import time, datetime, date

from auth.service import (
    TOKEN_COOKIE_NAME,
    get_medications,
    add_medication,
    delete_medication
)
from components.sidebar import authenticated_sidebar

# --- 1. PAGE CONFIGURATION & AUTHENTICATION ---
st.set_page_config(page_title="Manage Medications", page_icon="💊", layout="wide")

cookies = CookieManager()
if not cookies.ready():
    st.spinner("Initializing...")
    st.stop()

token = cookies.get(TOKEN_COOKIE_NAME)
if not token:
    st.warning("🔒 You are not logged in. Please log in to continue.")
    st.stop()

authenticated_sidebar(cookies)

# Session state for delete confirmation
if 'confirming_delete_med_id' not in st.session_state:
    st.session_state.confirming_delete_med_id = None

# --- 2. DATA FETCHING ---
@st.cache_data(show_spinner="Loading your medications...")
def load_medications_data(token_param):
    is_success, meds_data = get_medications(token_param)
    if not is_success:
        st.error(f"Could not load medications: {meds_data}")
        return []
    return meds_data

medications = load_medications_data(token)

# --- 3. PAGE UI ---
st.title("💊 Manage Your Medications")
st.markdown("Use this page to add, view, or remove your medications.")
st.markdown("---")

# --- ADVANCED 'ADD MEDICATION' FORM ---
with st.expander("➕ Add a New Medication", expanded=True):
    with st.form("new_medication_form", clear_on_submit=True):
        st.subheader("New Medication Details")
        
        c1, c2 = st.columns(2)
        with c1:
            med_name = st.text_input("Medication Name", placeholder="e.g., Crocin")
        with c2:
            med_dosage = st.text_input("Dosage", placeholder="e.g., 1 tablet, 500mg")

        st.markdown("**Frequency & Schedule**")
        
        freq_type = st.selectbox(
            "How often do you take this medication?",
            ("Daily", "Weekly", "Monthly", "As Needed")
        )

        freq_details = None
        if freq_type == "Weekly":
            days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            freq_details = st.multiselect(
                "On which days?",
                options=days_of_week,
                placeholder="Choose one or more days"
            )
        elif freq_type == "Monthly":
            freq_details = st.number_input(
                "On which day of the month?",
                min_value=1, max_value=31, value=1, step=1
            )

        st.markdown("**Timing**")
        timing_type = st.radio("Choose a timing method:", ("Meal-Related", "Specific Time"), horizontal=True)
        
        meal_timing, specific_time = None, None
        if timing_type == "Meal-Related":
            meal_timing = st.selectbox("When to take relative to meals?", ("Before Breakfast", "After Breakfast", "Before Lunch", "After Lunch", "Before Dinner", "After Dinner", "Bedtime"))
        else:
            specific_time_input = st.time_input("Select a specific time:", value=time(9, 0))
            specific_time = specific_time_input.isoformat() if specific_time_input else None
            
        submitted = st.form_submit_button("Add Medication to List")
        if submitted:
            if med_name and med_dosage:
                payload = {
                    "name": med_name, "dosage": med_dosage,
                    "timing_type": timing_type, "meal_timing": meal_timing, "specific_time": specific_time,
                    "frequency_type": freq_type,
                    "frequency_details": freq_details
                }
                is_added, msg = add_medication(token, payload)
                if is_added:
                    st.success("Medication added successfully!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"Failed to add medication: {msg}")
            else:
                st.warning("Please fill in the Medication Name and Dosage.")

st.markdown("---")

# --- DISPLAY EXISTING MEDICATIONS (COMPLETED SECTION) ---
st.header("Your Current Medication List")
if not medications:
    st.info("You haven't added any medications yet. Use the form above to add one.")
else:
    for med in reversed(medications):
        med_id = med['id']
        with st.container(border=True):
            if st.session_state.confirming_delete_med_id == med_id:
                st.warning(f"**Are you sure you want to delete {med['name']}?**")
                del_cols = st.columns([1, 1, 3])
                with del_cols[0]:
                    if st.button("✅ Yes, Delete", key=f"conf_{med_id}", use_container_width=True, type="primary"):
                        del_success, del_message = delete_medication(token, med_id)
                        st.session_state.confirming_delete_med_id = None
                        if del_success:
                            st.success(del_message)
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(del_message)
                with del_cols[1]:
                    if st.button("❌ No, Cancel", key=f"cancel_{med_id}", use_container_width=True):
                        st.session_state.confirming_delete_med_id = None
                        st.rerun()
            else:
                main_cols = st.columns([3, 1])
                with main_cols[0]:
                    st.subheader(f"{med['name']} ({med['dosage']})")
                    
                    # --- YEH NAYA DISPLAY LOGIC HAI ---
                    # Timing aur Frequency ko saaf-suthre tareeke se dikhana
                    
                    timing_str = med.get('meal_timing') or (datetime.strptime(med['specific_time'], '%H:%M:%S').strftime('%I:%M %p') if med.get('specific_time') else 'Anytime')
                    
                    freq_type = med.get('frequency_type', 'Daily')
                    freq_details = med.get('frequency_details')
                    
                    if freq_type == "Weekly" and freq_details:
                        schedule_str = f"Weekly on {', '.join(freq_details)}"
                    elif freq_type == "Monthly" and freq_details:
                        day = int(freq_details)
                        suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
                        schedule_str = f"Monthly on the {day}{suffix}"
                    else: # Daily or As Needed
                        schedule_str = freq_type
                        
                    st.markdown(f"**Schedule:** {schedule_str} | **Time:** {timing_str}")

                with main_cols[1]:
                    if st.button("Delete Medication", key=f"del_{med_id}", use_container_width=True, type="secondary"):
                        st.session_state.confirming_delete_med_id = med_id
                        st.rerun()

