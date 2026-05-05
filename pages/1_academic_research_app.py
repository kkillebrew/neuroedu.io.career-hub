# Inside pages/1_academic_research.py
import streamlit as st
import sys
import os
import pandas as pd

# --- PATH CONFIGURATION ---
# This tells the script to look one folder up to find the 'loaders' directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- IMPORT DATA ---
from loaders.academic_research_loader import (
    get_publications_data, 
    get_research_expertise, 
    get_academic_assets
)

# Initialize the data from the loader
pubs_df = get_publications_data()
expertise = get_research_expertise()
assets = get_academic_assets()

from career_hub_loader import (
    get_biographic_metadata,
    get_portfolio_metadata
)

bio = get_biographic_metadata()
_, _, academic = get_portfolio_metadata()

st.title("Academic Career & Research")

########################################
#  RENDER THE SIDEBAR FOR CAREER-HUB   #
########################################
# Point Python to the root directory so it can find the sidebar file
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from career_hub_sidebar import render_sidebar
render_sidebar()

c1, c2 = st.columns([2, 1])

with c1:
    st.header("Publications")
    # Loop through your pubs_df here as we did before
    for _, row in pubs_df.iterrows():
        st.markdown(f"**{row['Year']}** | [{row['Title']}]({row['Link']})")

with c2:
    st.header("Academic Assets")
    # Academic-specific CV download
    ac_cv = "documents/kyle_academic_cv.pdf"
    if os.path.exists(ac_cv):
        with open(ac_cv, "rb") as f:
            st.download_button("📂 Download Academic CV", f.read(), "Killebrew_Academic_CV.pdf")
    
    st.markdown("### Research Expertise")
    st.info("• Electrophysiology (EEG)\n• Psychosis Modeling\n• Experimental Design")