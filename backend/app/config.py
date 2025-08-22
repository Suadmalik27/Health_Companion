# frontend/config.py

import streamlit as st
import requests
import os

def get_api_base_url():
    """Get the API base URL from secrets, environment variables, or use default"""
    try:
        # First try Streamlit secrets
        return st.secrets["API_BASE_URL"]
    except:
        try:
            # Then try environment variables
            return os.environ.get("API_BASE_URL", "https://health-companion-backend-44ug.onrender.com")
        except:
            # Fallback to the deployed backend
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
