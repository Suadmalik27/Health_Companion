# frontend/pages/Health_Tips.py (Fixed - No config import)

import streamlit as st
import requests
from datetime import datetime
import random
import os

# Page configuration
st.set_page_config(
    page_title="Health Tips - Health Companion",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get API base URL directly
def get_api_base_url():
    """Get the API base URL from secrets, environment variables, or use default"""
    try:
        return st.secrets["API_BASE_URL"]
    except:
        try:
            return os.environ.get("API_BASE_URL", "https://health-companion-backend-44ug.onrender.com")
        except:
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

# Custom CSS for styling
def local_css():
    st.markdown("""
    <style>
    .health-tips-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    .tip-card {
        background: linear-gradient(135deg, #fff9e6 0%, #fff3e0 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #FF9800;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .tip-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    }
    .tip-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    .tip-category {
        background: #FF9800;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .tip-content {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #333;
        margin: 0;
    }
    .tip-actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .tip-card:hover .tip-actions {
        opacity: 1;
    }
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #78909c;
    }
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    .form-container {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    .category-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    .category-chip {
        padding: 0.5rem 1rem;
        border-radius: 25px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid #e0e0e0;
    }
    .category-chip:hover {
        border-color: #FF9800;
        background: #fff3e0;
    }
    .category-chip.selected {
        background: #FF9800;
        color: white;
        border-color: #FF9800;
    }
    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-left: 4px solid #4CAF50;
    }
    .stats-number {
        font-size: 2rem;
        font-weight: bold;
        color: #4CAF50;
        margin: 0;
    }
    .stats-label {
        color: #666;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

def fetch_all_tips():
    """Fetch all health tips"""
    response = make_api_request("GET", "/tips/")
    if response and response.status_code == 200:
        return response.json()
    return []

def fetch_random_tip():
    """Fetch a random health tip"""
    response = make_api_request("GET", "/tips/random")
    if response and response.status_code == 200:
        return response.json()
    return None

def create_tip(tip_data):
    """Create a new health tip"""
    headers = get_auth_headers()
    if not headers:
        return False, "Not authenticated"
    
    response = make_api_request("POST", "/tips/", json=tip_data, headers=headers)
    if response and response.status_code == 201:
        return True, response.json()
    return False, "Failed to create tip"

def update_tip(tip_id, tip_data):
    """Update an existing health tip"""
    headers = get_auth_headers()
    if not headers:
        return False, "Not authenticated"
    
    response = make_api_request("PUT", f"/tips/{tip_id}", json=tip_data, headers=headers)
    if response and response.status_code == 200:
        return True, response.json()
    return False, "Failed to update tip"

def delete_tip(tip_id):
    """Delete a health tip"""
    headers = get_auth_headers()
    if not headers:
        return False
    
    response = make_api_request("DELETE", f"/tips/{tip_id}", headers=headers)
    return response and response.status_code == 204

def get_tip_categories(tips):
    """Get unique categories from tips"""
    categories = set()
    for tip in tips:
        categories.add(tip.get('category', 'General'))
    return sorted(categories)

# Check if user is logged in
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access health tips")
    st.stop()

# Initialize session state
if 'edit_tip' not in st.session_state:
    st.session_state.edit_tip = None
if 'show_form' not in st.session_state:
    st.session_state.show_form = False
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = "All"
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "browse"

# Fetch tips
tips = fetch_all_tips()
random_tip = fetch_random_tip()
categories = get_tip_categories(tips)

# Page header
st.title("💡 Health Tips & Advice")
st.markdown("Discover helpful health tips and advice for senior wellness")

# Statistics section
if tips:
    st.markdown("### 📊 Tips Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <h3 class="stats-number">{len(tips)}</h3>
            <p class="stats-label">Total Tips</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        general_tips = len([t for t in tips if t.get('category') == 'General'])
        st.markdown(f"""
        <div class="stats-card">
            <h3 class="stats-number">{general_tips}</h3>
            <p class="stats-label">General Tips</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        unique_categories = len(set(t.get('category', 'General') for t in tips))
        st.markdown(f"""
        <div class="stats-card">
            <h3 class="stats-number">{unique_categories}</h3>
            <p class="stats-label">Categories</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Count tips created by current user (if authenticated)
        user_tips = len(tips)  # For now, all tips are visible to all users
        st.markdown(f"""
        <div class="stats-card">
            <h3 class="stats-number">{user_tips}</h3>
            <p class="stats-label">Available Tips</p>
        </div>
        """, unsafe_allow_html=True)

# View mode toggle
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.info("💡 Browse health tips or add your own wisdom to help others")
with col3:
    if st.button("➕ Add New Tip", use_container_width=True):
        st.session_state.show_form = True
        st.session_state.edit_tip = None
        st.rerun()

# Category filter
if categories:
    st.markdown("### 🏷️ Filter by Category")
    
    # Create category chips
    category_cols = st.columns(min(6, len(categories) + 1))
    
    with category_cols[0]:
        if st.button("All Categories", key="cat_all", use_container_width=True):
            st.session_state.selected_category = "All"
            st.rerun()
    
    for i, category in enumerate(categories, 1):
        with category_cols[i % len(category_cols)]:
            is_selected = st.session_state.selected_category == category
            if st.button(category, key=f"cat_{category}", use_container_width=True,
                       type="primary" if is_selected else "secondary"):
                st.session_state.selected_category = category
                st.rerun()

# Add/Edit Tip Form
if st.session_state.show_form:
    st.markdown("### 📝 " + ("Edit Health Tip" if st.session_state.edit_tip else "Add New Health Tip"))
    
    with st.form("tip_form"):
        # Category selection
        default_category = st.session_state.edit_tip.get('category', 'General') if st.session_state.edit_tip else 'General'
        category = st.selectbox(
            "Category",
            options=categories + ['New Category'] if categories else ['General', 'Diet', 'Exercise', 'Mental Health', 'New Category'],
            index=0 if default_category not in categories else categories.index(default_category),
            help="Select a category or choose 'New Category' to create a new one"
        )
        
        if category == 'New Category':
            new_category = st.text_input("New Category Name", placeholder="Enter new category name")
            category = new_category if new_category else 'General'
        
        # Tip content
        content = st.text_area(
            "Health Tip Content",
            value=st.session_state.edit_tip.get('content', '') if st.session_state.edit_tip else "",
            placeholder="Share your health wisdom here...",
            height=150,
            help="Write clear, helpful health advice"
        )
        
        submitted = st.form_submit_button("💾 Save Health Tip")
        
        if submitted:
            if not content.strip():
                st.error("Please provide tip content")
            else:
                tip_data = {
                    "content": content.strip(),
                    "category": category.strip()
                }
                
                if st.session_state.edit_tip:
                    success, result = update_tip(st.session_state.edit_tip['id'], tip_data)
                else:
                    success, result = create_tip(tip_data)
                
                if success:
                    st.success("Health tip saved successfully!")
                    st.session_state.show_form = False
                    st.session_state.edit_tip = None
                    st.rerun()
                else:
                    st.error(f"Error saving tip: {result}")
    
    if st.button("← Back to tips"):
        st.session_state.show_form = False
        st.session_state.edit_tip = None
        st.rerun()

else:
    # Display tips
    if tips:
        # Filter tips by selected category
        filtered_tips = tips
        if st.session_state.selected_category != "All":
            filtered_tips = [t for t in tips if t.get('category') == st.session_state.selected_category]
        
        if not filtered_tips:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">💡</div>
                <h3>No tips in this category</h3>
                <p>No health tips found for the selected category</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"### 💡 Health Tips ({len(filtered_tips)})")
            
            for tip in filtered_tips:
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="tip-card">
                        <div class="tip-header">
                            <span class="tip-category">{tip.get('category', 'General')}</span>
                        </div>
                        <p class="tip-content">{tip['content']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Edit and delete buttons (only show on hover via CSS)
                    if st.button("✏️", key=f"edit_{tip['id']}", help="Edit tip"):
                        st.session_state.edit_tip = tip
                        st.session_state.show_form = True
                        st.rerun()
                    
                    if st.button("🗑️", key=f"delete_{tip['id']}", help="Delete tip"):
                        if delete_tip(tip['id']):
                            st.success("Tip deleted successfully")
                            st.rerun()
                        else:
                            st.error("Failed to delete tip")
    
    else:
        # Empty state
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">💡</div>
            <h3>No health tips yet</h3>
            <p>Be the first to share health wisdom and help others</p>
            <p>Click the "Add New Tip" button to share your knowledge</p>
        </div>
        """, unsafe_allow_html=True)

# Daily Random Tip Section
st.markdown("---")
st.markdown("### 🎲 Today's Random Health Tip")

if random_tip:
    st.markdown(f"""
    <div class="tip-card">
        <div class="tip-header">
            <span class="tip-category">{random_tip.get('category', 'General')}</span>
        </div>
        <p class="tip-content">{random_tip['content']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Get Another Random Tip"):
        # Force refresh by clearing cache
        st.rerun()
else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">💡</div>
        <h3>No random tip available</h3>
        <p>Add some health tips to see random suggestions</p>
    </div>
    """, unsafe_allow_html=True)

# Health Tips Guidelines
st.markdown("---")
st.markdown("### 📋 Tips for Writing Good Health Advice")

guideline_col1, guideline_col2, guideline_col3 = st.columns(3)

with guideline_col1:
    st.info("""
    **Be Specific**  
    - Provide clear, actionable advice
    - Include practical examples
    - Avoid vague statements
    - Use simple language
    """)

with guideline_col2:
    st.info("""
    **Stay Positive**  
    - Focus on benefits and solutions
    - Use encouraging language
    - Share success stories
    - Be supportive and kind
    """)

with guideline_col3:
    st.info("""
    **Category Appropriately**  
    - Choose relevant categories
    - Create new categories if needed
    - Keep similar tips together
    - Help others find your advice
    """)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Health Companion - Senior Citizen Care App</div>", unsafe_allow_html=True)
