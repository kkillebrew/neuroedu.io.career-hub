"""
=============================================================================
MODULE: career_hub_app.py (Main Hub Entry Point)
AUTHOR: Kyle W. Killebrew, PhD
VERSION: 4.0 (Micro-Frontend Hub)
DESCRIPTION: 
    The landing page for career-hub.neuro-edu.io. Handles professional
    summary, CV downloads, and links to the Data Projects spoke hub.
=============================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
import requests

# Ensure local imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from career_hub_loader import (
    get_biographic_metadata, 
    get_portfolio_metadata, 
    get_references_metadata,
)

# --- DATA HYDRATION ---
bio = get_biographic_metadata()
pubs, skills, academic = get_portfolio_metadata()
references = get_references_metadata()

# --- UI CONFIGURATION ---
st.set_page_config(
    page_title=f"{bio['name']} | PhD Portfolio",
    page_icon="🔬",
    layout="wide"
)

########################################
#  RENDER THE SIDEBAR FOR CAREER-HUB   #
########################################
from career_hub_sidebar import render_sidebar
render_sidebar()

# --- MAIN HUB LAYOUT ---
# 1. TOP ROW: Profile Image and Title
col_img, col_text = st.columns([1, 4], gap="large")

with col_img:
    # This forces Streamlit to look relative to exactly where career_hub_app.py lives
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base_dir, "documents", "kyle.jpg")
    
    if os.path.exists(img_path):
        st.image(img_path, width='stretch')
    else:
        # Now it will tell you exactly what path it is failing to find!
        st.warning(f"Image not found. Looked in: {img_path}")

with col_text:
    st.title(bio['name'])
    st.subheader(bio['title'])

st.divider()

# 2. BOTTOM ROW: Bio/CV and Radar Chart
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### Strategic Vision")
    st.write(bio['bio'])
    
    st.divider()
    st.markdown("### Professional Documentation")
    cv_path = "documents/KWK_Academic_CV_20240520.pdf"
    if os.path.exists(cv_path):
        with open(cv_path, "rb") as f:
            st.download_button("📂 Download Professional CV", f.read(), "KWK_Academic_CV_20240520.pdf")
    else:
        st.button("📄 CV Not Found in /documents", disabled=True)

with col2:
    st.markdown("### Core Competencies")
    df_skills = pd.DataFrame(dict(r=list(skills.values()), theta=list(skills.keys())))
    fig = px.line_polar(df_skills, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='#2563eb', fillcolor='rgba(37, 99, 235, 0.3)')
    fig.update_layout(
        polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True, range=[0, 100])),
        margin=dict(l=60, r=60, t=20, b=20), height=400
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# GATEWAY TO THE SPOKE HUB
st.header("Explore My Work")
t1, t2, t3 = st.columns(3)

# st.header("🔬 Interactive Data Portfolio")
# st.write("For detailed analytical projects, including financial forecasting, signal processing pipelines, and machine learning models, please visit my dedicated Data Science Hub.")
# st.markdown('<a href="https://data-projects.neuro-edu.io" target="_blank" class="data-gate">Launch Data Science Projects Hub →</a>', unsafe_allow_html=True)

with t1:
    st.markdown("""
        <div class="ref-card">
            <div class="ref-name">🔬 Academic Research</div>
            <p style="font-size:0.9rem; color:#475569;">Peer-reviewed publications, neural variance modeling, and academic tenure.</p>
        </div>
    """, unsafe_allow_html=True)
    # This button uses the Streamlit MPA command to switch pages
    if st.button("View Research Spoke", key="goto_research"):
        st.switch_page("pages/1_academic_research_app.py")

with t2:
    st.write("For detailed analytical projects, including financial forecasting, signal processing pipelines, and machine learning models, please visit my dedicated Data Science Hub.")
    st.markdown("""
        <div class="ref-card">
            <div class="ref-name">📊 Data Science Hub</div>
            <p style="font-size:0.9rem; color:#475569;">Predictive analytics, machine learning, and interactive signal processing dashboards.</p>
        </div>
    """, unsafe_allow_html=True)
    # External link for the unique domain
    st.markdown('<a href="https://data-projects.neuro-edu.io" target="_blank" class="data-gate" style="font-size:0.9rem; padding:10px;">Launch External Data Hub</a>', unsafe_allow_html=True)

with t3:
    st.markdown("""
        <div class="ref-card">
            <div class="ref-name">🎓 Mentorship</div>
            <p style="font-size:0.9rem; color:#475569;">Educational design, personalized tutoring, and MATLAB-to-Python transition strategies.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("View Mentorship Spoke", key="goto_edu"):
        st.switch_page("pages/2_mentorship_app.py")

st.divider()

# REFERENCES SECTION (Now at bottom of Home)
st.header("Professional References")
st.caption("Academic and industry leaders available for verification of tenure and technical expertise.")
ref_cols = st.columns(3)
for i, ref in enumerate(references):
    with ref_cols[i % 3]:
        st.markdown(f"""
            <div class="ref-card">
                <span class="ref-name">{ref['name']}</span>
                <span class="ref-title">{ref['title']}</span>
                <span class="ref-contact">{ref['contact']}</span>
            </div>
        """, unsafe_allow_html=True)