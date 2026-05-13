"""
=============================================================================
MODULE: pages/1_academic_research_app.py
AUTHOR: Kyle W. Killebrew, PhD
DESCRIPTION: 
    The presentation layer for the Academic Research portfolio.
    Builds the UI dynamically and integrates live Plotly visualizations.
=============================================================================
"""

import streamlit as st
import sys
import os

# --- PATH CONFIGURATION ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- IMPORT DATA LOADERS ---
from loaders.academic_research_loader import (
    get_publications_data, 
    get_research_expertise, 
    get_academic_assets,
    get_project_narratives,
    get_sfm_switch_rate_data,
    plot_sfm_group_comparisons,
    PLOTLY_CONFIG
)

from career_hub_loader import get_references_metadata
from career_hub_sidebar import apply_global_settings, render_sidebar

# --- INITIALIZATION ---
apply_global_settings("Kyle W. Killebrew, PhD | Academic Research")
render_sidebar()

pubs_df = get_publications_data()
expertise = get_research_expertise()
narratives = get_project_narratives()

# ==========================================
# TOP SECTION: CV & PUBLICATIONS
# ==========================================
st.title("Academic Career & Research")
c1, c2 = st.columns([2, 1])

with c1:
    st.header("Publications")
    for _, row in pubs_df.iterrows():
        st.markdown(f"**{row['Year']}** | [{row['Title']}]({row['Link']})")

with c2:
    st.header("Academic Assets")
    ac_cv = "documents/kyle_academic_cv.pdf"
    if os.path.exists(ac_cv):
        with open(ac_cv, "rb") as f:
            st.download_button("📂 Download Academic CV", f.read(), "Killebrew_Academic_CV.pdf")
    
    st.markdown("### Research Expertise")
    st.info("\n".join([f"• {item}" for item in expertise]))

st.divider()

# ==========================================
# BOTTOM SECTION: INTERACTIVE TABS
# ==========================================
st.header("Interactive Research Methodologies")
st.write("A visual summary of methodologies utilized to uncover neural biomarkers and understand visual biases.")

# Create the Tabs Layout
tabs = st.tabs([
    "🧩 1. Biomarkers of Psychosis (SFM)", 
    "👁️ 2. Eye-Tracking", 
    "🧠 3. Neural Modeling", 
    "📊 4. Visual Biases", 
    "🎯 5. Ensemble Encoding"
])

# --- TAB 1: STRUCTURE FROM MOTION (SFM) ---
with tabs[0]:
    sfm_text = narratives[0]
    col_text, col_img = st.columns([1.5, 1], gap="large")
    
    with col_text:
        st.subheader(sfm_text["header"])
        st.write(sfm_text["blurb"])
        st.info("**Methodology:** Participants viewed an ambiguous rotating cylinder. By pressing buttons to indicate perceptual phase shifts, we extracted the switch rate ($Hz$).")
        
    with col_img:
        gif_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "documents", "rotatingCylinder.gif")
        if os.path.exists(gif_path):
            st.image(gif_path, use_container_width=True, caption="Bi-Stable Structure From Motion")
            
    st.divider()
    
    # --- LIVE DATA DASHBOARD ---
    st.subheader("Data Exploration: Switch Rates Across Populations")
    
    # 1. THE DROPDOWN TOGGLE (The UI Controller)
    selected_model = st.selectbox(
        "Select Clinical Grouping Model:",
        [
            "Standard (Controls vs. Relatives vs. Probands)",
            "Liability Model (Healthy [Con+Rel] vs. Probands)",
            "Direct Comparison (Controls vs. Probands)"
        ]
    )
    
    # 2. Fetch Data (Passing the selected model to the loader!)
    df_sfm = get_sfm_switch_rate_data(grouping_mode=selected_model)
    
    if df_sfm.empty:
        st.warning("⚠️ Data files not found. Please ensure `sfm_dashboard_data.parquet` and `SYON-3TDemographics...csv` are in the documents folder.")
    else:
        # Render Plot
        c1, c2 = st.columns([2, 1])
        with c1:
            fig = plot_sfm_group_comparisons(df_sfm)
            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
            
        with c2:
            st.markdown("### Statistical Insights")
            st.markdown("""
            Individuals with psychosis (PwPP) demonstrate **significantly faster switch rates** compared to healthy controls. 
            
            Interestingly, biological relatives exhibit an intermediate phenotype, suggesting that the perceptual switch rate ($Hz$) may serve as a viable **endophenotype** for genetic liability to schizophrenia.
            """)
            
            with st.expander("View Full Raw Subject Data"):
                display_cols = ['Subject', 'Group', 'Bistable_Hz', 'Real_Switch_Hz']
                available_cols = [c for c in display_cols if c in df_sfm.columns]
                st.dataframe(df_sfm[available_cols], use_container_width=True, hide_index=True)

# --- PLACEHOLDERS FOR REMAINING TABS ---
for i in range(1, 5):
    with tabs[i]:
        st.subheader(narratives[i]["header"])
        st.write(narratives[i]["blurb"])
        
        # Load static images as placeholders for now
        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "documents", narratives[i]["image_file"])
        if os.path.exists(img_path):
            st.image(img_path, width=400)
        
        st.warning("Interactive Python pipeline currently under construction.")

st.divider()

# ==========================================
# REFERENCES SECTION
# ==========================================
references = get_references_metadata()
st.header("Academic & Professional References")
ref_cols = st.columns(3)

for i, ref in enumerate(references):
    with ref_cols[i % 3]:
        st.markdown(f"""
            <div class="ref-card">
                <p class="ref-name" style="font-weight: bold; font-size: 1.1rem; margin-bottom: 0;">{ref['name']}</p>
                <p class="ref-title" style="font-size: 0.9rem; color: #475569; margin-bottom: 0.5rem;">{ref['title']}</p>
                <p style="font-size: 0.95rem;"><a href="mailto:{ref['contact']}" style="text-decoration: none; color: #0284c7;">✉️ {ref['contact']}</a></p>
            </div>
        """, unsafe_allow_html=True)