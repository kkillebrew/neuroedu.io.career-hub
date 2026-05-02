"""
=============================================================================
MODULE: Career Hub Main Application Interface (app.py)
AUTHOR: Kyle W. Killebrew, PhD
VERSION: 2.1 (Production-Ready)
DESCRIPTION: 
    This script serves as the frontend interface (the "View" layer) of the 
    application. Optimized for DigitalOcean deployment.
    
    --- MATLAB BRIDGE: ARCHITECTURE ---
    Unlike MATLAB App Designer which uses an Event-Driven Callback model 
    (where the app waits for a 'ButtonPushedFcn'), Streamlit uses a 
    Declarative Top-Down model. Every time a user interacts with a widget, 
    this ENTIRE script runs again from top to bottom. State is maintained 
    automatically by Streamlit.
=============================================================================
"""

import streamlit as st
import pandas as pd
import os
import sys
import requests

# --- SYSTEM & ENVIRONMENT SETUP ---
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
# Fetching metadata (Equivalent to calling your data load functions 
# during the `startupFcn` in App Designer).
bio = get_biographic_metadata()
pubs, skills, beliefs, _ = get_portfolio_metadata()
teaching = get_teaching_metadata()
references_data = get_references_metadata()

# --- UI & BROWSER CONFIGURATION ---
# MATLAB Equivalent: Setting the properties of the main UIFigure 
# (e.g., app.UIFigure.Name = 'Kyle | PhD Portfolio')
st.set_page_config(
    page_title=f"{bio['name']} | PhD Portfolio",
    page_icon="🔬",
    layout="wide"
)

# --- CUSTOM CSS STYLING ---
# MATLAB Equivalent: Using HTML components or uistyle() in App Designer 
# to override default button colors and shapes.
st.markdown("""
    <style>
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
    hr { margin-top: 1rem; margin-bottom: 1rem; border-color: #eee; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION MENU ---
# MATLAB Equivalent: A `uitabgroup` or a `uibuttongroup`. 
# The selected value dictates which "panel" or layout is visible below.
page = st.radio(
    "Navigation Select", 
    ["🏠 Home", "📈 Data Science", "🎓 Tutoring", "🔬 Research", "✉️ Contact"], 
    horizontal=True, 
    label_visibility="collapsed"
)
st.divider()

# =====================================================================
# PAGE ROUTING (MATLAB Equivalent: Switching Tab Visibility)
# =====================================================================

if page == "🏠 Home":
    # MATLAB Equivalent: A `uigridlayout` with 1 row and 2 columns.
    # The [1, 2] array sets relative widths, like `app.GridLayout.ColumnWidth = {'1x', '2x'}`.
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        img_path = "Documents/kyle.jpg"
        if os.path.exists(img_path): 
            # MATLAB Equivalent: uiimage(app.GridLayout)
            # Updated to width='stretch' to comply with Streamlit's 2026 engine updates
            st.image(img_path, width='stretch', caption=bio['name'])
        else:
            st.info("📸 **Profile Image**\n(Place 'kyle.jpg' in /Documents)")
            
        st.markdown("### 🛠 Technical Stack")
        for s, v in skills.items():
            st.write(f"**{s}**")
            st.progress(v/100) # MATLAB Equivalent: uiprogressbar()
            
    with col2:
        st.title(bio['name']) # MATLAB Equivalent: uilabel(FontSize=24)
        st.subheader(bio['title'])
        st.write(bio['bio'])
        st.divider()
        
        st.subheader("Professional Resumes")
        c1, c2 = st.columns(2)
        ds_path = "Documents/KWK_Data_Science_Resume_20240520.pdf"
        if os.path.exists(ds_path):
            with open(ds_path, "rb") as f: 
                # A download button combines a uibutton and file I/O operations natively
                c1.download_button("📊 Data Science Resume", f.read(), "Killebrew_DS.pdf")
        else:
            c1.button("📊 Resume (File Not Found)", disabled=True)

elif page == "📈 Data Science":
    st.title("Data Science & Modeling")
    st.info(f"**Mission:** {beliefs['sop']}")
    
    st.subheader("Core Principles")
    for p in beliefs['core_principles']: 
        st.write(f"✅ {p}")

elif page == "🎓 Tutoring":
    st.title("Education & Mentorship")
    for q in teaching['qualifications']: 
        st.success(f"🎓 {q}")
    
    st.markdown("### Rates & Inquiries")
    st.info(f"**Current Rates:** {teaching['rates']['Hourly Rate']}")
    st.caption("Custom project-based pricing available for modeling & data design.")

elif page == "🔬 Research":
    st.title("Publications & Tenure")
    
    # Iterating over the Pandas DataFrame (MATLAB Table equivalent) to render links
    for _, row in pubs.iterrows():
        st.markdown(f"**{row['Year']}** | **[{row['Title']}]({row['Link']})**")
        st.caption(f"Journal: {row['Journal']}")
        
    st.divider()
    with st.expander("📌 Professional References"):
        st.caption("Available for contact regarding academic and professional tenure:")
        for ref in references_data:
            st.markdown(f"**{ref['name']}** | {ref['title']} | `{ref['contact']}`")

elif page == "✉️ Contact":
    st.title("Inquiries")
    st.write("Send a message directly to my inbox for consulting or research collaboration.")
    
    # MATLAB Equivalent: A specialized panel where user inputs are 
    # gathered. The `form_submit_button` acts as the primary callback trigger.
    with st.form("contact"):
        name = st.text_input("Name")     # uieditfield('text')
        email = st.text_input("Email")
        msg = st.text_area("Message")    # uitextarea()
        
        if st.form_submit_button("Send"):
            # Fetching the API Key from Streamlit Secrets (DO/Cloud)
            key = st.secrets.get("WEB3FORMS_KEY", "")
            
            if key and name and email and msg:
                # MATLAB Equivalent: webwrite() or urlread() to send REST payloads
                res = requests.post(
                    "https://api.web3forms.com/submit", 
                    json={"access_key": key, "name": name, "email": email, "message": msg}
                )
                if res.status_code == 200: 
                    st.success("Message Sent! I will get back to you shortly.")
                else: 
                    st.error("Error sending message. Please email me at kylewkillebrew@gmail.com")
            else: 
                st.warning("Please fill out all fields and ensure the API key is configured.")
