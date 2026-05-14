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

from loaders.academic_research_loader import (
    get_publications_data, 
    get_research_expertise, 
    get_academic_assets,
    get_project_narratives,
    get_sfm_data,               # <--- NEW NAME
    plot_sfm_dashboard,         # <--- NEW NAME
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

    # Create the 5 main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Control Data Analysis", 
        "Main Behavioral Analysis", 
        "Modeling", 
        "Eyetracking", 
        "MRS"
    ])

    with tab1:
        st.header("Control Data Analysis")
        
        # --- SECTION 1: Histograms ---
        st.subheader("1. Distribution Profiles")
        hist_choice = st.selectbox(
            "Select Distribution to View:", 
            ["Percept Durations", "Participant Responses", "Reaction Times"],
            index=0 # Sets Percept Durations as default
        )
        
        # (Placeholder) Call your Plotly plotting function based on hist_choice here
        st.info(f"Plotly Interactive Graph for {hist_choice} will go here.")
        
        # Legacy EPS Expander for Section 1
        with st.expander("View Legacy pHCP Reference (EPS)"):
            if hist_choice == "Percept Durations":
                st.image("documents/pHCP_EPS_Files/HistOfPercDurations.png")
            elif hist_choice == "Participant Responses":
                st.image("documents/pHCP_EPS_Files/HistOfPartResponses.png")
            else:
                st.image("documents/pHCP_EPS_Files/HistOfReactionTimes.png")
                
        st.divider() # Creates a clean visual line between sections
        
        # --- SECTION 2: Control Task Performance ---
        st.subheader("2. Control Task Performance")
        col1, col2 = st.columns(2)
        
        with col1:
            # (Placeholder) Plotly Graph for AveDurAwayTowards
            st.info("Interactive Plot for Average Duration Away/Towards")
        with col2:
            # (Placeholder) Plotly Graph for Accuracy
            st.info("Interactive Plot for AccFULL")
            
        # Legacy EPS Expander for Section 2
        with st.expander("View Legacy pHCP References (EPS)"):
            ref_col1, ref_col2 = st.columns(2)
            with ref_col1:
                st.image("documents/pHCP_EPS_Files/AveDurAwayTowards.png", caption="pHCP Ave Dur Away/Towards")
            with ref_col2:
                st.image("documents/pHCP_EPS_Files/PaperFig_AccFULL.png", caption="pHCP Accuracy")

        st.divider()
        
        # --- SECTION 3: Test-Retest Reliability ---
        st.subheader("3. Test-Retest Reliability")
        col3, col4 = st.columns(2)
        
        with col3:
            # (Placeholder) Plotly Graph for Test-Retest Correlation
            st.info("Interactive Plot for Test-Retest Correlation")
        with col4:
            # (Placeholder) Plotly Graph for Median Range
            st.info("Interactive Plot for Median Range")
            
        # Legacy EPS Expander for Section 3
        with st.expander("View Legacy pHCP References (EPS)"):
            ref_col3, ref_col4 = st.columns(2)
            with ref_col3:
                st.image("documents/pHCP_EPS_Files/TestRetestSwitchRates.png", caption="pHCP Test-Retest Correlation")
            with ref_col4:
                st.image("documents/pHCP_EPS_Files/TestReTest_MedianRange.png", caption="pHCP Median Range")


    with tab2:
        # --- LIVE DATA DASHBOARD ---
        st.subheader("Data Exploration: Switch Rates & Percept Durations")
        
        # --- UI CONTROLLERS ---
        ui_c1, ui_c2 = st.columns(2)
        
        with ui_c1:
            selected_grouping = st.selectbox(
                "Select grouping for analysis:",
                [
                    "Standard (Controls vs. Relatives vs. PwPP)",
                    "Detailed Psychosis (SZ vs. SCA vs. BIP vs. Controls)",
                    "SZ vs Bip_Com (Schizophrenia vs. Bipolar+Other vs. Controls)",
                    "Standard + Total Combined (Includes Sample Average)"
                ]
            )
            # NEW: The Quality Control Toggle
            apply_qc_filter = st.checkbox(
                "Apply Quality Control Exclusions (Drop participants failing control task)", 
                value=True, # Default to True (exclusions applied)
                help="Filters out participants who failed to detect at least 7 real switches within 4 seconds."
            )
            
        with ui_c2:
            selected_metric = st.selectbox(
                "Select metric to visualize:",
                ["Switch Rate (Hz)", "Average Percept Duration (sec)"]
            )
        
        # --- DATA HYDRATION ---
        # NEW: Pass the checkbox state into the loader!
        # Pass BOTH UI states directly into the loader engine
        df_sfm = get_sfm_data(grouping_mode=selected_grouping, metric_mode=selected_metric, apply_qc=apply_qc_filter)
        
        if df_sfm.empty:
            st.warning("⚠️ Data files not found. Please ensure `sfm_dashboard_data.parquet` and `SYON-3TDemographics...csv` are in the documents folder.")
        else:
            # --- PLOTTING & STATS ---
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = plot_sfm_dashboard(df_sfm, selected_metric)
                st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                
            with c2:
                st.markdown("### Live Statistical Insights")
                st.caption("Non-parametric K-W and Mann-Whitney U models dynamically computed based on current parameters.")
                
                # Determine which column to run the stats on based on the dropdown
                stat_target = 'Bistable_Hz' if "Rate" in selected_metric else 'Bistable_Dur'
                
                # Fetch and display the live stats!
                from loaders.academic_research_loader import generate_live_statistics
                stats_output = generate_live_statistics(df_sfm, stat_target)
                st.info(stats_output)
                
                with st.expander("View Full Raw Subject Data"):
                    display_cols = ['Subject', 'Group', 'Bistable_Hz', 'Bistable_Dur']
                    available_cols = [c for c in display_cols if c in df_sfm.columns]
                    st.dataframe(df_sfm[available_cols], use_container_width=True, hide_index=True)

        # Add the legacy expander underneath your Plotly chart
        with st.expander("View Legacy pHCP Reference (EPS)"):
            # Assuming your metric selectbox variable is named something like 'selected_metric'
            if selected_metric == "Bistable Switch Rate (Hz)": # Adjust text to match your actual selectbox
                st.image("documents/pHCP_EPS_Files/AveSwitchRate.png", caption="pHCP Average Switch Rate")
            elif selected_metric == "Percept Duration (Sec)":
                st.image("documents/pHCP_EPS_Files/AvePercDur.png", caption="pHCP Average Percept Duration")

    with tab3:
        st.header("Modeling")
        st.info("Modeling pipeline coming soon.")

    with tab4:
        st.header("Eyetracking")
        st.info("Eyetracking integration coming soon.")

    with tab5:
        st.header("MRS")
        st.info("MRS correlation data coming soon.")


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
