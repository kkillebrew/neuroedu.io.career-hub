"""
=============================================================================
MODULE: Career Hub Main Application Interface (app.py)
AUTHOR: Kyle W. Killebrew, PhD
VERSION: 2.0 (Production-Ready)
DESCRIPTION: 
    This script serves as the frontend interface (the "View" layer) of the 
    application. It converts backend data structures (from portfolio_loader.py) 
    into an interactive web application using Streamlit. 
    
    The architecture follows a Model-View pattern to ensure data management 
    is isolated from UI design. Optimized for DigitalOcean deployment.
=============================================================================
"""

import streamlit as st
import pandas as pd
import os
import sys
import requests

# --- SYSTEM & ENVIRONMENT SETUP ---
# Appending the current directory to sys.path ensures that the 'portfolio_loader' 
# module can be imported regardless of the execution environment.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from portfolio_loader import (
        get_biographic_metadata, 
        get_portfolio_metadata, 
        get_teaching_metadata, 
        get_references_metadata
    )
except ImportError as e:
    st.error(f"Critical Error: Could not find 'portfolio_loader.py'. {e}")
    st.stop()

# --- DATA INITIALIZATION ---
# We fetch all metadata at startup to minimize latency during page navigation.
bio = get_biographic_metadata()
pubs, skills, beliefs, _ = get_portfolio_metadata()
teaching = get_teaching_metadata()
references_data = get_references_metadata()

# --- UI & BROWSER CONFIGURATION ---
st.set_page_config(
    page_title=f"{bio['name']} | PhD Portfolio",
    page_icon="🔬",
    layout="wide"
)

# --- CUSTOM CSS STYLING ---
# We inject raw CSS to customize Streamlit's default components, providing
# a more professional, branded appearance.
st.markdown("""
    <style>
    /* Custom Styling for Main Action Buttons */
    .stButton>button { 
        width: 100%; 
        border-radius: 5px; 
        background-color: #007bff; 
        color: white; 
        border: none;
        font-weight: 500;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover { 
        background-color: #0056b3; 
        border: none; 
    }
    /* Section Divider Styling */
    hr { margin-top: 1rem; margin-bottom: 1rem; border-color: #eee; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION MENU ---
# Using a horizontal radio button as a sleek navigation bar.
page = st.radio(
    "Navigation Select", 
    ["🏠 Home", "📈 Data Science", "🎓 Tutoring", "🔬 Research", "✉️ Contact"], 
    horizontal=True, 
    label_visibility="collapsed"
)
st.divider()

# =====================================================================
# PAGE: 🏠 HOME
# Purpose: Introductory profile, technical stack overview, and resumes.
# =====================================================================
if page == "🏠 Home":
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        # User Headshot logic
        img_path = "Documents/kyle.jpg"
        if os.path.exists(img_path): 
            st.image(img_path, use_container_width=True, caption=bio['name'])
        else:
            st.info("📸 **Profile Image**\n(Place 'kyle.jpg' in /Documents)")
            
        # Technical Skill Progress Bars
        st.markdown("### 🛠 Technical Stack")
        for s, v in skills.items():
            st.write(f"**{s}**")
            st.progress(v/100)
            
    with col2:
        st.title(bio['name'])
        st.subheader(bio['title'])
        st.write(bio['bio'])
        st.divider()
        
        # Resume Download Section
        st.subheader("Professional Resumes")
        c1, c2 = st.columns(2)
        ds_path = "Documents/KWK_Data_Science_Resume_20240520.pdf"
        if os.path.exists(ds_path):
            with open(ds_path, "rb") as f: 
                c1.download_button("📊 Data Science Resume", f.read(), "Killebrew_DS.pdf")
        else:
            c1.button("📊 Resume (File Not Found)", disabled=True)

# =====================================================================
# PAGE: 📈 DATA SCIENCE
# Purpose: Portfolio showcase and technical mission statement.
# =====================================================================
elif page == "📈 Data Science":
    st.title("Data Science & Modeling")
    st.info(f"**Mission:** {beliefs['sop']}")
    
    st.subheader("Core Principles")
    # Looping through principles defined in the loader
    for p in beliefs['core_principles']: 
        st.write(f"✅ {p}")

# =====================================================================
# PAGE: 🎓 TUTORING
# Purpose: Educational qualifications and service rates.
# =====================================================================
elif page == "🎓 Tutoring":
    st.title("Education & Mentorship")
    for q in teaching['qualifications']: 
        st.success(f"🎓 {q}")
    
    st.markdown("### Rates & Inquiries")
    st.info(f"**Current Rates:** {teaching['rates']['Hourly Rate']}")
    st.caption("Custom project-based pricing available for modeling & data design.")

# =====================================================================
# PAGE: 🔬 RESEARCH
# Purpose: Academic publications and professional references.
# =====================================================================
elif page == "🔬 Research":
    st.title("Publications & Tenure")
    # Dynamically rendering publication list from DataFrame
    for _, row in pubs.iterrows():
        st.markdown(f"**{row['Year']}** | **[{row['Title']}]({row['Link']})**")
        st.caption(f"Journal: {row['Journal']}")
        
    st.divider()
    with st.expander("📌 Professional References"):
        st.caption("Available for contact regarding academic and professional tenure:")
        for ref in references_data:
            st.markdown(f"**{ref['name']}** | {ref['title']} | `{ref['contact']}`")

# =====================================================================
# PAGE: ✉️ CONTACT
# Purpose: Lead generation via direct email integration.
# =====================================================================
elif page == "✉️ Contact":
    st.title("Inquiries")
    st.write("Send a message directly to my inbox for consulting or research collaboration.")
    
    with st.form("contact"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        msg = st.text_area("Message")
        
        if st.form_submit_button("Send"):
            # Fetching the API Key from Streamlit Secrets (for DigitalOcean/Cloud)
            key = st.secrets.get("WEB3FORMS_KEY", "")
            
            if key and name and email and msg:
                # API Call to Web3Forms to bridge the email to your inbox
                res = requests.post(
                    "https://api.web3forms.com/submit", 
                    json={"access_key": key, "name": name, "email": email, "message": msg}
                )
                if res.status_code == 200: 
                    st.success("Message Sent! I will get back to you shortly.")
                else: 
                    st.error("Error sending message. Please email me at kylewkillebrew@1mail.com")
            else: 
                st.warning("Please fill out all fields and ensure the API key is configured.")
