# /frontend/pages/6_Health_Tips.py (New Page for Tip Management)

import streamlit as st
import requests

# --- CONFIGURATION & API CLIENT (Required on every page) ---
if "API_BASE_URL" in st.secrets:
    API_BASE_URL = st.secrets["API_BASE_URL"]
else:
    API_BASE_URL = "http://127.0.0.1:8000"

# --- API CLIENT CLASS (Robust Version) ---
class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
    def _get_headers(self):
        token = st.session_state.get("token", None)
        if token: return {"Authorization": f"Bearer {token}"}
        return {}
    def _make_request(self, method, endpoint, **kwargs):
        try:
            return requests.request(method, f"{self.base_url}{endpoint}", headers=self._get_headers(), **kwargs)
        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Could not connect to the backend server."); return None
    def post(self, endpoint, json=None): return self._make_request("POST", endpoint, json=json)
    def get(self, endpoint): return self._make_request("GET", endpoint)
    def put(self, endpoint, json=None): return self._make_request("PUT", endpoint, json=json)
    def delete(self, endpoint): return self._make_request("DELETE", endpoint)

api = ApiClient(API_BASE_URL)

# --- SECURITY CHECK ---
if 'token' not in st.session_state:
    st.warning("Please login first to access this page."); st.stop()

# --- PAGE CONFIG ---
st.set_page_config(page_title="Manage Health Tips", layout="wide")

# --- HEALTH TIPS PAGE CONTENT ---
st.header("💡 Manage Health Tips")
st.write("Here you can add, edit, or remove the health tips that appear on the dashboard.")

# --- ADD NEW TIP FORM ---
with st.expander("➕ Add a New Health Tip"):
    with st.form("new_tip_form", clear_on_submit=True):
        category = st.text_input("Category", value="General", placeholder="e.g., Diet, Exercise")
        content = st.text_area("Tip Content", placeholder="Enter the health tip here...")
        
        if st.form_submit_button("Add Tip", use_container_width=True):
            if not content:
                st.warning("Please enter the tip content.")
            else:
                with st.spinner("Adding tip..."):
                    response = api.post("/tips/", json={"category": category, "content": content})
                if response and response.status_code == 201:
                    st.success("Health tip added successfully!"); st.rerun()
                else:
                    st.error("Failed to add tip.")

st.divider()

# --- DISPLAY ALL TIPS ---
st.subheader("Existing Health Tips")

with st.spinner("Loading tips..."):
    response = api.get("/tips/")

if response and response.status_code == 200:
    all_tips = response.json()
    if not all_tips:
        st.info("No health tips found. Add one using the form above to get started.")

    for tip in all_tips:
        with st.container(border=True):
            # Edit-in-place logic
            if st.session_state.get('editing_tip_id') == tip['id']:
                with st.form(key=f"edit_tip_form_{tip['id']}"):
                    st.subheader(f"Editing Tip #{tip['id']}")
                    new_category = st.text_input("Category", value=tip['category'])
                    new_content = st.text_area("Content", value=tip['content'])
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.form_submit_button("Save Changes", use_container_width=True):
                            with st.spinner("Saving..."):
                                update_data = {"category": new_category, "content": new_content}
                                put_response = api.put(f"/tips/{tip['id']}", json=update_data)
                            if put_response and put_response.status_code == 200:
                                st.success("Tip updated!"); del st.session_state['editing_tip_id']; st.rerun()
                            else:
                                st.error("Failed to update tip.")
                    with c2:
                        if st.form_submit_button("Cancel", type="secondary", use_container_width=True):
                            del st.session_state['editing_tip_id']; st.rerun()
            else:
                # Default display view
                col1, col2, col3 = st.columns([5, 1, 1])
                with col1:
                    st.markdown(f"**{tip['category']}**: {tip['content']}")
                with col2:
                    if st.button("Edit", key=f"edit_tip_{tip['id']}", use_container_width=True):
                        st.session_state.editing_tip_id = tip['id']; st.rerun()
                with col3:
                    if st.button("Delete", type="secondary", key=f"del_tip_{tip['id']}", use_container_width=True):
                        with st.spinner("Deleting..."):
                            delete_response = api.delete(f"/tips/{tip['id']}")
                        if delete_response and delete_response.status_code == 204:
                            st.toast("Tip deleted."); st.rerun()
                        else:
                            st.error("Failed to delete tip.")
else:
    st.error("Could not load health tips from the server.")