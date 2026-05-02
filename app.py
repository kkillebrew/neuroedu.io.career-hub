"""
=============================================================================
MODULE: Career Hub Main Application (app.py)
AUTHOR: Kyle W. Killebrew, PhD
VERSION: 3.0 (Enhanced UI)
DESCRIPTION: 
    Professional frontend for neuro-edu.io. Optimized for 2026 Streamlit.
    
    --- MATLAB BRIDGE: ARCHITECTURE ---
    Think of this as your "App Designer" .mlapp file. While MATLAB uses 
    callbacks, Streamlit uses a top-down execution model. Every interaction 
    re-runs the script, but state is preserved by the framework.
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
# Ensures that the app can find 'portfolio_loader.py' in the same directory
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
# MATLAB Equivalent: Initializing variables during the startupFcn.
bio = get_biographic_metadata()
pubs, skills, beliefs, academic = get_portfolio_metadata()
teaching = get_teaching_metadata()
references = get_references_metadata()

# --- UI CONFIGURATION ---
st.set_page_config(
    page_title=f"{bio['name']} | PhD Portfolio",
    page_icon="🔬",
    layout="wide"
)

# --- ADVANCED STYLING ---
# Using Custom CSS to create professional 'Reference Cards' and sidebar tweaks.
st.markdown("""
    <style>
    /* Reference Cards */
    .ref-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #007bff;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .ref-name { font-weight: 800; color: #007bff; margin-bottom: 2px; font-size: 1.1rem; }
    .ref-title { font-size: 0.85rem; color: #6c757d; font-style: italic; margin-bottom: 10px; }
    .ref-quote { font-size: 0.95rem; line-height: 1.5; color: #333; }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e9ecef;
    }
    
    /* Button Hover Effects */
    .stButton>button {
        transition: all 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: Profile & Academic Links ---
with st.sidebar:
    img_path = "Documents/kyle.jpg"
    if os.path.exists(img_path):
        # Using 2026 compliant width='stretch' instead of use_container_width
        st.image(img_path, width='stretch', caption=bio['name'])
    else:
        st.info("📸 **Profile Image**\n(Place 'kyle.jpg' in /Documents)")
    
    st.title(bio['name'])
    st.caption(f"📍 Las Vegas, NV | {bio['title']}")
    
    st.divider()
    st.subheader("🔗 Academic & Professional")
    st.markdown(f"🔬 [ORCID Profile](https://orcid.org/{academic['orcid']})")
    st.markdown(f"📈 [Google Scholar]({academic['google_scholar']})")
    st.markdown(f"💼 [LinkedIn]({academic['linkedin']})")
    
    st.divider()
    st.caption("Built with Python & Streamlit\nDeployed via DigitalOcean")

# --- TOP NAVIGATION ---
# MATLAB Equivalent: TabGroup selection logic.
page = st.radio(
    "Navigation Select", 
    ["🏠 Home", "📊 Data Science", "🎓 Education", "🔬 Research", "✉️ Contact"], 
    horizontal=True, 
    label_visibility="collapsed"
)
st.divider()

# =====================================================================
# PAGE ROUTING
# =====================================================================

if page == "🏠 Home":
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.header("Strategic Summary")
        st.write(bio['bio'])
        
        st.subheader("Professional Assets")
        ds_path = "Documents/KWK_Data_Science_Resume_20240520.pdf"
        if os.path.exists(ds_path):
            with open(ds_path, "rb") as f:
                st.download_button("📊 Download Data Science CV", f.read(), "Killebrew_DS.pdf")
        else:
            st.button("📊 CV (File Not Found)", disabled=True)
        
    with col2:
        st.header("Skills Radar")
        # Visualizing skills as a Radar Chart (MATLAB Equivalent: spiderplot)
        df_skills = pd.DataFrame(dict(r=list(skills.values()), theta=list(skills.keys())))
        fig = px.line_polar(df_skills, r='r', theta='theta', line_close=True, range_r=[0,100])
        fig.update_traces(fill='toself', line_color='#007bff')
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            margin=dict(l=40, r=40, t=40, b=40),
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)

elif page == "📊 Data Science":
    st.title("Data Science & Modeling Philosophy")
    st.info(f"**Mission:** {beliefs['sop']}")
    
    st.subheader("Core Principles")
    p_cols = st.columns(2)
    for i, p in enumerate(beliefs['core_principles']):
        p_cols[i%2].write(f"✅ {p}")

    st.divider()
    st.subheader("The 'Spoke' Applications")
    st.write("Independent analysis tools containerized and linked to this hub.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📈 Financial Forecaster")
        st.caption("Time-series analysis using Prophet and Scikit-learn.")
        st.button("Launch App (finance.neuro-edu.io)", disabled=True)
    with c2:
        st.markdown("### 🧠 EEG Signal Processor")
        st.caption("FFT analysis and modeling for neural population dynamics.")
        st.button("Launch App (signals.neuro-edu.io)", disabled=True)

elif page == "🎓 Education":
    st.title("Mentorship & Educational Design")
    for q in teaching['qualifications']:
        st.success(f"🎓 {q}")
    
    st.divider()
    st.subheader("Inquiry-Based Tutoring")
    st.write("Specializing in bridging the gap for students moving from visual languages (MATLAB) to scripted data science (Python).")
    st.info(f"**Current Rates:** {teaching['rates']['Standard Hourly']}")

elif page == "🔬 Research":
    st.title("Publications & Tenure")
    
    # MATLAB Table equivalent rendered as clean Markdown with Links
    for _, row in pubs.iterrows():
        st.markdown(f"**{row['Year']}** | **[{row['Title']}]({row['Link']})**")
        st.caption(f"Journal: {row['Journal']}")
    
    st.divider()
    st.subheader("Professional Testimonials")
    
    # Grid layout for reference cards
    ref_cols = st.columns(2)
    for i, ref in enumerate(references):
        col = ref_cols[i % 2]
        col.markdown(f"""
            <div class="ref-card">
                <div class="ref-name">{ref['name']}</div>
                <div class="ref-title">{ref['title']}</div>
                <div class="ref-quote">"{ref['quote']}"</div>
            </div>
        """, unsafe_allow_html=True)

elif page == "✉️ Contact":
    st.title("Inquiries")
    st.write("Reach out for research collaboration or private educational mentorship.")
    
    with st.form("contact"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        msg = st.text_area("Message")
        
        if st.form_submit_button("Send Message"):
            # Fetching API Key from DigitalOcean Environment Variables
            key = st.secrets.get("WEB3FORMS_KEY", "")
            if key and name and email and msg:
                res = requests.post(
                    "https://api.web3forms.com/submit", 
                    json={"access_key": key, "name": name, "email": email, "message": msg}
                )
                if res.status_code == 200:
                    st.success("Message Sent! I'll get back to you shortly.")
                else:
                    st.error("Error sending message. Please email me directly.")
            else:
                st.warning("Please fill out all fields.")
