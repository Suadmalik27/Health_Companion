# frontend/reset_password.py (Yeh ab ek helper hai)

import streamlit as st
import time
from auth.service import set_new_password

def draw_reset_page(token):
    """Yeh function poora Reset Password UI banata hai."""
    
    st.title("Create a New Password")
    st.markdown("Please enter and confirm your new password below.")
    
    with st.form("reset_password_form"):
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        submitted = st.form_submit_button("Reset Password", use_container_width=True, type="primary")
        
        if submitted:
            if not new_password or not confirm_password:
                st.warning("Please fill in both fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters long.")
            else:
                is_success, message = set_new_password(token, new_password)
                if is_success:
                    st.success(message)
                    st.info("Redirecting you to the login page...")
                    
                    # Browser ko redirect karne ke liye JavaScript ka istemal
                    st.markdown('<meta http-equiv="refresh" content="3; url=/" />', unsafe_allow_html=True)
                    st.stop()
                else:
                    st.error(message)
