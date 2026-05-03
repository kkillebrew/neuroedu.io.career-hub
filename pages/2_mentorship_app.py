"""
=============================================================================
MODULE: pages/2_mentorship_app.py
AUTHOR: Kyle W. Killebrew, PhD
VERSION: 1.0 (Spoke App)
DESCRIPTION: 
    The Educational Mentorship & Tutoring sub-page for career-hub.neuro-edu.io.
    Utilizes the 1-to-1 mentorship_loader.py.
=============================================================================
"""
import streamlit as st
import os
import sys

# --- PATH CONFIGURATION ---
# This tells the script to look one folder up to find the 'loaders' directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- IMPORT DATA ---
from loaders.mentorship_loader import get_mentorship_data

# Initialize the data from the loader
mentorship = get_mentorship_data()

from career_hub_loader import (
    get_biographic_metadata
    get_portfolio_metadata
)

pubs, skills, academic = get_portfolio_metadata()   
bio = get_biographic_metadata()
_, _, academic = get_portfolio_metadata()

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Mentorship | Kyle Killebrew", layout="wide")

# --- SHARED AESTHETIC STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #fdfdfd; }
    html, body, [class*="st-"] { font-size: 1.15rem; color: #1e293b; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #0f172a !important; font-weight: 800 !important; }
    
    /* Highlight Box */
    .method-box {
        padding: 20px;
        background-color: #f8fafc;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }
    .method-title { font-weight: 700; color: #1e3a8a; }
    
    /* Pricing Card */
    .rate-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        border-top: 5px solid #2563eb;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #f1f5f9;
    }
    .rate-price { font-size: 1.5rem; font-weight: 800; color: #2563eb; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:

    # --- 1. HIDE DEFAULT NAVIGATION ---
    # This CSS turns off Streamlit's ugly auto-generated file list
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none !important;}
        </style>
    """, unsafe_allow_html=True)

    # --- 2. CUSTOM DIRECTORY MENU ---
    st.divider()
    st.subheader("🧭 Directory")
    
    # Internal Pages (Make sure these filenames perfectly match your GitHub!)
    st.page_link("career_hub_app.py", label="Hub", icon="🏠")
    st.page_link("pages/1_academic_research_app.py", label="Academic Research Profile", icon="🔬")
    st.page_link("pages/2_mentorship_app.py", label="Academic Mentorship", icon="🎓")
    
    # External Data Hub Link (Styled to match your deep navy sidebar text)
    st.markdown("""
        <div style="padding: 0.35rem 0;">
            <a href="https://data-projects.neuro-edu.io" target="_blank" style="text-decoration: none; color: #f8fafc; font-size: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                📊 <span>Data Science Projects ↗</span>
            </a>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    # --- 3. MY SOCIALS ---
    st.subheader("🌐 Presence")
    st.markdown(f"🔬 [ORCID Profile](https://orcid.org/{academic.get('orcid', '')})")
    st.markdown(f"📈 [Google Scholar]({academic.get('google_scholar', '#')})")
    st.markdown(f"💼 [LinkedIn Profile]({academic.get('linkedin', '#')})")
    
    st.divider()
    st.caption("PhD Portfolio System | 2026")

# --- HEADER ---
st.title("Mentorship & Educational Design")
st.markdown("Bridging the gap between theory and practice through personalized, inquiry-based guidance.")

st.divider()

# --- TOP SECTION: Qualifications ---
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.header("Core Qualifications")
    for qual in mentorship['qualifications']:
        st.success(f"🎓 **{qual}**")

with col2:
    st.header("Financials")
    for rate_type, price in mentorship['rates'].items():
        st.markdown(f"""
            <div class="rate-card">
                <div style="font-size:0.9rem; color:#64748b; text-transform:uppercase;">{rate_type}</div>
                <div class="rate-price">{price}</div>
            </div>
            <br>
        """, unsafe_allow_html=True)

st.divider()

# --- BOTTOM SECTION: Methodology ---
st.header("Teaching Methodology")
st.write("My approach is designed specifically for researchers and industry professionals who need to master data tools without losing sight of scientific rigor.")

m_cols = st.columns(3)
for i, method in enumerate(mentorship['methodology']):
    with m_cols[i]:
        title, desc = method.split(":", 1)
        st.markdown(f"""
            <div class="method-box">
                <div class="method-title">{title}</div>
                <div style="font-size:0.95rem; color:#475569;">{desc.strip()}</div>
            </div>
        """, unsafe_allow_html=True)

# Mentorship section
st.title("Education & Mentorship")

tab1, tab2, tab3 = st.tabs(["🎓 Qualifications", "📝 Learner Profiles", "💡 Strategies"])

with tab1:
    st.header("Teaching Resume")
    # Download button for Teaching-specific resume
    t_cv = "documents/kyle_teaching_cv.pdf"
    if os.path.exists(t_cv):
         with open(t_cv, "rb") as f:
            st.download_button("📂 Download Teaching Resume", f.read(), "Killebrew_Teaching.pdf")
    
    st.markdown("[Visit my Wyzant Profile](https://www.wyzant.com/tutors/your_link_here)")

with tab2:
    st.header("Inquiry-Based Learner Profiles")
    st.write("I utilize standardized learner profile documents to track progress in:")
    st.markdown("- Programming Logic\n- Mathematical Intuition\n- Research Reproducibility")

with tab3:
    st.header("Educational Strategies")
    st.write("Specialized methodologies for MATLAB-to-Python transitions...")
    # Add your learning strategies here

# --- CONTACT CTA ---
st.divider()
st.info("💡 **Ready to accelerate your learning?** Use the Contact tab on the main page to inquire about session availability.")