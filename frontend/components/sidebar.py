# frontend/components/sidebar.py (VERSION 2.0 - MODERN & BEHTREEN)

import streamlit as st
from auth.service import TOKEN_COOKIE_NAME

def authenticated_sidebar(cookies):
    """
    Displays a modern, authenticated sidebar with custom styling, navigation links,
    and a prominent logout button.
    """
    # --- Custom CSS for the Sidebar ---
    # Yeh CSS sidebar ko ek professional look dega.
    st.markdown("""
    <style>
        /* --- Sidebar Container Styling --- */
        [data-testid="stSidebar"] {
            background-color: #F8F9FA; /* Halka gray background */
        }

        /* --- Sidebar Header Styling --- */
        [data-testid="stSidebar"] h2 {
            font-size: 1.5rem;
            color: #000;
            padding-top: 1rem;
        }
        
        /* --- Sidebar Navigation Links Styling --- */
        [data-testid="stSidebar"] .st-emotion-cache-17lnt27 a {
            padding: 10px 15px !important;
            border-radius: 8px;
            transition: background-color 0.2s, color 0.2s;
            font-size: 1.05rem;
        }
        [data-testid="stSidebar"] .st-emotion-cache-17lnt27 a:hover {
            background-color: #E9ECEF;
            color: #000;
        }
        
        /* Active page link ko highlight karna */
        [data-testid="stSidebar"] .st-emotion-cache-17lnt27 a[data-testid="stPageLink-Current"] {
            background-color: #1E88E5;
            color: white;
        }
        [data-testid="stSidebar"] .st-emotion-cache-17lnt27 a[data-testid="stPageLink-Current"]:hover {
            background-color: #1565C0;
            color: white;
        }


        /* --- Custom Divider --- */
        .sidebar-divider {
            margin-top: 1rem;
            margin-bottom: 1rem;
            border-top: 1px solid #DEE2E6;
        }

    </style>
    """, unsafe_allow_html=True)
    
    # --- Sidebar Content ---
    with st.sidebar:
        # st.title("Navigation Menu")
        st.info("Welcome back! You are logged in.")
        
        st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
        
        # --- Main Navigation Links ---
        # st.page_link("pages/Dashboard.py", label="Dashboard", icon="🏠")
        # st.page_link("pages/Medications.py", label="My Medications", icon="💊")
        # st.page_link("pages/Appointments.py", label="My Appointments", icon="🗓️")
        
        # st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

        # # --- Settings & Profile Links ---
        # st.page_link("pages/Profile.py", label="My Profile", icon="👤")
        # st.page_link("pages/Emergency_Contacts.py", label="Emergency Contacts", icon="📞")

        # st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
        
        # --- LOGOUT BUTTON ---
        # Logout button se pehle thodi khaali jagah
        st.write("")
        st.write("")

        if st.button("Logout", use_container_width=True, type="primary"):
            # Agar cookie mein token hai, toh use delete kar do
            if cookies.get(TOKEN_COOKIE_NAME):
                del cookies[TOKEN_COOKIE_NAME]
            
            # User ko Home page par wapas bhej do
            st.switch_page("Home.py")
