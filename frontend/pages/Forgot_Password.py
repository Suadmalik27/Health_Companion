# frontend/pages/Forgot_Password.py (VERSION 2.1 - ENGLISH UI)

import streamlit as st
from auth.service import request_password_reset
from pathlib import Path
import base64

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Forgot Password - Senior Wellness Hub",
    page_icon="❤️",
    layout="centered", # Centered layout is best for simple forms
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM STYLING ---
# Page ko ek modern aur saaf-suthra look dene ke liye custom CSS
st.markdown("""
<style>
    /* --- Cleaner Look ke liye Streamlit ke default elements ko hide karna --- */
    header, footer { visibility: hidden !important; }
    
    /* --- Main title ko bada aur centered karna --- */
    h1 {
        text-align: center;
        padding-bottom: 20px;
    }

    /* --- Form ko card jaisa look dena --- */
    .content-card {
        background: #FFFFFF;
        padding: 2.5rem;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTION FOR IMAGE ---
def get_image_as_base64(path):
    """ Reads an image file and returns it as a base64 encoded string. """
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return None

# --- 4. PAGE LAYOUT ---

# Image ko load karna
image_path = Path(__file__).parent.parent / "assets" / "icon.png"
img_base64 = get_image_as_base64(image_path)
if img_base64:
    st.image(f"data:image/png;base64,{img_base64}", width=100)

st.title("Forgot Your Password?")

st.markdown('<div class="content-card">', unsafe_allow_html=True)

# --- YEH LINE ENGLISH MEIN BADAL DI GAYI HAI ---
st.markdown("No problem. Enter your email address below, and we'll send you a link to reset it.")

with st.form("forgot_password_form"):
    email = st.text_input(
        "Your Email Address", 
        placeholder="Enter your registered email"
    )
    
    submitted = st.form_submit_button(
        "Send Reset Link", 
        use_container_width=True, 
        type="primary"
    )

    if submitted:
        if not email:
            st.warning("Please enter your email address.")
        else:
            with st.spinner("Sending request..."):
                is_success, message = request_password_reset(email)
            
            # Suraksha ke liye, hum hamesha ek success message dikhate hain
            # taaki koi yeh na pata laga sake ki kaunsa email registered hai.
            st.success("If an account with that email exists, a password reset link has been sent. Please check your inbox (and spam folder).")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
if st.button("Back to Login", use_container_width=True):
    st.switch_page("Home.py")

