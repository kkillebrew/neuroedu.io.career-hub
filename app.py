"""
=============================================================================
MODULE: Career Hub Main Application (app.py)
AUTHOR: Kyle W. Killebrew, PhD
VERSION: 3.3 (Structural Refinement)
DESCRIPTION: 
    Premium frontend for neuro-edu.io. Optimized for 2026 Streamlit.
    References moved to Home Page; quotes removed for professional clarity.
=============================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import requests

# --- SYSTEM SETUP ---
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

# --- DATA HYDRATION ---
bio = get_biographic_metadata()
pubs, skills, beliefs, academic = get_portfolio_metadata()
teaching = get_teaching_metadata()
references = get_references_metadata()

# --- UI CONFIGURATION ---
st.set_page_config(
    page_title=f"{bio['name']} | Portfolio",
    page_icon="🔬",
    layout="wide"
)

# --- PREMIUM AESTHETIC STYLING (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #fdfdfd; }
    
    html, body, [class*="st-"] {
        font-size: 1.15rem; 
        color: #1e293b;     
        font-family: 'Inter', sans-serif;
    }

    section[data-testid="stSidebar"] {
        background-color: #0f172a; 
        color: #f8fafc;
        border-right: 1px solid #334155;
    }
    
    section[data-testid="stSidebar"] .stText, 
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #f8fafc !important;
    }

    /* Refined Reference Cards - Minimized for contact-only view */
    .ref-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        border-left: 5px solid #2563eb; 
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #f1f5f9;
    }
    .ref-name { 
        font-weight: 800; 
        color: #1e3a8a; 
        font-size: 1.2rem; 
        margin-bottom: 2px;
    }
    .ref-title { 
        font-size: 0.95rem; 
        color: #64748b; 
        font-style: italic; 
        display: block;
        margin-bottom: 8px;
    }
    .ref-contact {
        font-size: 0.9rem;
        color: #2563eb;
        font-family: monospace;
    }
    
    h1, h2, h3 { color: #0f172a !important; font-weight: 800 !important; }
    
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    img_path = "Documents/kyle.jpg"
    if os.path.exists(img_path):
        st.image(img_path, width='stretch')
    else:
        st.info("📸 Profile Image Missing")
    
    st.markdown(f"## {bio['name']}")
    st.markdown(f"**{bio['title']}**")
    
    st.divider()
    st.subheader("🌐 Presence")
    st.markdown(f"🔬 [ORCID Profile](https://orcid.org/{academic.get('orcid', '')})")
    st.markdown(f"📈 [Google Scholar]({academic.get('google_scholar', '#')})")
    st.markdown(f"💼 [LinkedIn Profile]({academic.get('linkedin', '#')})")
    
    st.divider()
    st.caption("PhD Portfolio System | 2026")

# --- TOP NAVIGATION ---
page = st.radio(
    "Navigation Select", 
    ["🏠 Home", "📊 Data Science", "🎓 Education", "🔬 Research", "✉️ Contact"], 
    horizontal=True, 
    label_visibility="collapsed"
)
st.divider()

# =====================================================================
# PAGE LOGIC
# =====================================================================

if page == "🏠 Home":
    # SECTION 1: Bio and Skills
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.markdown("### Strategic Summary")
        st.write(bio['bio'])
        
        st.markdown("### Resume & Assets")
        ds_path = "Documents/KWK_Data_Science_Resume_20240520.pdf"
        if os.path.exists(ds_path):
            with open(ds_path, "rb") as f:
                st.download_button("📂 Download Professional CV", f.read(), "Killebrew_CV.pdf")
        
    with col2:
        st.markdown("### Core Expertise")
        df_skills = pd.DataFrame(dict(r=list(skills.values()), theta=list(skills.keys())))
        fig = px.line_polar(df_skills, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', line_color='#2563eb', fillcolor='rgba(37, 99, 235, 0.3)')
        fig.update_layout(
            polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True, range=[0, 100])),
            margin=dict(l=60, r=60, t=20, b=20), height=450
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    
    # SECTION 2: Professional Endorsements (Now at bottom of Home)
    st.markdown("### Professional References")
    st.caption("Academic and industry leaders available for verification of tenure and technical expertise.")
    
    ref_cols = st.columns(3) # Using 3 columns for better fit on home page
    for i, ref in enumerate(references):
        col = ref_cols[i % 3]
        col.markdown(f"""
            <div class="ref-card">
                <span class="ref-name">{ref['name']}</span>
                <span class="ref-title">{ref['title']}</span>
                <span class="ref-contact">{ref['contact']}</span>
            </div>
        """, unsafe_allow_html=True)

elif page == "📊 Data Science":
    st.title("Data Science Hub")
    st.markdown(f"> **Core Mission:** {beliefs['sop']}")
    
    st.markdown("### Foundational Principles")
    p_cols = st.columns(2)
    for i, p in enumerate(beliefs['core_principles']):
        p_cols[i%2].markdown(f"**{p}**")

    st.divider()
    st.markdown("### Interactive 'Spoke' Applications")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 💹 Financial Forecasting")
        st.caption("Time-series analysis and predictive modeling.")
        st.button("Launch Analysis", key="fin_spoke")
    with c2:
        st.markdown("#### 🧠 Neural Signal Processor")
        st.caption("DSP pipelines for EEG population data.")
        st.button("Launch Analysis", key="sig_spoke")

elif page == "🎓 Education":
    st.title("Educational Mentorship")
    for q in teaching['qualifications']:
        st.success(f"**{q}**")
    
    st.divider()
    st.markdown("### The MATLAB-to-Python Bridge")
    st.write("I specialize in helping researchers transition from script-based visual environments to production-grade Python data pipelines.")
    st.info(f"**Current Consultation Rate:** {teaching['rates']['Standard Hourly']}")

elif page == "🔬 Research":
    st.title("Scientific Contributions")
    st.caption("Peer-reviewed publications and primary research contributions.")
    for _, row in pubs.iterrows():
        st.markdown(f"#### [{row['Title']}]({row['Link']})")
        st.markdown(f"*{row['Year']}* — **{row['Journal']}**")
        st.divider()

elif page == "✉️ Contact":
    st.title("Collaborate")
    with st.form("contact_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        msg = st.text_area("How can I help you?")
        if st.form_submit_button("Submit Inquiry"):
            key = st.secrets.get("WEB3FORMS_KEY", "")
            if key and name and email and msg:
                res = requests.post("https://api.web3forms.com/submit", 
                                    json={"access_key": key, "name": name, "email": email, "message": msg})
                if res.status_code == 200:
                    st.success("Your inquiry has been transmitted.")
                else:
                    st.error("Submission failed. Contact kylewkillebrew@gmail.com")
            else:
                st.warning("Please provide contact details and message.")
