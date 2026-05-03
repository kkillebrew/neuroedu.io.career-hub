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
    get_references_metadata
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

# --- AESTHETIC STYLING (High-Contrast Professional) ---
st.markdown("""
    <style>
    .stApp { background-color: #fdfdfd; }
    html, body, [class*="st-"] { font-size: 1.15rem; color: #1e293b; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #0f172a !important; font-weight: 800 !important; }

    /* Sidebar: Deep Navy contrast */
    section[data-testid="stSidebar"] { background-color: #0f172a; color: #f8fafc; border-right: 1px solid #334155; }
    section[data-testid="stSidebar"] .stText, section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 { color: #f8fafc !important; }

    /* Reference Cards - Modern minimalist */
    .ref-card {
        background-color: #ffffff; padding: 24px; border-radius: 12px;
        border-left: 5px solid #2563eb; margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border: 1px solid #f1f5f9;
    }
    .ref-name { font-weight: 800; color: #1e3a8a; font-size: 1.2rem; }
    .ref-title { font-size: 0.95rem; color: #64748b; font-style: italic; display: block; margin-bottom: 8px; }
    .ref-contact { font-size: 0.9rem; color: #2563eb; font-family: monospace; }

    /* Data Projects Gateway Button */
    .data-gate {
        background-color: #2563eb; color: white !important; padding: 18px;
        border-radius: 10px; text-align: center; font-weight: bold; 
        text-decoration: none; display: block; font-size: 1.2rem;
        transition: background-color 0.3s ease;
    }
    .data-gate:hover { background-color: #1d4ed8; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    img_path = "documents/kyle.jpg"
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    
    st.markdown(f"## {bio['name']}")
    st.markdown(f"**{bio['title']}**")
    
    st.divider()
    st.subheader("🌐 Presence")
    st.markdown(f"🔬 [ORCID Profile](https://orcid.org/{academic.get('orcid', '')})")
    st.markdown(f"📈 [Google Scholar]({academic.get('google_scholar', '#')})")
    st.markdown(f"💼 [LinkedIn Profile]({academic.get('linkedin', '#')})")
    
    st.divider()
    st.caption("PhD Portfolio System | 2026")

# --- MAIN HUB LAYOUT ---
# We keep the landing page focused on Bio, CV, Skills, and Social Proof
st.title("Professional Summary")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### Strategic Vision")
    st.write(bio['bio'])
    
    st.divider()
    st.markdown("### Professional Documentation")
    cv_path = "documents/kyle_killebrew_cv.pdf"
    if os.path.exists(cv_path):
        with open(cv_path, "rb") as f:
            st.download_button("📂 Download Professional CV", f.read(), "Killebrew_CV.pdf")
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
st.header("🔬 Interactive Data Portfolio")
st.write("For detailed analytical projects, including financial forecasting, signal processing pipelines, and machine learning models, please visit my dedicated Data Science Hub.")
st.markdown('<a href="https://data-projects.neuro-edu.io" target="_blank" class="data-gate">Launch Data Science Projects Hub →</a>', unsafe_allow_html=True)

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