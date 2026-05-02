"""
=============================================================================
MODULE: Career Hub Main Application Interface (app.py)
AUTHOR: Kyle W. Killebrew
DESCRIPTION: 
    This script serves as the frontend interface (the "View" layer) of the 
    application. It functions similarly to MATLAB's App Designer, converting 
    the backend data structures (from portfolio_loader.py) into an interactive 
    web application using Streamlit.
=============================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# =====================================================================
# 1. ENVIRONMENT SETUP & PATHING
# =====================================================================
# Ensure Colab's background process (and Streamlit Cloud) can always find sibling files
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the data models. This keeps our UI code perfectly separated from 
# our data logic (Model-View architecture).
from portfolio_loader import get_biographic_metadata, get_portfolio_metadata, get_teaching_metadata, get_references_metadata

# Fetch all metadata into memory at startup so the app runs instantaneously.
bio = get_biographic_metadata()
pubs, skills, beliefs, academic = get_portfolio_metadata()
teaching = get_teaching_metadata()
references_data = get_references_metadata()


# =====================================================================
# 2. FILE DIRECTORY CONFIGURATION
# =====================================================================
# Single Source of Truth for file paths. If a filename changes in your repo, 
# you only ever have to update it right here.
HEADSHOT_FILE = "Documents/kyle.jpg"
DS_RESUME_FILE = "Documents/KWK_Data_Science_Resume_20240520.pdf"
AI_RESUME_FILE = "Documents/KWK_SME_AI_Resume_20260325.pdf"
TEACHING_RESUME_FILE = "Documents/KWK_Teacher_Resume_20260305.pdf"
ACADEMIC_CV_FILE = "Documents/KWK_Academic_CV_20240520.pdf"


# =====================================================================
# 3. GLOBAL APP CONFIGURATION & STYLING
# =====================================================================
# Must be the very first Streamlit command. Sets browser tab properties.
st.set_page_config(
    page_title=f"{bio['name']} | Portfolio",
    page_icon="🔬",
    layout="wide" # Uses the full width of the monitor rather than a narrow central column
)

# Injecting Custom CSS: Streamlit allows raw HTML/CSS injection to override default styling.
st.markdown("""
    <style>
    .ref-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin-bottom: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .ref-name { font-weight: bold; color: #007bff; margin-bottom: 0px; }
    .ref-title { font-size: 0.9em; color: #6c757d; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)


# =====================================================================
# 4. SIDEBAR & NAVIGATION ROUTING
# =====================================================================
# The sidebar acts as persistent real estate that stays visible on every page.
with st.sidebar:
    st.markdown("### 🔗 Quick Links")
    st.write("[Google Scholar](https://scholar.google.com/citations?user=y-2G-voAAAAJ&hl=en)")
    st.write("[ORCID Profile](https://orcid.org/0000-0002-9662-9844)")
    st.write("[GitHub](https://github.com/kkillebrew/)")
    st.write("[LinkedIn](https://www.linkedin.com/in/kylewkillebrew/)")

# Main Header Title
st.title(f"🌐 {bio['name']}")
st.caption(bio['title'])

# Main Navigation Router: We use a horizontal radio button to act as a 
# navigation bar. 'label_visibility="collapsed"' hides the title text for a cleaner UI.
page = st.radio(
    "Select a Page:", 
    ["🏠 Home & Bio", "📈 Data Science Portfolio", "🎓 Tutoring & Mentoring", "🔬 Researcher Profile"],
    horizontal=True,
    label_visibility="collapsed"
)
st.divider()


# =====================================================================
# 5. PAGE RENDERERS (The 'Switch/Case' Router)
# =====================================================================

if page == "🏠 Home & Bio":
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        # Safely attempt to load the headshot image.
        if os.path.exists(HEADSHOT_FILE):
            st.image(HEADSHOT_FILE, caption=bio['name'], use_container_width=True)
        else:
            st.info(f"📸 **Profile Picture Placeholder**\n\n*(Save your image as '{HEADSHOT_FILE}' in the folder to see it here!)*")
        
        st.markdown("### 🛠 Technical Stack")
        st.code("Python (Pandas/Scikit-learn)\nMATLAB (App Designer)\nSQL & Cloud Data\nStatistical Modeling")

    with col2:
        st.title(bio['name'])
        st.subheader(bio['title'])
        st.write(bio['bio'])
        
        # --- PDF DOCUMENT SERVERS ---
        st.markdown("### 📄 Professional Resumes")
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            if os.path.exists(DS_RESUME_FILE):
                with open(DS_RESUME_FILE, "rb") as pdf_file:
                    st.download_button("📊 Download Data Science Resume", data=pdf_file.read(), file_name="Kyle_Killebrew_Data_Science_Resume.pdf", mime="application/pdf")
            else:
                st.button(f"📊 Data Science Resume (Missing '{DS_RESUME_FILE}')")
                
        with res_col2:
            if os.path.exists(AI_RESUME_FILE):
                with open(AI_RESUME_FILE, "rb") as pdf_file:
                    st.download_button("🤖 Download AI Resume", data=pdf_file.read(), file_name="Kyle_Killebrew_AI_Resume.pdf", mime="application/pdf")
            else:
                st.button(f"🤖 AI Resume (Missing '{AI_RESUME_FILE}')")
        
        st.divider()
        
        # --- REFERENCES (Discreet Note) ---
        with st.expander("📌 Professional References"):
            st.caption("Available for contact regarding my academic, research, and professional tenure:")
            for ref in references_data:
                st.markdown(f"- **{ref['name']}** | *{ref['title']}* | ✉️ `{ref['contact']}`")


elif page == "📈 Data Science Portfolio":
    st.title("Project Showcase & Philosophy")
    
    st.info(f"**Statement of Purpose:** {beliefs['sop']}")
    
    st.markdown("### Core Principles")
    for principle in beliefs['core_principles']:
        st.write(f"✅ {principle}")
        
    st.divider()
    st.subheader("Interactive Pipelines")
    # This section will eventually hold the links to your converted interactive Plotly charts 
    projects = ["Financial Forecasting", "Clustering Analysis", "Signal Processing", "Tutoring Metrics"]
    for project in projects:
        with st.expander(f"📂 View Project: {project}"):
            st.write(f"Detailed analysis for {project}.")
            st.button("Launch App", key=project)


elif page == "🎓 Tutoring & Mentoring":
    st.title("Tutoring & Educational Services")
    
    st.write("### Qualifications")
    for qual in teaching['qualifications']:
        st.success(qual)
        
    st.markdown("### 📄 Teaching Materials")
    if os.path.exists(TEACHING_RESUME_FILE):
        with open(TEACHING_RESUME_FILE, "rb") as pdf_file:
            st.download_button("🎓 Download Teaching Resume", data=pdf_file.read(), file_name="Kyle_Killebrew_Teaching_Resume.pdf", mime="application/pdf")
    else:
        st.warning(f"Save your teaching resume as '{TEACHING_RESUME_FILE}' in the folder to enable the download.")
        
    st.write("### Rates")
    st.json(teaching['rates'])


elif page == "🔬 Researcher Profile":
    st.title("Research & Academic CV")
    
    # Iterating through the DataFrame to create a clean, hyperlinked list instead of a raw table
    st.markdown("### 📚 Selected Publications")
    for _, row in pubs.iterrows():
        st.markdown(f"**{row['Year']}** — **[{row['Title']}]({row['Link']})** \n*📖 {row['Journal']}*")
        st.write("") # Add a little spacing between items
    
    st.divider()
    
    st.markdown("### 📄 Academic Credentials")
    if os.path.exists(ACADEMIC_CV_FILE):
        with open(ACADEMIC_CV_FILE, "rb") as pdf_file:
            st.download_button("🔬 Download Academic CV", data=pdf_file.read(), file_name="Kyle_Killebrew_Academic_CV.pdf", mime="application/pdf")
    else:
         st.warning(f"Save your CV as '{ACADEMIC_CV_FILE}' in the folder to enable the download.")