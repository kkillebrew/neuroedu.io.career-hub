"""
=============================================================================
MODULE: career_hub_sidebar.py (UI Controller)
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    Centralized sidebar component for the Career Hub ecosystem.
    Imports into app.py and all pages/ scripts to ensure a uniform
    UI without duplicating code.
=============================================================================
"""

import streamlit as st
import os
from PIL import Image

def apply_global_settings(hub_title):
    """
    Sets the favicon and page title across the hub.
    """
    favicon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "documents", "Neuro-Edu_favicon_Transparent.ico")

    try:
        favicon = Image.open(favicon_path)
    except Exception:
        favicon = "🧠" 

    st.set_page_config(
        page_title=hub_title,
        page_icon=favicon,
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_sidebar():
    """
    Renders the centralized sidebar with custom CSS and navigation.
    """
    # --- 1. GLOBAL SIDEBAR CSS (Styling & Bug Fixes) ---
    st.markdown("""
        <style>
        /* Hide the default Streamlit sidebar navigation menu */
        [data-testid="stSidebarNav"] {display: none;}
        
        /* Fix the Chevron Bug: Prevent custom fonts from overriding icons */
        [data-testid="collapsedControl"] {
            font-family: sans-serif !important; 
        }

        /* Standardize Sidebar Background & STRICTLY Enforce Text Color */
        [data-testid="stSidebar"] {
            background-color: #0F172A !important; 
        }
        
        /* Prevents Streamlit's Light/Dark mode auto-detect from turning text gray */
        [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
            color: #F8FAFC !important;
        }
        
        /* Masthead styling */
        .masthead-container {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-top: -40px; 
            margin-bottom: 30px;
        }
        .masthead-text {
            line-height: 1.25;
        }
        .masthead-name {
            font-size: 1.15rem;
            font-weight: bold;
            color: #F8FAFC !important;
            margin-bottom: 4px;
        }
        .masthead-title {
            font-size: 0.75rem; 
            color: #94A3B8 !important; 
            line-height: 1.3;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # --- 2. MASTHEAD ---        
        col1, col2 = st.columns([1, 2.5], gap="small")
        
        with col1:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(base_dir, "documents", "Neuro-Edu_Logo_Transparent.png")
            
            if os.path.exists(logo_path):
                st.image(logo_path, use_container_width=True)
            else:
                st.write("🧠") 
        
        with col2:
             st.markdown("""
                <div class="masthead-text">
                    <div class="masthead-name">Kyle W. Killebrew, PhD</div>
                    <div class="masthead-title">Behavioral, Cognitive, Neuro, and Data Scientist and Educational Mentor</div>
                </div>
            """, unsafe_allow_html=True)

        st.divider()
        
        # --- 3. CUSTOM NAVIGATION ---
        st.markdown("### Navigation")
        
        # Internal Streamlit Page Links
        st.page_link("career_hub_app.py", label="Home / Hub", icon="🏠")
        st.page_link("pages/1_academic_research_app.py", label="Academic Research", icon="🔬")
        st.page_link("pages/2_mentorship_app.py", label="Education & Mentorship", icon="📚")
        
        # External Data Science Link (Opens in new tab)
        st.markdown("""
            <div style="margin-top: 5px;">
                <a href="https://data-projects.neuro-edu.io/" target="_blank" style="text-decoration: none; color: #F8FAFC; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.2rem;">📊</span> 
                    <span style="font-size: 1rem;">Data Science Portfolio ↗</span>
                </a>
            </div>
        """, unsafe_allow_html=True)