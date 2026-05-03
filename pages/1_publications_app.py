"""
=============================================================================
MODULE: pages/1_publications_app.py
AUTHOR: Kyle W. Killebrew, PhD
VERSION: 1.0 (Spoke App)
DESCRIPTION: 
    The Academic Research sub-page for career-hub.neuro-edu.io.
    Utilizes the 1-to-1 publications_loader.py.
=============================================================================
"""

import streamlit as st
import os
import sys

# Ensure the app can find the loaders folder from the pages sub-directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loaders.publications_loader import get_publications_data, get_publication_metrics

# --- DATA LOAD ---
pubs_df = get_publications_data()
metrics = get_publication_metrics()

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Publications | Kyle Killebrew", layout="wide")

# --- SHARED AESTHETIC STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #fdfdfd; }
    html, body, [class*="st-"] { font-size: 1.15rem; color: #1e293b; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #0f172a !important; font-weight: 800 !important; }
    
    /* Academic Item Card */
    .pub-box {
        padding: 25px;
        background-color: #ffffff;
        border-radius: 12px;
        border-left: 5px solid #2563eb;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #f1f5f9;
    }
    .pub-title { font-size: 1.25rem; font-weight: 700; color: #1e3a8a; line-height: 1.4; }
    .pub-meta { font-size: 0.95rem; color: #64748b; margin-top: 8px; }
    .pub-year { font-weight: 800; color: #2563eb; margin-right: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("Scientific Contributions")
st.markdown("A comprehensive record of peer-reviewed research, theoretical modeling, and academic tenure.")

# --- METRICS BAR ---
m_col1, m_col2, m_col3 = st.columns(3)
m_col1.metric("Research Areas", "3 Primary")
m_col2.metric("Publications", len(pubs_df))
m_col3.metric("Experience", "15+ Years")

st.divider()

# --- PUBLICATIONS LIST ---
# MATLAB Equivalent: A loop iterating through the rows of a Table (T)
for _, row in pubs_df.iterrows():
    st.markdown(f"""
        <div class="pub-box">
            <div class="pub-title"><a href="{row['Link']}" style="text-decoration:none; color:inherit;">{row['Title']}</a></div>
            <div class="pub-meta">
                <span class="pub-year">{row['Year']}</span> 
                | <i>{row['Journal']}</i>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- FOOTER NAVIGATION ---
st.divider()
st.caption("All links direct to full-text PDF or journal landing pages.")