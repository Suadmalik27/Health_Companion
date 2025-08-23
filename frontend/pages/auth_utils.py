import streamlit as st

def check_login():
    """Redirect user to login page if not logged in."""
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("⚠️ Please log in first.")
        st.switch_page("pages/Login_Signup.py")
