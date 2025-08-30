# frontend/components/custom_css.py (VERSION 2.0 - CLEANED AND VERIFIED)

import streamlit as st
from pathlib import Path

def load_css():
    """
    Loads the custom CSS file from the assets folder into the Streamlit app.
    This function centralizes the logic for loading styles.
    """
    # Construct the absolute path to the CSS file from this file's location.
    # This is a robust way to ensure the file is always found.
    # Path(__file__) -> Gets the path of the current file (custom_css.py)
    # .parent -> Moves up to the 'components' directory
    # .parent -> Moves up to the 'frontend' directory
    # / "assets" / "style.css" -> Moves into the assets folder to find the file
    css_file_path = Path(__file__).parent.parent / "assets" / "style.css"
    
    try:
        # Open and read the entire content of the CSS file.
        with open(css_file_path) as f:
            # Inject the CSS into the Streamlit app using a <style> tag.
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # If the CSS file is not found, show a helpful warning for debugging.
        st.warning(f"Custom CSS file not found at path: {css_file_path}")
