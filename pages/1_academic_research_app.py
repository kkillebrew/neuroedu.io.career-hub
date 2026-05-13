"""
=============================================================================
MODULE: pages/1_academic_research_app.py (Spoke View)
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    The presentation layer for the Academic Research portfolio.
    Builds the UI dynamically from data passed by the loader.
=============================================================================
"""

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
    get_academic_assets,
    get_project_narratives
)

from career_hub_loader import (
    get_biographic_metadata,
    get_portfolio_metadata,
    get_references_metadata
)

from career_hub_sidebar import apply_global_settings, render_sidebar

########################################
#        APPLY GLOBAL SETTINGS         #
########################################
apply_global_settings("Kyle W. Killebrew, PhD | Academic Research")

########################################
#  RENDER THE SIDEBAR FOR CAREER-HUB   #
########################################
render_sidebar()

# --- INITIALIZE DATA FROM LOADERS ---
bio = get_biographic_metadata()
_, _, academic = get_portfolio_metadata()
pubs_df = get_publications_data()
expertise = get_research_expertise()
assets = get_academic_assets()
narratives = get_project_narratives()

# --- TOP SECTION: RESUME & PUBLICATIONS ---
st.title("Academic Career & Research")
c1, c2 = st.columns([2, 1])

with c1:
    st.header("Publications")
    for _, row in pubs_df.iterrows():
        st.markdown(f"**{row['Year']}** | [{row['Title']}]({row['Link']})")

with c2:
    st.header("Academic Assets")
    # Academic-specific CV download
    ac_cv = "documents/kyle_academic_cv.pdf"
    # Ensure graceful failure if document is missing
    if os.path.exists(ac_cv):
        with open(ac_cv, "rb") as f:
            st.download_button("📂 Download Academic CV", f.read(), "Killebrew_Academic_CV.pdf")
    
    st.markdown("### Research Expertise")
    # Dynamically build the bulleted list from the loader data
    bulleted_list = "\n".join([f"• {item}" for item in expertise])
    st.info(bulleted_list)

st.divider()

# --- BOTTOM SECTION: PROJECT NARRATIVES (The GitHub Profile Migration) ---
st.header("Research Methodologies & Project Overviews")
st.write("A visual summary of methodologies utilized to uncover neural biomarkers and understand visual biases.")
st.write("") # Spacer

# We loop through the narratives dictionary dynamically
for project in narratives:
    # Use a 2:1 column ratio to give the text plenty of reading room
    col_text, col_img = st.columns([2, 1], gap="large")
    
    with col_text:
        st.subheader(project["header"])
        st.write(project["blurb"])
        
    with col_img:
        # Construct the absolute path to the anticipated image inside /documents/
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        img_path = os.path.join(base_dir, "documents", project["image_file"])
        
        # Graceful failure: If the image isn't there yet, show a placeholder warning instead of crashing
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        else:
            st.warning(f"🖼️ Image Placeholder\n\nPending upload: `{project['image_file']}`")
            
    st.divider()

# --- BOTTOM SECTION: REFERENCES ---
# Fetch the reference data from our central loader (The Model)
references = get_references_metadata()

st.header("Academic & Professional References")
st.caption("Academic and industry leaders available for verification of tenure and technical expertise.")

# Create a 3-column grid layout for the reference cards
ref_cols = st.columns(3)

# Loop through the references and place them in alternating columns
for i, ref in enumerate(references):
    # i % 3 ensures the cards wrap around the 3 columns cleanly
    with ref_cols[i % 3]:
        # We use unsafe_allow_html=True to utilize the custom CSS classes 
        # defined in your global sidebar/styling setup.
        st.markdown(f"""
            <div class="ref-card">
                <p class="ref-name" style="font-weight: bold; font-size: 1.1rem; margin-bottom: 0;">{ref['name']}</p>
                <p class="ref-title" style="font-size: 0.9rem; color: #475569;">{ref['title']}</p>
                <p style="font-style: italic; font-size: 0.95rem;">"{ref['text']}"</p>
            </div>
        """, unsafe_allow_html=True)